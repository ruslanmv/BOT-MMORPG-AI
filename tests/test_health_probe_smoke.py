"""
Smoke tests for modelhub.diagnostics.health_probe.

Pure stdlib module by design (so tests don't need any extra deps).
Each sub-probe is wrapped in try/except in the implementation; these
tests just assert the public shape and that no probe raises in a
clean environment.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from modelhub.diagnostics import health_probe


REPO_ROOT = Path(__file__).resolve().parent.parent


class TestDeepProbeShape:
    def test_returns_dict_with_top_level_keys(self):
        result = health_probe.deep_probe(install_dir=REPO_ROOT)
        # Required top-level categories. If any are missing, the AI
        # bundle would lose context -- regression guard.
        for key in (
            "install_dir",
            "system",
            "memory",
            "disk",
            "filesystem",
            "network",
            "python_runtime",
            "file_integrity",
            "environment",
            "antivirus",
        ):
            assert key in result, f"deep_probe missing top-level key: {key}"

    def test_system_subprobe_minimum_fields(self):
        result = health_probe.deep_probe(install_dir=REPO_ROOT)
        sysinfo = result["system"]
        assert "os" in sysinfo
        assert "python_version" in sysinfo
        # python_version should look like "3.x.y", not "unknown"
        assert sysinfo["python_version"].count(".") >= 1

    def test_disk_reports_install_and_temp(self):
        result = health_probe.deep_probe(install_dir=REPO_ROOT)
        d = result["disk"]
        assert "install" in d
        assert "temp" in d
        # Either entry should have free_gb (success) or error (failure).
        for label in ("install", "temp"):
            entry = d[label]
            assert "free_gb" in entry or "error" in entry

    def test_filesystem_flags_returned(self):
        result = health_probe.deep_probe(install_dir=REPO_ROOT)
        fs = result["filesystem"]
        assert "is_program_files" in fs
        assert "onedrive_redirected" in fs
        assert "install_dir_writable" in fs
        assert "path_length" in fs
        # Repo root is definitely not Program Files
        assert fs["is_program_files"] is False

    def test_network_subprobe(self):
        result = health_probe.deep_probe(install_dir=REPO_ROOT)
        net = result["network"]
        assert "loopback_resolves" in net
        # If we could bind, free_port is set; if not, bind_error is set.
        assert "free_port" in net or "bind_error" in net

    def test_file_integrity_is_a_list(self):
        result = health_probe.deep_probe(install_dir=REPO_ROOT)
        files = result["file_integrity"]
        assert isinstance(files, list)
        # Each entry should have path + status
        for entry in files:
            assert "path" in entry
            assert "status" in entry
            assert entry["status"] in ("ok", "missing", "unreadable")

    def test_environment_redacted(self):
        # The probe must NEVER leak unredacted env vars (PATH, secrets).
        # It returns ONLY the explicit allow-list in _OWN_ENV_VARS plus
        # PATH_length / PATHEXT.
        result = health_probe.deep_probe(install_dir=REPO_ROOT)
        env = result["environment"]
        # "PATH" itself must NEVER appear -- only the length
        assert "PATH" not in env
        # PATH_length must be a string (or absent)
        if "PATH_length" in env:
            assert env["PATH_length"].isdigit()


class TestRobustness:
    def test_never_raises_on_nonexistent_install_dir(self):
        # The probe must degrade gracefully when the install dir
        # doesn't exist (e.g. before the installer has run). Each
        # sub-probe should record an error rather than propagate.
        result = health_probe.deep_probe(install_dir=Path("/nonexistent/path/xyz"))
        assert isinstance(result, dict)
        assert "system" in result  # system info still works

    def test_file_integrity_marks_missing_files(self):
        result = health_probe.deep_probe(install_dir=Path("/nonexistent/path/xyz"))
        files = result["file_integrity"]
        # Every critical file should be reported "missing" since the
        # install dir doesn't exist.
        for entry in files:
            assert entry["status"] == "missing"

    def test_output_is_json_serializable(self):
        # The bundle wraps the probe in `json.dumps`. If any value is
        # non-serializable (e.g. a Path object slipped through), the
        # bundle build would crash.
        import json

        result = health_probe.deep_probe(install_dir=REPO_ROOT)
        # Use default=str to mirror the formatter's actual call.
        json.dumps(result, default=str)


class TestSecurityHardening:
    def test_secrets_not_leaked_via_environment(self):
        """
        Even if a secret-looking var is set in the environment, the
        probe must not return it (only allow-listed names + lengths).
        """
        import os

        sentinel = "ZG9udC1leHBvc2UtbWUtdG8tYW55b25l"  # deliberately exotic
        old_secret = os.environ.get("OPENAI_API_KEY")
        old_aws = os.environ.get("AWS_SECRET_ACCESS_KEY")
        os.environ["OPENAI_API_KEY"] = sentinel
        os.environ["AWS_SECRET_ACCESS_KEY"] = sentinel
        try:
            result = health_probe.deep_probe(install_dir=REPO_ROOT)
            import json

            blob = json.dumps(result, default=str)
            assert sentinel not in blob, (
                "Secret leaked into deep_probe output. "
                "_redact_env() should only emit allow-listed names."
            )
        finally:
            if old_secret is None:
                os.environ.pop("OPENAI_API_KEY", None)
            else:
                os.environ["OPENAI_API_KEY"] = old_secret
            if old_aws is None:
                os.environ.pop("AWS_SECRET_ACCESS_KEY", None)
            else:
                os.environ["AWS_SECRET_ACCESS_KEY"] = old_aws


class TestFormatterIntegration:
    """
    The bundle formatter accepts a system_probe field. Verify it
    renders the deep probe inside a fenced JSON block when present,
    and omits the section entirely when absent.
    """

    def test_bundle_omits_probe_section_when_absent(self):
        from modelhub.diagnostics import formatter

        out = formatter.format_bundle(
            [],
            app_version="test",
            install_dir="/test",
        )
        assert "## System probe" not in out

    def test_bundle_includes_probe_section_when_present(self):
        from modelhub.diagnostics import formatter

        probe = health_probe.deep_probe(install_dir=REPO_ROOT)
        # Need at least one entry for the bundle to render fully
        sample = {
            "id": "x",
            "timestamp": 0,
            "source": "unit",
            "error_type": "RuntimeError",
            "message": "test",
            "traceback": "",
            "primary_file": "",
            "primary_line": 0,
            "request_path": None,
            "request_method": None,
            "extra": {},
        }
        out = formatter.format_bundle(
            [sample],
            app_version="test",
            install_dir="/test",
            system_probe=probe,
        )
        assert "## System probe" in out
        # Probe rendered as JSON code block
        assert "```json" in out
        # Some recognisable field from the probe
        assert "system" in out

    def test_bundle_with_probe_is_json_safe(self):
        """
        When the bundle includes the probe as embedded JSON, the JSON
        block must round-trip through json.loads cleanly. Catches
        regressions where the probe gains a non-serializable value.
        """
        import json
        import re

        from modelhub.diagnostics import formatter

        probe = health_probe.deep_probe(install_dir=REPO_ROOT)
        sample = {
            "id": "x",
            "timestamp": 0,
            "source": "unit",
            "error_type": "RuntimeError",
            "message": "test",
            "traceback": "",
            "primary_file": "",
            "primary_line": 0,
            "request_path": None,
            "request_method": None,
            "extra": {},
        }
        out = formatter.format_bundle(
            [sample],
            app_version="test",
            install_dir="/test",
            system_probe=probe,
        )
        # Find the System probe code block specifically
        match = re.search(
            r"## System probe.*?```json\n(.*?)\n```",
            out,
            re.DOTALL,
        )
        assert match, "System probe block not found in bundle"
        # Must round-trip through json.loads
        parsed = json.loads(match.group(1))
        assert isinstance(parsed, dict)


@pytest.mark.skipif(
    not Path("/proc/meminfo").exists(),
    reason="memory probe path varies; only assert when /proc/meminfo present",
)
class TestMemoryOnLinux:
    def test_memory_returns_total_and_available_in_gb(self):
        result = health_probe.deep_probe(install_dir=REPO_ROOT)
        mem = result["memory"]
        assert "total_gb" in mem
        assert "available_gb" in mem
        assert mem["total_gb"] > 0
        assert mem["available_gb"] >= 0
