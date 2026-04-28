# 07 — Build & Test

The actual commands. All `make` targets resolve to either
`scripts/build_pipeline.ps1`, `scripts/verify_installer.ps1`, or
`pytest`. None has hidden behavior.

> Post-migration test status (this branch): **487 tests pass**, 3
> Windows-only tests skip on Linux dev hosts. New `make` targets:
> `make test-jobs` (sidecar JobRunner + routes) and `make test-doctor`
> (runtime doctor contract). See [09-architecture-end-to-end.md](./09-architecture-end-to-end.md)
> §8 for the end-to-end build-verification recipe.

## Prerequisites

| Tool | Why | Auto-installed? |
|---|---|---|
| Python 3.10+ | Build-time scripts + base venv | No (download from python.org) |
| `uv` | Faster Python dep resolution | Yes, by `make install-uv` |
| Rust + Cargo | Compiles the Tauri app | Yes, by `make build-installer` (via winget on Windows) |
| Tauri CLI | `cargo tauri build` | Yes, by `make build-installer` |
| NSIS | `makensis.exe` to compile installer.nsi | Yes, the Tauri bundler downloads its own copy on first build |

## Build

```powershell
# Full pipeline: stage everything, run preflight, build the .exe
make build-installer

# Or with an explicit version:
make build-installer VERSION=0.2.2

# Build + verify (silent install dry-run on the result)
make artifact

# Just verify a previously-built .exe
make verify-installer
```

Output lands in:

```
src-tauri\target\release\bundle\nsis\
├── installer.nsi                          (rendered NSIS source — debug here)
├── output.nsis-compile.log                (makensis warnings)
└── BOT-MMORPG-AI_<version>_x64-setup.exe  (shippable)
```

## Test

```powershell
# Install dev dependencies (pytest, coverage, mypy etc.)
make install-dev

# Full test suite (~110s; covers UI smoke, production readiness, ML pipeline)
make test

# Just the installer-related tests
.venv/bin/python -m pytest tests/test_tauri_ui_smoke.py tests/test_tauri_production_readiness.py -v

# With coverage report
make test-cov
```

Expected on a green branch:

```
405 passed, 1 skipped, 3 warnings in ~108s
```

The 1 skipped is `tests/health/test_health_smoke.py` — Windows-only,
expected to skip on Linux CI runners.

## Build with offline dependencies (for CI / clean room)

The build pipeline does this automatically — vendors all Python wheels
into `wheelhouse/` then installs from there with `--no-index`. This
avoids the network during the actual build.

If a CI box has limited network, set:

```powershell
$env:UV_OFFLINE = "1"      # Force uv to use the wheelhouse
$env:CARGO_NET_OFFLINE = "true"
```

## End-to-end smoke test (manual)

Until we ship a `tauri-driver` E2E suite (see future TODO):

```powershell
# 1. Clean any prior install
"C:\Program Files\BOT-MMORPG-AI\Uninstall.exe" /S

# 2. Build
make build-installer

# 3. Install
src-tauri\target\release\bundle\nsis\BOT-MMORPG-AI_*-x64-setup.exe

# 4. Run Diagnostic A from 06-debug-tools.md and confirm all [OK]

# 5. Launch the app
"C:\Program Files\BOT-MMORPG-AI\BOT-MMORPG-AI.exe"

# 6. In the app: ⚙ Settings → System Tools → ▶ Run Diagnosis
#    Expect every check ✔ except drivers (⚠ Optional, expected if you
#    haven't run Install Drivers).
```

If any of those steps fail, identify which layer (build / install /
runtime) using `04-bug-index.md`'s decision tree and fix the file
identified in `01-files-and-responsibilities.md`.

## CI workflows

| File | Trigger | What it does |
|---|---|---|
| `.github/workflows/build-windows-installer.yml` | Push to main, manual dispatch | Runs `make artifact` on a Windows runner, uploads the `.exe` artifact |
| `.github/workflows/release.yml` | Tagged release (`v*`) | Builds the installer, attaches it to the GitHub release |

The GitHub-side update checker (`check_for_update` Tauri command)
queries `releases/latest` from this repo. After tagging a new release,
installed apps will surface an "Update available" banner on next launch.

## Versioning

The installer filename embeds a version, set via this resolution order
(`Makefile:36-47`):

1. `make build-installer VERSION=0.2.2` — explicit override
2. `git describe --tags` — closest tag, with `-N-gSHA` suffix if off-tag
3. `0.0.0-dev` — fallback when no tags exist

The version is also written into the .exe manifest via a temp
`tauri-cfg-override-*.json` patched on top of `tauri.conf.json`.
