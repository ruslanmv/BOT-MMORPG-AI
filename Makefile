.PHONY: help install install-dev install-uv install-backend venv sync install-drivers download-drivers clean lint format format-check type-check test test-cov test-unit test-integration test-jobs test-doctor build docs clean-build clean-pyc clean-test clean-venv clean-localappdata check all release install-launcher launcher install-all collect-data train-model test-model artifact build-installer verify-installer test-installer clean-installer ci ci-lint ci-format dev dev-go dev-sidecar dev-sidecar-test dev-clean doctor help-debug run

# Default target
.DEFAULT_GOAL := help

# Command Definitions
# SYS_PYTHON: Uses your global python just for the 'help' menu (fast, no sync required)
SYS_PYTHON := python
# RUN_PYTHON: Uses 'uv run' to ensure code runs inside the virtual env
RUN_PYTHON := uv run python

# OS detection
ifeq ($(OS),Windows_NT)
	IS_WINDOWS := 1
else
	IS_WINDOWS := 0
endif

# PHASE 18: cross-platform "blank line" macro.
# - cmd.exe   : `echo.` (period right after, no space) prints empty line
# - bash / sh : bare `echo` prints empty line
# Without this, `@echo ""` prints a literal `""` on Windows because cmd.exe
# does NOT strip quotes from echo args (unlike sh). All Phase 15-18 targets
# use $(EMPTY) for blank lines and bare `@echo <text>` (no surrounding
# quotes) for content lines, so the same Makefile renders cleanly on both.
ifeq ($(IS_WINDOWS),1)
	EMPTY := echo.
else
	EMPTY := echo
endif

# -----------------------------------------------------------------------------
# Installer version
# -----------------------------------------------------------------------------
# `make artifact` (and friends) need a version to inject into tauri so the
# bundled .exe is named BOT-MMORPG-AI_<version>_x64-setup.exe instead of the
# static "1.0.0" hard-coded in tauri.conf.json. Resolution order:
#
#   1. VERSION=<x> on the command line:    make artifact VERSION=0.2.2
#   2. The latest reachable git tag (with leading `v` stripped). On a tagged
#      commit you get exactly that tag. Off the tag you get e.g.
#      `0.2.1-3-g4a5b6c7` -- still a valid semver pre-release identifier
#      that tauri/NSIS accept.
#   3. `0.0.0-dev` if neither is available (fresh tree, no tags, no override).
#
# To pin a release locally:                  make artifact VERSION=0.2.2
# To build a "current branch" build:         make artifact   (uses git describe)
# CI always passes VERSION via the env so this fallback never fires there.
ifeq ($(strip $(VERSION)),)
  # Resolve via the Python helper instead of shell + sed + grep -- on
  # Windows, GNU make often invokes cmd.exe for $(shell ...) and that has
  # neither sed nor grep, which is why earlier `make artifact` runs on
  # Windows always fell back to the static "1.0.0" baked into
  # tauri.conf.json. Python is already a build prerequisite.
  #
  # PHASE 18: stderr redirect must be platform-correct. /dev/null
  # only exists on Unix; cmd.exe interprets it as a real path and
  # prints "The system cannot find the path specified." before
  # falling through. Use NUL on Windows (the cmd.exe equivalent).
  ifeq ($(IS_WINDOWS),1)
    VERSION := $(shell $(SYS_PYTHON) scripts/version.py 2>NUL)
  else
    VERSION := $(shell $(SYS_PYTHON) scripts/version.py 2>/dev/null)
  endif
  ifeq ($(strip $(VERSION)),)
    # Even the python fallback failed (somehow). Hardcode a safe default.
    VERSION := 0.0.0-dev
  endif
endif

##@ General

