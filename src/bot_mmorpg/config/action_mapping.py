"""
MMORPG Action Mapping System for BOT-MMORPG-AI

This module defines comprehensive action mappings for MMORPG games,
supporting both keyboard+mouse and gamepad inputs.

Action Categories:
1. Movement: WASD, analog sticks
2. Skills: 1-9, F1-F12, skill combos
3. Combat: Attack, dodge, block, target
4. UI: Inventory, map, menu
5. Communication: Chat, emotes
6. Camera: Mouse look, zoom

Output Design:
- Multi-label: Multiple actions can be active simultaneously
- Continuous: Analog values for movement/camera
- Discrete: Button presses for skills
"""

from dataclasses import dataclass, replace
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple


class ActionCategory(Enum):
    """Categories of game actions."""

    MOVEMENT = auto()  # WASD, run, jump
    SKILLS = auto()  # Hotbar skills 1-9
    COMBAT = auto()  # Attack, dodge, block
    TARGETING = auto()  # Tab-target, click-target
    CAMERA = auto()  # Mouse look, zoom
    UI = auto()  # Inventory, map, menu
    COMMUNICATION = auto()  # Chat, emotes
    MODIFIER = auto()  # Shift, Ctrl, Alt


@dataclass
class ActionDefinition:
    """Definition of a single action."""

    id: int
    name: str
    category: ActionCategory
    key_binding: Optional[str] = None
    gamepad_binding: Optional[str] = None
    is_continuous: bool = False  # True for analog (movement, camera)
    is_toggle: bool = False  # True for toggle states (autorun)
    cooldown_ms: int = 0  # Minimum time between activations
    description: str = ""
    label: str = ""  # Short name used by the inference pipeline (logging/debug)

    def display_label(self) -> str:
        """Label used by the runtime pipeline for logs and debugging."""
        return self.label or self.gamepad_binding or self.name


@dataclass
class ActionGroup:
    """Group of related actions (e.g., movement directions)."""

    name: str
    actions: List[ActionDefinition]
    mutually_exclusive: bool = True  # Can only one be active?


# =============================================================================
# Standard MMORPG Action Definitions
# =============================================================================

# Movement Actions (0-15)
MOVEMENT_ACTIONS = [
    ActionDefinition(
        0,
        "move_forward",
        ActionCategory.MOVEMENT,
        "W",
        "Ly+",
        True,
        description="Move forward",
    ),
    ActionDefinition(
        1,
        "move_backward",
        ActionCategory.MOVEMENT,
        "S",
        "Ly-",
        True,
        description="Move backward",
    ),
    ActionDefinition(
        2,
        "move_left",
        ActionCategory.MOVEMENT,
        "A",
        "Lx-",
        True,
        description="Strafe left",
    ),
    ActionDefinition(
        3,
        "move_right",
        ActionCategory.MOVEMENT,
        "D",
        "Lx+",
        True,
        description="Strafe right",
    ),
    ActionDefinition(
        4,
        "move_forward_left",
        ActionCategory.MOVEMENT,
        "W+A",
        None,
        True,
        description="Move diagonally",
    ),
    ActionDefinition(
        5,
        "move_forward_right",
        ActionCategory.MOVEMENT,
        "W+D",
        None,
        True,
        description="Move diagonally",
    ),
    ActionDefinition(
        6,
        "move_backward_left",
        ActionCategory.MOVEMENT,
        "S+A",
        None,
        True,
        description="Move diagonally",
    ),
    ActionDefinition(
        7,
        "move_backward_right",
        ActionCategory.MOVEMENT,
        "S+D",
        None,
        True,
        description="Move diagonally",
    ),
    ActionDefinition(
        8,
        "jump",
        ActionCategory.MOVEMENT,
        "Space",
        "A",
        cooldown_ms=500,
        description="Jump",
    ),
    ActionDefinition(
        9, "sprint", ActionCategory.MOVEMENT, "Shift", "L3", description="Sprint/Run"
    ),
    ActionDefinition(
        10,
        "crouch",
        ActionCategory.MOVEMENT,
        "Ctrl",
        "R3",
        is_toggle=True,
        description="Crouch/Sneak",
    ),
    ActionDefinition(
        11,
        "dodge",
        ActionCategory.MOVEMENT,
        "Alt",
        "B",
        cooldown_ms=1000,
        description="Dodge roll",
    ),
    ActionDefinition(
        12,
        "mount",
        ActionCategory.MOVEMENT,
        "Z",
        "DOWN",
        cooldown_ms=2000,
        description="Mount/Dismount",
    ),
    ActionDefinition(
        13,
        "autorun",
        ActionCategory.MOVEMENT,
        "NumLock",
        "L3+R3",
        is_toggle=True,
        description="Auto-run toggle",
    ),
    ActionDefinition(
        14, "swim_up", ActionCategory.MOVEMENT, "Space", "A", description="Swim up"
    ),
    ActionDefinition(
        15, "swim_down", ActionCategory.MOVEMENT, "Ctrl", "B", description="Swim down"
    ),
]

