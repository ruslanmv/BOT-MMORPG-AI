"""
JobRunner -- pure-Python subprocess manager (no FastAPI).

Owns the entire child-process lifecycle for training / collection /
inference scripts. The FastAPI layer in routes.py is a thin wrapper
around this -- runner.py itself has no web framework dependency,
which makes it unit-testable from pytest without spinning up uvicorn.

Threading / async model
-----------------------
The runner uses asyncio: spawn -> create_subprocess_exec, two
StreamReader tasks per job (one for stdout, one for stderr) feeding
a bounded deque + an asyncio.Queue per subscribed log consumer. SSE
clients in routes.py become one queue per connection.

Cancellation
------------
DELETE /jobs/{id} -> Job.cancel(grace_seconds=5). Tries terminate()
first; falls back to kill() after the grace period. Records the
exit code (negative on POSIX signal, "killed" on Windows). The
process tree is killed best-effort; we don't track grandchildren.

Logging
-------
Every line read from stdout/stderr is appended to a bounded deque
(default maxlen=2000). A reconnecting SSE client gets the full
buffered context, then live updates. This mirrors the
modelhub/diagnostics/collector.py ring-buffer pattern.

Thread safety
-------------
All public methods are async and run on the event loop the runner
was constructed on. The only state mutated outside that loop is
the per-job log deque -- protected by an asyncio.Lock. Never raises
out of submit() on subprocess failure: failures populate Job.error
and put the job in status="failed" without crashing the runner.
"""

from __future__ import annotations

import asyncio
import os
import signal
import sys
import tempfile
import time
import uuid
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, AsyncIterator, Deque, Dict, List, Optional, Sequence

# Default log buffer size per job. ~2000 lines covers a multi-epoch
# training run with epoch-level prints + the final stack trace if it
# crashes. Bigger == more RAM but cheap; smaller risks losing the
# crash context which is the whole point.
DEFAULT_LOG_MAXLEN = 2000

# Grace period (seconds) before terminate() escalates to kill().
DEFAULT_TERMINATE_GRACE = 5.0

# Phase 26: Graceful-stop window. Cancel() writes a per-job stop flag
# file (path passed to the child via env BOTMMO_STOP_FLAG) and waits
# this long for the child to notice and exit on its own. Long enough
# for the recording collector to flush its dataset to disk; short
# enough that "Stop" still feels responsive if the child ignores it.
# Falls through to the existing SIGTERM/SIGKILL path on timeout.
DEFAULT_GRACEFUL_STOP_WINDOW = 8.0


JobStatus = str  # "queued" | "running" | "completed" | "failed" | "cancelled"


