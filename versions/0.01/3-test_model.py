"""
BOT-MMORPG-AI Inference Script (PyTorch)

Run trained models on live gameplay for automated control.
Supports multiple architectures with real-time inference.

Usage:
    python 3-test_model.py --model artifacts/model/efficientnet_lstm_best.pth
    python 3-test_model.py --model artifacts/model/mobilenet_v3_final.pth --no-gamepad
"""

from __future__ import annotations

import argparse
import sys
import os
import time
import random
import platform
from pathlib import Path
from collections import deque
from statistics import mean
from typing import Optional, List, Tuple

import numpy as np
import cv2

# PyTorch imports
try:
    import torch
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False
    print("[Warning] PyTorch not installed. Install with: pip install torch torchvision")

# Local imports - screen capture
try:
    from grabscreen import grab_screen
    GRABSCREEN_AVAILABLE = True
except ImportError:
    GRABSCREEN_AVAILABLE = False

# Local imports - keyboard control
try:
    from directkeys import PressKey, ReleaseKey, W, A, S, D
    DIRECTKEYS_AVAILABLE = True
except ImportError:
    DIRECTKEYS_AVAILABLE = False

# Local imports - key checking
try:
    from getkeys import key_check
    GETKEYS_AVAILABLE = True
except ImportError:
    GETKEYS_AVAILABLE = False

# Local imports - motion detection
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
    from vjoy2 import (
        gamepad_lt, gamepad_rt, game_lx_left, game_lx_right,
        game_ly_down, game_ly_up, look_rx_left, look_rx_right,
        look_ry_down, look_ry_up, button_A, button_B, button_X, button_Y,
        ultimate_release
    )
    VJOY_AVAILABLE = True
except ImportError:
    VJOY_AVAILABLE = False
    def ultimate_release(): pass

# Local imports - PyTorch models
try:
    from models_pytorch import load_model, get_model_info, get_device
    MODELS_AVAILABLE = True
except ImportError:
    MODELS_AVAILABLE = False

# Platform-specific imports
IS_WINDOWS = platform.system() == 'Windows'
if IS_WINDOWS:
    try:
        import msvcrt
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
MOTION_REQ = 800

# Action weights for prediction adjustment
# Format: [keyboard(9), gamepad(20)] = 29 base actions
_BASE_ACTION_WEIGHTS = np.array([
    4.5, 0.1, 0.1, 0.1, 1.8, 1.8, 0.5, 0.5, 0.2,  # Keyboard: W, S, A, D, WA, WD, SA, SD, NK
    1, 1, 1, 1, 1, 1,  # Gamepad: LT, RT, Lx, Ly, Rx, Ry
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1,  # Gamepad: UP, DOWN, LEFT, RIGHT, START, SELECT, L3, R3, LB, RB
    1, 1, 1, 1  # Gamepad: A, B, X, Y
])

# Mouse weight block: [x, y, dx, dy, vx, vy, lmb, rmb, mmb, scroll].
# Position/delta/velocity are continuous outputs (never chosen by argmax),
# so their weights stay low and out of the way of discrete actions.
_MOUSE_WEIGHTS_10 = np.array([0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 1.0, 1.0, 0.8, 0.3])

# Legacy 6-value mouse: [x, y, lmb, rmb, mmb, scroll]
_MOUSE_WEIGHTS_6 = np.array([0.1, 0.1, 1.0, 1.0, 0.8, 0.3])


def build_action_weights(num_actions: int) -> np.ndarray:
    """Build an action-weight array matching the model's output width.

    Recording with the mouse enabled appends 10 values to the 29-slot
    keyboard+gamepad vector, so a model trained that way emits 39
    outputs. Multiplying those 39 predictions by a fixed 29-slot weight
    array raised a broadcast error at the first frame (issue #82).
    """
    if num_actions <= 29:
        return _BASE_ACTION_WEIGHTS[:num_actions].copy()

    mouse_size = num_actions - 29
    if mouse_size == 10:
        mouse_w = _MOUSE_WEIGHTS_10
    elif mouse_size == 6:
        mouse_w = _MOUSE_WEIGHTS_6
    else:
        # Unknown mouse layout - neutral weight, still never argmax'd
        mouse_w = np.ones(mouse_size) * 0.5

    return np.concatenate([_BASE_ACTION_WEIGHTS, mouse_w])


# Default for backward compatibility (29 actions, no mouse)
ACTION_WEIGHTS = build_action_weights(29)

