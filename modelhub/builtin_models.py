# modelhub/builtin_models.py
"""
Builtin (shipping) models that come with the repo.

Goal:
- Make "it works out of the box" possible even before training.
- Treat these as READ-ONLY baseline artifacts, but show them in the same UI list
  as local trained models.

This repo (versions/0.01) produces/uses TF checkpoint artifacts in:
  versions/0.01/model/
    checkpoint
    test.index
    test.data-00000-of-00001
    test.meta

3-test_model.py loads:
  MODEL_NAME = 'model/test'
  model.load(MODEL_NAME)

So the builtin artifact is the checkpoint directory itself.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, List, Optional

from modelhub.action_space import BASE_ACTION_COUNT


@dataclass
class BuiltinModel:
    game_id: str
    model_id: str
    display_name: str
    model_type: str
    architecture: str
    artifact_kind: str  # "tf_checkpoint_dir" | "single_file"
    artifact_path: Path
    notes: str = ""


def _tf_checkpoint_ready(model_dir: Path, prefix: str = "test") -> bool:
    """
    Minimal check for TF checkpoint "prefix":
      - checkpoint file exists
      - <prefix>.index exists
      - <prefix>.data-* exists
    """
    if not model_dir.exists() or not model_dir.is_dir():
        return False
    if not (model_dir / "checkpoint").exists():
        return False
    if not (model_dir / f"{prefix}.index").exists():
        return False
    data_glob = list(model_dir.glob(f"{prefix}.data-*"))
    return len(data_glob) > 0


def list_builtin_models(project_root: Path, game_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Returns builtin models in the SAME SHAPE as modelhub.local_store.discover_local_models()

    Output example:
    {
      "id": "builtin_genshin_v001_test",
      "name": "Builtin • Genshin Impact • v0.01 (test checkpoint)",
      "type": "builtin",
      "architecture": "inception_v3",
      "paths": {
         "dir": ".../versions/0.01/model",
         "model_file": null,
         "profile": null,
         "metrics": null
      },
      "metrics": null,
      "builtin": true,
      "artifact_kind": "tf_checkpoint_dir",
      "run_hint": {
         "cwd": ".../versions/0.01",
         "checkpoint_prefix": "model/test"
      }
    }
    """
    v001 = project_root / "versions" / "0.01"
    builtins: List[BuiltinModel] = []

    # Default/baseline Genshin model (repo default)
    #  - checkpoint lives in versions/0.01/model
    #  - 3-test_model loads "model/test" relative to cwd versions/0.01
    ckpt_dir = v001 / "model"
    if _tf_checkpoint_ready(ckpt_dir, prefix="test"):
        builtins.append(
            BuiltinModel(
                game_id="genshin_impact",
                model_id="builtin_genshin_v001_test",
                display_name="Builtin • Genshin Impact • v0.01 (test checkpoint)",
                model_type="builtin",
                architecture="inception_v3",
                artifact_kind="tf_checkpoint_dir",
                artifact_path=ckpt_dir,
                notes="Ships with the repo (TF checkpoint). Good for sanity testing the pipeline/UI.",
            )
        )

    # Filter by game_id if requested
    if game_id:
        builtins = [b for b in builtins if b.game_id == game_id]

    # Map to UI-friendly dicts
    out: List[Dict[str, Any]] = []
    for b in builtins:
        out.append(
            {
                "id": b.model_id,
                "name": b.display_name,
                "type": b.model_type,
                "architecture": b.architecture,
                "paths": {
                    "dir": str(b.artifact_path),
                    # For checkpoints, there is no single model file to point to
                    "model_file": None,
                    "profile": None,
                    "metrics": None,
                },
                "metrics": None,
                "builtin": True,
                "artifact_kind": b.artifact_kind,
                "notes": b.notes,
                # Helpful hints so the launcher can run test_model correctly
                "run_hint": {
                    "cwd": str(v001),                 # run from versions/0.01
                    "checkpoint_prefix": "model/test" # matches 3-test_model.py
                },
            }
        )
    return out


def ensure_builtin_profile(target_dir: Path, game_id: str = "genshin_impact") -> Path:
    """
    Optional helper:
    Writes a minimal profile.json next to a *copied* builtin model (if you ever archive it),
    but does NOT modify files in versions/0.01.

    Returns path to profile.json.
    """
    import json
    import time

    profile = {
        "profile_name": "Builtin checkpoint",
        "game": game_id,
        "id": target_dir.name,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "type": "builtin",
        "architecture": "inception_v3",
        "format": "tf_checkpoint",
        "input_shape": [480, 270, 3],
        "classes": BASE_ACTION_COUNT,
        "dataset_id": "",
        "notes": "Generated locally from builtin model metadata.",
    }
    target_dir.mkdir(parents=True, exist_ok=True)
    p = target_dir / "profile.json"
    p.write_text(json.dumps(profile, indent=2), encoding="utf-8")
    return p
