# modelhub/profile_writer.py
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from modelhub.action_space import BASE_ACTION_COUNT


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def write_profile(target_dir: Path, meta: Dict[str, Any]) -> Dict[str, Any]:
    """
    Writes profile.json to the model directory.

    This repo (versions/0.01) defaults:
    - input images: 480x270 RGB
    - output classes: 29 (9 keyboard + 20 gamepad); a recording made with
      --mouse declares 39 instead, which the compatibility check also accepts.

    We keep this "safe + useful" even for black-box training:
    - If meta provides input_shape / class_count, we store them.
    - Otherwise we store known defaults for Genshin Impact templates.
    """
    game_id = meta.get("game_id", "unknown")

    # Known defaults for this project (versions/0.01)
    default_input_shape: List[int] = [480, 270, 3]
    default_class_count: int = BASE_ACTION_COUNT

    # Allow overrides from meta if you later add detection
    input_shape = meta.get("input_shape") or default_input_shape
    class_count = meta.get("class_count") or default_class_count

    # If someone passes explicit class labels, keep them; otherwise store a count only.
    # (Labels could be added later, but a count is enough for the
    # compatibility check, which accepts either the declared width or the
    # same width plus the mouse block.)
    classes = meta.get("classes")
    if classes is None:
        classes = class_count  # store number (int) rather than a fake list

    profile: Dict[str, Any] = {
        "profile_name": meta.get("model_name", "Unknown Model"),
        "game": game_id,
        "id": meta.get("model_id", ""),
        "created_at": meta.get("created_at", _now_iso()),
        "type": meta.get("type", "model"),
        "architecture": meta.get("architecture", "custom"),
        "format": meta.get("format", "unknown"),  # e.g. "tf_checkpoint", "keras", "torch"
        "input_shape": input_shape,
        "classes": classes,  # either int (count) or list of labels
        "dataset_id": meta.get("dataset_id", ""),
        "notes": meta.get("notes", ""),
    }

    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / "profile.json").write_text(json.dumps(profile, indent=2), encoding="utf-8")
    return profile