help: ## Display this help message
	@echo "======================================================================="
	@echo " BOT-MMORPG-AI - AI Bot for MMORPG Games"
	@echo "======================================================================="
	@$(SYS_PYTHON) -c "import sys, re; \
	lines = [l.strip() for l in sys.stdin]; \
	print('Available commands:'); \
	[print(f'  {m.group(1):<20} {m.group(2)}') for l in lines if (m := re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', l))]" < $(MAKEFILE_LIST)
	@echo ""

##@ Installation & Setup

install-uv: ## Install uv package manager
	@echo Installing uv package manager...
ifeq ($(IS_WINDOWS),1)
	@powershell -NoProfile -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"
else
	@sh -c "curl -LsSf https://astral.sh/uv/install.sh | sh"
endif
	@echo uv is installed
	@echo If 'uv' is not found, restart your terminal so PATH updates take effect.

venv: ## Create the virtual environment (Python 3.10 for best compatibility)
ifeq ($(IS_WINDOWS),1)
	@if exist ".venv\Scripts\python.exe" ( \
		echo Virtual environment already exists in .venv/ \
	) else ( \
		echo Creating virtual environment with Python 3.10... && \
		uv venv --python 3.10 && \
		echo Virtual environment created in .venv/ \
	)
else
	@if [ -d ".venv" ]; then \
		echo "Virtual environment already exists in .venv/"; \
	else \
		echo "Creating virtual environment with Python 3.10..."; \
		uv venv --python 3.10; \
		echo "Virtual environment created in .venv/"; \
	fi
endif

install: install-uv venv ## Install production dependencies
	@echo Installing production dependencies...
	@uv pip install -e .
	@echo Production dependencies installed

install-dev: install-uv venv ## Install development dependencies
	@echo Installing development dependencies...
	@uv pip install -e ".[dev]"
	@echo Development dependencies installed

install-backend: install-uv venv ## Install sidecar dependencies (FastAPI + uvicorn)
	@echo Installing backend dependencies...
	@uv pip install -e ".[backend]"
	@echo Backend dependencies installed

install-launcher: install-uv venv ## Install launcher dependencies (Eel)
	@echo Installing launcher dependencies...
	@uv pip install -e ".[launcher]"
	@echo Launcher dependencies installed

launcher: ## Run the Python/Eel launcher for development
	@echo "========================================"
	@echo " Starting BOT-MMORPG-AI Launcher (Dev)"
	@echo "========================================"
	@echo "Note: Install launcher dependencies first with 'make install-launcher'"
	@echo ""
	$(RUN_PYTHON) launcher/launcher.py

# -----------------------------------------------------------------------------
# DEV-MODE TARGETS (no installer required)
# -----------------------------------------------------------------------------
# `make dev`, `make dev-sidecar`, `make dev-sidecar-test` exist so you can
# validate the full backend stack BEFORE building the installer. They run
# everything from the repo source, using the host Python venv -- no
# python-runtime.zip extraction, no Program Files install dir, no `\\?\`
# extended-length paths, no AV scanning, no UAC. If the app works in dev
# mode then any failure under `make artifact` is a *packaging* issue, not
# a backend code issue. That's the "discard the backend issue" workflow.
#
# Layered from heaviest to lightest:
#   make dev               -> full Tauri shell + sidecar from source.
#                             Requires Rust toolchain + WebView2 (Windows)
#                             or libwebkit2gtk-4.0-dev (Linux).
#   make dev-sidecar       -> just the Python sidecar (no Tauri shell, no UI).
#                             Pure Python; works everywhere `make install` works.
#                             Stays in the foreground; Ctrl+C to stop.
#   make dev-sidecar-test  -> automated smoke test: spawn sidecar in a
#                             subprocess, wait for `READY url=... token=...`,
#                             do an authenticated `GET /health`, kill the
#                             subprocess. Exits 0 on success, 1 on failure.
#                             Use this in CI to catch breakage before installer
#                             builds.
# -----------------------------------------------------------------------------

dev: install install-backend ## Run the full app (Tauri UI + sidecar from source). No installer.
	@echo ========================================
	@echo  BOT-MMORPG-AI -- DEV MODE
	@echo ========================================
	@echo  Tauri shell: src-tauri/  (debug build, hot reload UI)
	@echo  Sidecar:     spawned from modelhub/tauri.py via the host
	@echo               .venv Python -- NO python-runtime.zip, NO
	@echo               extended-length paths, NO Program Files.
	@$(EMPTY)
	@echo  If the app works here but breaks under 'make artifact'
	@echo  then the bug is in PACKAGING, not in the backend code.
	@echo ========================================
	@$(EMPTY)
	@echo Stamping UI bundle tag so the running app prints which JS it loaded...
	@$(SYS_PYTHON) scripts/stamp_ui_build_tag.py
	@cd src-tauri && cargo tauri dev

dev-go: doctor dev ## One-shot: run `make doctor`, and if green, launch `make dev`.

dev-sidecar: install install-backend ## Run just the Python sidecar (no Tauri, no UI). Foreground.
	@echo ========================================
	@echo  BOT-MMORPG-AI -- SIDECAR ONLY
	@echo ========================================
	@echo  Spawning the FastAPI sidecar standalone.
	@echo  - port:          0  (auto-assigned, printed on READY line)
	@echo  - token:         devtoken
	@echo  - resource-root: $(CURDIR)
	@echo  - data-root:     $(CURDIR)/.dev-data
	@$(EMPTY)
	@echo  The sidecar prints  READY url=http://127.0.0.1:<port> token=devtoken
	@echo  when /health is reachable. Try:
	@echo    curl -H 'X-Auth-Token: devtoken' http://127.0.0.1:<port>/health
	@echo  Ctrl+C to stop.
	@echo ========================================
	@mkdir -p .dev-data
	@$(RUN_PYTHON) backend/entry_main.py \
	    --port 0 --token devtoken \
	    --resource-root "$(CURDIR)" --data-root "$(CURDIR)/.dev-data"

dev-sidecar-test: install install-backend ## Smoke-test the sidecar end-to-end: spawn -> READY -> /health -> kill.
	@echo ========================================
	@echo  BOT-MMORPG-AI -- SIDECAR SMOKE TEST
	@echo ========================================
	@$(RUN_PYTHON) scripts/dev_sidecar_smoke.py

dev-clean: ## Wipe the dev-mode data dir (.dev-data/). Cross-platform.
	@echo ========================================
	@echo  BOT-MMORPG-AI -- DEV-CLEAN
	@echo ========================================
	@echo Removing $(CURDIR)/.dev-data/ ...
	@$(SYS_PYTHON) -c "import shutil, pathlib; p = pathlib.Path('.dev-data'); shutil.rmtree(p, ignore_errors=True); print('  -> removed' if not p.exists() else '  -> still present (in-use? close `make dev` first)')"

doctor: install install-backend install-dev ## Run the full debug ladder: deps -> import -> smoke -> tests. AAA-grade.
	@echo ========================================
	@echo  BOT-MMORPG-AI -- DOCTOR
	@echo ========================================
	@echo  Runs the AAA-grade debug ladder, top to bottom.
	@echo  Stops at the first tier that fails so you know exactly
	@echo  where the breakage is. The principle: validate cheap
	@echo  things first; never run an expensive test until the
	@echo  cheap ones pass.
	@echo ========================================
	@$(EMPTY)
	@echo [Tier 0] Importing the sidecar package + core ML deps...
	@$(RUN_PYTHON) -c "import sys; import torch; import fastapi; import uvicorn; import modelhub; import modelhub.tauri; print(f'  -> python {sys.version.split()[0]} | torch {torch.__version__} | fastapi {fastapi.__version__} | modelhub.tauri {modelhub.tauri.__file__!r}')"
	@$(EMPTY)
	@echo [Tier 1] Sidecar end-to-end smoke (spawn -> READY -> /health -> auth -> kill)...
	@$(RUN_PYTHON) scripts/dev_sidecar_smoke.py
	@$(EMPTY)
	@echo [Tier 2] Backend pytest suite (sidecar contracts only -- fast)...
	@$(RUN_PYTHON) -m pytest \
	    tests/test_backend_startup.py \
	    tests/test_jobs_routes.py \
	    tests/test_jobs_runner.py \
	    tests/test_diagnostics_smoke.py \
	    tests/test_health_probe_smoke.py \
	    tests/test_runtime_doctor.py \
	    --no-cov -q
	@$(EMPTY)
	@echo ========================================
	@echo  [OK] Doctor passed -- backend stack is healthy.
	@echo ========================================
	@echo Next steps:
	@echo   1. 'make dev'      -- see the full UI (hot reload, no installer)
	@echo   2. 'make artifact' -- build the Windows installer .exe
	@$(EMPTY)
	@echo If 'make artifact' then fails, the bug is 100%% in PACKAGING
	@echo (NSIS, extended-length paths, AV, code-signing) -- not in the
	@echo backend code. Check the debug bundle's '## Likely Causes' section.

