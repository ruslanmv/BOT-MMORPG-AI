# modelhub/session_manager.py
"""
Session manager for recording + training.

FIXES (for launcher v0.1.8 workflow):
✅ Recording finalize detects datasets saved directly to datasets/<game>/<dataset_name>/ (optional workflow).
✅ Recording finalize ALSO works with your current collector that writes into versions/0.01/datasets/*.npy (snapshot fallback).
✅ Training finalize detects models saved directly to trained_models/<game>/<model_name>/ (launcher out_dir).
✅ Accepts out_dir passed from launcher: begin_training(..., out_dir="...") so finalize always checks the real folder.
✅ Writes profile.json for trained models so ModelHub validator & UI work.
✅ No more false "No new model artifact detected" when .pth exists.
✅ Windows-safe printing + name sanitization.
"""

from __future__ import annotations

import re
import shutil
import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any, Iterable

from modelhub.paths import get_candidate_paths
from modelhub.fs_snapshot import take_snapshot, find_changes
from modelhub.registry_store import register_dataset, register_model
from modelhub.profile_writer import write_profile
from modelhub.naming import slugify


# -------------------------
# SAFETY HELPERS
# -------------------------

_INVALID_WIN_CHARS = r'<>:"/\\|?*'
_CONTROL_CHARS_RE = re.compile(r"[\x00-\x1f\x7f]")
_INVALID_CHARS_RE = re.compile(rf"[{re.escape(_INVALID_WIN_CHARS)}]")


def _sanitize_for_windows_filename(name: str, replacement: str = "_") -> str:
    """Sanitize a user name to be safe for Windows filenames."""
    if name is None:
        name = ""
    s = str(name)

    s = _CONTROL_CHARS_RE.sub(replacement, s)
    s = _INVALID_CHARS_RE.sub(replacement, s)
    s = re.sub(r"\s+", " ", s).strip()
    s = s.rstrip(" .")  # Windows disallows trailing dots/spaces

    if not s:
        s = "Untitled"

    upper = s.upper()
    reserved = {
        "CON", "PRN", "AUX", "NUL",
        *(f"COM{i}" for i in range(1, 10)),
        *(f"LPT{i}" for i in range(1, 10)),
    }
    if upper in reserved:
        s = f"_{s}_"

    return s


def _safe_print(*parts: object) -> None:
    """Print that won't crash on Windows weird stdout encoding."""
    msg = " ".join("" if p is None else str(p) for p in parts)
    try:
        print(msg, flush=True)
        return
    except Exception:
        pass

    try:
        data = (msg + "\n").encode("utf-8", errors="replace")
        sys.stderr.buffer.write(data)
        sys.stderr.flush()
    except Exception:
        return


def _count_files(folder: Path, exts: Iterable[str]) -> int:
    c = 0
    for ext in exts:
        c += len(list(folder.rglob(f"*{ext}")))
    return c


def _find_primary_artifact_in_dir(model_dir: Path) -> Optional[Path]:
    """
    Pick the best model artifact inside model_dir.
    Priorities:
      1) *_final.pth / *_final.pt
      2) *_best.pth / *_best.pt
      3) any *.pth / *.pt / *.keras / *.h5 (newest mtime)
    """
    if not model_dir.exists() or not model_dir.is_dir():
        return None

    final = sorted(model_dir.glob("*_final.pth")) + sorted(model_dir.glob("*_final.pt"))
    if final:
        return max(final, key=lambda p: p.stat().st_mtime)

    best = sorted(model_dir.glob("*_best.pth")) + sorted(model_dir.glob("*_best.pt"))
    if best:
        return max(best, key=lambda p: p.stat().st_mtime)

    candidates: list[Path] = []
    for pat in ("*.pth", "*.pt", "*.keras", "*.h5"):
        candidates.extend(model_dir.glob(pat))

    if not candidates:
        return None

    return max(candidates, key=lambda p: p.stat().st_mtime)


# -------------------------
# MAIN CLASS
# -------------------------

