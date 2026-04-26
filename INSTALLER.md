# BOT MMORPG AI - Installer Guide

This document provides comprehensive information about building, testing, and distributing the Windows installer for BOT MMORPG AI.

> **Debugging an installer or runtime bug?** Read
> [`docs/installer/`](./docs/installer/README.md) — focused per-file
> reference, bug index, debug tools, and worked case studies. Optimized
> for AI sessions / new developers landing cold.
>
> | Doc | Read when… |
> |---|---|
> | [01 — Files & Responsibilities](./docs/installer/01-files-and-responsibilities.md) | You don't know which file controls a given install behavior. |
> | [02 — Build Pipeline](./docs/installer/02-build-pipeline.md) | You want to understand how `make build-installer` produces the `.exe`. |
> | [03 — Runtime Flow](./docs/installer/03-runtime-flow.md) | You need to understand what the installed `.exe` does at install time and at app launch. |
> | [04 — Bug Index](./docs/installer/04-bug-index.md) | A user reported a symptom and you need to know which file to edit. |
> | [05 — Case Studies](./docs/installer/05-case-studies.md) | You want worked examples of bugs we already fixed. |
> | [06 — Debug Tools](./docs/installer/06-debug-tools.md) | You need PowerShell scripts / commands to inspect the installer. |
> | [07 — Build & Test](./docs/installer/07-build-and-test.md) | You need the actual `make` commands to run a build. |

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Building the Installer](#building-the-installer)
- [Testing the Installer](#testing-the-installer)
- [GitHub Workflows](#github-workflows)
- [Distribution](#distribution)
- [Troubleshooting](#troubleshooting)

## Overview

The BOT MMORPG AI installer is built using **Tauri** (Rust-based desktop framework) with a **Python backend sidecar** bundled using PyInstaller. The installer uses **NSIS** (Nullsoft Scriptable Install System) to create a professional Windows installer that:

- Installs the desktop application with a modern UI
- Bundles the Python AI backend as a sidecar process
- Automatically installs required drivers (Interception + vJoy)
- Creates desktop and start menu shortcuts
- Provides a clean uninstaller

### Key Features

✅ **One-click Installation** - Users just run the installer, no manual setup required
✅ **Driver Auto-Install** - Interception and vJoy drivers installed during setup
✅ **No Python Required** - Python runtime is bundled, users don't need Python installed
✅ **Professional UI** - Modern desktop app with easy-to-use interface
✅ **Clean Uninstall** - Complete removal of all components
✅ **GitHub Actions** - Automated builds on every commit

## Architecture

### Component Overview

```
BOT MMORPG AI Installer
│
├── Tauri Desktop App (Rust)
│   ├── Frontend UI (HTML/JS)
│   ├── Backend API (Rust)
│   └── Sidecar Manager
│
├── Python Backend Sidecar (PyInstaller)
│   ├── HTTP API Server (127.0.0.1:random_port)
│   ├── Bot Control (collect/train/play)
│   └── Driver Status Checking
│
├── Driver Installers
│   ├── Interception (keyboard/mouse)
│   └── vJoy (virtual gamepad)
│
└── NSIS Installer
    ├── Application Files
    ├── Driver Installation
    ├── Shortcuts Creation
    └── Uninstaller
```

### Communication Flow

```
User Interface (Tauri)
        ↓
    Rust Backend
        ↓
  Python Sidecar (HTTP)
        ↓
   Bot Logic (Python)
        ↓
   Game Automation
```

### File Structure

```
BOT-MMORPG-AI/
├── src-tauri/              # Tauri application
│   ├── src/                # Rust source code
│   ├── binaries/           # Sidecar binaries (generated)
│   ├── drivers/            # Driver installers (copied during build)
│   ├── resources/          # Additional resources
│   ├── Cargo.toml          # Rust dependencies
│   └── tauri.conf.json     # Tauri configuration
│
├── tauri-ui/               # Frontend UI
│   ├── index.html          # Main UI page
│   └── main.js             # UI logic
│
├── backend/                # Python backend
│   └── main_backend.py     # Sidecar HTTP server
│
├── installer/              # Installer configuration
│   └── nsis_template.nsi   # NSIS installer template
│
├── scripts/                # Build scripts
│   ├── build_pipeline.ps1      # Main build script
│   ├── verify_installer.ps1    # Verification script
│   ├── test_installer.ps1      # Testing script
│   └── install_drivers.ps1     # Driver install helper
│
└── .github/workflows/      # CI/CD workflows
    ├── build-windows-installer.yml
    └── release.yml
```

## Prerequisites

### Development Machine Requirements

To build the installer, you need:

#### Required Software

1. **Windows 10/11** (64-bit)
2. **Python 3.10 or 3.11** - [Download](https://www.python.org/downloads/)
3. **Rust** (latest stable) - [Install](https://rustup.rs/)
4. **Node.js 18+** (optional, for UI development) - [Download](https://nodejs.org/)
5. **Git** - [Download](https://git-scm.com/)

#### Required Tools

The build pipeline will automatically install:
- **Tauri CLI** - Installed via `cargo install tauri-cli`
- **PyInstaller** - Installed via pip

#### Driver Installers (Optional for Testing)

For a fully functional installer, you need:
- `install-interception.exe` in `frontend/input_record/`
- `vJoySetup.exe` in `versions/0.01/pyvjoy/`

> **Note**: The build will create placeholders if these are missing, but the installer won't have driver support.

### Verifying Prerequisites

Run this PowerShell script to check if you have everything:

```powershell
# Check Python
python --version

# Check Rust
cargo --version
rustc --version

# Check Git
git --version

# Optional: Check Node.js
node --version
npm --version
```

Expected output:
```
Python 3.11.x
cargo 1.xx.x
rustc 1.xx.x
git version 2.xx.x
v20.xx.x (Node.js)
```

## Building the Installer

### Quick Start

The simplest way to build the installer:

```powershell
# Clone the repository
git clone https://github.com/ruslanmv/BOT-MMORPG-AI.git
cd BOT-MMORPG-AI

# Run the build pipeline
.\scripts\build_pipeline.ps1
```

This will:
1. ✅ Create a Python virtual environment
2. ✅ Install all Python dependencies
3. ✅ Build the Python backend with PyInstaller
4. ✅ Copy the backend to Tauri sidecar location
5. ✅ Copy driver installers
6. ✅ Build the Tauri application
7. ✅ Create the NSIS installer

**Output**: `src-tauri\target\release\bundle\nsis\BOT-MMORPG-AI_*.exe`

### Build Options

The build script supports several options:

```powershell
# Clean build (removes all previous build artifacts)
.\scripts\build_pipeline.ps1 -Clean

# Skip Python backend build (use existing)
.\scripts\build_pipeline.ps1 -SkipPython

# Skip Tauri build (only build backend)
.\scripts\build_pipeline.ps1 -SkipTauri

# Build and verify
.\scripts\build_pipeline.ps1 -Verify

# Combined options
.\scripts\build_pipeline.ps1 -Clean -Verify
```

### Step-by-Step Build Process

If you want to understand each step:

#### Step 1: Build Python Backend

```powershell
# Create virtual environment
python -m venv .venv

# Activate it
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -e .
pip install pyinstaller

# Build backend
pyinstaller --noconfirm --clean --onefile --name main-backend backend/main_backend.py

# The output will be in: dist/main-backend.exe
```

#### Step 2: Prepare Tauri Sidecar

```powershell
# Tauri requires sidecar binaries to have target triple suffix
$target = "x86_64-pc-windows-msvc"

# Create binaries directory
New-Item -Force -ItemType Directory src-tauri/binaries

# Copy and rename
Copy-Item dist/main-backend.exe "src-tauri/binaries/main-backend-$target.exe"
```

#### Step 3: Copy Driver Installers

```powershell
# Create driver directories
New-Item -Force -ItemType Directory src-tauri/drivers/interception
New-Item -Force -ItemType Directory src-tauri/drivers/vjoy
New-Item -Force -ItemType Directory src-tauri/resources/scripts

# Copy driver installers
Copy-Item frontend/input_record/install-interception.exe src-tauri/drivers/interception/
Copy-Item versions/0.01/pyvjoy/vJoySetup.exe src-tauri/drivers/vjoy/

# Copy install script
Copy-Item scripts/install_drivers.ps1 src-tauri/resources/scripts/
```

#### Step 4: Build Tauri Application

```powershell
# Navigate to Tauri directory
cd src-tauri

# Build the application
cargo tauri build

# The installer will be created in:
# target/release/bundle/nsis/BOT-MMORPG-AI_*.exe
```

### Build Time

Expected build times (on a modern PC):
- **First build**: 10-20 minutes (downloads and compiles dependencies)
- **Subsequent builds**: 2-5 minutes (incremental compilation)
- **Clean builds**: 5-10 minutes

## Testing the Installer

### Automated Testing

#### 1. Verify Build Artifacts

```powershell
.\scripts\verify_installer.ps1
```

This checks:
- ✅ Backend sidecar binary exists and is valid
- ✅ Driver installers are present
- ✅ Tauri application was built
- ✅ NSIS installer was created
- ✅ All files have reasonable sizes

#### 2. Test Installer Package

```powershell
.\scripts\test_installer.ps1
```

This validates:
- ✅ File is accessible
- ✅ File size is appropriate
- ✅ PE executable format is valid
- ✅ Digital signature check (optional)
- ✅ NSIS installer detection
- ✅ Component size analysis

### Manual Testing

#### Testing on Your Development Machine

⚠️ **Warning**: This will install the application on your system!

```powershell
# Find the installer
$installer = Get-ChildItem src-tauri/target/release/bundle/nsis/*.exe | Select-Object -First 1

# Run installer
Start-Process $installer.FullName
```

#### Testing on a Clean VM

**Recommended approach** for proper testing:

1. **Create a Windows VM** (VirtualBox, Hyper-V, or VMware)
   - Windows 10/11 (64-bit)
   - 4GB RAM minimum
   - 20GB disk space

2. **Copy the installer** to the VM

3. **Run the installer** with admin privileges

4. **Verify**:
   - Desktop shortcut created
   - Start menu shortcut created
   - Application launches
   - Drivers installed (check Device Manager)
   - All features work

5. **Test Uninstaller**:
   - Run uninstaller from Control Panel
   - Verify all files removed
   - Check no leftover registry entries

## GitHub Workflows

### Automated Build Workflow

**File**: `.github/workflows/build-windows-installer.yml`

This workflow runs on:
- Every push to `main`, `develop`, or `claude/**` branches
- Every pull request to `main` or `develop`
- Manual trigger via GitHub Actions UI

**What it does**:
1. Sets up Python, Rust, and Node.js
2. Installs dependencies
3. Builds Python backend with PyInstaller
4. Builds Tauri application
5. Creates NSIS installer
6. Runs automated tests
7. Uploads installer as artifact (30-day retention)

**Artifacts**: Available in the workflow run for download

### Release Workflow

**File**: `.github/workflows/release.yml`

This workflow runs on:
- Git tags matching `v*.*.*` (e.g., `v1.0.0`)
- Manual trigger with version input

**What it does**:
1. Creates a GitHub Release
2. Builds the installer
3. Uploads installer to the release
4. Generates release notes
5. Archives installer as artifact (90-day retention)

### Triggering a Release

#### Option 1: Git Tag (Recommended)

```bash
# Create and push a tag
git tag v1.0.0
git push origin v1.0.0
```

#### Option 2: Manual Dispatch

1. Go to **Actions** tab on GitHub
2. Select **Release** workflow
3. Click **Run workflow**
4. Enter version (e.g., `v1.0.0`)
5. Click **Run workflow**

### Workflow Status

Check workflow status:
- Green checkmark ✅ = Build successful
- Red X ❌ = Build failed
- Yellow dot 🟡 = Build in progress

## Distribution

### Download Links

After a release is created:

**Direct Download**:
```
https://github.com/ruslanmv/BOT-MMORPG-AI/releases/latest/download/BOT-MMORPG-AI-v1.0.0-Windows-Installer.exe
```

**Release Page**:
```
https://github.com/ruslanmv/BOT-MMORPG-AI/releases
```

### Installation Instructions for Users

Include this in your release notes:

---

### 🎮 How to Install

1. **Download** the installer (`BOT-MMORPG-AI-*-Windows-Installer.exe`)
2. **Right-click** and select **"Run as administrator"**
3. **Follow** the installation wizard
4. **Wait** for drivers to install (may take 1-2 minutes)
5. **Launch** from desktop shortcut or start menu

### 📋 System Requirements

- Windows 10/11 (64-bit)
- 8GB RAM (16GB recommended)
- NVIDIA GPU recommended
- 5GB free disk space

### 🔧 First-Time Setup

1. Launch BOT MMORPG AI
2. Click **"Collect Data"** and play your game for 10-15 minutes
3. Click **"Train Model"** and wait for training to complete (30-60 minutes)
4. Click **"Start Bot"** to let the AI play!

---

### Code Signing (Future Enhancement)

For production releases, consider code signing:

1. **Get a Code Signing Certificate**
   - DigiCert, Sectigo, or Comodo
   - Costs ~$200-500/year

2. **Sign the installer**:
   ```powershell
   signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com installer.exe
   ```

3. **Benefits**:
   - No Windows SmartScreen warning
   - Users trust signed software
   - Professional appearance

## Troubleshooting

### Common Build Issues

#### Issue: "Python not found"

**Solution**:
```powershell
# Add Python to PATH
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Python311", "User")

# Restart PowerShell and try again
```

#### Issue: "Rust/Cargo not found"

**Solution**:
```powershell
# Install Rust from https://rustup.rs/
# Restart PowerShell after installation
```

#### Issue: "PyInstaller failed"

**Solution**:
```powershell
# Clear PyInstaller cache
pyinstaller --clean backend/main_backend.py

# Or reinstall PyInstaller
pip uninstall pyinstaller
pip install pyinstaller
```

#### Issue: "Tauri build failed"

**Solution**:
```powershell
# Clean Tauri build cache
cd src-tauri
cargo clean
cd ..

# Rebuild
.\scripts\build_pipeline.ps1 -Clean
```

#### Issue: "Driver installers not found"

**Solution**:
The build will create placeholders automatically. For production builds:
1. Download Interception driver
2. Download vJoy installer
3. Place in correct directories
4. Rebuild

#### Issue: "NSIS installer not created"

**Solution**:
```powershell
# Check if NSIS is installed (Tauri bundles it)
# If build succeeded but no installer:

# 1. Check Tauri config
cat src-tauri/tauri.conf.json

# 2. Verify bundle settings
# "bundle": {
#   "active": true,
#   "targets": "all"
# }

# 3. Rebuild
.\scripts\build_pipeline.ps1 -Clean
```

### Installer Issues

#### Issue: "Installer fails to run"

**Symptoms**: Double-clicking installer does nothing

**Solution**:
- Run as administrator
- Check antivirus (may block unsigned executables)
- Verify installer is not corrupted (re-download)

#### Issue: "Driver installation fails"

**Symptoms**: Installer completes but drivers not installed

**Solution**:
- Must run installer as administrator
- Windows driver signature enforcement may block
- Check Windows Update for driver updates

#### Issue: "Application won't start"

**Symptoms**: Shortcuts created but app crashes on launch

**Solution**:
```powershell
# Check Windows Event Viewer for errors
eventvwr.msc

# Look in:
# Windows Logs > Application
# Filter for "Error" and "bot-mmorpg-ai"
```

### GitHub Workflow Issues

#### Issue: "Workflow fails in GitHub Actions"

**Solution**:
1. Check the workflow logs
2. Look for red error messages
3. Common causes:
   - Missing dependencies
   - Python version mismatch
   - Rust compilation errors
   - Out of disk space

#### Issue: "Artifact upload fails"

**Solution**:
- Check artifact size (< 2GB limit)
- Verify artifact paths are correct
- Check GitHub storage quota

### Getting Help

If you encounter issues not covered here:

1. **Check GitHub Issues**: [Issues Page](https://github.com/ruslanmv/BOT-MMORPG-AI/issues)
2. **Join Slack**: [#bot-mmorpg-ai](https://ruslanmv.slack.com/archives/C0A5N63DKSS)
3. **Email Support**: contact@ruslanmv.com

## Advanced Topics

### Customizing the UI

Edit `tauri-ui/index.html` and `tauri-ui/main.js` to customize the UI.

### Adding Features to Backend

Edit `backend/main_backend.py` to add new API endpoints.

### Modifying NSIS Installer

Edit `installer/nsis_template.nsi` to customize the installation process.

### Multi-Platform Support

Future support for macOS/Linux:
- Replace Windows drivers with platform-specific alternatives
- Adjust Tauri config for multiple targets
- Create separate build workflows

## License

This installer is part of the BOT MMORPG AI project, licensed under Apache 2.0.

See [LICENSE](LICENSE) for details.

---

**Made with ❤️ by the AI Gaming Community**
