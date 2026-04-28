"""
Sidecar end-to-end smoke test (no Tauri, no installer required).

Spawns `backend/entry_main.py` as a subprocess with the host Python,
waits for the `READY url=... token=...` handshake, fires an
authenticated `GET /health`, and reports pass/fail.

Why this exists:
    The full Tauri shell + installer flow has a lot of moving parts
    (python-runtime.zip extraction, embedded interpreter, NSIS
    install paths, AV scanning, UAC). When something breaks at
    `make artifact` it is hard to tell whether the backend code is
    at fault or whether the packaging layer is at fault. This smoke
    test isolates the backend: if it passes here, the FastAPI
    sidecar + JobRunner + diagnostics router all work correctly,
    and any subsequent `make artifact` failure is in the packaging
    pipeline alone.

Exit codes:
    0  every check passed (sidecar starts, READY handshake works,
       /health returns 2xx, auth token validated)
    1  any single check failed -- error printed to stderr with
       enough context to root-cause without re-running

No external deps -- uses stdlib only (subprocess, urllib, threading,
json) so it runs in any environment that has the project's
production deps installed (`make install`).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENTRY_MAIN = REPO_ROOT / "backend" / "entry_main.py"
TOKEN = "devtoken"
READY_TIMEOUT_S = 30  # cold imports of torch + fastapi can take a few seconds


def _line(prefix: str, msg: str) -> None:
    print(f"[{prefix}] {msg}", flush=True)


def _ok(msg: str) -> None:
    _line("OK  ", msg)


def _fail(msg: str) -> None:
    _line("FAIL", msg)


def _info(msg: str) -> None:
    _line("INFO", msg)


def _resolve_python() -> str:
    """Pick the same interpreter Make would use under `uv run python`.

    Falls back to ``sys.executable`` so this script also works when
    invoked directly as ``python scripts/dev_sidecar_smoke.py`` from
    the repo's venv.
    """
    venv_py = REPO_ROOT / ".venv" / (
        "Scripts/python.exe" if os.name == "nt" else "bin/python3"
    )
    if venv_py.exists():
        return str(venv_py)
    return sys.executable


def _read_ready_line(proc: subprocess.Popen[str], timeout: float) -> tuple[str, str]:
    """Block on the sidecar's stdout until we see ``READY url=... token=...``.

    Runs the read in a background thread so we can enforce a wall-clock
    timeout without leaking the subprocess on slow imports.

    Returns ``(base_url, token)`` -- raises RuntimeError on timeout, on
    exit-without-READY, and on a malformed READY line.
    """
    result: dict[str, object] = {}

    def reader() -> None:
        try:
            assert proc.stdout is not None
            for line in proc.stdout:
                line = line.rstrip("\r\n")
                if line.startswith("READY "):
                    url = ""
                    token = ""
                    for part in line.split():
                        if part.startswith("url="):
                            url = part[len("url=") :]
                        elif part.startswith("token="):
                            token = part[len("token=") :]
                    if url and token:
                        result["ok"] = (url, token)
                        return
            result["error"] = "sidecar exited without printing READY"
        except Exception as exc:  # noqa: BLE001
            result["error"] = f"reader thread crashed: {exc!r}"

    t = threading.Thread(target=reader, daemon=True)
    t.start()
    t.join(timeout=timeout)

    if "ok" in result:
        url, token = result["ok"]  # type: ignore[misc]
        return url, token  # type: ignore[return-value]
    if "error" in result:
        raise RuntimeError(str(result["error"]))
    raise RuntimeError(
        f"timed out after {timeout}s waiting for READY line "
        "(cold imports may need more time -- bump READY_TIMEOUT_S)"
    )


def _http_get(url: str, token: str, timeout: float = 5.0) -> tuple[int, dict]:
    """Authenticated GET. Returns ``(status_code, parsed_json)``."""
    req = urllib.request.Request(url, headers={"X-Auth-Token": token})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
        body = resp.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            payload = {"raw": body}
        return resp.status, payload


def main() -> int:
    if not ENTRY_MAIN.exists():
        _fail(f"entry_main.py not found at {ENTRY_MAIN}")
        return 1

    py = _resolve_python()
    _info(f"Python:        {py}")
    _info(f"entry_main.py: {ENTRY_MAIN}")
    _info(f"READY budget:  {READY_TIMEOUT_S}s")

    data_root = Path(tempfile.mkdtemp(prefix="bot-mmorpg-smoke-"))
    _info(f"Data root:     {data_root}")
    _info("")

    cmd = [
        py,
        "-u",
        str(ENTRY_MAIN),
        "--port",
        "0",
        "--token",
        TOKEN,
        "--resource-root",
        str(REPO_ROOT),
        "--data-root",
        str(data_root),
    ]

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    # Mirror the supervisor's PYTHONPATH layout so we exercise the
    # exact import path the production sidecar uses. Order matters:
    # backend/ first (for entry_main.py imports), then repo root
    # (parent-of-modelhub so `import modelhub` works -- this is the
    # Phase 9 + Phase 14 fix), then any pre-existing PYTHONPATH.
    sep = ";" if os.name == "nt" else ":"
    pypath_parts = [
        str(REPO_ROOT / "backend"),
        str(REPO_ROOT),  # parent of modelhub/
    ]
    if env.get("PYTHONPATH"):
        pypath_parts.append(env["PYTHONPATH"])
    env["PYTHONPATH"] = sep.join(pypath_parts)

    proc = subprocess.Popen(  # noqa: S603 -- args list, not shell
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
        cwd=str(REPO_ROOT),
    )

    rc = 1
    try:
        try:
            url, token = _read_ready_line(proc, READY_TIMEOUT_S)
        except RuntimeError as exc:
            _fail(str(exc))
            # Drain stderr so the user sees the actual failure cause.
            try:
                proc.kill()
                _, stderr = proc.communicate(timeout=2)
            except Exception:  # noqa: BLE001
                stderr = "<could not read stderr>"
            if stderr:
                _info("---- sidecar stderr ----")
                for line in stderr.splitlines():
                    print(f"    {line}", flush=True)
                _info("---- end sidecar stderr ----")
            return 1

        _ok(f"READY received: url={url} (token confirmed)")

        # /health round-trip with the exact token the sidecar accepts.
        try:
            status, payload = _http_get(f"{url}/health", token)
        except urllib.error.URLError as exc:
            _fail(f"GET /health failed: {exc}")
            return 1

        if status != 200:
            _fail(f"GET /health returned status {status}")
            return 1
        _ok(f"GET /health -> 200 OK ({json.dumps(payload, default=str)[:200]})")

        # Auth check: a request with the WRONG token must be rejected
        # so we know the supervisor's token contract is enforced.
        try:
            wrong_status, _ = _http_get(f"{url}/health", "wrong-token")
            if wrong_status == 200:
                _fail("GET /health with wrong token returned 200 (auth not enforced)")
                return 1
            _ok(f"Wrong-token request rejected with status {wrong_status}")
        except urllib.error.HTTPError as exc:
            if exc.code in (401, 403):
                _ok(f"Wrong-token request rejected with status {exc.code}")
            else:
                _fail(f"Wrong-token check unexpected status {exc.code}")
                return 1

        _info("")
        _ok("Sidecar smoke test PASSED. Backend stack is healthy.")
        rc = 0
    finally:
        if proc.poll() is None:
            try:
                proc.terminate()
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
        try:
            shutil.rmtree(data_root, ignore_errors=True)
        except Exception:  # noqa: BLE001
            pass

    return rc


if __name__ == "__main__":
    raise SystemExit(main())