help-debug: ## Print the AAA-grade debug recipe (use when something is broken).
	@$(SYS_PYTHON) -c "import pathlib; print(pathlib.Path('scripts/debug_recipe.txt').read_text(encoding='utf-8'), end='')"

install-all: install-uv venv ## Install all dependencies (requires pyproject.toml update)
	@echo Installing all dependencies...
	@uv pip install -e ".[all]"
	@echo All dependencies installed

sync: install-uv venv ## Refresh/reinstall dependencies from pyproject.toml
	@echo Syncing dependencies with uv...
	@uv pip install -e . --reinstall
	@echo Dependencies synced

install-drivers: ## Install vJoy and Interception drivers (Windows only, requires Admin)
ifeq ($(IS_WINDOWS),1)
	@echo "========================================"
	@echo " Installing Gaming Drivers"
	@echo "========================================"
	@echo "This will install:"
	@echo "  - vJoy (virtual joystick driver)"
	@echo "  - Interception (keyboard/mouse driver)"
	@echo ""
	@echo "NOTE: Requires Administrator privileges."
	@echo "      Uses drivers from repository."
	@echo "      Use 'make download-drivers' to download from source first."
	@echo ""
	@powershell -NoProfile -ExecutionPolicy Bypass -File scripts/install_drivers.ps1
else
	@echo "========================================"
	@echo " Driver Installation"
	@echo "========================================"
	@echo "ERROR: Driver installation is only supported on Windows."
	@echo ""
	@echo "These drivers are Windows-specific:"
	@echo "  - vJoy: Virtual joystick for game input simulation"
	@echo "  - Interception: Low-level keyboard/mouse driver"
	@echo ""
	@echo "For Linux/macOS, alternative input methods may be available"
	@echo "but are not currently supported by this project."
	@echo ""
endif

download-drivers: ## Download drivers from official sources and install (Windows only)
ifeq ($(IS_WINDOWS),1)
	@echo "========================================"
	@echo " Downloading & Installing Gaming Drivers"
	@echo "========================================"
	@echo "This will:"
	@echo "  1. Download drivers from official GitHub releases"
	@echo "  2. Install vJoy and Interception drivers"
	@echo ""
	@echo "Download sources:"
	@echo "  - vJoy: https://github.com/shauleiz/vJoy"
	@echo "  - Interception: https://github.com/oblitum/Interception"
	@echo ""
	@echo "NOTE: Requires Administrator privileges."
	@echo ""
	@powershell -NoProfile -ExecutionPolicy Bypass -File scripts/install_drivers.ps1 -Download
else
	@echo "========================================"
	@echo " Driver Download"
	@echo "========================================"
	@echo "ERROR: Driver download is only supported on Windows."
	@echo ""
	@echo "These drivers are Windows-specific and cannot be used on Linux/macOS."
	@echo ""
endif

##@ Code Quality

