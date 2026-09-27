"""
Tests for optional Mouse Capture module.

Validates MouseState dataclass, MouseCapture coordinate normalization,
and thread safety — all without needing an actual display or pynput listener.
"""

import threading
import time

import numpy as np
import pytest


class TestMouseState:
    """Test MouseState dataclass and serialization."""

    def test_default_values(self):
        """Test default MouseState is all-zero."""
        from bot_mmorpg.scripts.mouse_capture import MouseState

        state = MouseState()
        assert state.x == 0.0
        assert state.y == 0.0
        assert state.lmb == 0
        assert state.rmb == 0
        assert state.mmb == 0
        assert state.scroll == 0.0

    def test_to_array_shape(self):
        """Test to_array returns 10-element vector (x,y,dx,dy,vx,vy,lmb,rmb,mmb,scroll)."""
        from bot_mmorpg.scripts.mouse_capture import MouseState

        state = MouseState(
            x=0.5,
            y=0.25,
            dx=0.01,
            dy=-0.02,
            vx=0.1,
            vy=-0.1,
            lmb=1,
            rmb=0,
            mmb=1,
            scroll=-2.0,
        )
        arr = state.to_array()

        assert arr.shape == (10,)
        assert arr.dtype == np.float32
        np.testing.assert_array_almost_equal(
            arr, [0.5, 0.25, 0.01, -0.02, 0.1, -0.1, 1.0, 0.0, 1.0, -2.0]
        )

    def test_to_array_legacy_shape(self):
        """Test to_array_legacy returns 6-element backward-compatible vector."""
        from bot_mmorpg.scripts.mouse_capture import MouseState

        state = MouseState(x=0.5, y=0.25, lmb=1, rmb=0, mmb=1, scroll=-2.0)
        arr = state.to_array_legacy()

        assert arr.shape == (6,)
        assert arr.dtype == np.float32
        np.testing.assert_array_almost_equal(arr, [0.5, 0.25, 1.0, 0.0, 1.0, -2.0])

    def test_vector_size(self):
        """Test vector_size matches array length."""
        from bot_mmorpg.scripts.mouse_capture import MouseState

        assert MouseState.vector_size() == 10
        assert len(MouseState().to_array()) == MouseState.vector_size()
        assert MouseState.vector_size_legacy() == 6
        assert len(MouseState().to_array_legacy()) == MouseState.vector_size_legacy()

    def test_labels_match_vector_size(self):
        """Test labels list matches vector size."""
        from bot_mmorpg.scripts.mouse_capture import MouseState

        labels = MouseState.labels()
        assert len(labels) == MouseState.vector_size()
        assert "mouse_x" in labels
        assert "mouse_dx" in labels
        assert "mouse_vx" in labels
        assert "lmb" in labels

        labels_legacy = MouseState.labels_legacy()
        assert len(labels_legacy) == MouseState.vector_size_legacy()

    def test_frozen_dataclass(self):
        """Test MouseState is immutable (frozen)."""
        from bot_mmorpg.scripts.mouse_capture import MouseState

        state = MouseState(x=0.5, y=0.5)
        with pytest.raises(AttributeError):
            state.x = 0.9  # type: ignore[misc]


class TestMouseCaptureNormalization:
    """Test coordinate normalization without pynput listener."""

    def test_normalize_center(self):
        """Test that center of region normalizes to (0.5, 0.5)."""
        from bot_mmorpg.scripts.mouse_capture import MouseCapture

        mc = MouseCapture(capture_region=(0, 0, 1920, 1080))

        # Simulate mouse at center
        with mc._state.lock:
            mc._state.abs_x = 960
            mc._state.abs_y = 540

        state = mc.snapshot()
        assert abs(state.x - 0.5) < 0.01
        assert abs(state.y - 0.5) < 0.01

    def test_normalize_origin(self):
        """Test that top-left of region normalizes to (0, 0)."""
        from bot_mmorpg.scripts.mouse_capture import MouseCapture

        mc = MouseCapture(capture_region=(100, 200, 1100, 1200))

        with mc._state.lock:
            mc._state.abs_x = 100
            mc._state.abs_y = 200

        state = mc.snapshot()
        assert state.x == 0.0
        assert state.y == 0.0

    def test_normalize_bottom_right(self):
        """Test that bottom-right of region normalizes to (1, 1)."""
        from bot_mmorpg.scripts.mouse_capture import MouseCapture

        mc = MouseCapture(capture_region=(0, 0, 800, 600))

        with mc._state.lock:
            mc._state.abs_x = 800
            mc._state.abs_y = 600

        state = mc.snapshot()
        assert state.x == 1.0
        assert state.y == 1.0

    def test_clamp_outside_region(self):
        """Test coordinates outside region are clamped to [0, 1]."""
        from bot_mmorpg.scripts.mouse_capture import MouseCapture

        mc = MouseCapture(capture_region=(100, 100, 500, 500))

        # Way outside left/top
        with mc._state.lock:
            mc._state.abs_x = 0
            mc._state.abs_y = 0

        state = mc.snapshot()
        assert state.x == 0.0
        assert state.y == 0.0

        # Way outside right/bottom
        with mc._state.lock:
            mc._state.abs_x = 9999
            mc._state.abs_y = 9999

        state = mc.snapshot()
        assert state.x == 1.0
        assert state.y == 1.0

    def test_custom_region(self):
        """Test normalization with offset capture region."""
        from bot_mmorpg.scripts.mouse_capture import MouseCapture

        mc = MouseCapture(capture_region=(200, 100, 1000, 700))

        with mc._state.lock:
            mc._state.abs_x = 600  # 50% of 800-wide region from 200
            mc._state.abs_y = 400  # 50% of 600-tall region from 100

        state = mc.snapshot()
        assert abs(state.x - 0.5) < 0.01
        assert abs(state.y - 0.5) < 0.01