# Skill Actions (16-35) - Hotbar slots
SKILL_ACTIONS = [
    ActionDefinition(
        16,
        "skill_1",
        ActionCategory.SKILLS,
        "1",
        "X",
        cooldown_ms=100,
        description="Skill slot 1",
    ),
    ActionDefinition(
        17,
        "skill_2",
        ActionCategory.SKILLS,
        "2",
        "Y",
        cooldown_ms=100,
        description="Skill slot 2",
    ),
    ActionDefinition(
        18,
        "skill_3",
        ActionCategory.SKILLS,
        "3",
        "RB",
        cooldown_ms=100,
        description="Skill slot 3",
    ),
    ActionDefinition(
        19,
        "skill_4",
        ActionCategory.SKILLS,
        "4",
        "LB",
        cooldown_ms=100,
        description="Skill slot 4",
    ),
    ActionDefinition(
        20,
        "skill_5",
        ActionCategory.SKILLS,
        "5",
        "RT+X",
        cooldown_ms=100,
        description="Skill slot 5",
    ),
    ActionDefinition(
        21,
        "skill_6",
        ActionCategory.SKILLS,
        "6",
        "RT+Y",
        cooldown_ms=100,
        description="Skill slot 6",
    ),
    ActionDefinition(
        22,
        "skill_7",
        ActionCategory.SKILLS,
        "7",
        "RT+RB",
        cooldown_ms=100,
        description="Skill slot 7",
    ),
    ActionDefinition(
        23,
        "skill_8",
        ActionCategory.SKILLS,
        "8",
        "RT+LB",
        cooldown_ms=100,
        description="Skill slot 8",
    ),
    ActionDefinition(
        24,
        "skill_9",
        ActionCategory.SKILLS,
        "9",
        "LT+X",
        cooldown_ms=100,
        description="Skill slot 9",
    ),
    ActionDefinition(
        25,
        "skill_0",
        ActionCategory.SKILLS,
        "0",
        "LT+Y",
        cooldown_ms=100,
        description="Skill slot 10",
    ),
    ActionDefinition(
        26,
        "skill_minus",
        ActionCategory.SKILLS,
        "-",
        "LT+RB",
        cooldown_ms=100,
        description="Skill slot 11",
    ),
    ActionDefinition(
        27,
        "skill_equals",
        ActionCategory.SKILLS,
        "=",
        "LT+LB",
        cooldown_ms=100,
        description="Skill slot 12",
    ),
    # F-key skills (common in WoW, FFXIV)
    ActionDefinition(
        28,
        "skill_f1",
        ActionCategory.SKILLS,
        "F1",
        None,
        cooldown_ms=100,
        description="F1 action",
    ),
    ActionDefinition(
        29,
        "skill_f2",
        ActionCategory.SKILLS,
        "F2",
        None,
        cooldown_ms=100,
        description="F2 action",
    ),
    ActionDefinition(
        30,
        "skill_f3",
        ActionCategory.SKILLS,
        "F3",
        None,
        cooldown_ms=100,
        description="F3 action",
    ),
    ActionDefinition(
        31,
        "skill_f4",
        ActionCategory.SKILLS,
        "F4",
        None,
        cooldown_ms=100,
        description="F4 action",
    ),
    # Quick slot skills (Shift+number)
    ActionDefinition(
        32,
        "skill_shift_1",
        ActionCategory.SKILLS,
        "Shift+1",
        None,
        cooldown_ms=100,
        description="Shift+1",
    ),
    ActionDefinition(
        33,
        "skill_shift_2",
        ActionCategory.SKILLS,
        "Shift+2",
        None,
        cooldown_ms=100,
        description="Shift+2",
    ),
    ActionDefinition(
        34,
        "skill_shift_3",
        ActionCategory.SKILLS,
        "Shift+3",
        None,
        cooldown_ms=100,
        description="Shift+3",
    ),
    ActionDefinition(
        35,
        "skill_shift_4",
        ActionCategory.SKILLS,
        "Shift+4",
        None,
        cooldown_ms=100,
        description="Shift+4",
    ),
]