class SessionManager:
    def __init__(self, project_root: Path):
        self.root = Path(project_root)
        self.candidates = get_candidate_paths(project_root)
        self.active_session: Optional[Dict[str, Any]] = None
        self._snapshot: Dict[str, float] = {}

    # -------------------------
    # RECORDING SESSION (DATA)
    # -------------------------
    def begin_recording(self, game_id: str, dataset_name: str):
        dataset_name = dataset_name or "Untitled"
        _safe_print("[Session] Starting recording session:", dataset_name)

        self.active_session = {
            "type": "recording",
            "game_id": game_id,
            "name": dataset_name,
            "start_time": time.time(),
        }

        # Snapshot of candidate "data" directory for fallback detection
        self._snapshot = take_snapshot(self.candidates["data"], extensions={".npy"})

    def finalize_recording(self):
        # Phase 25: returns the archived dataset entry (or None) so the
        # FastAPI route -> Rust stop_recording -> JS chain can auto-fill
        # the Train tab's `train-dataset-id` with the just-recorded id,
        # eliminating the "No dataset selected" preflight that hits
        # first-time users right after their first successful recording.
        if not self.active_session or self.active_session.get("type") != "recording":
            return None

        _safe_print("[Session] Finalizing recording...")

        game_id = self.active_session["game_id"]
        raw_name = self.active_session["name"] or "Untitled"

        # PRIMARY (optional) workflow: if someone writes datasets directly into datasets/<game>/<dataset_name>/
        expected_dir = (self.root / "datasets" / game_id / raw_name).resolve()
        if expected_dir.exists() and expected_dir.is_dir():
            npy_count = _count_files(expected_dir, exts=(".npy",))
            png_count = _count_files(expected_dir, exts=(".png", ".jpg", ".jpeg"))
            total = npy_count + png_count
            if total > 0:
                entry = {
                    "id": expected_dir.name,
                    "name": raw_name,
                    "path": str(expected_dir.relative_to(self.root)),
                    "file_count": total,
                    "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "game_id": game_id,
                }
                register_dataset(game_id, entry)
                _safe_print(f"[Session] Registered dataset (direct): {total} file(s) -> {entry['path']}")
                self.active_session = None
                return entry

        # FALLBACK: detect new .npy created in candidates["data"] (works with your collector saving to versions/0.01/datasets/)
        current_state = take_snapshot(self.candidates["data"], extensions={".npy"})
        changed_files = find_changes(self._snapshot, current_state)

        changed_files = [
            f for f in changed_files
            if f.is_file()
            and (
                f.name.startswith("preprocessed_training_data-") or
                f.name.startswith("training_data-")
            )
            and f.suffix.lower() == ".npy"
        ]

        if not changed_files:
            _safe_print("[Session] Warning: No new dataset files detected (direct dir missing and no .npy changes).")
            self.active_session = None
            return None

        safe_display_name = _sanitize_for_windows_filename(raw_name)
        safe_slug = slugify(safe_display_name)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        dataset_id = f"{timestamp}_{safe_slug}"

        dest_dir = self.root / "datasets" / game_id / dataset_id
        dest_dir.mkdir(parents=True, exist_ok=True)

        count = 0
        for f in sorted(changed_files, key=lambda x: x.stat().st_mtime):
            try:
                shutil.copy2(str(f), str(dest_dir / f.name))
                count += 1
            except Exception as e:
                _safe_print("[Session] Error copying dataset file", str(f), ":", e)

        archived_entry = None
        if count > 0:
            archived_entry = {
                "id": dataset_id,
                "name": raw_name,
                "path": str(dest_dir.relative_to(self.root)),
                "file_count": count,
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "game_id": game_id,
            }
            register_dataset(game_id, archived_entry)
            _safe_print(f"[Session] Archived dataset: {count} file(s) -> {archived_entry['path']}")

        self.active_session = None
        return archived_entry

    # -------------------------
    # TRAINING SESSION (MODEL)
    # -------------------------
    def begin_training(
        self,
        game_id: str,
        model_name: str,
        dataset_id: str,
        arch: str,
        out_dir: str | None = None,
    ):
        model_name = model_name or "New Model"
        _safe_print("[Session] Starting training session:", model_name)

        self.active_session = {
            "type": "training",
            "game_id": game_id,
            "name": model_name,
            "dataset_id": dataset_id,
            "architecture": arch,
            # Store real output dir used by launcher (preferred)
            "out_dir": str(out_dir) if out_dir else "",
            "start_time": time.time(),
        }

        # Snapshot only as fallback (older workflows)
        self._snapshot = take_snapshot(self.candidates["model"], extensions=None)

    def finalize_training(self):
        if not self.active_session or self.active_session.get("type") != "training":
            return

        _safe_print("[Session] Finalizing training...")

        game_id = self.active_session["game_id"]
        raw_name = self.active_session["name"] or "New Model"
        arch = self.active_session.get("architecture", "custom")
        dataset_id = self.active_session.get("dataset_id", "")

        # PRIMARY: use out_dir passed from launcher
        out_dir = (self.active_session.get("out_dir") or "").strip()
        if out_dir:
            expected_dir = Path(out_dir).resolve()
        else:
            expected_dir = (self.root / "trained_models" / game_id / raw_name).resolve()

        # If launcher/UI name had invalid chars, try sanitized fallback folder
        if not expected_dir.exists():
            safe_display_name = _sanitize_for_windows_filename(raw_name)
            expected_dir = (self.root / "trained_models" / game_id / safe_display_name).resolve()

        if expected_dir.exists() and expected_dir.is_dir():
            primary = _find_primary_artifact_in_dir(expected_dir)
            if not primary:
                _safe_print(
                    "[Session] Warning: Training output folder exists but no model artifact found in it:",
                    expected_dir
                )
                self.active_session = None
                return

            # Ensure profile.json exists (required by ModelHub validator/UI)
            meta = {
                "model_name": raw_name,
                "game_id": game_id,
                # IMPORTANT: keep folder name as model_id so UI discovery matches
                "model_id": expected_dir.name,
                "dataset_id": dataset_id,
                "architecture": arch,
                "artifact": primary.name,
            }
            write_profile(expected_dir, meta)

            entry = {
                "id": expected_dir.name,
                "name": raw_name,
                "path": str(expected_dir.relative_to(self.root)),
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            }
            register_model(game_id, entry)

            _safe_print("[Session] Registered trained model:", entry["path"])
            self.active_session = None
            return

        # FALLBACK: legacy artifact discovery (snapshot diff)
        current_state = take_snapshot(self.candidates["model"], extensions=None)
        changed_files = find_changes(self._snapshot, current_state)

        preferred = [
            p for p in changed_files
            if p.is_file() and p.suffix.lower() in (".pth", ".pt", ".keras", ".h5")
        ]
        primary_artifact = max(preferred, key=lambda p: p.stat().st_mtime) if preferred else None

        if not primary_artifact:
            _safe_print("[Session] Warning: No new model artifact detected (expected_dir missing and snapshot found nothing).")
            self.active_session = None
            return

        safe_display_name = _sanitize_for_windows_filename(raw_name)
        safe_slug = slugify(safe_display_name)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        model_id = f"{timestamp}_{safe_slug}"

        dest_dir = self.root / "trained_models" / game_id / model_id
        dest_dir.mkdir(parents=True, exist_ok=True)

        dest_file: Optional[Path] = None
        try:
            ext = primary_artifact.suffix.lower()
            dest_file = dest_dir / f"model{ext}"
            shutil.copy2(str(primary_artifact), str(dest_file))
            _safe_print("[Session] Archived model artifact ->", str(dest_dir))
        except Exception as e:
            _safe_print("[Session] Error archiving model artifact:", e)
            self.active_session = None
            return

        meta = {
            "model_name": raw_name,
            "game_id": game_id,
            "model_id": model_id,
            "dataset_id": dataset_id,
            "architecture": arch,
            "artifact": dest_file.name if dest_file else "",
        }
        write_profile(dest_dir, meta)

        entry = {
            "id": model_id,
            "name": raw_name,
            "path": str(dest_dir.relative_to(self.root)),
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        register_model(game_id, entry)

        self.active_session = None
