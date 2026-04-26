<#
Build pipeline (Windows) - Optimized Architecture (No PyInstaller)
=================================================================

This pipeline uses embedded Python directly for ALL Python operations,
eliminating the need for PyInstaller and reducing installer size by ~500MB.

Steps:
1) Build wheelhouse + lock for OFFLINE installs
2) Bundle embeddable Python into src-tauri/resources/python/
3) Pre-install ALL Python deps (including PyTorch) into site-packages
4) UI Smoke Tests
5) Copy driver installers + scripts
6) Bundle versions folder
7) Build Tauri app + NSIS installer

Architecture:
- Single embedded Python 3.10 runtime handles everything
- Backend runs as Python script (not PyInstaller EXE)
- ML scripts, backend, and modelhub share the same Python environment
- Installer size reduced from ~1.3GB to ~800MB

Requirements:
- Host Python 3.10+ available as `python` (BUILD time only)
- Rust toolchain + cargo (install via rustup)
- Tauri CLI (cargo install tauri-cli)
- NSIS installed (Tauri bundler uses it)

Usage:
  powershell -NoProfile -ExecutionPolicy Bypass -File scripts\build_pipeline.ps1 [-SkipPython] [-SkipTauri] [-Clean] [-Verify] [-SkipRustInstall] [-SkipTauriCliInstall]
#>

param(
  [switch]$SkipPython,
  [switch]$SkipTauri,
  [switch]$Clean,
  [switch]$Verify,
  [switch]$SkipRustInstall,
  [switch]$SkipTauriCliInstall,
  # Override the version baked into the installer filename and the app's
  # internal package.version. CI passes the release tag (with the leading
  # `v` stripped); local builds can omit this and the version stays as
  # whatever tauri.conf.json says (currently 1.0.0).
  # MUST be a valid semver: 0.2.2, 0.2.2-nightly.abc1234, 1.0.0-rc.1, etc.
  [string]$Version = ""
)

$ErrorActionPreference = "Stop"

