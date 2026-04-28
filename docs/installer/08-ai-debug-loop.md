# 08 — AI Debug Loop

Self-contained debugging system for capturing runtime errors and
feeding them to an AI (Claude Code, GPT, …) in a structured format
so the AI can locate and fix the bug with minimal further questions.

**Read this when:** the app is throwing an error and you want to copy
the error context into Claude Code as a single paste.

> Post-migration the bundle now includes the runtime doctor's
> structured per-check verdict (commit `b0c2ac3`) plus the on-disk
> path enrichment for torch/numpy failures (commit `52dae2e`). When
> a sidecar-owned job ends with `status=failed` the UI also surfaces
> a persistent crash-reporter notification with a one-click `[Copy
> AI Bundle]` button so the user grabs context immediately. See
> [09-architecture-end-to-end.md](./09-architecture-end-to-end.md)
> §5 for the per-check reference.

## What it is

A *parallel observation layer*, not a surgery on the existing app.
Three capture sources, two storage layers, one UI button.

```
Capture sources (passive, observe-only)
  ▸ Rust: subprocess stderr Python tracebacks
        — see src-tauri/src/main.rs#run_python_script stderr thread
  ▸ Rust: explicit record_error() helper
        — for selected Rust failure paths (currently used by the
          stderr parser; future expansion possible)
  ▸ Sidecar: FastAPI exception middleware
        — see modelhub/tauri.py @app.exception_handler(Exception)

Storage (in-memory, bounded ring buffers; no persistence)
  ▸ Rust:    Arc<Mutex<VecDeque<ErrorEntry>>> on AppStateInner, cap 50
  ▸ Sidecar: collections.deque(maxlen=50) in
             modelhub/diagnostics/collector.py

Aggregator
  ▸ Tauri command recent_errors_for_ai (src-tauri/src/main.rs)
        merges the Rust ring buffer with sidecar's
        /diagnostics/recent/ai response and produces a Markdown+JSON
        bundle.

UI surface
  ▸ Settings → System Tools → AI Fix Loop section
  ▸ Two buttons: "🤖 Copy AI Fix Request" and "🧹 Clear Captured Errors"
```

## How to use it (humans)

1. Reproduce the bug (click the button that fails, etc.)
2. Open ⚙ **Settings** in the sidebar
3. Switch to the **System Tools** tab
4. Scroll to the **AI Fix Loop** section
5. Click **🤖 Copy AI Fix Request**
6. Open Claude Code
7. Paste

The bundle goes onto your clipboard as Markdown with embedded JSON
code blocks. Each captured error is one section. Claude reads:

- The error type + message
- The primary file + line from the traceback
- The full traceback
- A `candidate_files` list pointing at modules to read first
- The recent in-app log tail (last 200 lines from the terminal)

…and proposes a minimal patch. You review and apply.

## What gets captured

| Source | Trigger | Example |
|---|---|---|
| Rust stderr parser | Spawned Python script prints `Traceback (most recent call last):` | `ModuleNotFoundError: No module named 'grabscreen'` while running `1-collect_data.py` |
| Sidecar middleware | Any unhandled exception in a FastAPI route | `KeyError` in `/modelhub/catalog` handler |

## What does NOT get captured (yet)

- Tauri command errors that return `Err(...)` to JS — these are
  already surfaced as toasts (the notification system from
  `5334a65`), but the AI bundle doesn't include them. Future
  expansion: add `record_error` calls to the Rust command bodies
  that build error strings.
- Frontend JavaScript errors — would need `window.onerror` plumbing
  back through Tauri.

Both are fine to add later without changing the existing capture
shape.

## Bundle format

The exact shape that Claude Code reads. One JSON block per error:

```json
{
  "claude_code_task": "fix_runtime_error",
  "summary": "ModuleNotFoundError: No module named 'grabscreen'",
  "source": "spawned_script",
  "timestamp_ms": 1735206567000,
  "context": {
    "spawned_script": "C:\\Program Files\\BOT-MMORPG-AI\\resources\\versions\\0.01\\1-collect_data.py"
  },
  "error": {
    "type": "ModuleNotFoundError",
    "message": "No module named 'grabscreen'",
    "primary_file": "C:\\Program Files\\BOT-MMORPG-AI\\resources\\versions\\0.01\\1-collect_data.py",
    "primary_line": 10,
    "traceback": "Traceback (most recent call last):\n  File \"...\\1-collect_data.py\", line 10, in <module>\n    from grabscreen import grab_screen\nModuleNotFoundError: ..."
  },
  "candidate_files": [
    "src-tauri/src/main.rs",
    "docs/installer/04-bug-index.md",
    "C:\\Program Files\\BOT-MMORPG-AI\\resources\\versions\\0.01\\1-collect_data.py"
  ],
  "instructions": [
    "Read each candidate_files path before proposing changes.",
    "Identify the minimal patch that fixes the root cause.",
    "Do NOT rewrite entire files. Edit targeted lines only.",
    "Reference docs/installer/04-bug-index.md for similar prior bugs."
  ]
}
```

## Files involved

| File | Role | Edit when… |
|---|---|---|
| `modelhub/diagnostics/__init__.py` | Package marker | n/a |
| `modelhub/diagnostics/collector.py` | Sidecar ring buffer | You want to capture a new sidecar error class |
| `modelhub/diagnostics/formatter.py` | Per-entry Markdown+JSON | You want to change the bundle shape (add fields, tweak instructions) |
| `modelhub/diagnostics/routes.py` | FastAPI router | You want to add new HTTP endpoints |
| `modelhub/tauri.py:223` | Hook into `_unhandled_exception_handler` | n/a — already wired |
| `modelhub/tauri.py:518` | Mount the diagnostics router | n/a — already wired |
| `src-tauri/src/main.rs#parse_python_traceback` | Rust traceback parser | You want to handle a non-Python traceback format |
| `src-tauri/src/main.rs#record_error` | Rust capture helper | You want to record from a new Rust failure site |
| `src-tauri/src/main.rs#recent_errors_for_ai` | Aggregator command | You want to change what's in the bundle |
| `src-tauri/src/main.rs#build_ai_bundle` | Rust-side bundle formatter | Same as above |
| `tauri-ui/index.html` (System Tools tab) | UI buttons + handlers | You want to change the user-visible label / add buttons |

## Design constraints (what NOT to do)

- ❌ Inject AI calls into core logic. The diagnostic layer is observe-only.
- ❌ Persist errors to disk. By design — debugging is about right-now.
- ❌ Auto-apply AI fixes. Humans review every patch.
- ❌ Replace the existing logging. `terminal_update` events still flow normally.

## Maintenance notes

- The ring buffer caps are `MAX_ERRORS=50` (Rust) and
  `_MAX_ENTRIES=50` (Python). Don't push these higher — pasting more
  than ~50 errors into an AI chat blows past every model's context.
- `parse_python_traceback` is heuristic. If a script prints something
  that looks like `SomeUppercaseLine: foo` outside a real traceback,
  it'll get captured as a false-positive error. The cost is small
  (one entry in a 50-entry buffer) and the alternative (a strict
  parser) would miss legitimate errors that fall outside the
  CPython exact format.
- Sidecar HTTP fetch in `recent_errors_for_ai` is best-effort — if
  the sidecar is offline (the very state where bugs are most
  likely), only the Rust portion ships. That's fine; the user gets
  whatever we have.
