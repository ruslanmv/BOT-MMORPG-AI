#!/usr/bin/env python3
"""
runtime_doctor.py -- one-shot self-test for the bundled Python runtime.

Why this exists
---------------
Every previous "the trainer crashed mysteriously" bug had the same
shape:

  1. Build pipeline pruned a runtime-required submodule (torch.testing)
  2. CI smoke test passed because it ran BEFORE the prune
  3. User clicked Train, hit ModuleNotFoundError, then 0xC0000005 on
     interpreter shutdown
  4. The Tauri UI surfaced a generic "Process finished: exit_code=
     -1073741819" with no context

This script runs AFTER pruning (during build) and on every UI launch
(against the actually-installed runtime). It produces deterministic
JSON that the Tauri shell can interpret to show a green / yellow /
red banner. Each check has a stable name -- so a failing torch
sub-import becomes "torch_intact: error: ModuleNotFoundError ..."
instead of an opaque exit code.

Usage
-----
  python runtime_doctor.py --selftest          # default: JSON to stdout
  python runtime_doctor.py --selftest --pretty # human-readable
  python runtime_doctor.py --version

Exit codes
----------
  0  -- verdict == "ok"
  1  -- verdict == "warning"
  2  -- verdict == "error"
  3  -- doctor itself crashed (should never happen)

Output schema
-------------
  {
    "doctor_version": "1.1.0",
    "verdict": "ok" | "warning" | "error",
    "elapsed_ms": int,
    "platform": {os, python_version, executable, prefix},
    "checks": [
      {name: str, status: "ok" | "warn" | "error", detail: str,
       elapsed_ms: int},
      ...
    ]
  }

Design rules
------------
- Single file, stdlib-only entrypoint. The doctor itself must boot
  even when the bundled site-packages is half-broken -- so the top
  of this script imports nothing beyond stdlib. Each check imports
  its own deps lazily and catches BaseException so one broken check
  cannot poison the others.
- Never raises out of main(). Doctor crashes are themselves a
  diagnostic signal -- captured into the JSON, not re-raised.
- Vendor-neutral output. No "Claude Code" / "Anthropic" / specific
  AI assistant branding -- the JSON is consumed by whatever frontend.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import platform as _platform
import socket
import sys
import time
from dataclasses import asdict, dataclass, field
from typing import Callable, List, Optional

DOCTOR_VERSION = "1.1.0"


# --------------------------------------------------------------------------
# Result types
# --------------------------------------------------------------------------


@dataclass
class CheckResult:
    name: str
    status: str  # "ok" | "warn" | "error"
    detail: str
    elapsed_ms: int = 0


@dataclass
class DoctorReport:
    doctor_version: str = DOCTOR_VERSION
    verdict: str = "ok"  # "ok" | "warning" | "error"
    elapsed_ms: int = 0
    platform: dict = field(default_factory=dict)
    checks: List[CheckResult] = field(default_factory=list)


# --------------------------------------------------------------------------
# Check primitives
# --------------------------------------------------------------------------


def _run_check(name: str, fn: Callable[[], CheckResult]) -> CheckResult:
    """Wrap a check with timing + bulletproof error capture.

    A check function that raises ANY exception (including SystemExit
    from a misbehaving import side effect) is converted into an
    error-status CheckResult, never re-raised. This is the single
    most important invariant: one broken check cannot poison the
    rest of the report.
    """
    t0 = time.perf_counter()
    try:
        result = fn()
        if not isinstance(result, CheckResult):  # defensive
            result = CheckResult(name, "error", f"check returned non-CheckResult: {type(result).__name__}")
    except BaseException as e:  # noqa: BLE001 -- intentional broad catch
        result = CheckResult(name, "error", f"{type(e).__name__}: {e}")
    result.name = name  # force-correct in case the check forgot
    result.elapsed_ms = int((time.perf_counter() - t0) * 1000)
    return result


def _check_python_boot() -> CheckResult:
    return CheckResult(
        "python_boot",
        "ok",
        f"Python {sys.version.split()[0]} on {sys.platform} ({sys.executable})",
    )


def _check_vc_redist() -> CheckResult:
    """Probe Visual C++ 2015-2022 redistributable on Windows.

    A torch wheel with native extensions silently fails to load if
    the matching VC++ runtime isn't on the system. The error surfaces
    as 'OSError: [WinError 126] The specified module could not be
    found' or sometimes a teardown crash. Detecting the missing redist
    here gives a one-line cause instead.
    """
    if sys.platform != "win32":
        return CheckResult("vc_redist", "ok", "skipped (not Windows)")
    # Probe both DLLs that torch transitively needs.
    needed = ["vcruntime140.dll", "vcruntime140_1.dll", "msvcp140.dll"]
    missing: List[str] = []
    sys32 = os.environ.get("SystemRoot", r"C:\Windows") + r"\System32"
    for dll in needed:
        if not os.path.exists(os.path.join(sys32, dll)):
            missing.append(dll)
    if missing:
        return CheckResult(
            "vc_redist",
            "error",
            "Missing Visual C++ runtime DLLs: " + ", ".join(missing) + ". "
            "Install vc_redist.x64.exe from Microsoft.",
        )
    return CheckResult("vc_redist", "ok", "Visual C++ 2015-2022 x64 runtime present")


def _resolve_pkg_root(pkg: str) -> str:
    """Return the on-disk directory of an importable package, or a
    sentinel string. Used by the enriched failure paths below to give
    the operator (and any AI assistant reading the bundle) the exact
    path to inspect when a sub-import fails."""
    spec = importlib.util.find_spec(pkg)
    if spec and getattr(spec, "origin", None):
        return os.path.dirname(spec.origin)
    if spec and getattr(spec, "submodule_search_locations", None):
        # Namespace / package without origin -- pick the first location.
        try:
            return next(iter(spec.submodule_search_locations))
        except StopIteration:
            pass
    return "<not found on sys.path>"


def _missing_submodule_context(pkg_root: str, missing: str) -> str:
    """Describe where a missing submodule *should* live on disk.

    Issue #75: users reported `No module named 'torch._strobelight'`
    while the doctor's detail talked exclusively about torch/testing/ --
    one bundle even showed `torch_testing_dir_exists=True` right next to
    advice to un-quarantine torch/testing. The name of the module that
    actually failed, and whether ITS directory exists, is the
    diagnostic; the torch.testing story was a hard-coded leftover from
    the first bug of this class.

    Returns a "path=... exists=..." fragment, or "" when we can't map it.
    """
    if not missing or pkg_root == "<not found on sys.path>":
        return ""
    parts = missing.split(".")
    if len(parts) < 2:
        return ""
    # torch._strobelight -> <torch_root>/_strobelight
    rel = os.path.join(*parts[1:])
    candidate = os.path.join(pkg_root, rel)
    exists = os.path.isdir(candidate) or os.path.isfile(candidate + ".py")
    return f" | missing_module_path={candidate} | missing_module_path_exists={exists}"


def _check_torch_intact() -> CheckResult:
    # The whole reason this doctor exists: a previous build prune
    # deleted torch/testing/. Verify the FULL torch surface, not
    # just the top-level package.
    #
    # `import torch` alone is NOT sufficient: torch's own __init__ pulls
    # in a long tail of private subpackages (torch._strobelight among
    # them, issue #75), so a partial extract that loses one of those
    # fails at `import torch` with a name the operator has never heard
    # of. We probe the public surface explicitly and let the exception
    # carry whichever private module actually went missing.
    import importlib

    submodules = ["torch", "torch.testing", "torch.fx", "torch.nn", "torch.utils.data"]
    try:
        for sub in submodules:
            importlib.import_module(sub)
        import torch  # noqa: F811 -- second import is cached
        return CheckResult(
            "torch_intact",
            "ok",
            f"torch {torch.__version__} -- all required submodules importable",
        )
    except BaseException as e:  # noqa: BLE001
        # Add deterministic, actionable context for the two most common
        # production failures: missing subpackages after partial extract /
        # AV quarantine, and DLL-load crashes from wheel corruption. The
        # `torch_testing_dir_exists` boolean is the smoking gun for the
        # AV-quarantine pattern: if Python can't import torch AND the
        # testing directory is gone from disk, an external actor
        # (Defender, corporate AV) deleted it after extraction.
        torch_root = _resolve_pkg_root("torch")
        testing_dir = (
            os.path.join(torch_root, "testing")
            if torch_root != "<not found on sys.path>"
            else "<unknown>"
        )
        testing_exists = os.path.isdir(testing_dir) if testing_dir != "<unknown>" else False

        # Which module actually failed? ModuleNotFoundError carries it on
        # `.name`; fall back to parsing the message for other importers.
        missing = getattr(e, "name", "") or ""
        if not missing:
            import re as _re

            m = _re.search(r"No module named '([^']+)'", str(e))
            missing = m.group(1) if m else ""

        detail = (
            f"{type(e).__name__}: {e} | torch_root={torch_root} | "
            f"torch_testing_dir_exists={testing_exists}"
        )
        if missing:
            detail += f" | missing_module={missing}"
            detail += _missing_submodule_context(torch_root, missing)
        detail += ". "

        # Remediation, tailored to the failure that actually happened.
        # Recommending "AV exclusion then Repair Runtime" for a module
        # the shipped zip never contained sends users in a circle --
        # which is exactly what issue #75 reported after following the
        # old advice.
        if missing and missing != "torch.testing" and testing_exists:
            detail += (
                f"The rest of torch is present, so this is not a broad "
                f"quarantine -- '{missing}' alone is missing from the "
                "installed package. Re-extracting the same bundle will not "
                "add a file it never had: use [Repair PyTorch via pip] "
                "(Settings -> System Tools), which downloads a fresh torch "
                "wheel from upstream. Add the AV exclusion first if you run "
                "third-party antivirus."
            )
        else:
            detail += (
                "Likely partial/corrupted runtime extract or antivirus "
                "quarantine. Click [Add AV Exclusion] then [Repair Runtime] "
                "in the UI -- the order matters: AV exclusion first prevents "
                "the re-quarantine of torch/testing/ during re-extraction. "
                "If that does not clear it, use [Repair PyTorch via pip]."
            )

        return CheckResult("torch_intact", "error", detail)


def _check_torchvision_intact() -> CheckResult:
    try:
        import torchvision

        return CheckResult(
            "torchvision_intact",
            "ok",
            f"torchvision {torchvision.__version__} importable",
        )
    except BaseException as e:  # noqa: BLE001
        # When torch_intact above failed, torchvision's `import torch.nn`
        # hits a half-initialised torch module and raises a circular
        # import. Surface that causal chain explicitly so the operator
        # doesn't think torchvision itself is broken when the real fix
        # is upstream in torch_intact.
        return CheckResult(
            "torchvision_intact",
            "error",
            f"{type(e).__name__}: {e}. "
            "If torch_intact above also reports an error, this is "
            "downstream collateral -- fixing torch_intact (Repair Runtime / "
            "AV exclusion) will recover torchvision automatically.",
        )


def _check_numpy_intact() -> CheckResult:
    import importlib

    try:
        importlib.import_module("numpy")
        importlib.import_module("numpy.testing")  # transitively used by torch on some platforms
        import numpy

        return CheckResult(
            "numpy_intact",
            "ok",
            f"numpy {numpy.__version__} -- numpy.testing importable",
        )
    except BaseException as e:  # noqa: BLE001
        numpy_root = _resolve_pkg_root("numpy")
        testing_dir = (
            os.path.join(numpy_root, "testing")
            if numpy_root != "<not found on sys.path>"
            else "<unknown>"
        )
        testing_exists = os.path.isdir(testing_dir) if testing_dir != "<unknown>" else False
        return CheckResult(
            "numpy_intact",
            "error",
            f"{type(e).__name__}: {e} | numpy_root={numpy_root} | "
            f"numpy_testing_dir_exists={testing_exists}. "
            "Same failure class as torch_intact (partial extract or AV "
            "quarantine). Run [Add AV Exclusion] -> [Repair Runtime].",
        )


def _check_fastapi_intact() -> CheckResult:
    import fastapi
    import uvicorn

    return CheckResult(
        "fastapi_intact",
        "ok",
        f"fastapi {fastapi.__version__}, uvicorn {uvicorn.__version__}",
    )


def _check_cv2_intact() -> CheckResult:
    import cv2

    return CheckResult(
        "cv2_intact",
        "ok",
        f"opencv-python {cv2.__version__}",
    )


def _check_data_dir_writable(data_dir: Optional[str]) -> CheckResult:
    """Probe whether the operator's local data dir accepts writes.

    The Tauri shell passes the resolved %LOCALAPPDATA% path via the
    --data-dir flag (Batch 1 / MVP-1). If the doctor is run standalone
    we fall back to a short-lived temp file as the probe target.
    """
    import tempfile

    if data_dir:
        target = data_dir
    else:
        target = tempfile.gettempdir()
    try:
        os.makedirs(target, exist_ok=True)
        probe = os.path.join(target, ".runtime_doctor_probe")
        with open(probe, "w") as f:
            f.write("ok")
        os.remove(probe)
    except BaseException as e:  # noqa: BLE001
        return CheckResult(
            "data_dir_writable",
            "error",
            f"Cannot write to {target}: {type(e).__name__}: {e}",
        )
    return CheckResult("data_dir_writable", "ok", f"{target} is writable")


def _check_sidecar_port_bindable() -> CheckResult:
    """Bind ephemeral 127.0.0.1:0 -- proves the loopback stack works.

    Doesn't check a specific port (the sidecar picks ephemeral too);
    only that we can bind localhost at all. Catches misconfigured
    firewalls / VPN lockdowns that block loopback.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    finally:
        s.close()
    return CheckResult(
        "sidecar_port_bindable",
        "ok",
        f"loopback bind succeeded on ephemeral port {port}",
    )


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------


