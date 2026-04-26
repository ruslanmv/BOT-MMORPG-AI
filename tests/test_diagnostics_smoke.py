"""
Smoke tests for the AI debug-loop diagnostics module.

Covers the two pure-Python files added in commit c1e2688:
    modelhub/diagnostics/collector.py
    modelhub/diagnostics/formatter.py

The third file (routes.py) imports FastAPI and is exercised at sidecar
startup; we skip its tests in this venv where FastAPI isn't installed.

Also exercises the sitecustomize.py that src-tauri/src/main.rs writes
into the bundled embedded-Python site-packages on every launch -- by
extracting the literal-string lines from main.rs and compiling them
as Python. Regression guard against the IndentationError we hit when
the Rust source previously used `\` line continuations that swallowed
the leading whitespace inside the `if`-body.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from modelhub.diagnostics import collector, formatter

REPO_ROOT = Path(__file__).resolve().parent.parent
MAIN_RS = REPO_ROOT / "src-tauri" / "src" / "main.rs"


# ---------------------------------------------------------------------
# collector.py
# ---------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset_buffer():
    """Each test starts with an empty ring buffer."""
    collector.clear()
    yield
    collector.clear()


class TestCollector:
    def test_capture_message_adds_entry(self):
        before = collector.buffer_size()
        entry = collector.capture_message("test event", source="unit")
        assert entry["error_type"] == "ManualReport"
        assert entry["message"] == "test event"
        assert entry["source"] == "unit"
        assert collector.buffer_size() == before + 1

    def test_capture_exception_extracts_traceback(self):
        try:
            raise ValueError("boom")
        except ValueError as e:
            entry = collector.capture_exception(e, source="unit")
        assert entry["error_type"] == "ValueError"
        assert entry["message"] == "boom"
        # The traceback text should mention the test file
        assert "test_diagnostics_smoke.py" in entry["traceback"]
        # primary_file/line should point at the raise site in this file
        assert entry["primary_file"].endswith("test_diagnostics_smoke.py")
        assert entry["primary_line"] > 0

    def test_capture_exception_with_request_context(self):
        try:
            raise KeyError("missing-key")
        except KeyError as e:
            entry = collector.capture_exception(
                e,
                source="sidecar",
                request_path="/modelhub/catalog",
                request_method="GET",
                extra={"game_id": "genshin"},
            )
        assert entry["request_path"] == "/modelhub/catalog"
        assert entry["request_method"] == "GET"
        assert entry["extra"] == {"game_id": "genshin"}

    def test_recent_errors_returns_in_order(self):
        collector.capture_message("first")
        collector.capture_message("second")
        collector.capture_message("third")
        items = collector.recent_errors()
        assert len(items) == 3
        assert items[0]["message"] == "first"
        assert items[-1]["message"] == "third"

    def test_recent_errors_respects_limit(self):
        for i in range(10):
            collector.capture_message(f"msg {i}")
        items = collector.recent_errors(limit=3)
        assert len(items) == 3
        # Most recent 3, in order
        assert [e["message"] for e in items] == ["msg 7", "msg 8", "msg 9"]

    def test_buffer_caps_at_max_entries(self):
        # Push more than the cap and ensure oldest entries get dropped
        cap = collector._MAX_ENTRIES  # noqa: SLF001
        for i in range(cap + 20):
            collector.capture_message(f"msg {i}")
        assert collector.buffer_size() == cap
        items = collector.recent_errors()
        # Earliest 20 should have been dropped
        assert items[0]["message"] == "msg 20"
        assert items[-1]["message"] == f"msg {cap + 19}"

    def test_clear_returns_count_and_empties(self):
        for _ in range(5):
            collector.capture_message("x")
        assert collector.buffer_size() == 5
        cleared = collector.clear()
        assert cleared == 5
        assert collector.buffer_size() == 0

    def test_capture_exception_never_raises(self):
        # Pass nonsense and ensure we still return something rather than
        # propagating. The diagnostic layer must never escalate.
        class WeirdExc(Exception):
            def __str__(self):
                raise RuntimeError("str() blew up")

        # capture_exception is wrapped in try/except; even if extraction
        # fails it should return a stub.
        result = collector.capture_exception(WeirdExc())
        assert isinstance(result, dict)
        assert "error_type" in result or "id" in result


# ---------------------------------------------------------------------
# formatter.py
# ---------------------------------------------------------------------


class TestFormatter:
    def _sample_entry(self, **overrides):
        base = {
            "id": "err-test",
            "timestamp": 1735206567.0,
            "source": "spawned_script",
            "error_type": "ModuleNotFoundError",
            "message": "No module named 'grabscreen'",
            "traceback": (
                "Traceback (most recent call last):\n"
                '  File "/abs/path/to/repo/versions/0.01/1-collect_data.py", line 10, in <module>\n'
                "    from grabscreen import grab_screen\n"
                "ModuleNotFoundError: No module named 'grabscreen'\n"
            ),
            "primary_file": "/abs/path/to/repo/versions/0.01/1-collect_data.py",
            "primary_line": 10,
            "request_path": None,
            "request_method": None,
            "extra": {},
        }
        base.update(overrides)
        return base

    def test_to_repo_relative_strips_root(self):
        rel = formatter._to_repo_relative(  # noqa: SLF001
            "/abs/path/to/repo/src-tauri/src/main.rs",
            "/abs/path/to/repo",
        )
        assert rel == "src-tauri/src/main.rs"

    def test_to_repo_relative_handles_windows_paths(self):
        rel = formatter._to_repo_relative(  # noqa: SLF001
            "C:\\workspace\\repo\\src-tauri\\src\\main.rs",
            "C:\\workspace\\repo",
        )
        # Path separators preserved as-is, just prefix stripped
        assert rel.endswith("main.rs")
        assert "src-tauri" in rel

    def test_to_repo_relative_returns_unchanged_when_no_match(self):
        rel = formatter._to_repo_relative(  # noqa: SLF001
            "/some/other/path",
            "/abs/path/to/repo",
        )
        assert rel == "/some/other/path"

    def test_candidate_files_includes_primary_file(self):
        entry = self._sample_entry()
        cands = formatter._candidate_files(entry, "/abs/path/to/repo")  # noqa: SLF001
        # primary file should be repo-relative
        assert "versions/0.01/1-collect_data.py" in cands
        # bug index should always be there
        assert "docs/installer/04-bug-index.md" in cands
        # spawned_script source -> main.rs hint
        assert "src-tauri/src/main.rs" in cands

    def test_candidate_files_dedupes_and_preserves_order(self):
        entry = self._sample_entry(primary_file="docs/installer/04-bug-index.md")
        cands = formatter._candidate_files(entry, None)  # noqa: SLF001
        # Even though 04-bug-index appears in primary AND in defaults,
        # it shows up exactly once.
        assert cands.count("docs/installer/04-bug-index.md") == 1

    def test_candidate_files_per_source_hints(self):
        sidecar_entry = self._sample_entry(source="sidecar", primary_file="")
        cands = formatter._candidate_files(sidecar_entry, None)  # noqa: SLF001
        assert "modelhub/tauri.py" in cands
        assert "backend/main_backend.py" in cands

        rust_entry = self._sample_entry(source="rust", primary_file="")
        cands = formatter._candidate_files(rust_entry, None)  # noqa: SLF001
        assert "src-tauri/src/main.rs" in cands

    def test_format_one_produces_expected_shape(self):
        entry = self._sample_entry()
        out = formatter.format_one(entry, repo_root="/abs/path/to/repo")
        assert out["task"] == "fix_runtime_error"
        # Vendor-neutral: must NOT carry a vendor-specific key like
        # claude_code_task / chatgpt_task / etc. The bundle is generic.
        assert "claude_code_task" not in out
        assert out["summary"].startswith("ModuleNotFoundError:")
        assert out["error"]["type"] == "ModuleNotFoundError"
        assert out["error"]["primary_file"] == "versions/0.01/1-collect_data.py"
        assert out["error"]["primary_line"] == 10
        assert isinstance(out["candidate_files"], list)
        assert isinstance(out["instructions"], list)
        # Timestamp is ISO-formatted
        assert "T" in out["timestamp_iso"] and out["timestamp_iso"].endswith("Z")

    def test_format_one_is_json_serializable(self):
        entry = self._sample_entry()
        out = formatter.format_one(entry)
        # Must round-trip through json without TypeError
        encoded = json.dumps(out)
        decoded = json.loads(encoded)
        assert decoded["error"]["type"] == "ModuleNotFoundError"

    def test_format_bundle_empty_returns_friendly_message(self):
        out = formatter.format_bundle([])
        assert "No errors captured" in out
        assert out.startswith("# AI Fix Request")

    def test_format_bundle_markdown_structure(self):
        entries = [self._sample_entry()]
        out = formatter.format_bundle(
            entries,
            repo_root="/abs/path/to/repo",
            app_version="0.0.0-dev",
            install_dir="C:\\Program Files\\BOT-MMORPG-AI",
            log_tail="[10:49:24] (stderr) ModuleNotFoundError\n",
        )
        # Header + metadata
        assert out.startswith("# AI Fix Request")
        assert "0.0.0-dev" in out
        assert "BOT-MMORPG-AI" in out
        assert "Error count: 1" in out
        # Per-error section
        assert "### Error 1 — ModuleNotFoundError:" in out
        # JSON code block present
        assert "```json" in out
        # Recent log section appended
        assert "## Recent in-app log tail" in out
        assert "ModuleNotFoundError" in out
        # How-to footer is vendor-neutral: must mention "AI coding
        # assistant" (the new generic phrasing) and must NOT name a
        # specific vendor product like Claude Code or ChatGPT.
        assert "AI coding assistant" in out
        assert "Claude Code" not in out

    def test_format_bundle_with_multiple_errors_numbers_sections(self):
        entries = [
            self._sample_entry(message="first"),
            self._sample_entry(message="second"),
            self._sample_entry(message="third"),
        ]
        out = formatter.format_bundle(entries)
        assert "### Error 1 —" in out
        assert "### Error 2 —" in out
        assert "### Error 3 —" in out
        assert "Error count: 3" in out


# ---------------------------------------------------------------------
# End-to-end: collector -> formatter
# ---------------------------------------------------------------------


class TestEndToEnd:
    def test_capture_then_format_round_trip(self):
        collector.clear()
        try:
            raise RuntimeError("integration test failure")
        except RuntimeError as e:
            collector.capture_exception(e, source="unit")

        entries = collector.recent_errors()
        bundle = formatter.format_bundle(
            entries,
            app_version="test-1.0",
            install_dir="/test/install",
        )
        assert "RuntimeError" in bundle
        assert "integration test failure" in bundle
        assert "test-1.0" in bundle
        # Markdown JSON code blocks come in pairs: each "```json" opener
        # has a matching "```" closer. Total "```" tokens = 2 * blocks.
        json_blocks = bundle.count("```json")
        all_fences = bundle.count("```")
        assert all_fences == 2 * json_blocks, (
            "Markdown code-block fences are unbalanced"
        )


# ---------------------------------------------------------------------
# Embedded sitecustomize.py guardrail
#
# The Rust runtime (src-tauri/src/main.rs#ensure_python_env) writes a
# tiny sitecustomize.py into the bundled embedded-Python site-packages
# on every launch. Its job is to read BOT_VERSION_DIR (set by Rust)
# and prepend it to sys.path so spawned scripts can import sibling
# modules (grabscreen, getkeys, vjoy2, ...).
#
# A previous revision wrote that file via a single Rust string literal
# with `\` line continuations. Rust collapses every "\n\<whitespace>"
# into just "\n", which dedented the body of the if-statement and made
# Python reject the file with IndentationError -- breaking every
# spawned script the moment it tried a relative import.
#
# This test reads main.rs, extracts the literal sitecustomize_lines
# array, joins it the same way the Rust code does, and asks Python's
# compiler to parse it. If the indentation is wrong, compile() raises
# SyntaxError and this test fails before the broken bundle ever ships.
# ---------------------------------------------------------------------


class TestEmbeddedSitecustomize:
    def _extract_lines(self) -> list[str]:
        """
        Pull the sitecustomize_lines: &[&str] = &[ ... ]; block out of
        main.rs and return each Python line as a string. Uses a simple
        regex anchored on the variable name so it's robust to surrounding
        comment/code changes.
        """
        if not MAIN_RS.exists():
            pytest.skip(f"main.rs not found: {MAIN_RS}")
        text = MAIN_RS.read_text(encoding="utf-8")
        m = re.search(
            r"sitecustomize_lines:\s*&\[&str\]\s*=\s*&\[(.*?)\];",
            text,
            re.DOTALL,
        )
        assert m, (
            "Could not locate sitecustomize_lines in main.rs. "
            "If the Rust shape changed, update this test's regex."
        )
        body = m.group(1)
        # Each entry is a "..." string literal. Pull them out.
        return re.findall(r'"((?:[^"\\]|\\.)*)"', body)

    def test_lines_present(self):
        lines = self._extract_lines()
        assert lines, "sitecustomize_lines array was empty"

    def test_compiles_as_valid_python(self):
        lines = self._extract_lines()
        source = "\n".join(lines)
        # If indentation is wrong, compile() raises SyntaxError /
        # IndentationError and this test fails. That's the regression
        # we're guarding against.
        try:
            compile(source, "<sitecustomize.py from main.rs>", "exec")
        except SyntaxError as e:
            pytest.fail(
                f"Embedded sitecustomize.py is not valid Python: {e}\n"
                f"Source rebuilt from main.rs:\n---\n{source}\n---"
            )

    def test_executes_without_runtime_error(self):
        """
        The compiled sitecustomize must also be runnable (no NameError
        for missing imports etc.). Run it in a clean namespace with a
        synthetic BOT_VERSION_DIR pointing at this repo.
        """
        import os

        lines = self._extract_lines()
        source = "\n".join(lines)
        ns: dict = {}
        old_env = os.environ.get("BOT_VERSION_DIR")
        os.environ["BOT_VERSION_DIR"] = str(REPO_ROOT)
        try:
            exec(compile(source, "<sitecustomize>", "exec"), ns)
        finally:
            if old_env is None:
                os.environ.pop("BOT_VERSION_DIR", None)
            else:
                os.environ["BOT_VERSION_DIR"] = old_env

    def test_inserts_vdir_into_sys_path(self):
        """
        End-to-end: when BOT_VERSION_DIR is set, the script should
        prepend that directory to sys.path. We verify by running the
        compiled module against a fresh sys.path-shaped list.
        """
        import os
        import sys

        lines = self._extract_lines()
        source = "\n".join(lines)
        sentinel = str(REPO_ROOT / "versions" / "0.01")

        # Temporarily inject BOT_VERSION_DIR pointing at a real dir
        # (versions/0.01 must exist for the os.path.isdir check to pass).
        if not Path(sentinel).is_dir():
            pytest.skip(f"versions/0.01 dir not present at {sentinel}")

        old_env = os.environ.get("BOT_VERSION_DIR")
        old_path = list(sys.path)
        try:
            os.environ["BOT_VERSION_DIR"] = sentinel
            # Make sure the sentinel isn't already on sys.path (would
            # make the "if not in sys.path" branch a no-op and we'd
            # fail to detect breakage).
            sys.path[:] = [p for p in sys.path if p != sentinel]
            exec(compile(source, "<sitecustomize>", "exec"), {})
            assert sentinel in sys.path, (
                "sitecustomize did not prepend BOT_VERSION_DIR to sys.path"
            )
            # And it must be at the FRONT (insert(0, ...))
            assert sys.path[0] == sentinel, (
                "sitecustomize inserted BOT_VERSION_DIR but not at index 0"
            )
        finally:
            sys.path[:] = old_path
            if old_env is None:
                os.environ.pop("BOT_VERSION_DIR", None)
            else:
                os.environ["BOT_VERSION_DIR"] = old_env
