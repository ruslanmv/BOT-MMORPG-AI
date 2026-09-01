# backend/entry_main.py
"""
Entrypoint for the ModelHub/Tauri sidecar.

This file must stay tiny + stable for packaging. It bootstraps
sys.path so the bundled `modelhub` package is importable, then
forwards CLI args to modelhub.tauri.main(argv=...).

Rust should launch (DEV python or PROD embedded python):
  main-backend.exe --port 0 --token <token> --resource-root <...> --data-root <...>

modelhub/tauri.py prints (flush=True):
  READY url=http://127.0.0.1:<port> token=<token>

On ANY failure (including import-time failures before sidecar_main even runs),
this wrapper prints a single canonical line on stderr:
  FAILED error=<ExceptionType>: <message>
followed by the full traceback. The Rust supervisor's stderr reader (in
src-tauri/src/main.rs#start_sidecar_server) fast-fails on the `FAILED ` prefix,
which avoids the 60s READY timeout when the real cause is something we can
detect immediately (ModuleNotFoundError, SyntaxError, missing PYTHONPATH,
DLL load failure, etc.).

PHASE 17 -- WHY WE BOOTSTRAP sys.path HERE
-----------------------------------------
The Rust supervisor sets PYTHONPATH=<install>\resources;... so Python can
find the bundled `modelhub` package. That works in DEV (host venv Python).
It does NOT work in PROD (Windows embedded Python distribution).

Quoting the CPython docs:
  > If <prefix>\python<ver>._pth exists, the PYTHONPATH environment
  > variable is IGNORED, and sys.path is built strictly from the _pth file.
  https://docs.python.org/3/using/windows.html#finding-modules

The build-time _pth patcher (scripts/build_pipeline.ps1 + Rust's
patch_embedded_python_pth) writes:
    python310.zip
    .
    <absolute-path-to-site-packages>
    import site
That gets stdlib + site-packages onto sys.path -- but NOT the install's
resources/ directory where the modelhub package actually lives. PYTHONPATH
is ignored, so the supervisor's env var has zero effect.

Bootstrapping sys.path here, BEFORE the `from modelhub.tauri import ...`
line, makes the entry script self-contained: it works with any python
runtime (host venv, embedded, --isolated) regardless of how PYTHONPATH /
_pth are configured.
"""

from __future__ import annotations

import os
import sys
import traceback
from pathlib import Path
from typing import List


def _bootstrap_sys_path() -> None:
    """Insert the install's `resources/` directory onto sys.path.

    Tries three sources, in priority order:
      1. MODELHUB_RESOURCE_ROOT env var (set by the Rust supervisor) ->
         <root>/resources is the package parent.
      2. The script's own location: entry_main.py lives at
         <install>/resources/backend/entry_main.py, so the package
         parent is __file__'s grandparent.
      3. (Failure case) leave sys.path alone -- the import below will
         raise ModuleNotFoundError, the wrapper will print FAILED + a
         clean traceback, and the supervisor's launch report will name
         the failure precisely.

    Idempotent: re-running this function (e.g. in tests) does not
    duplicate sys.path entries.
    """
    candidates: list[Path] = []

    # 1. Supervisor-provided env var. Most reliable in PROD.
    env_root = os.environ.get("MODELHUB_RESOURCE_ROOT")
    if env_root:
        env_resources = Path(env_root) / "resources"
        if env_resources.is_dir():
            candidates.append(env_resources)
        # Some installs place the resources directory directly under
        # MODELHUB_RESOURCE_ROOT (without an extra "resources" leaf).
        # Accept both layouts.
        env_root_path = Path(env_root)
        if (env_root_path / "modelhub").is_dir():
            candidates.append(env_root_path)

    # 2. Walk up from __file__ as a fallback. Works in DEV when the env
    #    var isn't set, and as a safety net if the supervisor forgot it.
    try:
        here = Path(__file__).resolve()
        # entry_main.py -> backend/ -> resources/
        if here.parent.name == "backend":
            resources_dir = here.parent.parent
            if (resources_dir / "modelhub").is_dir():
                candidates.append(resources_dir)
    except (NameError, OSError):
        pass

    for path in candidates:
        path_str = str(path)
        if path_str not in sys.path:
            # Insert at front so we beat any stale `modelhub` shadow on
            # the path (e.g. a leftover from a previous install).
            sys.path.insert(0, path_str)