function Log-Ok([string]$msg)   { Write-Host "[OK]   $msg" -ForegroundColor Green }
function Log-Info([string]$msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Log-Warn([string]$msg) { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Log-Fail([string]$msg) { Write-Host "[FAIL] $msg" -ForegroundColor Red }

function Log-Step($step, [string]$msg) {
  # `$step` is untyped on purpose: callers pass 6.5, 6.6, 6.7, 6.9 as
  # sub-steps. Typing as [int] would silently truncate/round those to 6/7
  # and make the log say "STEP 7: Preflight" three times. Accept anything
  # and stringify it.
  Write-Host ""
  Write-Host "======================================"
  Write-Host (" STEP {0}: {1}" -f ([string]$step), $msg)
  Write-Host "======================================"
}

function Refresh-Path {
  $machine = [Environment]::GetEnvironmentVariable("Path", "Machine")
  $user    = [Environment]::GetEnvironmentVariable("Path", "User")
  $env:Path = "$machine;$user"

  $cargoBin = Join-Path $env:USERPROFILE ".cargo\bin"
  if (Test-Path $cargoBin) {
    if ($env:Path -notlike "*$cargoBin*") {
      $env:Path += ";$cargoBin"
    }
  }
}

function Test-Command-Runnable([string]$name) {
  try {
    if (Get-Command $name -ErrorAction SilentlyContinue) {
      $null = & $name --version 2>&1
      return ($LASTEXITCODE -eq 0)
    }
    return $false
  } catch {
    return $false
  }
}

function Ensure-Uv {
  # Install strategy (in priority order):
  #   1. Already on PATH? -> done.
  #   2. Official astral.sh PowerShell installer (adds %USERPROFILE%\.local\bin
  #      to PATH correctly -- this is what `pip install --user uv` fails at).
  #   3. `pip install --user uv` as last-resort fallback, with explicit PATH
  #      augmentation so the pipeline can still use it in this session.
  #   4. Give up cleanly. The pipeline already has a pip fallback code path.

  Refresh-Path
  if (Test-Command-Runnable "uv") {
    $uvVersion = & uv --version 2>&1
    Log-Ok "uv found: $uvVersion"
    return $true
  }

  # (2) Official installer -- production-grade, handles PATH + shims.
  Log-Info "uv not found. Installing via the official Astral installer..."
  try {
    $prevEP = $env:PSExecutionPolicyPreference
    try {
      # `irm | iex` is the documented bootstrap. We scope it with a subshell-ish
      # pwsh invocation so its side effects on $env:PATH take immediate effect.
      $installerUrl = "https://astral.sh/uv/install.ps1"
      $script = Invoke-RestMethod -Uri $installerUrl -UseBasicParsing
      Invoke-Expression $script
    } finally {
      $env:PSExecutionPolicyPreference = $prevEP
    }

    # astral.sh installer puts uv.exe in %USERPROFILE%\.local\bin by default.
    $uvCargoBin = Join-Path $env:USERPROFILE ".local\bin"
    if (Test-Path $uvCargoBin) {
      if ($env:Path -notlike "*$uvCargoBin*") { $env:Path = "$uvCargoBin;$env:Path" }
    }
    Refresh-Path

    if (Test-Command-Runnable "uv") {
      $uvVersion = & uv --version 2>&1
      Log-Ok "uv installed via astral installer: $uvVersion"
      return $true
    }
    Log-Warn "astral installer ran but uv still not runnable; trying pip fallback..."
  } catch {
    Log-Warn "Astral installer failed: $_"
    Log-Info "Falling back to pip..."
  }

  # (3) Pip fallback -- last resort. Note this installs into the user scripts
  # dir which is frequently not on PATH; we splice it in ourselves.
  try {
    & python -m pip install --user uv --quiet
    if ($LASTEXITCODE -ne 0) { throw "pip install uv failed (exit=$LASTEXITCODE)" }

    # python -m site --user-base gives us a reliable Scripts dir.
    $userBase = & python -m site --user-base 2>&1
    if ($LASTEXITCODE -eq 0 -and $userBase) {
      $userScripts = Join-Path ($userBase.Trim()) "Scripts"
      if (Test-Path $userScripts) {
        if ($env:Path -notlike "*$userScripts*") { $env:Path = "$userScripts;$env:Path" }
      }
    }
    Refresh-Path

    if (Test-Command-Runnable "uv") {
      $uvVersion = & uv --version 2>&1
      Log-Ok "uv installed via pip fallback: $uvVersion"
      return $true
    }
    Log-Warn "uv installed via pip but not runnable in this session."
    return $false
  } catch {
    Log-Warn "uv pip fallback failed: $_"
    Log-Info "Continuing without uv (pipeline has a pip code path)."
    return $false
  }
}

function Ensure-Rust {
  Refresh-Path
  if (Test-Command-Runnable "cargo") { return $true }

  Log-Warn "Rust/Cargo not found (or not runnable) in PATH."

  if ($SkipRustInstall) {
    Log-Warn "SkipRustInstall enabled; not attempting Rust install."
    return $false
  }

  if (-not (Test-Command-Runnable "winget")) {
    Log-Warn "winget not available; cannot auto-install Rust."
    return $false
  }

  Log-Info "Attempting to install Rust via winget (Rustup)..."
  try {
    & winget install -e --id Rustlang.Rustup --accept-package-agreements --accept-source-agreements --disable-interactivity
    if ($LASTEXITCODE -ne 0) {
      Log-Warn "winget Rust install failed: winget exited with code $LASTEXITCODE"
      return $false
    }

    Log-Ok "Rustup installed. Refreshing PATH..."
    Refresh-Path
    if (Test-Command-Runnable "cargo") { return $true }

    Log-Warn "Cargo installed but not executable in this session."
    return $false
  } catch {
    Log-Warn "winget Rust install exception: $_"
    return $false
  }
}

function Ensure-TauriCli {
  if (-not (Test-Command-Runnable "cargo")) { return $false }

  if ($SkipTauriCliInstall) {
    return (Test-Command-Runnable "cargo-tauri")
  }

  try {
    $v = & cargo tauri --version 2>&1
    if ($LASTEXITCODE -eq 0) {
      Log-Ok "Tauri CLI found: $v"
      return $true
    }
  } catch {}

  Log-Warn "Tauri CLI not found. Installing tauri-cli..."
  try {
    & cargo install tauri-cli --version "^1.0"
    if ($LASTEXITCODE -ne 0) {
      Log-Warn "cargo install tauri-cli failed with exit code $LASTEXITCODE"
      return $false
    }

    Refresh-Path
    try {
      $v2 = & cargo tauri --version 2>&1
      if ($LASTEXITCODE -eq 0) {
        Log-Ok "Tauri CLI installed: $v2"
        return $true
      }
    } catch {}

    Log-Warn "tauri-cli installed but still not runnable."
    return $false
  } catch {
    Log-Warn "Tauri CLI check/install failed: $_"
    return $false
  }
}

function Find-PythonExe {
  param([string[]]$Roots)

  foreach ($r in $Roots) {
    if (-not (Test-Path $r)) { continue }

    $hit = Get-ChildItem -Path $r -Recurse -File -Filter "python.exe" -ErrorAction SilentlyContinue |
      Select-Object -First 1

    if ($hit) { return $hit.FullName }
  }
  return $null
}

function Write-PyRuntime-Manifest {
  param([string]$DstDir, [string]$PickedFrom)

  try {
    $mf = Join-Path $DstDir "py_runtime_manifest.txt"
    $lines = @()
    $lines += ("BuiltAt=" + (Get-Date).ToString("s"))
    $lines += ("Host=" + $env:COMPUTERNAME)
    $lines += ("PickedFrom=" + $PickedFrom)
    $lines += ("Root=" + $DstDir)

    $files = Get-ChildItem -Path $DstDir -Recurse -File -ErrorAction SilentlyContinue |
      Select-Object FullName, Length |
      Sort-Object FullName

    foreach ($f in $files) {
      $lines += ("FILE=" + $f.FullName + " SIZE=" + $f.Length)
    }
    Set-Content -Path $mf -Value $lines -Encoding UTF8
  } catch {
    Log-Warn ("Could not write py_runtime_manifest.txt: " + $_.Exception.Message)
  }
}

function Ensure-EmbeddedPythonDownloaded {
  param([string]$Root)

  $ver = "3.10.11"
  $arch = "amd64"
  $zipName = "python-$ver-embed-$arch.zip"
  $url = "https://www.python.org/ftp/python/$ver/$zipName"

  $dst = Join-Path $Root "third_party\python\python-$ver-embed-$arch"
  New-Item -ItemType Directory -Force -Path $dst | Out-Null

  if (Test-Path (Join-Path $dst "python.exe")) {
    return $dst
  }

  $zipPath = Join-Path $dst $zipName

  Log-Info ("Python runtime not found. Downloading embeddable Python: " + $url)
  try {
    Invoke-WebRequest -Uri $url -OutFile $zipPath -UseBasicParsing
    Expand-Archive -Path $zipPath -DestinationPath $dst -Force
    Remove-Item -Force $zipPath -ErrorAction SilentlyContinue
    return $dst
  } catch {
    throw ("Auto-download failed. Please manually download: " + $url + " and extract it to: " + $dst + "  Error=" + $_.Exception.Message)
  }
}

function Patch-EmbeddedPythonPth {
  param(
    [string]$PyDir,          # src-tauri/resources/python
    [string]$SitePackagesRel # ".\site-packages"
  )

  $pth = Get-ChildItem -Path $PyDir -Filter "python*._pth" -File -ErrorAction SilentlyContinue | Select-Object -First 1
  if (-not $pth) {
    Log-Warn "No python*._pth found under $PyDir. Embedded python may not see site-packages."
    return
  }

  $pthPath = $pth.FullName
  $lines = @()
  try { $lines = Get-Content $pthPath -ErrorAction SilentlyContinue } catch { $lines = @() }
  if (-not $lines) { $lines = @() }

  if ($lines -notcontains $SitePackagesRel) { $lines += $SitePackagesRel }
  if ($lines -notcontains "import site")    { $lines += "import site" }

  Set-Content -Path $pthPath -Value $lines -Encoding ASCII
  Log-Ok "Patched embedded _pth: $pthPath"
}

function Ensure-BundledSitePackages {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory=$true)]
    [string]$RootDir
  )

  Set-StrictMode -Version Latest
  $ErrorActionPreference = "Stop"

  function Invoke-Checked {
    param(
      [Parameter(Mandatory=$true)][string]$FilePath,
      [Parameter(Mandatory=$true)][string[]]$Arguments,
      [string]$ErrorMessage = "Command failed"
    )
    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
      throw "$ErrorMessage (exit=$LASTEXITCODE): $FilePath $($Arguments -join ' ')"
    }
  }

  function Ensure-PipAvailable {
    param(
      [Parameter(Mandatory=$true)][string]$PythonExe
    )

    # Try pip first
    try {
      & $PythonExe -m pip --version | Out-Null
      if ($LASTEXITCODE -eq 0) { return }
    } catch {}

    # Try ensurepip (works for many venvs; might not exist in some stripped envs)
    try {
      & $PythonExe -m ensurepip --upgrade | Out-Null
      if ($LASTEXITCODE -eq 0) { return }
    } catch {}

    # Final: explicit failure with actionable message
    throw "Host python has no pip and ensurepip failed. Fix your build venv by recreating it with pip (e.g. 'uv venv --seed' or 'py -3.10 -m venv .venv' then 'python -m ensurepip --upgrade'). Host python: $PythonExe"
  }

  # ---- Paths ----
  $pyRoot   = Join-Path $RootDir "src-tauri\resources\python"
  $pyExe    = Join-Path $pyRoot "python.exe"
  $sitePkgs = Join-Path $pyRoot "site-packages"

  if (-not (Test-Path $pyExe)) { throw "Bundled python.exe not found: $pyExe" }
  New-Item -ItemType Directory -Force -Path $sitePkgs | Out-Null

  # Where your wheelhouse lives (generated by prepare script)
  $wheelhouseTag = "win_amd64_cp310"
  $whRoot   = Join-Path $RootDir "third_party\wheelhouse\$wheelhouseTag"
  $whWheels = Join-Path $whRoot "wheels"
  if (-not (Test-Path $whWheels)) { throw "Wheelhouse wheels folder missing: $whWheels" }

  Log-Step 99 "Pre-bundling Python deps into installer (site-packages)"
  Log-Info "Target site-packages: $sitePkgs"
  Log-Info "Wheelhouse Source: $whWheels"

  # ---- Host Python (drives pip install into target) ----
  # Prefer .venv if it exists (local dev), otherwise discover Python 3.10 (CI)
  $hostPy = $null

  # 1) Local dev venv (preferred when a developer has run `make install`).
  $venvPy = Join-Path $RootDir ".venv\Scripts\python.exe"
  if (Test-Path $venvPy) {
    $hostPy = $venvPy
    Log-Info "Using build venv Python: $hostPy"
  }

  # 2) Embedded Python downloaded by THIS pipeline at STEP 2.
  #
  # Step 2 of build_pipeline.ps1 downloads python-3.10.11-embed-amd64 to
  # third_party/python/ and patches it for use as the bundled runtime.
  # That same Python is exactly what the wheelhouse (cp310 win_amd64) is
  # built against, so it's the most reliable host for Step 99 -- and
  # crucially it's ALWAYS available by the time we get here, even when
  # the user hasn't run `make install` to create .venv.
  #
  # Without this candidate Step 99 falls through to system PATH, which
  # on the user's machine is Python 3.11, mismatching the wheelhouse and
  # aborting the build with:
  #   "Step 99 must run with Python 3.10 to match wheelhouse
  #    (win_amd64_cp310). Got: 3.11"
  if (-not $hostPy) {
    $embeddedDir = Get-ChildItem -Path (Join-Path $RootDir "third_party\python") `
                                 -Directory -Filter "python-3.10*-embed-amd64" `
                                 -ErrorAction SilentlyContinue |
                   Sort-Object Name -Descending | Select-Object -First 1
    if ($embeddedDir) {
      $candidate = Join-Path $embeddedDir.FullName "python.exe"
      if (Test-Path $candidate) {
        $hostPy = $candidate
        Log-Info "Using bundled embedded Python (downloaded by STEP 2): $hostPy"
      }
    }
  }

  # 3) Windows Python Launcher (py -3.10)
  if (-not $hostPy) {
    Log-Info "Build venv + bundled embedded Python not found, searching for system Python 3.10..."
    try {
      $pyLauncher = Get-Command py -ErrorAction SilentlyContinue
      if ($pyLauncher) {
        $pyPath = & py -3.10 -c "import sys; print(sys.executable)" 2>$null
        if ($LASTEXITCODE -eq 0 -and $pyPath -and (Test-Path $pyPath)) {
          $hostPy = $pyPath.Trim()
          Log-Info "Found Python 3.10 via py launcher: $hostPy"
        }
      }
    } catch {}
  }

  # 4) GitHub Actions hostedtoolcache (setup-python puts 3.10 here)
  if (-not $hostPy) {
    $toolcacheBase = "C:\hostedtoolcache\windows\Python"
    if (Test-Path $toolcacheBase) {
      $py310Dir = Get-ChildItem -Path $toolcacheBase -Directory -Filter "3.10*" -ErrorAction SilentlyContinue |
        Sort-Object Name -Descending | Select-Object -First 1
      if ($py310Dir) {
        $candidate = Join-Path $py310Dir.FullName "x64\python.exe"
        if (Test-Path $candidate) {
          $hostPy = $candidate
          Log-Info "Found Python 3.10 in hostedtoolcache: $hostPy"
        }
      }
    }
  }

  # 5) Generic 'python' in PATH (last resort, may not be 3.10)
  if (-not $hostPy) {
    $sysPy = Get-Command python -ErrorAction SilentlyContinue
    if ($sysPy) {
      $hostPy = $sysPy.Source
      Log-Info "Using system Python (may not be 3.10): $hostPy"
    } else {
      throw "No Python found: tried .venv, third_party/python embedded, py launcher, hostedtoolcache, system 'python' in PATH"
    }
  }

  # Validate host python is 3.10 and 64-bit (wheelhouse is cp310 win_amd64)
  $hostInfo = & $hostPy -c "import sys,platform; print(f'{sys.version_info.major}.{sys.version_info.minor}|{platform.architecture()[0]}|{sys.executable}')"
  if ($LASTEXITCODE -ne 0) { throw "Failed to query host python info: $hostPy" }

  $parts = $hostInfo.Trim().Split('|')
  $hostVer  = $parts[0]
  $hostArch = $parts[1]
  if ($hostVer -ne "3.10") { throw "Step 99 must run with Python 3.10 to match wheelhouse ($wheelhouseTag). Got: $hostVer ($hostPy)" }
  if ($hostArch -ne "64bit") { throw "Step 99 requires 64-bit host python for win_amd64 wheels. Got: $hostArch ($hostPy)" }

  # Ensure pip exists (fixes: No module named pip)
  Ensure-PipAvailable -PythonExe $hostPy

  # Upgrade core build tools (quiet but logged to file)
  $pipLog = Join-Path $RootDir "build_pip_step99.log"
  Log-Info "Pip log: $pipLog"

  # See note in prepare_python_from_pyproject_embed310_target.ps1: pin
  # setuptools<82 so PyTorch 2.x's distutils shim doesn't break.
  Invoke-Checked -FilePath $hostPy -Arguments @(
    "-m","pip","install","--upgrade","pip","setuptools<82","wheel",
    "--disable-pip-version-check","--no-python-version-warning",
    "--log",$pipLog
  ) -ErrorMessage "Failed to upgrade host pip/setuptools/wheel"

  # ---- Deterministic clean target ----
  try {
    if (Test-Path $sitePkgs) {
      Get-ChildItem -Path $sitePkgs -Force -ErrorAction SilentlyContinue |
        Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    }
  } catch {}

  New-Item -ItemType Directory -Force -Path $sitePkgs | Out-Null

  # ---- Correct install strategy ----
  # DO NOT install "all wheels" with --no-deps (causes duplicates like pycparser 2.23 + 3.0).
  # Instead, install your project spec using the wheelhouse as the only source and let pip resolve.
  #
  # IMPORTANT: keep it offline:
  #   --no-index + --find-links wheelhouse
  #
  # Choose the same spec you used when building wheelhouse. If you already have a wheel for your project in wheelhouse,
  # pip will pick it from --find-links.
  $projectSpec = "bot-mmorpg-ai[launcher,backend,ml]"

  Log-Info "Installing project spec into bundled site-packages (offline): $projectSpec"

  Invoke-Checked -FilePath $hostPy -Arguments @(
    "-m","pip","install",
    "--no-index",
    "--find-links",$whWheels,
    "--target",$sitePkgs,
    "--upgrade",
    "--force-reinstall",
    "--disable-pip-version-check",
    "--no-python-version-warning",
    "--log",$pipLog,
    $projectSpec
  ) -ErrorMessage "Failed to install project deps into bundled site-packages from wheelhouse"

  # ---- Patch python._pth so embedded python sees .\site-packages and imports site ----
  Patch-EmbeddedPythonPth -PyDir $pyRoot -SitePackagesRel ".\site-packages"

  # ---- Size/NSIS fix: do not copy wheelhouse ----
  Log-Info "Skipping wheelhouse copy (using installed site-packages only) to save space and prevent NSIS mmapping errors."

  # ---- Smoke tests (use embedded python, not host) ----
  Log-Info "Smoke test: embedded python can import from bundled site-packages..."
  Invoke-Checked -FilePath $pyExe -Arguments @(
    "-c","import sys; import numpy; print('numpy_ok'); print('python_ok', sys.version)"
  ) -ErrorMessage "Bundled python cannot import numpy from site-packages"

  # PyTorch smoke test (required for ML features)
  Log-Info "Smoke test: PyTorch import..."
  Invoke-Checked -FilePath $pyExe -Arguments @(
    "-c","import torch; print('torch_ok', torch.__version__)"
  ) -ErrorMessage "Bundled python cannot import torch (PyTorch)"

  # Optional: tensorflow import only if installed (ml-legacy)
  $tfMarker1 = Join-Path $sitePkgs "tensorflow"
  $hasTf = (Test-Path $tfMarker1) -or ((Get-ChildItem -Path $sitePkgs -Filter "tensorflow-*.dist-info" -ErrorAction SilentlyContinue | Measure-Object).Count -gt 0)

  if ($hasTf) {
    Log-Info "Smoke test: tensorflow import (legacy, may take time)..."
    Invoke-Checked -FilePath $pyExe -Arguments @(
      "-c","import tensorflow as tf; print('tf_ok', tf.__version__)"
    ) -ErrorMessage "Bundled python cannot import tensorflow"
  } else {
    Log-Info "TensorFlow not detected (optional ml-legacy); skipping tf import test."
  }

  # ---- Prune site-packages to reduce NSIS file count ----
  # NSIS can fail or timeout when bundling >30k files. Remove unnecessary items.
  Log-Info "Pruning bundled site-packages to reduce installer file count..."

  $pruneCountBefore = (Get-ChildItem -Path $sitePkgs -Recurse -File -ErrorAction SilentlyContinue | Measure-Object).Count

  # Remove __pycache__ directories and .pyc files (not needed for embedded python)
  Get-ChildItem -Path $sitePkgs -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue |
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

  # Remove test/tests directories inside packages (not needed at runtime)
  Get-ChildItem -Path $sitePkgs -Recurse -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -match "^(tests?|testing)$" } |
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

  # Remove .dist-info directories (metadata only, not needed at runtime)
  Get-ChildItem -Path $sitePkgs -Directory -Filter "*.dist-info" -ErrorAction SilentlyContinue |
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

  # Remove stray .pyc files outside __pycache__
  Get-ChildItem -Path $sitePkgs -Recurse -File -Filter "*.pyc" -ErrorAction SilentlyContinue |
    Remove-Item -Force -ErrorAction SilentlyContinue

  # Remove type stubs (.pyi files) - not needed at runtime
  Get-ChildItem -Path $sitePkgs -Recurse -File -Filter "*.pyi" -ErrorAction SilentlyContinue |
    Remove-Item -Force -ErrorAction SilentlyContinue

  $pruneCountAfter = (Get-ChildItem -Path $sitePkgs -Recurse -File -ErrorAction SilentlyContinue | Measure-Object).Count
  $pruned = $pruneCountBefore - $pruneCountAfter
  Log-Ok "Pruned $pruned files from site-packages ($pruneCountBefore -> $pruneCountAfter files)"

  Log-Ok "Bundled site-packages ready (production-safe install strategy)."
}


