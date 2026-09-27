"""
BOT-MMORPG-AI Inference Script (PyTorch)

Run trained models on live gameplay for automated control.
Supports multiple architectures with real-time inference.

Usage:
    bot-mmorpg-play --model artifacts/model/efficientnet_lstm_best.pth
    bot-mmorpg-play --model artifacts/model/mobilenet_v3_final.pth --no-gamepad
"""

from __future__ import annotations

import argparse
import platform
import random
import sys
import time
from collections import deque
from pathlib import Path
from statistics import mean
from typing import Optional, Tuple

import cv2
import numpy as np

# PyTorch imports
try:
    import torch

    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False
    # Stub for when PyTorch is not installed
    torch = None

# Local imports - screen capture
try:
    from .grabscreen import grab_screen

    GRABSCREEN_AVAILABLE = True
except ImportError:
    try:
        from grabscreen import grab_screen

        GRABSCREEN_AVAILABLE = True
    except ImportError:
        GRABSCREEN_AVAILABLE = False

# Local imports - keyboard control
try:
    from .directkeys import A, D, PressKey, ReleaseKey, S, W

    DIRECTKEYS_AVAILABLE = True
except ImportError:
    try:
        from directkeys import A, D, PressKey, ReleaseKey, S, W

        DIRECTKEYS_AVAILABLE = True
    except ImportError:
        DIRECTKEYS_AVAILABLE = False

# Local imports - key checking
try:
    from .getkeys import key_check

    GETKEYS_AVAILABLE = True
except ImportError:
    try:
        from getkeys import key_check

        GETKEYS_AVAILABLE = True
    except ImportError:
        GETKEYS_AVAILABLE = False

# Local imports - motion detection
try:
    from .motion import motion_detection

    MOTION_AVAILABLE = True
except ImportError:
    try:
        from motion import motion_detection

        MOTION_AVAILABLE = True
    except ImportError:
        MOTION_AVAILABLE = False

        def motion_detection(t_minus, t_now, t_plus, screen):
            """Stub motion detection."""
            return 1000  # Default high motion


# Local imports - gamepad (vJoy)
try:
    from .vjoy2 import (
        button_A,
        button_B,
        button_X,
        button_Y,
        game_lx_left,
        game_lx_right,
        game_ly_down,
        game_ly_up,
        gamepad_lt,
        gamepad_rt,
        look_rx_left,
        look_rx_right,
        look_ry_down,
        look_ry_up,
        ultimate_release,
    )

    VJOY_AVAILABLE = True
except ImportError:
    try:
        from vjoy2 import (
            button_A,
            button_B,
            button_X,
            button_Y,
            game_lx_left,
            game_lx_right,
            game_ly_down,
            game_ly_up,
            gamepad_lt,
            gamepad_rt,
            look_rx_left,
            look_rx_right,
            look_ry_down,
            look_ry_up,
            ultimate_release,
        )

        VJOY_AVAILABLE = True
    except ImportError:
        VJOY_AVAILABLE = False

        def ultimate_release():
            pass


# Local imports - PyTorch models
try:
    from .models_pytorch import get_device, load_model

    MODELS_AVAILABLE = True
except ImportError:
    try:
        from models_pytorch import get_device, load_model  # noqa: F401

        MODELS_AVAILABLE = True
    except ImportError:
        MODELS_AVAILABLE = False

# Mouse output – optional, only used when model has mouse predictions
try:
    from pynput.mouse import Button as _MBtn
    from pynput.mouse import Controller as _MouseCtrl

    _MOUSE_CTRL = _MouseCtrl()
    MOUSE_OUTPUT_AVAILABLE = True
except ImportError:
    _MOUSE_CTRL = None
    MOUSE_OUTPUT_AVAILABLE = False

# Action space definition -- single source of truth for action indices.
# Without this the module would fall back to hardcoded literals and drift from
# bot_mmorpg.config.action_mapping.
# Action space definition -- single source of truth for action indices.
# Without this the module would fall back to hardcoded literals and drift from
# bot_mmorpg.config.action_mapping.


def _resolve_action_mapping():
    """Return the action_mapping module, whichever way this file was started.

    ``test_model.py`` runs both as ``bot-mmorpg-play`` and as a bare script, so
    the same module is reachable under two names. Returns ``None`` when neither
    resolves, which leaves this file importable with degraded action metadata
    instead of failing at import time.
    """
    try:
        from ..config import action_mapping as resolved

        return resolved
    except ImportError:  # pragma: no cover - exercised only when run as a script
        pass

    try:
        from config import action_mapping as resolved

        return resolved
    except ImportError:
        pass

    # Direct script execution: put the package root on sys.path so the sibling
    # "config" package resolves.
    pkg_root = Path(__file__).resolve().parent.parent
    if str(pkg_root) not in sys.path:
        sys.path.insert(0, str(pkg_root))
    try:
        from config import action_mapping as resolved

        return resolved
    except ImportError:
        return None


