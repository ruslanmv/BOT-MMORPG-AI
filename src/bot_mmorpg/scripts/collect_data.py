"""
Data Collection Script for BOT-MMORPG-AI

Captures screen and input data for training neural networks.
Includes comprehensive error handling for production use.

Supports keyboard, gamepad, and optional mouse recording.
Mouse recording is additive and non-destructive: when enabled it
appends 6 extra values to the action vector; when disabled the
existing keyboard+gamepad pipeline is completely unchanged.
"""

import argparse
import logging
import time
from pathlib import Path
from typing import List, Optional, Tuple

import cv2
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# Import helper modules with fallback
try:
    from .getgamepad import gamepad_check
    from .getkeys import key_check
    from .grabscreen import grab_screen
except ImportError:
    try:
        from getgamepad import gamepad_check
        from getkeys import key_check
        from grabscreen import grab_screen
    except ImportError as e:
        logger.error(f"Failed to import required modules: {e}")
        logger.error(
            "Please ensure grabscreen.py, getkeys.py, and getgamepad.py are available"
        )
        grab_screen = None
        key_check = None
        gamepad_check = None

# Optional mouse capture – additive only, never breaks existing pipeline
try:
    from .mouse_capture import MouseCapture
except ImportError:
    try:
        from mouse_capture import MouseCapture
    except ImportError:
        MouseCapture = None


#: Frame size the whole pipeline agrees on: collect_data.py records at it,
#: test_model.py resizes to it, train_model.py does not rescale. A profile may
#: ask for something else (see :func:`resolve_target_size`) but it cannot win.
DEFAULT_TARGET_SIZE = (480, 270)

#: Used only when the config package cannot be imported at all.
_FALLBACK_BASE_ACTIONS = 29
_FALLBACK_MOUSE_ACTIONS = 10


def _load_action_space():
    """Resolve the shared action space through every import path this script has.

    Returns:
        Tuple of (action_space or None, mouse_output_size, mouse_fields,
        normalize_mouse_vector or None). The last two are empty only in the
        built-in fallback, where there is no field table to normalise against.
    """
    try:
        from ..config.action_mapping import (  # normal package import
            DEFAULT_ACTION_SPACE_NAME,
            MOUSE_FIELDS,
            MOUSE_OUTPUT_SIZE,
            get_pipeline_action_space,
            normalize_mouse_vector,
        )
    except ImportError:  # pragma: no cover - exercised only when run as a script
        try:
            from config.action_mapping import (
                DEFAULT_ACTION_SPACE_NAME,
                MOUSE_FIELDS,
                MOUSE_OUTPUT_SIZE,
                get_pipeline_action_space,
                normalize_mouse_vector,
            )
        except ImportError:
            try:
                import sys as _sys
                from pathlib import Path as _Path

                _pkg_root = _Path(__file__).resolve().parent.parent
                if str(_pkg_root) not in _sys.path:
                    _sys.path.insert(0, str(_pkg_root))
                from config.action_mapping import (
                    DEFAULT_ACTION_SPACE_NAME,
                    MOUSE_FIELDS,
                    MOUSE_OUTPUT_SIZE,
                    get_pipeline_action_space,
                    normalize_mouse_vector,
                )
            except ImportError:
                logger.warning(
                    "config.action_mapping not reachable; falling back to the "
                    f"built-in {_FALLBACK_BASE_ACTIONS}-slot layout. "
                    "Slot order stays identical, but the action space is no "
                    "longer validated at import time."
                )
                return None, _FALLBACK_MOUSE_ACTIONS, (), None

    return (
        get_pipeline_action_space(DEFAULT_ACTION_SPACE_NAME),
        MOUSE_OUTPUT_SIZE,
        MOUSE_FIELDS,
        normalize_mouse_vector,
    )


# Action space definition -- single source of truth for keyboard slot order.
ACTION_SPACE, MOUSE_OUTPUT_SIZE, MOUSE_FIELDS, _NORMALIZE_MOUSE = _load_action_space()

#: Number of keyboard slots at the head of the action space.
_KEYBOARD_SLOT_COUNT = 9

