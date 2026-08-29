#!/usr/bin/env python3
"""
ModelHub <-> Tauri bridge (local-only HTTP JSON API)

Production goals:
- Localhost-only server (127.0.0.1), no external exposure
- Token auth on every request (X-Auth-Token header)
- Works in dev (python -m modelhub.tauri) and in prod (PyInstaller sidecar)
- No UI/Eel dependencies
- Reuses existing ModelHub + SessionManager logic

READY line format:
  READY url=http://127.0.0.1:<port> token=<token>

Requirements:
  pip install fastapi uvicorn
"""

from __future__ import annotations

import sys as _sys


# Phase 18: suppress the benign Windows-only ProactorEventLoop close
# race that uvicorn triggers every time a keep-alive HTTP connection
# is closed by the supervisor's liveness watch. Pattern:
#
#     [Sidecar stderr] Exception in callback _ProactorBasePipeTransport._call_connection_lost(None)
#     [Sidecar stderr] handle: <Handle ...>
#     [Sidecar stderr] Traceback (most recent call last):
#     [Sidecar stderr]   File "...\asyncio\proactor_events.py", line 165, in _call_connection_lost
#     [Sidecar stderr]     self._sock.shutdown(socket.SHUT_RDWR)
#     [Sidecar stderr] ConnectionResetError: [WinError 10054] An existing connection was forcibly closed
#
# Root cause: ProactorEventLoop calls socket.shutdown(SHUT_RDWR) on a
# transport whose remote side already sent a TCP RST. The HTTP request
# has already completed successfully -- this is purely cleanup noise.
# CPython upstream tracker: https://github.com/python/cpython/issues/87419
#
# We monkey-patch the proactor transport's `_call_connection_lost` to
# silently swallow the specific 10054 case BEFORE asyncio's exception
# handler logs it. Other exceptions bubble through unchanged so a real
# socket bug is still surfaced.
def _suppress_proactor_winerror_10054() -> None:
    if _sys.platform != "win32":
        return
    try:
        from asyncio import proactor_events as _pe

        _orig = _pe._ProactorBasePipeTransport._call_connection_lost

        def _patched(self, exc):  # noqa: ANN001 -- internal asyncio API
            try:
                _orig(self, exc)
            except ConnectionResetError as e:
                # Filter ONLY the keep-alive close race (10054).
                # Anything else (e.g. genuine connection issues
                # during real I/O) re-raises as before.
                if getattr(e, "winerror", None) == 10054:
                    return
                raise
        _pe._ProactorBasePipeTransport._call_connection_lost = _patched
    except Exception:  # noqa: BLE001 -- patch is best-effort
        pass


_suppress_proactor_winerror_10054()

import argparse
import os
import secrets
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, List


# ----------------------------
# Roots (dev/prod)
# ----------------------------

DEFAULT_GAME_ID = "genshin_impact"
DEFAULT_VERSION = "0.01"

def _resolve_repo_root_from_file() -> Path:
    # modelhub/tauri.py -> modelhub -> repo root
    return Path(__file__).resolve().parent.parent

def _resolve_resource_root() -> Path:
    """
    Shipped assets root (read-only in production).
    Prefer explicit --resource-root or env.
    """
    env = os.environ.get("MODELHUB_RESOURCE_ROOT", "").strip()
    if env:
        return Path(env).expanduser().resolve()
    return _resolve_repo_root_from_file()

def _resolve_data_root() -> Path:
    """
    Writable root for new datasets/models.
    Prefer explicit --data-root or env.
    """
    env = os.environ.get("MODELHUB_DATA_ROOT", "").strip()
    if env:
        return Path(env).expanduser().resolve()
    # fallback to repo root (dev)
    return _resolve_repo_root_from_file()

RESOURCE_ROOT: Path = _resolve_resource_root()
DATA_ROOT: Path = _resolve_data_root()

# Ensure imports from repo root (dev) OR sidecar bundle path (prod).
# In prod PyInstaller, modelhub package is usually bundled, but dev needs repo root.
repo_root = _resolve_repo_root_from_file()
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))


# ----------------------------
# ModelHub imports
# ----------------------------

MODELHUB_AVAILABLE = False
session_manager = None

mh_list_games = None
mh_load_game = None
mh_discover_local_models = None
mh_validate_compatibility = None
mh_load_json = None
mh_load_settings = None
mh_get_datasets = None
mh_get_models = None
mh_delete_model_entry = None
mh_set_active_model = None
mh_get_active_model = None
mh_list_builtin_models = None

