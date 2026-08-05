"""
Regression tests for GitHub issue #79 ("Backend failed to start", v0.2.5).

The bundle in #79 contained three separate defects, only one of which
was the user's actual machine problem:

  1. `ImportError: DLL load failed while importing _C` was reported as
     `missing_module=_C` with remediation text about re-extracting the
     runtime. A DLL-load failure means the .pyd was FOUND and the OS
     could not resolve its native dependencies -- a different bug class
     with a different fix. The old wording sent the operator looking for
     a Python module that was sitting right there, and recommended
     [Repair Runtime], which cannot add a DLL the bundle never had.

  2. The system probe reported ALL 11 critical bundled files as
     `"status": "missing"` on a machine whose sidecar was running
     happily off those very files. `deep_probe` passed the DATA root
     (%LOCALAPPDATA%\\com.bot.mmorpg.ai) to `_file_integrity`, whose
     paths are relative to the INSTALL root (C:\\Program Files\\...).

  3. The in-app log line read `Install health: ERROR --` with nothing
     after the dashes. Runtime-doctor failures are merged into
     `h.checks` and can push the verdict to "error", but the log line
     was built only from the legacy `h.issues` array, which the merge
     never touches.
"""

from __future__ import annotations

import importlib.util
import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCTOR_PATH = ROOT / "scripts" / "runtime_doctor.py"
UI_JS = ROOT / "tauri-ui" / "main.js"

# Verbatim from the #79 debug bundle.
DLL_ERROR_MESSAGE = (
    "DLL load failed while importing _C: The specified module could not be found."
)


@pytest.fixture(scope="module")
def doctor():
    spec = importlib.util.spec_from_file_location("runtime_doctor_i79", DOCTOR_PATH)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["runtime_doctor_i79"] = mod
    spec.loader.exec_module(mod)
    return mod


def _torch_tree(tmp_path, *, lib_dlls=None, testing=False):
    """Build a fake installed-torch directory."""
    root = tmp_path / "site-packages" / "torch"
    root.mkdir(parents=True)
    if testing:
        (root / "testing").mkdir()
    if lib_dlls is not None:
        lib = root / "lib"
        lib.mkdir()
        for name in lib_dlls:
            (lib / name).write_bytes(b"MZ")
    return root


def _fail_torch_import(monkeypatch, exc: BaseException):
    import importlib as _il

    real_import = _il.import_module

    def fake_import(name, *args, **kwargs):
        if name == "torch":
            raise exc
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(_il, "import_module", fake_import)


# =====================================================================
# 1. DLL-load failures are their own bug class
# =====================================================================


def test_dll_load_failure_is_classified(doctor):
    assert doctor._is_dll_load_failure(ImportError(DLL_ERROR_MESSAGE))
    # Linux/macOS wording for the same underlying fault.
    assert doctor._is_dll_load_failure(
        ImportError("libtorch_cpu.so: cannot open shared object file")
    )
    # ERROR_MOD_NOT_FOUND surfaced as an OSError.
    err = OSError("The specified module could not be found")
    err.winerror = 126
    assert doctor._is_dll_load_failure(err)


def test_missing_module_is_not_a_dll_failure(doctor):
    """A genuinely absent package must keep the issue #75 remediation."""
    assert not doctor._is_dll_load_failure(
        ModuleNotFoundError(
            "No module named 'torch._strobelight'", name="torch._strobelight"
        )
    )
    assert not doctor._is_dll_load_failure(
        ModuleNotFoundError("No module named 'torch'")
    )


def test_torch_intact_reports_dll_class_not_a_missing_module(
    doctor, monkeypatch, tmp_path
):
    """The #79 bundle verbatim: `_C` reported as if the module vanished."""
    root = _torch_tree(tmp_path, lib_dlls=["c10.dll", "torch_cpu.dll"])
    monkeypatch.setattr(doctor, "_resolve_pkg_root", lambda pkg: str(root))
    # CPython sets .name to the leaf module for a native import failure.
    exc = ImportError(DLL_ERROR_MESSAGE, name="_C")
    _fail_torch_import(monkeypatch, exc)

    result = doctor._check_torch_intact()

    assert result.status == "error"
    assert "failure_class=dll_load" in result.detail
    assert "missing_module=_C" not in result.detail, (
        "Reporting a DLL-load failure as a missing Python module is what "
        "sent issue #79 after the wrong file."
    )


def test_torch_intact_dll_failure_carries_native_inventory(
    doctor, monkeypatch, tmp_path
):
    root = _torch_tree(tmp_path, lib_dlls=["c10.dll", "torch_cpu.dll", "fbgemm.dll"])
    monkeypatch.setattr(doctor, "_resolve_pkg_root", lambda pkg: str(root))
    _fail_torch_import(monkeypatch, ImportError(DLL_ERROR_MESSAGE, name="_C"))

    detail = doctor._check_torch_intact().detail

    assert "torch_lib_count=3" in detail
    assert str(root / "lib") in detail


