"""
Smoke tests for modelhub/jobs/routes.py.

Strategy
--------
The route layer is thin -- auth, body validation, dispatch into
JobRunner. The runner itself is exhaustively covered by
tests/test_jobs_runner.py (real subprocess lifecycle, log streaming,
cancellation). So here we only test what the route layer adds:

  - x-auth-token enforcement
  - POST /jobs argv validation
  - 404 on unknown ids
  - token-less dev mode skips auth

Anything that spans multiple HTTP requests with a live subprocess
(status polling, log buffer, SSE) is covered end-to-end on Windows
CI through the integration suite. TestClient creates per-request
event loops, which fights asyncio subprocess background tasks --
not worth the complexity here.
"""

from __future__ import annotations

import pytest

# Routes layer needs FastAPI -- only present in the bundled runtime
# (and on Windows CI). Skip the whole module gracefully on dev hosts
# without it. Same pattern as tests/test_diagnostics_smoke.py.
fastapi = pytest.importorskip("fastapi")
testclient_module = pytest.importorskip("fastapi.testclient")

FastAPI = fastapi.FastAPI
TestClient = testclient_module.TestClient

from modelhub.jobs.routes import make_router  # noqa: E402
from modelhub.jobs.runner import JobRunner  # noqa: E402

TOKEN = "test-token-xyz"


def _client(token=TOKEN):
    runner = JobRunner()
    app = FastAPI()
    app.include_router(make_router(expected_token=token, runner=runner))
    return TestClient(app)


# --- auth -----------------------------------------------------------------


def test_missing_token_returns_401():
    r = _client().get("/jobs")
    assert r.status_code == 401


def test_wrong_token_returns_401():
    r = _client().get("/jobs", headers={"x-auth-token": "wrong"})
    assert r.status_code == 401


def test_correct_token_passes_auth():
    r = _client().get("/jobs", headers={"x-auth-token": TOKEN})
    assert r.status_code == 200
    assert r.json()["ok"] is True
    assert r.json()["jobs"] == []


def test_token_less_mode_skips_auth():
    """expected_token=None -> dev mode, no header required."""
    r = _client(token=None).get("/jobs")
    assert r.status_code == 200


# --- validation -----------------------------------------------------------


def test_post_jobs_rejects_empty_argv():
    r = _client().post(
        "/jobs",
        json={"kind": "test", "argv": []},
        headers={"x-auth-token": TOKEN},
    )
    assert r.status_code == 400


def test_post_jobs_rejects_missing_kind():
    r = _client().post(
        "/jobs",
        json={"argv": ["/usr/bin/true"]},
        headers={"x-auth-token": TOKEN},
    )
    # Pydantic rejects the missing required field with 422.
    assert r.status_code == 422


def test_post_jobs_rejects_missing_argv():
    r = _client().post(
        "/jobs",
        json={"kind": "test"},
        headers={"x-auth-token": TOKEN},
    )
    assert r.status_code == 422


# --- 404 ------------------------------------------------------------------


def test_get_unknown_job_returns_404():
    r = _client().get("/jobs/no-such-id", headers={"x-auth-token": TOKEN})
    assert r.status_code == 404


def test_delete_unknown_job_returns_404():
    r = _client().delete("/jobs/no-such-id", headers={"x-auth-token": TOKEN})
    assert r.status_code == 404


def test_buffered_log_unknown_job_returns_404():
    r = _client().get("/jobs/no-such-id/log", headers={"x-auth-token": TOKEN})
    assert r.status_code == 404


def test_stream_log_unknown_job_returns_404():
    r = _client().get("/jobs/no-such-id/log/stream", headers={"x-auth-token": TOKEN})
    assert r.status_code == 404