# ---- Root directory ----
$scriptPath = $MyInvocation.MyCommand.Path
if ([string]::IsNullOrWhiteSpace($scriptPath)) { $scriptPath = $PSCommandPath }
$scriptDir = Split-Path -Parent $scriptPath
$root = (Resolve-Path (Join-Path $scriptDir "..")).Path

# ---- Guard: ensure versions folder exists (better error than Tauri glob failure) ----
$versionsDir = Join-Path $root "versions"
if (-not (Test-Path $versionsDir)) {
  throw "Missing required folder: $versionsDir (expected versions/0.01 etc.)"
}

Log-Info "Root directory: $root"
Log-Info ("Build started at: {0}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"))
Write-Host ""

# ================================
# STEP 0: Checking Prerequisites
# ================================
Log-Step 0 "Checking Prerequisites"

try {
  $pythonVersion = & python --version 2>&1
  Log-Ok "Host Python found: $pythonVersion"
} catch {
  Log-Fail "Host Python not found. Please install Python 3.10+"
  exit 1
}

$useUv = Ensure-Uv

if (-not $SkipTauri) {
  $hasCargo = Ensure-Rust
  if (-not $hasCargo) {
    Log-Fail "Rust/Cargo is required to build the installer."
    Log-Info "MANUAL FIX:"
    Log-Info "  1. Download https://rustup.rs/ and install."
    Log-Info "  2. Restart your terminal."
    Log-Info "  3. Verify by running: cargo --version"
    exit 1
  }

  try {
    $rustVersion = & cargo --version 2>&1
    Log-Ok "Rust found: $rustVersion"
  } catch {
    Log-Fail "Cargo command exists but failed to run. Please reinstall Rustup."
    exit 1
  }

  $hasTauri = Ensure-TauriCli
  if (-not $hasTauri) {
    Log-Fail "Tauri CLI is required."
    Log-Info "Run: cargo install tauri-cli"
    exit 1
  }
} else {
  Log-Warn "SkipTauri enabled; Rust/Cargo not required."
}

