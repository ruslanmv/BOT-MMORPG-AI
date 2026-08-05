"""
Deep system probe for the AI debug bundle.

Fired when verdict != "ready" so the bundle has enough context for an
AI assistant to diagnose installer / runtime issues without a back-
and-forth with the user. Pure stdlib (no psutil, no ctypes magic
unless wrapped in try/except). Privacy-first: every field that could
contain secrets is filtered or redacted.

Modeled on AAA-launcher diagnostics:
  - Steam "Show System Information"  -> hardware + driver + OS build
  - Battle.net "Open Tool"            -> file integrity check
  - Bungie Help Tool                  -> network + path hazards
  - Riot Vanguard support bundle      -> environment + antivirus

Categories captured:
  system          OS, arch, CPU count, Python version
  memory          total + available RAM (best-effort)
  disk            free space at install_dir + tempdir
  filesystem      Program Files / OneDrive / long-path / read-only flags
  network         loopback binds, free-port probe
  python_runtime  embedded python.exe presence + version + key imports
  file_integrity  size + SHA-256 prefix of critical bundled files
  environment     filtered subset of env vars we set ourselves
  antivirus       hint at running AV (Defender / McAfee / Norton / etc.)
"""

from __future__ import annotations

import hashlib
import os
import platform
import shutil
import socket
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Issue #76: every subprocess we read text from must pin an explicit
# encoding AND an error handler.
#
# The sidecar runs under PYTHONUTF8=1 / PYTHONIOENCODING=utf-8 (set by
# the Tauri shell), so `text=True` decodes child output as UTF-8. Windows
# console tools do not honour that -- on a Russian install `tasklist`
# emits cp866, and the first Cyrillic byte blew up inside
# subprocess's reader THREAD:
#
#   Exception in thread Thread-13 (_readerthread):
#     File "subprocess.py", line 1515, in _readerthread
#     File "codecs.py", line 322, in decode
#   UnicodeDecodeError: 'utf-8' codec can't decode byte 0x8a in position 44
#
# Because that raises off the main thread, `subprocess.run` returned a
# CompletedProcess with stdout=None instead of propagating; the AV probe
# then died on `rc.stdout.lower()` and every debug bundle from a
# non-English Windows was missing its antivirus section while the
# training log filled with tracebacks that looked like a training crash.
#
# errors="replace" keeps the probe lossy-but-alive: a mojibake process
# name is still greppable, an exploded reader thread is not.
_SUBPROCESS_TEXT_KWARGS: Dict[str, Any] = {
    "capture_output": True,
    "text": True,
    "encoding": "utf-8",
    "errors": "replace",
}

# How many bytes of each file to hash when computing the integrity prefix.
# Full-file hash on python-runtime.zip (~220 MB) would block the UI for
# seconds; first 1 MB is plenty to catch truncation / corruption.
_HASH_BYTES = 1 * 1024 * 1024
# Truncate the hex digest to keep the bundle paste-friendly.
_HASH_DIGEST_PREFIX = 12

# Critical bundled files. Relative to install_dir. Order matters: the
# first missing one is usually the bug, so we list things in install
# order so an AI assistant can stop reading at the first [MISSING].
_CRITICAL_FILES = [
    "BOT-MMORPG-AI.exe",
    "Uninstall.exe",
    "resources/runtime/python-runtime.zip",
    "resources/backend/entry_main.py",
    "resources/backend/main_backend.py",
    "resources/modelhub/tauri.py",
    "resources/versions/0.01/1-collect_data.py",
    "resources/versions/0.01/2-train_model.py",
    "resources/versions/0.01/3-test_model.py",
    "drivers/interception/install-interception.exe",
    "drivers/vjoy/vJoySetup.exe",
]

# Env vars we set ourselves — safe to dump verbatim. Anything else
# (notably API keys, tokens) gets redacted by _redact_env() below.
_OWN_ENV_VARS = [
    "BOT_VERSION_DIR",
    "MODELHUB_RESOURCE_ROOT",
    "MODELHUB_DATA_ROOT",
    "PYTHONUNBUFFERED",
    "PYTHONUTF8",
    "PYTHONIOENCODING",
    "BOTMMO_CAPTURE_MOUSE",
]


# ---------------------------------------------------------------------
# System
# ---------------------------------------------------------------------


