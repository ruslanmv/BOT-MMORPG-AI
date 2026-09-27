# modelhub/validator.py
import json
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, Sequence

from modelhub.action_space import MOUSE_OUTPUT_SIZES


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _as_shape(value: Any) -> Tuple[int, ...]:
    """
    Accepts:
      - [480,270,3] -> (480,270,3)
      - (480,270,3) -> (480,270,3)
      - [1,480,270,3] -> (480,270,3) (batch dimension trimmed)
      - None / invalid -> ()
    """
    if not value:
        return ()
    if not isinstance(value, (list, tuple)):
        return ()
    nums = []
    for x in value:
        try:
            nums.append(int(x))
        except Exception:
            return ()
    # Trim batch dimension if present
    if len(nums) == 4 and nums[0] == 1:
        nums = nums[1:]
    return tuple(nums)


def _as_class_count(value: Any) -> Optional[int]:
    """
    Accepts:
      - int -> int
      - "29" -> 29
      - ["W","S",...] -> len(list)
      - None -> None
    """
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value.strip())
        except Exception:
            return None
    if isinstance(value, (list, tuple)):
        return len(value)
    return None


def accepted_class_counts(expected_classes: int) -> Tuple[int, ...]:
    """Class counts a blueprint's expected width may legitimately be recorded at.

    Args:
        expected_classes: The discrete output count the blueprint declares.

    Returns:
        Every accepted output count, narrowest first: the declared width on its
        own, and once more with the mouse block appended.
    """
    return tuple(sorted({int(expected_classes) + extra for extra in MOUSE_OUTPUT_SIZES}))


def validate_compatibility(
    game_blueprint: Dict[str, Any],
    model_profile: Dict[str, Any],
) -> Tuple[bool, str]:
    """
    Checks whether a model profile is compatible with a game blueprint.

    Blueprint expects:
      - id
      - expected_input_shape (e.g. [480,270,3])
      - expected_classes (e.g. 29)

    Profile expects (minimum):
      - profile_name
      - architecture
      - game (optional but recommended)
      - input_shape (recommended)
      - classes (recommended: int count OR list of labels)

    A blueprint expecting 29 discrete outputs also accepts a 39-output model:
    `collect_data --mouse` appends the mouse block to the discrete slots, and
    both widths run through the same bot.
    """
    blueprint_id = game_blueprint.get("id")

    expected_shape = _as_shape(game_blueprint.get("expected_input_shape"))
    expected_classes = _as_class_count(game_blueprint.get("expected_classes"))

    profile_game = model_profile.get("game")
    profile_shape = _as_shape(model_profile.get("input_shape"))
    profile_classes = _as_class_count(model_profile.get("classes"))

    # ---- game id check (only if profile declares it) ----
    if profile_game and blueprint_id and profile_game != blueprint_id:
        return False, f"Profile game '{profile_game}' != blueprint '{blueprint_id}'"

    # ---- shape check (only if both sides declare it) ----
    if expected_shape and profile_shape and expected_shape != profile_shape:
        return False, f"Input shape mismatch: expected {expected_shape}, got {profile_shape}"

    # ---- class count check (only if both sides declare it) ----
    if expected_classes is not None and profile_classes is not None:
        accepted = accepted_class_counts(expected_classes)
        if int(profile_classes) not in accepted:
            return False, (
                f"Class count mismatch: expected "
                f"{' or '.join(str(count) for count in accepted)}, "
                f"got {profile_classes}"
            )

    # ---- required minimum metadata ----
    if not model_profile.get("architecture"):
        return False, "Missing required field: architecture"
    if not model_profile.get("profile_name"):
        return False, "Missing required field: profile_name"

    return True, "OK"