def test_torch_intact_dll_failure_recommends_pip_repair_over_reextract(
    doctor, monkeypatch, tmp_path
):
    """[Repair Runtime] re-extracts the same bundle. If the bundle's
    native payload is short, that is a no-op -- and #79's user ran it."""
    root = _torch_tree(tmp_path, lib_dlls=[])
    monkeypatch.setattr(doctor, "_resolve_pkg_root", lambda pkg: str(root))
    _fail_torch_import(monkeypatch, ImportError(DLL_ERROR_MESSAGE, name="_C"))

    detail = doctor._check_torch_intact().detail

    assert "Repair PyTorch via pip" in detail
    assert "will not add a DLL the bundle never had" in detail


def test_torch_intact_keeps_issue_75_wording_for_missing_modules(
    doctor, monkeypatch, tmp_path
):
    """Guard against the #79 fix regressing the #75 fix."""
    root = _torch_tree(tmp_path, lib_dlls=["c10.dll"], testing=True)
    monkeypatch.setattr(doctor, "_resolve_pkg_root", lambda pkg: str(root))
    _fail_torch_import(
        monkeypatch,
        ModuleNotFoundError(
            "No module named 'torch._strobelight'", name="torch._strobelight"
        ),
    )

    detail = doctor._check_torch_intact().detail

    assert "missing_module=torch._strobelight" in detail
    assert "failure_class=dll_load" not in detail
    assert "not a broad" in detail


# =====================================================================
# 2. The torch_dlls check
# =====================================================================


def test_torch_dlls_is_a_registered_check(doctor):
    """It must appear in the report, not just exist as a function --
    an unregistered check diagnoses nothing."""
    report = doctor.run_selftest()
    names = {c.name for c in report.checks}
    assert "torch_dlls" in names
    # Stable ordering: the inventory reads directly after the import it
    # explains.
    ordered = [c.name for c in report.checks]
    assert ordered.index("torch_dlls") == ordered.index("torch_intact") + 1


def test_torch_dlls_errors_when_lib_dir_is_gone(doctor, monkeypatch, tmp_path):
    root = _torch_tree(tmp_path)  # no lib/ at all
    monkeypatch.setattr(doctor, "_resolve_pkg_root", lambda pkg: str(root))
    monkeypatch.setattr(doctor, "_torch_install_roots", lambda: [str(root)])

    result = doctor._check_torch_dlls()

    assert result.status == "error"
    assert "torch/lib/ is missing entirely" in result.detail
    assert "Repair PyTorch via pip" in result.detail


def test_torch_dlls_errors_on_empty_lib_dir(doctor, monkeypatch, tmp_path):
    root = _torch_tree(tmp_path, lib_dlls=[])
    monkeypatch.setattr(doctor, "_resolve_pkg_root", lambda pkg: str(root))
    monkeypatch.setattr(doctor, "_torch_install_roots", lambda: [str(root)])

    result = doctor._check_torch_dlls()

    assert result.status == "error"
    assert "contains no native" in result.detail


def test_torch_dlls_ok_when_payload_present(doctor, monkeypatch, tmp_path):
    root = _torch_tree(
        tmp_path, lib_dlls=["c10.dll", "torch_cpu.dll", doctor._TORCH_EXTERNAL_DLL]
    )
    monkeypatch.setattr(doctor, "_resolve_pkg_root", lambda pkg: str(root))
    monkeypatch.setattr(doctor, "_torch_install_roots", lambda: [str(root)])

    result = doctor._check_torch_dlls()

    assert result.status == "ok"
    assert "3 native" in result.detail


def test_torch_dlls_warns_on_split_installation(doctor, monkeypatch, tmp_path):
    """#79's runtime had torch under `python/lib/site-packages` while the
    launcher exported `python/site-packages` on PYTHONPATH. A repair can
    rewrite one tree while the interpreter imports the other."""
    root = _torch_tree(tmp_path, lib_dlls=["c10.dll", doctor._TORCH_EXTERNAL_DLL])
    other = tmp_path / "lib" / "site-packages" / "torch"
    other.mkdir(parents=True)
    monkeypatch.setattr(doctor, "_resolve_pkg_root", lambda pkg: str(root))
    monkeypatch.setattr(doctor, "_torch_install_roots", lambda: [str(root), str(other)])

    result = doctor._check_torch_dlls()

    assert result.status == "warn"
    assert "2 torch trees" in result.detail
    assert str(other) in result.detail


def test_torch_dlls_defers_to_torch_intact_when_torch_is_absent(doctor, monkeypatch):
    monkeypatch.setattr(
        doctor, "_resolve_pkg_root", lambda pkg: "<not found on sys.path>"
    )
    result = doctor._check_torch_dlls()
    assert result.status == "warn"
    assert "see torch_intact" in result.detail


def test_torch_install_roots_finds_every_tree(doctor, monkeypatch, tmp_path):
    a = tmp_path / "a" / "site-packages"
    b = tmp_path / "b" / "lib" / "site-packages"
    (a / "torch").mkdir(parents=True)
    (b / "torch").mkdir(parents=True)
    monkeypatch.setattr(
        doctor.sys, "path", [str(a), str(b), "", str(tmp_path / "empty")]
    )

    roots = doctor._torch_install_roots()

    assert roots == [str(a / "torch"), str(b / "torch")]


