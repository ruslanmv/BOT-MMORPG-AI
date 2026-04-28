# 03 — Runtime Flow (what the installed .exe does)

{% raw %}
> **Updated for the post-migration model (MVP-1 through MVP-3d).**
> The pre-migration version of this doc described Tauri spawning
> Python directly. After the migration, every Python spawn goes
> through the sidecar's `/jobs` endpoint. See `09-architecture-end-to-end.md`
> for the full architectural picture.

Two distinct runtime layers. Bugs at one layer often look like bugs at
the other — read carefully before editing.

## Layer A — At install time (what `BOT-MMORPG-AI_*-x64-setup.exe` does)

When the user double-clicks the setup `.exe`, the embedded NSIS
bytecode (compiled by `makensis.exe` from the rendered `installer.nsi`)
runs. It is **self-contained**: no external config, template, or JSON
file is read at runtime. Everything was baked in at build time.

What the `.exe` contains:
- NSIS runtime (Nullsoft's installer engine)
- Compiled bytecode of every install instruction (paths, registry,
  shortcuts, driver invocations) — derived from `installer.nsi`
- LZMA-compressed copies of every `File` directive's source bytes
  (the entire `resources/**` and `drivers/**` payload, ~230 MB)

Install-time sequence:

1. Prompts UAC for admin (`RequestExecutionLevel admin`)
2. Reads `HKLM\Software\BOT-MMORPG-AI\InstallDir`; defaults to
   `$PROGRAMFILES64\BOT-MMORPG-AI`
3. Wizard pages (welcome → license → components → directory → install → finish)
4. Switches to `$INSTDIR` and `SetShellVarContext all` (per-machine)
5. Extracts the main binary: `File "/oname=BOT-MMORPG-AI.exe" "${MAINBINARYSRCPATH}"`
6. Iterates `{{#each resources_dirs}}` → `CreateDirectory "$INSTDIR\<dir>"`
   for every parent directory
7. Iterates `{{#each resources}}` → one `File /a /oname=<dest> <src>`
   per bundled file. Files extract under `$INSTDIR\resources\...` and
   `$INSTDIR\drivers\...`
8. Writes registry: `HKLM\Software\BOT-MMORPG-AI\{InstallDir, Version}`
9. Creates Start Menu folder + shortcuts, Desktop shortcut
10. Optionally invokes Interception and vJoy installers
11. Writes `Uninstall.exe`

After install, `$INSTDIR` is read-only territory:

```
C:\Program Files\BOT-MMORPG-AI\
├── BOT-MMORPG-AI.exe        Tauri Rust binary (~10 MB)
├── Uninstall.exe
├── drivers\
└── resources\
    ├── backend\entry_main.py
    ├── modelhub\
    │   ├── tauri.py                 sidecar app factory
    │   ├── diagnostics\             /diagnostics/* router
    │   └── jobs\                    /jobs/* router (MVP-3a/3b)
    │       ├── runner.py            JobRunner -- subprocess manager
    │       └── routes.py            FastAPI router + SSE
    ├── runtime\python-runtime.zip   ~230 MB, extracted on first launch
    ├── scripts\
    │   ├── runtime_doctor.py        self-test (MVP-2)
    │   ├── install_drivers.ps1
    │   └── download_models.ps1
    └── versions\0.01\               ML scripts (collect / train / test)
```

> Nothing under `$INSTDIR` is ever written to after install. All
> mutable state lives at `%LOCALAPPDATA%\com.bot.mmorpg.ai\` (see
> Layer B below). This is the MVP-1 split.

## Layer B — At app launch (what `BOT-MMORPG-AI.exe` does)

When the user double-clicks the installed app, `BOT-MMORPG-AI.exe`
(the Tauri Rust binary) runs. The single source of truth is
`src-tauri/src/main.rs`.

Launch sequence:

1. **`migrate_legacy_runtime_if_needed(app)`** (`main.rs:343`) — if a
   pre-MVP-1 install has runtime / datasets / models / logs / content
   under Program Files, move them to `%LOCALAPPDATA%\com.bot.mmorpg.ai\`.
   Idempotent. Best-effort. Never blocks startup.

2. **`ensure_runtime_layout(app)`** (`main.rs:412`) creates writable
   scratch dirs under the local-data root:
   ```
   %LOCALAPPDATA%\com.bot.mmorpg.ai\
   ├── runtime\py\           where python-runtime.zip extracts
   ├── runtime\tools\
   ├── content\
   ├── datasets\
   ├── models\
   └── logs\
   ```

3. **`ensure_default_env(app)`** writes a default
   `%LOCALAPPDATA%\com.bot.mmorpg.ai\.env` if absent.

4. **`start_sidecar_server(app)`** (`main.rs:1244`):
   - Locates the bundled python.exe at
     `%LOCALAPPDATA%\com.bot.mmorpg.ai\runtime\py\python\python.exe`.
     If not yet extracted, calls `ensure_python_env` which unpacks
     `resources/runtime/python-runtime.zip`.
   - Builds env: `PYTHONUNBUFFERED=1`, `PYTHONUTF8=1`, `PYTHONPATH`
     including `resources/backend` and `resources/modelhub` from
     Program Files.
   - Spawns:
     ```
     <bundled python> -u  $INSTDIR\resources\backend\entry_main.py
                          --port 0 --token <X>
                          --resource-root $INSTDIR\resources
                          --data-root    %LOCALAPPDATA%\com.bot.mmorpg.ai
     ```
   - **Wait loop with heartbeats:** up to 60s budget for the cold
     `import torch + fastapi + uvicorn + numpy + cv2` chain. Every
     5s emits `[Sidecar] still warming up... Ns/60s` to terminal_update
     so the UI chip shows live progress.
   - On READY line: stashes the parsed `SidecarApi { base_url, token }`
     in `AppState::sidecar`.
   - On 60s timeout: kills the child, sets
     `inner.sidecar_startup_failed = true` so subsequent api calls
     fail fast instead of hanging another 65s.

5. **WebView opens** `tauri-ui/index.html`. The frontend runs:
   - `checkInstallHealth` — invokes `install_health` + `runtime_doctor`
     in parallel. Doctor's per-check rows merge into the install-health
     banner.
   - The sidecar status chip listens on `terminal_update` heartbeats
     and reflects live state.

## How Rust resolves bundled paths at runtime

Two patterns. Both currently work after the MVP-1 path-resolver split:

| Pattern | Used by | Returns |
|---|---|---|
| `app.path_resolver().resolve_resource("resources/backend/entry_main.py")` | sidecar startup, doctor script lookup | `$INSTDIR\resources\backend\entry_main.py` (Program Files) |
| `installation_dir().join("resources").join("versions").join(version).join(name)` | `resolve_script` | `$INSTDIR\resources\versions\0.01\<name>` |
| `local_data_root(app)` (`main.rs:322`) | datasets, models, logs, runtime tree | `%LOCALAPPDATA%\com.bot.mmorpg.ai\` |

> **Critical:** the path passed to `resolve_resource` MUST include the
> `resources/` prefix because Tauri 1.x's `resources/**` glob preserves
> it on extraction. Don't pass `"backend/entry_main.py"` — that
> resolves to `$INSTDIR\backend\…` which doesn't exist.

> **Critical:** read-only resources live under `installation_dir()`
> (Program Files). Mutable runtime data lives under `local_data_root()`
> (%LOCALAPPDATA%). Two read-only-resource fallback paths in main.rs
> were fixed in MVP-1 to use `installation_dir()` instead of the
> coincidentally-correct pre-migration `local_data_root`.

## How a [Train] click becomes a Python spawn (post-MVP-3d)

```
HTML button click
        │
        ▼
tauri-ui/main.js handler  (e.g. window.toggleRecord / start_training)
        │
        ▼
window.__TAURI__.invoke('start_training', {…})
        │
        ▼
src-tauri/src/main.rs#start_training (async fn)
        │
        ├─► (A) api_post_with(/session/begin_training, {...})
        │       └─ best-effort sidecar bookkeeping; soft-fails if offline
        │
        └─► (B) start_python_script_via_sidecar(app, inner, window,
                    "train", "2-train_model.py", &[])
                │
                ├─ build_python_script_command(app, "2-train_model.py", &[], &window)
                │     └─ PythonScriptCommand { argv, env, cwd }
                │
                └─ submit_sidecar_job(inner, window, "train", argv, env, Some(cwd))
                       │
                       ├─ cancel any prior current_sidecar_job (DELETE /jobs/{prev})
                       ├─ POST /jobs  → sidecar spawns the child
                       ├─ store new job_id in inner.current_sidecar_job
                       └─ spawn_log_bridge_worker(window, inner, job_id)
                              │
                              │  every 500ms while job.status == "running":
                              │    GET /jobs/{id}/log    → emit each new line
                              │                            with "(stderr) " prefix
                              │                            for stderr stream
                              │    GET /jobs/{id}        → check terminal status
                              │
                              │  on stderr line: parse for Python traceback
                              │    record_error() → recent_errors ring buffer
                              │
                              │  on terminal status:
                              │    emit "[Sidecar] Job XYZ -> {failed|cancelled|completed}"
                              │    UI's maybeRaiseCrashNotification spawns toast
                              │      with [Copy AI Bundle] / [Run Diagnosis] actions
                              │    clear inner.current_sidecar_job slot
                              │    worker exits
```

For inference (`start_bot`), the Rust command resolves the active
model via `/modelhub/catalog` and forwards `--model <model_dir>` to
`3-test_model.py`. Same submit-via-sidecar path; just an extra
catalog lookup before the spawn.

## Crash containment

Pre-MVP-3d, a `0xC0000005` (STATUS_ACCESS_VIOLATION) from torch
teardown propagated to the Tauri parent and killed the UI. Now:

1. Sidecar spawns the child via `asyncio.create_subprocess_exec`.
2. Child crashes with 0xC0000005.
3. Sidecar's `_await_exit` task records `status=failed`,
   `exit_code=-1073741819`, leaves the buffered stderr (including
   the traceback) intact in the runner's deque.
4. Tauri's log-bridge worker observes the terminal status, surfaces
   the traceback to terminal_update, raises a crash-reporter toast.
5. UI keeps running. User can click [Copy AI Bundle] without
   relaunching.

## Things that LOOK like installer bugs but aren't

The runtime doctor + the diagnostic in `06-debug-tools.md` distinguish
these cleanly:

| Symptom | Real layer |
|---|---|
| `content/` `datasets/` `logs/` empty folders appear at `%LOCALAPPDATA%\com.bot.mmorpg.ai\` | Layer B — `ensure_runtime_layout` creates them. Not the installer. |
| `runtime/py/python/python.exe` exists at `%LOCALAPPDATA%\…` | Layer B — `ensure_python_env` unpacked the zip. Not the installer. |
| `.env` file appears at `%LOCALAPPDATA%\…` | Layer B — `ensure_default_env` wrote it. |
| "Sidecar API not ready after 65 s" | Layer B — usually cold-disk imports + AV scan. Recovery: AV exclusion + restart. |
| `torch_intact: error` with `torch_testing_dir_exists=False` | Could be either layer — see Bug #11 in `04-bug-index.md`. |
| `Script '2-train_model.py' not found` | Build-time — installer didn't extract `resources/versions/`. Check verify_installer.ps1 output. |
| `Sidecar startup failed at app launch` | Layer B — sidecar's first 60s wait timed out. UI chip shows Failed; click [↻ Restart Sidecar]. |
{% endraw %}
