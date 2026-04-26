"""
FastAPI router exposing the diagnostic ring buffer to the Tauri Rust
side. Mounted at /diagnostics by modelhub.tauri.main().

All routes are read-only (GET) except `clear` (DELETE). No mutating
operation here can affect the rest of the sidecar — by construction
the diagnostic layer only observes.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Header, HTTPException

from . import collector, formatter, health_probe

router = APIRouter(prefix="/diagnostics", tags=["diagnostics"])


def _auth_or_401(provided: Optional[str], expected: Optional[str]) -> None:
    """
    Same lightweight token check as the rest of the sidecar uses.
    The token is set by the Rust launcher at process spawn and held
    inside the launcher's SidecarApi struct. Without this, anyone on
    the local machine could read these routes.
    """
    if not expected:
        # Token wasn't configured (dev mode usually). Skip auth.
        return
    if provided != expected:
        raise HTTPException(status_code=401, detail="invalid x-auth-token")


def make_router(
    *, expected_token: Optional[str], repo_root: Optional[str] = None
) -> APIRouter:
    """
    Factory so modelhub.tauri can pass the same token + repo root used
    by the rest of its routes. Returns the configured APIRouter.
    """

    @router.get("/recent")
    async def recent(
        limit: int = 50,
        x_auth_token: Optional[str] = Header(default=None),
    ) -> List[Dict[str, Any]]:
        _auth_or_401(x_auth_token, expected_token)
        return collector.recent_errors(limit=limit)

    @router.get("/recent/ai")
    async def recent_ai(
        limit: int = 50,
        x_auth_token: Optional[str] = Header(default=None),
    ) -> Dict[str, Any]:
        """
        Returns the structured (per-entry dict) form. The full Markdown
        bundle is built on the Rust side so it can include the in-app
        log tail without round-tripping that big string over HTTP.
        """
        _auth_or_401(x_auth_token, expected_token)
        entries = collector.recent_errors(limit=limit)
        return {
            "ok": True,
            "count": len(entries),
            "entries": [formatter.format_one(e, repo_root=repo_root) for e in entries],
        }

    @router.get("/recent/markdown")
    async def recent_markdown(
        limit: int = 50,
        x_auth_token: Optional[str] = Header(default=None),
    ) -> Dict[str, Any]:
        """
        Convenience endpoint that returns the full Markdown bundle.
        Useful if a user copies via curl rather than the in-app button.
        """
        _auth_or_401(x_auth_token, expected_token)
        entries = collector.recent_errors(limit=limit)
        bundle = formatter.format_bundle(
            entries,
            repo_root=repo_root,
            install_dir=os.environ.get("MODELHUB_DATA_ROOT", ""),
        )
        return {"ok": True, "bundle": bundle}

    @router.delete("/recent")
    async def clear(
        x_auth_token: Optional[str] = Header(default=None),
    ) -> Dict[str, Any]:
        _auth_or_401(x_auth_token, expected_token)
        cleared = collector.clear()
        return {"ok": True, "cleared": cleared}

    @router.get("/deep_probe")
    async def deep_probe(
        x_auth_token: Optional[str] = Header(default=None),
    ) -> Dict[str, Any]:
        """
        Returns a deep system probe (system info, disk, network, file
        integrity, embedded-Python health, environment, antivirus
        hint). Fired by the Rust side when verdict != "ready" so the
        AI bundle and support report have enough context for
        root-cause analysis without follow-up questions.

        Pure read-only: every probe is wrapped in try/except inside
        health_probe.deep_probe so this route never raises.
        """
        _auth_or_401(x_auth_token, expected_token)
        install_dir = os.environ.get("MODELHUB_DATA_ROOT", "").strip()
        result = health_probe.deep_probe(
            install_dir=Path(install_dir) if install_dir else None,
        )
        return {"ok": True, "probe": result}

    return router
