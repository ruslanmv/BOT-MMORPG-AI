# 02 — Build Pipeline (build time)

What happens between `make build-installer` and a finished `.exe`.

## End-to-end diagram

```
developer types: make artifact
      │
      ▼
Makefile:327  →  build-installer  →  verify-installer
      │                                    │
      ▼                                    ▼
scripts/build_pipeline.ps1         scripts/verify_installer.ps1
      │
      │  STEP 1     Install uv if missing, create .venv
      │  STEP 2     Bundle embeddable Python 3.10 -> src-tauri/resources/python/
      │  STEP 3     Pre-install all Python deps (incl. PyTorch) into site-packages
      │  STEP 4     UI smoke tests (tests/test_tauri_ui_smoke.py)
      │  STEP 5     Verify backend Python files exist
      │  STEP 6     Copy driver installers + scripts to src-tauri/{drivers,resources/scripts}/
      │  STEP 6.5   Bundle versions/0.01/* into src-tauri/resources/versions/
      │  STEP 6.6   Bundle backend/* + modelhub/* into src-tauri/resources/{backend,modelhub}/
      │  STEP 6.7   Pack the embedded Python tree into resources/runtime/python-runtime.zip
      │  STEP 6.9   Preflight: grep installer/nsis_template.nsi for known bad patterns
      │  STEP 7     Invoke `cargo tauri build`
      │                          │
      ▼                          ▼
                        tauri-bundler 1.7.4 (Cargo.lock)
                                 │
                                 │  reads src-tauri/tauri.conf.json
                                 │  reads installer/nsis_template.nsi
                                 │  builds handlebars context
                                 │  renders -> src-tauri/target/release/bundle/nsis/installer.nsi
                                 │  shells out -> makensis.exe
                                 ▼
                        BOT-MMORPG-AI_<version>_x64-setup.exe   <- shippable
```

## What each staging step produces

Every staging step writes to `src-tauri/<somewhere>/`. After all steps,
the layout `tauri-bundler` sees is:

```
src-tauri/
├── drivers/
│   ├── interception/install-interception.exe
│   └── vjoy/vJoySetup.exe
├── resources/
│   ├── backend/{entry_main.py, main_backend.py}
│   ├── modelhub/{tauri.py, ...15 .py files}
│   ├── runtime/python-runtime.zip          (~220 MB)
│   ├── scripts/{install_drivers.ps1, download_models.ps1, install_ml_deps.ps1}
│   └── versions/0.01/{1-collect_data.py, 2-train_model.py, 3-test_model.py, ...}
└── tauri.conf.json
```

Tauri's `resources: ["resources/**", "drivers/**"]` glob picks all of
this up. Everything matched becomes one `File` directive in the rendered
`installer.nsi`.

## What handlebars-rust receives

The bundler hands handlebars these context variables (Tauri 1.x):

| Variable | Type | Use |
|---|---|---|
| `resources` | `BTreeMap<PathBuf, (PathBuf, PathBuf)>` | Map of source path → `(dest_dir, dest_path)`. The `{{#each resources}}` loop iterates this. |
| `resources_dirs` | `HashSet<PathBuf>` | Every parent dir referenced by `resources`. The `{{#each resources_dirs}}` loop pre-creates these. |
| `main_binary_name` | `String` | The Cargo `package.name` (lowercase: `bot-mmorpg-ai`). |
| `main_binary_path` | `String` | Absolute path to the freshly built `.exe`. |
| `out_file` | `String` | Output installer filename. |
| `version` | `String` | Either `package.version` from Cargo.toml or the `VERSION=` override. |
| `license_file` | `String` (optional) | Path passed via `tauri.bundle.windows.nsis.license`. |
| `install_webview2_mode` | `bool` (optional) | True if WebView2 bootstrapper should be embedded. |

## Render output (what to inspect when debugging)

After `cargo tauri build` runs, **the rendered NSIS source survives**:

```
src-tauri/target/release/bundle/nsis/
├── installer.nsi                          <- the rendered template; READ THIS to debug install bugs
├── output.nsis-compile.log                <- makensis warnings + every File directive
└── BOT-MMORPG-AI_<version>_x64-setup.exe  <- the shippable installer
```

Read `06-debug-tools.md` for the exact PowerShell to grep this.

## Where each commit on the `claude/verify-directory-structure-DLUt1` branch fits

| Commit | What stage / file it touches |
|---|---|
| `94196b4` | nsis_template.nsi — removed broken `resources_dirs` block (initial wrong fix) |
| `8fed9a1` | nsis_template.nsi — strip handlebars tokens from comment block |
| `943f9f8` | nsis_template.nsi — escape backslash before handlebars (the real fix) |
| `8ef898d` | tests/test_tauri_production_readiness.py — update template invariants |

See `05-case-studies.md` for the full debug story behind each.
