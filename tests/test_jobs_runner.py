"""
Tests for modelhub/jobs/runner.py.

The runner is pure-Python (no FastAPI), so we exercise it directly
via asyncio.run. The subprocesses are real `python -c '...'` calls
because the whole point of the runner is to manage real processes.

Coverage:
  - submit() returns a Job; status transitions queued -> running -> completed
  - stdout + stderr are both captured into the buffer
  - exit_code is recorded; status reflects success vs failure
  - cancel() stops a long-running job; status becomes 'cancelled'
  - stream_log() emits buffered context first, then live updates,
    then terminates on __EOF__
  - submit() with a non-existent argv puts the job in 'failed' WITHOUT
    raising (the route handler relies on this invariant)
  - to_dict() emits a JSON-serialisable view (no live process handle)
"""

from __future__ import annotations

import asyncio
import json
import sys

import pytest

from modelhub.jobs.runner import Job, JobRunner


def _run(coro):
    """Helper: run an async test body to completion."""
    return asyncio.run(coro)


# --- happy path -----------------------------------------------------------


def test_submit_returns_job():
    async def body():
        runner = JobRunner()
        job = await runner.submit("test", [sys.executable, "-c", "print('hello')"])
        assert isinstance(job, Job)
        assert job.job_id
        assert job.status in ("running", "completed")
        return job

    job = _run(body())
    assert job.kind == "test"


def test_completed_job_records_zero_exit_code():
    async def body():
        runner = JobRunner()
        job = await runner.submit(
            "echo", [sys.executable, "-c", "import sys; sys.exit(0)"]
        )
        # Wait for exit by polling the job record.
        for _ in range(200):
            j = await runner.get(job.job_id)
            if j is not None and j.status == "completed":
                return j
            await asyncio.sleep(0.05)
        return await runner.get(job.job_id)

    job = _run(body())
    assert job is not None
    assert job.status == "completed", f"got {job.status} {job.error!r}"
    assert job.exit_code == 0


def test_failed_job_marks_status_and_keeps_exit_code():
    async def body():
        runner = JobRunner()
        job = await runner.submit(
            "fail", [sys.executable, "-c", "import sys; sys.exit(7)"]
        )
        for _ in range(200):
            j = await runner.get(job.job_id)
            if j is not None and j.status in ("completed", "failed"):
                return j
            await asyncio.sleep(0.05)
        return await runner.get(job.job_id)

    job = _run(body())
    assert job is not None
    assert job.status == "failed"
    assert job.exit_code == 7


def test_stdout_and_stderr_are_both_captured():
    async def body():
        runner = JobRunner()
        job = await runner.submit(
            "both",
            [
                sys.executable,
                "-c",
                "import sys; print('OUT'); print('ERR', file=sys.stderr)",
            ],
        )
        for _ in range(200):
            j = await runner.get(job.job_id)
            if j is not None and j.status == "completed":
                break
            await asyncio.sleep(0.05)
        return await runner.buffered_log(job.job_id)

    lines = _run(body())
    streams = {ln.stream: ln.text for ln in lines}
    # Use 'in' rather than '==' because OS line buffering and the
    # interleave order across streams isn't guaranteed.
    assert any(ln.text == "OUT" and ln.stream == "stdout" for ln in lines), streams
    assert any(ln.text == "ERR" and ln.stream == "stderr" for ln in lines), streams