lint: ## Run all linters (flake8, pylint)
	@echo Running flake8...
	@$(RUN_PYTHON) -m flake8 src/ tests/ --max-line-length=100 --exclude=frontend/assets/backup,build,dist || $(RUN_PYTHON) -c "exit(0)"
	@echo Running pylint...
	@$(RUN_PYTHON) -m pylint src/bot_mmorpg --rcfile=pyproject.toml || $(RUN_PYTHON) -c "exit(0)"
	@echo Linting complete

format: ## Format code using black and isort
	@echo Formatting code with black...
	@$(RUN_PYTHON) -m black src/ tests/ --line-length=100 --exclude=frontend/assets/backup
	@echo Sorting imports with isort...
	@$(RUN_PYTHON) -m isort src/ tests/ --profile=black --line-length=100
	@echo Code formatted

format-check: ## Check code formatting
	@echo Checking code format...
	@$(RUN_PYTHON) -m black src/ tests/ --check --line-length=100 --exclude=frontend/assets/backup
	@$(RUN_PYTHON) -m isort src/ tests/ --check-only --profile=black --line-length=100
	@echo Format check complete

type-check: ## Run type checking with mypy
	@echo Running type checks...
	@$(RUN_PYTHON) -m mypy src/ --config-file=pyproject.toml || $(RUN_PYTHON) -c "exit(0)"
	@echo Type checking complete

check: format-check lint type-check ## Run all code quality checks

ci-lint: ## Run ruff linter (same as GitHub Actions CI)
	@echo "Running ruff lint check..."
	@$(RUN_PYTHON) -m ruff check src/ tests/
	@echo "Ruff lint passed"

ci-format: ## Run ruff format check (same as GitHub Actions CI)
	@echo "Running ruff format check..."
	@$(RUN_PYTHON) -m ruff format --check src/ tests/
	@echo "Ruff format passed"

ci: ci-lint ci-format test ## Run full CI pipeline locally (lint + format + tests)

##@ Testing

test: ## Run all tests
	@echo Running all tests...
	@$(RUN_PYTHON) -m pytest tests/ -v
	@echo All tests passed

test-cov: ## Run tests with coverage report
	@echo Running tests with coverage...
	@$(RUN_PYTHON) -m pytest tests/ -v --cov=src/bot_mmorpg --cov-report=html --cov-report=term-missing
	@echo Coverage report generated in htmlcov/

test-unit: ## Run unit tests only
	@echo Running unit tests...
	@$(RUN_PYTHON) -m pytest tests/ -v -m unit
	@echo Unit tests passed

test-integration: ## Run integration tests only
	@echo Running integration tests...
	@$(RUN_PYTHON) -m pytest tests/ -v -m integration
	@echo Integration tests passed

test-jobs: ## Run JobRunner + /jobs FastAPI route tests (MVP-3a/3b)
	@echo "Running sidecar JobRunner + routes tests..."
	@$(RUN_PYTHON) -m pytest tests/test_jobs_runner.py tests/test_jobs_routes.py -v
	@echo "Sidecar jobs tests passed"

test-doctor: ## Run runtime_doctor.py self-test contract tests (MVP-2)
	@echo "Running runtime doctor tests..."
	@$(RUN_PYTHON) -m pytest tests/test_runtime_doctor.py -v
	@echo "Runtime doctor tests passed"

##@ Building & Documentation

build: clean-build ## Build distribution packages
	@echo Building distribution packages...
	@uv pip install build
	@$(RUN_PYTHON) -m build
	@echo Distribution packages built in dist/

docs: ## Generate documentation (Sphinx setup required)
	@echo "========================================"
	@echo " Documentation Generation"
	@echo "========================================"
	@echo "NOTE: Sphinx documentation is not yet configured."
	@echo ""
	@echo "Available documentation:"
	@echo "  - README.md       : Project overview"
	@echo "  - USAGE.md        : User guide for gamers"
	@echo "  - SETUP_GUIDE.md  : Setup instructions"
	@echo "  - INSTALLER.md    : Installer guide"
	@echo "  - docs/*.md       : Additional docs"
	@echo ""
	@echo "To set up Sphinx documentation:"
	@echo "  1. uv pip install -e '.[docs]'"
	@echo "  2. sphinx-quickstart docs/"
	@echo "  3. Configure docs/conf.py"
	@echo "  4. Run: cd docs && make html"
	@echo ""

