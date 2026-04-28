# 05 — Case Studies

{% raw %}
Worked examples of the bugs fixed on the
`claude/verify-directory-structure-DLUt1` branch. Read these to learn
the failure modes and the right way to fix them.

## Bug #1 — `resources_dirs` block removed but it was needed

**Commit:** `94196b4` (initially wrong fix; corrected later by `943f9f8`)

**Symptom:** install dialog showed `Create folder: C:\Program Files\BOT-MMORPG-AI{{this}}` 5 times.

**First (wrong) hypothesis:** `resources_dirs` is a Tauri 2.x-only
variable, undefined in 1.x, so the loop was bogus and should be removed.

**What was actually wrong:** the loop is fine in Tauri 1.x —
`tauri-bundler 1.7.4` exposes `resources_dirs` as a `HashSet<PathBuf>`.
The bug was the escape rule (Bug #3).

**Lesson:** always verify variable existence by looking at the bundler's
canonical template before removing a loop. The canonical 1.x template at
`github.com/tauri-apps/tauri/blob/1.x/tooling/bundler/src/bundle/windows/templates/installer.nsi`
uses both loops.

## Bug #2 — Handlebars syntax error from comment block

**Commit:** `8fed9a1`

**Symptom:**
```
Failed to setup custom handlebar template: invalid handlebars syntax
    --> Template error in installer.nsi:384:1
```

**Cause:** the doc-comment in the template included literal
`{{#if resources_dirs}}` and `{{#each resources_dirs}}` text as illustration.
NSIS treats `;` as a line-comment marker, but `tauri-bundler` runs
`handlebars-rust` on the **whole file** before NSIS sees it. The
illustrative tokens were parsed as real block-opens with no matching closes;
handlebars hit EOF with unbalanced state and aborted.

**Fix:** rewrote the comment in plain prose with zero `{{...}}` literals.

**Lesson:** never put double-curly tokens inside an NSIS comment. If
you want to refer to handlebars expressions in docs, use words ("the
each-loop", "the if-block"), not the literal syntax.

## Bug #3 — `\{{` is the handlebars escape, not a path separator

**Commit:** `943f9f8` (the real installer fix)

**Symptom:** same as Bug #1, but persistent after the first attempt.
The rendered NSIS contained literal `{{this.[0]}}` text in
`CreateDirectory` lines.

**Cause:** in handlebars-rust, `\{{` is the escape sequence for a
literal `{{` in the output (it suppresses expression parsing).
The template had:

```nsi
CreateDirectory "$INSTDIR\{{this.[0]}}"
```

Handlebars saw `\{{` and emitted the literal `{{` to the output, leaving
`this.[0]}}` as plain text. NSIS then created folders literally named
`{{this.[0]}}`.

**Fix:** every NSIS path string with handlebars now uses double backslash
(`\\{{...}}`):

```nsi
CreateDirectory "$INSTDIR\\{{this}}"
File /a "/oname={{this.[1]}}" "{{unescape-dollar-sign @key}}"
```

`\\` renders to a single `\`, then `{{...}}` is parsed normally.
Confirmed against the upstream Tauri 1.x canonical template.

**Lesson:** when handlebars expressions appear inside NSIS strings,
double-escape every `\` that precedes `{{`. The
`tests/test_tauri_production_readiness.py::test_nsis_template_has_correct_escaping`
test now enforces this invariant.

## Bug #4 — Resolver missed the `resources/` prefix

**Commit:** `964e7c8`

**Symptom:** after the installer was fixed, every Run Bot / Train / Record
attempt failed with `Script '<X>.py' not found` listing four wrong paths.
Files were definitely on disk under `$INSTDIR\resources\versions\0.01\`,
but the resolver looked at `$INSTDIR\versions\0.01\`.

**Cause:** Tauri 1.x's `resources: ["resources/**"]` glob preserves the
`resources/` prefix on extraction. The Rust code passed
`resolve_resource("backend/entry_main.py")` without the prefix, so the
resolver returned `$INSTDIR\backend\entry_main.py` (which doesn't exist).

**Fix:** three call sites in `main.rs` updated:
- `start_sidecar_server`: `resolve_resource("resources/backend/entry_main.py")`
- ...the modelhub PYTHONPATH lookup: `resolve_resource("resources/modelhub")`
- `resolve_script`: added `$INSTDIR\resources\versions\<ver>\<name>` as
  the **first** probe candidate (kept legacy fallbacks for users with
  manual workaround copies).

**Lesson:** when Tauri's resource glob has a prefix, every
`resolve_resource("...")` call must include that prefix. The
diagnostic in `06-debug-tools.md` checks both layers and tells you which
side is wrong.

## Bug #5 — PowerShell driver path resolution wrong in PROD

**Commit:** `9d8a16f`

**Symptom:** Install Drivers button → UAC prompt → "Missing file" error
referencing `C:\Program Files\BOT-MMORPG-AI\resources\drivers\…` — a
folder that doesn't exist.

**Cause:** the bundled script lives at
`$INSTDIR\resources\scripts\install_drivers.ps1`. The script computed:

```powershell
$root = Split-Path -Parent $PSScriptRoot     # ...\resources
$driversDir = Join-Path $root "drivers"      # ...\resources\drivers (wrong)
```

But the bundler's `drivers/**` glob keeps the `drivers\` folder at
**install root**, not under `resources\`.

**Fix:** probe three candidates in order:
```powershell
$candidates = @(
    "$PSScriptRoot\..\..\drivers",        # PROD: install_dir\drivers (correct)
    "$PSScriptRoot\..\src-tauri\drivers", # DEV:  repo\src-tauri\drivers
    "$PSScriptRoot\..\drivers"            # legacy fallback
)
```

**Lesson:** the build pipeline copies `scripts/install_drivers.ps1` to
`src-tauri/resources/scripts/install_drivers.ps1` at build time — but
the canonical version in `scripts/` is the one that ships. Edit there.

## Bug #6 — `start_bot` didn't pass `--model`

**Commit:** `4e16d1b`

**Symptom:** Run Bot button click → instant failure with no log.

**Cause:** `versions/0.01/3-test_model.py:502` declares
`parser.add_argument("--model", required=True, ...)`, but
`start_bot` in Rust spawned the script with no args:

```rust
fn start_bot(...) -> Result<String, String> {
    run_python_script(app, "3-test_model.py", window, state.inner.clone())
}
```

Every click since the script switched to PyTorch silently failed with
`argparse: the following arguments are required: --model`.

**Fix:** `start_bot` now hits the sidecar's
`/modelhub/catalog?game_id=<gid>` endpoint, extracts the
`active.model_dir` field, and forwards `--model <path>` to the script.
If no active model: returns a clear error message instead of spawning.
Frontend gates the button on the same condition with
`refreshRunBotGate()`.

**Lesson:** when a Python script declares required CLI args, the Rust
caller must pass them. Add an integration test that round-trips
through `start_bot` to catch this class of bug.

## Bug #7 — External `<a target="_blank">` links inert

**Commit:** `3d98b3d`

**Symptom:** "Star on GitHub", "Download Latest Installer", "Update Now",
"View Patch Notes" links all did nothing in the installed app.

**Cause:** Tauri 1.x's webview silently drops `<a target="_blank">`
navigation by default.

**Fix:** one delegated click handler in `tauri-ui/index.html` that catches
every `<a target="_blank">` click and routes it through
`window.__TAURI__.shell.open()` (already permitted via
`tauri.conf.json :: shell.open: true`).

**Lesson:** Tauri webview link handling is opt-in. Either use a global
interceptor (cheap) or `shell.open()` per-link.

## Bug #8 — `hidden` attribute didn't actually hide cards

**Commit:** `104adae`

**Symptom:** clicking the X / Later buttons on banners ran the JS
correctly (`banner.hidden = true`), but the banner stayed on screen.

**Cause:** the HTML `hidden` attribute hides via the user-agent rule
`[hidden] { display: none }`. Our `.notification-card { display: flex }`
was declared later and won on cascade order, so `hidden` set the
attribute but `display: flex` kept the element rendered.

**Fix:** one CSS rule:

```css
[hidden] { display: none !important; }
```

Re-asserts `hidden`'s semantic above every per-component `display` rule.

**Lesson:** any class that sets explicit `display: <anything>` will
override the UA `[hidden]` rule. Either use `!important` once globally
(this fix), or write `.my-class[hidden] { display: none }` for every
class — the global rule is much less maintenance.

## Bug #9 — Prune rule deleted `torch/testing/` from bundled site-packages

**Symptom (in-app log on a fresh `0.0.0-dev` install):**

```
[Warning] PyTorch failed to import:
  ModuleNotFoundError: No module named 'torch.testing'
[Error] PyTorch not available -- training cannot start.
[System] Process finished: exit_code=-1073741819     # 0xC0000005
```

The trainer fails BEFORE it does any work. The exit code is a
Windows access violation, not a clean Python `sys.exit(1)`.

**Cause:** `scripts/build_pipeline.ps1` had a regex that pruned
unit-test directories from the bundled site-packages to keep the
NSIS file count under the ~30k cliff:

```powershell
Where-Object { $_.Name -match "^(tests?|testing)$" }
```

That pattern matches three names: `test`, `tests`, AND `testing`.
The third match deleted **public, runtime-required submodules** of
mainstream scientific-Python wheels:

- `torch/testing/` — `assert_close`, `make_tensor`; transitively
  imported by `torch._dynamo`, `torch.fx`, several modelhub model
  registries.
- `numpy/testing/` — imported transitively by torch on some
  platforms during init.
- `pandas/testing/`, `scipy/testing/`, `sympy/testing/` — collateral.

The 0xC0000005 follows the `ModuleNotFoundError`: native extensions
in `torch._C` finished registering C++ globals, then Python caught
the import error and started cleanup. During shutdown the half-
initialized extensions raced against a `sys.modules` that no
longer references `torch.testing` and crashed with a teardown-phase
access violation.

The build's pre-prune torch smoke test passed (the package was still
intact at that point). No post-prune smoke test existed, so a green
CI build shipped a corrupted installer to users.

**Fix:** two changes in `scripts/build_pipeline.ps1`:

1. Tighten the prune filter to plural-only:

   ```powershell
   Where-Object { $_.Name -ieq "tests" }
   ```

   `tests/` (plural) is the strong convention for unit-test
   directories specifically; the singular `test/` and `testing/`
   are runtime API surface for several scientific packages.

2. Add a post-prune integrity check that runs the bundled
   `python.exe` against an explicit list of imports the runtime
   actually performs:

   ```powershell
   $postPruneTests = @(
     "import torch, torch.testing, torch.nn, torch.fx",
     "import torchvision",
     "import numpy, numpy.testing",
     "import fastapi, uvicorn",
     "import cv2",
   )
   ```

   This converts a runtime crash on the user's machine into a
   build-time failure on CI. If you change the prune rules, add
   the corresponding `import x.y` line.

3. Regression test at `tests/health/test_bundled_site_packages_intact.py`
   asserts the same submodules exist on a built/installed copy, so
   `make verify` / `verify_installer.ps1` catches the same class
   of regression locally.

**Lesson:** "size optimization" passes that delete files by name
pattern are dangerous. The `tests/` (plural) convention is real and
worth honoring; `test/` and `testing/` (singular) are NOT
test-suite conventions — they are public API directories in the
science-Python ecosystem. When you must prune, prune by **explicit
manifest of files known to be safe to drop**, not by directory-name
regex. Always smoke-test what the user will actually import, AFTER
every destructive build step.

## Bug #10 — Prune block was no longer load-bearing

**Symptom:** none observed in the wild — caught proactively while
auditing the build pipeline for MVP-4.

**Cause:** the original prune block (Bug #9 above) existed because
NSIS has a hard cliff around 30k bundled files. STEP 6.7 of the
build pipeline already packs the whole `python/` tree into a single
`python-runtime.zip`, so NSIS sees ONE file regardless of how many
files are inside the zip. The prune block was therefore deleting
files for size savings only — and any future rule change carried
the same risk profile as Bug #9 (accidentally remove a runtime
submodule, ship a corrupted installer, learn about it from a user
crash report).

The high-risk strips that remained:

- `tests/` (plural) — already proven safe by Bug #9, but no
  longer load-bearing once the zip carries the file-count.
- `*.dist-info/` — required at runtime by `importlib.metadata`
  and by entry-point lookup (uvicorn's CLI). Removing them on
  some wheel layouts produces "uvicorn entry point not found"
  failures that are extremely hard to attribute back to the
  build pipeline.

**Fix:** drop both strips in `scripts/build_pipeline.ps1`. Keep
only the auto-generated artifact strips (`__pycache__`, stray
`.pyc`, `.pyi` type stubs) — those have zero failure surface
because CPython auto-regenerates them on import.

The runtime integrity check (introduced in Bug #9) is renamed
from "post-prune" to "runtime integrity" and gains an extra
`importlib.metadata.version()` assertion to lock in the
dist-info preservation.

**Size impact:** modest installer growth (the zip already
compresses redundancy heavily). If size becomes a concern again,
the AAA-grade fix is to upgrade the zip compressor from DEFLATE
to LZMA2 (~30% smaller bundle), not to delete files pip
installed.

**Lesson:** prune rules are technical debt with negative ROI
once they're not load-bearing. Audit the assumptions every time
the build pipeline changes shape.

## Bug #11 — `torch/testing` deleted by AV after a clean extract

**Commits:** `52dae2e` (doctor enrichment), `3ea14a1` (`repair_pytorch_via_pip`).

**Symptom (in-the-wild user report after MVP-4 was already shipped):**

```
Runtime doctor: error
torch_intact: ERR  ModuleNotFoundError: No module named 'torch.testing' |
                   torch_root=C:\Users\<u>\AppData\Local\com.bot.mmorpg.ai\runtime\py\python\site-packages\torch |
                   torch_testing_dir_exists=False
numpy_intact: ERR  ModuleNotFoundError: No module named 'numpy.testing' |
                   numpy_root=C:\Users\<u>\AppData\Local\com.bot.mmorpg.ai\runtime\py\python\site-packages\numpy |
                   numpy_testing_dir_exists=False
torchvision_intact: ERR cannot import name 'nn' from partially initialized
                   module 'torch' (most likely due to a circular import)
```

The build pipeline's runtime-integrity check (added in Bug #10) had
PASSED at build time — `torch.testing` was inside `python-runtime.zip`
when the build finished. So the directory got deleted **between
extraction to `%LOCALAPPDATA%` and the doctor's first probe**.

**Cause:** Defender real-time scan running on a freshly-extracted
unsigned package directory. AV products typically delete specific
binaries / directories that match a heuristic. Two `testing/` dirs
vanishing in lockstep across two unrelated packages is the classic
signature: not random, not zip corruption, an external actor.

**Distinguishing this from Bug #9:** the diagnostic enrichment in
`52dae2e` makes this trivial. Bug #9 (build-time): `torch_root` is
sentinel-string "<not found on sys.path>" because torch was never
installed. Bug #11 (runtime AV): `torch_root` resolves to a real
directory but `torch_testing_dir_exists=False`. The boolean is the
smoking gun.

**Fix:** none in code — this is a runtime state issue. The recovery
flow is in-product:

1. `[🛡 Add AV Exclusion]` → UAC → Defender excludes
   `%LOCALAPPDATA%\com.bot.mmorpg.ai\runtime\py\`.
2. `[🔧 Repair Runtime]` → re-extracts `python-runtime.zip` into the
   now-excluded directory; AV gives it a pass.
3. `[↻ Restart Sidecar]` and `[▶ Run Diagnosis]` to verify.

If steps 1+2 don't restore the directory (the bundled zip itself
is from a pre-MVP-4 build that never had `torch/testing/` to begin
with):

4. `[🩺 Repair PyTorch (pip)]` → downloads fresh `torch +
   torchvision + numpy` from PyPI's CPU index, force-reinstalling
   without dependencies. 2-5 min, ~250 MB. Bypasses both the bundled
   zip AND any persistent AV interference (pip writes to a temp
   dir then atomic-renames, which most AV products give a pass).

**Lesson:** AV-quarantine of fresh extracts is a real failure class
that no amount of build-side hardening can prevent. The complete fix
is a **pre-emptive AV exclusion at install time** — an NSIS post-
install hook that runs `Add-MpPreference -ExclusionPath` (with a
consent checkbox in the wizard) so the user never has to click any
recovery button. Tracked in `09-architecture-end-to-end.md` §7
item 2 as the primary deferred work item for the next session.
{% endraw %}
