"""
Sidecar-owned job runner for BOT-MMORPG-AI.

Background
----------
Prior to MVP-3, the Tauri Rust shell spawned every Python script
directly: training, data collection, inference. Crashes in any of
those processes would race against the parent Tauri process during
shutdown and surface as 0xC0000005 (STATUS_ACCESS_VIOLATION) with
no Python-side traceback in the UI log.

This package moves the spawn surface inside the sidecar. The Tauri
shell now POSTs `/jobs/train`, `/jobs/collect`, `/jobs/inference`
and bridges an SSE log stream to its terminal_update event. The
sidecar owns the child process tree, captures stdout + stderr into
a bounded per-job ring buffer, and exposes status / cancellation
over HTTP. The Tauri UI never spawns Python directly.

Why the sidecar instead of Rust:
  - Crashes contained inside the sidecar process tree, not propagated
    to the UI process.
  - Logs persist on the sidecar side, survive a UI restart.
  - Adding a new script becomes one new endpoint, not a new Rust
    spawn path with its own argv quoting + env handling.
  - Same observation surface as /diagnostics: in-memory ring buffer
    consumed by the AI Fix Bundle without re-implementing capture.

Modules:
  runner.py   JobRunner -- pure-Python subprocess manager (no FastAPI)
  routes.py   FastAPI APIRouter that wraps JobRunner with auth + SSE
"""
