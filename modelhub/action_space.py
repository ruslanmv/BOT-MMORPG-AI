# modelhub/action_space.py
"""Output widths a model profile may declare for the pipeline action space.

`collect_data` writes the discrete action slots on their own, and appends a
mouse block to them when it runs with `--mouse`. A model trained from mouse
recordings therefore has more output classes than one trained without it, and
both are valid for the same game blueprint.

The widths are read from `bot_mmorpg.config.action_mapping` so this catalog
tool cannot drift from the recording pipeline. The literals below apply only
when that package is not importable, which keeps the modelhub usable on its own.
"""

#: Discrete action slots recorded without mouse capture (9 keyboard + 20 gamepad).
BASE_ACTION_COUNT = 29

#: Width of the mouse block appended by `collect_data --mouse`.
MOUSE_OUTPUT_SIZE = 10

try:
    from bot_mmorpg.config.action_mapping import (
        DEFAULT_ACTION_SPACE_NAME,
        MOUSE_OUTPUT_SIZE as _RECORDED_MOUSE_WIDTH,
        get_pipeline_action_space,
    )

    BASE_ACTION_COUNT = get_pipeline_action_space(
        DEFAULT_ACTION_SPACE_NAME
    ).num_actions
    MOUSE_OUTPUT_SIZE = _RECORDED_MOUSE_WIDTH
except ImportError:  # pragma: no cover - only when the package is not installed
    pass

#: Output counts a model profile may declare for a pipeline action space.
ACCEPTED_CLASS_COUNTS = (BASE_ACTION_COUNT, BASE_ACTION_COUNT + MOUSE_OUTPUT_SIZE)

#: Extra outputs a recording may append to its discrete slots. A blueprint
#: expecting N discrete classes also accepts a model with N + each of these.
MOUSE_OUTPUT_SIZES = (0, MOUSE_OUTPUT_SIZE)