def _system_info() -> Dict[str, Any]:
    return {
        "os": platform.platform(),
        "os_release": platform.release(),
        "machine": platform.machine(),
        "processor": platform.processor() or "unknown",
        "cpu_count": os.cpu_count() or 0,
        "python_version": sys.version.split()[0],
        "python_arch": platform.architecture()[0],
        "python_executable": sys.executable,
    }


# ---------------------------------------------------------------------
# Memory (best-effort; never raises)
# ---------------------------------------------------------------------


def _memory_info() -> Dict[str, Any]:
    """
    Try ctypes on Windows (GlobalMemoryStatusEx), /proc/meminfo on
    Linux. Returns {} if neither path works, since memory info is
    nice-to-have, not critical for installer diagnostics.
    """
    out: Dict[str, Any] = {}
    try:
        if platform.system() == "Windows":
            import ctypes

            class _MemStatus(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]

            stat = _MemStatus()
            stat.dwLength = ctypes.sizeof(_MemStatus)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
            out["total_gb"] = round(stat.ullTotalPhys / 1024**3, 1)
            out["available_gb"] = round(stat.ullAvailPhys / 1024**3, 1)
            out["load_pct"] = int(stat.dwMemoryLoad)
        elif Path("/proc/meminfo").exists():
            kv = {}
            for line in Path("/proc/meminfo").read_text().splitlines():
                k, _, v = line.partition(":")
                kv[k.strip()] = v.strip()
            total_kb = int(kv.get("MemTotal", "0 kB").split()[0])
            avail_kb = int(kv.get("MemAvailable", "0 kB").split()[0])
            out["total_gb"] = round(total_kb / 1024 / 1024, 1)
            out["available_gb"] = round(avail_kb / 1024 / 1024, 1)
    except Exception as e:  # noqa: BLE001
        out["error"] = f"memory probe failed: {type(e).__name__}"
    return out


# ---------------------------------------------------------------------
# Disk
# ---------------------------------------------------------------------


def _disk_info(install_dir: Path) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for label, path in (("install", install_dir), ("temp", Path(_safe_tempdir()))):
        try:
            usage = shutil.disk_usage(str(path))
            out[label] = {
                "free_gb": round(usage.free / 1024**3, 1),
                "total_gb": round(usage.total / 1024**3, 1),
                "used_pct": (
                    round(100 * (usage.total - usage.free) / usage.total, 1)
                    if usage.total
                    else 0.0
                ),
            }
        except Exception as e:  # noqa: BLE001
            out[label] = {"error": f"{type(e).__name__}: {e}"}
    return out


def _safe_tempdir() -> str:
    import tempfile

    try:
        return tempfile.gettempdir()
    except Exception:  # noqa: BLE001
        return os.environ.get("TEMP", os.environ.get("TMP", "/tmp"))


# ---------------------------------------------------------------------
# Filesystem hazards (the Windows-on-Program-Files / OneDrive / long-
# path triple-witching that breaks installers in subtle ways)
# ---------------------------------------------------------------------


def _filesystem_hazards(install_dir: Path) -> Dict[str, Any]:
    s = str(install_dir)
    return {
        "install_dir": s,
        "is_program_files": _is_under_program_files(s),
        "onedrive_redirected": _is_under_onedrive(s),
        "long_path_support": _check_long_path_support(),
        "install_dir_writable": _is_writable(install_dir),
        "path_length": len(s),
        "path_too_long_warning": len(s) > 200,  # Windows MAX_PATH=260; leave headroom
    }


def _is_under_program_files(path: str) -> bool:
    p = path.replace("\\", "/").lower()
    return p.startswith("c:/program files") or p.startswith("c:/program files (x86)")


def _is_under_onedrive(path: str) -> bool:
    return "onedrive" in path.lower()


def _check_long_path_support() -> Optional[bool]:
    """
    Returns True if Windows long-path support is enabled in the registry,
    False if explicitly disabled, None on non-Windows or query failure.
    Long paths are off by default on Windows 10 < 1607 and need a
    registry tweak; many AppData paths exceed MAX_PATH.
    """
    if platform.system() != "Windows":
        return None
    try:
        import winreg  # type: ignore

        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\FileSystem",
        )
        try:
            value, _ = winreg.QueryValueEx(key, "LongPathsEnabled")
            return bool(value)
        finally:
            winreg.CloseKey(key)
    except Exception:  # noqa: BLE001
        return None


