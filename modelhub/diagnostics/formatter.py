"""
Format captured errors into a vendor-neutral, AI-ready bundle.

Output is Markdown with embedded JSON. Designed to be pasted into
any AI coding assistant or LLM chat that has file-read access:

  - Markdown sections so a human reading it sees structure
  - A single JSON code block per error so the model can parse it
    deterministically
  - Repo-relative file paths preferred over absolute paths so the
    assistant can pass them straight to its file-reader tool
  - Candidate file list at the top so the model knows what to load
    BEFORE reading the traceback

The formatter is pure: no imports from collector, no I/O. The
caller passes in the entries, the formatter produces a string.
"""
from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Optional


def _to_repo_relative(absolute_path: str, repo_root: Optional[str]) -> str:
    """
    Best-effort: strip repo_root from an absolute path so the assistant's
    file-reader sees a clean repo-relative arg. Returns the original
    path if repo_root is missing or doesn't match.
    """
    if not absolute_path or not repo_root:
        return absolute_path
    norm_abs = absolute_path.replace("\\", "/").rstrip("/")
    norm_root = repo_root.replace("\\", "/").rstrip("/")
    if norm_abs.lower().startswith(norm_root.lower() + "/"):
        return norm_abs[len(norm_root) + 1 :]
    return absolute_path


def _candidate_files(entry: Dict[str, Any], repo_root: Optional[str]) -> List[str]:
    """
    Heuristic: list repo files an LLM should read first when fixing
    this error. Pulls from primary_file (most recent traceback frame)
    plus a few well-known launch-path files based on `source`.
    """
    out: List[str] = []
    primary = _to_repo_relative(entry.get("primary_file") or "", repo_root)
    if primary:
        out.append(primary)

    source = entry.get("source") or ""
    # Anything that ran via the Rust subprocess launcher should
    # also point at run_python_script and resolve_script.
    if source in {"subprocess", "spawned_script"}:
        out.append("src-tauri/src/main.rs")  # run_python_script
    if source == "sidecar":
        out.append("modelhub/tauri.py")
        out.append("backend/main_backend.py")
    if source == "rust":
        out.append("src-tauri/src/main.rs")

    # Always include the bug index so the LLM checks for prior art.
    out.append("docs/installer/04-bug-index.md")

    # Dedupe preserving order
    seen = set()
    uniq: List[str] = []
    for p in out:
        if p and p not in seen:
            seen.add(p)
            uniq.append(p)
    return uniq


def format_one(entry: Dict[str, Any], repo_root: Optional[str] = None) -> Dict[str, Any]:
    """
    Convert a collector entry into the dictionary that gets serialized
    into the AI bundle. Pure transformation.
    """
    return {
        "task": "fix_runtime_error",
        "summary": f"{entry.get('error_type', 'Error')}: {entry.get('message', '')}",
        "source": entry.get("source"),
        "timestamp_iso": time.strftime(
            "%Y-%m-%dT%H:%M:%SZ", time.gmtime(entry.get("timestamp", 0))
        ),
        "context": {
            "request_path": entry.get("request_path"),
            "request_method": entry.get("request_method"),
            **(entry.get("extra") or {}),
        },
        "error": {
            "type": entry.get("error_type"),
            "message": entry.get("message"),
            "primary_file": _to_repo_relative(entry.get("primary_file") or "", repo_root),
            "primary_line": entry.get("primary_line") or 0,
            "traceback": entry.get("traceback") or "",
        },
        "candidate_files": _candidate_files(entry, repo_root),
        "instructions": [
            "Read each candidate_files path before proposing changes.",
            "Identify the minimal patch that fixes the root cause.",
            "Do NOT rewrite entire files. Edit targeted lines only.",
            "Reference docs/installer/04-bug-index.md for similar prior bugs.",
            "If the fix touches the installer or Rust runtime, also update docs/installer/05-case-studies.md with a new entry.",
        ],
    }


def format_bundle(
    entries: List[Dict[str, Any]],
    *,
    repo_root: Optional[str] = None,
    app_version: Optional[str] = None,
    install_dir: Optional[str] = None,
    log_tail: Optional[str] = None,
) -> str:
    """
    Build the final Markdown+JSON bundle the user copies and pastes.

    Layout:
        # AI Fix Request
        - app version
        - install dir
        - error count
        ## Errors
        ### Error 1 — <summary>
        ```json
        {...}
        ```
        ### Error 2 — <summary>
        ```json
        {...}
        ```
        ## Recent log tail
        ```
        ...last 200 lines from the in-app terminal...
        ```
    """
    if not entries:
        return (
            "# AI Fix Request\n\n"
            "_No errors captured this session. Reproduce the failing "
            "action first, then copy this bundle._\n"
        )

    lines: List[str] = ["# AI Fix Request", ""]
    lines.append(f"- App version: `{app_version or 'unknown'}`")
    lines.append(f"- Install dir: `{install_dir or 'unknown'}`")
    lines.append(f"- Error count: {len(entries)}")
    lines.append("")
    lines.append("## Errors")
    lines.append("")

    for i, entry in enumerate(entries, start=1):
        formatted = format_one(entry, repo_root=repo_root)
        summary = formatted["summary"]
        lines.append(f"### Error {i} — {summary}")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(formatted, indent=2))
        lines.append("```")
        lines.append("")

    if log_tail:
        lines.append("## Recent in-app log tail")
        lines.append("")
        lines.append("```")
        lines.append(log_tail.rstrip())
        lines.append("```")
        lines.append("")

    lines.append(
        "## Usage\n\n"
        "Paste this entire block into your AI coding assistant. It has "
        "enough context (error type, primary file + line, traceback, "
        "candidate files, recent log) to locate the root cause without "
        "follow-up questions. Always review the proposed patch before "
        "applying."
    )

    return "\n".join(lines) + "\n"
