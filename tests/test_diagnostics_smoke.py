"""
Smoke tests for the AI debug-loop diagnostics module.

Covers the two pure-Python files added in commit c1e2688:
    modelhub/diagnostics/collector.py
    modelhub/diagnostics/formatter.py

The third file (routes.py) imports FastAPI and is exercised at sidecar
startup; we skip its tests in this venv where FastAPI isn't installed.
"""

from __future__ import annotations

import json

import pytest

from modelhub.diagnostics import collector, formatter


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
        assert out["claude_code_task"] == "fix_runtime_error"
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
        # How-to footer
        assert "Paste the entire block above into Claude Code" in out

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
