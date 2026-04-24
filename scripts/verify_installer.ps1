<#
.SYNOPSIS
    Verifies that the installer was built correctly with all required components.

.DESCRIPTION
    This script checks:
    - Backend sidecar binary exists and is valid
    - Driver installers are present
    - Tauri application was built
    - NSIS installer was created
    - All files have reasonable sizes

.EXAMPLE
    .\scripts\verify_installer.ps1
#>

$ErrorActionPreference = "Stop"

function Write-Success($msg) {
    Write-Host "✓ $msg" -ForegroundColor Green
}

function Write-Failure($msg) {
    Write-Host "✗ $msg" -ForegroundColor Red
}

function Write-Info($msg) {
    Write-Host "ℹ $msg" -ForegroundColor Cyan
}

$root = Resolve-Path "$(Split-Path -Parent $MyInvocation.MyCommand.Path)\.." | % Path
$errors = @()

Write-Info "Starting installer verification..."
Write-Info "Root directory: $root"
Write-Host ""

# Check 1: Backend sidecar binary
Write-Info "Checking backend sidecar binary..."
$target = "x86_64-pc-windows-msvc"
$sidecarPath = Join-Path $root "src-tauri\binaries\main-backend-$target.exe"

if (Test-Path $sidecarPath) {
    $size = (Get-Item $sidecarPath).Length / 1MB
    if ($size -gt 1) {
        Write-Success "Backend sidecar exists: $([math]::Round($size, 2)) MB"
    } else {
        Write-Failure "Backend sidecar is too small: $([math]::Round($size, 2)) MB"
        $errors += "Backend sidecar file size is suspiciously small"
    }
} else {
    Write-Failure "Backend sidecar not found: $sidecarPath"
    $errors += "Missing backend sidecar binary"
}

# Check 2: Driver installers
Write-Info "Checking driver installers..."

$interceptionPath = Join-Path $root "src-tauri\drivers\interception\install-interception.exe"
if (Test-Path $interceptionPath) {
    $size = (Get-Item $interceptionPath).Length / 1KB
    Write-Success "Interception installer exists: $([math]::Round($size, 2)) KB"
} else {
    Write-Failure "Interception installer not found: $interceptionPath"
    $errors += "Missing Interception driver installer"
}

$vjoyPath = Join-Path $root "src-tauri\drivers\vjoy\vJoySetup.exe"
if (Test-Path $vjoyPath) {
    $size = (Get-Item $vjoyPath).Length / 1KB
    Write-Success "vJoy installer exists: $([math]::Round($size, 2)) KB"
} else {
    Write-Failure "vJoy installer not found: $vjoyPath"
    $errors += "Missing vJoy driver installer"
}

# Check 3: PowerShell install scripts
Write-Info "Checking install scripts..."

$installScriptPath = Join-Path $root "src-tauri\resources\scripts\install_drivers.ps1"
if (Test-Path $installScriptPath) {
    Write-Success "Install drivers script exists"
} else {
    Write-Failure "Install drivers script not found: $installScriptPath"
    $errors += "Missing install_drivers.ps1 script"
}

$modelsScriptPath = Join-Path $root "src-tauri\resources\scripts\download_models.ps1"
if (Test-Path $modelsScriptPath) {
    Write-Success "Download models script exists"
} else {
    Write-Failure "Download models script not found: $modelsScriptPath"
    $errors += "Missing download_models.ps1 script"
}

# Check 4: Tauri application binary
Write-Info "Checking Tauri application binary..."

$tauriExePath = Join-Path $root "src-tauri\target\release\bot-mmorpg-ai.exe"
if (Test-Path $tauriExePath) {
    $size = (Get-Item $tauriExePath).Length / 1MB
    Write-Success "Tauri application exists: $([math]::Round($size, 2)) MB"
} else {
    Write-Failure "Tauri application not found: $tauriExePath"
    $errors += "Missing Tauri application binary"
}

# Check 5: NSIS installer
Write-Info "Checking NSIS installer..."

$installerDir = Join-Path $root "src-tauri\target\release\bundle\nsis"
if (Test-Path $installerDir) {
    $installers = Get-ChildItem -Path $installerDir -Filter "*.exe"

    if ($installers.Count -gt 0) {
        foreach ($installer in $installers) {
            $size = $installer.Length / 1MB
            Write-Success "NSIS installer: $($installer.Name) ($([math]::Round($size, 2)) MB)"

            # Check if it's a valid PE executable
            $header = Get-Content -Path $installer.FullName -Encoding Byte -TotalCount 2
            if ($header[0] -eq 0x4D -and $header[1] -eq 0x5A) {
                Write-Success "Valid PE executable header"
            } else {
                Write-Failure "Invalid executable header for $($installer.Name)"
                $errors += "Invalid installer executable format"
            }
        }
    } else {
        Write-Failure "No installer executables found in $installerDir"
        $errors += "No NSIS installer generated"
    }
} else {
    Write-Failure "Installer directory not found: $installerDir"
    $errors += "NSIS installer directory does not exist"
}

