import os
import sys
import time
import signal
import argparse
from pathlib import Path

import cv2
import numpy as np

from grabscreen import grab_screen
from getkeys import key_check
from getgamepad import gamepad_check

# Optional mouse capture (issues #21, #33, #36)
# Enable via: set BOTMMO_CAPTURE_MOUSE=true (Windows) or --mouse flag
try:
    # Try importing from the modern package first
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
    from bot_mmorpg.scripts.mouse_capture import MouseCapture

    _MOUSE_AVAILABLE = True
except ImportError:
    _MOUSE_AVAILABLE = False
    MouseCapture = None


# ============================================================
# Configuration (can be overridden by launcher env vars)
# ============================================================
# Region: left, top, right, bottom
DEFAULT_CAPTURE_REGION = (0, 40, 1920, 1120)

# Model input resolution (width, height)
DEFAULT_RESOLUTION = (480, 270)

# Preview window resolution (width, height)
DEFAULT_PREVIEW_RESOLUTION = (640, 360)

DEFAULT_OUTPUT_DIR = Path("datasets")  # relative to cwd (versions/0.01)
DEFAULT_FILE_PREFIX = "preprocessed_training_data"

DEFAULT_SAVE_EVERY = 500
DEFAULT_PRINT_EVERY = 100
DEFAULT_TARGET_FPS = 30

PAUSE_TOGGLE_KEY = "T"
QUIT_KEY = ord("q")
WINDOW_NAME = "window"


def _parse_resolution(res: str, fallback=(480, 270)):
    """
    Parse "480x270" into (480, 270).
    """
    try:
        if not res:
            return fallback
        s = str(res).lower().strip()
        if "x" not in s:
            return fallback
        w, h = s.split("x", 1)
        w, h = int(w.strip()), int(h.strip())
        if w <= 0 or h <= 0:
            return fallback
        return (w, h)
    except Exception:
        return fallback


def _parse_region(region: str, fallback=DEFAULT_CAPTURE_REGION):
    """
    Parse "left,top,right,bottom" into tuple[int,int,int,int].
    """
    try:
        if not region:
            return fallback
        parts = [p.strip() for p in str(region).split(",")]
        if len(parts) != 4:
            return fallback
        left, top, right, bottom = map(int, parts)
        if right <= left or bottom <= top:
            return fallback
        return (left, top, right, bottom)
    except Exception:
        return fallback


# Read overrides from environment (launcher can set these)
CAPTURE_REGION = _parse_region(os.getenv("BOTMMO_CAPTURE_REGION"), DEFAULT_CAPTURE_REGION)
RESOLUTION = _parse_resolution(os.getenv("BOTMMO_RESOLUTION"), DEFAULT_RESOLUTION)
PREVIEW_RESOLUTION = _parse_resolution(os.getenv("BOTMMO_PREVIEW_RESOLUTION"), DEFAULT_PREVIEW_RESOLUTION)

OUTPUT_DIR = Path(os.getenv("BOTMMO_OUTPUT_DIR", str(DEFAULT_OUTPUT_DIR)))
FILE_PREFIX = os.getenv("BOTMMO_FILE_PREFIX", DEFAULT_FILE_PREFIX)

SAVE_EVERY = int(os.getenv("BOTMMO_SAVE_EVERY", str(DEFAULT_SAVE_EVERY)))
PRINT_EVERY = int(os.getenv("BOTMMO_PRINT_EVERY", str(DEFAULT_PRINT_EVERY)))
TARGET_FPS = int(os.getenv("BOTMMO_TARGET_FPS", str(DEFAULT_TARGET_FPS)))

# Optional metadata (launcher passes these; script can ignore safely)
GAME_ID = os.getenv("BOTMMO_GAME_ID", "unknown")
DATASET_NAME = os.getenv("BOTMMO_DATASET_NAME", "Untitled")
MONITOR_ID = os.getenv("BOTMMO_MONITOR_ID", "")


# -------------------------
# Labels (same as original mapping)
# -------------------------
W  = [1, 0, 0, 0, 0, 0, 0, 0, 0]
S  = [0, 1, 0, 0, 0, 0, 0, 0, 0]
A  = [0, 0, 1, 0, 0, 0, 0, 0, 0]
D  = [0, 0, 0, 1, 0, 0, 0, 0, 0]
WA = [0, 0, 0, 0, 1, 0, 0, 0, 0]
WD = [0, 0, 0, 0, 0, 1, 0, 0, 0]
SA = [0, 0, 0, 0, 0, 0, 1, 0, 0]
SD = [0, 0, 0, 0, 0, 0, 0, 1, 0]
NK = [0, 0, 0, 0, 0, 0, 0, 0, 1]