#: (action_id, key combo) pairs in slot order, derived from the action space.
if ACTION_SPACE is not None:
    _KEYBOARD_SLOTS = [
        (
            action.id,
            tuple(action.key_binding.split("+")) if action.key_binding else (),
        )
        for action in ACTION_SPACE.actions[:_KEYBOARD_SLOT_COUNT]
    ]
    _NO_KEY_ID = ACTION_SPACE.actions[_KEYBOARD_SLOT_COUNT - 1].id
else:  # pragma: no cover - config package unavailable
    _KEYBOARD_SLOTS = [
        (0, ("W",)),
        (1, ("S",)),
        (2, ("A",)),
        (3, ("D",)),
        (4, ("W", "A")),
        (5, ("W", "D")),
        (6, ("S", "A")),
        (7, ("S", "D")),
        (8, ()),
    ]
    _NO_KEY_ID = 8


class DataCollectionError(Exception):
    """Custom exception for data collection errors."""

    pass


class ScreenCaptureError(DataCollectionError):
    """Raised when screen capture fails."""

    pass


def base_action_count() -> int:
    """Number of keyboard+gamepad slots the pipeline records."""
    if ACTION_SPACE is not None:
        return ACTION_SPACE.num_actions
    return _FALLBACK_BASE_ACTIONS


def expected_action_width(with_mouse: bool) -> int:
    """Number of values in one recorded action vector."""
    return base_action_count() + (MOUSE_OUTPUT_SIZE if with_mouse else 0)


def describe_action_space() -> str:
    """One-line human readable breakdown of the recorded action vector."""
    gamepad_slots = base_action_count() - _KEYBOARD_SLOT_COUNT
    return (
        f"{base_action_count()} actions "
        f"({_KEYBOARD_SLOT_COUNT} keyboard + {gamepad_slots} gamepad) "
        f"+ {MOUSE_OUTPUT_SIZE} mouse = {expected_action_width(True)} values"
    )


def resolve_target_size(profile) -> Tuple[int, int]:
    """Frame size to record at, for *profile* (or ``None`` for the default).

    The profile's ``recommended_input_size`` is honoured only when it matches
    the rest of the pipeline. Any other value is reported and replaced, because
    a differently sized dataset cannot be fed to ``test_model.py`` without
    re-recording.
    """
    pipeline = f"{DEFAULT_TARGET_SIZE[0]}x{DEFAULT_TARGET_SIZE[1]}"

    if profile is None:
        return DEFAULT_TARGET_SIZE

    try:
        size = tuple(int(v) for v in profile.recommended_input_size)
    except (TypeError, ValueError):
        size = ()

    if len(size) != 2 or any(v <= 0 for v in size):
        logger.warning(
            f"Profile '{profile.id}' has an unreadable recommended_input_size "
            f"({getattr(profile, 'recommended_input_size', None)!r}). "
            f"Recording at the pipeline size {pipeline}."
        )
        return DEFAULT_TARGET_SIZE

    if size != DEFAULT_TARGET_SIZE:
        logger.warning(
            f"Profile '{profile.id}' recommends {size[0]}x{size[1]} but the "
            f"pipeline records {pipeline} (test_model.py resizes to it, "
            f"train_model.py does not rescale). Recording at {pipeline}."
        )
        return DEFAULT_TARGET_SIZE

    return size


def validate_profile(profile) -> None:
    """Check a game profile against the action space this script records.

    Args:
        profile: Loaded ``GameProfile``, or ``None`` when ``--game`` was not used.

    Raises:
        DataCollectionError: If the profile declares an action count the
            pipeline cannot produce.
    """
    if profile is None:
        return

    base = base_action_count()
    declared_space = str(getattr(profile, "action_space", "") or "")
    if declared_space and ACTION_SPACE is not None:
        if declared_space != ACTION_SPACE.name:
            logger.warning(
                f"Profile '{profile.id}' declares action_space "
                f"'{declared_space}' but the pipeline records "
                f"'{ACTION_SPACE.name}'. Using the pipeline layout."
            )

    try:
        declared = int(profile.num_actions)
    except (TypeError, ValueError):
        declared = -1

    if declared in (base, base + MOUSE_OUTPUT_SIZE):
        return

    raise DataCollectionError(
        f"Profile '{profile.id}' declares num_actions: {declared}, but this "
        f"pipeline records {base} values without --mouse and "
        f"{base + MOUSE_OUTPUT_SIZE} with it. A dataset recorded from this "
        f"profile would not line up with a trained model. Set "
        f"input.num_actions to {base} in the profile."
    )