# ================================
# Optional Clean
# ================================
if ($Clean) {
  Log-Step 1 "Cleaning Build Artifacts"

  $cleanTargets = @(
    "dist",
    "build",
    ".venv",
    "src-tauri\target",
    "src-tauri\binaries",
    "src-tauri\drivers",
    "src-tauri\resources\scripts",
    "src-tauri\resources\sidecar",
    "src-tauri\resources\python\site-packages",
    "src-tauri\resources\wheelhouse"
  )

  foreach ($rel in $cleanTargets) {
    $p = Join-Path $root $rel
    if (Test-Path $p) {
      Log-Info "Removing: $rel"
      Remove-Item -Recurse -Force $p -ErrorAction SilentlyContinue
    }
  }

  Get-ChildItem -Path $root -Filter "*.spec" -ErrorAction SilentlyContinue | ForEach-Object {
    Log-Info "Removing: $($_.Name)"
    Remove-Item -Force $_.FullName
  }

  Log-Ok "Clean completed"
}

# ===================== BUNDLE_PY_RUNTIME_BEGIN =====================
# STEP 1: Build wheelhouse + lock for OFFLINE installs
# =====================
Log-Step 1 "Preparing wheelhouse (cp310 win_amd64)"

# Run the prepare script to populate wheels
& (Join-Path $root "scripts\prepare_python_from_pyproject_embed310_target.ps1") `
  -Extras @("launcher","backend","ml") `
  -TargetTag "win_amd64_cp310" `
  -RebuildTarget
if ($LASTEXITCODE -ne 0) { exit 1 }
# ===================== BUNDLE_PY_RUNTIME_END =====================

# ================================
# STEP 2: Bundle embeddable python into src-tauri/resources/python
# ================================
Log-Step 2 "Bundling embeddable Python runtime"

try {
  $pyDst = Join-Path $root "src-tauri\resources\python"
  New-Item -ItemType Directory -Force -Path $pyDst | Out-Null

  # Clean destination (keep README.txt if present)
  Get-ChildItem $pyDst -Force -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -ne "README.txt" } |
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

  $searchRoots = @(
    (Join-Path $root "third_party\python"),
    (Join-Path $root "src-tauri\resources\python")
  )

  $pyExePath = Find-PythonExe -Roots $searchRoots

  if (-not $pyExePath) {
    $dlDir = Ensure-EmbeddedPythonDownloaded -Root $root
    $pyExePath = Find-PythonExe -Roots @($dlDir, (Join-Path $root "third_party\python"))
  }

  if (-not $pyExePath) {
    throw ("Python runtime not found. Expected python.exe somewhere under: " + ($searchRoots -join " OR "))
  }

  $pickedDir = Split-Path -Parent $pyExePath
  Copy-Item -Recurse -Force (Join-Path $pickedDir "*") $pyDst
  Log-Ok ("Bundled Python runtime from: " + $pickedDir)

  $pyExeRoot = Join-Path $pyDst "python.exe"
  if (-not (Test-Path $pyExeRoot)) {
    throw ("Python runtime copy succeeded but python.exe not at root: " + $pyExeRoot + " (pickedDir=" + $pickedDir + ")")
  }

  Write-PyRuntime-Manifest -DstDir $pyDst -PickedFrom $pickedDir
} catch {
  Log-Fail "$_"
  exit 1
}

# ================================
# STEP 3: Pre-bundle ALL python deps into site-packages (includes PyTorch)
# ================================
try {
  Ensure-BundledSitePackages -RootDir $root
} catch {
  Log-Fail "$_"
  exit 1
}

# ================================
# STEP 4: UI Smoke Tests (pre-build)
# ================================
Log-Step 4 "UI Smoke Tests (pre-build)"

try {
  Log-Info "Running UI/installer smoke tests..."
  if (Test-Path "tests/test_tauri_ui_smoke.py") {
      & python tests/test_tauri_ui_smoke.py
      if ($LASTEXITCODE -ne 0) { throw "UI smoke tests failed (exit code $LASTEXITCODE)" }
      Log-Ok "UI smoke tests passed"
  } else {
      Log-Warn "Smoke test file not found. Skipping."
  }
} catch {
  Log-Fail "$_"
  exit 1
}

# ================================
# STEP 5: Verify Backend Python Files (No PyInstaller - Direct Python Execution)
# ================================
# NOTE: We no longer build a PyInstaller sidecar. The Tauri app runs the backend
# directly using the embedded Python runtime. This reduces installer size by ~500MB.
Log-Step 5 "Verifying Backend Python Files"

$backendEntry = Join-Path $root "backend\entry_main.py"
$modelhubDir  = Join-Path $root "modelhub"

if (-not (Test-Path $backendEntry)) {
  Log-Fail "Backend entry point not found: $backendEntry"
  exit 1
}
Log-Ok "Backend entry point exists: $backendEntry"

if (-not (Test-Path $modelhubDir)) {
  Log-Fail "Modelhub directory not found: $modelhubDir"
  exit 1
}
Log-Ok "Modelhub directory exists: $modelhubDir"

# Verify key modelhub modules exist
$modelhubTauri = Join-Path $modelhubDir "tauri.py"
if (-not (Test-Path $modelhubTauri)) {
  Log-Warn "Modelhub tauri.py not found: $modelhubTauri"
} else {
  Log-Ok "Modelhub tauri.py exists"
}

# Verify the bundled embedded Python can import core dependencies
$bundledPyExe = Join-Path $root "src-tauri\resources\python\python.exe"
if (Test-Path $bundledPyExe) {
  Log-Info "Smoke testing bundled Python imports (fastapi, uvicorn)..."
  try {
    & $bundledPyExe -c "import fastapi, uvicorn; print('Backend deps OK')" 2>$null
    if ($LASTEXITCODE -eq 0) {
      Log-Ok "Bundled Python can import backend dependencies"
    } else {
      Log-Warn "Bundled Python failed to import fastapi/uvicorn (may be installed at runtime)"
    }
  } catch {
    Log-Warn "Could not test bundled Python imports: $_"
  }
} else {
  Log-Warn "Bundled Python not yet available (will be created in earlier step)"
}

Log-Ok "Backend verification complete (PyInstaller build SKIPPED - using direct Python execution)"

# ================================
# STEP 6: Copy driver installers + scripts
# ================================
Log-Step 6 "Copying Driver Installers + Scripts"

$drvInterDir = Join-Path $root "src-tauri\drivers\interception"
$drvVjoyDir  = Join-Path $root "src-tauri\drivers\vjoy"
$resScripts  = Join-Path $root "src-tauri\resources\scripts"

New-Item -Force -ItemType Directory $drvInterDir | Out-Null
New-Item -Force -ItemType Directory $drvVjoyDir  | Out-Null
New-Item -Force -ItemType Directory $resScripts  | Out-Null

$mlScriptSrc = Join-Path $root "scripts\install_ml_deps.ps1"
$mlScriptDst = Join-Path $resScripts "install_ml_deps.ps1"
if (Test-Path $mlScriptSrc) {
  Copy-Item -Force $mlScriptSrc $mlScriptDst
  Log-Ok "Install ML deps script copied"
} else {
  Log-Warn "Install ML deps script not found: $mlScriptSrc"
}

$interceptionSrc = Join-Path $root "frontend\input_record\install-interception.exe"
$interceptionDst = Join-Path $drvInterDir "install-interception.exe"
if (Test-Path $interceptionSrc) {
  Copy-Item -Force $interceptionSrc $interceptionDst
  Log-Ok "Interception driver copied"
} else {
  Log-Warn "Interception installer not found: $interceptionSrc"
  Log-Warn "Creating placeholder (installer will not have driver support)"
  "Placeholder" | Set-Content -Path $interceptionDst -NoNewline
}

$vjoySrc = Join-Path $root "versions\0.01\pyvjoy\vJoySetup.exe"
$vjoyDst = Join-Path $drvVjoyDir "vJoySetup.exe"
if (Test-Path $vjoySrc) {
  Copy-Item -Force $vjoySrc $vjoyDst
  Log-Ok "vJoy driver copied"
} else {
  Log-Warn "vJoy installer not found: $vjoySrc"
  Log-Warn "Creating placeholder (installer will not have driver support)"
  "Placeholder" | Set-Content -Path $vjoyDst -NoNewline
}

$installScriptSrc = Join-Path $root "scripts\install_drivers.ps1"
$installScriptDst = Join-Path $resScripts "install_drivers.ps1"
if (Test-Path $installScriptSrc) {
  Copy-Item -Force $installScriptSrc $installScriptDst
  Log-Ok "Install drivers script copied"
} else {
  Log-Warn "Install drivers script not found: $installScriptSrc"
}

$modelsScriptSrc = Join-Path $root "scripts\download_models.ps1"
$modelsScriptDst = Join-Path $resScripts "download_models.ps1"
if (Test-Path $modelsScriptSrc) {
  Copy-Item -Force $modelsScriptSrc $modelsScriptDst
  Log-Ok "Download models script copied"
} else {
  Log-Warn "Download models script not found: $modelsScriptSrc"
}


Log-Step 6.5 "Bundling versions into resources (runtime files only)"

# We only ship what the installed app actually runs. The source `versions/0.01/`
# contains research notebooks (*.ipynb), screenshots (*.png/*.jpg), datasets,
# and a Windows-only `pyvjoy/` driver folder. Including any of those would:
#   (a) bloat the installer by hundreds of MB,
#   (b) ship a file with a space in its name (`numpy analsis.ipynb`) which
#       breaks the NSIS `File /oname=` directive and fails the release build
#       on line 254 (the failure we are fixing here),
#   (c) ship installer-unrelated assets that were never meant for end users.
#
# Allow-list:
#   - *.py  (the ML scripts themselves, incl. helper modules like grabscreen.py)
#   - *.txt (requirements lock, etc.)
#   - *.dll / *.lib (vJoy interop libs consumed by pyvjoy.py at runtime)

$srcVersions = Join-Path $root "versions"
$dstVersions = Join-Path $root "src-tauri\resources\versions"

if (-not (Test-Path $srcVersions)) { throw "Missing versions folder: $srcVersions" }

if (Test-Path $dstVersions) {
  Remove-Item $dstVersions -Recurse -Force -ErrorAction SilentlyContinue
}
New-Item -ItemType Directory -Force -Path $dstVersions | Out-Null

$allowedExt = @(".py", ".txt", ".dll", ".lib")
$copied = 0
$skipped = 0
$skippedSpaceNames = @()

Get-ChildItem -Path $srcVersions -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object {
  $ext = $_.Extension.ToLowerInvariant()
  $shouldCopy = $allowedExt -contains $ext

  # Defense in depth: refuse any filename with a space, even if the extension
  # is allowed. An unquoted /oname= in NSIS cannot handle spaces. If we ever
  # need such a file at runtime, rename it in-repo.
  if ($_.Name -match '\s') {
    $shouldCopy = $false
    $skippedSpaceNames += $_.FullName
  }

  if ($shouldCopy) {
    $rel = $_.FullName.Substring($srcVersions.Length).TrimStart('\','/')
    $dst = Join-Path $dstVersions $rel
    $dstDir = Split-Path -Parent $dst
    if (-not (Test-Path $dstDir)) { New-Item -ItemType Directory -Force -Path $dstDir | Out-Null }
    Copy-Item -Force $_.FullName $dst
    $copied++
  } else {
    $skipped++
  }
}

Log-Ok ("Versions staged: {0} files copied, {1} skipped (notebooks/images/datasets/space-in-name)" -f $copied, $skipped)
if ($skippedSpaceNames.Count -gt 0) {
  Log-Warn ("Skipped {0} file(s) with spaces in the name (would break NSIS):" -f $skippedSpaceNames.Count)
  foreach ($n in $skippedSpaceNames) { Log-Warn ("  - " + $n) }
}

# Sanity: require the three primary scripts to have made it through.
$mustExist = @(
  "0.01\1-collect_data.py",
  "0.01\2-train_model.py",
  "0.01\3-test_model.py"
)
foreach ($rel in $mustExist) {
  $full = Join-Path $dstVersions $rel
  if (-not (Test-Path $full)) {
    throw "versions staging failed: required file missing -> $full"
  }
}
Log-Ok "Versions staging verified: primary scripts present"


Log-Step 6.6 "Bundling backend and modelhub into resources (filtered)"

# Reusable filter: stage a Python source tree into the bundle while rejecting
# local editor/OS junk that commonly sneaks into working copies and would
# either (a) bloat the installer or (b) contain whitespace in the filename and
# break NSIS's `File /oname=` directive (the same failure mode we fixed for
# versions/ in STEP 6.5).
#
# Allow-list of extensions a Python runtime actually needs:
#   .py  .pyi  .json  .txt  .yaml  .yml  .toml  .cfg
# Everything else (e.g. "session_manager copy.py" doesn't match because of
# the space; .ipynb/.png/.pyc/.DS_Store/~$* get filtered out by extension or
# the whitespace check below).
function Copy-PythonTreeFiltered {
  param(
    [Parameter(Mandatory=$true)][string]$SrcDir,
    [Parameter(Mandatory=$true)][string]$DstDir,
    [Parameter(Mandatory=$true)][string]$Label
  )

  if (-not (Test-Path $SrcDir)) {
    Log-Warn ("{0} folder not found: {1}" -f $Label, $SrcDir)
    return
  }

  if (Test-Path $DstDir) {
    Remove-Item $DstDir -Recurse -Force -ErrorAction SilentlyContinue
  }
  New-Item -ItemType Directory -Force -Path $DstDir | Out-Null

  $allowedExt = @('.py', '.pyi', '.json', '.txt', '.yaml', '.yml', '.toml', '.cfg')
  $junkDirs   = @('__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache', '.venv', 'node_modules')

  $copied = 0; $skipped = 0
  $skippedSpace = @(); $skippedDir = @(); $skippedExt = @()

  Get-ChildItem -Path $SrcDir -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object {
    $rel = $_.FullName.Substring($SrcDir.Length).TrimStart('\','/')
    $relNorm = $rel -replace '\\','/'

    # Drop anything under junk directories (__pycache__ etc.)
    if ($junkDirs | Where-Object { $relNorm -match "(^|/)$([Regex]::Escape($_))(/|$)" }) {
      $skippedDir += $rel; $skipped++; return
    }

    # Reject whitespace anywhere in the full relative path (NSIS /oname hazard).
    if ($_.Name -match '\s') {
      $skippedSpace += $rel; $skipped++; return
    }

    # Reject OS cruft (~$file, .DS_Store, Thumbs.db).
    if ($_.Name -match '^~\$' -or $_.Name -eq '.DS_Store' -or $_.Name -eq 'Thumbs.db') {
      $skippedSpace += $rel; $skipped++; return
    }

    $ext = $_.Extension.ToLowerInvariant()
    if (-not ($allowedExt -contains $ext)) {
      $skippedExt += $rel; $skipped++; return
    }

    $dst = Join-Path $DstDir $rel
    $dstParent = Split-Path -Parent $dst
    if (-not (Test-Path $dstParent)) { New-Item -ItemType Directory -Force -Path $dstParent | Out-Null }
    Copy-Item -Force $_.FullName $dst
    $copied++
  }

  Log-Ok ("{0} staged: {1} files copied, {2} skipped" -f $Label, $copied, $skipped)
  if ($skippedSpace.Count -gt 0) {
    Log-Warn ("  {0}: rejected {1} file(s) with whitespace / OS-cruft names:" -f $Label, $skippedSpace.Count)
    foreach ($n in $skippedSpace) { Log-Warn ("    - " + $n) }
  }
  if ($skippedDir.Count -gt 0) {
    Log-Info ("  {0}: skipped {1} file(s) under cache/venv dirs" -f $Label, $skippedDir.Count)
  }
  if ($skippedExt.Count -gt 0 -and $skippedExt.Count -le 10) {
    Log-Info ("  {0}: skipped {1} non-runtime extension file(s):" -f $Label, $skippedExt.Count)
    foreach ($n in $skippedExt) { Log-Info ("    - " + $n) }
  } elseif ($skippedExt.Count -gt 10) {
    Log-Info ("  {0}: skipped {1} non-runtime extension file(s)" -f $Label, $skippedExt.Count)
  }
}

Copy-PythonTreeFiltered `
  -SrcDir (Join-Path $root "backend") `
  -DstDir (Join-Path $root "src-tauri\resources\backend") `
  -Label "Backend"

