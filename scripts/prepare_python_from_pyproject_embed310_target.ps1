<#
prepare_python_from_pyproject_embed310_target.ps1

Production-ready wheelhouse + portable site-packages builder for Windows embeddable Python.
UPDATED: Uses 'pip wheel' exclusively to ensure all dependencies (binary or source) are captured.

Workflow:
 1. Setup Embedded Python & Pip.
 2. Build local project wheel -> Store in Wheelhouse.
 3. POPULATE WHEELHOUSE (Use 'pip wheel' to resolve everything).
 4. NUCLEAR INSTALL (Force install every wheel found).
 5. Verify.

Usage:
  powershell -NoProfile -ExecutionPolicy Bypass -File scripts\prepare_python_from_pyproject_embed310_target.ps1 `
    -Extras @("backend","launcher","ml") `
    -TargetTag "win_amd64_cp310" `
    -RebuildTarget
#>

param(
    [string[]]$Extras = @("backend","launcher","ml"),
    [string]$TargetTag = "win_amd64_cp310",
    [switch]$RebuildTarget,
    [switch]$NoInternetBootstrap
)

$ErrorActionPreference = "Stop"

# Prevent user-site installs to keep the embedded environment isolated
$env:PIP_USER        = "no"
$env:PIP_NO_USER_CFG = "1"
$env:PYTHONUSERBASE  = ""
$env:PYTHONDONTWRITEBYTECODE = "1"

function Info($m) { Write-Host "[INFO] $m" -ForegroundColor Cyan }
function Ok($m)   { Write-Host "[OK]   $m" -ForegroundColor Green }
function Warn($m) { Write-Host "[WARN] $m" -ForegroundColor Yellow }
function Fail($m) { Write-Host "[FAIL] $m" -ForegroundColor Red; exit 1 }

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = (Resolve-Path (Join-Path $scriptDir "..")).Path

$pyproject = Join-Path $root "pyproject.toml"
if (-not (Test-Path $pyproject)) { Fail "pyproject.toml not found at: $pyproject" }

# -------------------------
# 1. Embedded Python fetch
# -------------------------
function Ensure-EmbeddedPython310Downloaded {
    param([string]$Root)
    $ver = "3.10.11"; $arch = "amd64"
    $zipName = "python-$ver-embed-$arch.zip"
    $url = "https://www.python.org/ftp/python/$ver/$zipName"
    $dst = Join-Path $Root "third_party\python\python-$ver-embed-$arch"
    
    if (-not (Test-Path $dst)) { New-Item -ItemType Directory -Force -Path $dst | Out-Null }
    
    $pyExe = Join-Path $dst "python.exe"
    if (Test-Path $pyExe) { return $dst }
    
    $zipPath = Join-Path $dst $zipName
    Info "Embeddable Python not found. Downloading from official source: $url"
    try {
        Invoke-WebRequest -Uri $url -OutFile $zipPath -UseBasicParsing
        Expand-Archive -Path $zipPath -DestinationPath $dst -Force
        Remove-Item -Force $zipPath -ErrorAction SilentlyContinue
        return $dst
    } catch {
        Fail ("Auto-download of Python failed. Verify internet connection.`nError=" + $_.Exception.Message)
    }
}

$pyRuntimeDir = Join-Path $root "third_party\python\python-3.10.11-embed-amd64"
$pyExe = Join-Path $pyRuntimeDir "python.exe"

if (-not (Test-Path $pyExe)) {
    $pyRuntimeDir = Ensure-EmbeddedPython310Downloaded -Root $root
    $pyExe = Join-Path $pyRuntimeDir "python.exe"
}

# -------------------------
# 2. Patching python*._pth
# -------------------------
function Patch-EmbeddedPythonPth {
    param([string]$PyDir, [string]$TargetTag)
    $pth = Get-ChildItem -Path $PyDir -Filter "python*._pth" | Select-Object -First 1
    if (-not $pth) { Warn "No ._pth file found to patch."; return }

    $relTarget = "..\portable_site_packages\$TargetTag"
    $lines = Get-Content -Path $pth.FullName
    
    $newLines = @()
    if (-not ($lines | Where-Object { $_.Trim() -eq "." })) { $newLines += "." }
    if (-not ($lines | Where-Object { $_.Trim() -eq $relTarget })) { $newLines += $relTarget }
    
    foreach ($line in $lines) {
        if ($line.Trim() -eq "#import site" -or $line.Trim() -eq "import site") { continue }
        if ($line.Trim() -eq ".") { continue }
        $newLines += $line
    }
    $newLines += "import site"

    Set-Content -Path $pth.FullName -Value $newLines -Encoding ASCII
    Ok "Patched $($pth.Name) to include portable site-packages and enable site module."
}