##@ Cleaning

clean: clean-build clean-pyc clean-test clean-venv ## Remove all build artifacts (does NOT touch %LOCALAPPDATA% runtime; use clean-localappdata for that)
	@echo Cleaned all build artifacts
	@echo "  Note: %LOCALAPPDATA%/com.bot.mmorpg.ai/ is preserved (user data)."
	@echo "  Run 'make clean-localappdata' separately to wipe runtime/datasets/models."

clean-venv: ## Remove virtual environment
	@echo Removing virtual environment...
	@$(SYS_PYTHON) -c "import shutil; shutil.rmtree('.venv', ignore_errors=True)"

clean-build: ## Remove build artifacts
	@echo Cleaning build artifacts...
	@$(SYS_PYTHON) -c "import shutil, os; dirs=['build', 'dist', '.eggs']; [shutil.rmtree(d, ignore_errors=True) for d in dirs];"
	@$(SYS_PYTHON) -c "import pathlib; [p.unlink() for p in pathlib.Path('.').rglob('*.egg-info')]"

clean-pyc: ## Remove Python file artifacts
	@echo Cleaning Python artifacts...
	@$(SYS_PYTHON) -c "import pathlib; [p.unlink() for p in pathlib.Path('.').rglob('*.py[co]')]"
	@$(SYS_PYTHON) -c "import pathlib; [p.unlink() for p in pathlib.Path('.').rglob('*~')]"
	@$(SYS_PYTHON) -c "import pathlib, shutil; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]"

clean-test: ## Remove test and coverage artifacts
	@echo Cleaning test artifacts...
	@$(SYS_PYTHON) -c "import shutil; dirs=['.tox', '.pytest_cache', 'htmlcov', '.mypy_cache']; [shutil.rmtree(d, ignore_errors=True) for d in dirs];"
	@$(SYS_PYTHON) -c "import os; os.remove('.coverage') if os.path.exists('.coverage') else None"

clean-localappdata: ## Wipe the runtime tree under %LOCALAPPDATA% (Windows-only; MVP-1)
	@echo "Removing %LOCALAPPDATA%/com.bot.mmorpg.ai (runtime, datasets, models, logs)..."
ifeq ($(IS_WINDOWS),1)
	@powershell -NoProfile -ExecutionPolicy Bypass -Command \
	  "$$root = Join-Path $$env:LOCALAPPDATA 'com.bot.mmorpg.ai'; \
	   if (Test-Path $$root) { \
	     Remove-Item -Recurse -Force $$root -ErrorAction SilentlyContinue; \
	     Write-Host '[OK] Removed' $$root \
	   } else { \
	     Write-Host '[SKIP] Not present:' $$root \
	   }"
else
	@echo "  (No-op on non-Windows: the runtime tree only exists on Windows installs)"
endif

##@ Application Commands

collect-data: ## Run data collection script directly (dev only; production goes through the sidecar)
	@echo "Starting data collection (DIRECT script run -- bypasses the sidecar)..."
	@echo "  In the installed app, this is spawned via POST /jobs (MVP-3d). Use this"
	@echo "  target for fast script-level debugging without the Tauri shell."
	@$(RUN_PYTHON) versions/0.01/1-collect_data.py

train-model: ## Run model training script directly (dev only; production goes through the sidecar)
	@echo "Starting model training (DIRECT script run -- bypasses the sidecar)..."
	@echo "  In the installed app, this is spawned via POST /jobs (MVP-3d). Use this"
	@echo "  target for fast script-level debugging without the Tauri shell."
	@$(RUN_PYTHON) versions/0.01/2-train_model.py

