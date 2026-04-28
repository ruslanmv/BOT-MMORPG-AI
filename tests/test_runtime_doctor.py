"""
Tests for scripts/runtime_doctor.py.

The doctor is a stdlib-only single-file CLI that exercises the
bundled site-packages. These tests don't try to assert specific
package versions are available -- we test the doctor's *contract*:

  - JSON output schema is stable
  - Exit codes match verdicts
  - One broken check cannot poison the rest
  - The doctor never raises out of main(), even on catastrophic
    internal failure
  - --version prints the doctor's version and exits 0
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCTOR_PATH = ROOT / "scripts" / "runtime_doctor.py"


def _load_doctor_module():
    """Import scripts/runtime_doctor.py as a module without spawning."""
    spec = importlib.util.spec_from_file_location("runtime_doctor", DOCTOR_PATH)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    # Must register in sys.modules BEFORE exec_module: the dataclass
    # decorator inside runtime_doctor.py resolves forward-ref string
    # annotations (from `from __future__ import annotations`) by
    # looking the module up in sys.modules. Skip this and you get
    # `AttributeError: 'NoneType' object has no attribute '__dict__'`
    # from the stdlib dataclasses module.
    sys.modules["runtime_doctor"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def doctor():
    return _load_doctor_module()


# --- Module-level invariants ---


def test_doctor_file_exists():
    assert DOCTOR_PATH.exists(), f"Missing: {DOCTOR_PATH}"


def test_doctor_version_constant_present(doctor):
    assert isinstance(doctor.DOCTOR_VERSION, str)
    assert len(doctor.DOCTOR_VERSION.split(".")) == 3, (
        "DOCTOR_VERSION should be semver MAJOR.MINOR.PATCH; got "
        f"{doctor.DOCTOR_VERSION!r}"
    )


# --- Exit code mapping ---


def test_verdict_to_exit_code(doctor):
    assert doctor.verdict_to_exit_code("ok") == 0
    assert doctor.verdict_to_exit_code("warning") == 1
    assert doctor.verdict_to_exit_code("error") == 2
    assert doctor.verdict_to_exit_code("garbage") == 3


# --- _run_check captures every exception ---


def test_run_check_captures_value_error(doctor):
    def bad():
        raise ValueError("nope")

    result = doctor._run_check("test_check", bad)
    assert result.status == "error"
    assert result.name == "test_check"
    assert "ValueError" in result.detail
    assert "nope" in result.detail


def test_run_check_captures_os_error(doctor):
    """OSError is the shape of torch DLL load failure on Windows."""
    def bad():
        raise OSError("[WinError 126] The specified module could not be found")

    result = doctor._run_check("torch_intact", bad)
    assert result.status == "error"
    assert "OSError" in result.detail
    assert "WinError 126" in result.detail


def test_run_check_captures_systemexit(doctor):
    """A misbehaving import should not be able to kill the doctor."""
    def evil():
        raise SystemExit(99)

    result = doctor._run_check("evil", evil)
    assert result.status == "error"
    assert "SystemExit" in result.detail


def test_run_check_forces_correct_name(doctor):
    """If a check returns a CheckResult with the wrong name field, the
    runner must fix it. This protects the JSON schema from drift."""
    def returns_with_wrong_name():
        return doctor.CheckResult("OOPS_WRONG", "ok", "")

    result = doctor._run_check("expected_name", returns_with_wrong_name)
    assert result.name == "expected_name"


def test_run_check_records_elapsed_ms(doctor):
    def quick():
        return doctor.CheckResult("quick", "ok", "")

    result = doctor._run_check("quick", quick)
    assert isinstance(result.elapsed_ms, int)
    assert result.elapsed_ms >= 0


# --- Verdict rollup ---


def test_run_selftest_returns_report(doctor):
    """Doctor always produces a structured report, regardless of
    which packages are present in the test environment."""
    report = doctor.run_selftest()
    assert hasattr(report, "verdict")
    assert hasattr(report, "checks")
    assert hasattr(report, "platform")
    assert report.verdict in ("ok", "warning", "error")
    assert isinstance(report.checks, list)
    assert len(report.checks) >= 5, (
        f"Doctor should run >=5 checks; got {len(report.checks)}"
    )


def test_run_selftest_each_check_has_required_fields(doctor):
    report = doctor.run_selftest()
    for chk in report.checks:
        assert chk.name, "CheckResult.name must not be empty"
        assert chk.status in ("ok", "warn", "error"), (
            f"Invalid status {chk.status!r} on check {chk.name}"
        )
        assert isinstance(chk.detail, str)
        assert isinstance(chk.elapsed_ms, int)


# --- JSON serialization ---


def test_report_to_json_round_trip(doctor):
    report = doctor.run_selftest()
    payload = doctor.report_to_json(report)
    parsed = json.loads(payload)
    assert parsed["doctor_version"] == doctor.DOCTOR_VERSION
    assert parsed["verdict"] in ("ok", "warning", "error")
    assert isinstance(parsed["checks"], list)
    assert "platform" in parsed
    assert "elapsed_ms" in parsed


def test_report_to_json_pretty_is_multi_line(doctor):
    report = doctor.run_selftest()
    pretty = doctor.report_to_json(report, pretty=True)
    compact = doctor.report_to_json(report, pretty=False)
    assert "\n" in pretty
    assert "\n" not in compact
    # Both must parse to the same payload.
    assert json.loads(pretty)["checks"] == json.loads(compact)["checks"]


# --- main() entrypoint ---


def test_main_version_flag(doctor):
    assert doctor.main(["--version"]) == 0


def test_main_selftest_returns_int(doctor):
    """main() must always return an int, even when the runtime is
    incomplete. Hangs / raises here = doctor itself broken."""
    rc = doctor.main(["--selftest"])
    assert isinstance(rc, int)
    assert rc in (0, 1, 2, 3)


# --- End-to-end via subprocess (matches how Tauri will call it) ---


def test_subprocess_invocation_emits_valid_json(tmp_path):
    """The way the Tauri shell will actually invoke the doctor."""
    proc = subprocess.run(
        [sys.executable, str(DOCTOR_PATH), "--selftest", "--data-dir", str(tmp_path)],
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert proc.stdout, "Doctor produced no stdout"
    payload = json.loads(proc.stdout)
    assert payload["verdict"] in ("ok", "warning", "error")
    assert payload["doctor_version"]
    # data_dir_writable check should pass against the tmp_path we
    # provided, regardless of dev-env package availability.
    by_name = {c["name"]: c for c in payload["checks"]}
    assert "data_dir_writable" in by_name
    assert by_name["data_dir_writable"]["status"] == "ok"


def test_subprocess_exit_code_matches_verdict(tmp_path):
    proc = subprocess.run(
        [sys.executable, str(DOCTOR_PATH), "--selftest", "--data-dir", str(tmp_path)],
        capture_output=True,
        text=True,
        timeout=180,
    )
    payload = json.loads(proc.stdout)
    expected = {"ok": 0, "warning": 1, "error": 2}.get(payload["verdict"], 3)
    assert proc.returncode == expected, (
        f"verdict={payload['verdict']} but exit={proc.returncode} (expected {expected})"
    )


# --- Enriched torch_intact / numpy_intact failure context ---
#
# Regression guard for the diagnostic enrichment that surfaces
# torch_root + torch_testing_dir_exists in the failure detail. Without
# this, an AV-quarantined torch/testing/ produces only a generic
# ModuleNotFoundError message that doesn't disambiguate from "torch
# was never installed". With it, the operator (and any AI assistant
# reading the bundle) sees the on-disk path and the boolean smoking
# gun.


def test_resolve_pkg_root_for_stdlib_module(doctor):
    """_resolve_pkg_root should find a known-installed package."""
    # `json` is a stdlib package that lives on every Python install.
    root = doctor._resolve_pkg_root("json")
    assert isinstance(root, str)
    assert root.endswith("json") or root == "<not found on sys.path>" or "json" in root


def test_resolve_pkg_root_for_missing_package(doctor):
    """A bogus name returns the sentinel string, never raises."""
    root = doctor._resolve_pkg_root("definitely_not_a_real_package_botmmo_xyz")
    assert root == "<not found on sys.path>"


def test_torch_intact_failure_detail_carries_path_context(doctor, monkeypatch):
    """Simulate torch.testing missing -- detail must carry torch_root +
    torch_testing_dir_exists so the bundle is actionable."""
    import importlib as _il

    real_import = _il.import_module

    def fake_import(name, *a, **kw):
        if name == "torch.testing":
            raise ModuleNotFoundError("No module named 'torch.testing'")
        return real_import(name, *a, **kw)

    monkeypatch.setattr(_il, "import_module", fake_import)
    result = doctor._check_torch_intact()
    assert result.status == "error"
    assert "torch_root=" in result.detail
    assert "torch_testing_dir_exists=" in result.detail
    # Remediation hint must reference both buttons in the UI flow.
    assert "AV Exclusion" in result.detail or "AV exclusion" in result.detail.lower()
    assert "Repair Runtime" in result.detail or "repair runtime" in result.detail.lower()


def test_numpy_intact_failure_detail_carries_path_context(doctor, monkeypatch):
    """Simulate numpy.testing missing -- same enrichment as torch."""
    import importlib as _il

    real_import = _il.import_module

    def fake_import(name, *a, **kw):
        if name == "numpy.testing":
            raise ModuleNotFoundError("No module named 'numpy.testing'")
        return real_import(name, *a, **kw)

    monkeypatch.setattr(_il, "import_module", fake_import)
    result = doctor._check_numpy_intact()
    assert result.status == "error"
    assert "numpy_root=" in result.detail
    assert "numpy_testing_dir_exists=" in result.detail


def test_torchvision_failure_explains_collateral(doctor, monkeypatch):
    """When torchvision import raises, the detail should call out that
    this is downstream of torch_intact failure (not torchvision being
    independently broken)."""
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *a, **kw):
        if name == "torchvision":
            raise ImportError(
                "cannot import name 'nn' from partially initialized module 'torch'"
            )
        return real_import(name, *a, **kw)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    result = doctor._check_torchvision_intact()
    assert result.status == "error"
    assert "downstream" in result.detail.lower() or "collateral" in result.detail.lower()