Patch-EmbeddedPythonPth -PyDir $pyRuntimeDir -TargetTag $TargetTag

# -------------------------
# 3. Bootstrapping PIP
# -------------------------
Info "Checking for pip in embedded runtime..."
$hasPip = $false
try {
    & $pyExe -m pip --version 2>$null
    if ($LASTEXITCODE -eq 0) { $hasPip = $true }
} catch {}

if (-not $hasPip) {
    Warn "ensurepip missing. Bootstrapping via get-pip.py..."
    $getPipPath = Join-Path $pyRuntimeDir "get-pip.py"
    try {
        Invoke-WebRequest -Uri "https://bootstrap.pypa.io/get-pip.py" -OutFile $getPipPath -UseBasicParsing
        & $pyExe $getPipPath --no-warn-script-location
        Remove-Item -Force $getPipPath -ErrorAction SilentlyContinue
        Ok "pip successfully bootstrapped."
    } catch {
        Fail "Failed to bootstrap pip. Error: $($_.Exception.Message)"
    }
} else {
    Ok "pip is already present."
}

Info "Upgrading build tools (including hatchling build backend)..."
& $pyExe -m pip install --upgrade pip setuptools wheel hatchling --quiet

# -------------------------
# 4. Preparing Directories
# -------------------------
$wheelRoot = Join-Path $root ("third_party\wheelhouse\" + $TargetTag)
$wheelDir  = Join-Path $wheelRoot "wheels"
$targetRoot = Join-Path $root "third_party\python\portable_site_packages"
$targetDir  = Join-Path $targetRoot $TargetTag

if ($RebuildTarget -and (Test-Path $targetDir)) {
    Info "Cleaning old target directory: $targetDir"
    Remove-Item -Recurse -Force $targetDir
}

# When -RebuildTarget is requested, also clean the wheelhouse itself. Without
# this, `pip wheel` accumulates multiple versions of the same package across
# runs (e.g. anyio-4.12.1 AND anyio-4.13.0), and the subsequent `pip install -r
# install_manifest.txt` refuses to install both with a ResolutionImpossible
# error. A full rebuild has to mean a full rebuild.
if ($RebuildTarget -and (Test-Path $wheelDir)) {
    Info "Cleaning old wheelhouse: $wheelDir"
    Remove-Item -Recurse -Force $wheelDir
}

New-Item -ItemType Directory -Force -Path $targetDir | Out-Null
New-Item -ItemType Directory -Force -Path $wheelDir  | Out-Null

# -------------------------
# 5. Build Project Wheel
# -------------------------
$extrasStr = ""
if ($Extras -and $Extras.Count -gt 0) { $extrasStr = "[" + ($Extras -join ",") + "]" }
$spec = ".${extrasStr}"

Push-Location $root
try {
    $tmpDir = Join-Path $env:TEMP ("bot-build-" + [guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Force -Path $tmpDir | Out-Null
    
    Info "Building local project wheel for $spec..."
    & $pyExe -m pip wheel --no-deps --wheel-dir $tmpDir $spec
    
    $projWheel = Get-ChildItem -Path $tmpDir -Filter "*.whl" | Select-Object -First 1
    if (-not $projWheel) { Fail "Failed to build the project wheel." }

    Copy-Item -Force $projWheel.FullName (Join-Path $wheelDir $projWheel.Name)
    Ok "Project wheel saved to Wheelhouse: $($projWheel.Name)"

    Remove-Item -Recurse -Force $tmpDir
} finally {
    Pop-Location
}

# -------------------------
# 6. POPULATE WHEELHOUSE (Robust Method)
# -------------------------
Info "Populating wheelhouse for $spec (Offline ready)..."

# Use 'pip wheel' instead of 'pip download'.
# 'pip wheel' is smarter: it downloads binaries if they exist, OR builds from source if needed.
# It ensures we end up with a .whl for EVERY dependency.
Warn "Resolving and building all dependencies into wheels..."
& $pyExe -m pip wheel --wheel-dir $wheelDir --find-links $wheelDir $spec
if ($LASTEXITCODE -ne 0) {
    Fail "Failed to resolve/build wheels for $spec."
}

# Clean up any leftover source files (we only want wheels)
Get-ChildItem -Path $wheelDir -Include *.tar.gz, *.zip -Recurse | Remove-Item -Force

# -------------------------
# 6a. DEDUPLICATE WHEELS
# -------------------------
# `pip wheel` only adds wheels; it never removes old ones. If a dependency's
# version was bumped since a previous run, both the old and the new wheel live
# side by side, and Step 7's `pip install -r install_manifest.txt` will fail
# with ResolutionImpossible ("Cannot install anyio 4.12.1 and anyio 4.13.0").
# Group wheels by canonical package name, keep the highest version only, and
# delete the rest. This makes repeat builds self-healing.
Info "Deduplicating wheelhouse (keep latest version per package)..."
$wheelFiles = Get-ChildItem -Path $wheelDir -Filter "*.whl" -File
$groups = @{}
foreach ($w in $wheelFiles) {
    # PEP 427: <distribution>-<version>[-<build>]-<python>-<abi>-<platform>.whl
    # Use the first two '-' separated chunks as (name, version). Lowercase name
    # and normalize dashes->underscores for robust grouping.
    $parts = $w.BaseName -split '-'
    if ($parts.Length -lt 2) { continue }
    $name = $parts[0].ToLowerInvariant().Replace('_', '-')
    $ver  = $parts[1]
    if (-not $groups.ContainsKey($name)) { $groups[$name] = @() }
    $groups[$name] += [pscustomobject]@{ File = $w; Version = $ver }
}

$removed = 0
foreach ($name in $groups.Keys) {
    $entries = $groups[$name]
    if ($entries.Count -le 1) { continue }
    # Sort by version using System.Version when possible, fall back to string.
    $sorted = $entries | Sort-Object -Property @{
        Expression = {
            try {
                # Strip pre-release/post/dev suffixes to keep System.Version happy.
                $v = ($_.Version -replace '[^0-9\.].*$', '').TrimEnd('.')
                if ([string]::IsNullOrWhiteSpace($v)) { [System.Version]"0.0" }
                else { [System.Version]$v }
            } catch { [System.Version]"0.0" }
        }
        Descending = $true
    }, @{ Expression = "Version"; Descending = $true }
    $keep = $sorted[0]
    foreach ($e in $sorted[1..($sorted.Count - 1)]) {
        Warn ("Removing old wheel (keeping {0} {1}): {2}" -f $name, $keep.Version, $e.File.Name)
        Remove-Item -Force $e.File.FullName
        $removed++
    }
}
if ($removed -gt 0) {
    Ok ("Deduplicated wheelhouse: removed {0} older wheel(s)." -f $removed)
} else {
    Info "Wheelhouse already had a single version per package (no duplicates)."
}

$totalWheels = (Get-ChildItem -Path $wheelDir -Filter "*.whl").Count
Ok "Wheelhouse populated with $totalWheels wheels."

# Validation: Check if critical wheels are actually there
if (-not (Test-Path (Join-Path $wheelDir "mss*.whl"))) {
    Fail "Critical dependency 'mss' is missing from the wheelhouse! Check pyproject.toml."
}
if (-not (Test-Path (Join-Path $wheelDir "numpy*.whl"))) {
    Fail "Critical dependency 'numpy' is missing from the wheelhouse!"
}

# -------------------------
# 7. NUCLEAR INSTALL (Force All Wheels)
# -------------------------
Info "Step 7: Explicitly installing ALL wheels from Wheelhouse..."

# Get list of all wheels
$allWheels = Get-ChildItem -Path $wheelDir -Filter "*.whl" | Select-Object -ExpandProperty FullName

# Write file list to a requirements file to avoid command-line length limits
$reqFile = Join-Path $wheelDir "install_manifest.txt"
$allWheels | Out-File -FilePath $reqFile -Encoding ASCII

try {
    # --force-reinstall: overwrites anything broken
    # --no-deps: we are giving it ALL deps explicitly in the list, so don't try to resolve online
    & $pyExe -m pip install `
        --no-index `
        --target $targetDir `
        --force-reinstall `
        --ignore-installed `
        --no-deps `
        -r $reqFile

    if ($LASTEXITCODE -ne 0) {
        Fail "Nuclear install failed."
    }
} finally {
    Remove-Item -Force $reqFile -ErrorAction SilentlyContinue
}

Ok "Installation complete (All modules forced)."

# -------------------------
# 8. Final Sanity Check
# -------------------------
Info "Verifying environment..."
& $pyExe -c "import numpy; import mss; import cv2; import eel; import torch; print('SUCCESS: Portable environment is operational.')"
if ($LASTEXITCODE -ne 0) { Fail "Environment verification failed. Missing 'mss' or other modules." }

Ok "========================================================="
Ok " PREPARE SCRIPT COMPLETED SUCCESSFULLY"
Ok "========================================================="