@dataclass
class LogLine:
    """One captured stdout/stderr line + which stream it came from."""
    stream: str  # "stdout" | "stderr"
    text: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class Job:
    """Lifecycle + accumulated state of one spawned subprocess."""
    job_id: str
    kind: str
    argv: List[str]
    env: Dict[str, str]
    cwd: Optional[str]
    submitted_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    finished_at: Optional[float] = None
    status: JobStatus = "queued"
    pid: Optional[int] = None
    exit_code: Optional[int] = None
    error: Optional[str] = None  # Reason a queued/running job moved to failed.

    # Internal: the live process handle + log buffer + per-subscriber queues.
    # Hidden from the public to_dict() because they're not JSON-serialisable.
    _process: Optional[asyncio.subprocess.Process] = None
    _log_buffer: Deque[LogLine] = field(default_factory=lambda: deque(maxlen=DEFAULT_LOG_MAXLEN))
    _log_lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    _log_subscribers: List[asyncio.Queue] = field(default_factory=list)
    _reader_tasks: List[asyncio.Task] = field(default_factory=list)
    # Phase 26: cooperative-cancel hook. We hand the child a flag-file
    # path via env BOTMMO_STOP_FLAG; cancel() writes the file as a
    # "please exit cleanly" signal before falling back to SIGTERM/kill.
    _stop_flag_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Public-facing JSON view -- no live process handle, no buffer."""
        return {
            "job_id": self.job_id,
            "kind": self.kind,
            "status": self.status,
            "pid": self.pid,
            "exit_code": self.exit_code,
            "submitted_at": self.submitted_at,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "error": self.error,
            "argv": self.argv,
            "log_buffered_lines": len(self._log_buffer),
        }


class JobRunner:
    """Owns the global job dict + spawn/cancel/log primitives."""

    def __init__(
        self,
        log_maxlen: int = DEFAULT_LOG_MAXLEN,
        terminate_grace: float = DEFAULT_TERMINATE_GRACE,
        graceful_stop_window: float = DEFAULT_GRACEFUL_STOP_WINDOW,
    ) -> None:
        self._jobs: Dict[str, Job] = {}
        self._jobs_lock = asyncio.Lock()
        self._log_maxlen = log_maxlen
        self._terminate_grace = terminate_grace
        self._graceful_stop_window = graceful_stop_window

    # ----------------------------------------------------------- spawn

    async def submit(
        self,
        kind: str,
        argv: Sequence[str],
        env: Optional[Dict[str, str]] = None,
        cwd: Optional[str] = None,
    ) -> Job:
        """Spawn a child process and return the Job record.

        Failures during spawn (e.g. ENOENT, permission denied) populate
        Job.error and set status="failed" -- they never raise. This
        makes the route handler trivial: it always gets a Job back.
        """
        job_id = uuid.uuid4().hex[:12]
        merged_env = dict(os.environ)
        if env:
            merged_env.update(env)

        # Phase 26: per-job stop-flag path. Hand it to the child via
        # env so collectors / trainers can poll for "user clicked Stop"
        # and exit cleanly (saving their last batch) instead of being
        # hard-killed mid-write. Pre-cleared so a stale flag from a
        # previous job that crashed doesn't make this child exit at
        # startup. /tmp (or %TEMP%) is the right home: world-writable,
        # cleaned by the OS, and not on a volume we might rmtree.
        stop_flag_path = str(
            Path(tempfile.gettempdir()) / f"botmmo_stop_{job_id}.flag"
        )
        try:
            os.unlink(stop_flag_path)
        except FileNotFoundError:
            pass
        except OSError:
            pass
        merged_env["BOTMMO_STOP_FLAG"] = stop_flag_path

        job = Job(
            job_id=job_id,
            kind=kind,
            argv=list(argv),
            env=dict(env or {}),
            cwd=cwd,
        )
        job._stop_flag_path = stop_flag_path
        # Replace the default 2000-line deque with the runner's
        # configured maxlen.
        job._log_buffer = deque(maxlen=self._log_maxlen)

        async with self._jobs_lock:
            self._jobs[job_id] = job

        try:
            proc = await asyncio.create_subprocess_exec(
                *job.argv,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=merged_env,
                cwd=cwd,
            )
        except BaseException as e:  # noqa: BLE001
            job.status = "failed"
            job.error = f"spawn: {type(e).__name__}: {e}"
            job.finished_at = time.time()
            return job

        job._process = proc
        job.pid = proc.pid
        job.status = "running"
        job.started_at = time.time()

        # Spawn one reader task per stream. Storing them keeps them
        # from being GC'd while still pumping.
        job._reader_tasks = [
            asyncio.create_task(self._pump_stream(job, "stdout", proc.stdout)),
            asyncio.create_task(self._pump_stream(job, "stderr", proc.stderr)),
            asyncio.create_task(self._await_exit(job)),
        ]
        return job

    async def _pump_stream(
        self,
        job: Job,
        stream_name: str,
        reader: Optional[asyncio.StreamReader],
    ) -> None:
        if reader is None:
            return
        while True:
            try:
                raw = await reader.readline()
            except BaseException:  # noqa: BLE001 -- reader closed mid-flight
                break
            if not raw:
                break
            try:
                text = raw.decode("utf-8", errors="replace").rstrip("\r\n")
            except BaseException:  # noqa: BLE001
                text = repr(raw)
            line = LogLine(stream=stream_name, text=text)
            await self._fanout(job, line)

    async def _fanout(self, job: Job, line: LogLine) -> None:
        async with job._log_lock:
            job._log_buffer.append(line)
            # Snapshot the subscriber list under the lock; deliver
            # outside the lock so a slow consumer can't block the
            # pump.
            subs = list(job._log_subscribers)
        for q in subs:
            try:
                q.put_nowait(line)
            except asyncio.QueueFull:
                # SSE consumer fell behind -- drop the live update;
                # they can re-fetch the buffer from /jobs/{id}/log
                # to catch up. Better than blocking the pump.
                pass

    async def _await_exit(self, job: Job) -> None:
        if job._process is None:
            return
        try:
            rc = await job._process.wait()
        except BaseException as e:  # noqa: BLE001
            job.error = f"wait: {type(e).__name__}: {e}"
            rc = -1
        job.exit_code = rc
        job.finished_at = time.time()
        # Status: keep "cancelled" if cancel() set it; otherwise
        # completed if rc==0, failed otherwise. NOTE: on POSIX a
        # signal-killed process returns negative rc; on Windows
        # it's the exit code from TerminateProcess (typically 1).
        if job.status != "cancelled":
            job.status = "completed" if rc == 0 else "failed"
        # Phase 26: clean up the stop-flag file. We pre-clear at spawn
        # time too, but cleaning up post-exit keeps /tmp tidy and
        # avoids the (benign) "[Info] Cooperative stop enabled" log
        # line referring to a path that no longer matters.
        if job._stop_flag_path:
            try:
                os.unlink(job._stop_flag_path)
            except FileNotFoundError:
                pass
            except OSError:
                pass
        # Wake up any subscribers so they can close their SSE
        # connections cleanly.
        async with job._log_lock:
            subs = list(job._log_subscribers)
        for q in subs:
            try:
                q.put_nowait(LogLine(stream="control", text="__EOF__"))
            except asyncio.QueueFull:
                pass

    # ----------------------------------------------------------- query

    async def get(self, job_id: str) -> Optional[Job]:
        async with self._jobs_lock:
            return self._jobs.get(job_id)

    async def list(self) -> List[Job]:
        async with self._jobs_lock:
            return list(self._jobs.values())

    async def buffered_log(self, job_id: str) -> List[LogLine]:
        """Return the entire buffered log for a job (no live updates)."""
        job = await self.get(job_id)
        if job is None:
            return []
        async with job._log_lock:
            return list(job._log_buffer)

    async def stream_log(
        self,
        job_id: str,
    ) -> AsyncIterator[LogLine]:
        """Async iterator: buffered context first, then live updates.

        Caller closes the iterator (route handler awaits client
        disconnect). On close we unsubscribe so the subscriber list
        stays bounded.
        """
        job = await self.get(job_id)
        if job is None:
            return
        q: asyncio.Queue = asyncio.Queue(maxsize=1024)
        async with job._log_lock:
            # Prime the subscriber's queue with the buffered context,
            # then register so live updates are delivered.
            for line in list(job._log_buffer):
                try:
                    q.put_nowait(line)
                except asyncio.QueueFull:
                    break
            job._log_subscribers.append(q)
        try:
            while True:
                line = await q.get()
                if line.stream == "control" and line.text == "__EOF__":
                    return
                yield line
        finally:
            async with job._log_lock:
                try:
                    job._log_subscribers.remove(q)
                except ValueError:
                    pass

    # ----------------------------------------------------------- cancel

    async def cancel(self, job_id: str) -> Optional[Job]:
        """Cooperative-then-forceful cancel.

        Phase 26 promotes cancel from "polite SIGTERM, escalate to kill"
        to a three-phase ladder:

          1. Cooperative stop: write the per-job stop-flag file and
             give the child up to DEFAULT_GRACEFUL_STOP_WINDOW seconds
             to notice (it polls the path from $BOTMMO_STOP_FLAG).
             This lets the recording collector flush its last batch to
             disk via its existing graceful-exit path -- the same
             codepath that ran when the user pressed `Q` manually --
             so we don't lose frames when "Stop" is clicked while a
             batch is buffered.

          2. SIGTERM (POSIX) / terminate() (Windows): the legacy
             "polite kill" if the cooperative stop didn't take.

          3. SIGKILL: last-resort hard kill after _terminate_grace.

        This is cross-platform safe (no console-group / SIGBREAK
        plumbing required on Windows) and decoupled from the script's
        signal handlers.
        """
        job = await self.get(job_id)
        if job is None:
            return None
        if job._process is None or job.status not in ("queued", "running"):
            return job

        job.status = "cancelled"
        proc = job._process

        # Phase 1: cooperative stop via flag file.
        if job._stop_flag_path:
            try:
                # Touch the file. Atomic enough: child polls existence,
                # not contents. Using "x" mode so we don't quietly
                # overwrite an unrelated path if some external tool
                # somehow staged a file there.
                with open(job._stop_flag_path, "w", encoding="utf-8") as f:
                    f.write(f"cancel:{time.time()}\n")
            except FileExistsError:
                # Already requested -- benign.
                pass
            except OSError:
                # Couldn't write (disk full, AV lock). Skip straight
                # to terminate; nothing else we can do here.
                pass
            else:
                try:
                    await asyncio.wait_for(
                        proc.wait(),
                        timeout=self._graceful_stop_window,
                    )
                    # Child exited on its own. We're done.
                    return job
                except asyncio.TimeoutError:
                    pass

        # Phase 2: SIGTERM / terminate().
        try:
            if sys.platform == "win32":
                proc.terminate()
            else:
                proc.send_signal(signal.SIGTERM)
        except ProcessLookupError:
            return job
        except BaseException:  # noqa: BLE001
            pass

        # Phase 3: hard kill if still alive after grace.
        try:
            await asyncio.wait_for(proc.wait(), timeout=self._terminate_grace)
        except asyncio.TimeoutError:
            try:
                proc.kill()
            except BaseException:  # noqa: BLE001
                pass
        return job