def _is_writable(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".health_probe_writable"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        return True
    except Exception:  # noqa: BLE001
        return False


# ---------------------------------------------------------------------
# Network
# ---------------------------------------------------------------------


def _network_info() -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    # Can we resolve localhost? (Sidecar uses 127.0.0.1.)
    try:
        socket.gethostbyname("localhost")
        out["loopback_resolves"] = True
    except Exception:  # noqa: BLE001
        out["loopback_resolves"] = False
    # Can we bind to a free localhost port? (Sidecar uses port 0 = pick free.)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("127.0.0.1", 0))
        out["free_port"] = s.getsockname()[1]
        s.close()
    except Exception as e:  # noqa: BLE001
        out["bind_error"] = f"{type(e).__name__}: {e}"
    return out


# ---------------------------------------------------------------------
# Embedded Python runtime health
# ---------------------------------------------------------------------


def _embedded_python_health(install_dir: Path) -> Dict[str, Any]:
    py = install_dir / "runtime" / "py" / "python" / "python.exe"
    out: Dict[str, Any] = {
        "embedded_python": str(py),
        "exists": py.exists(),
    }
    if not py.exists():
        return out
    # Run python --version
    try:
        rc = subprocess.run(
            [str(py), "--version"],
            timeout=5,
            **_SUBPROCESS_TEXT_KWARGS,
        )
        out["version"] = ((rc.stdout or "") + (rc.stderr or "")).strip()
        out["runs"] = rc.returncode == 0
    except Exception as e:  # noqa: BLE001
        out["version_error"] = f"{type(e).__name__}: {e}"
        out["runs"] = False
        return out

    # Try importing each critical package via a one-shot subprocess.
    # We do NOT import them in-process because this module runs inside
    # the sidecar; the goal is to test the BUNDLED runtime, not us.
    pkgs = ["fastapi", "uvicorn", "numpy", "torch", "cv2"]
    importable: Dict[str, bool] = {}
    for pkg in pkgs:
        try:
            r = subprocess.run(
                [str(py), "-c", f"import {pkg}"],
                timeout=10,
                **_SUBPROCESS_TEXT_KWARGS,
            )
            importable[pkg] = r.returncode == 0
        except Exception:  # noqa: BLE001
            importable[pkg] = False
    out["importable"] = importable
    return out


# ---------------------------------------------------------------------
# File integrity (size + SHA-256 prefix of the first MB)
# ---------------------------------------------------------------------


def _file_integrity(install_dir: Path) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for rel in _CRITICAL_FILES:
        path = install_dir / rel
        rec: Dict[str, Any] = {"path": rel}
        if not path.exists():
            rec["status"] = "missing"
            out.append(rec)
            continue
        try:
            size = path.stat().st_size
            with path.open("rb") as fh:
                head = fh.read(_HASH_BYTES)
            digest = hashlib.sha256(head).hexdigest()[:_HASH_DIGEST_PREFIX]
            rec["status"] = "ok"
            rec["size"] = size
            rec["sha256_prefix"] = digest
        except Exception as e:  # noqa: BLE001
            rec["status"] = "unreadable"
            rec["error"] = f"{type(e).__name__}: {e}"
        out.append(rec)
    return out


# ---------------------------------------------------------------------
# Environment (filtered)
# ---------------------------------------------------------------------


def _redact_env() -> Dict[str, str]:
    """
    Return only env vars WE set or read. Everything else is filtered to
    avoid leaking PATH-embedded secrets / API keys / OAuth tokens. The
    PATH length is reported as a number (long PATH on Windows can break
    subprocess spawning silently).
    """
    out: Dict[str, str] = {}
    for k in _OWN_ENV_VARS:
        v = os.environ.get(k, "")
        if v:
            out[k] = v
    out["PATH_length"] = str(len(os.environ.get("PATH", "")))
    out["PATHEXT"] = os.environ.get("PATHEXT", "")  # Windows-only, safe
    return out


# ---------------------------------------------------------------------
# Antivirus hint (process-list scan; no network)
# ---------------------------------------------------------------------


def _antivirus_hint() -> Dict[str, Any]:
    """
    AAA convention: AV is the #1 cause of "the installer ran fine but
    the app won't launch". We surface a hint by name-matching against
    known AV processes. We deliberately do NOT make a value judgement
    or flag the AV as a problem — just expose its presence so the
    bundle reader can correlate.
    """
    if platform.system() != "Windows":
        return {"skipped": "non-Windows"}
    suspects = [
        "MsMpEng.exe",  # Windows Defender
        "MsSense.exe",  # Defender for Endpoint
        "mcshield.exe",  # McAfee
        "avp.exe",  # Kaspersky
        "ekrn.exe",  # ESET
        "bdagent.exe",  # Bitdefender
        "avgnt.exe",  # Avira
        "norton.exe",  # Norton
        "vsmon.exe",  # ZoneAlarm
    ]
    found: List[str] = []
    try:
        # tasklist is available on every Windows since XP. CSV format
        # so we don't have to deal with column-aligned parsing.
        rc = subprocess.run(
            ["tasklist", "/FO", "CSV", "/NH"],
            timeout=5,
            **_SUBPROCESS_TEXT_KWARGS,
        )
        if rc.returncode != 0:
            return {"error": f"tasklist exit={rc.returncode}"}
        out_lower = (rc.stdout or "").lower()
        for proc in suspects:
            if proc.lower() in out_lower:
                found.append(proc)
    except Exception as e:  # noqa: BLE001
        return {"error": f"{type(e).__name__}: {e}"}
    return {"detected": found, "candidates_scanned": len(suspects)}


# ---------------------------------------------------------------------
# Public entrypoint
# ---------------------------------------------------------------------


def _resolve_resource_root(data_root: Path) -> Path:
    """Locate the tree that holds the SHIPPED files.

    Issue #79: `deep_probe` passed the data root to every sub-probe,
    including `_file_integrity`. But `_CRITICAL_FILES` are relative to
    the INSTALL directory (`C:\\Program Files\\BOT-MMORPG-AI`), while the
    data root is `%LOCALAPPDATA%\\com.bot.mmorpg.ai` -- two different
    trees since the MVP-1 migration. Every single bundled file therefore
    reported `"status": "missing"`, which makes a debug bundle look like
    a catastrophically broken install and buries whatever the real fault
    was. In the #79 bundle all 11 critical files were flagged missing on
    a machine whose sidecar was running happily off those very files.

    The Rust launcher exports MODELHUB_RESOURCE_ROOT; fall back to the
    data root only when it is absent, so behaviour is unchanged for any
    caller that genuinely has one combined tree.
    """
    env_root = os.environ.get("MODELHUB_RESOURCE_ROOT") or os.environ.get("BOT_INSTALL_DIR")
    if env_root:
        try:
            candidate = Path(env_root).resolve()
            if candidate.exists():
                return candidate
        except Exception:  # noqa: BLE001
            pass
    return data_root


def deep_probe(install_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    Run every probe and return a structured dict. Never raises; each
    sub-probe is wrapped in its own try/except.

    `install_dir` is the DATA root (runtime/, datasets/, models/, logs/)
    and defaults to MODELHUB_DATA_ROOT (set by the Rust launcher), then
    to cwd. File-integrity checks run against the RESOURCE root instead
    -- see `_resolve_resource_root`.
    """
    if install_dir is None:
        install_dir = Path(
            os.environ.get("MODELHUB_DATA_ROOT")
            or os.environ.get("BOT_INSTALL_DIR")
            or os.getcwd()
        ).resolve()

    resource_root = _resolve_resource_root(install_dir)

    out: Dict[str, Any] = {
        "install_dir": str(install_dir),
        # Both roots are reported so a reader can tell at a glance
        # whether a "missing" row means the file is gone or the probe
        # looked in the wrong tree.
        "data_root": str(install_dir),
        "resource_root": str(resource_root),
    }

    for name, fn in [
        ("system", _system_info),
        ("memory", _memory_info),
        ("disk", lambda: _disk_info(install_dir)),
        ("filesystem", lambda: _filesystem_hazards(install_dir)),
        ("network", _network_info),
        ("python_runtime", lambda: _embedded_python_health(install_dir)),
        ("file_integrity", lambda: _file_integrity(resource_root)),
        ("environment", _redact_env),
        ("antivirus", _antivirus_hint),
    ]:
        try:
            out[name] = fn()
        except Exception as e:  # noqa: BLE001
            out[name] = {"error": f"{type(e).__name__}: {e}"}

    return out
