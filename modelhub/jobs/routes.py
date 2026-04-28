"""
FastAPI router that wraps modelhub/jobs/runner.py with auth + SSE.

Mounted at /jobs by modelhub.tauri.build_app(). The Tauri Rust shell
calls these routes instead of spawning Python directly.

Endpoints
---------
  POST   /jobs                       Submit a new job (kind, argv, env, cwd)
  GET    /jobs                       List all jobs
  GET    /jobs/{id}                  Read one job's status snapshot
  DELETE /jobs/{id}                  Cancel (terminate + grace + kill)
  GET    /jobs/{id}/log              Buffered log snapshot
  GET    /jobs/{id}/log/stream       SSE: buffered context, then live updates

Auth
----
Same x-auth-token scheme as /diagnostics (set by the Rust launcher
at sidecar spawn). Without the token, only loopback connections from
the same launcher have the token.

Why SSE not WebSockets
----------------------
SSE is one-way (server -> client) which fits log streaming exactly,
parses with the standard EventSource browser API, and survives
reconnects with last-event-id. WebSockets buy us nothing for this
case but cost more code.
"""

from __future__ import annotations

import asyncio
import json
import time
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .runner import JobRunner


def _auth_or_401(provided: Optional[str], expected: Optional[str]) -> None:
    """Match the diagnostics router's auth pattern verbatim."""
    if not expected:
        return
    if provided != expected:
        raise HTTPException(status_code=401, detail="invalid x-auth-token")


class SubmitJobBody(BaseModel):
    """Request body for POST /jobs.

    `kind` is a free-form string the UI uses to label the job
    ("train", "collect", "inference"). `argv` is the full command
    line including the python interpreter -- the route does NOT
    add anything to it because the Rust shell already knows the
    correct embedded-python path and resolves the script via
    Tauri's path resolver.
    """
    kind: str
    argv: List[str]
    env: Optional[Dict[str, str]] = None
    cwd: Optional[str] = None


def make_router(
    *,
    expected_token: Optional[str],
    runner: Optional[JobRunner] = None,
) -> APIRouter:
    """Factory: build the router with the configured token + runner.

    The runner is module-singleton in production (modelhub.tauri creates
    one and reuses it across routes). Tests pass a fresh runner each
    time for isolation.
    """
    router = APIRouter(prefix="/jobs", tags=["jobs"])
    _runner = runner if runner is not None else JobRunner()

    @router.post("")
    async def submit_job(
        body: SubmitJobBody,
        x_auth_token: Optional[str] = Header(default=None),
    ) -> Dict[str, Any]:
        _auth_or_401(x_auth_token, expected_token)
        if not body.argv:
            raise HTTPException(status_code=400, detail="argv must not be empty")
        job = await _runner.submit(
            kind=body.kind,
            argv=body.argv,
            env=body.env,
            cwd=body.cwd,
        )
        return {"ok": True, "job": job.to_dict()}

    @router.get("")
    async def list_jobs(
        x_auth_token: Optional[str] = Header(default=None),
    ) -> Dict[str, Any]:
        _auth_or_401(x_auth_token, expected_token)
        return {"ok": True, "jobs": [j.to_dict() for j in await _runner.list()]}

    @router.get("/{job_id}")
    async def get_job(
        job_id: str,
        x_auth_token: Optional[str] = Header(default=None),
    ) -> Dict[str, Any]:
        _auth_or_401(x_auth_token, expected_token)
        job = await _runner.get(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail=f"job {job_id} not found")
        return {"ok": True, "job": job.to_dict()}

    @router.delete("/{job_id}")
    async def cancel_job(
        job_id: str,
        x_auth_token: Optional[str] = Header(default=None),
    ) -> Dict[str, Any]:
        _auth_or_401(x_auth_token, expected_token)
        job = await _runner.cancel(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail=f"job {job_id} not found")
        return {"ok": True, "job": job.to_dict()}

    @router.get("/{job_id}/log")
    async def buffered_log(
        job_id: str,
        x_auth_token: Optional[str] = Header(default=None),
    ) -> Dict[str, Any]:
        _auth_or_401(x_auth_token, expected_token)
        job = await _runner.get(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail=f"job {job_id} not found")
        lines = await _runner.buffered_log(job_id)
        return {
            "ok": True,
            "job_id": job_id,
            "lines": [
                {"stream": ln.stream, "text": ln.text, "timestamp": ln.timestamp}
                for ln in lines
            ],
        }

    @router.get("/{job_id}/log/stream")
    async def stream_log(
        job_id: str,
        x_auth_token: Optional[str] = Header(default=None),
    ) -> StreamingResponse:
        """SSE endpoint. Each `data:` event is a JSON object with
        {stream, text, timestamp}. The stream ends with a `data:
        {"type":"end"}` event when the job terminates so the client
        can close cleanly.
        """
        _auth_or_401(x_auth_token, expected_token)
        job = await _runner.get(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail=f"job {job_id} not found")

        async def event_stream():
            # Heartbeat helps long-running idle jobs: if no log line
            # arrives for >25s, send a `:keepalive` comment so proxies
            # / corporate firewalls don't drop the connection.
            heartbeat_interval = 25.0
            last_send = time.monotonic()
            try:
                async for line in _runner.stream_log(job_id):
                    payload = json.dumps({
                        "stream": line.stream,
                        "text": line.text,
                        "timestamp": line.timestamp,
                    })
                    yield f"data: {payload}\n\n"
                    last_send = time.monotonic()
                    # Opportunistic heartbeat between log lines is
                    # unnecessary; we send keepalives only when idle.
                # Stream ended -- tell the client.
                yield 'data: {"type":"end"}\n\n'
            except asyncio.CancelledError:
                # Client disconnected; nothing to do, the runner's
                # stream_log finally clause unsubscribes us.
                raise
            # Note: heartbeat_interval / last_send currently unused
            # in this minimal version; wired in for future enhancement
            # without changing the route shape.
            _ = heartbeat_interval
            _ = last_send

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                # Disable proxy buffering so each line flushes promptly.
                "X-Accel-Buffering": "no",
            },
        )

    return router