# Combat Actions (36-47)
COMBAT_ACTIONS = [
    ActionDefinition(
        36,
        "attack_basic",
        ActionCategory.COMBAT,
        "LMB",
        "RT",
        description="Basic attack",
    ),
    ActionDefinition(
        37,
        "attack_heavy",
        ActionCategory.COMBAT,
        "RMB",
        "LT",
        cooldown_ms=500,
        description="Heavy attack",
    ),
    ActionDefinition(
        38,
        "block",
        ActionCategory.COMBAT,
        "RMB_hold",
        "LT_hold",
        description="Block/Parry",
    ),
    ActionDefinition(
        39, "interact", ActionCategory.COMBAT, "E", "A", description="Interact/Pickup"
    ),
    ActionDefinition(
        40,
        "use_item",
        ActionCategory.COMBAT,
        "Q",
        "UP",
        cooldown_ms=1000,
        description="Use quick item",
    ),
    ActionDefinition(
        41,
        "ultimate",
        ActionCategory.COMBAT,
        "R",
        "LB+RB",
        cooldown_ms=30000,
        description="Ultimate ability",
    ),
    ActionDefinition(
        42,
        "heal",
        ActionCategory.COMBAT,
        "H",
        "DOWN",
        cooldown_ms=10000,
        description="Heal/Potion",
    ),
    ActionDefinition(
        43,
        "buff_self",
        ActionCategory.COMBAT,
        "B",
        "LEFT",
        cooldown_ms=60000,
        description="Self buff",
    ),
    ActionDefinition(
        44,
        "combo_1",
        ActionCategory.COMBAT,
        "Shift+LMB",
        "RT+A",
        description="Combo attack 1",
    ),
    ActionDefinition(
        45,
        "combo_2",
        ActionCategory.COMBAT,
        "Shift+RMB",
        "LT+A",
        description="Combo attack 2",
    ),
    ActionDefinition(
        46,
        "weapon_swap",
        ActionCategory.COMBAT,
        "`",
        "SELECT",
        cooldown_ms=1000,
        description="Swap weapon",
    ),
    ActionDefinition(
        47,
        "special",
        ActionCategory.COMBAT,
        "V",
        "R3",
        cooldown_ms=5000,
        description="Special action",
    ),
]

# Targeting Actions (48-55)
TARGETING_ACTIONS = [
    ActionDefinition(
        48,
        "target_nearest",
        ActionCategory.TARGETING,
        "Tab",
        "RB",
        description="Target nearest enemy",
    ),
    ActionDefinition(
        49,
        "target_prev",
        ActionCategory.TARGETING,
        "Shift+Tab",
        "LB",
        description="Target previous",
    ),
    ActionDefinition(
        50,
        "target_self",
        ActionCategory.TARGETING,
        "F1",
        None,
        description="Target self",
    ),
    ActionDefinition(
        51,
        "target_party_1",
        ActionCategory.TARGETING,
        "F2",
        None,
        description="Target party member 1",
    ),
    ActionDefinition(
        52,
        "target_party_2",
        ActionCategory.TARGETING,
        "F3",
        None,
        description="Target party member 2",
    ),
    ActionDefinition(
        53,
        "target_party_3",
        ActionCategory.TARGETING,
        "F4",
        None,
        description="Target party member 3",
    ),
    ActionDefinition(
        54,
        "clear_target",
        ActionCategory.TARGETING,
        "Escape",
        "B",
        description="Clear target",
    ),
    ActionDefinition(
        55,
        "focus_target",
        ActionCategory.TARGETING,
        "Shift+F",
        None,
        description="Set focus target",
    ),
]