_ACTION_MAPPING = _resolve_action_mapping()

if _ACTION_MAPPING is not None:
    ACTION_SPACE = _ACTION_MAPPING.get_pipeline_action_space(
        _ACTION_MAPPING.DEFAULT_ACTION_SPACE_NAME
    )
    # Recorded mouse block, in mouse_capture.MouseState.to_array() order.
    MOUSE_FIELDS = _ACTION_MAPPING.MOUSE_FIELDS
    MOUSE_OUTPUT_SIZE = _ACTION_MAPPING.MOUSE_OUTPUT_SIZE
    _DENORMALIZE_MOUSE = _ACTION_MAPPING.denormalize_mouse_value
else:  # pragma: no cover - only when the config package is unreachable
    ACTION_SPACE = None
    MOUSE_FIELDS = ()
    MOUSE_OUTPUT_SIZE = 0
    _DENORMALIZE_MOUSE = None

#: Mouse field by name, so ``execute_mouse`` reads a slot through its name
#: rather than a magic index that a reordered block would silently invalidate.
_MOUSE_FIELD = {field.name: field for field in MOUSE_FIELDS}

# Platform-specific imports
IS_WINDOWS = platform.system() == "Windows"
if IS_WINDOWS:
    try:
        import msvcrt  # noqa: F401

        MSVCRT_AVAILABLE = True
    except ImportError:
        MSVCRT_AVAILABLE = False
else:
    MSVCRT_AVAILABLE = False


# =============================================================================
# Configuration
# =============================================================================

GAME_WIDTH = 1920
GAME_HEIGHT = 1080
WIDTH = 480
HEIGHT = 270

# Motion detection settings
LOG_LEN = 25
MOTION_REQ = 500  # Lowered from 800 – catches stuck-on-wall earlier

# Stuck recovery cooldown (seconds) – prevents spam-reversing
STUCK_COOLDOWN = 4.0

# Base action weights for keyboard(9) + gamepad(20) = 29
# Mouse weights are appended dynamically when model has mouse outputs.
_BASE_ACTION_WEIGHTS = np.array(
    [
        2.5,
        0.5,
        1.0,
        1.0,
        1.5,
        1.5,
        0.8,
        0.8,
        0.1,  # Keyboard: W, S, A, D, WA, WD, SA, SD, NK
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,  # Gamepad: LT, RT, Lx, Ly, Rx, Ry
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,  # Gamepad: UP, DOWN, LEFT, RIGHT, START, SELECT, L3, R3, LB, RB
        1.2,
        1.2,
        1.2,
        1.2,  # Gamepad: A, B, X, Y – slight boost for ability buttons
    ]
)

# Number of discrete slots (keyboard + gamepad) that precede any mouse outputs.
# Derived from the action space so the weight table below cannot drift out of
# sync with it; falls back to the historical 29 when the config package is
# unavailable.
_BASE_ACTION_COUNT = ACTION_SPACE.num_actions if ACTION_SPACE is not None else 29

if len(_BASE_ACTION_WEIGHTS) != _BASE_ACTION_COUNT:  # pragma: no cover
    raise ValueError(
        f"_BASE_ACTION_WEIGHTS has {len(_BASE_ACTION_WEIGHTS)} entries but the "
        f"'{ACTION_SPACE.name if ACTION_SPACE else 'standard'}' action space "
        f"defines {_BASE_ACTION_COUNT} discrete actions"
    )

# Mouse weight block, in the same order as config.action_mapping.MOUSE_FIELDS:
# [x, y, dx, dy, vx, vy, lmb, rmb, mmb, scroll]
# Position/delta/velocity are continuous outputs (not chosen via argmax),
# so their weights are low to avoid competing with discrete actions.
_MOUSE_WEIGHTS_10 = np.array([0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 1.0, 1.0, 0.8, 0.3])

# Legacy 6-value mouse: [x, y, lmb, rmb, mmb, scroll]
_LEGACY_MOUSE_OUTPUT_SIZE = 6
_MOUSE_WEIGHTS_6 = np.array([0.1, 0.1, 1.0, 1.0, 0.8, 0.3])

if MOUSE_OUTPUT_SIZE and len(_MOUSE_WEIGHTS_10) != MOUSE_OUTPUT_SIZE:
    # pragma: no cover - guards a reordering of MOUSE_FIELDS against these
    # positional weights, which would silently reweight the wrong outputs.
    raise ValueError(
        f"_MOUSE_WEIGHTS_10 has {len(_MOUSE_WEIGHTS_10)} entries but the action "
        f"space records a {MOUSE_OUTPUT_SIZE}-value mouse block"
    )


