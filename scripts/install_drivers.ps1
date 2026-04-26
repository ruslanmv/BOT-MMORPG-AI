param(
    [switch]$Download  # If set, download drivers from internet if missing
)

# --- SELF-ELEVATION BLOCK ---
# MOVED: This must come AFTER param() but BEFORE the main logic.
# This checks if the script is running as Admin. If not, it restarts itself as Admin.
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "Requesting Administrator privileges..." -ForegroundColor Yellow
    
    # Build the argument list to pass current parameters to the elevated instance
    $argList = "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`""
    if ($PSBoundParameters.Count -gt 0) {
        foreach ($key in $PSBoundParameters.Keys) {
            # Handle switch parameters (like -Download) vs value parameters
            if ($PSBoundParameters[$key] -is [bool]) {
                if ($PSBoundParameters[$key]) { $argList += " -$key" }
            } else {
                $argList += " -$key `"$($PSBoundParameters[$key])`""
            }
        }
    }
    
    Start-Process powershell.exe -ArgumentList $argList -Verb RunAs
    exit
}
# ----------------------------

$ErrorActionPreference = "Stop"

function Write-Info($m){ Write-Host "[INFO] $m" -ForegroundColor Cyan }
function Write-Ok($m){ Write-Host "[OK]   $m" -ForegroundColor Green }
function Write-Warn($m){ Write-Host "[WARN] $m" -ForegroundColor Yellow }
function Write-Err($m){ Write-Host "[ERR]  $m" -ForegroundColor Red }

function Assert-Admin {
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()
    ).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $isAdmin) {
        Write-Err "This script requires Administrator privileges to install drivers."
        Write-Info "Please right-click PowerShell and select 'Run as Administrator'"
        exit 1
    }
}

# FIXED: Renamed $args to $InstallArgs to avoid conflict with reserved variable
function Run-Exe($path, $InstallArgs="") {
    if (-not (Test-Path $path)) { throw "Missing file: $path" }
    
    Write-Info "Running: $path $InstallArgs"
    
    # FIXED: Only pass ArgumentList if $InstallArgs is not empty to avoid null error
    if ([string]::IsNullOrWhiteSpace($InstallArgs)) {
        $p = Start-Process -FilePath $path -Wait -PassThru
    } else {
        $p = Start-Process -FilePath $path -ArgumentList $InstallArgs -Wait -PassThru
    }

    if ($p.ExitCode -ne 0) { throw "Failed (exit $($p.ExitCode)): $path" }
}

function Download-Driver {
    param(
        [string]$Url,
        [string]$OutPath,
        [string]$Name
    )

    $outDir = Split-Path -Parent $OutPath
    if (-not (Test-Path $outDir)) {
        New-Item -ItemType Directory -Path $outDir -Force | Out-Null
    }

    Write-Info "Downloading $Name from $Url..."
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri $Url -OutFile $OutPath -UseBasicParsing
        Write-Ok "$Name downloaded to $OutPath"
        return $true
    } catch {
        Write-Err "Failed to download ${Name}: $($_.Exception.Message)"
        return $false
    }
}

function Download-AndExtract-Driver {
    param(
        [string]$Url,
        [string]$OutDir,
        [string]$ExpectedExe,
        [string]$Name
    )

    if (-not (Test-Path $OutDir)) {
        New-Item -ItemType Directory -Path $OutDir -Force | Out-Null
    }

    $zipPath = Join-Path $OutDir "temp_download.zip"

    Write-Info "Downloading $Name from $Url..."
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri $Url -OutFile $zipPath -UseBasicParsing
        Write-Ok "$Name archive downloaded"

        Write-Info "Extracting $Name..."
        Expand-Archive -Path $zipPath -DestinationPath $OutDir -Force
        Remove-Item $zipPath -Force

        # Find the exe in extracted contents
        $found = Get-ChildItem -Path $OutDir -Recurse -Filter "*.exe" | Select-Object -First 1
        if ($found -and ($found.FullName -ne $ExpectedExe)) {
            Copy-Item $found.FullName -Destination $ExpectedExe -Force
        }

        Write-Ok "$Name extracted"
        return $true
    } catch {
        Write-Err "Failed to download/extract ${Name}: $($_.Exception.Message)"
        if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
        return $false
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " BOT-MMORPG-AI Driver Installer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Assert-Admin

# Locate the drivers/ folder. Two install layouts are possible:
#
#   DEV (this repo):
#     <repo>\scripts\install_drivers.ps1
#         => drivers at <repo>\src-tauri\drivers\
#
#   PROD (after `make build-installer` + NSIS install):
#     C:\Program Files\BOT-MMORPG-AI\resources\scripts\install_drivers.ps1
#         => drivers at C:\Program Files\BOT-MMORPG-AI\drivers\
#         (the resources/** glob in tauri.conf.json puts THIS script under
#          resources\scripts\, but the drivers/** glob keeps drivers\ at the
#          install root -- one level higher than where this script lives.)
#
# The previous version assumed PROD drivers were at <script_parent>\drivers,
# which resolves to ...\resources\drivers and silently misses every install
# attempt because that folder doesn't exist.
$candidates = @(
    (Join-Path $PSScriptRoot "..\..\drivers"),         # PROD: install_dir\drivers
    (Join-Path $PSScriptRoot "..\src-tauri\drivers"),  # DEV:  repo\src-tauri\drivers
    (Join-Path $PSScriptRoot "..\drivers")             # legacy/fallback
)
$driversDir = $null
foreach ($c in $candidates) {
    $resolved = (Resolve-Path -LiteralPath $c -ErrorAction SilentlyContinue).Path
    if ($resolved -and (Test-Path $resolved)) {
        $driversDir = $resolved
        break
    }
}
if (-not $driversDir) {
    Write-Err "Could not locate the drivers/ folder."
    Write-Err "Tried (relative to $PSScriptRoot):"
    foreach ($c in $candidates) { Write-Err "  - $c" }
    Write-Err "Re-run the latest installer to restore drivers/interception/ and drivers/vjoy/."
    exit 1
}
Write-Info "Using drivers folder: $driversDir"

$interceptionDir = Join-Path $driversDir "interception"
$vjoyDir = Join-Path $driversDir "vjoy"
$interception = Join-Path $interceptionDir "install-interception.exe"
$vjoy = Join-Path $vjoyDir "vJoySetup.exe"

# Download URLs
$interceptionUrl = "https://github.com/oblitum/Interception/releases/download/v1.0.1/Interception.zip"
$vjoyUrl = "https://github.com/shauleiz/vJoy/releases/download/v2.1.9.1/vJoySetup.exe"

Write-Info "Checking driver availability..."

if (-not (Test-Path $interception)) {
    if ($Download) {
        Write-Warn "Interception driver not found. Downloading..."
        $success = Download-AndExtract-Driver -Url $interceptionUrl -OutDir $interceptionDir -ExpectedExe $interception -Name "Interception"
    } else {
        Write-Warn "Interception driver not found at $interception"
    }
}

if (-not (Test-Path $vjoy)) {
    if ($Download) {
        Write-Warn "vJoy driver not found. Downloading..."
        Download-Driver -Url $vjoyUrl -OutPath $vjoy -Name "vJoy"
    } else {
        Write-Warn "vJoy driver not found at $vjoy"
    }
}

Write-Host ""
Write-Info "Installing drivers..."
Write-Host ""

# Install Interception
if (Test-Path $interception) {
    Write-Info "Installing Interception driver..."
    try {
        Push-Location (Split-Path $interception)
        Run-Exe ".\install-interception.exe" "/install"
        Pop-Location
        Write-Ok "Interception driver installed."
    } catch {
        Write-Warn "Interception install failed: $($_.Exception.Message)"
    }
}

# Install vJoy
if (Test-Path $vjoy) {
    Write-Info "Installing vJoy driver..."
    try {
        Run-Exe $vjoy "/S"
        Write-Ok "vJoy driver installed."
    } catch {
        Write-Warn "vJoy install failed: $($_.Exception.Message)"
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Ok "Driver installation sequence complete!"
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Warn "A system REBOOT is required for drivers to take effect."
Write-Host ""