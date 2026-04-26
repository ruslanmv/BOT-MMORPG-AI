import json
import unittest
from pathlib import Path

# Paths
ROOT = Path(__file__).resolve().parents[1]
UI_HTML = ROOT / "tauri-ui" / "index.html"
UI_JS = ROOT / "tauri-ui" / "main.js"
TAURI_CONF = ROOT / "src-tauri" / "tauri.conf.json"
NSIS_TEMPLATE = ROOT / "installer" / "nsis_template.nsi"


class TestTauriUI(unittest.TestCase):
    # REMOVED: test_no_inline_onclick
    # Reason: The current UI design intentionally uses inline handlers (e.g. onclick="toggleRecord()")
    # which are permitted by the 'unsafe-inline' CSP policy in tauri.conf.json.

    def test_nav_has_data_tabs(self):
        """Ensure navigation buttons have data-tab attributes for JS routing."""
        if not UI_HTML.exists():
            self.skipTest("HTML not found")
        html = UI_HTML.read_text(encoding="utf-8", errors="replace")
        for tab in ("dashboard", "teach", "train", "run", "strategist"):
            self.assertIn(f'data-tab="{tab}"', html, f"Missing data-tab for {tab}")

    def test_main_js_no_tauri_imports(self):
        """Ensure we use window.__TAURI__ instead of node imports."""
        if not UI_JS.exists():
            self.skipTest("JS not found")
        js = UI_JS.read_text(encoding="utf-8", errors="replace")
        self.assertNotIn(
            "@tauri-apps/api", js, "main.js still imports npm @tauri-apps/api"
        )

    def test_main_js_has_event_listeners(self):
        """Ensure JS attaches event listeners (wireEvents or standard listeners)."""
        if not UI_JS.exists():
            self.skipTest("JS not found")
        js = UI_JS.read_text(encoding="utf-8", errors="replace")
        # Check for standard event attachment
        self.assertIn("addEventListener", js, "main.js missing addEventListener logic")

    def test_nsis_template_uses_canonical_define_pattern(self):
        """Ensure NSIS template uses the canonical Tauri 1.6 !define pattern.

        Background: previous revisions of this template inlined
        ``$INSTDIR\\\\{{main_binary_name}}.exe`` everywhere and relied on
        Rust handlebars to render the double-escaped backslash literally.
        That worked but had two latent bugs:

        1. The handlebars var ``{{main_binary_name}}`` is derived from
           Cargo.toml's ``name`` field (lowercase ``bot-mmorpg-ai``), not
           from ``productName`` (``BOT-MMORPG-AI``). Shortcuts and
           registry keys silently rendered the wrong case.
        2. Inlining ``{{main_binary_path}}`` directly into a quoted ``File``
           argument passes raw Windows paths through handlebars without
           ``unescape-dollar-sign`` and produces strings NSIS parses
           oddly (a ``$`` in the build path is read as a NSIS variable).

        The canonical tauri-v1.6.6 ``installer.nsi`` (lines 29-30, 541-542)
        solves both with a two-step indirection:

            !define MAINBINARYNAME "BOT-MMORPG-AI"
            !define MAINBINARYSRCPATH "{{main_binary_path}}"
            File "/oname=${MAINBINARYNAME}.exe" "${MAINBINARYSRCPATH}"

        This test enforces that pattern so we cannot regress to the
        inlined form.
        """
        if not NSIS_TEMPLATE.exists():
            self.skipTest("NSIS not found")
        nsi = NSIS_TEMPLATE.read_text(encoding="utf-8", errors="replace")

        # (1) Canonical defines must be present.
        self.assertIn(
            "!define MAINBINARYNAME",
            nsi,
            "Missing !define MAINBINARYNAME (canonical Tauri 1.6 pattern)",
        )
        self.assertIn(
            '!define MAINBINARYSRCPATH "{{main_binary_path}}"',
            nsi,
            "Missing !define MAINBINARYSRCPATH for the bundler-injected path",
        )

        # (2) The main File directive must consume the defines, not
        # inline the handlebars vars.
        self.assertIn(
            'File "/oname=${MAINBINARYNAME}.exe" "${MAINBINARYSRCPATH}"',
            nsi,
            "Main File directive must use the !define indirection",
        )

        # (3) Regression guard: no inlined {{main_binary_name}} or
        # {{main_binary_path}} anywhere except the single
        # MAINBINARYSRCPATH define line. Anything else means a future
        # contributor reintroduced the bug class.
        for var_name in ("main_binary_name", "main_binary_path"):
            handlebars_var = "{{" + var_name + "}}"
            for line_no, line in enumerate(nsi.splitlines(), start=1):
                if handlebars_var not in line:
                    continue
                # The MAINBINARYSRCPATH define line is the ONE allowed
                # use of {{main_binary_path}}.
                if (
                    var_name == "main_binary_path"
                    and "!define MAINBINARYSRCPATH" in line
                ):
                    continue
                # Comments are fine; they document the pattern.
                stripped = line.lstrip()
                if stripped.startswith(";"):
                    continue
                self.fail(
                    f"Inlined handlebars var {{{{{var_name}}}}} found at "
                    f"line {line_no}: {line!r}. Use ${{MAINBINARYNAME}} or "
                    f"${{MAINBINARYSRCPATH}} via the !define pattern."
                )

    def test_csp_has_script_src(self):
        """Ensure Tauri conf has CSP defined."""
        if not TAURI_CONF.exists():
            self.skipTest("Conf not found")
        conf = json.loads(TAURI_CONF.read_text(encoding="utf-8", errors="replace"))
        csp = conf.get("tauri", {}).get("security", {}).get("csp", "")
        self.assertIn("script-src", csp, "CSP missing script-src")


if __name__ == "__main__":
    unittest.main()
