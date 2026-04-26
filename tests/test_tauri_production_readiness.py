"""
Tauri Production Readiness Tests

Validates that the Tauri desktop application is ready for release to gamers.
Covers: build configuration, UI assets, security, Rust source integrity,
and feature parity with the Eel-based launcher.

All tests are non-destructive and additive - they only read and verify.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

# Add src to path for optional bot_mmorpg imports
SRC_PATH = str(ROOT / "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

try:
    from bot_mmorpg.bridge.handlers import CommandHandler  # noqa: F401

    BRIDGE_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    BRIDGE_AVAILABLE = False

requires_bridge = pytest.mark.skipif(
    not BRIDGE_AVAILABLE,
    reason="bot_mmorpg.bridge.handlers not importable (missing torch or package)",
)

TAURI_DIR = ROOT / "src-tauri"
TAURI_CONF = TAURI_DIR / "tauri.conf.json"
CARGO_TOML = TAURI_DIR / "Cargo.toml"
MAIN_RS = TAURI_DIR / "src" / "main.rs"
UI_DIR = ROOT / "tauri-ui"
UI_HTML = UI_DIR / "index.html"
UI_JS = UI_DIR / "main.js"
LAUNCHER_PY = ROOT / "launcher" / "launcher.py"


# ---------------------------------------------------------------------------
# Build Configuration
# ---------------------------------------------------------------------------
class TestBuildConfiguration:
    """Verify Tauri build configuration is production-ready."""

    def test_tauri_conf_exists(self):
        """tauri.conf.json must exist."""
        assert TAURI_CONF.exists()

    def test_tauri_conf_valid_json(self):
        """tauri.conf.json must be valid JSON."""
        conf = json.loads(TAURI_CONF.read_text(encoding="utf-8"))
        assert isinstance(conf, dict)

    def test_product_name_set(self):
        """Product name must be set for installer."""
        conf = json.loads(TAURI_CONF.read_text(encoding="utf-8"))
        name = conf.get("package", {}).get("productName", "")
        assert name == "BOT-MMORPG-AI"

    def test_version_set(self):
        """Version must be set (semver)."""
        conf = json.loads(TAURI_CONF.read_text(encoding="utf-8"))
        version = conf.get("package", {}).get("version", "")
        parts = version.split(".")
        assert len(parts) == 3, f"Version must be semver: {version}"
        assert all(p.isdigit() for p in parts)

    def test_window_dimensions_suitable_for_gaming(self):
        """Window size must be large enough for gaming UI."""
        conf = json.loads(TAURI_CONF.read_text(encoding="utf-8"))
        windows = conf.get("tauri", {}).get("windows", [])
        assert len(windows) >= 1

        main_window = windows[0]
        assert main_window.get("width", 0) >= 1200, "Window too narrow for gaming UI"
        assert main_window.get("height", 0) >= 800, "Window too short for gaming UI"
        assert main_window.get("resizable", False) is True

    def test_bundle_category_is_game(self):
        """Bundle category must be 'Game' for app stores."""
        conf = json.loads(TAURI_CONF.read_text(encoding="utf-8"))
        category = conf.get("tauri", {}).get("bundle", {}).get("category", "")
        assert category == "Game"

    def test_bundle_identifier_set(self):
        """Bundle identifier must be set (reverse domain)."""
        conf = json.loads(TAURI_CONF.read_text(encoding="utf-8"))
        ident = conf.get("tauri", {}).get("bundle", {}).get("identifier", "")
        assert "." in ident, f"Identifier must be reverse-domain: {ident}"

    def test_nsis_installer_configured(self):
        """NSIS installer must be configured for Windows distribution."""
        conf = json.loads(TAURI_CONF.read_text(encoding="utf-8"))
        targets = conf.get("tauri", {}).get("bundle", {}).get("targets", [])
        assert "nsis" in targets, "NSIS must be a bundle target"

    def test_icons_configured(self):
        """Application icons must be configured."""
        conf = json.loads(TAURI_CONF.read_text(encoding="utf-8"))
        icons = conf.get("tauri", {}).get("bundle", {}).get("icon", [])
        assert len(icons) >= 1, "At least one icon must be configured"

    def test_cargo_toml_exists(self):
        """Cargo.toml must exist for Rust compilation."""
        assert CARGO_TOML.exists()

    def test_cargo_dependencies_complete(self):
        """Cargo.toml must have all required dependencies."""
        content = CARGO_TOML.read_text(encoding="utf-8")
        required_deps = ["tauri", "serde", "serde_json", "reqwest", "tokio"]
        for dep in required_deps:
            assert dep in content, f"Missing Cargo dependency: {dep}"

    def test_with_global_tauri_enabled(self):
        """withGlobalTauri must be true for __TAURI__ window API."""
        conf = json.loads(TAURI_CONF.read_text(encoding="utf-8"))
        wgt = conf.get("build", {}).get("withGlobalTauri", False)
        assert wgt is True, "withGlobalTauri must be true for window.__TAURI__"


# ---------------------------------------------------------------------------
# Security Configuration
# ---------------------------------------------------------------------------
class TestSecurityConfiguration:
    """Verify security settings protect gamers."""

    def test_csp_defined(self):
        """Content Security Policy must be defined."""
        conf = json.loads(TAURI_CONF.read_text(encoding="utf-8"))
        csp = conf.get("tauri", {}).get("security", {}).get("csp", "")
        assert len(csp) > 0, "CSP must be defined"

    def test_csp_has_script_src(self):
        """CSP must restrict script sources."""
        conf = json.loads(TAURI_CONF.read_text(encoding="utf-8"))
        csp = conf.get("tauri", {}).get("security", {}).get("csp", "")
        assert "script-src" in csp, "CSP must define script-src"

    def test_csp_has_default_src(self):
        """CSP must have default-src restriction."""
        conf = json.loads(TAURI_CONF.read_text(encoding="utf-8"))
        csp = conf.get("tauri", {}).get("security", {}).get("csp", "")
        assert "default-src" in csp, "CSP must define default-src"

    def test_freeze_prototype_enabled(self):
        """Prototype freezing should be enabled for security."""
        conf = json.loads(TAURI_CONF.read_text(encoding="utf-8"))
        freeze = conf.get("tauri", {}).get("security", {}).get("freezePrototype", False)
        assert freeze is True, "freezePrototype should be true"

    def test_fs_scope_restricted(self):
        """Filesystem access must be scoped (not wildcard)."""
        conf = json.loads(TAURI_CONF.read_text(encoding="utf-8"))
        fs = conf.get("tauri", {}).get("allowlist", {}).get("fs", {})
        scope = fs.get("scope", [])
        # Should not allow root access
        for s in scope:
            assert s != "/**", "FS scope must not be root wildcard"
            assert s != "/*", "FS scope must not be root wildcard"

    def test_shell_not_fully_open(self):
        """Shell API must not have 'all' enabled."""
        conf = json.loads(TAURI_CONF.read_text(encoding="utf-8"))
        shell = conf.get("tauri", {}).get("allowlist", {}).get("shell", {})
        assert shell.get("all", True) is False, "Shell 'all' must be false"


# ---------------------------------------------------------------------------
# Rust Source Integrity
# ---------------------------------------------------------------------------
class TestRustSourceIntegrity:
    """Verify Rust source code is production-quality."""

    def test_main_rs_exists(self):
        """main.rs must exist."""
        assert MAIN_RS.exists()

    def test_main_rs_has_all_three_phase_commands(self):
        """main.rs must register commands for all 3 phases."""
        content = MAIN_RS.read_text(encoding="utf-8")
        assert "start_recording" in content, "Missing start_recording command"
        assert "start_training" in content, "Missing start_training command"
        assert "start_bot" in content, "Missing start_bot command"

    def test_main_rs_has_stop_process(self):
        """main.rs must have stop_process command."""
        content = MAIN_RS.read_text(encoding="utf-8")
        assert "stop_process" in content

    def test_main_rs_registers_all_handlers(self):
        """main.rs must register all required handlers in invoke_handler."""
        content = MAIN_RS.read_text(encoding="utf-8")
        required_handlers = [
            "get_ai_config",
            "save_configuration",
            "start_recording",
            "start_training",
            "start_bot",
            "stop_process",
            "modelhub_is_available",
        ]
        for handler in required_handlers:
            assert handler in content, f"Handler not registered: {handler}"

    def test_main_rs_has_sidecar_management(self):
        """main.rs must manage the Python sidecar process."""
        content = MAIN_RS.read_text(encoding="utf-8")
        assert "start_sidecar_server" in content
        assert "SidecarApi" in content

    def test_main_rs_has_process_cleanup(self):
        """main.rs must clean up processes on exit."""
        content = MAIN_RS.read_text(encoding="utf-8")
        assert "shutdown_all" in content
        assert "CloseRequested" in content or "ExitRequested" in content

    def test_main_rs_has_stable_python_env(self):
        """main.rs must set stable Python environment variables."""
        content = MAIN_RS.read_text(encoding="utf-8")
        assert "PYTHONUNBUFFERED" in content
        assert "PYTHONUTF8" in content

    def test_main_rs_script_resolution_has_fallbacks(self):
        """Script resolution must have multiple fallback paths."""
        content = MAIN_RS.read_text(encoding="utf-8")
        assert "resolve_script" in content
        # Must handle both dev and prod paths
        assert "debug_assertions" in content

    def test_main_rs_windows_subprocess_handling(self):
        """main.rs must handle Windows subprocess creation properly."""
        content = MAIN_RS.read_text(encoding="utf-8")
        assert "CREATE_NO_WINDOW" in content or "creation_flags" in content

    def test_main_rs_has_terminal_events(self):
        """main.rs must emit terminal_update events to frontend."""
        content = MAIN_RS.read_text(encoding="utf-8")
        assert "terminal_update" in content


# ---------------------------------------------------------------------------
# UI Assets
# ---------------------------------------------------------------------------
class TestUIAssets:
    """Verify Tauri UI assets are complete and correct."""

    def test_html_exists(self):
        """index.html must exist."""
        assert UI_HTML.exists()

    def test_js_exists(self):
        """main.js must exist."""
        assert UI_JS.exists()

    def test_html_has_all_navigation_tabs(self):
        """UI must have tabs for all major features."""
        html = UI_HTML.read_text(encoding="utf-8", errors="replace")
        required_tabs = ["dashboard", "teach", "train", "run", "strategist"]
        for tab in required_tabs:
            assert f'data-tab="{tab}"' in html, f"Missing nav tab: {tab}"

    def test_js_uses_tauri_invoke_not_eel(self):
        """main.js must use Tauri invoke, not Eel calls."""
        js = UI_JS.read_text(encoding="utf-8", errors="replace")
        assert "__TAURI__" in js, "Must use window.__TAURI__"
        assert "eel." not in js, "Must not contain eel.* calls"

    def test_js_uses_event_listeners(self):
        """main.js must use addEventListener (not inline handlers)."""
        js = UI_JS.read_text(encoding="utf-8", errors="replace")
        assert "addEventListener" in js

    def test_js_has_recording_controls(self):
        """main.js must have recording start/stop functions."""
        js = UI_JS.read_text(encoding="utf-8", errors="replace")
        assert "toggleRecord" in js or "startRecording" in js or "start_recording" in js

    def test_js_has_training_controls(self):
        """main.js must have training start function."""
        js = UI_JS.read_text(encoding="utf-8", errors="replace")
        assert "trainModel" in js or "startTraining" in js or "start_training" in js

    def test_js_has_bot_controls(self):
        """main.js must have bot start/stop functions."""
        js = UI_JS.read_text(encoding="utf-8", errors="replace")
        assert "toggleBot" in js or "startBot" in js or "start_bot" in js

    def test_js_has_terminal_listener(self):
        """main.js must listen for terminal_update events from Rust."""
        js = UI_JS.read_text(encoding="utf-8", errors="replace")
        assert "terminal_update" in js

    def test_html_has_terminal_element(self):
        """UI must have a terminal/log display element."""
        html = UI_HTML.read_text(encoding="utf-8", errors="replace")
        assert "terminal" in html.lower(), "UI must have a terminal display"


# ---------------------------------------------------------------------------
# Launcher Feature Parity
# ---------------------------------------------------------------------------
class TestLauncherFeatureParity:
    """Verify Tauri version has the same features as the Eel launcher."""

    def test_launcher_exists(self):
        """Eel launcher must exist for comparison."""
        assert LAUNCHER_PY.exists()

    def test_both_have_recording(self):
        """Both Tauri and launcher must support recording."""
        rs = MAIN_RS.read_text(encoding="utf-8")
        py = LAUNCHER_PY.read_text(encoding="utf-8", errors="replace")

        assert "start_recording" in rs
        assert "start_recording" in py

    def test_both_have_training(self):
        """Both Tauri and launcher must support training."""
        rs = MAIN_RS.read_text(encoding="utf-8")
        py = LAUNCHER_PY.read_text(encoding="utf-8", errors="replace")

        assert "start_training" in rs
        assert "start_training" in py

    def test_both_have_bot_execution(self):
        """Both Tauri and launcher must support bot execution."""
        rs = MAIN_RS.read_text(encoding="utf-8")
        py = LAUNCHER_PY.read_text(encoding="utf-8", errors="replace")

        assert "start_bot" in rs
        assert "start_bot" in py

    def test_both_have_stop_process(self):
        """Both Tauri and launcher must support stopping processes."""
        rs = MAIN_RS.read_text(encoding="utf-8")
        py = LAUNCHER_PY.read_text(encoding="utf-8", errors="replace")

        assert "stop_process" in rs
        assert "stop_process" in py

    def test_both_have_ai_config(self):
        """Both Tauri and launcher must support AI configuration."""
        rs = MAIN_RS.read_text(encoding="utf-8")
        py = LAUNCHER_PY.read_text(encoding="utf-8", errors="replace")

        assert "get_ai_config" in rs
        assert "get_ai_config" in py

    def test_both_have_save_configuration(self):
        """Both Tauri and launcher must support saving configuration."""
        rs = MAIN_RS.read_text(encoding="utf-8")
        py = LAUNCHER_PY.read_text(encoding="utf-8", errors="replace")

        assert "save_configuration" in rs
        assert "save_configuration" in py

    def test_both_have_modelhub_integration(self):
        """Both Tauri and launcher must have ModelHub integration."""
        rs = MAIN_RS.read_text(encoding="utf-8")
        py = LAUNCHER_PY.read_text(encoding="utf-8", errors="replace")

        assert "modelhub" in rs.lower()
        assert "modelhub" in py.lower() or "ModelHub" in py

    def test_both_reference_same_scripts(self):
        """Both must call the same Python phase scripts."""
        rs = MAIN_RS.read_text(encoding="utf-8")
        py = LAUNCHER_PY.read_text(encoding="utf-8", errors="replace")

        scripts = ["1-collect_data.py", "2-train_model.py", "3-test_model.py"]
        for script in scripts:
            assert script in rs, f"Tauri missing script ref: {script}"
            assert script in py, f"Launcher missing script ref: {script}"

    def test_both_have_default_game_id(self):
        """Both must use the same default game ID."""
        rs = MAIN_RS.read_text(encoding="utf-8")
        py = LAUNCHER_PY.read_text(encoding="utf-8", errors="replace")

        assert "genshin_impact" in rs
        assert "genshin_impact" in py


# ---------------------------------------------------------------------------
# Bridge / Handlers (Python backend used by Tauri)
# ---------------------------------------------------------------------------
@requires_bridge
class TestBridgeHandlers:
    """Verify the Python bridge handlers work correctly for Tauri."""

    def test_handlers_module_importable(self):
        """bridge.handlers must be importable."""
        from bot_mmorpg.bridge.handlers import CommandHandler

        assert CommandHandler is not None

    def test_handler_ping(self):
        """Ping handler must return ok status."""
        from bot_mmorpg.bridge.handlers import CommandHandler

        handler = CommandHandler()
        result = handler.handle_system_ping()

        assert result["status"] == "ok"
        assert "timestamp" in result

    def test_handler_version(self):
        """Version handler must return version info."""
        try:
            import torch  # noqa: F401
        except ImportError:
            pytest.skip("torch required for version handler")

        from bot_mmorpg.bridge.handlers import CommandHandler

        handler = CommandHandler()
        result = handler.handle_system_get_version()

        assert "app_version" in result
        assert "python_version" in result

    def test_handler_hardware_detection(self):
        """Hardware detection handler must work."""
        from bot_mmorpg.bridge.handlers import CommandHandler

        handler = CommandHandler()
        result = handler.handle_config_get_hardware()

        assert "cpu_cores" in result
        assert result["cpu_cores"] > 0
        assert "ram_mb" in result
        assert result["ram_mb"] > 0
        assert "tier" in result

    def test_handler_list_games(self):
        """List games handler must return game profiles."""
        from bot_mmorpg.bridge.handlers import CommandHandler

        handler = CommandHandler()
        games = handler.handle_config_list_games()

        assert isinstance(games, list)
        assert len(games) > 0
        for game in games:
            assert "id" in game
            assert "name" in game

    def test_handler_training_state_default(self):
        """Training state must default to not-training."""
        from bot_mmorpg.bridge.handlers import CommandHandler

        handler = CommandHandler()
        state = handler.handle_training_get_state()

        assert state["is_training"] is False

    def test_handler_inference_state_default(self):
        """Inference state must default to not-running."""
        from bot_mmorpg.bridge.handlers import CommandHandler

        handler = CommandHandler()
        state = handler.handle_inference_get_state()

        assert state["is_running"] is False
        assert state["model_loaded"] is False

    def test_handler_cleanup(self):
        """Handler cleanup must not raise errors."""
        from bot_mmorpg.bridge.handlers import CommandHandler

        handler = CommandHandler()
        handler.cleanup()  # Should not raise

    def test_handler_training_stop_when_not_training(self):
        """Stopping training when not training must be safe."""
        from bot_mmorpg.bridge.handlers import CommandHandler

        handler = CommandHandler()
        result = handler.handle_training_stop()

        assert result["status"] == "stopped"

    def test_handler_inference_stop_when_not_running(self):
        """Stopping inference when not running must be safe."""
        from bot_mmorpg.bridge.handlers import CommandHandler

        handler = CommandHandler()
        result = handler.handle_inference_stop()

        assert result["status"] == "stopped"


# ---------------------------------------------------------------------------
# Entry Points
# ---------------------------------------------------------------------------
class TestEntryPoints:
    """Verify all entry points exist and are configured."""

    def test_python_entry_points_defined(self):
        """pyproject.toml must define all 3 CLI entry points."""
        pyproject = ROOT / "pyproject.toml"
        content = pyproject.read_text(encoding="utf-8")

        assert "bot-mmorpg-collect" in content
        assert "bot-mmorpg-train" in content
        assert "bot-mmorpg-play" in content

    def test_src_scripts_exist(self):
        """src/bot_mmorpg/scripts/ must have all 3 phase modules."""
        scripts_dir = ROOT / "src" / "bot_mmorpg" / "scripts"
        assert (scripts_dir / "collect_data.py").exists()
        assert (scripts_dir / "train_model.py").exists()
        assert (scripts_dir / "test_model.py").exists()

    def test_version_scripts_exist(self):
        """versions/0.01/ must have all 3 phase scripts."""
        versions_dir = ROOT / "versions" / "0.01"
        assert (versions_dir / "1-collect_data.py").exists()
        assert (versions_dir / "2-train_model.py").exists()
        assert (versions_dir / "3-test_model.py").exists()

    def test_backend_entry_exists(self):
        """Backend entry module must exist for Tauri sidecar."""
        backend_dir = ROOT / "backend"
        assert backend_dir.exists()
        assert (backend_dir / "main_backend.py").exists()

    def test_modelhub_tauri_entry_exists(self):
        """ModelHub Tauri API entry must exist."""
        modelhub_dir = ROOT / "modelhub"
        assert modelhub_dir.exists()
        tauri_py = modelhub_dir / "tauri.py"
        assert tauri_py.exists(), "modelhub/tauri.py required for sidecar"


# ---------------------------------------------------------------------------
# Installer Assets
# ---------------------------------------------------------------------------
class TestInstallerAssets:
    """Verify installer-related assets are present."""

    def test_nsis_template_exists(self):
        """NSIS installer template must exist."""
        nsis = ROOT / "installer" / "nsis_template.nsi"
        assert nsis.exists()

    def test_nsis_template_has_correct_escaping(self):
        """NSIS template follows the canonical tauri-bundler 1.6.6+
        pattern: a !define indirection for the main binary name (so we
        never inline {{main_binary_name}} in a path string), and
        double-backslash escape on the resources_dirs each-loop where
        a handlebars expression DOES live inside an NSIS path string.

        The previous version of this test asserted the literal
        `\\{{main_binary_name}}` pattern, but our template stopped
        inlining that variable in path strings entirely (commit
        943f9f8 in branch claude/verify-directory-structure-DLUt1)
        because it was the cause of the literal-{{this}}-named-folders
        bug at install time. The safer architecture is to keep
        handlebars expressions OUT of NSIS path strings whenever
        possible, and double-escape the few places they must appear.
        """
        nsis = ROOT / "installer" / "nsis_template.nsi"
        if not nsis.exists():
            pytest.skip("NSIS template not found")

        content = nsis.read_text(encoding="utf-8", errors="replace")

        # Invariant 1: MAINBINARYNAME is an NSIS macro, referenced via
        # ${MAINBINARYNAME} from File / shortcut / registry directives.
        assert '!define MAINBINARYNAME "BOT-MMORPG-AI"' in content, (
            "NSIS template must define MAINBINARYNAME as an NSIS macro "
            "instead of inlining {{main_binary_name}} in path strings."
        )
        assert "${MAINBINARYNAME}.exe" in content, (
            "NSIS template must reference ${MAINBINARYNAME} from File "
            "/ shortcut directives."
        )

        # Invariant 2: where handlebars DO appear in NSIS path strings
        # (the resources_dirs each-loop), the path uses double backslash
        # before `{{`. handlebars-rust treats `\\{{` as the escape
        # sequence for a literal `{{` (suppressing expression parsing),
        # so single-backslash here would render as the literal text
        # "{{this}}" and NSIS would create a folder by that exact name.
        assert r'"$INSTDIR\\{{this}}"' in content, (
            "resources_dirs CreateDirectory must use DOUBLE backslash "
            "before {{this}} -- single backslash is the handlebars "
            "escape sequence for literal {{ and produces folders "
            "literally named '{{this}}' at install time."
        )

    def test_license_file_exists(self):
        """License file must exist for installer."""
        license_path = TAURI_DIR / "license.txt"
        if not license_path.exists():
            # Also check root
            license_path = ROOT / "LICENSE"
        assert license_path.exists(), "License file required for installer"

    def test_icon_files_exist(self):
        """Application icon files must exist."""
        icons_dir = TAURI_DIR / "icons"
        if not icons_dir.exists():
            pytest.skip("Icons directory not found")

        # At least one icon format must exist
        icon_formats = list(icons_dir.glob("*.png")) + list(icons_dir.glob("*.ico"))
        assert len(icon_formats) > 0, "At least one icon file required"