test-model: ## Run model testing/playing script directly (dev only; production goes through the sidecar)
	@echo "Starting model testing (DIRECT script run -- bypasses the sidecar)..."
	@echo "  In the installed app, this is spawned via POST /jobs (MVP-3d). Use this"
	@echo "  target for fast script-level debugging without the Tauri shell."
	@$(RUN_PYTHON) versions/0.01/3-test_model.py

##@ Running the Application

# Phase 23-C: legacy `run:` is now an alias for the canonical `dev`
# target (line ~168). Previously this file declared `dev:` twice
# (once as the Phase 15 dev-mode entry, once as `dev: run` here)
# and GNU Make picked the LAST definition -- silently bypassing
# Phase 15's install / install-backend prereqs. Single source of
# truth now lives at the top of the file.
run: dev  ## Alias for `make dev` (legacy name).

run-backend: ## Run only the Python backend (for testing)
	@echo "Starting backend API server..."
	@$(RUN_PYTHON) backend/main_backend.py

##@ Installer (Windows Only)

artifact: build-installer verify-installer ## Build Windows installer artifact (complete workflow)
	@echo ""
	@echo "========================================"
	@echo " Installer Build Complete!"
	@echo "========================================"
	@echo "Version:            $(VERSION)"
	@echo "Installer location: src-tauri/target/release/bundle/nsis/"
	@echo "Expected filename:  BOT-MMORPG-AI_$(VERSION)_x64-setup.exe"
	@echo ""
	@echo "What the installer ships (post-migration):"
	@echo "  - Tauri UI in Program Files (read-only)"
	@echo "  - Bundled python runtime + ML site-packages"
	@echo "  - Sidecar (FastAPI) + JobRunner (modelhub/jobs/)"
	@echo "  - runtime_doctor.py for the install-health banner"
	@echo ""
	@echo "What the installer does NOT contain:"
	@echo "  - The runtime tree at %LOCALAPPDATA%/com.bot.mmorpg.ai/."
	@echo "    That tree is created on first launch by the Tauri shell"
	@echo "    (extracts python-runtime.zip into the user-writable path)."
	@echo "    Pre-migration installs are auto-migrated from Program Files."
	@echo ""
	@echo "Next steps:"
	@echo "  1. Test installer: make test-installer"
	@echo "  2. Test on Windows VM"
	@echo "  3. Create release: git tag v$(VERSION) && git push origin v$(VERSION)"
	@echo ""

build-installer: ## Build the installer (Windows: NSIS .exe; Linux: portable .tar.gz). Override version with VERSION=0.2.2.
ifeq ($(IS_WINDOWS),1)
	@echo "========================================"
	@echo " Building Windows Installer"
	@echo "========================================"
	@echo "Version: $(VERSION)"
	@echo ""
	@echo "This will:"
	@echo "  1. Bundle embedded Python + ML site-packages"
	@echo "  2. Build Tauri desktop application with --config version override"
	@echo "  3. Create NSIS installer package"
	@echo ""
	@echo "Stamping UI bundle tag $(VERSION) into tauri-ui/main.js (Phase 23-B)..."
	@$(SYS_PYTHON) scripts/stamp_ui_build_tag.py --tag $(VERSION)
	@echo ""
	@powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build_pipeline.ps1 -Version "$(VERSION)"
else ifeq ($(shell uname -s),Linux)
	@echo "========================================"
	@echo " Building Linux Bundle"
	@echo "========================================"
	@echo "Version: $(VERSION)"
	@echo ""
	@echo "Tauri 1.x's GTK shell is not packaged for Ubuntu 24.04 (webkit2gtk-4.0)"
	@echo "so the Linux artifact is the portable runtime tarball, not a .deb/.AppImage."
	@echo "Smoke-tests record (synthetic) -> train -> inference end-to-end."
	@echo ""
	@VERSION='$(VERSION)' bash ./scripts/linux_smoke_and_bundle.sh