# Camera Actions (56-63) - Continuous values
CAMERA_ACTIONS = [
    ActionDefinition(
        56,
        "camera_left",
        ActionCategory.CAMERA,
        "MouseX-",
        "Rx-",
        True,
        description="Rotate camera left",
    ),
    ActionDefinition(
        57,
        "camera_right",
        ActionCategory.CAMERA,
        "MouseX+",
        "Rx+",
        True,
        description="Rotate camera right",
    ),
    ActionDefinition(
        58,
        "camera_up",
        ActionCategory.CAMERA,
        "MouseY-",
        "Ry-",
        True,
        description="Tilt camera up",
    ),
    ActionDefinition(
        59,
        "camera_down",
        ActionCategory.CAMERA,
        "MouseY+",
        "Ry+",
        True,
        description="Tilt camera down",
    ),
    ActionDefinition(
        60, "zoom_in", ActionCategory.CAMERA, "ScrollUp", "UP", description="Zoom in"
    ),
    ActionDefinition(
        61,
        "zoom_out",
        ActionCategory.CAMERA,
        "ScrollDown",
        "DOWN",
        description="Zoom out",
    ),
    ActionDefinition(
        62,
        "first_person",
        ActionCategory.CAMERA,
        "Home",
        None,
        description="First person view",
    ),
    ActionDefinition(
        63,
        "reset_camera",
        ActionCategory.CAMERA,
        "End",
        "R3",
        description="Reset camera",
    ),
]

# UI Actions (64-71)
UI_ACTIONS = [
    ActionDefinition(
        64, "inventory", ActionCategory.UI, "I", "START", description="Open inventory"
    ),
    ActionDefinition(
        65, "map", ActionCategory.UI, "M", "SELECT", description="Open map"
    ),
    ActionDefinition(
        66, "character", ActionCategory.UI, "C", None, description="Character screen"
    ),
    ActionDefinition(
        67, "skills_menu", ActionCategory.UI, "K", None, description="Skills menu"
    ),
    ActionDefinition(
        68, "quest_log", ActionCategory.UI, "J", None, description="Quest log"
    ),
    ActionDefinition(
        69, "social", ActionCategory.UI, "O", None, description="Social/Friends"
    ),
    ActionDefinition(
        70,
        "escape_menu",
        ActionCategory.UI,
        "Escape",
        "START",
        description="Escape/Pause menu",
    ),
    ActionDefinition(
        71,
        "screenshot",
        ActionCategory.UI,
        "PrintScreen",
        None,
        description="Take screenshot",
    ),
]

# Special state: No action
NO_ACTION = ActionDefinition(
    72, "idle", ActionCategory.MOVEMENT, None, None, description="No action/Idle"
)


# -----------------------------------------------------------------------------
# Keyboard base actions (slots 0-8)
# -----------------------------------------------------------------------------
# These nine slots are the layout the data-collection / training / inference
# pipeline has always used: the four cardinal directions, the four diagonals,
# and an idle sentinel for "no movement key is currently held".
#
# Slot 8 is deliberately the idle sentinel and NOT ``jump`` (which lives at
# slot 8 of the full ``MOVEMENT_ACTIONS`` list). Trained checkpoints encode
# slot 8 as "nothing pressed", so the standard space must keep that meaning.
# Changing it would silently make every existing model jump instead of idle.

NO_KEY_ACTION = ActionDefinition(
    8,
    "no_keys",
    ActionCategory.MOVEMENT,
    None,
    None,
    label="nokeys",
    description="No movement key held (idle sentinel)",
)

# Short labels the runtime pipeline logs, matching the historical ACTION_NAMES.
_KEYBOARD_LABELS = (
    "straight",
    "reverse",
    "left",
    "right",
    "forward+left",
    "forward+right",
    "reverse+left",
    "reverse+right",
    "nokeys",
)

#: The nine keyboard slots (indices 0-8) shared by the "basic" and "standard"
#: action spaces. Order and ``key_binding`` values are load-bearing: the
#: recorder (``collect_data.keys_to_output``) and the executor
#: (``test_model.execute_action``) both index into this list directly.
KEYBOARD_BASE_ACTIONS: List[ActionDefinition] = [
    replace(action, label=label)
    for action, label in zip(MOVEMENT_ACTIONS[:8] + [NO_KEY_ACTION], _KEYBOARD_LABELS)
]

#: Index of the idle sentinel within :data:`KEYBOARD_BASE_ACTIONS`.
NO_KEY_ACTION_ID = NO_KEY_ACTION.id