# Check 6: UI files
Write-Info "Checking UI files..."

$uiIndexPath = Join-Path $root "tauri-ui\index.html"
if (Test-Path $uiIndexPath) {
    Write-Success "UI index.html exists"
} else {
    Write-Failure "UI index.html not found: $uiIndexPath"
    $errors += "Missing UI index.html"
}

$uiJsPath = Join-Path $root "tauri-ui\main.js"
if (Test-Path $uiJsPath) {
    Write-Success "UI main.js exists"
} else {
    Write-Failure "UI main.js not found: $uiJsPath"
    $errors += "Missing UI main.js"
}

# Check 7: Bundled runtime (root cause of issues #26/#37/#42)
# The Tauri app expects these under src-tauri/resources/ so NSIS includes them.
# If any is missing, the installed app will print "Sidecar API not ready" and
# "Script not found" — the very bugs users are hitting.
Write-Info "Checking bundled runtime (python + backend + modelhub + versions)..."

$bundledPython = Join-Path $root "src-tauri\resources\python\python.exe"
if (Test-Path $bundledPython) {
    Write-Success "Bundled Python runtime exists: resources/python/python.exe"
} else {
    Write-Failure "Bundled Python runtime missing: $bundledPython"
    $errors += "resources/python/python.exe missing (sidecar cannot start)"
}

$bundledSitePkgs = Join-Path $root "src-tauri\resources\python\site-packages"
if (Test-Path $bundledSitePkgs) {
    $countFiles = (Get-ChildItem -Path $bundledSitePkgs -Recurse -File -ErrorAction SilentlyContinue | Measure-Object).Count
    if ($countFiles -gt 100) {
        Write-Success "Bundled site-packages populated: $countFiles files"
    } else {
        Write-Failure "Bundled site-packages too small: only $countFiles files"
        $errors += "resources/python/site-packages is empty or incomplete"
    }
} else {
    Write-Failure "Bundled site-packages missing: $bundledSitePkgs"
    $errors += "resources/python/site-packages missing (No module named uvicorn/numpy/torch)"
}

$bundledBackend = Join-Path $root "src-tauri\resources\backend\entry_main.py"
if (Test-Path $bundledBackend) {
    Write-Success "Bundled backend entry exists: resources/backend/entry_main.py"
} else {
    Write-Failure "Bundled backend missing: $bundledBackend"
    $errors += "resources/backend/entry_main.py missing (sidecar cannot start)"
}

$bundledModelhub = Join-Path $root "src-tauri\resources\modelhub\tauri.py"
if (Test-Path $bundledModelhub) {
    Write-Success "Bundled modelhub exists: resources/modelhub/tauri.py"
} else {
    Write-Failure "Bundled modelhub missing: $bundledModelhub"
    $errors += "resources/modelhub/tauri.py missing (HTTP API cannot serve)"
}

$bundledVersions = Join-Path $root "src-tauri\resources\versions\0.01\1-collect_data.py"
if (Test-Path $bundledVersions) {
    Write-Success "Bundled collect_data script exists: resources/versions/0.01/1-collect_data.py"
} else {
    Write-Failure "Bundled collect_data script missing: $bundledVersions"
    $errors += "resources/versions/0.01/1-collect_data.py missing (recording will fail with 'Script not found')"
}

$bundledTrain = Join-Path $root "src-tauri\resources\versions\0.01\2-train_model.py"
if (Test-Path $bundledTrain) {
    Write-Success "Bundled train script exists: resources/versions/0.01/2-train_model.py"
} else {
    Write-Failure "Bundled train script missing: $bundledTrain"
    $errors += "resources/versions/0.01/2-train_model.py missing (training will fail)"
}

# Summary
Write-Host ""
Write-Host "======================================"
Write-Host " VERIFICATION SUMMARY"
Write-Host "======================================"

if ($errors.Count -eq 0) {
    Write-Success "All checks passed! Installer is ready."
    Write-Host ""
    Write-Info "Installer location: $installerDir"
    exit 0
} else {
    Write-Failure "Verification failed with $($errors.Count) error(s):"
    Write-Host ""
    foreach ($error in $errors) {
        Write-Host "  • $error" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Info "Please run the build pipeline again: .\scripts\build_pipeline.ps1"
    exit 1
}
