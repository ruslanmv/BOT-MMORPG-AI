# 09 — Architecture End-to-End (post-migration)

{% raw %}
**The single doc that explains how the whole stack works today and
where the live issues are.** Read this before any of the older docs
in this folder — some still describe the pre-migration model.

If you only have ten minutes, read §1, §6, §7.

## §1 — One paragraph summary

`BOT-MMORPG-AI.exe` is a Tauri 1.x desktop app. At launch it extracts
a bundled embedded-Python runtime into the user's `%LOCALAPPDATA%`,
spawns a local FastAPI sidecar over loopback, and hands every Python
spawn (data collection, training, inference) to the sidecar via
`POST /jobs`. The Tauri shell never spawns Python directly anymore.
The runtime doctor (`scripts/runtime_doctor.py`) runs at every launch
to validate the bundled runtime is intact and surfaces specific check
failures into the install-health banner. When something fails, the
user has a four-button recovery ladder before having to reinstall.

## §2 — Where things live on the user's disk

After install + first launch:

```
C:\Program Files\BOT-MMORPG-AI\         ← installer-owned, READ-ONLY
├── BOT-MMORPG-AI.exe                    Tauri Rust binary
├── Uninstall.exe
├── drivers\
│   ├── interception\install-interception.exe
│   └── vjoy\vJoySetup.exe
└── resources\
    ├── backend\entry_main.py            sidecar entry point
    ├── modelhub\                        sidecar Python package
    │   ├── tauri.py                     FastAPI app factory
    │   ├── diagnostics\                 /diagnostics/* routes
    │   └── jobs\                        /jobs/* routes (MVP-3a/3b)
    │       ├── runner.py                JobRunner -- subprocess manager
    │       └── routes.py                FastAPI router + SSE
    ├── runtime\
    │   └── python-runtime.zip           ~230 MB, extracted on first launch
    ├── scripts\
    │   ├── install_drivers.ps1
    │   ├── runtime_doctor.py            self-test (MVP-2)
    │   └── download_models.ps1
    └── versions\0.01\
        ├── 1-collect_data.py            data collection
        ├── 2-train_model.py             training
        ├── 3-test_model.py              inference
        └── ...

%LOCALAPPDATA%\com.bot.mmorpg.ai\        ← user-owned, READ-WRITE
├── runtime\py\python\                    extracted from python-runtime.zip
│   ├── python.exe                        the bundled interpreter
│   └── site-packages\                    torch, fastapi, uvicorn, numpy, cv2, ...
├── datasets\                             user-recorded training data
├── models\                               trained model checkpoints
├── logs\                                 sidecar + Tauri logs
├── content\                              ML artifacts (caches, presets)
└── .env                                  AI_PROVIDER + API keys
```

**Why this split:** the Program Files tree never needs to be written to
after install — it's signed installer territory. All mutable state lives
under `%LOCALAPPDATA%` so the app runs without admin elevation, pip
self-repair works, AV-quarantine recovery works, and the install dir
can be on a read-only volume if IT policy demands it.

**Migration:** if a user upgrades from a pre-MVP-1 install (where the
runtime tree lived under Program Files), `migrate_legacy_runtime_if_needed`
in `src-tauri/src/main.rs:343` moves the legacy data to the new location
on first launch. Idempotent, best-effort, never blocks startup.

## §3 — Three processes, three responsibilities

```
┌──────────────────────────────────────────┐
│  BOT-MMORPG-AI.exe         (Tauri shell) │   PROCESS A
│  - WebView (UI)                          │
│  - Rust core                             │
│  - HTTP client to sidecar                │
│  - Spawns sidecar, never spawns Python   │
└──────────────────┬───────────────────────┘
                   │ HTTP / loopback
                   ▼
┌──────────────────────────────────────────┐
│  python.exe (sidecar)      (FastAPI)     │   PROCESS B
│  - /health, /modelhub/*                  │
│  - /diagnostics/*                        │
│  - /jobs/*  (POST submits ML script)     │
│  - JobRunner: owns ML subprocess tree    │
└──────────────────┬───────────────────────┘
                   │ asyncio.create_subprocess_exec
                   ▼
┌──────────────────────────────────────────┐
│  python.exe (job)          (script)      │   PROCESS C
│  - 1-collect_data.py / 2-train_model.py  │
│    / 3-test_model.py                     │
│  - stdout + stderr captured into the     │
│    sidecar's per-job ring buffer         │
│  - on crash: status=failed, exit_code    │
│    surfaces to UI; sidecar survives      │
└──────────────────────────────────────────┘
```

