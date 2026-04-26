"""
In-memory ring buffer for sidecar runtime errors.

Single global deque, thread-safe by GIL + a lock for the few mutating
operations that need atomicity. No persistence — by design. Errors that
matter to AI debugging are the ones happening RIGHT NOW; if the sidecar
restarts, the buffer resets and that's correct.
"""
from __future__ import annotations

import threading
import time
import traceback
from collections import deque
from typing import Any, Deque, Dict, List, Optional

# Hard cap. 50 entries keeps the AI bundle small enough to paste into
# any chat client (Claude, ChatGPT) under any context limit, while
# being deep enough to capture a multi-step failure cascade.
_MAX_ENTRIES = 50

_buffer: Deque[Dict[str, Any]] = deque(maxlen=_MAX_ENTRIES)
_lock = threading.Lock()


def capture_exception(
    exc: BaseException,
    *,
    source: str = "sidecar",
    request_path: Optional[str] = None,
    request_method: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Record a Python exception. Called from the FastAPI exception
    middleware in modelhub/tauri.py and from explicit try/except blocks
    in any sidecar module.

    Returns the entry that was stored, so the caller can echo a
    correlation id into its own logs if it wants.

    NEVER raises. If the buffer push fails for any reason we return
    a stub entry instead of letting the diagnostic layer break the
    request flow it was meant to observe.
    """
    try:
        tb_text = traceback.format_exc()
        # Strip the most recent frame's "File ..." line for a quick
        # primary-file hint. Best-effort -- if format is weird we
        # just leave it blank.
        primary_file = ""
        primary_line = 0
        for line in reversed(tb_text.splitlines()):
            stripped = line.strip()
            if stripped.startswith('File "') and ", line " in stripped:
                # Format: File "<path>", line <N>, in <fn>
                try:
                    path_part = stripped.split('File "', 1)[1].split('"', 1)[0]
                    line_part = stripped.split(", line ", 1)[1].split(",", 1)[0]
                    primary_file = path_part
                    primary_line = int(line_part)
                    break
                except (IndexError, ValueError):
                    continue

        entry = {
            "id": f"err-{int(time.time() * 1000)}-{id(exc) & 0xFFFF:x}",
            "timestamp": time.time(),
            "source": source,
            "error_type": type(exc).__name__,
            "message": str(exc),
            "traceback": tb_text,
            "primary_file": primary_file,
            "primary_line": primary_line,
            "request_path": request_path,
            "request_method": request_method,
            "extra": extra or {},
        }
        with _lock:
            _buffer.append(entry)
        return entry
    except Exception:  # noqa: BLE001
        # Diagnostic layer must never escalate. If we can't even
        # format the entry, return something inert.
        return {"id": "err-stub", "error_type": "DiagnosticInternalError"}


def capture_message(
    message: str,
    *,
    source: str = "sidecar",
    error_type: str = "ManualReport",
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Record a non-exception event the caller wants the AI to see
    (e.g. a degraded subsystem, a fallback used). Same shape as
    capture_exception so the formatter doesn't need to branch.
    """
    entry = {
        "id": f"msg-{int(time.time() * 1000)}",
        "timestamp": time.time(),
        "source": source,
        "error_type": error_type,
        "message": message,
        "traceback": "",
        "primary_file": "",
        "primary_line": 0,
        "request_path": None,
        "request_method": None,
        "extra": extra or {},
    }
    with _lock:
        _buffer.append(entry)
    return entry


def recent_errors(limit: int = _MAX_ENTRIES) -> List[Dict[str, Any]]:
    """Return the most-recent `limit` entries, newest last."""
    with _lock:
        items = list(_buffer)
    return items[-limit:] if limit > 0 else items


def clear() -> int:
    """Empty the buffer. Returns the count cleared."""
    with _lock:
        n = len(_buffer)
        _buffer.clear()
    return n


def buffer_size() -> int:
    with _lock:
        return len(_buffer)