class InputCaptureError(DataCollectionError):
    """Raised when input capture fails."""

    pass


def keys_to_output(keys: List[str]) -> List[int]:
    """
    One-hot encode keyboard input into the action space's keyboard slots.

    The action space (``bot_mmorpg.config.action_mapping``) owns the slot order
    and the key combinations; this function only resolves which slot the keys
    currently held match. The most specific (longest) combination wins, so
    holding W+A selects ``move_forward_left`` rather than ``move_forward``.

    Args:
        keys: List of pressed key characters

    Returns:
        One-hot encoded list ordered like ``KEYBOARD_BASE_ACTIONS`` --
        [W, S, A, D, WA, WD, SA, SD, NOKEY]
    """
    output = [0] * _KEYBOARD_SLOT_COUNT
    best_id, best_len = _NO_KEY_ID, 0

    for action_id, combo in _KEYBOARD_SLOTS:
        if combo and len(combo) > best_len and all(key in keys for key in combo):
            best_id, best_len = action_id, len(combo)

    output[best_id] = 1
    return output


def gamepad_keys_to_output(lista: List) -> List[int]:
    """Convert gamepad input to integer list."""
    return [int(elem) for elem in lista]


def validate_dependencies() -> bool:
    """
    Validate that all required dependencies are available.

    Returns:
        True if all dependencies are available

    Raises:
        DataCollectionError: If dependencies are missing
    """
    missing = []

    if grab_screen is None:
        missing.append("grabscreen")
    if key_check is None:
        missing.append("getkeys")
    if gamepad_check is None:
        missing.append("getgamepad")

    if missing:
        raise DataCollectionError(
            f"Missing required modules: {', '.join(missing)}. "
            "Please ensure all helper modules are installed."
        )

    return True


def capture_screen(
    region: Tuple[int, int, int, int],
    target_size: Tuple[int, int] = DEFAULT_TARGET_SIZE,
) -> np.ndarray:
    """
    Capture and process screen region.

    Args:
        region: Screen region (x1, y1, x2, y2)
        target_size: Target resize dimensions (width, height)

    Returns:
        Processed screen image as numpy array

    Raises:
        ScreenCaptureError: If capture fails
    """
    try:
        screen = grab_screen(region=region)

        if screen is None or screen.size == 0:
            raise ScreenCaptureError("Screen capture returned empty image")

        # Resize
        screen = cv2.resize(screen, target_size)

        # Convert color space
        screen = cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)

        return screen

    except ScreenCaptureError:
        raise
    except Exception as e:
        raise ScreenCaptureError(f"Failed to capture screen: {e}")