#: The twenty gamepad slots (indices 9-28) of the "standard" action space.
_STANDARD_GAMEPAD_ACTIONS: List[ActionDefinition] = [
    ActionDefinition(9, "gamepad_lt", ActionCategory.COMBAT, None, "LT"),
    ActionDefinition(10, "gamepad_rt", ActionCategory.COMBAT, None, "RT"),
    ActionDefinition(11, "gamepad_lx", ActionCategory.MOVEMENT, None, "Lx", True),
    ActionDefinition(12, "gamepad_ly", ActionCategory.MOVEMENT, None, "Ly", True),
    ActionDefinition(13, "gamepad_rx", ActionCategory.CAMERA, None, "Rx", True),
    ActionDefinition(14, "gamepad_ry", ActionCategory.CAMERA, None, "Ry", True),
    ActionDefinition(15, "gamepad_up", ActionCategory.UI, None, "UP"),
    ActionDefinition(16, "gamepad_down", ActionCategory.UI, None, "DOWN"),
    ActionDefinition(17, "gamepad_left", ActionCategory.UI, None, "LEFT"),
    ActionDefinition(18, "gamepad_right", ActionCategory.UI, None, "RIGHT"),
    ActionDefinition(19, "gamepad_start", ActionCategory.UI, None, "START"),
    ActionDefinition(20, "gamepad_select", ActionCategory.UI, None, "SELECT"),
    ActionDefinition(21, "gamepad_l3", ActionCategory.MOVEMENT, None, "L3"),
    ActionDefinition(22, "gamepad_r3", ActionCategory.CAMERA, None, "R3"),
    ActionDefinition(23, "gamepad_lb", ActionCategory.SKILLS, None, "LB"),
    ActionDefinition(24, "gamepad_rb", ActionCategory.SKILLS, None, "RB"),
    ActionDefinition(25, "gamepad_a", ActionCategory.COMBAT, None, "A"),
    ActionDefinition(26, "gamepad_b", ActionCategory.COMBAT, None, "B"),
    ActionDefinition(27, "gamepad_x", ActionCategory.SKILLS, None, "X"),
    ActionDefinition(28, "gamepad_y", ActionCategory.SKILLS, None, "Y"),
]

# =============================================================================
# Mouse block
# =============================================================================
#: Mouse slots appended after the discrete actions when a model is trained with
#: mouse capture enabled. ``collect_data`` writes ``mouse_state.to_array()``,
#: whose layout :data:`MOUSE_FIELDS` mirrors -- keep the two in sync.
#:
#: Five of the ten fields are signed. Mouse capture normalises deltas and
#: velocities to [-1, 1] and records scroll as a signed step count, but the
#: training loss (``nn.BCEWithLogitsLoss``) can only represent a target in
#: [0, 1]. A negative target is unreachable for that loss, so it does not
#: converge: the gradient drives the logit towards -inf and the field collapses
#: to 0, which inference then reads as "full left" rather than "no movement".
#:
#: Recording therefore stores signed fields mapped through ``(v + 1) / 2``, and
#: inference inverts them with ``(p - 0.5) * 2`` -- the transform
#: ``InferenceEngine.execute_mouse`` already performs.
MOUSE_OUTPUT_SIZE = 10
MOUSE_ACTION_ID = 72  # first mouse slot == len(KEYBOARD_BASE_ACTIONS) + 20


@dataclass(frozen=True)
class MouseField:
    """One slot of the recorded mouse block.

    Attributes:
        index: Position inside the mouse block, appended after the discrete slots.
        name: Label used in logs and validation errors.
        signed: True when the raw capture value can go negative and therefore has
            to be mapped into [0, 1] before it reaches a BCE loss.
        description: What the raw capture value means.
    """

    index: int
    name: str
    signed: bool
    description: str


MOUSE_FIELDS: Tuple[MouseField, ...] = (
    MouseField(0, "x", False, "absolute position, fraction of the capture region"),
    MouseField(1, "y", False, "absolute position, fraction of the capture region"),
    MouseField(2, "dx", True, "frame delta, fraction of the capture region width"),
    MouseField(3, "dy", True, "frame delta, fraction of the capture region height"),
    MouseField(4, "vx", True, "velocity, fraction of mouse_capture._MAX_VELOCITY"),
    MouseField(5, "vy", True, "velocity, fraction of mouse_capture._MAX_VELOCITY"),
    MouseField(6, "lmb", False, "left button held"),
    MouseField(7, "rmb", False, "right button held"),
    MouseField(8, "mmb", False, "middle button held"),
    MouseField(9, "scroll", True, "signed scroll step count"),
)

