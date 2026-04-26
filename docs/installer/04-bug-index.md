# 04 — Bug Index

{% raw %}
Symptom → file → fix-pattern. Ordered roughly by frequency on this
project. **Start here when a user reports an installer or runtime bug.**

## Build-time symptoms (the build itself fails)

### `Failed to setup custom handlebar template: invalid handlebars syntax`

The handlebars-rust parser hit unbalanced `{{...}}` tokens or an
unescaped `\{{` sequence in the template.

- **File:** `installer/nsis_template.nsi`
- **Common causes:** comment lines containing `{{#each ...}}` or
  `{{#if ...}}` without matching closes (NSIS's `;` is not a
  handlebars escape — handlebars parses the entire file regardless),
  or `\{{` (single backslash) in path strings.
- **Fix:** balance the tokens; rephrase comments without literal
  `{{` sequences. For path strings, use `\\{{` (double backslash).
- **See:** `05-case-studies.md` Bug #2 + Bug #3.

### `cargo tauri build` exits 0 but the `.exe` is suspiciously small (<10 MB)

The bundler couldn't find resources to bundle. Almost always a missing
staging step.

- **File:** `scripts/build_pipeline.ps1` — check that step 6.5/6.6/6.7 actually ran
- **Verify:** `Get-ChildItem src-tauri/resources -Recurse | Measure-Object` should show ~20k files

### `makensis.exe` errors with `Usage: File ...`

A resource filename contains spaces and the `/oname=` directive isn't
quoted, OR the staged file legitimately has whitespace in its name
that the build pipeline's filter missed.

- **File 1:** `installer/nsis_template.nsi` — make sure every `File`
  directive uses `File "/oname={{...}}" "{{...}}"` (quotes around both)
- **File 2:** `scripts/build_pipeline.ps1` — the filter that rejects
  whitespace filenames is around line 909 (versions) and 993 (backend/modelhub)
- **Guardrail:** `build_pipeline.ps1:1167` already greps for the
  unquoted form. Don't disable that check.

## Install-time symptoms (the .exe runs but the install is wrong)

### Folders literally named `{{this}}` or `{{this.[0]}}` appear under `$INSTDIR`

The handlebars escape rule was violated. `\{{` in handlebars-rust is
the escape for a literal `{{`, not a path separator. The bundler emitted
the unparsed expression to the rendered NSIS, and NSIS dutifully created
folders with those literal names.

- **File:** `installer/nsis_template.nsi`
- **Fix:** every NSIS path string with handlebars must use double
  backslash: `"$INSTDIR\\{{this}}"`, NOT `"$INSTDIR\{{this}}"`.
- **See:** `05-case-studies.md` Bug #3 (`943f9f8`).

### Resources are missing entirely from `$INSTDIR\resources\`

Either the bundler payload doesn't contain them, or the install-time
extraction failed silently.