try:
    from modelhub.session_manager import SessionManager
    from modelhub.registry_store import (
        get_datasets,
        get_models,
        delete_model_entry,
        set_active_model,
        get_active_model,
    )
    from modelhub.local_store import discover_local_models as _discover_local_models
    from modelhub.registry import (
        list_games,
        load_game,
        ensure_default_catalog,
    )
    from modelhub.validator import (
        validate_compatibility,
        load_json,
    )
    from modelhub.settings import load_settings
    from modelhub.builtin_models import list_builtin_models

    mh_list_games = list_games
    mh_load_game = load_game
    mh_discover_local_models = _discover_local_models
    mh_validate_compatibility = validate_compatibility
    mh_load_json = load_json
    mh_load_settings = load_settings
    mh_get_datasets = get_datasets
    mh_get_models = get_models
    mh_delete_model_entry = delete_model_entry
    mh_set_active_model = set_active_model
    mh_get_active_model = get_active_model
    mh_list_builtin_models = list_builtin_models

    # Create default registry/catalog if needed (dev). In prod, it may live under DATA_ROOT.
    # If your ensure_default_catalog always writes relative to repo, you can still call it safely;
    # fallback filesystem scanning below guarantees UI won’t be empty.
    ensure_default_catalog()

    # IMPORTANT: SessionManager should operate against DATA_ROOT so new recordings/training appear.
    session_manager = SessionManager(DATA_ROOT)
    MODELHUB_AVAILABLE = True
except Exception as e:
    MODELHUB_AVAILABLE = False
    session_manager = None
    _MODELHUB_INIT_ERROR = str(e)


def _normalize_game_id(game_id: Optional[str]) -> str:
    gid = (game_id or "").strip()
    return gid if gid else DEFAULT_GAME_ID


def _import_grabscreen():
    """Import the screen-capture module, whatever the layout.

    Three layouts have to work:
      1. The package is installed (`pip install -e .`) -- plain import.
      2. A dev checkout, where `bot_mmorpg` is a src-layout package and
         only the repo root is on sys.path -- add `<repo>/src`.
      3. A shipped install, which bundles
         `resources/versions/<ver>/grabscreen.py` (an identical copy)
         but no `src/` tree at all -- load that file directly.

    Raises ImportError naming everything probed when none of them work,
    so the endpoint can report something actionable instead of 500ing.
    """
    try:
        from bot_mmorpg.scripts import grabscreen  # noqa: PLC0415

        return grabscreen
    except ImportError:
        pass

    probed: List[str] = []

    for root in (repo_root, RESOURCE_ROOT, RESOURCE_ROOT / "resources"):
        candidate = Path(root) / "src"
        probed.append(str(candidate))
        if not (candidate / "bot_mmorpg").is_dir():
            continue
        if str(candidate) not in sys.path:
            sys.path.insert(0, str(candidate))
        try:
            from bot_mmorpg.scripts import grabscreen  # noqa: PLC0415

            return grabscreen
        except ImportError:
            continue

    # Shipped install: load the bundled standalone copy by path.
    import importlib.util

    for root in (RESOURCE_ROOT, RESOURCE_ROOT / "resources", repo_root):
        bundled = Path(root) / "versions" / DEFAULT_VERSION / "grabscreen.py"
        probed.append(str(bundled))
        if not bundled.is_file():
            continue
        spec = importlib.util.spec_from_file_location(
            "bot_mmorpg_grabscreen_bundled", bundled
        )
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        sys.modules["bot_mmorpg_grabscreen_bundled"] = module
        spec.loader.exec_module(module)
        return module

    raise ImportError(
        "bot_mmorpg.scripts.grabscreen not importable; probed: "
        + ", ".join(probed)
    )


# ----------------------------
# Fallback scanners (guarantee UI is never empty)
# ----------------------------

def _scan_versions_builtin_models(resource_root: Path, gid: str) -> List[Dict[str, Any]]:
    """
    Treat versions/<version>/model/ as builtin models (Option B).
    This makes builtins appear even if registry/builtin_models.py doesn’t scan versions/.
    """
    out: List[Dict[str, Any]] = []
    base = resource_root / "versions" / DEFAULT_VERSION / "model"

    if not base.exists() or not base.is_dir():
        return out

    # If folder exists, advertise it as a builtin model entry.
    # ModelHub UI expects {name/path/...}. Keep it simple and stable.
    out.append({
        "id": f"versions_{DEFAULT_VERSION}_model",
        "name": f"Bundled Model ({DEFAULT_VERSION})",
        "path": str(base.as_posix()),
        "source": "versions",
        "game_id": gid,
    })
    return out


