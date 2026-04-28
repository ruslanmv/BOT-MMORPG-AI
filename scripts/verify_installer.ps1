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

# IMPORTANT: this file MUST start with a UTF-8 BOM (the three bytes
# EF BB BF immediately before "<#"). The release workflow spawns
# `powershell -File scripts/verify_installer.ps1` which is Windows
# PowerShell 5.1, not pwsh. PS 5.1 decodes source files per the system
# ANSI codepage UNLESS the file has a UTF-8 BOM. Without the BOM, any
# UTF-8 character introduced into this file (a fancy quote, em-dash,
# check-mark glyph, ...) gets mis-decoded as CP-1252, the surrounding
# string literal fails to parse, the Write-* helpers below never
# register, and later calls fail with
#   "The term 'Write-Info' is not recognized as the name of a cmdlet"
# That is the exact failure we are guarding against. The BOM forces
# UTF-8 decoding regardless of the host's system codepage, so even if
# a future edit reintroduces non-ASCII characters the file still
# parses cleanly. Use [OK] / [FAIL] / [INFO] sentinels in
# user-visible strings to keep the file ASCII-clean as a second line
# of defense.

function Write-Success($msg) {
    Write-Host "[OK]   $msg" -ForegroundColor Green
}

function Write-Failure($msg) {
    Write-Host "[FAIL] $msg" -ForegroundColor Red
}

function Write-Info($msg) {
    Write-Host "[INFO] $msg" -ForegroundColor Cyan
}

# PHASE 13: non-fatal degraded-success channel. Used when a check
# couldn't complete for environmental reasons (UAC denied, sandbox
# without admin, etc.) but the build itself is fine. Goes to the
# $warnings array, which is reported separately from $errors at the
# verification summary so a CI runner can decide whether to treat
# warnings as failures.
function Write-Warn($msg) {
    Write-Host "[WARN] $msg" -ForegroundColor Yellow
}

# Normalize a Windows path to its canonical long form so string-compares
# don't fail on 8.3 short names. CI runners often have $env:TEMP =
# "C:\Users\RUNNER~1\AppData\..." (where RUNNER~1 is the auto-generated
# 8.3 short name for "runneradmin"), while NSIS resolves the install
# directory to its long form before writing shortcut targets. Pure
# string comparison then reports the shortcut as wrong even though both
# paths point at the same file.
#
# Get-Item walks the actual filesystem and returns the canonical
# long-name form via .FullName. If the path doesn't exist yet, we fall
# back to GetFullPath which at least normalizes . / .. / case.
function Resolve-LongPath([string]$Path) {
    if (-not $Path) { return $null }
    try {
        return (Get-Item -LiteralPath $Path -ErrorAction Stop).FullName
    } catch {
        return [System.IO.Path]::GetFullPath($Path)
    }
}

$root = Resolve-Path "$(Split-Path -Parent $MyInvocation.MyCommand.Path)\.." | % Path
$errors = @()
# PHASE 13: warnings are non-fatal -- a check that couldn't complete
# for environmental reasons (UAC canceled, missing optional driver
# installer, etc.) goes here instead of $errors. Reported in the
# summary so the operator sees them but `make artifact` doesn't fail.
$warnings = @()

Write-Info "Starting installer verification..."
Write-Info "Root directory: $root"
Write-Host ""

# Check 1: Backend sidecar binary
# Architecture changed: we no longer build a PyInstaller-frozen
# main-backend.exe. The Tauri app spawns the embedded Python runtime
# from resources/runtime/python-runtime.zip and runs backend/entry_main.py
# directly. The presence of those bundled assets is verified by
# Check 7 below ("Bundled runtime"); the old sidecar binary check would
# always fail and was masking the real verification result.
Write-Info "Skipping legacy PyInstaller sidecar check (architecture moved to embedded Python runtime)."

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

