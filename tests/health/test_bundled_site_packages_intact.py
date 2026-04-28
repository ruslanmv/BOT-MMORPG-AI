"""
Regression guard: bundled embedded-Python site-packages must contain
every submodule the runtime actually imports.

Background
----------
v0.0.0-dev shipped with `scripts/build_pipeline.ps1` running a prune
rule `Where-Object { $_.Name -match "^(tests?|testing)$" }` against
the bundled site-packages directory. That regex matches three names:
'test', 'tests', AND 'testing'. The 'testing' match deleted public,
runtime-required submodules of mainstream scientific-Python packages:

  - torch/testing/      (assert_close, make_tensor; transitively
                         imported by torch._dynamo, torch.fx,
                         several modelhub model registries)
  - numpy/testing/      (imported transitively by torch on some
                         platforms during init)
  - pandas/testing/, scipy/testing/, sympy/testing/  (collateral)

User-visible symptom on a clean install:

    [Warning] PyTorch failed to import:
      ModuleNotFoundError: No module named 'torch.testing'
    [Error] PyTorch not available -- training cannot start.
    [System] Process finished: exit_code=-1073741819   <-- 0xC0000005

The 0xC0000005 is a teardown-phase access violation: native extensions
in `torch._C` partially initialized, then Python shutdown ran while
torch.testing's module slot was already gone.

Fix lives in `scripts/build_pipeline.ps1` (regex tightened to
`-ieq "tests"` only, plus a post-prune integrity check). This test is
a belt-and-suspenders check on the SHIPPED installer: it walks the
bundled site-packages directory (when present on the build machine)
and asserts every required submodule directory exists on disk. The
build-pipeline check runs on CI; this test runs on local installer
verification (`make verify` / `verify_installer.ps1`).
"""

from __future__ import annotations

import pathlib
import platform

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]


# Candidate locations for the bundled site-packages, in priority order.
# We probe rather than hard-code so this test works whether you run it:
#   - against a local dev tree where `make build-runtime` produced
#     src-tauri/resources/python/site-packages
#   - against an installed copy at C:\Program Files\BOT-MMORPG-AI\...
#   - inside CI where neither exists (test is then skipped)
_BUNDLED_CANDIDATES = (
    ROOT / "src-tauri" / "resources" / "python" / "site-packages",
    ROOT / "src-tauri" / "resources" / "python" / "Lib" / "site-packages",
    pathlib.Path(r"C:\Program Files\BOT-MMORPG-AI\runtime\py\python\site-packages"),
)


# Submodules that the previous prune rule deleted and that our runtime
# code (or its transitive imports) actually loads. If you add a new
# pruning rule to build_pipeline.ps1, update this list.
_REQUIRED_SUBMODULE_DIRS = (
    "torch/testing",
    "torch/fx",
    "torch/nn",
    "numpy/testing",
)


def _find_bundled_site_packages() -> pathlib.Path | None:
    for cand in _BUNDLED_CANDIDATES:
        if cand.exists() and (cand / "torch").exists():
            return cand
    return None


@pytest.mark.health
def test_bundled_site_packages_has_runtime_submodules():
    sp = _find_bundled_site_packages()
    if sp is None:
        pytest.skip(
            "No bundled site-packages found at any candidate location -- "
            "this test runs against a built/installed copy only."
        )

    missing: list[str] = []
    for rel in _REQUIRED_SUBMODULE_DIRS:
        target = sp / rel
        # Either a directory package (`testing/__init__.py`) or a
        # single-file module (`testing.py`) is acceptable.
        as_dir_init = target / "__init__.py"
        as_module_file = target.with_suffix(".py")
        if as_dir_init.exists() or as_module_file.exists():
            continue
        missing.append(rel)

    assert not missing, (
        "Bundled site-packages is missing runtime-required submodules:\n"
        + "\n".join(f"  - {sp / rel}" for rel in missing)
        + "\n\nThis means the build_pipeline.ps1 prune rule deleted them."
        " Check `Where-Object { $_.Name ... }` filters and ensure none"
        " match 'test' or 'testing' (only 'tests' plural is safe to strip)."
    )


@pytest.mark.health
@pytest.mark.skipif(
    platform.system() != "Windows", reason="Embedded python is Windows-only"
)
def test_bundled_python_can_import_torch_testing():
    """
    Even stronger guard: actually invoke the bundled python.exe and
    have it `import torch.testing`. Catches partial corruption that a
    file-existence check would miss (zero-byte file, broken __init__).
    """
    import subprocess

    sp = _find_bundled_site_packages()
    if sp is None:
        pytest.skip("No bundled site-packages found.")

    py = sp.parent / "python.exe"
    if not py.exists():
        py = sp.parent.parent / "python.exe"
    if not py.exists():
        pytest.skip(f"Bundled python.exe not found near {sp}")

    result = subprocess.run(
        [
            str(py),
            "-c",
            "import torch, torch.testing, torch.fx; print('ok', torch.__version__)",
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, (
        f"Bundled python failed to import torch submodules.\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )
