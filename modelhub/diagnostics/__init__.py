"""
Non-invasive AI-debug-loop layer for the BOT-MMORPG-AI sidecar.

Plugs into modelhub/tauri.py via a single router include and a single
exception-handling middleware. Captures runtime errors into an
in-memory ring buffer that the Tauri Rust side aggregates with its
own error stream, then surfaces in the Settings -> System Tools UI
as a Markdown+JSON bundle the user copies into Claude Code.

Design constraints (from the originating design doc):
  - additive only: this package does not touch any existing module
  - feature-flagged off-by-default would be safe but the cost of an
    always-on 50-entry ring buffer is negligible, so it's always on
  - read-only observation: nothing here changes request/response
    semantics; middleware re-raises every exception it captures
  - human-governed: AI suggests, humans approve. We never auto-apply.

Modules:
  collector.py  ring buffer + capture API
  formatter.py  AI-ready Markdown bundle
  routes.py     FastAPI APIRouter mounted by modelhub.tauri.main()
"""