def capture_input(
    mouse_capturer: Optional[object] = None,
) -> Tuple[List[int], List[int], Optional[np.ndarray]]:
    """
    Capture keyboard, gamepad, and (optionally) mouse input.

    Mouse recording is additive and non-destructive:
    - When *mouse_capturer* is ``None`` the returned mouse vector is ``None``
      and the existing keyboard+gamepad values are unchanged.
    - When a :class:`MouseCapture` instance is provided, its
      ``MOUSE_OUTPUT_SIZE``-element float32 snapshot is appended, with the
      signed fields mapped into ``[0, 1]`` so the BCE loss can represent them.
      ``InferenceEngine.execute_mouse`` inverts that mapping at playback time.

    Args:
        mouse_capturer: Optional MouseCapture instance (or None to skip).

    Returns:
        Tuple of (keyboard_output, gamepad_output, mouse_output_or_none)

    Raises:
        InputCaptureError: If input capture fails
    """
    try:
        # Capture keyboard
        keys = key_check() if key_check else []
        keyboard_output = keys_to_output(keys)

        # Capture gamepad (with fallback for missing gamepad)
        try:
            gamepad_keys = gamepad_check() if gamepad_check else []
            gamepad_output = (
                gamepad_keys_to_output(gamepad_keys) if gamepad_keys else []
            )
        except Exception:
            # Gamepad not available - use empty output
            gamepad_output = []

        # Capture mouse (additive – only when explicitly enabled)
        mouse_output = None
        if mouse_capturer is not None:
            try:
                state = mouse_capturer.snapshot()
                # Signed fields are mapped into [0, 1] here so the BCE loss
                # can actually represent them; execute_mouse inverts this
                # at playback time.
                mouse_output = np.asarray(
                    _NORMALIZE_MOUSE(state.to_array()),
                    dtype=np.float32,
                )
            except Exception as exc:
                # Mouse capture failure must never break recording -- but it
                # must not be silent either. A dropped block is
                # indistinguishable from a bot that simply has no mouse, and
                # the dataset looks fine until training collapses.
                mouse_output = None
                logger.warning(f"Mouse capture failed, recording without it: {exc}")

        return keyboard_output, gamepad_output, mouse_output

    except Exception as e:
        raise InputCaptureError(f"Failed to capture input: {e}")


def save_training_data(data: List, path: Path) -> bool:
    """
    Save training data to file with safety checks.

    Args:
        data: Training data to save
        path: Output file path

    Returns:
        True if save successful
    """
    try:
        # Create backup if file exists
        if path.exists():
            backup_path = path.with_suffix(".npy.bak")
            path.rename(backup_path)
            logger.info(f"Created backup: {backup_path}")

        # Save data – training samples are [screen_array, label_array] pairs
        # with different shapes, so we must use dtype=object + allow_pickle.
        arr = np.array(data, dtype=object)
        np.save(path, arr, allow_pickle=True)
        logger.info(f"Saved {len(data)} frames to {path}")

        # Verify save
        if not path.exists():
            raise IOError("Save verification failed - file not created")

        return True

    except Exception as e:
        logger.error(f"Failed to save training data: {e}")
        return False


def show_preview(screen: np.ndarray, window_name: str = "Recorder Preview") -> bool:
    """
    Show preview window if display is available.

    Args:
        screen: Screen image to display
        window_name: Window title

    Returns:
        False if user pressed 'q' to quit, True otherwise
    """
    try:
        preview = cv2.resize(screen, (640, 360))
        cv2.imshow(window_name, preview)

        if cv2.waitKey(25) & 0xFF == ord("q"):
            return False
        return True

    except Exception:
        # Display not available (headless mode)
        return True


def cleanup():
    """Clean up resources."""
    try:
        cv2.destroyAllWindows()
    except Exception:
        pass