def build_action_weights(num_actions: int) -> np.ndarray:
    """Build action weights array matching model output size.

    Automatically appends mouse weights when num_actions > _BASE_ACTION_COUNT.
    """
    if num_actions <= _BASE_ACTION_COUNT:
        return _BASE_ACTION_WEIGHTS[:num_actions].copy()

    mouse_size = num_actions - _BASE_ACTION_COUNT
    if mouse_size == MOUSE_OUTPUT_SIZE:
        mouse_w = _MOUSE_WEIGHTS_10
    elif mouse_size == _LEGACY_MOUSE_OUTPUT_SIZE:
        mouse_w = _MOUSE_WEIGHTS_6
    else:
        # Unknown mouse format – equal weight
        mouse_w = np.ones(mouse_size) * 0.5

    return np.concatenate([_BASE_ACTION_WEIGHTS, mouse_w])


# Default for backward compatibility (29 actions, no mouse)
ACTION_WEIGHTS = build_action_weights(_BASE_ACTION_COUNT)

# Action names for logging. Derived from the action space so a new gamepad slot
# cannot be added without a matching label here; the literal list below is only
# used when the config package cannot be imported.
ACTION_NAMES = (
    [action.display_label() for action in ACTION_SPACE.actions]
    if ACTION_SPACE is not None
    else [
        "straight",
        "reverse",
        "left",
        "right",
        "forward+left",
        "forward+right",
        "reverse+left",
        "reverse+right",
        "nokeys",
        "LT",
        "RT",
        "Lx",
        "Ly",
        "Rx",
        "Ry",
        "UP",
        "DOWN",
        "LEFT",
        "RIGHT",
        "START",
        "SELECT",
        "L3",
        "R3",
        "LB",
        "RB",
        "A",
        "B",
        "X",
        "Y",
    ]
)


# =============================================================================
# Keyboard Actions
# =============================================================================


def straight():
    """Move forward."""
    if DIRECTKEYS_AVAILABLE:
        PressKey(W)
        ReleaseKey(A)
        ReleaseKey(D)
        ReleaseKey(S)


def left():
    """Turn left (occasionally move forward)."""
    if DIRECTKEYS_AVAILABLE:
        if random.randrange(0, 3) == 1:
            PressKey(W)
        else:
            ReleaseKey(W)
        PressKey(A)
        ReleaseKey(S)
        ReleaseKey(D)


def right():
    """Turn right (occasionally move forward)."""
    if DIRECTKEYS_AVAILABLE:
        if random.randrange(0, 3) == 1:
            PressKey(W)
        else:
            ReleaseKey(W)
        PressKey(D)
        ReleaseKey(A)
        ReleaseKey(S)


def reverse():
    """Move backward."""
    if DIRECTKEYS_AVAILABLE:
        PressKey(S)
        ReleaseKey(A)
        ReleaseKey(W)
        ReleaseKey(D)


def forward_left():
    """Move forward and left."""
    if DIRECTKEYS_AVAILABLE:
        PressKey(W)
        PressKey(A)
        ReleaseKey(D)
        ReleaseKey(S)


def forward_right():
    """Move forward and right."""
    if DIRECTKEYS_AVAILABLE:
        PressKey(W)
        PressKey(D)
        ReleaseKey(A)
        ReleaseKey(S)


def reverse_left():
    """Move backward and left."""
    if DIRECTKEYS_AVAILABLE:
        PressKey(S)
        PressKey(A)
        ReleaseKey(W)
        ReleaseKey(D)


def reverse_right():
    """Move backward and right."""
    if DIRECTKEYS_AVAILABLE:
        PressKey(S)
        PressKey(D)
        ReleaseKey(W)
        ReleaseKey(A)


def no_keys():
    """Release all keys (occasionally move forward)."""
    if DIRECTKEYS_AVAILABLE:
        if random.randrange(0, 3) == 1:
            PressKey(W)
        else:
            ReleaseKey(W)
        ReleaseKey(A)
        ReleaseKey(S)
        ReleaseKey(D)


def release_all_keys():
    """Release all keyboard keys."""
    if DIRECTKEYS_AVAILABLE:
        ReleaseKey(A)
        ReleaseKey(W)
        ReleaseKey(D)
        ReleaseKey(S)


# =============================================================================
# Keyboard action mapping
# =============================================================================

