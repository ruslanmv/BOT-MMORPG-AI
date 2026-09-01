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

### `fatal error C1083: Cannot open include file: 'Python.h'` / `Failed building wheel for gevent`

A dependency without a prebuilt `cp310`/`cp311` wheel (e.g. `gevent` /
`greenlet`, pulled in transitively by `eel`) tries to compile from
source against the **embeddable** Python runtime — which ships only the
interpreter, no `Include\Python.h` and no `libs\python3XX.lib`. The MSVC
compile starts and dies immediately on the missing header.

- **File:** `scripts/prepare_python_from_pyproject_embed310_target.ps1`
  and `..._embed311_target.ps1` (`Ensure-EmbeddedBuildHeaders`)
- **Fix:** before any `pip wheel` / `pip install --target`, copy
  `Include\*` and `libs\python3XX.lib` from a full host CPython of the
  same minor version (the one `actions/setup-python` installs — headers
  are ABI-stable across `3.X.Y` patch releases) into the embeddable
  runtime dir. Also pass `--prefer-binary` so pip only compiles when no
  wheel exists. Best-effort: warns and continues if no host interpreter
  with headers is found.
- **Why not just pin/remove the dep:** the header provisioning fixes the
  whole class of "C-extension dep has no cp3XX wheel" build breaks, not
  just this one package.

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

### `ModuleNotFoundError: No module named 'torch.testing'` followed by exit `-1073741819`

The build pipeline's site-packages prune rule deleted runtime-required
submodules. `import torch` succeeds at the package level (the directory
is intact); a transitive `import torch.testing` then raises, and the
half-initialized native `torch._C` extensions crash on interpreter
shutdown with `STATUS_ACCESS_VIOLATION` (0xC0000005, exit code
`-1073741819`).

- **File:** `scripts/build_pipeline.ps1` (prune rule around line 580).
- **Affected packages:** `torch/testing`, `numpy/testing`, and any other
  `*/testing/` directory in mainstream scientific-Python wheels.
- **Fix:** the prune `Where-Object` filter must match `tests` (plural)
  only — never `test` or `testing`. Also: a post-prune integrity check
  must `import` every required submodule under the bundled python.exe
  so a future regression breaks the build, not the user's machine.
- **End-user recovery (no rebuild):**
  ```powershell
  & "C:\Program Files\BOT-MMORPG-AI\runtime\py\python\python.exe" `
    -m pip install --upgrade --force-reinstall --no-deps `
    --index-url https://download.pytorch.org/whl/cpu torch torchvision
  ```
- **See:** `05-case-studies.md` Bug #9.

### `torch.testing` / `numpy.testing` missing AT RUNTIME on a clean install (Bug #11, the AV-quarantine variant)

Distinct from Bug #9 above. Bug #9 is the BUILD shipping a corrupted
zip. Bug #11 is the BUILD shipping a clean zip but Defender (or
corporate AV) deleting `torch/testing/` and `numpy/testing/` from
disk after the Tauri shell extracts the zip into `%LOCALAPPDATA%`.

**Distinguishing signal:** open Settings → System Tools → Run
Diagnosis. The runtime doctor's `torch_intact` row shows:

```
ModuleNotFoundError: No module named 'torch.testing' |
torch_root=C:\Users\<u>\AppData\Local\com.bot.mmorpg.ai\runtime\py\python\site-packages\torch |
torch_testing_dir_exists=False
```

The boolean is the smoking gun: torch's package dir exists, the
`testing/` subdirectory does not. AV-quarantine fits this pattern
exactly — AV products typically delete specific signed binaries
or directory trees that match a heuristic, not random files.

- **File:** none — this is a runtime state issue, not a code bug.
- **Recovery (in this exact order, the order matters):**
  1. Click `[🛡 Add AV Exclusion]` in the install-health banner or
     Settings → System Tools. UAC prompt → Defender excludes
     `%LOCALAPPDATA%\com.bot.mmorpg.ai\runtime\py\`.
  2. Click `[🔧 Repair Runtime]`. Re-extracts python-runtime.zip
     into the now-excluded directory; AV gives it a pass.
  3. Click `[↻ Restart Sidecar]` and / or `[▶ Run Diagnosis]`. The
     doctor verdict should flip to `ok`.
- **Last-resort recovery if the bundled zip itself is also broken
  (an installer built before MVP-4 shipped):**
  - Click `[🩺 Repair PyTorch (pip)]`. Downloads fresh torch +
    torchvision + numpy from PyPI, force-reinstalling without deps.
    2-5 minutes; ~250 MB; bypasses both the bundled zip AND any
    AV interference (pip writes to a temp dir then atomic-renames,
    which most AV products give a pass).
- **Code that drives these recoveries:**
  - `src-tauri/src/main.rs#add_av_exclusion`
  - `src-tauri/src/main.rs#repair_runtime`
  - `src-tauri/src/main.rs#repair_pytorch_via_pip`
  - `src-tauri/src/main.rs#restart_sidecar`