else
	@echo "========================================"
	@echo " Windows Installer Build"
	@echo "========================================"
	@echo "ERROR: Installer build is only supported on Windows."
	@echo ""
	@echo "To build the installer:"
	@echo "  1. Use a Windows machine or VM"
	@echo "  2. Install prerequisites: Python 3.10+, Rust, Tauri CLI"
	@echo "  3. Run: make artifact"
	@echo ""
	@echo "Or use GitHub Actions:"
	@echo "  - Push to GitHub: git push"
	@echo "  - Check Actions tab for build artifacts"
	@echo "  - Download installer from workflow run"
	@echo ""
	@exit 1
endif

verify-installer: ## Verify installer was built correctly (asserts the bundled .exe filename matches $(VERSION))
ifeq ($(IS_WINDOWS),1)
	@echo "========================================"
	@echo " Verifying Installer Build"
	@echo "========================================"
	@echo "Expected version in installer filename: $(VERSION)"
	@powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify_installer.ps1
	@powershell -NoProfile -ExecutionPolicy Bypass -Command \
	  "$$exe = Get-ChildItem -Path 'src-tauri/target/release/bundle/nsis' -Filter '*.exe' -ErrorAction SilentlyContinue | Select-Object -First 1; \
	   if (-not $$exe) { Write-Error 'No installer .exe under src-tauri/target/release/bundle/nsis -- did the build fail?'; exit 1 }; \
	   if ($$exe.Name -notmatch [Regex]::Escape('$(VERSION)')) { \
	     Write-Error ('[FAIL] Installer filename ''' + $$exe.Name + ''' does not contain expected version ''$(VERSION)''. The -Version override did not flow through the build pipeline.'); \
	     exit 1 \
	   }; \
	   $$sizeMB = [math]::Round($$exe.Length / 1MB, 1); \
	   if ($$sizeMB -lt 50) { \
	     Write-Error ('[FAIL] Installer is suspiciously small (' + $$sizeMB + ' MB). Expected >= 50 MB. Did the embedded python runtime get bundled?'); \
	     exit 1 \
	   }; \
	   Write-Host ('[OK] Installer filename matches version: ' + $$exe.Name + ' (' + $$sizeMB + ' MB)')"
else
	@echo "========================================"
	@echo " Installer Verification"
	@echo "========================================"
	@echo "Verification is only available on Windows."
	@echo "Use GitHub Actions to verify builds on CI."
	@echo ""
endif

test-installer: ## Test the installer package
ifeq ($(IS_WINDOWS),1)
	@echo "========================================"
	@echo " Testing Installer Package"
	@echo "========================================"
	@powershell -NoProfile -ExecutionPolicy Bypass -File scripts/test_installer.ps1
else
	@echo "========================================"
	@echo " Installer Testing"
	@echo "========================================"
	@echo "Testing is only available on Windows."
	@echo "Use GitHub Actions to test builds on CI."
	@echo ""
endif

clean-installer: ## Clean installer build artifacts
	@echo Cleaning installer artifacts...
ifeq ($(IS_WINDOWS),1)
	@powershell -NoProfile -ExecutionPolicy Bypass -Command "Remove-Item -Recurse -Force -ErrorAction SilentlyContinue dist, build, src-tauri/target, src-tauri/binaries, *.spec"
else
	@rm -rf dist build src-tauri/target src-tauri/binaries *.spec 2>/dev/null || true
endif
	@echo Installer artifacts cleaned

##@ Complete Workflows

all: install-dev format lint type-check test ## Run complete development workflow
	@echo Complete workflow finished successfully

release: clean build ## Prepare a release
	@echo Release prepared. Distribution packages in dist/
	@echo Next steps:
	@echo   1. Review CHANGELOG.md
	@echo   2. Update version in src/bot_mmorpg/__init__.py
	@echo   3. Create a git tag
	@echo   4. Push to repository
