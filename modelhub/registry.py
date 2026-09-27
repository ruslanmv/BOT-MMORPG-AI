# modelhub/registry.py
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, List

from modelhub.action_space import BASE_ACTION_COUNT

CATALOG_DIR = Path("catalog")
GAMES_DIR = CATALOG_DIR / "games"


def _read_json(p: Path) -> Dict[str, Any]:
    return json.loads(p.read_text(encoding="utf-8"))


def _write_json(p: Path, data: Dict[str, Any]) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")


def ensure_default_catalog() -> None:
    """
    Ensures catalog files exist so the UI doesn't crash on a fresh install.
    Non-destructive: only creates missing files.
    """
    CATALOG_DIR.mkdir(parents=True, exist_ok=True)
    if not (CATALOG_DIR / "catalog.json").exists():
        _write_json(
            CATALOG_DIR / "catalog.json",
            {"version": "1.0", "games": ["genshin_impact"]},
        )

    # Ensure default game template exists
    genshin_dir = GAMES_DIR / "genshin_impact"
    genshin_dir.mkdir(parents=True, exist_ok=True)
    if not (genshin_dir / "game.json").exists():
        _write_json(
            genshin_dir / "game.json",
            {
                "id": "genshin_impact",
                "display_name": "Genshin Impact",
                "recommended_resolution": [1920, 1080],
                "supported_inputs": ["keyboard", "gamepad"],
                "expected_input_shape": [480, 270, 3],
                "expected_classes": BASE_ACTION_COUNT,
                "notes": "Default blueprint. Local models only by default.",
            },
        )
    if not (genshin_dir / "models.json").exists():
        _write_json(genshin_dir / "models.json", {"models": []})


def list_games() -> List[Dict[str, Any]]:
    """
    Returns all game blueprints in catalog/catalog.json.
    """
    ensure_default_catalog()
    catalog = _read_json(CATALOG_DIR / "catalog.json")
    out: List[Dict[str, Any]] = []

    for gid in catalog.get("games", []):
        gpath = GAMES_DIR / gid / "game.json"
        if gpath.exists():
            out.append(_read_json(gpath))

    # Stable ordering for UI
    out.sort(key=lambda g: (g.get("display_name") or g.get("id") or ""))
    return out


def load_game(game_id: str) -> Dict[str, Any]:
    """
    Loads one game blueprint.
    """
    ensure_default_catalog()
    gpath = GAMES_DIR / game_id / "game.json"
    return _read_json(gpath)


def list_catalog_models(game_id: str) -> List[Dict[str, Any]]:
    """
    Lists models declared in catalog (optional, mostly future use).
    """
    ensure_default_catalog()
    mpath = GAMES_DIR / game_id / "models.json"
    if not mpath.exists():
        return []
    data = _read_json(mpath)
    return data.get("models", [])


def add_or_update_catalog_model(game_id: str, model_entry: Dict[str, Any]) -> None:
    """
    Adds or updates an entry in catalog/games/<game_id>/models.json.
    """
    ensure_default_catalog()
    gdir = GAMES_DIR / game_id
    gdir.mkdir(parents=True, exist_ok=True)

    mpath = gdir / "models.json"
    data: Dict[str, Any] = {"models": []}
    if mpath.exists():
        data = _read_json(mpath)

    models = [m for m in data.get("models", []) if m.get("id") != model_entry.get("id")]
    models.append(model_entry)
    data["models"] = sorted(models, key=lambda x: x.get("id", ""))

    _write_json(mpath, data)