- **What the next session should fix:** see `09-architecture-end-to-end.md` §7
  item #2. A pre-emptive AV exclusion at install time (NSIS post-install
  hook) would close this fully so the user never has to click anything.
- **See:** `05-case-studies.md` Bug #11.

### "uvicorn entry point not found" / `importlib.metadata.PackageNotFoundError`

The build pipeline stripped `*.dist-info/` directories to save
installer size. A subset of runtime callers (uvicorn's CLI,
`importlib.metadata.version()`, anything using entry points) need
those directories present.

- **File:** `scripts/build_pipeline.ps1` — the strip block around
  line 569 must NOT match `*.dist-info`.
- **Fix:** strip only `__pycache__/`, `*.pyc`, `*.pyi` (truly
  auto-generated). Keep everything else pip installed.
- **See:** `05-case-studies.md` Bug #10.

### `No module named 'uvicorn'` on a machine where numpy/cv2 import fine, with two `torch` trees

Distinct from the "uvicorn entry point" bug above (that ships a broken
zip). Here the shipped zip is fine — the build's **mandatory** runtime
integrity check (`build_pipeline.ps1`, `import fastapi, uvicorn` +
dist-info asserts) cannot pass otherwise — but the *per-user* runtime at
`%LOCALAPPDATA%\com.bot.mmorpg.ai\runtime\py\python\` has drifted into a
mixed state.

**Distinguishing signals** (all present in issue #85):

- `numpy` and `cv2` import OK, but `uvicorn` is *entirely* missing and
  `fastapi` fails on a transitive dep (`typing_inspection`).
- The runtime doctor's `torch_dlls` row warns **"2 torch trees on
  sys.path"**: `...\site-packages\torch` **and**
  `...\Lib\site-packages\torch`.
- The sidecar's `PYTHONPATH` (in the debug bundle's Environment block)
  lists `...\runtime\py\python\site-packages` but **not**
  `...\runtime\py\python\Lib\site-packages`.

**Root cause.** The build installs deps with `pip --target site-packages`
(a flat `site-packages`), and the Rust supervisor puts exactly that
directory on the sidecar's `PYTHONPATH`. But every pip-based repair —
including the app's own **Repair PyTorch via pip** — installs into the
interpreter's *standard* `Lib\site-packages`. Anything a repair (re)installs
lands in a directory the sidecar never added, so a repaired `uvicorn`/
`torch` is invisible to it even though it is on disk. That is why the
user's repeated Repair Runtime / Repair PyTorch clicks never recovered
the sidecar.

- **File:** `backend/entry_main.py` (`_bootstrap_site_packages`).
- **Fix:** the sidecar now appends **both** `<prefix>\site-packages` and
  `<prefix>\Lib\site-packages` (derived from `sys.prefix`/
  `sys.executable`) to `sys.path` at startup, so it finds its own
  installed packages regardless of which location a repair used and
  regardless of the supervisor-supplied `PYTHONPATH`. Guarded by
  `test_backend_startup.py::TestSidecarSitePackagesBootstrap`.
- **Still needed on the AV axis:** the broken `torch` in this bundle
  (missing `torch/lib/`, `torch._strobelight`) is the separate
  AV-quarantine problem — see the `torch.testing` AV entry above. The
  path fix makes a *successful* pip-repair actually take effect; it does
  not stop AV from re-quarantining torch. Add the AV exclusion first.
- **End-user recovery (no rebuild), simplest first:**
  1. Fully delete `%LOCALAPPDATA%\com.bot.mmorpg.ai\runtime`, then
     relaunch — the app re-extracts a clean runtime with no stale
     second tree.
  2. Or reinstall the backend deps into the bundled interpreter:
     ```powershell
     & "$env:LOCALAPPDATA\com.bot.mmorpg.ai\runtime\py\python\python.exe" `
       -m pip install --upgrade fastapi "uvicorn[standard]"
     ```

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

### Sidecar dies at import with `TypeError: Unable to evaluate type annotation '... | None'`

A FastAPI route parameter used a PEP 604 union (`Dict[str, Any] | None`),
which only parses on Python 3.10+. `from __future__ import annotations`
does not defer it: FastAPI evaluates route annotations when the route is
registered, so it just becomes a string FastAPI must `eval`. The failure
takes down `create_app()` — the whole backend, not one endpoint — on any
interpreter older than 3.10.

- **File:** `modelhub/tauri.py` (route signatures)
- **Fix:** use `Optional[...]` in route parameters. Only affects Python
  3.9 and older, so the shipped bundle (3.10/3.11) never showed it while
  a dev checkout on 3.9 could not start the backend at all.
- **Guardrail:** `tests/test_issue_81_82_regressions.py::
  test_sidecar_routes_avoid_python_310_only_annotations` parses every
  route signature, so this holds on interpreters that would accept it.

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

### "Recording saved" but no dataset appears in the Train tab

