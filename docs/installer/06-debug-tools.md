# 06 — Debug Tools

{% raw %}
Copy-paste PowerShell + bash to diagnose installer and runtime bugs.

## Diagnostic A — Verify a live install matches the expected layout

After install, before launching the app:

```powershell
$ROOT = "C:\Program Files\BOT-MMORPG-AI"

Write-Host "`n=== Required resource files ===" -ForegroundColor Cyan
$expect = @(
  "BOT-MMORPG-AI.exe",
  "Uninstall.exe",
  "resources\runtime\python-runtime.zip",
  "resources\backend\entry_main.py",
  "resources\backend\main_backend.py",
  "resources\modelhub\tauri.py",
  "resources\versions\0.01\1-collect_data.py",
  "resources\versions\0.01\2-train_model.py",
  "resources\versions\0.01\3-test_model.py",
  "resources\scripts\install_drivers.ps1",
  "drivers\interception\install-interception.exe",
  "drivers\vjoy\vJoySetup.exe"
)
$missing = @()
foreach ($rel in $expect) {
  $full = Join-Path $ROOT $rel
  if (Test-Path $full) {
    Write-Host ("  [OK]   {0,12:N0}  {1}" -f (Get-Item $full).Length, $rel) -ForegroundColor Green
  } else {
    Write-Host ("  [MISS]              {0}" -f $rel) -ForegroundColor Red
    $missing += $rel
  }
}

if ($missing.Count -eq 0) {
  Write-Host "`nInstaller extracted everything. Bug is in app runtime." -ForegroundColor Yellow
  Write-Host "Look at: src-tauri/src/main.rs (path resolvers, sidecar startup)"
} else {
  Write-Host "`nInstaller is missing $($missing.Count) file(s). Bug is in build/template." -ForegroundColor Red
  Write-Host "Look at: installer/nsis_template.nsi or scripts/build_pipeline.ps1"
}
```

**How to interpret:** every `[OK]` means the installer extracted that
file correctly. Any `[MISS]` means an installer-layer bug. If everything
is `[OK]` but the app still doesn't work, the bug is in
`src-tauri/src/main.rs` or `modelhub/tauri.py`.

## Diagnostic B — Read the rendered installer.nsi

Most installer bugs are template-rendering bugs, and the rendered
intermediate is the only file that tells you exactly what was compiled
into the `.exe`.

```powershell
# After `make build-installer`, before running the .exe:
$rendered = "src-tauri\target\release\bundle\nsis\installer.nsi"

if (Test-Path $rendered) {
  Write-Host "Rendered NSIS source:" -ForegroundColor Cyan

  # Show every File / CreateDirectory directive plus any leaked handlebars
  Get-Content $rendered |
    Select-String -Pattern 'CreateDirectory|^\s*File |\{\{' |
    Select-Object -First 40
} else {
  Write-Host "Build hasn't run or output dir was cleaned." -ForegroundColor Yellow
}
```

**Red flag:** any line in the output containing `{{` or `}}` means
handlebars failed to render that expression. Bug is in the template's
escape rules. See `04-bug-index.md` and `05-case-studies.md` Bug #3.

## Diagnostic C — Inspect the .exe payload with 7-Zip

The `.exe` is just an LZMA-compressed archive plus the NSIS runtime.
You can list its contents without installing:

```powershell
7z l "src-tauri\target\release\bundle\nsis\BOT-MMORPG-AI_*-x64-setup.exe"
```

Extract the payload to inspect:

```powershell
7z x "src-tauri\target\release\bundle\nsis\BOT-MMORPG-AI_*-x64-setup.exe" -o"C:\tmp\setup-payload"
Get-ChildItem "C:\tmp\setup-payload" -Recurse | Select-Object FullName
```

**How to interpret:** if `7z l` shows the file, the bundler embedded it
correctly and the bug is in the NSIS install bytecode (template). If
`7z l` doesn't show it, the bundler skipped it (`tauri.conf.json` glob
mismatch or staging step failure).

## Diagnostic D — Sidecar startup capture

If "Sidecar API not ready after 5 s" is showing, the embedded Python
sidecar is failing or slow. Capture stderr by running it manually:

```powershell
cd "C:\Program Files\BOT-MMORPG-AI"

$env:MODELHUB_RESOURCE_ROOT = "$pwd\resources"
$env:MODELHUB_DATA_ROOT     = "$pwd"
$env:PYTHONPATH = "$pwd\resources\backend;$pwd\resources\modelhub;$pwd\runtime\py\site-packages"

& "$pwd\runtime\py\python\python.exe" -u "$pwd\resources\backend\entry_main.py" --port 0 --token test
```

The first non-`READY` line of stderr is the import error / runtime crash.
This is exactly the sidecar startup the Rust code spawns at app launch
(see `src-tauri/src/main.rs#start_sidecar_server`).

## Diagnostic E — In-app diagnosis (built-in)

The app ships a one-click diagnostic. Open the installed app, click
**⚙ Settings** → **System Tools** → **▶ Run Diagnosis**. The panel runs
the `install_health` Tauri command and renders one row per subsystem
with a severity icon. Click **📋 Copy Support Report** to get a
Markdown bundle (app version, OS, install paths, every check) you can
paste into a GitHub issue.

This corresponds to:
- `src-tauri/src/main.rs#install_health` (line 1937) — the per-check probe
- `src-tauri/src/main.rs#support_report` (line 2166) — the Markdown bundle
- `tauri-ui/index.html` System Tools tab — the rendering

## Diagnostic F — Check the `terminal_update` event stream

Every Rust-side print to the user goes through:

```rust
window.emit("terminal_update", "...message...");
```

In the WebView devtools console (right-click → Inspect Element →
Console) you'll see them logged. Useful when the in-app log console
isn't visible (e.g. on the Run Bot tab).

## Build-time invariant checks

The build pipeline already greps the template for known bad patterns
before invoking `cargo tauri build`. If you discover a new failure mode,
add it to the preflight at `scripts/build_pipeline.ps1:1156-1175`.

Existing checks:
- `File /a /oname={{` (unquoted `/oname=`)
- Any whitespace in staged resource filenames

To add: `\\\\{{` regex (double backslash escape). Currently checked
indirectly via `tests/test_tauri_production_readiness.py`.
{% endraw %}