def _scan_datasets_fs(data_root: Path, gid: str) -> List[Dict[str, Any]]:
    """Scan ``<data_root>/datasets/<gid>/`` for datasets.

    Each immediate subdirectory is one dataset. As a fallback (issues
    #57, #60), if the user has loose ``.npy`` files at the root of
    ``datasets/<gid>/`` -- for example from running ``collect_data.py``
    directly with ``--out datasets/<gid>`` or from a pre-v0.2.2 build
    that didn't pin the output path -- expose those files as a synthetic
    "Unsorted recordings" dataset so they don't disappear silently from
    the Train tab.
    """
    datasets_dir = data_root / "datasets" / gid
    if not datasets_dir.exists():
        return []
    out: List[Dict[str, Any]] = []
    loose_npy_count = 0
    loose_latest_mtime = 0.0
    for p in sorted(datasets_dir.iterdir()):
        if p.is_dir():
            try:
                npy_count = sum(1 for _ in p.rglob("*.npy"))
            except Exception:
                npy_count = 0
            try:
                png_count = sum(1 for _ in p.rglob("*.png")) + sum(
                    1 for _ in p.rglob("*.jpg")
                )
            except Exception:
                png_count = 0
            out.append({
                "id": p.name,
                "name": p.name,
                "path": str(p.as_posix()),
                "file_count": npy_count + png_count,
            })
        elif p.is_file() and p.suffix.lower() == ".npy":
            loose_npy_count += 1
            try:
                loose_latest_mtime = max(loose_latest_mtime, p.stat().st_mtime)
            except Exception:
                pass
    if loose_npy_count > 0:
        out.append({
            "id": "_unsorted",
            "name": "Unsorted recordings",
            "path": str(datasets_dir.as_posix()),
            "file_count": loose_npy_count,
            "note": (
                "Loose .npy files at the root of this game's datasets folder. "
                "Move them into a named subfolder, or re-record so they get "
                "archived into a proper dataset directory."
            ),
        })
    return out


def _resolve_checkpoint_in_dir(model_dir: str) -> Optional[str]:
    """Pick the right `.pth` checkpoint inside a trained-model folder.

    Mirrors the Rust resolver in src-tauri/src/main.rs::resolve_checkpoint_path
    so behavior is identical whether the resolution happens at activate
    time (here) or at start_bot time (Rust). Priority:

      1. `*_best.pth`    -- best validation snapshot
      2. `*_final.pth`   -- last-epoch weights
      3. newest `*.pth`  -- fallback for non-conventional names

    Returns the absolute path as a string, or None if no `.pth` exists.
    Caller treats None as "let the Rust side resolve later or surface
    the train-first hint" -- this helper never raises for missing
    artifacts.
    """
    if not model_dir:
        return None
    p = Path(model_dir)
    if p.is_file() and p.suffix == ".pth":
        return str(p.as_posix())
    if not p.is_dir():
        return None
    try:
        pths = list(p.glob("*.pth"))
    except Exception:
        return None
    if not pths:
        return None
    best = next((q for q in pths if q.name.endswith("_best.pth")), None)
    if best is not None:
        return str(best.as_posix())
    final_ = next((q for q in pths if q.name.endswith("_final.pth")), None)
    if final_ is not None:
        return str(final_.as_posix())
    pths.sort(key=lambda q: q.stat().st_mtime, reverse=True)
    return str(pths[0].as_posix())


def _scan_trained_models_fs(data_root: Path, gid: str) -> List[Dict[str, Any]]:
    """Filesystem fallback for the local-models list.

    The trained-models grid in the UI sorts newest-first and pre-selects
    the just-trained model after `training_finalized`. To make that
    sort reliable without forcing the UI to stat() each folder, we
    surface a few derived fields here:

      - mtime_ms      : most-recent .pth artifact mtime (or folder mtime)
      - created_at    : ISO-8601 string of mtime_ms
      - has_artifacts : true when at least one *.pth exists
      - checkpoint    : resolved best/final/newest *.pth file path
                        (Phase 31 -- consumed by Set Active so the
                        Rust inference launcher gets a file, not a
                        folder, fixing the "Permission denied: '...New
                        Model'" error on Windows)

    These are best-effort metadata; the UI treats them as optional.
    """
    import time
    from datetime import datetime, timezone

    models_dir = data_root / "trained_models" / gid
    if not models_dir.exists():
        return []
    out: List[Dict[str, Any]] = []
    for p in sorted(models_dir.iterdir()):
        if not p.is_dir():
            continue
        try:
            pths = sorted(p.glob("*.pth"), key=lambda q: q.stat().st_mtime, reverse=True)
        except Exception:
            pths = []
        try:
            base_mtime = p.stat().st_mtime
        except Exception:
            base_mtime = time.time()
        latest_mtime = pths[0].stat().st_mtime if pths else base_mtime
        checkpoint = _resolve_checkpoint_in_dir(str(p))
        out.append({
            "id": p.name,
            "name": p.name,
            "path": str(p.as_posix()),
            "model_dir": str(p.as_posix()),
            "source": "trained_models",
            "mtime_ms": int(latest_mtime * 1000),
            "created_at": datetime.fromtimestamp(latest_mtime, tz=timezone.utc).isoformat(),
            "has_artifacts": bool(pths),
            "checkpoint": checkpoint,
        })
    # newest first so the UI doesn't have to re-sort if it trusts the order
    out.sort(key=lambda m: m.get("mtime_ms", 0), reverse=True)
    return out