def test_native_payload_context_handles_unresolvable_roots(doctor):
    """Never raise on a torch we could not locate."""
    frag = doctor._torch_native_payload_context("<not found on sys.path>")
    assert "torch_lib_dir_exists=False" in frag


# =====================================================================
# 3. file_integrity looked in the wrong tree
# =====================================================================


def test_deep_probe_checks_file_integrity_against_the_resource_root(
    monkeypatch, tmp_path
):
    """The #79 bundle flagged all 11 shipped files missing because the
    probe searched the data root."""
    from modelhub.diagnostics import health_probe  # noqa: PLC0415

    data_root = tmp_path / "AppData" / "Local" / "com.bot.mmorpg.ai"
    resource_root = tmp_path / "Program Files" / "BOT-MMORPG-AI"
    data_root.mkdir(parents=True)
    resource_root.mkdir(parents=True)

    # Lay down the shipped files where they really live.
    for rel in health_probe._CRITICAL_FILES:
        target = resource_root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"payload")

    monkeypatch.setenv("MODELHUB_DATA_ROOT", str(data_root))
    monkeypatch.setenv("MODELHUB_RESOURCE_ROOT", str(resource_root))

    out = health_probe.deep_probe()

    statuses = {row["path"]: row["status"] for row in out["file_integrity"]}
    missing = sorted(p for p, s in statuses.items() if s == "missing")
    assert not missing, f"present files reported missing: {missing}"
    assert out["resource_root"] == str(resource_root.resolve())
    assert out["data_root"] == str(data_root.resolve())


def test_deep_probe_still_reports_genuinely_missing_files(monkeypatch, tmp_path):
    """The fix must not turn the check into a rubber stamp."""
    from modelhub.diagnostics import health_probe  # noqa: PLC0415

    data_root = tmp_path / "data"
    resource_root = tmp_path / "install"
    data_root.mkdir()
    resource_root.mkdir()
    monkeypatch.setenv("MODELHUB_DATA_ROOT", str(data_root))
    monkeypatch.setenv("MODELHUB_RESOURCE_ROOT", str(resource_root))

    out = health_probe.deep_probe()

    statuses = {row["status"] for row in out["file_integrity"]}
    assert statuses == {"missing"}


def test_deep_probe_falls_back_to_the_data_root(monkeypatch, tmp_path):
    """Callers with one combined tree (and no MODELHUB_RESOURCE_ROOT)
    must behave exactly as before."""
    from modelhub.diagnostics import health_probe  # noqa: PLC0415

    combined = tmp_path / "combined"
    combined.mkdir()
    monkeypatch.setenv("MODELHUB_DATA_ROOT", str(combined))
    monkeypatch.delenv("MODELHUB_RESOURCE_ROOT", raising=False)
    monkeypatch.delenv("BOT_INSTALL_DIR", raising=False)

    out = health_probe.deep_probe()

    assert out["resource_root"] == str(combined.resolve())


def test_resolve_resource_root_ignores_a_nonexistent_env_path(monkeypatch, tmp_path):
    from modelhub.diagnostics import health_probe  # noqa: PLC0415

    data_root = tmp_path / "data"
    data_root.mkdir()
    monkeypatch.setenv(
        "MODELHUB_RESOURCE_ROOT", str(tmp_path / "does" / "not" / "exist")
    )

    assert health_probe._resolve_resource_root(data_root) == data_root


# =====================================================================
# 4. "Install health: ERROR --" with no reason
# =====================================================================


def test_install_health_log_line_uses_the_merged_checks():
    js = UI_JS.read_text(encoding="utf-8", errors="replace")
    start = js.index("banner.hidden = false;")
    end = js.index("install-health-dismiss", start)
    block = js[start:end]

    assert "h.issues" in block, "legacy fallback should still be present"
    assert re.search(r"errs\.length\s*\?\s*errs\s*:\s*warns", block), (
        "The log line must be built from the merged `checks` array -- "
        "runtime-doctor failures never appear in the legacy `h.issues` "
        "array, which is why issue #79 logged a bare 'ERROR --'."
    )
    assert "no per-check detail reported" in block, (
        "An error verdict with nothing after the dashes is unusable in a "
        "pasted bug report; say so explicitly instead."
    )


def test_doctor_rows_have_ui_labels():
    """A doctor check with no labelMap entry renders its raw snake_case
    name in the banner."""
    js = UI_JS.read_text(encoding="utf-8", errors="replace")
    start = js.index("const labelMap = {")
    end = js.index("};", start)
    labelled = set(re.findall(r"(\w+):\s*\"", js[start:end]))

    doctor_src = DOCTOR_PATH.read_text(encoding="utf-8", errors="replace")
    reg_start = doctor_src.index("    name_for: dict = {")
    reg_end = doctor_src.index("    }", reg_start)
    registered = set(re.findall(r':\s*"(\w+)"', doctor_src[reg_start:reg_end]))
    registered.add("data_dir_writable")  # supplied via the lambda default

    unlabelled = sorted(registered - labelled)
    assert not unlabelled, f"doctor checks with no UI label: {unlabelled}"
