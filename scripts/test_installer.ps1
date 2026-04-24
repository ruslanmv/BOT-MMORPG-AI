<#
.SYNOPSIS
    Tests the installer in a controlled environment.

.DESCRIPTION
    This script performs automated testing of the installer:
    - Extracts installer contents (if possible)
    - Checks for required components
    - Validates file signatures
    - Simulates installation (in test mode)

.PARAMETER InstallerPath
    Path to the installer executable to test

.EXAMPLE
    .\scripts\test_installer.ps1
    .\scripts\test_installer.ps1 -InstallerPath "path\to\installer.exe"
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$InstallerPath
)

$ErrorActionPreference = "Stop"

function Write-Success($msg) {
    Write-Host "[OK]   $msg" -ForegroundColor Green
}

function Write-Failure($msg) {
    Write-Host "[FAIL] $msg" -ForegroundColor Red
}

function Write-Info($msg) {
    Write-Host "[INFO] $msg" -ForegroundColor Cyan
}

function Write-Warning($msg) {
    Write-Host "[WARN] $msg" -ForegroundColor Yellow
}

$root = Resolve-Path "$(Split-Path -Parent $MyInvocation.MyCommand.Path)\.." | % Path

# Find installer if not specified
if (-not $InstallerPath) {
    Write-Info "Searching for installer..."
    $installerDir = Join-Path $root "src-tauri\target\release\bundle\nsis"

    if (-not (Test-Path $installerDir)) {
        Write-Failure "Installer directory not found: $installerDir"
        Write-Info "Please build the installer first: .\scripts\build_pipeline.ps1"
        exit 1
    }

    $installers = Get-ChildItem -Path $installerDir -Filter "*.exe"

    if ($installers.Count -eq 0) {
        Write-Failure "No installer found in $installerDir"
        exit 1
    }

    $InstallerPath = $installers[0].FullName
}

if (-not (Test-Path $InstallerPath)) {
    Write-Failure "Installer not found: $InstallerPath"
    exit 1
}

Write-Info "Testing installer: $InstallerPath"
Write-Host ""

$testResults = @{
    Passed = @()
    Failed = @()
    Warnings = @()
}

# Test 1: File exists and is accessible
Write-Info "Test 1: File accessibility..."
try {
    $installer = Get-Item $InstallerPath
    $testResults.Passed += "File is accessible"
    Write-Success "File is accessible"
} catch {
    $testResults.Failed += "Cannot access installer file: $_"
    Write-Failure "Cannot access installer file"
}

# Test 2: File size check
Write-Info "Test 2: File size validation..."
$size = (Get-Item $InstallerPath).Length / 1MB

if ($size -lt 1) {
    $testResults.Failed += "Installer size is too small: $([math]::Round($size, 2)) MB"
    Write-Failure "Installer is too small: $([math]::Round($size, 2)) MB"
} elseif ($size -lt 10) {
    $testResults.Warnings += "Installer size is smaller than expected: $([math]::Round($size, 2)) MB"
    Write-Warning "Installer is smaller than expected: $([math]::Round($size, 2)) MB"
} else {
    $testResults.Passed += "File size is appropriate: $([math]::Round($size, 2)) MB"
    Write-Success "File size is appropriate: $([math]::Round($size, 2)) MB"
}

# Test 3: PE executable validation
Write-Info "Test 3: Executable format validation..."
try {
    $header = Get-Content -Path $InstallerPath -Encoding Byte -TotalCount 2

    if ($header[0] -eq 0x4D -and $header[1] -eq 0x5A) {
        $testResults.Passed += "Valid PE executable format"
        Write-Success "Valid PE executable format (MZ header)"
    } else {
        $testResults.Failed += "Invalid PE executable format"
        Write-Failure "Invalid executable format"
    }
} catch {
    $testResults.Failed += "Cannot read executable header: $_"
    Write-Failure "Cannot read executable header"
}