#: Number of signed fields, i.e. the ones a BCE loss cannot represent raw.
MOUSE_SIGNED_FIELD_COUNT = sum(1 for f in MOUSE_FIELDS if f.signed)


def mouse_field(name: str) -> MouseField:
    """Look a mouse field up by name.

    Raises:
        KeyError: If no field carries that name.
    """
    for field in MOUSE_FIELDS:
        if field.name == name:
            return field
    raise KeyError(name)


def normalize_mouse_vector(values) -> List[float]:
    """Map a raw mouse capture block into the [0, 1] targets the loss expects.

    Unsigned fields pass through untouched; signed fields are mapped through
    ``(v + 1) / 2``. Callers that need an array should wrap the result in
    ``numpy.asarray`` so the dtype stays float32.

    Args:
        values: Raw values in ``mouse_capture.MouseState.to_array()`` order.

    Returns:
        A new list of ``MOUSE_OUTPUT_SIZE`` floats.

    Raises:
        ValueError: If the vector length does not match ``MOUSE_OUTPUT_SIZE``.
    """
    if len(values) != MOUSE_OUTPUT_SIZE:
        raise ValueError(
            "Expected %d mouse values, got %d" % (MOUSE_OUTPUT_SIZE, len(values))
        )

    scaled = [float(v) for v in values]
    for field in MOUSE_FIELDS:
        if field.signed:
            scaled[field.index] = scaled[field.index] * 0.5 + 0.5
    return scaled


def denormalize_mouse_value(field: MouseField, value: float) -> float:
    """Inverse of :func:`normalize_mouse_vector` for a single field.

    Args:
        field: The field the prediction belongs to.
        value: Raw model output for that field, in [0, 1].

    Returns:
        The signed value for signed fields, otherwise the value unchanged.
    """
    if field.signed:
        return (float(value) - 0.5) * 2.0
    return float(value)


# =============================================================================
# Action Space Configurations
# =============================================================================


@dataclass
class ActionSpaceConfig:
    """Configuration for model action space."""

    name: str
    description: str
    actions: List[ActionDefinition]
    output_type: str  # "single" (softmax) or "multi" (sigmoid)

    @property
    def num_actions(self) -> int:
        return len(self.actions)

    @property
    def action_names(self) -> List[str]:
        return [a.name for a in self.actions]

    def get_action_by_id(self, action_id: int) -> Optional[ActionDefinition]:
        for action in self.actions:
            if action.id == action_id:
                return action
        return None


# Basic action space (movement only, no gamepad)
ACTION_SPACE_BASIC = ActionSpaceConfig(
    name="basic",
    description="Basic WASD movement only (9 actions)",
    actions=list(KEYBOARD_BASE_ACTIONS),
    output_type="multi",
)

# Standard action space (29 actions - current pipeline default)
ACTION_SPACE_STANDARD = ActionSpaceConfig(
    name="standard",
    description="Standard keyboard + gamepad (29 actions)",
    actions=list(KEYBOARD_BASE_ACTIONS) + list(_STANDARD_GAMEPAD_ACTIONS),
    output_type="multi",
)

# Extended action space (73 actions - full MMORPG)
ACTION_SPACE_EXTENDED = ActionSpaceConfig(
    name="extended",
    description="Full MMORPG action space with skills (73 actions)",
    actions=(
        MOVEMENT_ACTIONS  # 0-15
        + SKILL_ACTIONS  # 16-35
        + COMBAT_ACTIONS  # 36-47
        + TARGETING_ACTIONS  # 48-55
        + CAMERA_ACTIONS  # 56-63
        + UI_ACTIONS  # 64-71
        + [NO_ACTION]  # 72
    ),
    output_type="multi",  # Allow simultaneous actions
)

# Compact skill-focused (for action games like Lost Ark, BDO)
ACTION_SPACE_COMBAT = ActionSpaceConfig(
    name="combat",
    description="Combat-focused with movement + skills (48 actions)",
    actions=(
        MOVEMENT_ACTIONS + SKILL_ACTIONS + COMBAT_ACTIONS
    ),  # 0-15  # 16-35  # 36-47
    output_type="multi",
)


