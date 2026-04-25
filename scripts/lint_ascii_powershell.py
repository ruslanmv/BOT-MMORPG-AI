#!/usr/bin/env python3
"""
Fail CI if any .ps1/.psm1 file under scripts/ contains non-ASCII bytes,
or if any .github/workflows/*.yml contains non-ASCII bytes outside an
explicit `body: |` block (release-note bodies are rendered by GitHub
as Markdown and never executed; emoji there is fine).

Why this exists
---------------
The Release workflow on Windows runners spawns
    powershell -File scripts/<thing>.ps1
which is Windows PowerShell 5.1, NOT pwsh. PS 5.1 decodes source files
per the system ANSI codepage (CP-1252 on the GitHub runners) when the
file lacks a UTF-8 BOM. UTF-8 byte sequences like the check-mark glyph
get mis-decoded as garbage, the string-literal parser fails inside the
function body, the function never registers, and later calls error out
with "Write-Info is not recognized". This script blocks PRs from
re-introducing that hazard.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent


def find_files() -> tuple[list[Path], list[Path]]:
    ps = sorted(
        list((REPO / "scripts").rglob("*.ps1"))
        + list((REPO / "scripts").rglob("*.psm1"))
    )
    yml = sorted(
        list((REPO / ".github" / "workflows").rglob("*.yml"))
        + list((REPO / ".github" / "workflows").rglob("*.yaml"))
    )
    return ps, yml


def scan_powershell(path: Path) -> list[tuple[int, str]]:
    """Return [(line_no, line_text)] of any line containing non-ASCII."""
    bad = []
    text = path.read_bytes().decode("utf-8", errors="replace")
    for n, line in enumerate(text.splitlines(), 1):
        if any(ord(c) > 127 for c in line):
            bad.append((n, line))
    return bad


_BODY_OPEN = re.compile(r"^(?P<indent>\s*)body:\s*\|\s*$")


def scan_workflow_yaml(path: Path) -> list[tuple[int, str]]:
    """
    Return non-ASCII offenders in a workflow YAML, exempting any line that
    is part of a `body: |` block (release notes -- emoji is fine there).
    """
    bad = []
    text = path.read_bytes().decode("utf-8", errors="replace")
    in_body = False
    body_indent = 0
    for n, line in enumerate(text.splitlines(), 1):
        m = _BODY_OPEN.match(line)
        if m:
            in_body = True
            body_indent = len(m.group("indent"))
            continue
        if in_body:
            if not line.strip():
                continue  # blank line stays in block
            leading = len(line) - len(line.lstrip())
            if leading > body_indent:
                continue  # still inside the body block
            in_body = False  # de-dented; fall through to check this line
        if any(ord(c) > 127 for c in line):
            bad.append((n, line))
    return bad


def main() -> int:
    ps_files, yml_files = find_files()

    failed = False
    for f in ps_files:
        offenders = scan_powershell(f)
        if offenders:
            failed = True
            rel = f.relative_to(REPO)
            print(
                f"::error file={rel}::Non-ASCII content in a PowerShell file. "
                f"Windows PowerShell 5.1 mis-decodes UTF-8 without a BOM; "
                f"use ASCII sentinels like [OK]/[FAIL]/[INFO]."
            )
            for n, line in offenders[:5]:
                print(f"  {rel}:{n}: {line}")

    for f in yml_files:
        offenders = scan_workflow_yaml(f)
        if offenders:
            failed = True
            rel = f.relative_to(REPO)
            print(
                f"::error file={rel}::Non-ASCII outside a `body: |` block in a "
                f"workflow YAML. Run-blocks may execute under PowerShell 5.1; "
                f"keep them ASCII."
            )
            for n, line in offenders[:5]:
                print(f"  {rel}:{n}: {line}")

    if failed:
        return 1

    print(
        f"OK: scanned {len(ps_files)} PowerShell file(s) and "
        f"{len(yml_files)} workflow YAML file(s); all clean."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
