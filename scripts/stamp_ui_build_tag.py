"""Stamp the UI build tag into tauri-ui/main.js.

Substitutes the literal `%BUILD_TAG%` in main.js with the live
version string (same one Rust embeds), so the UI logs which
bundle is actually running on every page load.

Why this exists (Phase 23-B):
  Tauri 1.x dev mode and NSIS installs both have observed cases
  where stale JS shipped or got cached, producing the "fix is
  in repo but not running" failure mode. Without a runtime
  fingerprint there's no way to tell stale-JS apart from
  fix-was-wrong from a debug bundle. This script ensures the
  bundle's first JS log line is always the build tag.

Idempotent:
  - Re-running with the same tag is a no-op.
  - Re-running after `git pull` overwrites with the new tag.
  - Re-running on a checkout that's already stamped (placeholder
    is gone) re-stamps based on the literal we expect to find,
    skipping if it can't be located.

Resolves the tag from (in priority order):
  1. $BUILD_TAG env var (CI, explicit overrides)
  2. `git describe --tags --dirty --always` from the repo root
  3. "dev-{unix-ms}" if neither is available

Invoked by:
  - make dev          -> stamp before `cargo tauri dev` reads main.js
  - make artifact     -> stamp before scripts/build_pipeline.ps1 packs it
  - tests             -> n/a (tests use the placeholder unchanged)

Reverse operation:
  scripts/stamp_ui_build_tag.py --restore
  resets main.js back to the placeholder so a developer's working
  tree doesn't accumulate build-tag changes between iterations.
"""

from __future__ import annotations

import argparse
import os
import pathlib
import shutil
import subprocess
import sys
import time

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
MAIN_JS = REPO_ROOT / "tauri-ui" / "main.js"
PLACEHOLDER = '"%BUILD_TAG%"'  # quoted on purpose -- matches the JS literal


def resolve_tag() -> str:
    env = os.environ.get("BUILD_TAG", "").strip()
    if env:
        return env
    try:
        out = subprocess.check_output(
            ["git", "describe", "--tags", "--dirty", "--always"],
            cwd=str(REPO_ROOT),
            stderr=subprocess.DEVNULL,
        )
        tag = out.decode("utf-8", errors="replace").strip()
        if tag:
            return tag
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass
    return f"dev-{int(time.time() * 1000)}"


def stamp(tag: str) -> int:
    if not MAIN_JS.exists():
        print(f"[stamp_ui_build_tag] {MAIN_JS} not found", file=sys.stderr)
        return 1
    text = MAIN_JS.read_text(encoding="utf-8")

    # Find the BUILD_TAG declaration line. We accept both the
    # placeholder (raw checkout) and an already-stamped form
    # (re-running after a previous stamp).
    needle_start = 'const BUILD_TAG = "'
    idx = text.find(needle_start)
    if idx == -1:
        print(
            "[stamp_ui_build_tag] could not locate `const BUILD_TAG = \"...\"`; skipping",
            file=sys.stderr,
        )
        return 0  # not fatal -- main.js may have been refactored
    end = text.find('"', idx + len(needle_start))
    if end == -1:
        print(
            "[stamp_ui_build_tag] malformed BUILD_TAG line (no closing quote)",
            file=sys.stderr,
        )
        return 1
    new_text = text[: idx + len(needle_start)] + tag + text[end:]

    if new_text == text:
        print(f"[stamp_ui_build_tag] already stamped: {tag}")
        return 0

    # Atomic write: write to a sibling temp file then rename.
    tmp = MAIN_JS.with_suffix(".js.tmp")
    tmp.write_text(new_text, encoding="utf-8")
    shutil.move(str(tmp), str(MAIN_JS))
    print(f"[stamp_ui_build_tag] stamped: {tag}")
    return 0


def restore() -> int:
    if not MAIN_JS.exists():
        return 0
    text = MAIN_JS.read_text(encoding="utf-8")
    needle_start = 'const BUILD_TAG = "'
    idx = text.find(needle_start)
    if idx == -1:
        return 0
    end = text.find('"', idx + len(needle_start))
    if end == -1:
        return 0
    placeholder = "%BUILD_TAG%"
    new_text = text[: idx + len(needle_start)] + placeholder + text[end:]
    if new_text == text:
        print("[stamp_ui_build_tag] already at placeholder")
        return 0
    tmp = MAIN_JS.with_suffix(".js.tmp")
    tmp.write_text(new_text, encoding="utf-8")
    shutil.move(str(tmp), str(MAIN_JS))
    print("[stamp_ui_build_tag] restored placeholder")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--restore",
        action="store_true",
        help="Reset main.js to the %%BUILD_TAG%% placeholder.",
    )
    parser.add_argument(
        "--tag",
        default=None,
        help="Override the resolved tag (otherwise uses $BUILD_TAG or git describe).",
    )
    args = parser.parse_args()
    if args.restore:
        return restore()
    tag = args.tag or resolve_tag()
    return stamp(tag)


if __name__ == "__main__":
    raise SystemExit(main())
