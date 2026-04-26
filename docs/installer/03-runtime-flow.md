# 03 — Runtime Flow (what the installed .exe does)

{% raw %}
Two distinct runtime layers. Bugs at one layer often look like bugs at
the other — read carefully before editing.

## Layer A — At install time (what `BOT-MMORPG-AI_*-x64-setup.exe` does)

When the user double-clicks the setup `.exe`, the embedded NSIS
bytecode (compiled by `makensis.exe` from the rendered `installer.nsi`)
runs. It is **self-contained**: it does NOT read any external config,
template, or JSON file at runtime. Everything was baked in at build time.

What the `.exe` contains internally:
- NSIS runtime (Nullsoft's installer engine)
- Compiled bytecode of every install instruction (paths, registry,
  shortcuts, driver invocations) — derived from `installer.nsi`
- LZMA-compressed copies of every `File` directive's source bytes
  (the entire `resources/**` and `drivers/**` payload, ~220 MB)

What the `.exe` does at install time, in order:

1. Prompts UAC for admin (`RequestExecutionLevel admin`)
2. Reads `HKLM\Software\BOT-MMORPG-AI\InstallDir` for the upgrade target;
   defaults to `$PROGRAMFILES64\BOT-MMORPG-AI`
3. Shows the wizard pages (welcome → license → components → directory → install → finish)
4. Switches to `$INSTDIR` and `SetShellVarContext all` (per-machine)
5. Extracts the main binary: `File "/oname=BOT-MMORPG-AI.exe" "${MAINBINARYSRCPATH}"`
6. Iterates `{{#each resources_dirs}}` → `CreateDirectory "$INSTDIR\<dir>"`
   for every parent directory
7. Iterates `{{#each resources}}` → one `File /a /oname=<dest> <src>`
   per bundled file. Files extract under `$INSTDIR\resources\...` and
   `$INSTDIR\drivers\...` because the globs preserved those prefixes.
8. Writes registry: `HKLM\Software\BOT-MMORPG-AI\{InstallDir, Version}`
   plus the Windows uninstall registration under
   `HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall\BOT-MMORPG-AI`
9. Creates Start Menu folder + shortcuts, Desktop shortcut
10. Optionally invokes Interception and vJoy installers
11. Writes `Uninstall.exe`

After install, `$INSTDIR` looks like:

```
C:\Program Files\BOT-MMORPG-AI\
├── BOT-MMORPG-AI.exe        (~10 MB Tauri Rust binary)
├── Uninstall.exe
├── drivers\
│   ├── interception\
│   └── vjoy\vJoySetup.exe
└── resources\
    ├── backend\{entry_main.py, main_backend.py}
    ├── modelhub\{tauri.py, ...}
    ├── runtime\python-runtime.zip   (~220 MB)
    ├── scripts\
    └── versions\0.01\{1-collect_data.py, 2-train_model.py, 3-test_model.py, ...}
```

## Layer B — At app launch (what `BOT-MMORPG-AI.exe` does)

When the user double-clicks the installed app, `BOT-MMORPG-AI.exe`
(the Tauri Rust binary) runs. The single source of truth is
`src-tauri/src/main.rs`.

In order:

1. **`ensure_runtime_layout(app)`** (`main.rs:276`) creates writable scratch dirs:
   ```
   $INSTDIR\content\        \datasets\        \logs\
   $INSTDIR\models\         \runtime\py\      \runtime\tools\
   ```
   These are NOT from the installer. The .exe itself creates them on every launch.
2. **`ensure_env_file()`** writes a default `$INSTDIR\.env` if absent
3. **`ensure_python_env(app, &window)`** unpacks `resources/runtime/python-runtime.zip`
   into `$INSTDIR\runtime\py\python\` if not already extracted
4. **`start_sidecar_server(app)`** (`main.rs:975`) spawns:
   ```
   <runtime_python_exe> -u  $INSTDIR\resources\backend\entry_main.py
                            --port 0 --token <X>
                            --resource-root $INSTDIR\resources
                            --data-root    $INSTDIR
   ```
   Waits up to 5s for `READY url=http://127.0.0.1:<port> token=<X>`
   on stdout. Stashes the parsed `SidecarApi { base_url, token }`
   in `AppState::sidecar`.
5. **WebView opens** `tauri-ui/index.html`. Frontend `main.js` runs.

## How Rust resolves bundled paths at runtime

Two patterns. Both currently work after the fixes on this branch:

| Pattern | Used by | Returns |
|---|---|---|
| `app.path_resolver().resolve_resource("resources/backend/entry_main.py")` | sidecar startup | `$INSTDIR\resources\backend\entry_main.py` |
| `installation_dir().join("resources").join("versions").join(version).join(name)` | `resolve_script` | `$INSTDIR\resources\versions\0.01\<name>` |

**Critical:** the path passed to `resolve_resource` MUST include the
`resources/` prefix because Tauri 1.x's `resources/**` glob preserves
it on extraction. Pre-fix versions of this code path passed
`"backend/entry_main.py"` and silently looked at `$INSTDIR\backend\…`
which doesn't exist.

## How the Frontend wires to the backend

```
HTML button click
        │
        ▼
tauri-ui/main.js handler  (e.g. window.toggleRecord)
        │
        ▼
window.__TAURI__.invoke('start_recording', {…})
        │
        ▼
src-tauri/src/main.rs#start_recording  (async fn)
        │
        ├─► (A) api_post_with(/session/begin_recording)   <- sidecar bookkeeping
        │       (best-effort; failure logs a warning but doesn't block)
        │
        └─► (B) run_python_script(app, "1-collect_data.py", &[], …)
                spawns <runtime_python> versions/0.01/1-collect_data.py
                stdout/stderr lines → window.emit('terminal_update')
                                    → frontend logToTerminal()
                                    → in-app log console
```

Path A is bookkeeping (SessionManager state).
Path B does the actual heavy work.

For inference (`start_bot`), the Rust command resolves the active model
via the sidecar's `/modelhub/catalog` endpoint and forwards
`--model <model_dir>` to `3-test_model.py`. If no active model is set,
Rust returns a clear error and the script never spawns.

## Things that LOOK like installer bugs but aren't

The diagnostic in `06-debug-tools.md` distinguishes these cleanly:

| Symptom | Real layer |
|---|---|
| `content/` `datasets/` `logs/` empty folders appear at $INSTDIR root | Layer B — `ensure_runtime_layout` creates them. Not the installer. |
| `runtime/py/python/python.exe` exists at $INSTDIR | Layer B — `ensure_python_env` unpacked the zip. Not the installer. |
| `.env` file appears at $INSTDIR | Layer B — `ensure_env_file` wrote it. |
| "Sidecar API not ready after 5 s" | Layer B — sidecar spawn timing or import crash. Not the installer. |
| `Script '2-train_model.py' not found` | Could be either layer — the installer might have not extracted, OR the resolver is searching wrong paths. Run the diagnostic to tell which. |
{% endraw %}