class TestMouseCaptureButtons:
    """Test button and scroll state capture."""

    def test_button_states(self):
        """Test button states are captured correctly."""
        from bot_mmorpg.scripts.mouse_capture import MouseCapture

        mc = MouseCapture()

        with mc._state.lock:
            mc._state.lmb = 1
            mc._state.rmb = 0
            mc._state.mmb = 1

        state = mc.snapshot()
        assert state.lmb == 1
        assert state.rmb == 0
        assert state.mmb == 1

    def test_scroll_accumulation(self):
        """Test scroll delta accumulates and resets per snapshot."""
        from bot_mmorpg.scripts import mouse_capture
        from bot_mmorpg.scripts.mouse_capture import MouseCapture

        mc = MouseCapture()

        # Half of full scale, so the normalisation by _MAX_SCROLL_STEPS is
        # visible without landing on the clamp.
        with mc._state.lock:
            mc._state.scroll_accum = mouse_capture._MAX_SCROLL_STEPS / 2

        state1 = mc.snapshot()
        assert state1.scroll == 0.5

        # Scroll should be reset after snapshot
        state2 = mc.snapshot()
        assert state2.scroll == 0.0

    def test_negative_scroll(self):
        """Test negative scroll (scroll down)."""
        from bot_mmorpg.scripts import mouse_capture
        from bot_mmorpg.scripts.mouse_capture import MouseCapture

        mc = MouseCapture()

        with mc._state.lock:
            mc._state.scroll_accum = -mouse_capture._MAX_SCROLL_STEPS / 2

        state = mc.snapshot()
        assert state.scroll == -0.5

    def test_scroll_beyond_full_scale_is_clamped(self):
        """A fast wheel flick sends more steps than one frame can express,
        so snapshot() has to bound it. Without the clamp the recorded block
        leaves the [0, 1] range the rest of the pipeline assumes.
        """
        from bot_mmorpg.scripts.mouse_capture import MouseCapture

        mc = MouseCapture()

        for accum, expected in ((50.0, 1.0), (-50.0, -1.0)):
            with mc._state.lock:
                mc._state.scroll_accum = accum
            assert mc.snapshot().scroll == expected