# Physical keypress handlers, keyed by action-space name. The action space owns
# *which* actions exist and in what order; this table only says how each one is
# pressed on this machine. Keeping them separate is what lets a new action be
# added in action_mapping.py without silently going unhandled here.
_KEYBOARD_ACTION_HANDLERS = {
    "move_forward": straight,
    "move_backward": reverse,
    "move_left": left,
    "move_right": right,
    "move_forward_left": forward_left,
    "move_forward_right": forward_right,
    "move_backward_left": reverse_left,
    "move_backward_right": reverse_right,
    "no_keys": no_keys,
}

#: Number of leading slots in the action space that are keyboard actions.
_KEYBOARD_SLOT_COUNT = 9

if ACTION_SPACE is not None:
    _keyboard_slots = ACTION_SPACE.actions[:_KEYBOARD_SLOT_COUNT]
    _missing = [
        a.name for a in _keyboard_slots if a.name not in _KEYBOARD_ACTION_HANDLERS
    ]
    if _missing:  # pragma: no cover - guards against an incomplete edit
        raise ValueError(
            f"No keypress handler for action(s) {_missing}; add them to "
            f"_KEYBOARD_ACTION_HANDLERS in test_model.py"
        )
    KEYBOARD_ACTIONS = {
        action.id: _KEYBOARD_ACTION_HANDLERS[action.name] for action in _keyboard_slots
    }
else:  # pragma: no cover - config package unavailable
    KEYBOARD_ACTIONS = {
        0: straight,
        1: reverse,
        2: left,
        3: right,
        4: forward_left,
        5: forward_right,
        6: reverse_left,
        7: reverse_right,
        8: no_keys,
    }


# =============================================================================
# Gamepad action mapping
# =============================================================================
# Handlers are keyed by action-space name for the same reason the keyboard ones
# are. vJoy only exposes bindings for triggers, both analog sticks and the face
# buttons, so the D-pad / START / SELECT / L3 / R3 / LB / RB slots have no
# handler. Those are collected in UNIMPLEMENTED_GAMEPAD_ACTIONS and reported at
# startup instead of being selected by the model and silently ignored.


def _press(fn) -> "callable":
    """Wrap a plain press (no direction) in the signed-axis handler shape."""

    def handler(value: float = 0.0) -> None:
        fn()

    return handler


def _axis(negative, positive) -> "callable":
    """Wrap an analog axis: the prediction's sign selects the direction."""

    def handler(value: float) -> None:
        if value < 0:
            negative()
        else:
            positive()

    return handler


GAMEPAD_ACTIONS = {}
UNIMPLEMENTED_GAMEPAD_ACTIONS = []

if VJOY_AVAILABLE:
    _GAMEPAD_ACTION_HANDLERS = {
        "gamepad_lt": _press(gamepad_lt),
        "gamepad_rt": _press(gamepad_rt),
        "gamepad_lx": _axis(game_lx_left, game_lx_right),
        "gamepad_ly": _axis(game_ly_down, game_ly_up),
        "gamepad_rx": _axis(look_rx_left, look_rx_right),
        "gamepad_ry": _axis(look_ry_down, look_ry_up),
        "gamepad_a": _press(button_A),
        "gamepad_b": _press(button_B),
        "gamepad_x": _press(button_X),
        "gamepad_y": _press(button_Y),
    }

    if ACTION_SPACE is not None:
        _gamepad_slots = ACTION_SPACE.actions[_KEYBOARD_SLOT_COUNT:]
        GAMEPAD_ACTIONS = {
            action.id: _GAMEPAD_ACTION_HANDLERS[action.name]
            for action in _gamepad_slots
            if action.name in _GAMEPAD_ACTION_HANDLERS
        }
        UNIMPLEMENTED_GAMEPAD_ACTIONS = [
            (action.id, action.display_label())
            for action in _gamepad_slots
            if action.name not in _GAMEPAD_ACTION_HANDLERS
        ]
    else:  # pragma: no cover - config package unavailable
        GAMEPAD_ACTIONS = {
            9: _press(gamepad_lt),
            10: _press(gamepad_rt),
            11: _axis(game_lx_left, game_lx_right),
            12: _axis(game_ly_down, game_ly_up),
            13: _axis(look_rx_left, look_rx_right),
            14: _axis(look_ry_down, look_ry_up),
            25: _press(button_A),
            26: _press(button_B),
            27: _press(button_X),
            28: _press(button_Y),
        }
        UNIMPLEMENTED_GAMEPAD_ACTIONS = [
            (i, n)
            for i, n in enumerate(
                [
                    "UP",
                    "DOWN",
                    "LEFT",
                    "RIGHT",
                    "START",
                    "SELECT",
                    "L3",
                    "R3",
                    "LB",
                    "RB",
                ],
                start=15,
            )
        ]