Copy-PythonTreeFiltered `
  -SrcDir (Join-Path $root "modelhub") `
  -DstDir (Join-Path $root "src-tauri\resources\modelhub") `
  -Label "ModelHub"

# Belt-and-suspenders sanity: the two entrypoints must exist after staging.
$mustExistPy = @(
  "src-tauri\resources\backend\entry_main.py",
  "src-tauri\resources\modelhub\tauri.py"
)
foreach ($rel in $mustExistPy) {
  $full = Join-Path $root $rel
  if (-not (Test-Path $full)) {
    throw "Backend/ModelHub staging failed: required file missing -> $full"
  }
}


# ================================
# STEP 6.7: Pack the embedded Python runtime + site-packages into a single zip.
#
# Why: Tauri's NSIS bundler iterates every bundled resource file through a
# handlebars `{{#each resources}}` template. With site-packages holding
# ~20,000+ files (PyTorch, CUDA libs, numpy, opencv), and `cargo tauri build`
# defaulting to debug-level `handlebars::render` logging, the job emits
# hundreds of thousands of log lines and exceeds GitHub Actions' log buffer,
# killing the job with exit code 1 (this is what broke the v0.2.1 release).
#
# By packing the whole runtime tree into ONE zip, Tauri bundles a single file
# instead of 20k, NSIS compiles in seconds, and the installer is smaller
# because the zip compresses the tree once rather than LZMA-ing tens of
# thousands of per-file headers. The Rust app extracts the zip on first launch
# via main.rs::ensure_python_env -> extract_zip_to().
# ================================
Log-Step 6.7 "Packing embedded Python runtime into a single archive"

$pythonDir   = Join-Path $root "src-tauri\resources\python"
# IMPORTANT: keep the zip inside a subdirectory of resources/, NOT at the
# root. Tauri 1.x's `resources/**` glob in tauri.conf.json walks
# subdirectories but does NOT match files that live at the root of the
# resources/ directory. Putting python-runtime.zip directly under
# src-tauri/resources/ silently produced a stub installer (~0.7 MB instead
# of ~600 MB) because NSIS never saw it. Subdirectory it is.
$runtimeDir  = Join-Path $root "src-tauri\resources\runtime"
$runtimeZip  = Join-Path $runtimeDir "python-runtime.zip"
New-Item -ItemType Directory -Force -Path $runtimeDir | Out-Null

if (-not (Test-Path $pythonDir)) {
  Log-Fail "Cannot pack runtime: $pythonDir does not exist. Earlier STEP 2/3 must run first."
  exit 1
}

if (Test-Path $runtimeZip) {
  Remove-Item -Force $runtimeZip -ErrorAction SilentlyContinue
}

try {
  Add-Type -AssemblyName System.IO.Compression.FileSystem
  [System.IO.Compression.ZipFile]::CreateFromDirectory(
    $pythonDir,
    $runtimeZip,
    [System.IO.Compression.CompressionLevel]::Optimal,
    $false
  )
  $zipSizeMB = [math]::Round((Get-Item $runtimeZip).Length / 1MB, 1)
  Log-Ok ("Packed runtime into: {0} ({1} MB)" -f $runtimeZip, $zipSizeMB)
} catch {
  Log-Fail "Failed to pack runtime: $_"
  exit 1
}

# Remove the unpacked python/ tree so Tauri's NSIS bundler only sees the zip.
# (Leaving the tree in would double-bundle it AND re-trigger the handlebars flood.)
try {
  Remove-Item -Recurse -Force $pythonDir -ErrorAction SilentlyContinue
  Log-Ok "Removed unpacked python/ tree (tauri will bundle python-runtime.zip instead)"
} catch {
  Log-Warn "Could not remove $pythonDir ; NSIS bundle may be larger than necessary: $_"
}

# ================================
# STEP 6.9: Preflight - verify required resources before building installer
# (Blocks the broken-installer symptom from issues #26/#37/#42)
# ================================
Log-Step 6.9 "Preflight: verifying bundled resources"

$preflightErrors = @()

$resReq = @(
  @{ Path = "src-tauri\resources\runtime\python-runtime.zip";                        Why = "Packed Python runtime missing (sidecar cannot start)" },
  @{ Path = "src-tauri\resources\backend\entry_main.py";                             Why = "Sidecar entry missing"                      },
  @{ Path = "src-tauri\resources\modelhub\tauri.py";                                 Why = "ModelHub HTTP API missing"                  },
  @{ Path = "src-tauri\resources\versions\0.01\1-collect_data.py";                   Why = "'Script not found' on Start Recording"     },
  @{ Path = "src-tauri\resources\versions\0.01\2-train_model.py";                    Why = "'Script not found' on Train"                },
  @{ Path = "src-tauri\resources\versions\0.01\3-test_model.py";                     Why = "'Script not found' on Start Bot"            }
)

foreach ($r in $resReq) {
  $full = Join-Path $root $r.Path
  if (Test-Path $full) {
    Log-Ok ("OK: " + $r.Path)
  } else {
    Log-Fail ("MISSING: " + $r.Path + " -> " + $r.Why)
    $preflightErrors += $r.Path
  }
}

# Sanity-check the runtime zip is a reasonable size (a truly empty runtime
# would be <1 MB; real runtime is hundreds of MB).
$runtimeZipPath = Join-Path $root "src-tauri\resources\runtime\python-runtime.zip"
if (Test-Path $runtimeZipPath) {
  $zipMB = (Get-Item $runtimeZipPath).Length / 1MB
  if ($zipMB -lt 10) {
    Log-Fail ("python-runtime.zip suspiciously small: {0:N1} MB (would cause 'No module named uvicorn')" -f $zipMB)
    $preflightErrors += "python-runtime.zip (too small)"
  } else {
    Log-Ok ("python-runtime.zip size: {0:N1} MB" -f $zipMB)
  }
}

# ----------------------------------------------------------------
# Hardening: catch the failure modes that broke previous releases
# BEFORE we spend ~5 minutes compiling Rust + linking the bundler.
# ----------------------------------------------------------------

# (a) NSIS template quoting. When `/oname=...` is unquoted, a single resource
# filename with a space explodes makensis on line 254 with
# "Usage: File ..." and `os error 2`. We check the template we ship, and the
# copy tauri bundler will render, both require the quoted form.
$nsisTemplate = Join-Path $root "installer\nsis_template.nsi"
if (Test-Path $nsisTemplate) {
  $tmpl = Get-Content -Raw $nsisTemplate
  # Bad pattern: `File /a /oname=<handlebars>` without surrounding quotes.
  if ($tmpl -match 'File\s+/a\s+/oname=\{\{') {
    Log-Fail ("NSIS template has UNQUOTED /oname= (file names with spaces will break makensis). " +
              "Required form: File /a ""/oname={{this.[1]}}"" ""{{@key}}""")
    $preflightErrors += "installer/nsis_template.nsi (unquoted /oname=)"
  } else {
    Log-Ok "NSIS template /oname= is correctly quoted"
  }
}

# (b) Any staged bundle resource whose filename contains whitespace will break
# the unquoted-oname path even if we fixed the template (belt + braces --
# some NSIS versions also choke on whitespace even when quoted due to
# downstream File /r expansions). Scan everything tauri will bundle.
$stagedRoots = @(
  (Join-Path $root "src-tauri\resources"),
  (Join-Path $root "src-tauri\drivers")
)
$badSpaceFiles = @()
foreach ($sr in $stagedRoots) {
  if (-not (Test-Path $sr)) { continue }
  Get-ChildItem -Path $sr -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object {
    if ($_.Name -match '\s') { $badSpaceFiles += $_.FullName }
  }
}
if ($badSpaceFiles.Count -gt 0) {
  Log-Fail ("Found {0} bundle file(s) with spaces in the name. Rename them in-repo or exclude from staging:" -f $badSpaceFiles.Count)
  foreach ($f in $badSpaceFiles) { Log-Fail ("  - " + $f) }
  $preflightErrors += "bundle contains filename(s) with whitespace"
}

if ($preflightErrors.Count -gt 0) {
  Log-Fail ("Preflight failed with {0} issue(s). Aborting to prevent shipping a broken installer." -f $preflightErrors.Count)
  Log-Info "Re-run earlier steps (wheelhouse, Python bundling, site-packages install, Step 6.5/6.6/6.7)."
  exit 1
}

Log-Ok "Preflight passed - all required resources present"

# ================================
# STEP 7: Build Tauri
# ================================
if (-not $SkipTauri) {
  Log-Step 7 "Building Tauri Application"

  # Clean any previous installer .exe files in the bundle dir before running
  # cargo tauri build. Otherwise running this script twice (e.g. once at
  # 1.0.0 and once at 0.2.2) leaves both versions on disk and the verify
  # step can't tell which one is the new build. This is also why the user
  # saw both BOT-MMORPG-AI_0.1.5_x64-setup.exe AND _1.0.0_ listed in the
  # bundle dir after a single make artifact run.
  $installerDir = Join-Path $root "src-tauri\target\release\bundle\nsis"
  if (Test-Path $installerDir) {
    Get-ChildItem -Path $installerDir -Filter "*.exe" -ErrorAction SilentlyContinue |
      ForEach-Object {
        Log-Info ("Removing previous installer: " + $_.Name)
        Remove-Item -Force $_.FullName -ErrorAction SilentlyContinue
      }
  }

  Push-Location (Join-Path $root "src-tauri")
  try {
    # CRITICAL: do NOT pass --verbose here and explicitly pin RUST_LOG to
    # "info". `cargo tauri build --verbose` enables debug-level logging for
    # the `handlebars` crate that tauri-bundler uses to render the NSIS
    # template. With ~20k resource files the {{#each resources}} block emits
    # ~60k "Debug [handlebars::render]" lines, overflows GitHub Actions' log
    # buffer, and the job dies with exit 1. (That is what broke the v0.2.1
    # release -- build_windows-installer.yml succeeded because it doesn't run
    # this pipeline; release-windows-installer.yml failed because it does.)
    $prevRustLog = $env:RUST_LOG
    $env:RUST_LOG = "info,handlebars=warn,tauri_bundler=info"

    # Build the cargo tauri argument list. When -Version is provided, override
    # tauri.conf.json's package.version so the installer filename and the
    # baked-in app version both match the release tag (otherwise tauri uses
    # the static "1.0.0" from tauri.conf.json and ships
    # BOT-MMORPG-AI_1.0.0_x64-setup.exe regardless of the tag).
    $tauriArgs = @('tauri', 'build')
    $tmpCfgFile = $null
    if ($Version -ne "") {
      # tauri 1.x's --config accepts EITHER inline JSON OR a path to a JSON
      # file. We use a temp file: passing inline JSON via PowerShell 5.1
      # native-command argument splatting is unreliable -- PS sometimes
      # strips the inner double-quotes before they reach `cargo.exe`,
      # producing
      #     "Error failed to parse config to merge: key must be a string"
      # when tauri sees `{ package: { version: ... } }` (unquoted keys).
      # A temp-file path side-steps PS's quote handling completely.
      # Strict SemVer 2.0.0 regex. Critically, this rejects numeric pre-release
      # identifiers with leading zeroes (e.g. '0378990'), which Tauri's parser
      # also rejects with "Error `package > version` must be a semver string".
      $semverRe = '^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(-((0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*)(\.(0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*))*))?(\+[0-9A-Za-z-]+(\.[0-9A-Za-z-]+)*)?$'
      if ($Version -notmatch $semverRe) {
        throw "Invalid -Version '$Version' (must be semver like 0.2.2 or 0.2.2-nightly.gabc1234; numeric identifiers must not have leading zeroes)"
      }
      $tmpCfgFile = Join-Path $env:TEMP ("tauri-cfg-override-{0}.json" -f ([guid]::NewGuid().ToString("N")))
      # ConvertTo-Json on a hashtable produces canonical, well-quoted JSON.
      # Encoded as ASCII to avoid any BOM that might trip a strict parser.
      @{ package = @{ version = $Version } } |
        ConvertTo-Json -Depth 4 -Compress |
        Set-Content -Path $tmpCfgFile -Encoding ASCII
      $tauriArgs += '--config'
      $tauriArgs += $tmpCfgFile
      Log-Info ("Overriding tauri package.version -> {0} (via {1})" -f $Version, $tmpCfgFile)
    } else {
      Log-Info "No -Version override; using tauri.conf.json default."
    }

    Log-Info "Running cargo tauri build (RUST_LOG=$($env:RUST_LOG))..."
    & cargo @tauriArgs
    $tauriExit = $LASTEXITCODE

    # Restore previous RUST_LOG so subsequent steps aren't affected.
    if ($null -eq $prevRustLog) {
      Remove-Item Env:\RUST_LOG -ErrorAction SilentlyContinue
    } else {
      $env:RUST_LOG = $prevRustLog
    }

    if ($tauriExit -ne 0) { throw "Tauri build failed with exit code $tauriExit" }
    Log-Ok "Tauri build completed successfully"
  } catch {
    Log-Fail "Tauri build failed: $_"
    Pop-Location
    if ($null -ne $tmpCfgFile -and (Test-Path $tmpCfgFile)) {
      Remove-Item -Force $tmpCfgFile -ErrorAction SilentlyContinue
    }
    exit 1
  } finally {
    Pop-Location
    if ($null -ne $tmpCfgFile -and (Test-Path $tmpCfgFile)) {
      Remove-Item -Force $tmpCfgFile -ErrorAction SilentlyContinue
    }
  }

  if (Test-Path $installerDir) {
    $installers = @(Get-ChildItem -Path $installerDir -Filter "*.exe" -ErrorAction SilentlyContinue)
    if ($installers.Count -eq 0) {
      Log-Fail "No installer executables produced in $installerDir"
      exit 1
    }
    if ($installers.Count -gt 1) {
      Log-Fail ("Expected exactly one installer in {0}, found {1}:" -f $installerDir, $installers.Count)
      foreach ($i in $installers) { Log-Fail ("  - " + $i.Name) }
      exit 1
    }

    $installer = $installers[0]
    $sizeMB    = [math]::Round(($installer.Length / 1MB), 2)
    Log-Ok ("NSIS installer created: {0} ({1} MB)" -f $installer.Name, $sizeMB)

    # Filename must contain the version we asked tauri to bake in. Catches
    # the case where -Version was empty / didn't flow through.
    if ($Version -ne "" -and ($installer.Name -notmatch [Regex]::Escape($Version))) {
      Log-Fail ("Installer filename '{0}' does not contain the expected version '{1}'." -f $installer.Name, $Version)
      Log-Fail "The -Version override did not reach `cargo tauri build`. Check the Makefile / CI plumbing."
      exit 1
    }

    # Sanity size check. A real installer (with embedded Python + ML deps)
    # is hundreds of MB. Anything under 50 MB means the resources didn't
    # actually get bundled (the Tauri-glob bug we just fixed produced
    # ~0.7 MB stubs). Hard-fail rather than silently shipping a broken exe.
    if ($sizeMB -lt 50) {
      Log-Fail ("Installer is suspiciously small ({0} MB). Expected >= 50 MB once the python-runtime.zip is bundled." -f $sizeMB)
      Log-Fail "Likely cause: tauri's resources/** glob is not picking up python-runtime.zip. Confirm the zip is under src-tauri\resources\runtime\, not at the resources root."
      exit 1
    }
  } else {
    Log-Fail "Installer directory not found: $installerDir"
    exit 1
  }
} else {
  Log-Warn "Skipping Tauri build"
}

# ================================
# STEP 8: Verify (optional)
# ================================
if ($Verify) {
  Log-Step 8 "Running Verification"

  $verifyScript = Join-Path $root "scripts\verify_installer.ps1"
  if (Test-Path $verifyScript) {
    & $verifyScript
    if ($LASTEXITCODE -ne 0) {
      Log-Fail "Verification failed"
      exit 1
    }
    Log-Ok "Verification completed"
  } else {
    Log-Warn "Verification script not found: $verifyScript"
  }
}

Write-Host ""
Write-Host "======================================"
Write-Host " BUILD COMPLETED"
Write-Host "======================================"
Log-Ok ("Build finished at: {0}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"))
Write-Host ""
Log-Info "Installer location: src-tauri\target\release\bundle\nsis\"
Write-Host ""
Log-Info "Next steps:"
Write-Host "  1. Run tests:   .\scripts\test_installer.ps1"
Write-Host "  2. Verify:      .\scripts\verify_installer.ps1"
Write-Host "  3. Test install on a clean Windows machine"
Write-Host ""