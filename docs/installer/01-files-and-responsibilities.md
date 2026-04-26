# 01 — Files & Responsibilities

{% raw %}
The seven files that govern installer behavior, in execution order.
Edit the file matching the layer where your bug lives.

## 1. The single source of truth for installer instructions

**`installer/nsis_template.nsi`** — Handlebars-templated NSIS script.

Defines every install/uninstall step the user sees:
- Wizard pages (welcome / license / components / directory / install / finish)
- Default install dir (`$PROGRAMFILES64\BOT-MMORPG-AI`)
- Privilege requirement (`RequestExecutionLevel admin`)
- File extraction loops (`{{#each resources}}` / `{{#each resources_dirs}}`)
- Registry keys (`HKLM\Software\BOT-MMORPG-AI`)
- Start Menu / Desktop shortcuts
- Driver invocations (Interception / vJoy)
- The uninstaller section

Tauri's bundler renders this file (substituting `{{...}}` expressions) into
the rendered `installer.nsi` and hands it to `makensis.exe`, which
compiles it into the `.exe` setup file.

**Edit when:** any install/uninstall behavior is wrong — paths, registry,
shortcuts, extracted files, driver invocations.

## 2. The wiring that makes Tauri use that template

**`src-tauri/tauri.conf.json`**

Two relevant lines:

| Line | Purpose |
|---|---|
| `tauri.bundle.windows.nsis.template: "../installer/nsis_template.nsi"` | Tells Tauri to use OUR template, not its built-in one. |
| `tauri.bundle.resources: ["resources/**", "drivers/**"]` | Glob patterns that decide which files become bundled `resources` and feed the `{{#each resources}}` loop. |

**Edit when:** you need Tauri to bundle different files, or change the
default install mode (`perMachine` vs `perUser`).

## 3. The bundler that does the rendering

**`src-tauri/Cargo.lock`** pins **`tauri-bundler 1.7.4`** (transitively, via
`tauri-build`/`tauri-cli`).

This Rust crate:
- Reads `tauri.conf.json`
- Builds the Handlebars context (`resources`, `resources_dirs`,
  `main_binary_path`, `version`, `out_file`, etc.)
- Renders our `installer/nsis_template.nsi` through `handlebars-rust`
- Shells out to `makensis.exe`

The exact context shape (e.g. `resources` is `BTreeMap<PathBuf, (PathBuf,
PathBuf)>`) is decided here, NOT by us.

**Edit when:** never directly — but be aware that **upgrading this version
can silently change template variables**. Verify after any tauri version
bump by reading `06-debug-tools.md` (capture the rendered installer.nsi).

## 4. The orchestrator

**`scripts/build_pipeline.ps1`** — the only thing that actually invokes
`cargo tauri build`.

Responsibilities:
- Stages files into `src-tauri/resources/{backend,modelhub,runtime,scripts,versions}/`
  (steps 6, 6.5, 6.6, 6.7) so Tauri's `resources/**` glob picks them up
- Runs preflight checks against the template (line 1164–1175 already
  greps for unquoted `/oname=` — extend this for new invariants)
- Sets `RUST_LOG` and the version override
- Decides **which files exist for the bundler to bundle**

**Edit when:** you need to change what gets staged into the bundle, add a
new pre-flight check, or modify the build sequence.

## 5. The make target the user actually types

**`Makefile`**

| Target | Line | Purpose |
|---|---|---|
| `build-installer` | 342 | Runs the pipeline. |
| `artifact` | 327 | Runs `build-installer` then `verify-installer`. |
| `verify-installer` | 385 | Calls `scripts/verify_installer.ps1`. |
| `test-installer` | 414 | Calls `scripts/test_installer.ps1`. |

**Edit when:** you want to add a new build step or change the version
resolution logic (the `VERSION := ...` block at the top).

## 6. Post-build verification

**`scripts/verify_installer.ps1`** — runs after the build. Does a
**real silent install into a temp dir**, so its log is the most reliable
source-of-truth about what the rendered template actually does.
Notable: it runs the installer with `/S` (silent) — symptoms only
visible in GUI mode may not surface here.

**`scripts/test_installer.ps1`** — heavier integration test (only run
on demand via `make test-installer`).

**Edit when:** verification missed a real bug at install time. Add a
`Test-Path` assertion for the file that should have been extracted.

## 7. Template guardrail tests

| File | Line | What it asserts |
|---|---|---|
| `tests/test_tauri_ui_smoke.py` | — | The template uses the canonical `MAINBINARYSRCPATH` two-step indirection and `{{main_binary_path}}` only appears once. |
| `tests/test_tauri_production_readiness.py` | 554 | The template uses the `!define MAINBINARYNAME` macro and uses `\\{{this}}` (double-backslash) inside path strings. |

**Edit when:** you've changed a template invariant the tests no longer
match. Update the test to assert the new invariant — don't just delete.
{% endraw %}