# Runtime self-test (MVP-2). Tauri's `runtime_doctor` command shells
# out to <bundled-python> resources\scripts\runtime_doctor.py to drive
# the install-health banner. Missing this file = banner can never
# resolve to "ready" because the doctor command synthesises a
# "doctor_script_not_found" error on every launch.
$doctorScriptPath = Join-Path $root "src-tauri\resources\scripts\runtime_doctor.py"
if (Test-Path $doctorScriptPath) {
    Write-Success "Runtime doctor script exists: resources/scripts/runtime_doctor.py"
} else {
    Write-Failure "Runtime doctor script not found: $doctorScriptPath"
    $errors += "Missing runtime_doctor.py (UI install-health banner cannot drive)"
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
# "Script not found" -- the very bugs users are hitting.
Write-Info "Checking bundled runtime (python runtime zip + backend + modelhub + versions)..."

# After STEP 6.7 the python runtime is packaged as a single zip file under
# resources\runtime\ (the Tauri main.rs unpack code looks there first; see
# src-tauri/src/main.rs lines ~350 and ~368). Older builds shipped the
# unpacked python/ tree at resources\python\; accept either, plus the legacy
# resources\python-runtime.zip location for backward compatibility.
$bundledZip = Join-Path $root "src-tauri\resources\runtime\python-runtime.zip"
$bundledZipLegacy = Join-Path $root "src-tauri\resources\python-runtime.zip"
$bundledPython = Join-Path $root "src-tauri\resources\python\python.exe"

$zipPath = $null
$zipRel  = $null
if (Test-Path $bundledZip) {
    $zipPath = $bundledZip
    $zipRel  = "resources/runtime/python-runtime.zip"
} elseif (Test-Path $bundledZipLegacy) {
    $zipPath = $bundledZipLegacy
    $zipRel  = "resources/python-runtime.zip"
}

if ($zipPath) {
    $zipMB = (Get-Item $zipPath).Length / 1MB
    if ($zipMB -ge 10) {
        Write-Success ("Bundled Python runtime archive exists: {0} ({1:N1} MB)" -f $zipRel, $zipMB)
    } else {
        Write-Failure ("Bundled Python runtime archive too small: {0:N1} MB" -f $zipMB)
        $errors += "$zipRel is suspiciously small (offline deps missing)"
    }
} elseif (Test-Path $bundledPython) {
    Write-Success "Bundled Python runtime exists (unpacked legacy layout): resources/python/python.exe"

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
} else {
    Write-Failure "Bundled Python runtime missing: expected one of $bundledZip, $bundledZipLegacy, or $bundledPython"
    $errors += "resources/runtime/python-runtime.zip and resources/python/ both missing (sidecar cannot start)"
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

# MVP-3a/3b: sidecar-owned job runner. The Tauri shell now POSTs every
# Python spawn to /jobs (collect_data, train_model, test_model) instead
# of spawning locally. Missing this package = "Sidecar returned no
# job_id" on every Start click.
$bundledJobsRoutes = Join-Path $root "src-tauri\resources\modelhub\jobs\routes.py"
$bundledJobsRunner = Join-Path $root "src-tauri\resources\modelhub\jobs\runner.py"
if ((Test-Path $bundledJobsRoutes) -and (Test-Path $bundledJobsRunner)) {
    Write-Success "Bundled modelhub.jobs package exists (runner.py + routes.py)"
} else {
    Write-Failure "Bundled modelhub.jobs package incomplete (need runner.py + routes.py)"
    $errors += "resources/modelhub/jobs/ missing (Tauri /jobs POSTs will all fail)"
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

# Check 8: Real install dry-run (the test that would have caught the missing-exe bug)
#
# Up to here every check just asserts that build artifacts exist on disk and that
# the .exe has a valid PE header. That is what let CI report "All checks passed!"
# while real installs were broken (the install dir contained Uninstall.exe,
# installer.nsi, English.nsh and resources/, but NO main exe). The only check
# that would have caught it is to actually run the installer against a clean
# directory and walk the result. We do that here:
#   1) Run BOT-MMORPG-AI_*_x64-setup.exe /S /D=<temp>  (NSIS silent + dir override)
#   2) Assert <temp>\BOT-MMORPG-AI.exe is present
#   3) Assert <temp>\installer.nsi and <temp>\English.nsh are NOT present
#   4) Assert <temp>\Uninstall.exe is present
#   5) Run Uninstall.exe /S to clean up
#
# Skip flag for environments where running an admin installer is impractical
# (developers without admin, sandboxed CI runners). Set $env:SKIP_INSTALL_DRYRUN=1.
Write-Info "Performing real silent-install dry-run..."

if ($env:SKIP_INSTALL_DRYRUN -eq "1") {
    Write-Info "SKIP_INSTALL_DRYRUN=1 set; skipping real silent-install verification."
} else {
    $installerExe = $null
    if (Test-Path $installerDir) {
        $installerExe = Get-ChildItem -Path $installerDir -Filter "BOT-MMORPG-AI_*_x64-setup.exe" -ErrorAction SilentlyContinue |
            Select-Object -First 1
    }

    if (-not $installerExe) {
        Write-Failure "No BOT-MMORPG-AI_*_x64-setup.exe in $installerDir; cannot dry-run."
        $errors += "installer .exe missing for dry-run"
    } else {
        $testDir = Join-Path $env:TEMP ("bot-mmorpg-install-test-{0}" -f ([guid]::NewGuid().ToString("N").Substring(0, 8)))
        Write-Info ("Dry-run target dir: {0}" -f $testDir)
        Write-Info ("Running: {0} /S /D={1}" -f $installerExe.Name, $testDir)

        # NSIS quirks:
        #  - /D= MUST be the LAST argument and MUST NOT be quoted (NSIS reads
        #    it as the literal rest of the command line). PowerShell respects
        #    that as long as we pass it as a single bare token.
        #  - /S enables silent install (no GUI).
        # Start-Process + -Wait gives us a deterministic exit code.
        #
        # PHASE 13 hardening: NSIS installers default to
        # `RequestExecutionLevel admin`, so Windows pops a UAC prompt
        # for THIS launch even when the target is in user-writable
        # %TEMP%. If the operator is away from the keyboard the UAC
        # prompt either auto-cancels or sits forever (depending on
        # GP); PowerShell raises a TERMINATING InvalidOperationException
        # ("The operation was canceled by the user.") which
        # -ErrorAction SilentlyContinue does NOT swallow -- it crashes
        # the whole verify step and `make artifact` exits non-zero.
        # We catch it explicitly: the build itself already succeeded;
        # the dry-run is a confirmation, not a correctness gate. So
        # we downgrade to a warning + clear remediation so the
        # operator can either retry interactively, set
        # SKIP_INSTALL_DRYRUN=1, or just skip and run the .exe by
        # hand later.
        #
        # Heads-up before Start-Process so the operator knows a UAC
        # prompt is about to appear and isn't surprised. We can't
        # extend Windows' built-in UAC dialog timeout from here, so
        # the realistic mitigation is "tell them it's coming" + "if
        # they miss it, it's a warning not an error".
        Write-Info ""
        Write-Info ">>> About to launch the installer to verify a clean install."
        Write-Info ">>> Windows will show a UAC prompt in ~3s. Click YES to proceed."
        Write-Info ">>> If you miss the prompt, the dry-run will be skipped with a"
        Write-Info ">>> warning -- the build itself is already complete."
        Write-Info ""
        Start-Sleep -Seconds 3

        $proc = $null
        $launchCanceled = $false
        $launchHardErrored = $false  # set when an unexpected
                                     # exception was already reported,
                                     # so the elseif below doesn't
                                     # double-count it.
        try {
            $proc = Start-Process -FilePath $installerExe.FullName `
                -ArgumentList "/S", "/D=$testDir" `
                -Wait -PassThru -ErrorAction Stop
        } catch [System.InvalidOperationException] {
            # The exception text is localized but the symptom is
            # always a missed/denied UAC prompt or AV block. Match
            # both common variants ("canceled" / "cancelled").
            if ($_.Exception.Message -match "canceled|cancelled") {
                $launchCanceled = $true
            } else {
                Write-Failure "Silent installer launch failed: $($_.Exception.Message)"
                $errors += "silent install launch failed: $($_.Exception.Message)"
                $launchHardErrored = $true
            }
        } catch {
            # Any other unexpected exception -- preserve old behavior
            # so a real bug is still surfaced. Set the hard-error
            # flag so the launch-state cascade below doesn't add a
            # second "no-process" entry.
            Write-Failure "Silent installer launch failed: $($_.Exception.Message)"
            $errors += "silent install launch failed: $($_.Exception.Message)"
            $launchHardErrored = $true
        }

        if ($launchCanceled) {
            Write-Warn ""
            Write-Warn "==============================================================="
            Write-Warn "SILENT INSTALL DRY-RUN: NOT TESTED"
            Write-Warn ""
            Write-Warn "Nobody confirmed the UAC prompt within Windows' built-in"
            Write-Warn "timeout (~2 minutes). The build itself succeeded -- only"
            Write-Warn "the post-build 'does it install cleanly on a fresh dir?'"
            Write-Warn "check did not run."
            Write-Warn ""
            Write-Warn "Bypass next time (skip the dry-run entirely):"
            Write-Warn "  PowerShell:    `$env:SKIP_INSTALL_DRYRUN = '1'; make artifact"
            Write-Warn "  Bash:          SKIP_INSTALL_DRYRUN=1 make artifact"
            Write-Warn ""
            Write-Warn "Or actually run the dry-run yourself when you're at the keyboard:"
            Write-Warn "  $($installerExe.FullName) /S /D=<some-temp-dir>"
            Write-Warn "==============================================================="
            Write-Warn ""
            $warnings += "silent install dry-run not tested (nobody confirmed UAC prompt)"
        } elseif ($launchHardErrored) {
            # Catch-all branch already wrote Failure + appended to
            # $errors; nothing more to do here. We just need to
            # NOT fall through to the next elseif (which would add
            # a duplicate "<no-process>" entry).
        } elseif ($null -eq $proc -or $proc.ExitCode -ne 0) {
            $code = if ($proc) { $proc.ExitCode } else { "<no-process>" }
            Write-Failure "Silent installer exited with code $code"
            $errors += "silent install failed (exit $code)"
        } else {
            Write-Success "Silent installer exit code: 0"

            # (1) Main exe MUST be present.
            $expectedExe = Join-Path $testDir "BOT-MMORPG-AI.exe"
            if (Test-Path $expectedExe) {
                $exeSizeMB = [math]::Round((Get-Item $expectedExe).Length / 1MB, 2)
                Write-Success ("Main exe present at {0} ({1} MB)" -f $expectedExe, $exeSizeMB)
            } else {
                Write-Failure "MAIN EXE MISSING: $expectedExe (this is the headline bug)"
                $errors += "BOT-MMORPG-AI.exe not extracted by silent install"
            }

            # (2) The file must be stored with the canonical UPPERCASE name.
            # NTFS is case-insensitive at LOOKUP time but PRESERVES the
            # original casing in directory listings. Test-Path
            # "bot-mmorpg-ai.exe" returns true even when the file was
            # actually written as "BOT-MMORPG-AI.exe", so the previous
            # lowercase-variant check was tautological and produced a
            # false-positive failure. Assert against the actual stored
            # name returned by Get-ChildItem instead.
            $mainExeEntry = Get-ChildItem -Path $testDir -File -ErrorAction SilentlyContinue |
                Where-Object { $_.Name -ieq "BOT-MMORPG-AI.exe" } |
                Select-Object -First 1

            if ($mainExeEntry) {
                # -ceq is the case-SENSITIVE equality operator. If
                # /oname=BOT-MMORPG-AI.exe ever regressed to lowercase
                # the comparison would catch it.
                if ($mainExeEntry.Name -ceq "BOT-MMORPG-AI.exe") {
                    Write-Success ("Main exe stored with canonical case: {0}" -f $mainExeEntry.Name)
                } else {
                    Write-Failure ("Main exe stored with non-canonical case: '{0}' (expected 'BOT-MMORPG-AI.exe')" -f $mainExeEntry.Name)
                    $errors += ("main exe casing mismatch: {0}" -f $mainExeEntry.Name)
                }
            }

            # (3) Bundler artifacts MUST NOT leak into install dir.
            foreach ($leak in @("installer.nsi", "English.nsh", "nsis-output.exe")) {
                $leakPath = Join-Path $testDir $leak
                if (Test-Path $leakPath) {
                    Write-Failure "Bundler artifact leaked into install dir: $leak"
                    $errors += "$leak present in install dir (cleanup failed)"
                } else {
                    Write-Success "No leaked bundler artifact: $leak"
                }
            }

            # (4) Uninstall.exe must exist (NSIS guarantees this only after WriteUninstaller).
            $uninstallExe = Join-Path $testDir "Uninstall.exe"
            if (Test-Path $uninstallExe) {
                Write-Success "Uninstall.exe present"

                # (4b) Shortcuts: verify each .lnk created by the installer
                # actually targets a real file. The previous bug class would
                # have shipped shortcuts pointing to a non-existent main exe;
                # this check catches that immediately. We use WScript.Shell COM
                # to read .lnk TargetPath -- this is the same API Windows
                # Explorer uses to resolve a shortcut's "Target" property.
                $wsh = $null
                try { $wsh = New-Object -ComObject WScript.Shell } catch {}

                if ($null -eq $wsh) {
                    Write-Info "WScript.Shell COM unavailable; skipping shortcut-target check"
                } else {
                    # The installer creates these per the NSIS template:
                    #   $SMPROGRAMS\BOT-MMORPG-AI\BOT-MMORPG-AI.lnk -> $INSTDIR\BOT-MMORPG-AI.exe
                    #   $SMPROGRAMS\BOT-MMORPG-AI\Uninstall.lnk     -> $INSTDIR\Uninstall.exe
                    #   $DESKTOP\BOT-MMORPG-AI.lnk                  -> $INSTDIR\BOT-MMORPG-AI.exe
                    # Note: per-machine NSIS install writes to All Users
                    # ($SMPROGRAMS = CommonStartMenu, $DESKTOP = CommonDesktop).
                    $allUsersStart = [Environment]::GetFolderPath("CommonStartMenu")
                    $allUsersDesk  = [Environment]::GetFolderPath("CommonDesktopDirectory")

                    $shortcutChecks = @(
                        @{
                            Lnk    = (Join-Path $allUsersStart "Programs\BOT-MMORPG-AI\BOT-MMORPG-AI.lnk")
                            Target = (Join-Path $testDir "BOT-MMORPG-AI.exe")
                            Label  = "Start Menu app shortcut"
                        },
                        @{
                            Lnk    = (Join-Path $allUsersStart "Programs\BOT-MMORPG-AI\Uninstall.lnk")
                            Target = (Join-Path $testDir "Uninstall.exe")
                            Label  = "Start Menu uninstall shortcut"
                        },
                        @{
                            Lnk    = (Join-Path $allUsersDesk "BOT-MMORPG-AI.lnk")
                            Target = (Join-Path $testDir "BOT-MMORPG-AI.exe")
                            Label  = "Desktop app shortcut"
                        }
                    )

                    foreach ($sc in $shortcutChecks) {
                        if (-not (Test-Path $sc.Lnk)) {
                            Write-Failure ("{0} not created: {1}" -f $sc.Label, $sc.Lnk)
                            $errors += ("{0} missing" -f $sc.Label)
                            continue
                        }

                        try {
                            $lnkObj = $wsh.CreateShortcut($sc.Lnk)
                            $actualTarget = $lnkObj.TargetPath
                        } catch {
                            Write-Failure ("Could not read {0} target: {1}" -f $sc.Label, $_.Exception.Message)
                            $errors += ("{0} unreadable" -f $sc.Label)
                            continue
                        }

                        # Case-insensitive path equality after resolving 8.3
                        # short names. NTFS is case-insensitive by default,
                        # and lnk targets are stored in whatever long-form
                        # NSIS expanded $INSTDIR to -- which doesn't always
                        # match the (possibly 8.3-short) value we built
                        # $sc.Target from. Resolve-LongPath canonicalizes
                        # both sides before comparing.
                        $expectedNorm = Resolve-LongPath $sc.Target
                        $actualNorm   = Resolve-LongPath $actualTarget
                        if ($actualNorm -ieq $expectedNorm) {
                            Write-Success ("{0} -> {1}" -f $sc.Label, $actualTarget)
                        } else {
                            Write-Failure ("{0} points to wrong target.`n  expected: {1}`n  actual:   {2}`n  (normalized: {3} vs {4})" -f $sc.Label, $sc.Target, $actualTarget, $expectedNorm, $actualNorm)
                            $errors += ("{0} target mismatch" -f $sc.Label)
                        }

                        # And the target must actually exist on disk.
                        if (Test-Path $actualTarget) {
                            Write-Success ("{0} target file exists" -f $sc.Label)
                        } else {
                            Write-Failure ("{0} target file missing on disk: {1}" -f $sc.Label, $actualTarget)
                            $errors += ("{0} target missing on disk" -f $sc.Label)
                        }
                    }
                }

                # (5) Clean up: run uninstaller silently. We do not gate the
                # overall verification result on this; it's just hygiene.
                Write-Info "Running silent uninstall to clean up..."
                $unProc = Start-Process -FilePath $uninstallExe `
                    -ArgumentList "/S" -Wait -PassThru -ErrorAction SilentlyContinue
                if ($unProc -and $unProc.ExitCode -eq 0) {
                    Write-Success "Silent uninstall exit code: 0"
                } else {
                    $code = if ($unProc) { $unProc.ExitCode } else { "<no-process>" }
                    Write-Info "Uninstall exited with code $code (best-effort cleanup; not fatal)"
                }

                # NSIS uninstall is async on some Windows builds (it spawns
                # Un_A.exe and returns immediately). Give the leftover dir a
                # short window to disappear, then force-remove it.
                Start-Sleep -Seconds 2
                if (Test-Path $testDir) {
                    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $testDir
                }
            } else {
                Write-Failure "Uninstall.exe missing in $testDir"
                $errors += "Uninstall.exe not produced"
            }
        }
    }
}

# Summary
Write-Host ""
Write-Host "======================================"
Write-Host " VERIFICATION SUMMARY"
Write-Host "======================================"

if ($errors.Count -eq 0) {
    if ($warnings.Count -eq 0) {
        Write-Success "All checks passed! Installer is ready."
    } else {
        # Phase 13: degraded-success path. The installer is still
        # ready (build succeeded, all hard checks passed) but one
        # or more soft checks were skipped because they needed
        # human interaction (UAC) or an optional asset (vJoy).
        Write-Success "All required checks passed. Installer is ready (with $($warnings.Count) warning(s) below)."
    }
    Write-Host ""
    Write-Info "Installer location: $installerDir"
    if ($warnings.Count -gt 0) {
        Write-Host ""
        Write-Warn "Warnings (non-fatal -- build is still good):"
        foreach ($w in $warnings) {
            Write-Host "  - $w" -ForegroundColor Yellow
        }
    }
    exit 0
} else {
    Write-Failure "Verification failed with $($errors.Count) error(s):"
    Write-Host ""
    # NOTE: do NOT name the loop variable `$error` -- that's a PowerShell
    # automatic, read-only variable. Doing so used to abort the whole
    # script with "Cannot overwrite variable Error because it is read-only
    # or constant" before the failures could even be printed.
    foreach ($err in $errors) {
        Write-Host "  - $err" -ForegroundColor Yellow
    }
    if ($warnings.Count -gt 0) {
        Write-Host ""
        Write-Warn "Also reported $($warnings.Count) warning(s):"
        foreach ($w in $warnings) {
            Write-Host "  - $w" -ForegroundColor Yellow
        }
    }
    Write-Host ""
    Write-Info "Please run the build pipeline again: .\scripts\build_pipeline.ps1"
    exit 1
}
