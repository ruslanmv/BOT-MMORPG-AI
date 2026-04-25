#!/usr/bin/env python3
"""
Resolve the build version for the installer.

Resolution order:
  1. The VERSION environment variable, if set and looks like semver.
  2. `git describe --tags --always` -- normalise:
       leading "v" stripped, "-dirty" suffix dropped.
     If it doesn't start with N.N.N (e.g. tagless tree, returns a bare
     SHA), prefix with "0.0.0-dev." so the result is still valid semver
     (Tauri / NSIS reject anything else).
  3. Fall back to "0.0.0-dev".

Why a Python script instead of pure $(shell ...) in the Makefile:
  On Windows, GNU make often invokes cmd.exe for $(shell ...). cmd.exe
  has no `sed`, no `grep`, no useful pipe semantics. The earlier
  Makefile version assumed Bash + sed + grep and silently produced an
  empty VERSION on Windows, which made `make artifact` ship the
  static "1.0.0" baked into tauri.conf.json. Pure Python avoids the
  shell-portability hazard.

Output: prints the resolved semver to stdout. Always exits 0.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys

_SEMVER_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+([-+][0-9A-Za-z.+\-]+)?$")
_PREFIX_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+")


def _normalise(raw: str) -> str:
    raw = raw.strip()
    if not raw:
        return ""
    if raw.startswith("v"):
        raw = raw[1:]
    # Drop only the literal "-dirty" suffix git appends, not arbitrary
    # post-tag content like "0.2.1-3-gabc1234".
    if raw.endswith("-dirty"):
        raw = raw[: -len("-dirty")]
    return raw


def _from_git() -> str:
    try:
        out = subprocess.check_output(
            ["git", "describe", "--tags", "--always"],
            stderr=subprocess.DEVNULL,
        )
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return ""
    return _normalise(out.decode("utf-8", errors="replace"))


def resolve() -> str:
    explicit = (os.environ.get("VERSION") or "").strip()
    if explicit:
        explicit = _normalise(explicit)
        if _SEMVER_RE.match(explicit):
            return explicit
        # Non-semver explicit: still keep it but coerce.
        return f"0.0.0-dev.{explicit}" if not _PREFIX_RE.match(explicit) else explicit

    derived = _from_git()
    if not derived:
        return "0.0.0-dev"

    if _PREFIX_RE.match(derived):
        return derived

    # Bare SHA / non-semver: wrap so tauri / NSIS accept it.
    # Strip any chars that aren't valid in a semver pre-release identifier.
    safe = re.sub(r"[^0-9A-Za-z.\-]", "", derived) or "unknown"
    return f"0.0.0-dev.{safe}"


def main() -> int:
    print(resolve())
    return 0


if __name__ == "__main__":
    sys.exit(main())