The Rust shell spawns `1-collect_data.py` with
`--out <data_root>/datasets/<gid>/<name>` so the recording lands where
`modelhub/tauri.py::_scan_datasets_fs` looks. The **legacy**
`versions/0.01/1-collect_data.py` had no argument parser, so it ignored
`--out` entirely and wrote to a bare `datasets/` folder (driven only by
`BOTMMO_OUTPUT_DIR`). Result: recording "succeeds" but the file lands
outside `datasets/<gid>/` and never shows up in the UI.

- **File:** `versions/0.01/1-collect_data.py` (`_resolve_output_dir`)
- **Fix:** parse `--out` (with `parse_known_args` so future flags don't
  crash the recorder) and use it as the output dir, falling back to
  `BOTMMO_OUTPUT_DIR` then the default. Keeps the writer, the session
  bookkeeping, and `_scan_datasets_fs` all pointed at the same path.
- **Issues:** #57, #60, #63, #65.

### Training crash: `Target size (... 39) must be the same as input size (... 29)`

`BCEWithLogitsLoss` failed in `2-train_model.py` because the dataset's
action vector was 39 wide (29 keyboard+gamepad **plus** 10 mouse values
when mouse recording is on) while the model's output head was hard-sized
to 29 via the `--num-actions` default.

- **File:** `versions/0.01/2-train_model.py` (`GameplayDataset.num_actions`,
  `main()` head-size resolution)
- **Fix:** auto-detect the head size from the dataset
  (`self.actions.shape[1]`) and default `--num-actions` to `0` (auto). A
  positive `--num-actions` still overrides for advanced use. The model
  head now always matches the recorded action width (29 or 39).
- **Issue:** #64.

### Run Bot fails: `size mismatch for action_head.3.weight ... torch.Size([39, 256]) ... torch.Size([29, 256])`

The mirror image of #64, on the inference side. Training now sizes the
head to the dataset (39 with mouse recording on), but `load_model()`
rebuilt the architecture with its 29-action default and then tried to
load 39-wide weights into it, so the job died at model load.

- **File:** `versions/0.01/models_pytorch.py` and
  `src/bot_mmorpg/scripts/models_pytorch.py` (`load_model`,
  `save_model`, `infer_num_actions`), plus
  `versions/0.01/3-test_model.py` (action-weight sizing)
- **Fix:** `save_model` records `num_actions`; `load_model` takes the
  width from the checkpoint — metadata first, else inferred by diffing
  the stored weights against a probe model, which also recovers
  checkpoints from older builds — and returns it in the metadata so the
  inference engine sizes its action-weight table to match.
- **Issue:** #82.

### Preview pane stuck on "No Preview yet" / "screen capture won't capture my screen"

`get_screen_preview` in `src-tauri/src/main.rs` forwards to the sidecar's
`POST /capture/preview`, but that route was never defined in
`modelhub/tauri.py`. Every request 404'd, the UI's catch block left the
placeholder up, and nothing reached the log — indistinguishable from a
preview nobody had started.

- **File:** `modelhub/tauri.py` (`/capture/preview`, `/capture/monitors`,
  `_import_grabscreen`), `tauri-ui/main.js` (`updatePreviewImageTauri`)
- **Fix:** implement both routes. `_import_grabscreen` resolves the
  capture module across all three layouts — installed package, dev
  src-layout checkout, and the shipped bundle, which ships
  `resources/versions/0.01/grabscreen.py` but no `src/` tree. The UI now
  logs the backend's error + hint instead of staying silent.
- **Issue:** #57, #81.

### Capture is blurry, cropped, or empty on a 4K / scaled display

A process that has not declared DPI awareness gets a virtualized desktop
from Win32: `GetSystemMetrics` reports the scaled size and `BitBlt`
returns a DWM-rescaled copy. Lowering the display resolution never
helped because *scaling*, not resolution, triggers the virtualization.

- **File:** `src/bot_mmorpg/scripts/grabscreen.py` and its
  `versions/0.01/` twin (`enable_dpi_awareness`, `_grab_screen_win32`)
- **Fix:** declare per-monitor-v2 DPI awareness at import (falling back
  down the Win8.1 / Vista chain), tolerate GDI's padded scanlines
  instead of reshaping blindly, and fall back to `mss` when a BitBlt
  comes back blank or throws.
- **Issue:** #81, #8.

### Training dies with a CUDA out-of-memory dump, or the GPU is slower than the CPU

The shipped trainer ran a fixed batch size in fp32 with no OOM handling,
so an 8 GB card died mid-epoch and a card that survived trained slower
than CPU for lack of mixed precision.

- **File:** `versions/0.01/2-train_model.py` (`autotune_batch_size`,
  `train_epoch`)
- **Fix:** fit the batch size to the detected VRAM, enable AMP (and
  gradient checkpointing on small cards), and skip an out-of-memory
  batch instead of aborting — stopping with an actionable
  `--batch-size N` message only if OOM keeps repeating. `--no-autotune`
  keeps a hand-picked batch size.
- **Issue:** #27.

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