def _bootstrap_site_packages() -> None:
    """Put THIS interpreter's own site-packages onto sys.path.

    The bundled runtime installs third-party deps (fastapi, uvicorn,
    torch, numpy, ...) into the embedded interpreter, and the sidecar is
    supposed to see them via the patched `pythonXY._pth` + `import site`.
    Two things break that in the field (issue #85):

      * The Rust supervisor passes an explicit ``PYTHONPATH`` that lists
        ``runtime\\py\\python\\site-packages`` (the build's
        ``pip --target`` location) but NOT the interpreter's standard
        ``Lib\\site-packages``. Any repair that shells out to
        ``pip install`` -- including the app's own "Repair PyTorch via
        pip" -- writes to ``Lib\\site-packages`` by default, so those
        packages land in a directory the sidecar never adds. The result
        is exactly the reported failure: ``No module named 'uvicorn'``
        with a second, shadow ``torch`` tree the doctor warns about.
      * If a repair rewrites ``pythonXY._pth`` without ``import site``,
        the whole site machinery goes quiet and even ``site-packages``
        stops resolving.

    Adding both site directories, derived from ``sys.executable`` /
    ``sys.prefix`` at runtime, makes the sidecar self-sufficient: it
    finds its own installed packages no matter which location a repair
    used and regardless of the supervisor-supplied PYTHONPATH. Appended
    (not inserted at front) so a project checkout on ``sys.path[0]`` still
    wins; guarded by ``is_dir()`` so nonexistent paths are skipped; and
    wrapped so this never raises (a bad path must not abort startup).
    """
    try:
        roots = {Path(sys.prefix)}
        try:
            roots.add(Path(sys.executable).resolve().parent)
        except (OSError, ValueError):
            pass

        # Both layouts the bundled runtime can present:
        #   <prefix>\site-packages     -- pip install --target (build)
        #   <prefix>\Lib\site-packages -- standard install (pip repair)
        for root in roots:
            for rel in ("site-packages", os.path.join("Lib", "site-packages")):
                sp = root / rel
                sp_str = str(sp)
                if sp_str not in sys.path and sp.is_dir():
                    sys.path.append(sp_str)
    except Exception:  # noqa: BLE001 -- bootstrapping must never raise
        pass


def main() -> int:
    # Bootstrap BEFORE the import. If we leave it inside the try/except
    # below, an exception here gets swallowed into the FAILED line --
    # which is fine, but bootstrapping should never raise (we use
    # try/except inside _bootstrap_sys_path to be sure).
    _bootstrap_sys_path()
    _bootstrap_site_packages()

    # Top-level safety net so EVERY launch failure produces a uniform,
    # parseable marker. Without this, an ImportError in
    # `from modelhub.tauri import main` (e.g. a missing dependency, a
    # corrupted .pyd, a broken sys.path) prints a Python traceback to
    # stderr but never the `FAILED ` line -- so the Rust supervisor has
    # to wait the full 60s READY timeout before declaring failure
    # instead of bailing immediately. AAA-grade launchers (Steam,
    # Battle.net) all have this kind of canonical-failure-marker
    # contract between supervisor and child.
    try:
        # Import the real sidecar entrypoint
        from modelhub.tauri import main as sidecar_main

        # Forward args exactly (skip program name)
        argv: List[str] = sys.argv[1:]

        # sidecar_main already returns an int exit code (0/1). Keep it safe anyway.
        rc = sidecar_main(argv)
        return int(rc) if rc is not None else 0
    except KeyboardInterrupt:
        # User-initiated SIGINT. Standard Unix convention: 128 + SIGINT(2) = 130.
        return 130
    except SystemExit:
        # Python's normal exit mechanism. Let it propagate -- if a
        # caller explicitly raised SystemExit, they've already chosen
        # the exit code.
        raise
    except Exception as e:  # noqa: BLE001 -- we deliberately catch everything else
        tb = traceback.format_exc()
        # Two writes, both wrapped in their own try/except so a closed
        # stderr (rare but possible if the parent killed the pipe)
        # still lets us return a non-zero exit code.
        try:
            # Single canonical failure line. Format mirrors the inner
            # FAILED line in modelhub/tauri.py so the Rust parser does
            # not need to special-case the wrapper. Phase 17: include
            # sys.path snapshot in the message so a future
            # ModuleNotFoundError immediately tells you what was on the
            # path -- the next debugger doesn't have to guess whether
            # bootstrap fired.
            sys_path_repr = ";".join(sys.path[:8])  # truncate -- bundle has the rest
            print(
                f"FAILED error={type(e).__name__}: {e} | sys.path[0:8]={sys_path_repr}",
                file=sys.stderr,
                flush=True,
            )
            # Full traceback to stderr so the launch report's
            # stderr_lines and the [Sidecar stderr] terminal lines
            # capture the actual cause for the debug bundle.
            print(tb, file=sys.stderr, flush=True)
        except Exception:  # noqa: BLE001
            pass
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