# ----------------------------
# FastAPI server
# ----------------------------

def create_app(token: str):
    from fastapi import FastAPI, Header, HTTPException, Request
    from fastapi.responses import JSONResponse

    app = FastAPI(
        title="ModelHub Tauri API",
        version="0.1.8",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )

    def _auth(x_auth_token: Optional[str]):
        if not x_auth_token or x_auth_token != token:
            raise HTTPException(status_code=401, detail="Unauthorized")

    @app.exception_handler(Exception)
    async def _unhandled_exception_handler(request: Request, exc: Exception):
        # Non-invasive observation: capture into the diagnostic ring buffer
        # before the response is built. This is read-only -- the response
        # below is unchanged from the pre-diagnostic version.
        try:
            from .diagnostics import collector as _diag_collector
            _diag_collector.capture_exception(
                exc,
                source="sidecar",
                request_path=str(request.url.path),
                request_method=request.method,
            )
        except Exception:  # noqa: BLE001
            # Never let the diagnostic layer break error handling.
            pass
        return JSONResponse(status_code=500, content={"ok": False, "error": str(exc)})

    @app.get("/health")
    async def health(x_auth_token: Optional[str] = Header(default=None)):
        _auth(x_auth_token)

        # Collect diagnostic info for troubleshooting (#26, #37)
        diagnostics = {}
        if not MODELHUB_AVAILABLE:
            diagnostics["warning"] = _MODELHUB_INIT_ERROR
            diagnostics["troubleshooting"] = (
                "The sidecar API started but ModelHub failed to initialize. "
                "Check that all Python dependencies are installed (pip install -e .) "
                "and that the catalog/ and game_profiles/ directories exist."
            )

        # Check writable data root
        try:
            test_file = DATA_ROOT / ".write_test"
            test_file.touch()
            test_file.unlink()
        except Exception:
            diagnostics["data_root_writable"] = False
            diagnostics["data_root_error"] = (
                f"Cannot write to {DATA_ROOT}. "
                "Check file permissions or set MODELHUB_DATA_ROOT env var."
            )

        return {
            "ok": True,
            "modelhub": MODELHUB_AVAILABLE,
            "resource_root": str(RESOURCE_ROOT),
            "data_root": str(DATA_ROOT),
            "version": "0.1.9",
            "session_manager": session_manager is not None,
            **diagnostics,
        }

    @app.get("/diagnostics")
    async def diagnostics(x_auth_token: Optional[str] = Header(default=None)):
        """Extended diagnostics endpoint for debugging setup issues (#26, #37)."""
        _auth(x_auth_token)
        import platform as plat

        diag = {
            "ok": True,
            "python_version": plat.python_version(),
            "platform": plat.system(),
            "modelhub_available": MODELHUB_AVAILABLE,
            "session_manager": session_manager is not None,
            "resource_root": str(RESOURCE_ROOT),
            "resource_root_exists": RESOURCE_ROOT.exists(),
            "data_root": str(DATA_ROOT),
            "data_root_exists": DATA_ROOT.exists(),
        }

        # Check key directories
        for name in ["catalog", "game_profiles", "versions"]:
            p = RESOURCE_ROOT / name
            diag[f"{name}_exists"] = p.exists()

        # Check PyTorch availability
        try:
            import torch
            diag["pytorch_version"] = torch.__version__
            diag["cuda_available"] = torch.cuda.is_available()
            if torch.cuda.is_available():
                diag["gpu_name"] = torch.cuda.get_device_name(0)
                # CUDA 13 / torch >= 2.10 renamed the device property
                # `total_mem` -> `total_memory`. Probe both so this
                # diagnostics endpoint doesn't raise AttributeError on
                # newer builds (which the `except ImportError` below would
                # NOT catch). Mirrors _safe_total_vram_gb in
                # train_model.py. See issue #59.
                props = torch.cuda.get_device_properties(0)
                vram = getattr(props, "total_memory", None)
                if vram is None:
                    vram = getattr(props, "total_mem", None)
                diag["gpu_vram_gb"] = round(vram / 1e9, 1) if vram else None
        except ImportError:
            diag["pytorch_version"] = None
            diag["cuda_available"] = False
        except Exception as e:
            # GPU probing must never abort the whole diagnostics payload
            # (#26/#37 rely on this endpoint to debug broken setups).
            diag.setdefault("pytorch_version", None)
            diag["gpu_probe_error"] = str(e)

        # List available games
        if mh_list_games:
            try:
                games = mh_list_games() or []
                diag["available_games"] = [
                    g["id"] if isinstance(g, dict) else g for g in games
                ]
            except Exception as e:
                diag["available_games_error"] = str(e)

        if not MODELHUB_AVAILABLE:
            diag["init_error"] = _MODELHUB_INIT_ERROR

        return diag

    # -------- Session endpoints --------

    @app.post("/session/begin_recording")
    async def begin_recording(payload: Dict[str, Any], x_auth_token: Optional[str] = Header(default=None)):
        _auth(x_auth_token)
        if not session_manager:
            return {"ok": False, "error": "SessionManager not available"}
        gid = _normalize_game_id(payload.get("game_id"))
        dataset_name = (payload.get("dataset_name") or "Untitled").strip()
        session_manager.begin_recording(gid, dataset_name)
        return {"ok": True}

    @app.post("/session/begin_training")
    async def begin_training(payload: Dict[str, Any], x_auth_token: Optional[str] = Header(default=None)):
        _auth(x_auth_token)
        if not session_manager:
            return {"ok": False, "error": "SessionManager not available"}
        gid = _normalize_game_id(payload.get("game_id"))
        model_name = (payload.get("model_name") or "New Model").strip()
        dataset_id = (payload.get("dataset_id") or "").strip()
        arch = (payload.get("arch") or "custom").strip()
        out_dir = (payload.get("out_dir") or "").strip()
        session_manager.begin_training(gid, model_name, dataset_id, arch, out_dir=out_dir)
        return {"ok": True}

    @app.post("/session/finalize")
    async def finalize(payload: Dict[str, Any] | None = None, x_auth_token: Optional[str] = Header(default=None)):
        _auth(x_auth_token)
        if not session_manager or not getattr(session_manager, "active_session", None):
            return {"ok": True, "finalized": None}

        stype = session_manager.active_session.get("type")
        if stype == "recording":
            # Phase 25: forward the archived dataset entry (id, name,
            # path, file_count, game_id) to the Rust shell so it can
            # surface the new dataset id in the stop_recording response,
            # which lets the UI prefill `train-dataset-id` and skip the
            # "No dataset selected" preflight on first use.
            archived = session_manager.finalize_recording()
            return {"ok": True, "finalized": "recording", "dataset": archived}
        if stype == "training":
            session_manager.finalize_training()
            return {"ok": True, "finalized": "training"}
        return {"ok": True, "finalized": "unknown"}

    # -------- Screen capture endpoints --------
    #
    # The Rust shell has always forwarded "Preview" to POST
    # /capture/preview (main.rs::get_screen_preview) and the monitor
    # picker to the sidecar, but neither route existed here -- every
    # request 404'd and the UI fell back to its empty state. That is the
    # "screen capture won't capture my screen" of issue #81 and the
    # "Preview section only shows 'No Preview yet'" of issue #57: the
    # capture code was fine, nothing was ever asked to run it.

    @app.get("/capture/monitors")
    async def capture_monitors(x_auth_token: Optional[str] = Header(default=None)):
        _auth(x_auth_token)
        try:
            grabscreen = _import_grabscreen()
        except Exception as e:  # noqa: BLE001
            return {
                "ok": False,
                "monitors": [],
                "error": f"Screen capture unavailable: {e}",
                "hint": (
                    "Install the capture dependencies: "
                    "pip install mss (all platforms) or pywin32 (Windows)."
                ),
            }
        try:
            return {"ok": True, "monitors": grabscreen.list_monitors()}
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "monitors": [], "error": str(e)}

    @app.post("/capture/preview")
    async def capture_preview(
        payload: Optional[Dict[str, Any]] = None,
        x_auth_token: Optional[str] = Header(default=None),
    ):
        _auth(x_auth_token)
        payload = payload or {}

        # The shell sends 0 for "primary"; grabscreen numbers monitors
        # from 1 (mss convention), so 0 means "first real monitor".
        try:
            monitor_id = int(payload.get("monitor_id") or 0)
        except (TypeError, ValueError):
            monitor_id = 0
        if monitor_id < 1:
            monitor_id = 1

        try:
            width = int(payload.get("width") or 640)
            height = int(payload.get("height") or 360)
        except (TypeError, ValueError):
            width, height = 640, 360

        try:
            grabscreen = _import_grabscreen()
        except Exception as e:  # noqa: BLE001
            return {
                "ok": False,
                "error": f"Screen capture unavailable: {e}",
                "hint": (
                    "Install the capture dependencies: "
                    "pip install mss (all platforms) or pywin32 (Windows)."
                ),
            }

        try:
            image = grabscreen.grab_screen_base64(monitor_id, width, height, 70)
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "error": str(e)}

        return {
            "ok": True,
            "monitor_id": monitor_id,
            "format": "jpeg",
            "encoding": "base64",
            "image": image,
        }

    # -------- ModelHub endpoints --------

    @app.get("/modelhub/available")
    async def modelhub_available(x_auth_token: Optional[str] = Header(default=None)):
        _auth(x_auth_token)
        return {"ok": True, "available": MODELHUB_AVAILABLE}

    @app.get("/modelhub/games")
    async def modelhub_games(x_auth_token: Optional[str] = Header(default=None)):
        _auth(x_auth_token)
        # If registry-based list fails, still provide default game so UI isn’t empty.
        if mh_list_games is None:
            return {"ok": True, "games": [DEFAULT_GAME_ID]}
        games = mh_list_games() or []
        if not games:
            games = [DEFAULT_GAME_ID]
        return {"ok": True, "games": games}

    @app.get("/modelhub/catalog")
    async def modelhub_catalog(game_id: str = "", x_auth_token: Optional[str] = Header(default=None)):
        _auth(x_auth_token)
        gid = _normalize_game_id(game_id)

        # Builtins:
        builtin = []
        if mh_list_builtin_models:
            try:
                # IMPORTANT: builtins should be scanned from RESOURCE_ROOT (shipped assets)
                builtin = mh_list_builtin_models(RESOURCE_ROOT, gid) or []
            except Exception:
                builtin = []

        # Option B injection: versions/0.01/model as builtin
        builtin += _scan_versions_builtin_models(RESOURCE_ROOT, gid)

        # Datasets/models registry (may be empty in fresh install)
        datasets = []
        models = []
        active = None

        if MODELHUB_AVAILABLE:
            try:
                datasets = mh_get_datasets(gid) if mh_get_datasets else []
            except Exception:
                datasets = []
            try:
                models = mh_get_models(gid) if mh_get_models else []
            except Exception:
                models = []
            try:
                active = mh_get_active_model() if mh_get_active_model else None
            except Exception:
                active = None

        # Local trained models: prefer your discover function, fallback to filesystem scan
        local_models = []
        if mh_discover_local_models and mh_load_settings:
            try:
                s = mh_load_settings()
                # Ensure local_models_dir resolves under DATA_ROOT
                # If settings points to "trained_models", this becomes DATA_ROOT/trained_models/<gid>
                local_models = mh_discover_local_models((DATA_ROOT / s.local_models_dir), gid) or []
            except Exception:
                local_models = []

        if not local_models:
            local_models = _scan_trained_models_fs(DATA_ROOT, gid)

        # If registry datasets empty, fallback to filesystem (so recording appears immediately)
        if not datasets:
            datasets = _scan_datasets_fs(DATA_ROOT, gid)

        return {
            "ok": True,
            "resource_root": str(RESOURCE_ROOT),
            "data_root": str(DATA_ROOT),
            "builtin_models": builtin,
            "datasets": datasets,
            "models": models,
            "local_models": local_models,
            "active": active,
        }

    @app.post("/modelhub/active")
    async def modelhub_set_active(payload: Dict[str, Any], x_auth_token: Optional[str] = Header(default=None)):
        _auth(x_auth_token)
        if not MODELHUB_AVAILABLE or mh_set_active_model is None:
            return {"ok": False, "error": "ModelHub not available"}
        gid = _normalize_game_id(payload.get("game_id"))
        model_id = (payload.get("model_id") or "").strip()
        path = (payload.get("path") or "").strip()
        # Phase 31: optional resolved checkpoint file. The Rust
        # inference launcher prefers `model_file` over walking the
        # directory. Absent value is fine -- the launcher resolves it
        # via best -> final -> newest as a fallback.
        model_file = (payload.get("model_file") or "").strip()
        if not model_id or not path:
            return {"ok": False, "error": "model_id and path are required"}

        # If the UI sent only a directory, resolve a checkpoint here so
        # `active_model.json` carries the file path going forward and
        # other consumers (CLI, smoke tests) don't have to repeat the
        # walk. Best-effort: leave unset on failure rather than
        # blocking the activation -- the Rust resolver will still
        # cover us at start_bot time.
        if not model_file:
            try:
                model_file = _resolve_checkpoint_in_dir(path) or ""
            except Exception:
                model_file = ""

        mh_set_active_model(gid, model_id, path, model_file)
        return {"ok": True, "model_file": model_file or None}

    # Phase 22: dedicated /modelhub/datasets endpoint. Previously the
    # Rust shell's `list_datasets` Tauri command called this URL, but
    # NO matching route existed -- the sidecar always returned 404 and
    # the Rust side reported `{datasets: []}` to the UI. So even after
    # a successful recording, the Train tab and the Teach -> Datasets
    # card both showed "No datasets found" forever. The Catalog endpoint
    # /modelhub/catalog DID surface datasets via mh_get_datasets, but
    # only as part of the bigger catalog response.
    #
    # This endpoint scans `<DATA_ROOT>/datasets/<game>/` (the same path
    # collect_data.py writes to via session_manager.begin_recording)
    # and returns the dataset directories as JSON. Falls back to the
    # ModelHub registry when available so test datasets registered via
    # the API also surface.
    @app.get("/modelhub/datasets")
    async def modelhub_datasets(
        game_id: Optional[str] = None,
        x_auth_token: Optional[str] = Header(default=None),
    ):
        _auth(x_auth_token)
        gid = _normalize_game_id(game_id)
        # Filesystem scan -- canonical source of truth, works even
        # without ModelHub registry init.
        datasets = _scan_datasets_fs(DATA_ROOT, gid)
        # Augment with ModelHub registry entries (test fixtures, etc.)
        # that may not be on disk under the standard layout.
        if MODELHUB_AVAILABLE and mh_get_datasets is not None:
            try:
                seen_ids = {d.get("id") for d in datasets}
                for ds in mh_get_datasets(gid) or []:
                    if ds.get("id") not in seen_ids:
                        datasets.append(ds)
                        seen_ids.add(ds.get("id"))
            except Exception:
                pass
        return {"ok": True, "datasets": datasets, "game_id": gid}

    @app.post("/modelhub/delete")
    async def modelhub_delete(payload: Dict[str, Any], x_auth_token: Optional[str] = Header(default=None)):
        _auth(x_auth_token)
        if not MODELHUB_AVAILABLE:
            return {"ok": False, "error": "ModelHub not available"}

        gid = _normalize_game_id(payload.get("game_id"))
        model_id = (payload.get("model_id") or "").strip()
        path = (payload.get("path") or "").strip()
        if not model_id or not path:
            return {"ok": False, "error": "model_id and path are required"}

        # Safety: only allow deletes under DATA_ROOT/trained_models/<gid>/
        try:
            full_path = Path(path).expanduser()
            if not full_path.is_absolute():
                full_path = (DATA_ROOT / full_path).resolve()
            else:
                full_path = full_path.resolve()

            safe_root = (DATA_ROOT / "trained_models" / gid).resolve()
            if safe_root not in full_path.parents and full_path != safe_root:
                return {"ok": False, "error": f"Refusing to delete outside trained_models/{gid}"}

            if full_path.exists():
                if full_path.is_dir():
                    import shutil
                    shutil.rmtree(full_path)
                else:
                    full_path.unlink()

            if mh_delete_model_entry:
                mh_delete_model_entry(gid, model_id)

            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @app.post("/modelhub/validate")
    async def modelhub_validate(payload: Dict[str, Any], x_auth_token: Optional[str] = Header(default=None)):
        _auth(x_auth_token)
        if mh_load_game is None or mh_validate_compatibility is None or mh_load_json is None:
            return {"ok": False, "message": "ModelHub not installed"}

        gid = _normalize_game_id(payload.get("game_id"))
        model_dir = (payload.get("model_dir") or "").strip()
        if not model_dir:
            return {"ok": False, "message": "model_dir is required"}

        blueprint = mh_load_game(gid)
        profile_path = Path(model_dir) / "profile.json"
        if not profile_path.exists():
            return {"ok": False, "message": "Missing profile.json"}

        profile = mh_load_json(profile_path)
        ok, msg = mh_validate_compatibility(blueprint, profile)
        return {"ok": True, "result": {"ok": ok, "message": msg}}

    # ─────────────────────────────────────────────────────────────────
    # AI debug-loop diagnostics (non-invasive observation layer).
    #
    # The router below exposes /diagnostics/recent, /diagnostics/recent/ai,
    # /diagnostics/recent/markdown, and DELETE /diagnostics/recent for the
    # Settings -> System Tools UI. The error-capture side already happened
    # in `_unhandled_exception_handler` above. Mounted last so route
    # registration order is irrelevant -- every prior router takes priority.
    #
    # Wrapped in try/except: if the diagnostics module fails to import for
    # any reason (missing file in a custom build), the sidecar still runs
    # without the debug routes. Belt-and-suspenders given how new this is.
    try:
        from .diagnostics.routes import make_router as _make_diag_router
        # Pass repo_root so the formatter can produce repo-relative paths.
        # In production it's the resource root's parent (-> install dir);
        # in dev mode it's the repo root.
        _diag_repo_root = os.environ.get(
            "BOT_REPO_ROOT",
            str((RESOURCE_ROOT.parent if RESOURCE_ROOT else Path("."))),
        )
        app.include_router(_make_diag_router(expected_token=token, repo_root=_diag_repo_root))
    except Exception as _diag_err:  # noqa: BLE001
        # Soft fail. Print to stderr so a developer can see it but the
        # sidecar starts regardless.
        print(f"[Sidecar] diagnostics router not mounted: {_diag_err}", flush=True)

    # MVP-3: sidecar-owned job runner. Tauri now POSTs /jobs/* instead of
    # spawning Python directly. Crashes in training/collection are
    # contained inside the sidecar's process tree, never reach the UI.
    # Same soft-fail pattern as diagnostics: if the module won't import,
    # the sidecar still serves /modelhub/* + /diagnostics/*.
    try:
        from .jobs.routes import make_router as _make_jobs_router
        app.include_router(_make_jobs_router(expected_token=token))
    except Exception as _jobs_err:  # noqa: BLE001
        print(f"[Sidecar] jobs router not mounted: {_jobs_err}", flush=True)

    return app


