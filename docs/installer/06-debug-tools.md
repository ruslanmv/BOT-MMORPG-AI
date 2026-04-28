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
  # Sidecar-owned job runner (MVP-3a/3b)
  "resources\modelhub\jobs\__init__.py",
  "resources\modelhub\jobs\runner.py",
  "resources\modelhub\jobs\routes.py",
  # Runtime self-test (MVP-2)
  "resources\scripts\runtime_doctor.py",
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

## Diagnostic G — Verify the bundled runtime tree (post-MVP-1)

After MVP-1 the runtime extracts to `%LOCALAPPDATA%\com.bot.mmorpg.ai\`,
not `$INSTDIR`. Use this when the doctor reports `torch_intact: error`
and you need to know whether the on-disk tree is healthy.

```powershell
$RT = "$env:LOCALAPPDATA\com.bot.mmorpg.ai\runtime\py\python"
$SP = "$RT\site-packages"

# 1. Bundled python boots cleanly
& "$RT\python.exe" --version

# 2. Critical submodules exist on disk -- the smoking-gun probe for
#    the AV-quarantine pattern (Bug #11 in 04-bug-index.md).
@(
  "$SP\torch\__init__.py",
  "$SP\torch\testing\__init__.py",     # Bug #9 / #11 deletes this
  "$SP\torch\fx\__init__.py",
  "$SP\torchvision\__init__.py",
  "$SP\numpy\__init__.py",
  "$SP\numpy\testing\__init__.py",     # Bug #11 also deletes this
  "$SP\fastapi\__init__.py",
  "$SP\uvicorn\__init__.py",
  "$SP\cv2\__init__.py"
) | ForEach-Object {
    $rel = $_.Replace("$SP\", "")
    if (Test-Path $_) {
        Write-Host ("  [OK]   {0}" -f $rel) -ForegroundColor Green
    } else {
        Write-Host ("  [MISS] {0}" -f $rel) -ForegroundColor Red
    }
}

# 3. Run the runtime doctor against the bundled python
& "$RT\python.exe" "C:\Program Files\BOT-MMORPG-AI\resources\scripts\runtime_doctor.py" `
   --selftest --pretty --data-dir "$env:LOCALAPPDATA\com.bot.mmorpg.ai"
```

The third command emits the same JSON the Tauri command `runtime_doctor`
returns to the UI. Useful when the UI itself isn't running (early-boot
debug, headless reproductions).

## Diagnostic H — In-app recovery ladder (post-MVP-3)

Click order matters. From the install-health banner or chip:

| Step | Button | What it does | When to use |
|---|---|---|---|
| 1 | `[↻ Restart Sidecar]` | Re-runs `start_sidecar_server` | Transient startup stall; first-launch cold-disk timeout |
| 2 | `[🛡 Add AV Exclusion]` | UAC prompt → `Add-MpPreference -ExclusionPath` for the runtime tree | Doctor reports `torch_testing_dir_exists=False` |
| 3 | `[🔧 Repair Runtime]` | Re-extracts `python-runtime.zip` into `%LOCALAPPDATA%\…\runtime\py\` | After AV exclusion, OR partial extract |
| 4 | `[🩺 Repair PyTorch (pip)]` | `pip install --force-reinstall --no-deps torch torchvision numpy` | Bundled zip itself is broken (pre-MVP-4 installer); 2-5 min, ~250 MB |
| 5 | `[📂 Open Logs Folder]` | Explorer at `%LOCALAPPDATA%\…\logs\` | Need to attach logs to a bug report |

Each maps to a Tauri command in `src-tauri/src/main.rs`:
`restart_sidecar`, `add_av_exclusion`, `repair_runtime`,
`repair_pytorch_via_pip`, `open_local_data_folder`.

After steps 2 + 3 (or step 4), click `[▶ Run Diagnosis]` to flip the
doctor verdict. Green chip = OK; red dot on the sidebar gear = error.

## Diagnostic I — Read the doctor JSON from outside the app

The doctor's full JSON output is what feeds the AI Fix Bundle, the
install-health banner, and the Settings → Runtime table. To inspect
it directly without the UI:

```powershell
$RT = "$env:LOCALAPPDATA\com.bot.mmorpg.ai\runtime\py\python"
$DOC = "C:\Program Files\BOT-MMORPG-AI\resources\scripts\runtime_doctor.py"
$DATA = "$env:LOCALAPPDATA\com.bot.mmorpg.ai"

& "$RT\python.exe" $DOC --selftest --pretty --data-dir $DATA |
  Out-File -Encoding utf8 "$env:TEMP\bot-mmorpg-doctor.json"
notepad "$env:TEMP\bot-mmorpg-doctor.json"
```

The `verdict` field rolls up to the worst per-check status. The
`checks[].detail` field carries the enriched failure context for
the bug-#9 pattern (torch_root + torch_testing_dir_exists).

## Build-time invariant checks

The build pipeline already greps the template for known bad patterns
before invoking `cargo tauri build`. If you discover a new failure mode,
add it to the preflight at `scripts/build_pipeline.ps1:1156-1175`.

Existing checks:
- `File /a /oname={{` (unquoted `/oname=`)
- Any whitespace in staged resource filenames

Plus the **runtime integrity check** added in MVP-4 at line 622-634:
runs the bundled python.exe against an explicit list of imports
(`torch.testing`, `numpy.testing`, `fastapi`, `uvicorn`, `cv2`,
`importlib.metadata.version()`) post-prune. Fails the build if any
import or version lookup fails — converts a runtime crash on the
user's machine into a build-time failure on CI.

To add a new check there: append a `@{ Stmt = ...; Why = ... }`
hashtable to `$integrityTests`.
{% endraw %}
