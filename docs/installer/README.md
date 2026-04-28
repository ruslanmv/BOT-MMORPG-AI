# Installer Documentation Index

Reference for **debugging and modifying the BOT-MMORPG-AI installer**.
Optimized for new developers / AI sessions landing cold and needing
to find the right file fast.

> **Read 09 first.** It's the post-migration end-to-end overview.
> The earlier docs (03 / 04 / 05) reference the pre-migration model
> in places and are being refreshed batch-by-batch.

## Read in this order

| # | File | Read when… |
|---|---|---|
| **9** | [09-architecture-end-to-end.md](./09-architecture-end-to-end.md) | **Start here.** Full picture of how the installer + Tauri shell + sidecar + ML scripts fit together AFTER the `claude/verify-directory-structure-DLUt1` migration (MVP-1 through MVP-3d). Lists known issues and where fixes should land. |
| 1 | [01-files-and-responsibilities.md](./01-files-and-responsibilities.md) | You don't know which file controls a given install behavior. The 7-file map. |
| 2 | [02-build-pipeline.md](./02-build-pipeline.md) | You want to understand how `make build-installer` produces the `.exe`. |
| 3 | [03-runtime-flow.md](./03-runtime-flow.md) | What the **installed .exe** does at install time and at app launch. |
| 4 | [04-bug-index.md](./04-bug-index.md) | A user reports a symptom and you need to know which file to edit. |
| 5 | [05-case-studies.md](./05-case-studies.md) | Worked examples of bugs we already fixed on this branch. |
| 6 | [06-debug-tools.md](./06-debug-tools.md) | You're stuck and need PowerShell scripts / commands to inspect a live install or the runtime doctor JSON. |
| 7 | [07-build-and-test.md](./07-build-and-test.md) | You need to actually run a build, run the test suite, or verify the installer. |
| 8 | [08-ai-debug-loop.md](./08-ai-debug-loop.md) | The app is throwing an error at runtime and you want to copy a structured fix-request bundle into Claude Code. |

## TL;DR for the impatient

- **All install behavior is authored in:** `installer/nsis_template.nsi`
- **All Tauri shell behavior is authored in:** `src-tauri/src/main.rs`
- **The Python sidecar lives at:** `modelhub/tauri.py` (mounts routers from `modelhub/{diagnostics,jobs}/`)
- **All ML scripts live at:** `versions/0.01/{1-collect_data.py, 2-train_model.py, 3-test_model.py}`
- **The orchestrator that ties them together:** `scripts/build_pipeline.ps1`
- **The bundler that renders the template:** `tauri-bundler 1.7.4` (pinned in `src-tauri/Cargo.lock`)
- **The render output to inspect when debugging:** `src-tauri/target/release/bundle/nsis/installer.nsi`

If a user-reported bug doesn't match anything in [04-bug-index.md](./04-bug-index.md),
the answer is almost always in one of:

| Layer | File | Symptoms it owns |
|---|---|---|
| Build | `installer/nsis_template.nsi` | rendered installer.nsi has wrong tokens / paths |
| Build | `scripts/build_pipeline.ps1` | resources are missing or stale; integrity check fails |
| Install | NSIS bytecode (compiled from template) | files don't extract; registry wrong; shortcuts wrong |
| Tauri shell | `src-tauri/src/main.rs` | sidecar doesn't start; jobs don't dispatch; UI commands fail |
| Sidecar | `modelhub/tauri.py` + `modelhub/jobs/*` | HTTP routes return 5xx; SSE streams don't deliver |
| ML scripts | `versions/0.01/*.py` | training / collection / inference itself crashes |

## Reality check (post-migration current state)

The branch ships major architectural changes (see 09). What that means
in practice:

| Concern | Status |
|---|---|
| Runtime data location | `%LOCALAPPDATA%\com.bot.mmorpg.ai\` (was Program Files) — see 09 §2 |
| Python spawn ownership | Sidecar (was Tauri shell) — see 09 §4 |
| Crash containment | A torch crash now stays inside the sidecar process tree — UI keeps responding |
| Install-health visibility | Runtime doctor at every launch + persistent banner — see 09 §5 |
| Recovery flow | 4-button ladder (Restart / Repair Runtime / Repair PyTorch via pip / AV Exclusion) — see 06 |

**Known unfixed surfaces** (deferred to a future session):

1. First-launch may still time out if cold-disk imports exceed 60s on
   very slow HDDs — increase the budget in `start_sidecar_server` if
   reports come in.
2. AV-quarantine of `torch/testing/` after extraction is the most
   common in-the-wild failure — recovery flow handles it but the user
   has to click. A pre-emptive AV exclusion at install time would close
   this fully.
3. `repair_pytorch_via_pip` requires network access; offline-only
   environments need a different recovery path.
4. The doctor's `vc_redist` check probes `vcruntime140.dll` only — it
   won't catch a missing UCRT or a half-installed redistributable.

These are all in the bug-index and architecture doc with pointers to
where fixes belong.

## Pointers to user-facing docs

The top-level [INSTALLER.md](../../INSTALLER.md) (in the repo root) holds the
**user-facing build guide** — prerequisites, GitHub Actions workflows,
distribution. This `docs/installer/` folder is the **developer-facing
debug reference**.