def keys_to_output(keys):
    """
    Convert keys to a one-hot-ish array:
     0  1  2  3  4   5   6   7    8
    [W, S, A, D, WA, WD, SA, SD, NOKEY]
    """
    if "W" in keys and "A" in keys:
        return WA
    if "W" in keys and "D" in keys:
        return WD
    if "S" in keys and "A" in keys:
        return SA
    if "S" in keys and "D" in keys:
        return SD
    if "W" in keys:
        return W
    if "S" in keys:
        return S
    if "A" in keys:
        return A
    if "D" in keys:
        return D
    return NK


EXPECTED_GAMEPAD_LEN = 20  # 2 triggers + 4 axes + 14 buttons


def gamepad_keys_to_output(values):
    """
    Convert gamepad list to ints with fixed-length output.
    Expected order from your getgamepad.py:
    ['LT','RT','Lx','Ly','Rx','Ry','UP','DOWN','LEFT','RIGHT',
     'START','SELECT','L3','R3','LB','RB','A','B','X','Y']

    Returns a list of exactly EXPECTED_GAMEPAD_LEN integers.
    Pads with zeros if gamepad returns fewer values, truncates if more.
    This prevents the inhomogeneous shape ValueError in np.save (issue #15).
    """
    out = [int(v) for v in values]
    # Ensure consistent length to avoid inhomogeneous numpy array shapes
    if len(out) < EXPECTED_GAMEPAD_LEN:
        out.extend([0] * (EXPECTED_GAMEPAD_LEN - len(out)))
    elif len(out) > EXPECTED_GAMEPAD_LEN:
        out = out[:EXPECTED_GAMEPAD_LEN]
    return out


