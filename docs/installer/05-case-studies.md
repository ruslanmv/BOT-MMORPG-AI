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
{% endraw %}