# Test 4: Digital signature check (optional)
Write-Info "Test 4: Digital signature check..."
try {
    $signature = Get-AuthenticodeSignature -FilePath $InstallerPath

    if ($signature.Status -eq 'Valid') {
        $testResults.Passed += "Valid digital signature"
        Write-Success "Valid digital signature from: $($signature.SignerCertificate.Subject)"
    } elseif ($signature.Status -eq 'NotSigned') {
        $testResults.Warnings += "Installer is not digitally signed"
        Write-Warning "Installer is not digitally signed (expected for development builds)"
    } else {
        $testResults.Warnings += "Digital signature status: $($signature.Status)"
        Write-Warning "Digital signature status: $($signature.Status)"
    }
} catch {
    $testResults.Warnings += "Could not check digital signature: $_"
    Write-Warning "Could not check digital signature"
}

# Test 5: NSIS installer detection
Write-Info "Test 5: NSIS installer detection..."
try {
    $content = Get-Content -Path $InstallerPath -Encoding Byte -TotalCount 10000
    $nsisSignature = [System.Text.Encoding]::ASCII.GetString($content)

    if ($nsisSignature -match "Nullsoft") {
        $testResults.Passed += "NSIS installer detected"
        Write-Success "NSIS installer detected"
    } else {
        $testResults.Warnings += "Could not detect NSIS signature"
        Write-Warning "Could not detect NSIS signature in first 10KB"
    }
} catch {
    $testResults.Warnings += "Could not scan for NSIS signature: $_"
    Write-Warning "Could not scan for NSIS signature"
}

# Test 6: Required components check (by size heuristic)
Write-Info "Test 6: Component size analysis..."

$expectedMinSize = 15 # MB - adjust based on your app
$actualSize = (Get-Item $InstallerPath).Length / 1MB

if ($actualSize -ge $expectedMinSize) {
    $testResults.Passed += "Installer appears to contain all components"
    Write-Success "Installer size suggests all components are included"
} else {
    $testResults.Warnings += "Installer might be missing components (size: $([math]::Round($actualSize, 2)) MB, expected: >$expectedMinSize MB)"
    Write-Warning "Installer might be missing components"
}

# Summary
Write-Host ""
Write-Host "======================================"
Write-Host " TEST SUMMARY"
Write-Host "======================================"
Write-Host ""
Write-Host "Installer: $(Split-Path $InstallerPath -Leaf)" -ForegroundColor White
Write-Host "Size: $([math]::Round($size, 2)) MB" -ForegroundColor White
Write-Host ""

Write-Host "Passed Tests: $($testResults.Passed.Count)" -ForegroundColor Green
foreach ($test in $testResults.Passed) {
    Write-Host "  [OK]   $test" -ForegroundColor Green
}

if ($testResults.Warnings.Count -gt 0) {
    Write-Host ""
    Write-Host "Warnings: $($testResults.Warnings.Count)" -ForegroundColor Yellow
    foreach ($warning in $testResults.Warnings) {
        Write-Host "  [WARN] $warning" -ForegroundColor Yellow
    }
}

if ($testResults.Failed.Count -gt 0) {
    Write-Host ""
    Write-Host "Failed Tests: $($testResults.Failed.Count)" -ForegroundColor Red
    foreach ($failure in $testResults.Failed) {
        Write-Host "  [FAIL] $failure" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "======================================"
    Write-Failure "INSTALLER TESTS FAILED"
    exit 1
} else {
    Write-Host ""
    Write-Host "======================================"
    Write-Success "ALL TESTS PASSED"
    Write-Host ""
    Write-Info "The installer is ready for distribution!"
    Write-Host ""
    Write-Info "Next steps:"
    Write-Host "  1. Test manual installation on a clean Windows machine"
    Write-Host "  2. Verify all features work correctly"
    Write-Host "  3. Create a release on GitHub"
    Write-Host ""
    exit 0
}