# =============================================================================
# Action Space Registry
# =============================================================================

ACTION_SPACES: Dict[str, ActionSpaceConfig] = {
    "basic": ACTION_SPACE_BASIC,
    "standard": ACTION_SPACE_STANDARD,
    "extended": ACTION_SPACE_EXTENDED,
    "combat": ACTION_SPACE_COMBAT,
}

#: The action space the training and inference pipeline uses unless a caller
#: explicitly asks for another one. Checkpoints are trained against this
#: layout, so changing it invalidates existing models.
DEFAULT_ACTION_SPACE_NAME = "standard"


def validate_action_spaces() -> List[str]:
    """Check the built-in action spaces for structural mistakes.

    Returns a list of human-readable problem descriptions (empty when clean).
    Called once at import time so a bad edit fails loudly and immediately
    instead of silently shifting every action index by one.

    Verifies that, for each space:
      * action ids are contiguous and match their position in the list
        (``decode_actions_multi_label`` and ``get_action_by_id`` would
        otherwise disagree about which output slot an action belongs to);
      * action names are unique;
      * the space uses multi-label output, matching the BCEWithLogitsLoss
        objective used by ``train_model.py``.
    """
    problems: List[str] = []

    for name, space in ACTION_SPACES.items():
        for position, action in enumerate(space.actions):
            if action.id != position:
                problems.append(
                    f"{name}: action {action.name!r} has id {action.id} "
                    f"but sits at position {position}"
                )

        names = [action.name for action in space.actions]
        duplicates = {n for n in names if names.count(n) > 1}
        if duplicates:
            problems.append(f"{name}: duplicate action names {sorted(duplicates)}")

        if space.output_type != "multi":
            problems.append(
                f"{name}: output_type is {space.output_type!r} but the pipeline "
                f"trains with BCEWithLogitsLoss (multi-label sigmoid)"
            )

    # The keyboard base slots are shared by the recorder and the executor; if
    # their length drifts, recorded data and inference disagree silently.
    if len(KEYBOARD_BASE_ACTIONS) + len(_STANDARD_GAMEPAD_ACTIONS) != 29:
        problems.append(
            "standard space is no longer 29 actions "
            f"(got {len(KEYBOARD_BASE_ACTIONS) + len(_STANDARD_GAMEPAD_ACTIONS)})"
        )
    if KEYBOARD_BASE_ACTIONS[NO_KEY_ACTION_ID].name != NO_KEY_ACTION.name:
        problems.append(
            f"slot {NO_KEY_ACTION_ID} must be the idle sentinel "
            f"{NO_KEY_ACTION.name!r}, got "
            f"{KEYBOARD_BASE_ACTIONS[NO_KEY_ACTION_ID].name!r}"
        )

    return problems


_ACTION_SPACE_PROBLEMS = validate_action_spaces()
if _ACTION_SPACE_PROBLEMS:  # pragma: no cover - import-time guard
    raise ValueError(
        "Invalid action space configuration in bot_mmorpg.config.action_mapping:\n  - "
        + "\n  - ".join(_ACTION_SPACE_PROBLEMS)
    )


def get_action_space(name: str = DEFAULT_ACTION_SPACE_NAME) -> ActionSpaceConfig:
    """Get action space configuration by name."""
    return ACTION_SPACES.get(name.lower(), ACTION_SPACES[DEFAULT_ACTION_SPACE_NAME])


#: Action spaces the collect/train/inference pipeline can actually execute.
#: ``combat`` and ``extended`` define skill, targeting and UI bindings for which
#: ``test_model.execute_action`` has no handlers, so a model routed through them
#: would emit actions that silently do nothing.
PIPELINE_SUPPORTED_SPACES = ("basic", "standard")


def get_pipeline_action_space(
    name: str = DEFAULT_ACTION_SPACE_NAME,
) -> ActionSpaceConfig:
    """Resolve an action space for use by the runtime pipeline.

    Unlike :func:`get_action_space`, this never returns a space the pipeline
    cannot execute: an unsupported-but-existing name falls back to the default
    space instead of yielding a model whose actions go nowhere. The caller can
    detect the substitution with :func:`is_pipeline_supported`.
    """
    space = get_action_space(name)
    if space.name not in PIPELINE_SUPPORTED_SPACES:
        return ACTION_SPACES[DEFAULT_ACTION_SPACE_NAME]
    return space