class TestMouseCaptureFirstFrame:
    """The first move after start() must not be differenced against (0, 0).

    Unseeded, a 20px nudge recorded as dx=+0.48 dy=+0.56 with the velocity
    pinned at the ceiling: a full-speed camera whip in both axes, on the very
    first frame of every session, which the model would then be trained on.
    """

    @staticmethod
    def _fake_pynput(position):
        """Stand in for pynput.mouse so this runs without a real cursor."""
        import types

        mouse_mod = types.ModuleType("pynput.mouse")

        class _Controller:
            @property
            def position(self):
                return position

        class _Listener:
            def __init__(self, **kwargs):
                self.kwargs = kwargs

            def start(self):
                pass

            def stop(self):
                pass

        mouse_mod.Controller = _Controller
        mouse_mod.Listener = _Listener
        mouse_mod.Button = types.SimpleNamespace(
            left="left", right="right", middle="middle"
        )
        pynput_mod = types.ModuleType("pynput")
        pynput_mod.mouse = mouse_mod
        return pynput_mod

    def test_start_seeds_position_and_delta_baseline(self, monkeypatch):
        import sys

        from bot_mmorpg.scripts.mouse_capture import MouseCapture

        pynput_mod = self._fake_pynput((900, 600))
        monkeypatch.setitem(sys.modules, "pynput", pynput_mod)
        monkeypatch.setitem(sys.modules, "pynput.mouse", pynput_mod.mouse)

        mc = MouseCapture(capture_region=(0, 0, 1920, 1080))
        mc.start()
        try:
            assert (mc._prev_abs_x, mc._prev_abs_y) == (900, 600)

            first = mc.snapshot()
            # No movement has happened, so the frame must report none.
            assert first.dx == 0.0
            assert first.dy == 0.0
            assert first.vx == 0.0
            assert first.vy == 0.0
            # Position must be real, not the (0, 0) fallback.
            assert first.x == pytest.approx(900 / 1920)
            assert first.y == pytest.approx(600 / 1080)
        finally:
            mc.stop()

    def test_first_nudge_is_measured_against_the_cursor(self, monkeypatch):
        """20px right reads as ~0.0104, not as the absolute position."""
        import sys

        from bot_mmorpg.scripts.mouse_capture import MouseCapture

        pynput_mod = self._fake_pynput((900, 600))
        monkeypatch.setitem(sys.modules, "pynput", pynput_mod)
        monkeypatch.setitem(sys.modules, "pynput.mouse", pynput_mod.mouse)

        mc = MouseCapture(capture_region=(0, 0, 1920, 1080))
        mc.start()
        try:
            mc.snapshot()  # settle the timer
            with mc._state.lock:  # a real move event lands at 920, 600
                mc._state.abs_x = 920
                mc._state.abs_y = 600
            moved = mc.snapshot()
            assert moved.dx == pytest.approx(20 / 1920)
            assert moved.dy == 0.0
        finally:
            mc.stop()


class TestMouseCaptureThreadSafety:
    """Test thread safety of snapshot and state updates."""

    def test_concurrent_snapshots(self):
        """Test that concurrent snapshots don't corrupt data."""
        from bot_mmorpg.scripts.mouse_capture import MouseCapture

        mc = MouseCapture(capture_region=(0, 0, 1000, 1000))
        results = []
        errors = []

        def worker():
            try:
                for i in range(100):
                    with mc._state.lock:
                        mc._state.abs_x = i * 10
                        mc._state.abs_y = i * 10
                    state = mc.snapshot()
                    arr = state.to_array()
                    assert arr.shape == (10,)
                    assert 0.0 <= state.x <= 1.0
                    assert 0.0 <= state.y <= 1.0
                    results.append(state)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"Thread errors: {errors}"
        assert len(results) == 400

    def test_snapshot_timestamp(self):
        """Test that snapshots have increasing timestamps."""
        from bot_mmorpg.scripts.mouse_capture import MouseCapture

        mc = MouseCapture()
        s1 = mc.snapshot()
        time.sleep(0.01)
        s2 = mc.snapshot()

        assert s2.timestamp > s1.timestamp


class TestMouseCaptureIntegration:
    """Test integration with existing data pipeline."""

    def test_concat_with_keyboard_gamepad(self):
        """Test that mouse vector concatenates with keyboard/gamepad vectors."""
        from bot_mmorpg.scripts.mouse_capture import MouseState

        # Simulate typical pipeline: keyboard(9) + gamepad(20) + mouse(10)
        keyboard_output = np.array([1, 0, 0, 0, 0, 0, 0, 0, 0])
        gamepad_output = np.zeros(20, dtype=int)
        mouse_state = MouseState(
            x=0.5, y=0.3, dx=0.01, dy=-0.02, vx=0.1, vy=-0.1, lmb=1
        )
        mouse_output = mouse_state.to_array()

        combined = np.concatenate([keyboard_output, gamepad_output, mouse_output])

        assert combined.shape == (39,)  # 9 + 20 + 10
        assert combined[0] == 1  # W key
        assert abs(combined[29] - 0.5) < 0.01  # mouse_x
        assert abs(combined[30] - 0.3) < 0.01  # mouse_y
        assert abs(combined[31] - 0.01) < 0.001  # mouse_dx
        assert combined[35] == 1.0  # lmb (index 29+6)

    def test_array_save_load_roundtrip(self, tmp_path):
        """Test that mouse data survives numpy save/load."""
        from bot_mmorpg.scripts.mouse_capture import MouseState

        state = MouseState(
            x=0.75,
            y=0.25,
            dx=0.05,
            dy=-0.1,
            vx=0.3,
            vy=-0.2,
            lmb=1,
            rmb=0,
            mmb=0,
            scroll=2.5,
        )
        arr = state.to_array()

        path = tmp_path / "mouse_test.npy"
        np.save(str(path), arr)
        loaded = np.load(str(path))

        np.testing.assert_array_almost_equal(arr, loaded)