**Each process owns exactly one concern.** A crash in C cannot kill B
(the runner catches `_await_exit` and records exit_code). A crash in B
cannot kill A (Tauri's HTTP client times out and the chip flips to
Failed). Pre-MVP-3d, processes B and C were the same as A spawning
Python directly — a single 0xC0000005 from torch teardown would take
down the UI alongside the script.

## §4 — How the user's click becomes a Python spawn

Old flow (pre-MVP-3d):

```
[Train] click → invoke('start_training') → Tauri spawns python.exe →
crash → 0xC0000005 propagates → UI dies
```

Current flow (post-MVP-3d):

```
[Train] click
   │
   ▼
window.__TAURI__.invoke('start_training', {...})
   │
   ▼
src-tauri/src/main.rs#start_training (async)
   │
   ├─ build_python_script_command(app, "2-train_model.py", &[], &window)
   │     → resolves bundled python.exe in %LOCALAPPDATA%
   │     → resolves script path in Program Files\resources\versions\0.01
   │     → composes PYTHONPATH (script dir + site-packages)
   │     → injects BOT_VERSION_DIR + AI_PROVIDER + GEMINI_API_KEY etc.
   │     → returns PythonScriptCommand { argv, env, cwd }
   │
   ▼
submit_sidecar_job(inner, window, "train", argv, env, cwd)
   │
   ├─ if a previous sidecar job is still running → DELETE /jobs/{prev_id}
   │
   ▼
api_post_with("/jobs", payload)   ← HTTP POST to sidecar
   │
   ▼
modelhub/jobs/routes.py::submit_job
   │
   ▼
JobRunner.submit("train", argv, env, cwd)
   │
   ├─ asyncio.create_subprocess_exec(*argv, env=merged, cwd=cwd)
   ├─ spawn _pump_stream(stdout) + _pump_stream(stderr) tasks
   ├─ spawn _await_exit task
   └─ return Job snapshot {job_id, status, pid}
                 │
                 ▼
       payload.job.job_id stored in
       inner.current_sidecar_job slot
                 │
                 ▼
       spawn_log_bridge_worker(window, inner, job_id)
                 │
                 │  every 500ms:
                 │    GET /jobs/{id}/log     → emit new lines to UI
                 │    GET /jobs/{id}         → check terminal status
                 │
                 │  on stderr line:
                 │    parse for Python traceback
                 │    record_error() into recent_errors ring buffer
                 │
                 │  on terminal status:
                 │    emit "[Sidecar] Job XYZ -> {completed|failed|cancelled}"
                 │    UI's maybeRaiseCrashNotification spawns a toast
                 │      with [Copy AI Bundle] / [Run Diagnosis] actions
                 ▼
            worker exits, slot cleared
```

**The poll-every-500ms log bridge** is intentional simplicity. The
sidecar exposes SSE on `/jobs/{id}/log/stream` for any future browser
consumer, but reqwest's bytes_stream needs feature flags + a line
decoder. Recording / training scripts print at most a few times per
second, so 500ms latency is invisible.

## §5 — Runtime doctor — what every check means

`scripts/runtime_doctor.py --selftest` outputs JSON with one row per
check. The Tauri command `runtime_doctor` invokes it under the bundled
python.exe and returns the JSON to the UI. The result drives the
install-health banner AND is appended to the AI Fix Bundle.

| Check | What it asserts | If it fails |
|---|---|---|
| `python_boot` | Bundled python.exe loads | Runtime tree corrupt; click `[🔧 Repair Runtime]` |
| `vc_redist` | `vcruntime140.dll` + `msvcp140.dll` present in System32 | Install vc_redist.x64.exe from Microsoft |
| `torch_intact` | `torch + torch.testing + torch.fx + torch.nn` all importable | Click `[🛡 Add AV Exclusion]` then `[🔧 Repair Runtime]`; if still broken, `[🩺 Repair PyTorch (pip)]` |
| `torchvision_intact` | `torchvision` import succeeds | Usually downstream of `torch_intact` failure -- fix that first |
| `numpy_intact` | `numpy + numpy.testing` importable | Same recovery as `torch_intact` |
| `fastapi_intact` | `fastapi + uvicorn` importable + version recorded | Sidecar can't run -- `[🔧 Repair Runtime]` |
| `cv2_intact` | `opencv-python` importable | Recording script will crash -- `[🔧 Repair Runtime]` |
| `data_dir_writable` | Write probe to `%LOCALAPPDATA%` succeeds | OS / disk permission issue -- not in app's power to fix |
| `sidecar_port_bindable` | 127.0.0.1 ephemeral bind succeeds | Loopback firewall blocking -- whitelist the binary |