# Action names for logging
ACTION_NAMES = [
    'straight', 'reverse', 'left', 'right', 'forward+left', 'forward+right',
    'reverse+left', 'reverse+right', 'nokeys',
    'LT', 'RT', 'Lx', 'Ly', 'Rx', 'Ry',
    'UP', 'DOWN', 'LEFT', 'RIGHT', 'START', 'SELECT', 'L3', 'R3', 'LB', 'RB',
    'A', 'B', 'X', 'Y'
]


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

        # Load model
        self.model, self.metadata = self._load_model()
        self.model.eval()

        # Output width the checkpoint was actually trained with. load_model
        # resolves this from the checkpoint (metadata, else the stored
        # weights), so a mouse-enabled model (39 outputs) runs without the
        # "size mismatch for action_head" failure of issue #82.
        self.num_actions = int(
            self.metadata.get('num_actions', getattr(self.model, 'num_actions', 29))
        )
        self.has_mouse_output = self.num_actions > 29
        self._action_weights = build_action_weights(self.num_actions)

        # Check if model is temporal
        self.is_temporal = self.metadata.get('temporal_frames', 1) > 1
        if self.is_temporal:
            self.temporal_frames = self.metadata.get('temporal_frames', temporal_frames)

        # Frame buffer for temporal models
        self.frame_buffer = deque(maxlen=self.temporal_frames)

        # Motion detection
        self.motion_log = deque(maxlen=LOG_LEN)
        self.t_minus = None
        self.t_now = None
        self.t_plus = None

        print(f"\n{'='*60}")
        print(f"Inference Engine Initialized")
        print(f"{'='*60}")
        print(f"  Model: {self.model_path.name}")
        print(f"  Architecture: {self.metadata.get('model_name', 'Unknown')}")
        print(f"  Device: {self.device}")
        print(
            f"  Actions: {self.num_actions} "
            f"(mouse={'on' if self.has_mouse_output else 'off'})"
        )
        print(f"  Temporal: {self.is_temporal} (frames={self.temporal_frames})")
        print(f"  Gamepad: {'Enabled' if self.enable_gamepad else 'Disabled'}")
        print(f"{'='*60}\n")

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
                return 0, 0.0, np.zeros(self.num_actions)  # Default action

            # Stack frames: (seq, C, H, W)
            input_tensor = torch.stack(list(self.frame_buffer), dim=0)
            input_tensor = input_tensor.unsqueeze(0).to(self.device)  # (1, seq, C, H, W)
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

        # Apply action weights (sized to this model's output width)
        weighted = predictions * self._action_weights
        weighted_abs = np.abs(weighted)

        # The best discrete action comes from the first 29 slots only;
        # mouse outputs beyond them are continuous, not argmax candidates.
        discrete_end = min(29, len(weighted_abs))
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

        if action_idx == 9:
            gamepad_lt()
        elif action_idx == 10:
            gamepad_rt()
        elif action_idx == 11:
            if action_val < 0:
                game_lx_left()
            else:
                game_lx_right()
        elif action_idx == 12:
            if action_val < 0:
                game_ly_down()
            else:
                game_ly_up()
        elif action_idx == 13:
            if action_val < 0:
                look_rx_left()
            else:
                look_rx_right()
        elif action_idx == 14:
            if action_val < 0:
                look_ry_down()
            else:
                look_ry_up()
        # D-pad and buttons (15-28)
        elif action_idx == 25:
            button_A()
        elif action_idx == 26:
            button_B()
        elif action_idx == 27:
            button_X()
        elif action_idx == 28:
            button_Y()

    def check_stuck(self, delta_count: int) -> bool:
        """
        Check if the character appears stuck based on motion.

        Args:
            delta_count: Current frame motion value

        Returns:
            True if stuck detected
        """
        self.motion_log.append(delta_count)

        if len(self.motion_log) >= LOG_LEN:
            motion_avg = mean(self.motion_log)
            if motion_avg < MOTION_REQ:
                return True

        return False

    def evasive_maneuver(self):
        """Execute random evasive maneuver when stuck."""
        print("STUCK DETECTED! Executing evasive maneuver...")

        choice = random.randrange(0, 4)

        if choice == 0:
            reverse()
            time.sleep(random.uniform(1, 2))
            forward_left()
            time.sleep(random.uniform(1, 2))
        elif choice == 1:
            reverse()
            time.sleep(random.uniform(1, 2))
            forward_right()
            time.sleep(random.uniform(1, 2))
        elif choice == 2:
            reverse_left()
            time.sleep(random.uniform(1, 2))
            forward_right()
            time.sleep(random.uniform(1, 2))
        elif choice == 3:
            reverse_right()
            time.sleep(random.uniform(1, 2))
            forward_left()
            time.sleep(random.uniform(1, 2))

        # Clear most of motion log
        for _ in range(LOG_LEN - 2):
            if self.motion_log:
                self.motion_log.popleft()


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

    parser.add_argument("--model", required=True, help="Path to model checkpoint (.pth)")
    parser.add_argument("--no-gamepad", action="store_true", help="Disable gamepad output")
    parser.add_argument("--cpu", action="store_true", help="Force CPU inference")
    parser.add_argument("--width", type=int, default=GAME_WIDTH, help="Game window width")
    parser.add_argument("--height", type=int, default=GAME_HEIGHT, help="Game window height")
    parser.add_argument("--delay", type=float, default=0, help="Delay between frames (seconds)")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args(argv)

    # Check dependencies
    if not PYTORCH_AVAILABLE:
        print("[Error] PyTorch not available. Install with: pip install torch torchvision")
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
                    delta_count = motion_detection(t_minus, t_now, t_plus, screen_resized)
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

                # Get action name
                action_name = ACTION_NAMES[action_idx] if action_idx < len(ACTION_NAMES) else f"action_{action_idx}"

                # Check if stuck
                if engine.check_stuck(delta_count):
                    engine.evasive_maneuver()

                # Logging
                loop_time = time.time() - loop_start
                motion_avg = mean(engine.motion_log) if engine.motion_log else 0

                if args.verbose:
                    print(f"Time: {loop_time:.3f}s | Motion: {motion_avg:.0f} | Action: {action_name} ({action_val:.2f})")
                else:
                    print(f"Action: {action_name:15} | Motion: {motion_avg:6.0f} | FPS: {1/max(loop_time, 0.001):.1f}")

                # Optional delay
                if args.delay > 0:
                    time.sleep(args.delay)

            # Check for pause/escape
            if check_escape():
                print("\nESC pressed - exiting...")
                break

            if GETKEYS_AVAILABLE:
                keys = key_check()
                if 'T' in keys:
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
