"""
Mouse Capture Module for BOT-MMORPG-AI (Optional Feature)

Records mouse position, delta movement, velocity, and button state for
training models that need mouse input (camera control, targeting, aiming).

This module is OPTIONAL and ADDITIVE — it never modifies or breaks the
existing keyboard/gamepad pipeline.  Import it only when mouse recording
is explicitly enabled by the user.

Industry best practices implemented:
- Absolute position (normalized [0,1]) for targeting / menu clicks
- Delta movement  (normalized [-1,1]) for camera control in 3D MMOs
- Velocity vector  (px/sec, normalized) for smooth camera interpolation
- Per-frame scroll delta for zoom control
- High-frequency raw event accumulation (pynput listener thread)
- Thread-safe lock-free-ish reads (single lock, held <1µs)
- Resolution-independent: all values normalized to capture region

Output vector (10 floats):
  [x, y, dx, dy, vx, vy, lmb, rmb, mmb, scroll]

Backward compatibility:
  MouseState.to_array()        → 10 values (new default)
  MouseState.to_array_legacy() →  6 values (old format, for migration)

Usage:
    from bot_mmorpg.scripts.mouse_capture import MouseCapture

    mc = MouseCapture(capture_region=(0, 0, 1920, 1080))
    mc.start()
    state = mc.snapshot()   # MouseState dataclass
    arr   = state.to_array()   # shape (10,) float32
    mc.stop()
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Optional, Tuple

import numpy as np

# ── Maximum velocity (px / sec) used for normalization ──────────────
_MAX_VELOCITY = 4000.0  # pixels per second (a fast flick on 1080p)

# ── Maximum scroll (steps / frame) used for normalization ─────────────
# Scroll arrives from pynput as an unbounded accumulated step count, so it
# has to be bounded like the other signed fields. One frame at a fast
# flick of the wheel is a good full-scale value.
_MAX_SCROLL_STEPS = 3.0


@dataclass(frozen=True)
class MouseState:
    """Immutable snapshot of mouse state at a single point in time.

    All spatial values are normalized so the model is resolution-independent.

    Attributes:
        x, y       — absolute position [0, 1] relative to capture region
        dx, dy     — delta movement since last snapshot, normalized to [-1, 1]
                     where ±1 means moved the full width/height of the region
        vx, vy     — velocity (px/sec) normalized to [-1, 1] via _MAX_VELOCITY
        lmb, rmb, mmb — button states (0 or 1)
        scroll     — scroll delta since last snapshot, normalized to [-1, 1]
                  via _MAX_SCROLL_STEPS
        timestamp  — time.time() when this snapshot was taken
    """

    x: float = 0.0
    y: float = 0.0
    dx: float = 0.0
    dy: float = 0.0
    vx: float = 0.0
    vy: float = 0.0
    lmb: int = 0
    rmb: int = 0
    mmb: int = 0
    scroll: float = 0.0
    timestamp: float = 0.0

    # ── Serialization ────────────────────────────────────────────────

    def to_array(self) -> np.ndarray:
        """Return [x, y, dx, dy, vx, vy, lmb, rmb, mmb, scroll] as float32 (len 10)."""
        return np.array(
            [
                self.x,
                self.y,
                self.dx,
                self.dy,
                self.vx,
                self.vy,
                float(self.lmb),
                float(self.rmb),
                float(self.mmb),
                self.scroll,
            ],
            dtype=np.float32,
        )

    def to_array_legacy(self) -> np.ndarray:
        """Return [x, y, lmb, rmb, mmb, scroll] as float32 (len 6).

        Provided for backward-compatibility with datasets recorded before
        the delta/velocity upgrade.
        """
        return np.array(
            [
                self.x,
                self.y,
                float(self.lmb),
                float(self.rmb),
                float(self.mmb),
                self.scroll,
            ],
            dtype=np.float32,
        )

    @staticmethod
    def vector_size() -> int:
        """Number of elements in the default output vector."""
        return 10

    @staticmethod
    def vector_size_legacy() -> int:
        """Number of elements in the legacy 6-value vector."""
        return 6

    @staticmethod
    def labels() -> list[str]:
        """Human-readable labels for each element (default 10-element vector)."""
        return [
            "mouse_x",
            "mouse_y",
            "mouse_dx",
            "mouse_dy",
            "mouse_vx",
            "mouse_vy",
            "lmb",
            "rmb",
            "mmb",
            "scroll",
        ]

    @staticmethod
    def labels_legacy() -> list[str]:
        """Labels for the legacy 6-element vector."""
        return ["mouse_x", "mouse_y", "lmb", "rmb", "mmb", "scroll"]


# ── Internal mutable state ──────────────────────────────────────────


@dataclass
class _RawMouseState:
    """Mutable internal state updated by the listener thread."""

    abs_x: int = 0
    abs_y: int = 0
    lmb: int = 0
    rmb: int = 0
    mmb: int = 0
    scroll_accum: float = 0.0
    lock: threading.Lock = field(default_factory=threading.Lock)


# ── Main capture class ──────────────────────────────────────────────


class MouseCapture:
    """Threaded mouse listener that provides low-latency snapshots.

    Parameters
    ----------
    capture_region : tuple (left, top, right, bottom)
        Pixel region used for normalization.  Coordinates outside the
        region are clamped to [0, 1].
    """

    def __init__(self, capture_region: Tuple[int, int, int, int] = (0, 0, 1920, 1080)):
        self._region = capture_region
        self._width = max(1, capture_region[2] - capture_region[0])
        self._height = max(1, capture_region[3] - capture_region[1])
        self._state = _RawMouseState()
        self._listener: Optional[object] = None
        self._running = False

        # Previous snapshot state for delta / velocity computation
        self._prev_abs_x: int = 0
        self._prev_abs_y: int = 0
        self._prev_time: float = 0.0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start capturing mouse events in a background thread."""
        if self._running:
            return

        try:
            from pynput import mouse  # type: ignore[import-untyped]
        except ImportError:
            raise ImportError(
                "pynput is required for mouse capture. "
                "Install it with: pip install pynput"
            )

        def on_move(x: int, y: int) -> None:
            with self._state.lock:
                self._state.abs_x = x
                self._state.abs_y = y

        def on_click(x: int, y: int, button: mouse.Button, pressed: bool) -> None:
            val = 1 if pressed else 0
            with self._state.lock:
                self._state.abs_x = x
                self._state.abs_y = y
                if button == mouse.Button.left:
                    self._state.lmb = val
                elif button == mouse.Button.right:
                    self._state.rmb = val
                elif button == mouse.Button.middle:
                    self._state.mmb = val

        def on_scroll(x: int, y: int, dx: int, dy: int) -> None:
            with self._state.lock:
                self._state.abs_x = x
                self._state.abs_y = y
                self._state.scroll_accum += dy

        self._listener = mouse.Listener(
            on_move=on_move,
            on_click=on_click,
            on_scroll=on_scroll,
        )
        self._listener.start()
        self._running = True

        # Seed from where the cursor actually is. Without this the first move
        # event is differenced against (0, 0), so a 20px nudge records as a
        # full-speed camera whip in both axes and every session opens with a
        # frame that is a lie.
        try:
            pos = mouse.Controller().position
            self._prev_abs_x = int(pos[0])
            self._prev_abs_y = int(pos[1])
            with self._state.lock:
                self._state.abs_x = self._prev_abs_x
                self._state.abs_y = self._prev_abs_y
        except Exception:  # pragma: no cover - cursor position unavailable
            # Leave the defaults; the first frame after a real move will carry
            # a bogus delta, which is no worse than not listening at all.
            pass

    def stop(self) -> None:
        """Stop the listener thread."""
        if self._listener is not None:
            self._listener.stop()
            self._listener = None
        self._running = False

    @property
    def is_running(self) -> bool:
        return self._running

    def snapshot(self) -> MouseState:
        """Return an immutable snapshot of the current mouse state.

        Computes delta movement and velocity since the previous call.
        Scroll accumulator is reset after each call so you get the delta
        since the previous snapshot (matches frame-by-frame recording).
        """
        now = time.time()

        with self._state.lock:
            raw_x = self._state.abs_x
            raw_y = self._state.abs_y
            lmb = self._state.lmb
            rmb = self._state.rmb
            mmb = self._state.mmb
            # Scroll accumulates raw step counts; bound it to [-1, 1] so every
            # signed field in the recorded block shares a single range and the
            # (v + 1) / 2 mapping in config.action_mapping stays valid.
            scroll = max(-1.0, min(1.0, self._state.scroll_accum / _MAX_SCROLL_STEPS))
            self._state.scroll_accum = 0.0

        # ── Absolute position: normalized [0, 1] ──
        left, top = self._region[0], self._region[1]
        norm_x = max(0.0, min(1.0, (raw_x - left) / self._width))
        norm_y = max(0.0, min(1.0, (raw_y - top) / self._height))

        # ── Delta movement: normalized [-1, 1] ──
        pixel_dx = raw_x - self._prev_abs_x
        pixel_dy = raw_y - self._prev_abs_y
        norm_dx = max(-1.0, min(1.0, pixel_dx / self._width))
        norm_dy = max(-1.0, min(1.0, pixel_dy / self._height))

        # ── Velocity: px/sec normalized by _MAX_VELOCITY to [-1, 1] ──
        dt = now - self._prev_time if self._prev_time > 0 else 1.0 / 60
        dt = max(dt, 1e-6)  # avoid division by zero
        vel_x = pixel_dx / dt
        vel_y = pixel_dy / dt
        norm_vx = max(-1.0, min(1.0, vel_x / _MAX_VELOCITY))
        norm_vy = max(-1.0, min(1.0, vel_y / _MAX_VELOCITY))

        # ── Update previous state ──
        self._prev_abs_x = raw_x
        self._prev_abs_y = raw_y
        self._prev_time = now

        return MouseState(
            x=norm_x,
            y=norm_y,
            dx=norm_dx,
            dy=norm_dy,
            vx=norm_vx,
            vy=norm_vy,
            lmb=lmb,
            rmb=rmb,
            mmb=mmb,
            scroll=scroll,
            timestamp=now,
        )

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    def __enter__(self) -> "MouseCapture":
        self.start()
        return self

    def __exit__(self, *exc: object) -> None:
        self.stop()

    def __del__(self) -> None:
        self.stop()