- **Diagnose:** run the script in `06-debug-tools.md` (the diagnostic
  PowerShell). If it shows files exist under `$INSTDIR\resources\`, the
  installer is fine and you're chasing a runtime bug.
- **If files truly missing:** inspect the bundled `.exe` payload with
  `7z l`. If `7z l` shows them, the install bytecode is wrong (template
  bug). If `7z l` doesn't show them, the bundler skipped them
  (`tauri.conf.json` glob mismatch, or build_pipeline didn't stage them).

### Install dialog shows `Create folder: C:\Program Files\BOT-MMORPG-AI{{this}}` (5x)

This was the original symptom that triggered the whole branch. Same
class as the previous bug.

- **File:** `installer/nsis_template.nsi`
- **Fix:** use the canonical Tauri 1.x pattern (two separate loops:
  `{{#each resources_dirs}}` for `CreateDirectory`, `{{#each resources}}`
  for `File`) with `\\{{...}}` escaping.

## Runtime symptoms (install OK, app launches, but features fail)

### "Sidecar API not ready after 5 s"

The Python sidecar didn't print `READY url=...` to stdout within 5
seconds of being spawned.

- **Files:** `src-tauri/src/main.rs` (sidecar timeout — line 1205),
  `backend/entry_main.py` (the entrypoint that imports and calls
  `modelhub.tauri.main`)
- **Common causes:** Python cold-start lag (FastAPI + torch + numpy +
  cv2 imports can exceed 5s on a fresh disk), the backend script crashing
  on import, or AV holding `python.exe`.
- **Fix:** bump the timeout to 20-30s, or capture sidecar stderr into
  the in-app log so the import error is visible.

### "Script 'X.py' not found" with multiple `tried:` paths

The Rust script resolver didn't find the script.

- **File:** `src-tauri/src/main.rs#resolve_script` (around line 864)
- **Common cause:** wrong path prefix. Tauri 1.x's `resources/**` glob
  preserves the `resources/` prefix on extraction, so the resolver MUST
  probe `$INSTDIR\resources\versions\…` first.
- **See:** `05-case-studies.md` Bug #4 (`964e7c8`).

### "Failed to start bot: argument --model is required"

The `start_bot` Rust command spawned `3-test_model.py` without args,
but the script requires `--model`.

- **File:** `src-tauri/src/main.rs#start_bot` (line 1693)
- **Fix:** look up active model via sidecar `/modelhub/catalog`,
  forward `--model <model_dir>` to the script.
- **See:** `05-case-studies.md` Bug #6 (`4e16d1b`).

### Install Drivers button does nothing or fails with "Missing file"

The PowerShell driver script computes the wrong driver path under PROD.

- **File:** `scripts/install_drivers.ps1` (path resolution at line 134)
- **Fix:** probe `$PSScriptRoot\..\..\drivers` first (PROD layout has
  the script under `resources\scripts\`, drivers at `$INSTDIR\drivers\`,
  not `$INSTDIR\resources\drivers\`).
- **See:** `05-case-studies.md` Bug #5 (`9d8a16f`).

## UI-layer symptoms (frontend can't reach the backend)

### Notification "Dismiss" / "×" / "Later" buttons appear inert

`hidden` attribute set but element stays visible (CSS `display: flex`
on `.notification-card` overrides the user-agent `[hidden]` rule).

- **File:** `tauri-ui/index.html` — global rule `[hidden] { display: none !important }`
- **See:** `05-case-studies.md` Bug #8 (`104adae`).

### `<a target="_blank">` external links do nothing

Tauri 1.x webview drops external link navigation by default.

- **File:** `tauri-ui/index.html` — global click interceptor that
  routes through `window.__TAURI__.shell.open()`
- **See:** `05-case-studies.md` Bug #7 (`3d98b3d`).

### "ModelHub offline" in the log even when sidecar should be running

Either the sidecar genuinely failed (see runtime symptoms above), OR
the frontend is calling Tauri commands that haven't been wired through.

- **Frontend file:** `tauri-ui/main.js#refreshModelhubAvailability`
- **Rust file:** `src-tauri/src/main.rs#modelhub_is_available`
- **Sidecar file:** `modelhub/tauri.py:356` (`/modelhub/available` route)

## Decision tree

```
User reports a bug.
        │
        ▼
Does `make build-installer` itself fail?
        │
   ┌────┴────┐
   YES       NO
   │         │
   │         ▼
   │    Run diagnostic from 06-debug-tools.md
   │         │
   │    ┌────┴─────┐
   │    │          │
   │   Files       Files
   │   MISSING     PRESENT
   │   from        under
   │   $INSTDIR    $INSTDIR
   │    │          │
   │    ▼          ▼
   ▼    Installer  App-runtime layer
   nsis_template   nsis_template      src-tauri/src/main.rs
   .nsi or         .nsi or             OR  modelhub/tauri.py
   build_pipeline  build_pipeline      OR  the .py script itself
   .ps1            .ps1
```
{% endraw %}