else:  # pragma: no cover - vJoy not installed
    UNIMPLEMENTED_GAMEPAD_ACTIONS = [
        (i, n)
        for i, n in enumerate(
            [
                "LT",
                "RT",
                "Lx",
                "Ly",
                "Rx",
                "Ry",
                "UP",
                "DOWN",
                "LEFT",
                "RIGHT",
                "START",
                "SELECT",
                "L3",
                "R3",
                "LB",
                "RB",
                "A",
                "B",
                "X",
                "Y",
            ],
            start=9,
        )
    ]


# =============================================================================
# Inference Engine
# =============================================================================


class InferenceEngine:
    """
    Real-time inference engine for gameplay control.

    Handles model loading, frame preprocessing, and action execution.
    """

    def __init__(
        self,
        model_path: str,
        device: Optional[torch.device] = None,
        enable_gamepad: bool = True,
        temporal_frames: int = 4,
    ):
        """
        Initialize inference engine.

        Args:
            model_path: Path to saved model checkpoint
            device: PyTorch device (auto-detected if None)
            enable_gamepad: Enable gamepad output (requires vJoy)
            temporal_frames: Number of frames for temporal models
        """
        self.model_path = Path(model_path)
        self.device = device or get_device()
        self.enable_gamepad = enable_gamepad and VJOY_AVAILABLE
        self.temporal_frames = temporal_frames

        if enable_gamepad and not VJOY_AVAILABLE:
            print(
                "[Warn] Gamepad requested but vJoy is not available - using keyboard only."
            )

        if self.enable_gamepad and UNIMPLEMENTED_GAMEPAD_ACTIONS:
            labels = ", ".join(label for _, label in UNIMPLEMENTED_GAMEPAD_ACTIONS)
            print(
                f"[Info] {len(UNIMPLEMENTED_GAMEPAD_ACTIONS)} of the gamepad "
                f"action slots have no vJoy binding and will be dropped if the "
                f"model selects them: {labels}"
            )

        # Load model
        self.model, self.metadata = self._load_model()
        self.model.eval()

        # Check if model is temporal
        self.is_temporal = self.metadata.get("temporal_frames", 1) > 1
        if self.is_temporal:
            self.temporal_frames = self.metadata.get("temporal_frames", temporal_frames)

        # Frame buffer for temporal models
        self.frame_buffer = deque(maxlen=self.temporal_frames)

        # Detect model output size and mouse support
        self.num_actions = self.metadata.get("num_actions", _BASE_ACTION_COUNT)
        self.has_mouse_output = self.num_actions > _BASE_ACTION_COUNT
        self.mouse_output_size = max(0, self.num_actions - _BASE_ACTION_COUNT)

        # Slots the model selected but that have no vJoy binding (warned once)
        self._warned_unmapped_actions = set()

        # Build action weights matching model output size
        self._action_weights = build_action_weights(self.num_actions)

        # Motion detection
        self.motion_log = deque(maxlen=LOG_LEN)
        self.t_minus = None
        self.t_now = None
        self.t_plus = None

        # Stuck recovery state
        self._last_evasion_time = 0.0
        self._consecutive_stuck = 0

        print(f"\n{'=' * 60}")
        print("Inference Engine Initialized")
        print(f"{'=' * 60}")
        print(f"  Model: {self.model_path.name}")
        print(f"  Architecture: {self.metadata.get('model_name', 'Unknown')}")
        print(f"  Device: {self.device}")
        print(f"  Temporal: {self.is_temporal} (frames={self.temporal_frames})")
        print(f"  Gamepad: {'Enabled' if self.enable_gamepad else 'Disabled'}")
        print(
            f"  Actions: {self.num_actions} (mouse={'%d values' % self.mouse_output_size if self.has_mouse_output else 'off'})"
        )
        print(f"{'=' * 60}\n")

    def _load_model(self) -> Tuple[torch.nn.Module, dict]:
        """Load model from checkpoint."""
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found: {self.model_path}")

        model, metadata = load_model(str(self.model_path), device=self.device)
        return model, metadata

    def preprocess_frame(self, frame: np.ndarray) -> torch.Tensor:
        """
        Preprocess frame for model input.

        Args:
            frame: BGR frame from screen capture

        Returns:
            Preprocessed tensor ready for model
        """
        # Resize
        frame = cv2.resize(frame, (WIDTH, HEIGHT))

        # Convert BGR to RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convert to tensor (NCHW format)
        tensor = torch.tensor(frame, dtype=torch.float32)
        tensor = tensor.permute(2, 0, 1)  # HWC -> CHW
        tensor = tensor / 255.0  # Normalize to [0, 1]

        return tensor

    def predict(self, frame: np.ndarray) -> Tuple[int, float, np.ndarray]:
        """
        Run inference on a frame.

        For models with mouse output (num_actions > 29), the mouse values
        are continuous predictions at indices [29:].  The discrete action
        index is chosen only from the first 29 (keyboard+gamepad) slots;
        mouse movement is executed separately via ``execute_mouse()``.

        Args:
            frame: BGR frame from screen capture

        Returns:
            Tuple of (action_index, action_value, raw_predictions)
        """
        # Preprocess
        tensor = self.preprocess_frame(frame)

        # Handle temporal models
        if self.is_temporal:
            self.frame_buffer.append(tensor)

            # Wait until buffer is full
            if len(self.frame_buffer) < self.temporal_frames:
                return 0, 0.0, np.zeros(self.num_actions)

            # Stack frames: (seq, C, H, W)
            input_tensor = torch.stack(list(self.frame_buffer), dim=0)
            input_tensor = input_tensor.unsqueeze(0).to(
                self.device
            )  # (1, seq, C, H, W)
        else:
            input_tensor = tensor.unsqueeze(0).to(self.device)  # (1, C, H, W)

        # Inference
        with torch.no_grad():
            outputs = self.model(input_tensor)
            # Apply sigmoid for multi-label probabilities
            probs = torch.sigmoid(outputs)

        # Convert to numpy
        predictions = probs.cpu().numpy()[0]
        predictions = np.round(predictions, 2)

        # Apply action weights (dynamically sized)
        weighted = predictions * self._action_weights
        weighted_abs = np.abs(weighted)

        # Best discrete action is chosen from first 29 slots only
        # (mouse outputs are continuous, not picked by argmax)
        discrete_end = min(_BASE_ACTION_COUNT, len(weighted_abs))
        action_idx = int(np.argmax(weighted_abs[:discrete_end]))
        action_val = weighted[action_idx]

        return action_idx, action_val, predictions

    def execute_action(self, action_idx: int, action_val: float):
        """
        Execute the predicted action.

        Args:
            action_idx: Index of the action (0-28)
            action_val: Value/confidence of the action
        """
        # Keyboard actions (0-8)
        if action_idx in KEYBOARD_ACTIONS:
            KEYBOARD_ACTIONS[action_idx]()
            return

        # Gamepad actions (9-28)
        if not self.enable_gamepad:
            return

        handler = GAMEPAD_ACTIONS.get(action_idx)
        if handler is None:
            self._report_unmapped_action(action_idx)
            return

        handler(action_val)

    def _report_unmapped_action(self, action_idx: int) -> None:
        """Warn (once per slot) that the model selected an action we cannot press.

        The action space defines 20 gamepad slots but vJoy only exposes bindings
        for ten of them. A model can and does select the unbound slots; without
        this the bot looks like it is playing while the input is dropped.
        """
        if action_idx in self._warned_unmapped_actions:
            return

        self._warned_unmapped_actions.add(action_idx)
        label = (
            ACTION_NAMES[action_idx]
            if action_idx < len(ACTION_NAMES)
            else f"slot {action_idx}"
        )
        print(
            f"[Warn] Model selected gamepad action '{label}' (slot {action_idx}) "
            f"but vJoy exposes no binding for it - input dropped. Add a handler "
            f"in _GAMEPAD_ACTION_HANDLERS to enable it."
        )

    def execute_mouse(self, predictions: np.ndarray):
        """Execute mouse actions from model predictions (optional, additive).

                Only called when ``self.has_mouse_output`` is True.
                Uses delta movement (dx, dy) for smooth camera control via
                linear interpolation, and handles click predictions.

        The mouse values follow the discrete slots, and each one is read by name
                through ``config.action_mapping.MOUSE_FIELDS``, so reordering that
                block cannot silently swap dx with dy. Signed fields (dx, dy, vx, vy,
                scroll) are recorded as ``(v + 1) / 2`` and mapped back here.

                Legacy 6-value checkpoints (x, y, lmb, rmb, mmb, scroll) carry no
                delta, so camera movement is skipped for them.
        """
        if not MOUSE_OUTPUT_AVAILABLE or _MOUSE_CTRL is None:
            return

        if _DENORMALIZE_MOUSE is None:  # pragma: no cover
            # Without the field table there is no safe way to tell which slot
            # holds which mouse value, so decline rather than guess.
            return

        mouse_preds = predictions[_BASE_ACTION_COUNT:]
        if len(mouse_preds) >= MOUSE_OUTPUT_SIZE:
            # Current format: prefer the recorded delta for the camera, which
            # is smoother than moving to the absolute cursor position.
            dx = mouse_preds[_MOUSE_FIELD["dx"].index]
            dy = mouse_preds[_MOUSE_FIELD["dy"].index]
            lmb_prob = mouse_preds[_MOUSE_FIELD["lmb"].index]
            rmb_prob = mouse_preds[_MOUSE_FIELD["rmb"].index]
            scroll_val = mouse_preds[_MOUSE_FIELD["scroll"].index]
        elif len(mouse_preds) >= _LEGACY_MOUSE_OUTPUT_SIZE:
            # Legacy 6-value: no delta was recorded, so drive the camera to a
            # remapped zero instead of pretending the delta was "full left".
            dx = dy = 0.5
            lmb_prob = mouse_preds[2]
            rmb_prob = mouse_preds[3]
            scroll_val = mouse_preds[5]
        else:
            return

        # ── Smooth mouse movement via delta ──
        # dx/dy are sigmoid outputs in [0,1]; the recorder mapped the signed range
        # through (v + 1) / 2, so invert it to recover [-1,1] and scale to
        # pixels. A remapped 0 means "no movement", 1 means "full right".
        dx_remapped = _DENORMALIZE_MOUSE(_MOUSE_FIELD["dx"], dx)
        dy_remapped = _DENORMALIZE_MOUSE(_MOUSE_FIELD["dy"], dy)
        # Scale: max ~100px per frame for smooth camera
        pixel_dx = int(dx_remapped * 100)
        pixel_dy = int(dy_remapped * 100)

        if abs(pixel_dx) > 2 or abs(pixel_dy) > 2:
            _MOUSE_CTRL.move(pixel_dx, pixel_dy)

        # ── Click handling (threshold 0.5) ──
        if lmb_prob > 0.5:
            _MOUSE_CTRL.press(_MBtn.left)
        else:
            _MOUSE_CTRL.release(_MBtn.left)

        if rmb_prob > 0.5:
            _MOUSE_CTRL.press(_MBtn.right)
        else:
            _MOUSE_CTRL.release(_MBtn.right)

        # ── Scroll ──
        scroll_remapped = _DENORMALIZE_MOUSE(_MOUSE_FIELD["scroll"], scroll_val)
        if abs(scroll_remapped) > 0.3:
            _MOUSE_CTRL.scroll(0, int(scroll_remapped * 3))

    def check_stuck(self, delta_count: int) -> bool:
        """
        Check if the character appears stuck based on motion.

        Uses a cooldown to avoid repeated evasive maneuvers.

        Args:
            delta_count: Current frame motion value

        Returns:
            True if stuck detected and cooldown has elapsed
        """
        self.motion_log.append(delta_count)

        if len(self.motion_log) >= LOG_LEN:
            motion_avg = mean(self.motion_log)
            if motion_avg < MOTION_REQ:
                # Respect cooldown so we don't spam evasive maneuvers
                now = time.time()
                if now - self._last_evasion_time >= STUCK_COOLDOWN:
                    return True

        return False

    def evasive_maneuver(self):
        """Execute structured evasive maneuver when stuck.

        Escalates strategy on consecutive detections:
        1st: back up + turn
        2nd: longer reverse + opposite turn
        3rd+: full 180-degree turn attempt
        """
        self._consecutive_stuck += 1
        self._last_evasion_time = time.time()

        level = min(self._consecutive_stuck, 3)
        print(f"STUCK DETECTED (level {level})! Executing evasive maneuver...")

        if level == 1:
            # Simple: back up briefly, turn one direction
            reverse()
            time.sleep(0.8)
            turn = random.choice([forward_left, forward_right])
            turn()
            time.sleep(1.0)
        elif level == 2:
            # Medium: longer reverse, turn opposite direction
            reverse()
            time.sleep(1.5)
            turn = random.choice([left, right])
            turn()
            time.sleep(1.5)
            straight()
            time.sleep(0.5)
        else:
            # Aggressive: full 180 turn
            reverse()
            time.sleep(1.0)
            turn = random.choice([left, right])
            turn()
            time.sleep(2.5)
            straight()
            time.sleep(1.0)

        # Clear motion log so we re-evaluate from fresh state
        self.motion_log.clear()

    def reset_stuck_counter(self):
        """Reset consecutive stuck counter when normal motion resumes."""
        if self._consecutive_stuck > 0 and len(self.motion_log) >= LOG_LEN:
            if mean(self.motion_log) >= MOTION_REQ * 1.5:
                self._consecutive_stuck = 0


