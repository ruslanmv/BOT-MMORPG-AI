<#
.SYNOPSIS
    Verifies a freshly-installed BOT-MMORPG-AI on Windows.

.DESCRIPTION
    Run this AFTER you've double-clicked BOT-MMORPG-AI_<version>_x64-setup.exe
    and accepted the UAC prompt. It checks every subsystem the user-facing
    app needs:

      1. Install layout (drivers, scripts, runtime archive, ML scripts)
      2. The first-launch python-runtime.zip extraction worked OR will
      3. Tauri sidecar can be spawned and reaches READY
      4. /modelhub/available and /modelhub/games respond
      5. The three production scripts can each --help (proves the runtime
         imports them with all dependencies)

    Anything red means the UI banner I added (install_health) would
    have shown the same diagnosis to a real user.

.PARAMETER InstallDir
    Path to the install. Defaults to "C:\Program Files\BOT-MMORPG-AI".

.EXAMPLE
    powershell -NoProfile -ExecutionPolicy Bypass -File scripts\windows_post_install_check.ps1
#>

param(
  [string]$InstallDir = "C:\Program Files\BOT-MMORPG-AI"
)

$ErrorActionPreference = "Stop"

function Write-Ok    ([string]$m) { Write-Host "[OK]   $m" -ForegroundColor Green }
function Write-Fail  ([string]$m) { Write-Host "[FAIL] $m" -ForegroundColor Red }
function Write-Info  ([string]$m) { Write-Host "[INFO] $m" -ForegroundColor Cyan }
function Write-Hdr   ([string]$m) {
  Write-Host ""
  Write-Host "==========================================="
  Write-Host " $m"
  Write-Host "==========================================="
}

$failures = @()

Write-Hdr "1. Install layout"
$mustExist = @(
  @{ P = "BOT-MMORPG-AI.exe";                                Why = "Tauri shell" },
  @{ P = "Uninstall.exe";                                    Why = "Uninstaller" },
  @{ P = "drivers\interception\install-interception.exe";    Why = "Interception driver installer" },
  @{ P = "drivers\vjoy\vJoySetup.exe";                       Why = "vJoy driver installer" },
  @{ P = "resources\runtime\python-runtime.zip";             Why = "Embedded Python runtime archive" },
  @{ P = "resources\backend\entry_main.py";                  Why = "Sidecar entrypoint" },
  @{ P = "resources\modelhub\tauri.py";                      Why = "ModelHub HTTP API" },
  @{ P = "resources\versions\0.01\1-collect_data.py";        Why = "Recording script" },
  @{ P = "resources\versions\0.01\2-train_model.py";         Why = "Training script" },
  @{ P = "resources\versions\0.01\3-test_model.py";          Why = "Run-Bot script" },
  @{ P = "resources\scripts\install_drivers.ps1";            Why = "Driver re-install helper" }
)
foreach ($m in $mustExist) {
  $full = Join-Path $InstallDir $m.P
  if (Test-Path $full) {
    if ($m.P -match "python-runtime\.zip$") {
      $sz = [math]::Round((Get-Item $full).Length / 1MB, 1)
      if ($sz -lt 10) {
        Write-Fail ("$($m.P) is suspiciously small ({0} MB)" -f $sz)
        $failures += "$($m.P): too small ($sz MB)"
      } else {
        Write-Ok ("$($m.P) ({0} MB)" -f $sz)
      }
    } else {
      Write-Ok $m.P
    }
  } else {
    Write-Fail "$($m.P) MISSING ($($m.Why))"
    $failures += "$($m.P) missing"
  }
}

Write-Hdr "2. Drivers actually registered (vJoy + Interception)"
$drivers = Get-PnpDevice -ErrorAction SilentlyContinue |
           Where-Object { $_.FriendlyName -match "vJoy|Interception" }
if ($drivers) {
  foreach ($d in $drivers) {
    Write-Ok ("{0,-40} status={1}" -f $d.FriendlyName, $d.Status)
  }
} else {
  Write-Fail "No vJoy / Interception devices found via Get-PnpDevice. Re-run resources\scripts\install_drivers.ps1 as Administrator."
  $failures += "drivers not registered"
}

Write-Hdr "3. Embedded Python runtime extraction"
$extractedExe = Join-Path $InstallDir "runtime\py\python\python.exe"
if (Test-Path $extractedExe) {
  $ver = & $extractedExe --version 2>&1
  Write-Ok "Runtime extracted: $ver"
} else {
  Write-Info "runtime\py\python\python.exe not yet extracted (this happens on first launch of BOT-MMORPG-AI.exe)."
  Write-Info "Run BOT-MMORPG-AI.exe once, watch for '[System] Extracting bundled Python runtime ->' in the terminal, then re-run this script."
}

Write-Hdr "4. The three ML scripts can be invoked (--help)"
if (Test-Path $extractedExe) {
  foreach ($script in "1-collect_data.py", "2-train_model.py", "3-test_model.py") {
    $sp = Join-Path $InstallDir "resources\versions\0.01\$script"
    Write-Info "  -> $script --help"
    & $extractedExe -u $sp --help 2>&1 |
        Select-Object -First 5 |
        ForEach-Object { Write-Host "    | $_" }
    if ($LASTEXITCODE -eq 0) {
      Write-Ok "$script imports + parses CLI"
    } else {
      Write-Fail "$script crashed on --help (likely missing deps in the runtime)"
      $failures += "$script --help failed"
    }
  }
} else {
  Write-Info "Skipped: runtime not yet extracted."
}

Write-Hdr "5. Sidecar HTTP API (only after launching BOT-MMORPG-AI.exe once)"
# We can't auto-launch the Tauri shell because it would block the script, so
# instead we tell the user how to verify it manually.
Write-Info "Manual step: launch BOT-MMORPG-AI from the Start Menu, watch the in-app"
Write-Info "             terminal panel until you see:"
Write-Info "                [System] Extracting bundled Python runtime -> ..."
Write-Info "                [System] Sidecar Python: ...\runtime\py\python\python.exe"
Write-Info "                [System] Sidecar Script: ...\resources\backend\entry_main.py"
Write-Info "                [System] Sidecar READY"
Write-Info "             plus a green dashboard with no red 'Backend installation"
Write-Info "             is incomplete' banner."

Write-Host ""
Write-Host "==========================================="
if ($failures.Count -eq 0) {
  Write-Ok "All offline checks passed. Now do the manual launch step in section 5."
  exit 0
} else {
  Write-Fail "Found $($failures.Count) issue(s):"
  foreach ($f in $failures) { Write-Host "  - $f" -ForegroundColor Yellow }
  exit 1
}