**Enriched failure detail (commit `52dae2e`):** when `torch_intact` or
`numpy_intact` fails, the detail also reports `torch_root=<path>`
and `torch_testing_dir_exists=<bool>`. The boolean is the smoking gun
for AV-quarantine: the import error AND the directory missing from
disk = an external actor (Defender) deleted it after extraction.

## §6 — Where bugs actually live (current state)

Mapping symptom → file → ownership tier.

| Symptom | Owning file | Tier |
|---|---|---|
| Installer doesn't run / wrong shortcuts | `installer/nsis_template.nsi` | Build-time |
| Build fails at integrity check | `scripts/build_pipeline.ps1` (line 622-634) | Build-time |
| Sidecar never starts (READY line not seen in 60s) | `src-tauri/src/main.rs#start_sidecar_server` (line 1244) | Tauri shell |
| Sidecar starts but `/health` returns 500 | `modelhub/tauri.py` exception middleware | Sidecar |
| `POST /jobs` returns "argv must not be empty" | `modelhub/jobs/routes.py::submit_job` | Sidecar |
| Job submitted but logs never stream | `src-tauri/src/main.rs#spawn_log_bridge_worker` | Tauri shell |
| Training crashes with traceback | `versions/0.01/2-train_model.py` | ML script |
| Doctor says `torch_testing_dir_exists=False` | Pre-MVP-4 zip OR runtime AV quarantine | Build-time OR runtime |
| `[Add AV Exclusion]` UAC prompt fails | `src-tauri/src/main.rs#add_av_exclusion` | Tauri shell |
| `[Repair Runtime]` re-extracts but doctor still red | The bundled zip itself is corrupt -- need `[🩺 Repair PyTorch (pip)]` | Build-time |

For each, jump to the file and grep for the function name. Each is
heavily commented because the migration history demanded it.

## §7 — Known unfixed surfaces (where the next session should focus)

