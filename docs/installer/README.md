# Installer Documentation Index

Reference for **debugging and modifying the BOT-MMORPG-AI installer**.
Optimized for new developers / AI sessions landing cold and needing
to find the right file fast.

## Read in this order

| # | File | Read when… |
|---|---|---|
| 1 | [01-files-and-responsibilities.md](./01-files-and-responsibilities.md) | You don't know which file controls a given install behavior. The 7-file map. |
| 2 | [02-build-pipeline.md](./02-build-pipeline.md) | You want to understand how `make build-installer` produces the `.exe`. |
| 3 | [03-runtime-flow.md](./03-runtime-flow.md) | You need to understand what the **installed .exe** does at install time and at app launch. |
| 4 | [04-bug-index.md](./04-bug-index.md) | A user reports a symptom and you need to know which file to edit. **Start here for active bugs.** |
| 5 | [05-case-studies.md](./05-case-studies.md) | You want to see worked examples of bugs we already fixed on the `claude/verify-directory-structure-DLUt1` branch. |
| 6 | [06-debug-tools.md](./06-debug-tools.md) | You're stuck and need PowerShell scripts / commands to inspect the installer or a live install. |
| 7 | [07-build-and-test.md](./07-build-and-test.md) | You need to actually run a build, run the test suite, or verify the installer. |
| 8 | [08-ai-debug-loop.md](./08-ai-debug-loop.md) | The app is throwing an error at runtime and you want to copy a structured fix-request bundle into Claude Code. |

## TL;DR for the impatient

- **All install behavior is authored in one file:** `installer/nsis_template.nsi`
- **All runtime behavior is authored in one file:** `src-tauri/src/main.rs`
- **The orchestrator that ties them together:** `scripts/build_pipeline.ps1`
- **The bundler that renders the template:** `tauri-bundler 1.7.4` (pinned in `src-tauri/Cargo.lock`)
- **The render output to inspect when debugging:** `src-tauri/target/release/bundle/nsis/installer.nsi`

If a user-reported bug doesn't match anything in [04-bug-index.md](./04-bug-index.md),
the answer is almost always in either `nsis_template.nsi` (build-time) or `main.rs`
(runtime). Both files are large but well-commented.

## Pointers to user-facing docs

The top-level [INSTALLER.md](../../INSTALLER.md) (in the repo root) holds the
**user-facing build guide** — prerequisites, GitHub Actions workflows,
distribution. This `docs/installer/` folder is the **developer-facing
debug reference**.