def run_selftest(data_dir: Optional[str] = None) -> DoctorReport:
    """Execute every check, build the report, derive the verdict."""
    t0 = time.perf_counter()
    report = DoctorReport()
    report.platform = {
        "os": sys.platform,
        "python_version": sys.version.split()[0],
        "executable": sys.executable,
        "prefix": sys.prefix,
        "machine": _platform.machine(),
    }

    checks: List[Callable[[], CheckResult]] = [
        _check_python_boot,
        _check_vc_redist,
        _check_torch_intact,
        _check_torchvision_intact,
        _check_numpy_intact,
        _check_fastapi_intact,
        _check_cv2_intact,
        lambda: _check_data_dir_writable(data_dir),
        _check_sidecar_port_bindable,
    ]
    name_for: dict = {
        _check_python_boot: "python_boot",
        _check_vc_redist: "vc_redist",
        _check_torch_intact: "torch_intact",
        _check_torchvision_intact: "torchvision_intact",
        _check_numpy_intact: "numpy_intact",
        _check_fastapi_intact: "fastapi_intact",
        _check_cv2_intact: "cv2_intact",
        _check_sidecar_port_bindable: "sidecar_port_bindable",
    }
    for chk in checks:
        # The lambda for data_dir_writable doesn't appear in the dict;
        # _run_check forces the name on the result anyway.
        name = name_for.get(chk, "data_dir_writable")
        report.checks.append(_run_check(name, chk))

    if any(c.status == "error" for c in report.checks):
        report.verdict = "error"
    elif any(c.status == "warn" for c in report.checks):
        report.verdict = "warning"
    else:
        report.verdict = "ok"

    report.elapsed_ms = int((time.perf_counter() - t0) * 1000)
    return report