1. **First-launch on very slow HDDs.** `start_sidecar_server` budgets
   60s for the bundled python's `import torch + fastapi + uvicorn +
   numpy + cv2` chain. Reports of slower disks (older spindles,
   network drives) may still time out. **Fix path:** make the budget
   adaptive — measure `python.exe -c "pass"` boot time at first run,
   multiply by N for the import chain. Or just bump to 120s.

2. **AV quarantine of `torch/testing/` and `numpy/testing/` after
   extraction.** This is the most common in-the-wild failure. The
   recovery flow handles it (`[🛡 Add AV Exclusion]` → `[🔧 Repair
   Runtime]`) but the user has to click two buttons in order. **Fix
   path A:** NSIS post-install hook that runs `Add-MpPreference
   -ExclusionPath` automatically (with consent checkbox in the
   wizard). **Fix path B:** sign the zip / signed installer reduces
   AV heuristic pressure substantially.

3. **`repair_pytorch_via_pip` requires network access.** Offline-only
   environments need a different recovery path. **Fix path:** ship a
   `wheels/` subdirectory in the installer with the same wheels pip
   would download, then `pip install --find-links wheels/
   --no-index torch torchvision`. Adds ~250 MB to installer size;
   trade-off worth measuring.

4. **`vc_redist` check probes only `vcruntime140.dll` + `msvcp140.dll`
   in System32.** It misses UCRT, half-installed redistributables,
   and 32-bit redists shadowing the 64-bit ones. **Fix path:** also
   probe `Get-ItemProperty
   HKLM:\Software\Microsoft\VisualStudio\14.0\VC\Runtimes\x64` for
   the installed version field.

5. **Pip itself missing from the bundled python.** Embedded python
   distributions don't ship pip by default. The build pipeline
   bootstraps it (`prepare_python_from_pyproject_embed310_target.ps1`),
   but if the user runs `[🩺 Repair PyTorch (pip)]` and pip's own
   files were among the AV-quarantined ones, the repair fails with
   "No module named pip". **Fix path:** the doctor should add a
   `pip_intact` check; if missing, `[Repair Runtime]` re-extracts
   the pip files first.

6. **No prevent-double-spawn lock at job-submit time.** The Tauri
   side cancels the prior `current_sidecar_job` before submitting a
   new one, but a fast double-click can race past the lock and
   register two jobs. UX impact: small (the second job inherits the
   same script + env), but worth a mutex on the JS side.

7. **Doctor's `data_dir_writable` probe writes to the local-data root,
   not specifically the runtime tree.** A user with the runtime tree
   on a read-only network share but `%LOCALAPPDATA%` writable would
   pass this check but fail at runtime. **Fix path:** probe the
   runtime tree explicitly.

8. **Sidecar startup-failed signal is global.** Once
   `sidecar_startup_failed` is set, every subsequent `wait_for_sidecar`
   fails fast — but if the user clicks `[↻ Restart Sidecar]` and the
   second attempt succeeds, the flag is correctly cleared by
   `restart_sidecar`. There's no automatic retry. **Fix path:** an
   exponential-backoff watchdog that retries up to N times before
   giving up.

## §8 — How to verify a build is healthy end-to-end

1. **Build:** `make artifact`. Watch for "Runtime integrity check
   passed (all required modules + metadata present)" near STEP 6.7.
   If this fails, the build is broken — DO NOT ship.

2. **Unpack the zip without installing:** see `06-debug-tools.md`
   Diagnostic C. Confirm `torch/testing/__init__.py` and
   `numpy/testing/__init__.py` exist inside.

3. **Install + first launch:** the install-health banner should flip
   to `Ready` (green chip) within ~60s. The sidebar gear gets a red
   dot only on `error`-level checks (warnings don't dot it).

4. **Run Diagnosis (Settings → System Tools):** every check must be
   `OK`. If `torch_intact` or `numpy_intact` shows error with
   `_testing_dir_exists=False`, AV is quarantining — see Bug #11
   in `04-bug-index.md`.

5. **End-to-end smoke:** click Record → wait 5 seconds → click Stop.
   A new `.npy` file should appear under `%LOCALAPPDATA%\
   com.bot.mmorpg.ai\datasets\`. If yes, the full pipeline (UI →
   Tauri → sidecar → script → disk) is healthy.

## §9 — One-table summary of every commit on this branch

| Commit | What it ships |
|---|---|
| `5aae82e` | MVP-1: runtime / datasets / models / logs in `%LOCALAPPDATA%` |
| `5f949ff` | MVP-2: `runtime_doctor.py` + Tauri command + UI banner integration |
| `973c2ab` | MVP-3a: `modelhub/jobs/runner.py` (subprocess manager, no FastAPI) |
| `6e0503e` | MVP-3b: `modelhub/jobs/routes.py` (FastAPI router + SSE + auth) |
| `6b55c7b` | MVP-3c: Tauri-side helpers (`submit_sidecar_job_cmd`, etc.) |
| `3277810` | MVP-4: drop non-load-bearing prune steps; integrity check |
| `8443fef` | MVP-3d: cutover -- every Python spawn goes through the sidecar |
| `7ce45f1` | Align Makefile + workflows + verify_installer with the migration |
| `e6817c7` | Fix duplicate `#[tauri::command]` on `submit_sidecar_job_cmd` |
| `45f6ecf` | Sidecar startup: 60s budget + heartbeats + accurate copy |
| `5806293` | Enterprise UI: sidecar chip + 4 recovery buttons |
| `b0c2ac3` | Doctor verdict in AI Fix Bundle + doctor table + crash reporter |
| `571289c` | UI polish P1: design tokens, BEM buttons, wizard CSS |
| `52dae2e` | Doctor enrichment: torch_root + testing_dir_exists |
| `3ea14a1` | `repair_pytorch_via_pip` -- nuclear-option recovery |

That's the complete picture. Anything not here is either pre-existing
behavior (predates the migration) or deferred to a future session per
§7 above.
{% endraw %}
