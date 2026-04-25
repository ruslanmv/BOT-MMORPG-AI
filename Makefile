.PHONY: help install install-dev install-uv venv sync install-drivers download-drivers clean lint format format-check type-check test test-cov test-unit test-integration build docs clean-build clean-pyc clean-test clean-venv check all release install-launcher launcher install-all collect-data train-model test-model artifact build-installer verify-installer test-installer clean-installer ci ci-lint ci-format

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
  VERSION := $(shell $(SYS_PYTHON) scripts/version.py 2>/dev/null)
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
	@if [ -d ".venv" ]; then \
		echo "Virtual environment already exists in .venv/"; \
	else \
		echo "Creating virtual environment with Python 3.10..."; \
		uv venv --python 3.10; \
		echo "Virtual environment created in .venv/"; \
	fi

install: install-uv venv ## Install production dependencies
	@echo Installing production dependencies...
	@uv pip install -e .
	@echo Production dependencies installed

install-dev: install-uv venv ## Install development dependencies
	@echo Installing development dependencies...
	@uv pip install -e ".[dev]"
	@echo Development dependencies installed

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

clean: clean-build clean-pyc clean-test clean-venv ## Remove all artifacts
	@echo Cleaned all artifacts

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

##@ Application Commands

collect-data: ## Run data collection script
	@echo Starting data collection...
	@$(RUN_PYTHON) versions/0.01/1-collect_data.py

train-model: ## Run model training script
	@echo Starting model training...
	@$(RUN_PYTHON) versions/0.01/2-train_model.py

test-model: ## Run model testing/playing script
	@echo Starting model testing...
	@$(RUN_PYTHON) versions/0.01/3-test_model.py

##@ Running the Application

run: ## Run the application in development mode
	@echo "========================================"
	@echo " Starting BOT MMORPG AI"
	@echo "========================================"
	@echo "Frontend: tauri-ui/ (HTML/CSS/JavaScript)"
	@echo "Backend: Python sidecar (auto-started)"
	@echo ""
ifeq ($(IS_WINDOWS),1)
	@echo "Starting Tauri development server..."
	@cd src-tauri && cargo tauri dev
else
	@echo "Checking prerequisites..."
	@which cargo >/dev/null 2>&1 || (echo "ERROR: Rust/Cargo not found. Install from https://rustup.rs/" && exit 1)
	@echo "Starting Tauri development server..."
	@cd src-tauri && cargo tauri dev
endif

dev: run ## Alias for 'run' - Start development server

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