def _pick_host() -> str:
    return "127.0.0.1"


def run_server(port: int, token: str) -> Tuple[str, str]:
    import uvicorn
    from uvicorn.config import Config
    from uvicorn.server import Server
    import socket

    host = _pick_host()
    app = create_app(token)

    config = Config(
        app=app,
        host=host,
        port=port,
        log_level="warning",
        access_log=False,
        lifespan="off",
    )
    server = Server(config=config)

    if port == 0:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((host, 0))
        sock.listen(128)
        bound_port = sock.getsockname()[1]
        sockets = [sock]
    else:
        bound_port = port
        sockets = None

    base_url = f"http://{host}:{bound_port}"
    print(f"READY url={base_url} token={token}", flush=True)

    if sockets is not None:
        server.run(sockets=sockets)
    else:
        server.run()

    return base_url, token


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="ModelHub local HTTP API for Tauri")
    parser.add_argument("--port", type=int, default=0, help="Port to bind. Use 0 to auto-pick.")
    parser.add_argument("--token", type=str, default="", help="Auth token. If empty, generates one.")
    parser.add_argument("--resource-root", type=str, default="", help="Read-only shipped assets root (versions/, etc).")
    parser.add_argument("--data-root", type=str, default="", help="Writable data root (datasets/, trained_models/).")
    args = parser.parse_args(argv)

    if args.resource_root.strip():
        os.environ["MODELHUB_RESOURCE_ROOT"] = args.resource_root.strip()
    if args.data_root.strip():
        os.environ["MODELHUB_DATA_ROOT"] = args.data_root.strip()

    # Recompute globals after env set
    global RESOURCE_ROOT, DATA_ROOT
    RESOURCE_ROOT = _resolve_resource_root()
    DATA_ROOT = _resolve_data_root()
    DATA_ROOT.mkdir(parents=True, exist_ok=True)

    token = args.token.strip() or secrets.token_urlsafe(32)

    try:
        run_server(args.port, token)
        return 0
    except KeyboardInterrupt:
        return 0
    except Exception as e:
        # Phase 8: route the canonical FAILED marker to STDERR.
        # The Rust supervisor's fast-fail parser (main.rs stderr
        # thread) looks for `FAILED ` only on stderr -- printing it
        # to stdout (Python's `print` default) meant the supervisor
        # waited the full 60s timeout instead of bailing immediately.
        # Mirror in entry_main.py's wrapper for the import-time path.
        print(f"FAILED error={e}", file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