def next_available_file(output_dir: Path, prefix: str) -> tuple[Path, int]:
    """
    Find the next non-existing file name like:
    datasets/preprocessed_training_data-1.npy, -2.npy, ...
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    idx = 1
    while True:
        candidate = output_dir / f"{prefix}-{idx}.npy"
        if not candidate.exists():
            return candidate, idx
        idx += 1


def save_chunk(path: Path, data: list) -> None:
    """
    Save using np.save. Stores python objects; load with allow_pickle=True.
    """
    arr = np.array(data, dtype=object)
    np.save(str(path), arr)
    print(f"[SAVED] {path} ({len(data)} samples)")


def _resolve_output_dir(argv=None) -> Path:
    """Decide where to write the .npy chunks.

    Priority (highest first):
      1. ``--out PATH`` on the command line. The Tauri shell spawns us
         with ``--out <data_root>/datasets/<gid>/<name>`` so the
         recording lands exactly where the Train tab's scanner
         (``modelhub/tauri.py::_scan_datasets_fs``) looks. Before this
         was honored, the flag was silently ignored and recordings
         landed in a bare ``datasets/`` folder that never showed up in
         the UI -- the "dataset not appearing after recording" bug
         (issues #57, #60, #63, #65).
      2. ``BOTMMO_OUTPUT_DIR`` environment variable (legacy launcher).
      3. The default ``datasets/`` relative to the working directory.

    Unknown args are tolerated (parse_known_args) so a future caller can
    pass extra flags without crashing the recorder mid-launch.
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--out", "--output", dest="out", default=None)
    args, _unknown = parser.parse_known_args(argv)
    if args.out:
        return Path(args.out)
    return OUTPUT_DIR


def main(argv=None):
    output_dir = _resolve_output_dir(argv)
    out_path, idx = next_available_file(output_dir, FILE_PREFIX)

    # Mouse recording support (issues #21, #33, #36)
    mouse_enabled = os.getenv("BOTMMO_CAPTURE_MOUSE", "").lower() == "true"

    print("=================================================")
    print("[Collector] 1-collect_data.py")
    print(f"[Collector] Game ID      : {GAME_ID}")
    print(f"[Collector] Dataset Name : {DATASET_NAME}")
    print(f"[Collector] Monitor ID   : {MONITOR_ID}")
    print(f"[Collector] CaptureRegion: {CAPTURE_REGION}")
    print(f"[Collector] Resolution   : {RESOLUTION}")
    print(f"[Collector] Mouse Record : {'ENABLED' if mouse_enabled else 'DISABLED'}")
    print(f"[Collector] Output Dir   : {output_dir.resolve()}")
    print(f"[Collector] Output File  : {out_path.name}")
    print("=================================================")
    if not mouse_enabled:
        print("[Tip] Mouse recording is available! Enable with:")
        print("      set BOTMMO_CAPTURE_MOUSE=true   (Windows cmd)")
        print("      $env:BOTMMO_CAPTURE_MOUSE='true' (PowerShell)")
        print("      export BOTMMO_CAPTURE_MOUSE=true (Linux/macOS)")
        print("      Or use the modern script: python -m bot_mmorpg.scripts.collect_data --mouse")
        print("")
    print("[Tip] Windows users: use 'set' instead of 'export' for env vars (#34)")
    print("[Tip] Custom region: set BOTMMO_CAPTURE_REGION=0,0,1280,720")
    print("")

    training_data = []

    # Initialize mouse capture if enabled (#21, #33, #36)
    mouse_capturer = None
    if mouse_enabled:
        if _MOUSE_AVAILABLE and MouseCapture is not None:
            mouse_capturer = MouseCapture(capture_region=CAPTURE_REGION)
            mouse_capturer.start()
            print("[Mouse] Recording ENABLED (adds 10 values: x, y, dx, dy, vx, vy, lmb, rmb, mmb, scroll)")
        else:
            print("[Mouse] WARNING: Mouse recording requested but pynput is not installed.")
            print("        Install with: pip install pynput")
            print("        Continuing without mouse recording.")

    # Countdown (kept from your original behavior)
    for i in range(4, 0, -1):
        print(i)
        time.sleep(1)

    paused = False
    last_toggle_time = 0.0
    toggle_debounce_s = 0.35

    # Graceful stop support: SIGINT is the POSIX path; the
    # BOTMMO_STOP_FLAG env var (Phase 26) is the cross-platform path
    # used by the launcher's job runner. The launcher writes the flag
    # file when the user clicks Stop, then waits ~8s for us to
    # notice and exit cleanly before falling back to SIGTERM/kill.
    # Both paths converge on `running = False`, which lets the bottom
    # of the loop save the buffered samples and print "[Info] Exited
    # cleanly." -- the same codepath that ran when Q was pressed.
    running = True

    def _handle_sigint(signum, frame):
        nonlocal running
        running = False

    signal.signal(signal.SIGINT, _handle_sigint)

    stop_flag_path = os.environ.get("BOTMMO_STOP_FLAG", "").strip() or None
    if stop_flag_path:
        print(f"[Info] Cooperative stop enabled; flag={stop_flag_path}")

    print("STARTING!!!")

    # FPS limiter
    frame_interval = 1.0 / max(1, TARGET_FPS)
    last_frame_time = 0.0

    try:
        while running:
            now = time.time()

            # Phase 26: cooperative stop check. Poll once per loop
            # iteration -- cheap (one stat() syscall on a tmp path)
            # and tight enough that the user's "Stop" click responds
            # within one frame interval (~50ms at 20fps).
            if stop_flag_path and os.path.exists(stop_flag_path):
                print("[Info] Stop flag detected; exiting cleanly...")
                running = False
                break

            # Pause toggle (debounced)
            keys_now = key_check()
            if PAUSE_TOGGLE_KEY in keys_now and (now - last_toggle_time) > toggle_debounce_s:
                paused = not paused
                last_toggle_time = now
                print("unpaused!" if not paused else "Pausing!")
                time.sleep(0.1)

            if paused:
                time.sleep(0.05)
                continue

            # FPS limiter
            dt = now - last_frame_time
            if dt < frame_interval:
                time.sleep(max(0.0, frame_interval - dt))
            last_frame_time = time.time()

            # Capture
            screen = grab_screen(region=CAPTURE_REGION)

            # Validate capture (fixes #15 - empty/invalid screens cause shape errors)
            if screen is None or screen.size == 0:
                continue

            # Resize for model input (enforces consistent shape)
            screen = cv2.resize(screen, RESOLUTION)

            # BGR -> RGB (kept from original)
            screen = cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)

            # Keys + gamepad
            output_keys = keys_to_output(keys_now)
            try:
                gp_raw = gamepad_check()
            except Exception:
                gp_raw = [0] * EXPECTED_GAMEPAD_LEN
            output_gp = gamepad_keys_to_output(gp_raw)

            # Build action vector: keyboard (9) + gamepad (20) = 29 base
            parts = [np.array(output_keys), np.array(output_gp)]

            # Append mouse state if enabled (adds 10 values, issues #21/#33/#36)
            if mouse_capturer is not None:
                try:
                    mouse_state = mouse_capturer.snapshot()
                    parts.append(mouse_state.to_array())  # float32, shape (10,)
                except Exception:
                    pass  # Mouse failure must never break recording

            output = np.concatenate(parts, axis=None)

            # Append sample (kept exact structure)
            training_data.append([screen, output])

            # Preview (optional quit with 'q' still supported)
            cv2.imshow(WINDOW_NAME, cv2.resize(screen, PREVIEW_RESOLUTION))
            if cv2.waitKey(1) & 0xFF == QUIT_KEY:
                break

            # Progress + save chunks
            if len(training_data) % PRINT_EVERY == 0:
                print(f"[Info] Collected: {len(training_data)} samples")

            if len(training_data) >= SAVE_EVERY:
                save_chunk(out_path, training_data)
                training_data = []
                idx += 1
                out_path = output_dir / f"{FILE_PREFIX}-{idx}.npy"

    finally:
        # Save remainder so stopping from launcher doesn't lose data
        if training_data:
            save_chunk(out_path, training_data)

        # Stop mouse capture if it was started
        if mouse_capturer is not None:
            mouse_capturer.stop()
            print("[Mouse] Capture stopped.")

        cv2.destroyAllWindows()
        print("[Info] Exited cleanly.")


if __name__ == "__main__":
    main()