def is_pipeline_supported(name: str) -> bool:
    """Whether the runtime pipeline can execute the named action space."""
    return get_action_space(name).name in PIPELINE_SUPPORTED_SPACES


def list_action_spaces() -> List[str]:
    """List available action space names."""
    return list(ACTION_SPACES.keys())


# =============================================================================
# Multi-Label Output Encoding
# =============================================================================


def encode_actions_multi_label(
    active_actions: List[str], action_space: ActionSpaceConfig
) -> List[int]:
    """
    Encode multiple simultaneous actions as multi-label vector.

    Args:
        active_actions: List of action names that are active
        action_space: Action space configuration

    Returns:
        Binary vector where 1 = action active, 0 = inactive
    """
    output = [0] * action_space.num_actions

    for action_name in active_actions:
        for i, action in enumerate(action_space.actions):
            if action.name == action_name:
                output[i] = 1
                break

    return output


def decode_actions_multi_label(
    output_vector: List[float], action_space: ActionSpaceConfig, threshold: float = 0.5
) -> List[ActionDefinition]:
    """
    Decode multi-label output to list of active actions.

    Args:
        output_vector: Model output (probabilities)
        action_space: Action space configuration
        threshold: Activation threshold

    Returns:
        List of active ActionDefinition objects
    """
    active_actions = []

    for i, (prob, action) in enumerate(zip(output_vector, action_space.actions)):
        if prob >= threshold:
            active_actions.append(action)

    return active_actions


# =============================================================================
# Game-Specific Presets
# =============================================================================
# These record the action space each game *would* ideally use. Only "standard"
# is executable today (see PIPELINE_SUPPORTED_SPACES), so profile loading
# resolves through get_pipeline_action_space() and falls back rather than
# handing the pipeline a space it cannot drive.

GAME_ACTION_PRESETS: Dict[str, str] = {
    # Action MMORPGs - need full skill bars
    "genshin_impact": "combat",
    "lost_ark": "combat",
    "black_desert_online": "combat",
    "new_world": "combat",
    # Tab-target MMORPGs - standard is fine
    "world_of_warcraft": "extended",
    "final_fantasy_xiv": "extended",
    "guild_wars_2": "combat",
    "elder_scrolls_online": "combat",
    # Simpler games
    "runescape": "standard",
    "albion_online": "standard",
    "path_of_exile": "combat",
    # Default
    "custom": "standard",
}


def get_recommended_action_space(game_id: str) -> ActionSpaceConfig:
    """Get recommended action space for a specific game."""
    game_id_lower = game_id.lower().replace(" ", "_").replace("-", "_")
    preset_name = GAME_ACTION_PRESETS.get(game_id_lower, "standard")
    return get_action_space(preset_name)


# =============================================================================
# Documentation
# =============================================================================

ACTION_SPACE_TABLE = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    MMORPG Action Space Configurations                          ║
╠═══════════════════╦════════════╦═════════════════════════════════════════════╣
║ Name              ║ Actions    ║ Description                                  ║
╠═══════════════════╬════════════╬═════════════════════════════════════════════╣
║ basic             ║ 9          ║ WASD movement only (no gamepad)              ║
║ standard          ║ 29         ║ Keyboard + full gamepad  ← pipeline default  ║
║ combat            ║ 48         ║ Movement + skills + combat (action RPGs)     ║
║ extended          ║ 73         ║ Full MMORPG (movement, skills, UI, camera)   ║
╚═══════════════════╩════════════╩═════════════════════════════════════════════╝

Output Type:
- every space is multi-label (sigmoid) because train_model.py optimises
  BCEWithLogitsLoss, so simultaneous inputs ("W + strafe + click") are learnable

Slots 0-8 are the shared keyboard layout and must stay stable:
  0 W        1 S        2 A        3 D
  4 W+A      5 W+D      6 S+A      7 S+D
  8 nokeys  (idle sentinel -- NOT jump)

Slots 9-28 are gamepad, then 6 mouse values are appended when mouse capture
is enabled (35 total).
"""


if __name__ == "__main__":
    print(ACTION_SPACE_TABLE)
    print("\nAvailable action spaces:")
    for name, space in ACTION_SPACES.items():
        print(f"  {name}: {space.num_actions} actions - {space.description}")