# =============================================================================
# Main Loop
# =============================================================================


def check_escape() -> bool:
    """Check if escape key was pressed (Windows only)."""
    if MSVCRT_AVAILABLE:
        import msvcrt

        if msvcrt.kbhit() and ord(msvcrt.getch()) == 27:
            return True
    return False


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="BOT-MMORPG-AI Inference (PyTorch)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--model", required=True, help="Path to model checkpoint (.pth)"
    )
    parser.add_argument(
        "--no-gamepad", action="store_true", help="Disable gamepad output"
    )
    parser.add_argument("--cpu", action="store_true", help="Force CPU inference")
    parser.add_argument(
        "--width", type=int, default=GAME_WIDTH, help="Game window width"
    )
    parser.add_argument(
        "--height", type=int, default=GAME_HEIGHT, help="Game window height"
    )
    parser.add_argument(
        "--delay", type=float, default=0, help="Delay between frames (seconds)"
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args(argv)

    # Check dependencies
    if not PYTORCH_AVAILABLE:
        print(
            "[Error] PyTorch not available. Install with: pip install torch torchvision"
        )
        return 1

    if not MODELS_AVAILABLE:
        print("[Error] models_pytorch.py not found")
        return 1

    if not GRABSCREEN_AVAILABLE:
        print("[Error] Screen capture not available (grabscreen.py)")
        return 1

    if not DIRECTKEYS_AVAILABLE:
        print("[Warning] Keyboard control not available (directkeys.py)")

    # Device
    device = torch.device("cpu") if args.cpu else get_device()

    # Initialize engine
    try:
        engine = InferenceEngine(
            model_path=args.model,
            device=device,
            enable_gamepad=not args.no_gamepad,
        )
    except FileNotFoundError as e:
        print(f"[Error] {e}")
        return 1
    except Exception as e:
        print(f"[Error] Failed to load model: {e}")
        return 1

    # Countdown
    print("\nStarting in...")
    for i in range(3, 0, -1):
        print(f"  {i}")
        time.sleep(1)
    print("GO!\n")

    paused = False
    game_width = args.width
    game_height = args.height

    # Initialize frame buffers for motion detection
    screen = grab_screen(region=(0, 40, game_width, game_height + 40))
    screen = cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)
    prev = cv2.resize(screen, (WIDTH, HEIGHT))

    t_minus = prev
    t_now = prev
    t_plus = prev

    print("Running inference... (Press T to pause, ESC to quit)")
    print("-" * 60)

    try:
        while True:
            loop_start = time.time()

            if not paused:
                # Capture screen
                screen = grab_screen(region=(0, 40, game_width, game_height + 40))
                screen = cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)
                screen_resized = cv2.resize(screen, (WIDTH, HEIGHT))

                # Motion detection
                if MOTION_AVAILABLE:
                    delta_count = motion_detection(
                        t_minus, t_now, t_plus, screen_resized
                    )
                else:
                    delta_count = 1000  # Default high motion

                # Update motion buffers
                t_minus = t_now
                t_now = t_plus
                t_plus = cv2.blur(screen_resized, (4, 4))

                # Predict action
                action_idx, action_val, predictions = engine.predict(screen)

                # Execute action
                engine.execute_action(action_idx, action_val)

                # Execute mouse output if model supports it (additive)
                if engine.has_mouse_output:
                    engine.execute_mouse(predictions)

                # Get action name
                action_name = (
                    ACTION_NAMES[action_idx]
                    if action_idx < len(ACTION_NAMES)
                    else f"action_{action_idx}"
                )

                # Check if stuck or reset counter when moving normally
                if engine.check_stuck(delta_count):
                    engine.evasive_maneuver()
                else:
                    engine.reset_stuck_counter()

                # Logging
                loop_time = time.time() - loop_start
                motion_avg = mean(engine.motion_log) if engine.motion_log else 0

                if args.verbose:
                    print(
                        f"Time: {loop_time:.3f}s | Motion: {motion_avg:.0f} | Action: {action_name} ({action_val:.2f})"
                    )
                else:
                    print(
                        f"Action: {action_name:15} | Motion: {motion_avg:6.0f} | FPS: {1 / max(loop_time, 0.001):.1f}"
                    )

                # Optional delay
                if args.delay > 0:
                    time.sleep(args.delay)

            # Check for pause/escape
            if check_escape():
                print("\nESC pressed - exiting...")
                break

            if GETKEYS_AVAILABLE:
                keys = key_check()
                if "T" in keys:
                    if paused:
                        paused = False
                        print("RESUMED")
                        time.sleep(0.5)
                    else:
                        paused = True
                        release_all_keys()
                        print("PAUSED (press T to resume)")
                        time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n\nKeyboard interrupt - exiting...")

    finally:
        # Clean up
        release_all_keys()
        if VJOY_AVAILABLE:
            ultimate_release()
        print("\nInference stopped.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