def main(argv: Optional[List[str]] = None) -> int:
    """
    Main data collection function.

    Args:
        argv: Command line arguments

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parser = argparse.ArgumentParser(
        description="BOT MMORPG - Data Collection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Controls:
  T     - Toggle pause/resume
  Q     - Quit (in preview window)

Example:
  python collect_data.py --out data/my_session
        """,
    )
    parser.add_argument(
        "--out", default="data/raw", help="Output folder for training data"
    )
    parser.add_argument(
        "--region",
        default=None,
        help="Screen capture region (x1,y1,x2,y2). Auto-detected when --game is used.",
    )
    parser.add_argument(
        "--game",
        default=None,
        help=(
            "Game profile ID (e.g., dragon_ball_online). "
            "Auto-detects window region and sets output folder. "
            "Use with --task to select a specific task config."
        ),
    )
    parser.add_argument(
        "--task",
        default="farming",
        help="Task type from game profile (default: farming). Used with --game.",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=500,
        help="Frames per chunk file (default: 500)",
    )
    parser.add_argument(
        "--no-preview", action="store_true", help="Disable preview window"
    )
    parser.add_argument(
        "--mouse",
        action="store_true",
        help="Enable mouse recording (additive – appends 6 values to action vector)",
    )
    args = parser.parse_args(argv)

    # Environment variable fallback for --mouse (used by Tauri/launcher UI)
    if not args.mouse:
        import os

        env_mouse = os.environ.get("BOTMMO_CAPTURE_MOUSE", "").lower()
        if env_mouse == "true":
            args.mouse = True

    # --- Game profile integration ---
    game_profile = None
    if args.game:
        try:
            from ..config.profile_loader import GameProfileLoader
        except ImportError:
            try:
                import sys

                sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
                from bot_mmorpg.config.profile_loader import GameProfileLoader
            except ImportError:
                logger.warning(
                    "Could not load profile_loader; --game flag ignored. "
                    "Falling back to manual --region."
                )
                GameProfileLoader = None

        if GameProfileLoader is not None:
            try:
                loader = GameProfileLoader()
                game_profile = loader.load(args.game)
                validate_profile(game_profile)
                logger.info(f"Loaded game profile: {game_profile.name}")

                # Auto-configure output directory
                if args.out == "data/raw":
                    import datetime

                    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    args.out = f"datasets/{args.game}/{ts}_{args.task}"
                    logger.info(f"Output directory set to: {args.out}")

                # Log task config if available
                task_cfg = game_profile.get_task_config(args.task)
                if task_cfg:
                    logger.info(
                        f"Task '{args.task}': {task_cfg.description} "
                        f"(fps_target={task_cfg.fps_target})"
                    )

                # A profile that needs the mouse gets it. Without these
                # values the recorded vector is narrower than the one
                # the profile (and therefore the model) describes.
                if game_profile.requires_mouse and not args.mouse:
                    args.mouse = True
                    logger.info(
                        "Game profile requires mouse: recording enabled "
                        f"automatically (+{MOUSE_OUTPUT_SIZE} values)."
                    )
            except FileNotFoundError:
                logger.error(f"Game profile '{args.game}' not found.")
                logger.error(
                    "Available profiles are listed in game_profiles/index.yaml"
                )
                return 1
            except DataCollectionError as e:
                logger.error(f"Game profile '{args.game}' is inconsistent: {e}")
                return 1

    # --- Auto-detect game window region ---
    if args.region is None and args.game:
        try:
            from .grabscreen import find_game_window
        except ImportError:
            try:
                from grabscreen import find_game_window
            except ImportError:
                find_game_window = None

        if find_game_window is not None:
            detected = find_game_window(args.game)
            if detected is not None:
                args.region = ",".join(str(v) for v in detected)
                logger.info(f"Auto-detected game window region: {args.region}")
            else:
                # Fallback to game profile typical resolution
                if game_profile is not None:
                    w, h = game_profile.typical_resolution
                    args.region = f"0,0,{w},{h}"
                    logger.warning(
                        f"Game window not found. Using profile resolution: {args.region}. "
                        "Position your game window at the top-left corner of your screen, "
                        "or specify --region manually."
                    )
                else:
                    args.region = "0,0,1280,720"
                    logger.warning(
                        "Game window not found. Using default 1280x720. "
                        "Specify --region manually for best results."
                    )

    # Frame size: the game profile picks it, the pipeline has a veto.
    target_size = resolve_target_size(game_profile)
    logger.info(f"Frame size: {target_size[0]}x{target_size[1]}")
    logger.info(f"Action vector: {describe_action_space()}")

    # Final fallback for region
    if args.region is None:
        args.region = "0,40,1920,1120"

    # Parse region
    try:
        region = tuple(map(int, args.region.split(",")))
        if len(region) != 4:
            raise ValueError("Region must have 4 values")
    except ValueError as e:
        logger.error(f"Invalid region format: {e}")
        logger.error("Use format: x1,y1,x2,y2 (e.g., 0,40,1920,1120)")
        return 1

    # Validate dependencies
    try:
        validate_dependencies()
    except DataCollectionError as e:
        logger.error(str(e))
        return 1

    # Setup output directory
    out_dir = Path(args.out)
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory: {out_dir.resolve()}")
    except Exception as e:
        logger.error(f"Cannot create output directory: {e}")
        return 1

    # Find starting file index
    starting_value = 1
    while True:
        file_name = out_dir / f"training_data-{starting_value}.npy"
        if file_name.exists():
            starting_value += 1
        else:
            logger.info(f"Starting with file index: {starting_value}")
            break

    training_data = []
    paused = False
    frame_count = 0
    error_count = 0
    max_consecutive_errors = 10

    # --- Optional mouse capture (additive, non-destructive) ---
    mouse_capturer = None
    if args.mouse:
        if MouseCapture is None:
            logger.warning(
                "Mouse recording requested but pynput is not installed. "
                "Continuing without mouse. Install with: pip install pynput"
            )
        else:
            mouse_capturer = MouseCapture(capture_region=region)
            mouse_capturer.start()
            logger.info(
                f"Mouse recording ENABLED (adds {MOUSE_OUTPUT_SIZE} values: "
                f"{', '.join(f.name for f in MOUSE_FIELDS)})"
            )

    # Countdown
    logger.info("Starting in...")
    for i in range(3, 0, -1):
        logger.info(f"  {i}...")
        time.sleep(1)

    logger.info("RECORDING STARTED! Press 'T' to pause, 'Q' to quit.")

    try:
        while True:
            if not paused:
                try:
                    # Capture screen
                    screen = capture_screen(region=region, target_size=target_size)

                    # Capture input (mouse is additive / non-destructive)
                    keyboard_output, gamepad_output, mouse_output = capture_input(
                        mouse_capturer=mouse_capturer
                    )

                    # Combine inputs – mouse appended only when enabled
                    parts = [np.array(keyboard_output)]
                    if gamepad_output:
                        parts.append(np.array(gamepad_output))
                    if mouse_output is not None:
                        parts.append(mouse_output)
                    final_output = np.concatenate(parts, axis=None)

                    training_data.append([screen, final_output])
                    frame_count += 1
                    error_count = 0  # Reset on success

                    # Show preview
                    if not args.no_preview:
                        if not show_preview(screen):
                            logger.info("User requested quit via preview window")
                            break

                    # Progress logging
                    if frame_count % 100 == 0:
                        logger.info(
                            f"Captured {frame_count} frames (buffer: {len(training_data)})"
                        )

                    # Save chunks
                    if len(training_data) >= args.chunk_size:
                        save_path = out_dir / f"training_data-{starting_value}.npy"
                        if save_training_data(training_data, save_path):
                            training_data = []
                            starting_value += 1
                        else:
                            logger.warning("Save failed, will retry on next chunk")

                except ScreenCaptureError as e:
                    error_count += 1
                    logger.warning(f"Screen capture error ({error_count}): {e}")

                except InputCaptureError as e:
                    error_count += 1
                    logger.warning(f"Input capture error ({error_count}): {e}")

                # Check for too many consecutive errors
                if error_count >= max_consecutive_errors:
                    logger.error(
                        f"Too many consecutive errors ({max_consecutive_errors}). Stopping."
                    )
                    break

            # Check for pause/quit
            try:
                keys = key_check() if key_check else []

                if "T" in keys:
                    paused = not paused
                    status = "PAUSED" if paused else "RESUMED"
                    logger.info(f"Recording {status}")
                    time.sleep(0.5)  # Debounce

                if "Q" in keys:
                    logger.info("User requested quit")
                    break

            except Exception:
                pass  # Ignore key check errors during pause check

            # Small delay to prevent CPU overload when paused
            if paused:
                time.sleep(0.1)

    except KeyboardInterrupt:
        logger.info("Interrupted by user (Ctrl+C)")

    finally:
        # Save any remaining data
        if training_data:
            logger.info(f"Saving remaining {len(training_data)} frames...")
            save_path = out_dir / f"training_data-{starting_value}.npy"
            save_training_data(training_data, save_path)

        # Stop mouse capture if it was started
        if mouse_capturer is not None:
            mouse_capturer.stop()
            logger.info("Mouse capture stopped.")

        cleanup()
        logger.info(f"Data collection complete. Total frames: {frame_count}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