def report_to_json(report: DoctorReport, pretty: bool = False) -> str:
    payload = asdict(report)
    if pretty:
        return json.dumps(payload, indent=2)
    return json.dumps(payload, separators=(",", ":"))


def verdict_to_exit_code(verdict: str) -> int:
    return {"ok": 0, "warning": 1, "error": 2}.get(verdict, 3)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="runtime_doctor",
        description="Self-test for the bundled BOT-MMORPG-AI Python runtime.",
    )
    parser.add_argument("--selftest", action="store_true", help="Run all checks (default)")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print the JSON output")
    parser.add_argument("--data-dir", default=None, help="Local data dir to probe for writability")
    parser.add_argument("--version", action="store_true", help="Print doctor version and exit")
    args = parser.parse_args(argv)

    if args.version:
        print(DOCTOR_VERSION)
        return 0

    # Default action is --selftest. We accept the explicit flag for
    # clarity in scripts but don't require it.
    try:
        report = run_selftest(data_dir=args.data_dir)
        print(report_to_json(report, pretty=args.pretty))
        return verdict_to_exit_code(report.verdict)
    except BaseException as e:  # noqa: BLE001
        # Doctor itself crashed -- emit a minimal error report so
        # the caller still gets actionable JSON.
        crash_report = DoctorReport(
            verdict="error",
            checks=[CheckResult("doctor_self", "error", f"{type(e).__name__}: {e}")],
            platform={
                "os": sys.platform,
                "python_version": sys.version.split()[0],
                "executable": sys.executable,
            },
        )
        print(report_to_json(crash_report, pretty=args.pretty))
        return 3


if __name__ == "__main__":
    sys.exit(main())