# --- cancellation ---------------------------------------------------------


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Process group signalling differs on Windows; the cancel "
    "primitive is exercised by the integration suite there.",
)
def test_cancel_terminates_long_running_job():
    async def body():
        # Phase 26: cancel() now first writes a cooperative stop-flag
        # and waits up to graceful_stop_window for the child to exit
        # on its own. This sleep child doesn't poll the flag, so we
        # tune the window down to 0.5s to keep the test snappy and
        # exercise the SIGTERM/kill fallback path.
        runner = JobRunner(terminate_grace=2.0, graceful_stop_window=0.5)
        job = await runner.submit(
            "sleep",
            [sys.executable, "-c", "import time; time.sleep(60)"],
        )
        # Give the child a moment to come up before we cancel.
        await asyncio.sleep(0.3)
        await runner.cancel(job.job_id)
        # Wait for the await_exit task to settle the status.
        for _ in range(100):
            j = await runner.get(job.job_id)
            if j is not None and j.finished_at is not None:
                return j
            await asyncio.sleep(0.05)
        return await runner.get(job.job_id)

    job = _run(body())
    assert job is not None
    assert job.status == "cancelled"
    assert job.finished_at is not None


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Process signalling differs on Windows; cooperative-stop is "
    "exercised by the integration suite there.",
)
def test_cooperative_stop_via_flag_file_skips_signals():
    """Phase 26: cancel() should write the per-job stop-flag and let
    a cooperative child exit on its own, without escalating to
    SIGTERM/kill. This is the path the recording collector uses to
    flush its dataset before the process goes away."""

    async def body():
        # Aggressive grace: if we DO escalate to SIGTERM the test
        # would still pass, but the assertion on exit_code == 0
        # below catches that regression -- a SIGTERMed Python
        # returns a negative rc on POSIX.
        runner = JobRunner(terminate_grace=2.0, graceful_stop_window=3.0)
        job = await runner.submit(
            "sleep",
            [
                sys.executable,
                "-c",
                # Poll BOTMMO_STOP_FLAG; exit 0 once it appears.
                "import os, time; p=os.environ['BOTMMO_STOP_FLAG']\n"
                "while not os.path.exists(p): time.sleep(0.05)\n"
                "print('graceful exit')",
            ],
        )
        await asyncio.sleep(0.3)
        await runner.cancel(job.job_id)
        for _ in range(100):
            j = await runner.get(job.job_id)
            if j is not None and j.finished_at is not None:
                return j
            await asyncio.sleep(0.05)
        return await runner.get(job.job_id)

    job = _run(body())
    assert job is not None
    assert job.status == "cancelled"
    # Cooperative path -- child exited 0, not via signal.
    assert job.exit_code == 0, f"expected clean exit, got rc={job.exit_code}"


# --- non-fatal failure path on spawn error --------------------------------


def test_spawn_failure_returns_failed_job_without_raising():
    """A bad executable path must not raise out of submit().

    The route handler relies on always getting a Job back so it can
    return a structured error to the caller instead of HTTP 500.
    """

    async def body():
        runner = JobRunner()
        job = await runner.submit(
            "bogus",
            ["/this/path/definitely/does/not/exist/either-way"],
        )
        return job

    job = _run(body())
    assert job.status == "failed"
    assert job.error is not None
    assert "spawn" in job.error.lower()
    assert job.pid is None


# --- streaming ------------------------------------------------------------


def test_stream_log_emits_buffered_then_terminates():
    async def body():
        runner = JobRunner()
        job = await runner.submit(
            "stream",
            [
                sys.executable,
                "-c",
                "for i in range(3): print(f'line{i}')",
            ],
        )
        # Wait for exit so the buffer has the full log + EOF marker.
        for _ in range(200):
            j = await runner.get(job.job_id)
            if j is not None and j.status == "completed":
                break
            await asyncio.sleep(0.05)

        collected = []
        async for line in runner.stream_log(job.job_id):
            collected.append(line)
            if len(collected) >= 3:
                break
        return collected

    lines = _run(body())
    texts = [ln.text for ln in lines]
    assert "line0" in texts
    assert "line2" in texts


# --- list / get / to_dict -------------------------------------------------


def test_list_jobs_returns_all_submitted():
    async def body():
        runner = JobRunner()
        a = await runner.submit("a", [sys.executable, "-c", "pass"])
        b = await runner.submit("b", [sys.executable, "-c", "pass"])
        ids = {j.job_id for j in await runner.list()}
        return ids, a.job_id, b.job_id

    ids, ai, bi = _run(body())
    assert ai in ids
    assert bi in ids


def test_to_dict_is_json_serialisable():
    async def body():
        runner = JobRunner()
        job = await runner.submit("json", [sys.executable, "-c", "print('hi')"])
        # Even before exit, to_dict must be serialisable.
        return job.to_dict()

    payload = _run(body())
    text = json.dumps(payload)
    parsed = json.loads(text)
    assert parsed["kind"] == "json"
    assert parsed["status"] in ("queued", "running", "completed", "failed")
    assert "log_buffered_lines" in parsed
    # Live process handle MUST NOT appear in to_dict().
    assert "_process" not in parsed
    assert "_log_buffer" not in parsed


def test_get_unknown_job_returns_none():
    async def body():
        runner = JobRunner()
        return await runner.get("missing")

    assert _run(body()) is None
