# Done by Frannecklp
# Cross-platform support added for Linux/macOS

import base64
import platform

import cv2
import numpy as np

# Platform detection for cross-platform support
IS_WINDOWS = platform.system() == "Windows"

if IS_WINDOWS:
    try:
        import win32api
        import win32con
        import win32gui
        import win32ui

        _WIN32_AVAILABLE = True
    except ImportError:
        _WIN32_AVAILABLE = False
else:
    _WIN32_AVAILABLE = False

# Cross-platform fallback using mss (works on all platforms)
try:
    import mss

    _MSS_AVAILABLE = True
except ImportError:
    _MSS_AVAILABLE = False


def enable_dpi_awareness():
    """Opt this process into true physical pixels on Windows.

    A process that has not declared DPI awareness gets a *virtualized*
    desktop from Win32: on a 4K monitor at 150% scaling,
    GetSystemMetrics reports 2560x1440 and BitBlt hands back a
    DWM-rescaled, blurry copy of the desktop instead of the real
    3840x2160 pixels. Lowering the display resolution does not help,
    because scaling -- not resolution -- is what triggers the
    virtualization. That is issue #81: "I got a 4K screen but even if I
    lowered my resolution it still won't capture my screen."

    Declares awareness through the newest API the OS offers and falls
    back down the chain (Win10 1703 -> Win8.1 -> Vista). Safe to call
    repeatedly and on non-Windows platforms, where it is a no-op.

    Returns:
        bool: True if the process is DPI-aware after this call.
    """
    if not IS_WINDOWS:
        return False

    import ctypes

    # Win10 1703+: per-monitor v2, the only mode that stays correct when
    # the window is dragged between monitors of differing scale.
    try:
        # DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 == -4
        if ctypes.windll.user32.SetProcessDpiAwarenessContext(-4):
            return True
    except (AttributeError, OSError):
        pass

    # Win8.1+: PROCESS_PER_MONITOR_DPI_AWARE == 2
    try:
        # S_OK (0) or E_ACCESSDENIED (already set by a manifest) both mean
        # the process ends up DPI-aware.
        hresult = ctypes.windll.shcore.SetProcessDpiAwareness(2)
        if hresult in (0, -2147024891):
            return True
    except (AttributeError, OSError):
        pass

    # Vista+: system-DPI aware. Better than nothing on a scaled 4K panel.
    try:
        return bool(ctypes.windll.user32.SetProcessDPIAware())
    except (AttributeError, OSError):
        return False


# Declare awareness at import time, before any capture call reads the
# screen metrics -- Windows latches the process's awareness on first use.
_DPI_AWARE = enable_dpi_awareness()


def list_monitors():
    """
    List all available monitors/screens.

    Returns:
        list: List of monitor dictionaries with id, name, and dimensions.
              Example: [{"id": 0, "name": "Primary (1920x1080)", "width": 1920, "height": 1080, "left": 0, "top": 0}]
    """
    monitors = []

    if _MSS_AVAILABLE:
        with mss.mss() as sct:
            # Skip monitor 0 (it's the combined virtual screen on Windows)
            for i, mon in enumerate(sct.monitors[1:], start=1):
                monitors.append(
                    {
                        "id": i,
                        "name": f"Monitor {i} ({mon['width']}x{mon['height']})",
                        "width": mon["width"],
                        "height": mon["height"],
                        "left": mon["left"],
                        "top": mon["top"],
                    }
                )
    elif IS_WINDOWS and _WIN32_AVAILABLE:
        # Fallback: just report primary monitor
        width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        monitors.append(
            {
                "id": 1,
                "name": f"Primary ({width}x{height})",
                "width": width,
                "height": height,
                "left": 0,
                "top": 0,
            }
        )
    else:
        # Default fallback
        monitors.append(
            {
                "id": 1,
                "name": "Primary (Unknown)",
                "width": 1920,
                "height": 1080,
                "left": 0,
                "top": 0,
            }
        )

    return monitors


def grab_screen_monitor(monitor_id=1):
    """
    Capture a specific monitor by ID.

    Args:
        monitor_id: Monitor ID (1-based, from list_monitors())

    Returns:
        numpy.ndarray: RGB image array of the captured monitor.
    """
    if _MSS_AVAILABLE:
        with mss.mss() as sct:
            if monitor_id < 1 or monitor_id >= len(sct.monitors):
                monitor_id = 1  # Default to primary
            monitor = sct.monitors[monitor_id]
            screenshot = sct.grab(monitor)
            img = np.array(screenshot)
            return cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)

    # Fallback to full screen
    return grab_screen()


def grab_screen_thumbnail(monitor_id=1, max_width=320, max_height=180):
    """
    Capture a monitor and return a thumbnail-sized image.
    Useful for preview displays.

    Args:
        monitor_id: Monitor ID to capture
        max_width: Maximum thumbnail width
        max_height: Maximum thumbnail height

    Returns:
        numpy.ndarray: Resized RGB image array
    """
    img = grab_screen_monitor(monitor_id)
    h, w = img.shape[:2]
    if h == 0 or w == 0:
        raise RuntimeError(f"Captured an empty frame from monitor {monitor_id}.")

    # Calculate scale to fit within max dimensions. Never upscale: a
    # thumbnail of a 4K screen is a downscale, and clamping to >= 1px
    # keeps cv2.resize from rejecting a degenerate size.
    scale = min(max_width / w, max_height / h, 1.0)
    new_w = max(1, int(w * scale))
    new_h = max(1, int(h * scale))

    return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)


def grab_screen_base64(monitor_id=1, max_width=640, max_height=360, quality=70):
    """
    Capture a monitor and return as base64 JPEG string.
    Perfect for sending to web UI.

    Args:
        monitor_id: Monitor ID to capture
        max_width: Maximum image width
        max_height: Maximum image height
        quality: JPEG quality (1-100)

    Returns:
        str: Base64-encoded JPEG image data
    """
    img = grab_screen_thumbnail(monitor_id, max_width, max_height)
    # Convert RGB to BGR for OpenCV encoding
    img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    # Encode as JPEG
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    _, buffer = cv2.imencode(".jpg", img_bgr, encode_param)
    # Convert to base64
    return base64.b64encode(buffer).decode("utf-8")


def _grab_screen_win32(region=None):
    """Windows-specific screen capture using Win32 API (original implementation)."""
    hwin = win32gui.GetDesktopWindow()

    if region:
        left, top, x2, y2 = region
        width = x2 - left + 1
        height = y2 - top + 1
    else:
        width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
        height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
        left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
        top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)

    if width <= 0 or height <= 0:
        raise RuntimeError(
            f"Win32 reported a {width}x{height} capture area; "
            "the screen metrics are unusable."
        )

    hwindc = win32gui.GetWindowDC(hwin)
    srcdc = win32ui.CreateDCFromHandle(hwindc)
    memdc = srcdc.CreateCompatibleDC()
    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(srcdc, width, height)
    memdc.SelectObject(bmp)
    memdc.BitBlt((0, 0), (width, height), srcdc, (left, top), win32con.SRCCOPY)

    signedIntsArray = bmp.GetBitmapBits(True)
    # Fix: Use np.frombuffer instead of deprecated np.fromstring
    img = np.frombuffer(signedIntsArray, dtype="uint8")

    srcdc.DeleteDC()
    memdc.DeleteDC()
    win32gui.ReleaseDC(hwin, hwindc)
    win32gui.DeleteObject(bmp.GetHandle())

    # GDI pads each scanline to a 4-byte boundary and, on some scaled
    # displays, hands back a bitmap slightly wider than requested.
    # Reshaping blindly raised "cannot reshape array of size N" and took
    # the whole recording down (issue #81); derive the real row width
    # from the buffer instead so the capture survives.
    expected = height * width * 4
    if img.size != expected:
        if img.size % (height * 4) != 0:
            raise RuntimeError(
                f"Win32 returned {img.size} bytes for a {width}x{height} "
                "capture; the bitmap layout is unusable."
            )
        actual_width = img.size // (height * 4)
        img = img.reshape(height, actual_width, 4)[:, :width]
    else:
        img = img.reshape(height, width, 4)

    return cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)


def _is_blank(img):
    """True when a frame carries no picture at all (all-black / empty).

    A GDI BitBlt of the desktop DC returns solid black for windows drawn
    through a path it cannot read -- fullscreen-exclusive games and some
    hardware-accelerated compositors. Detecting it lets the caller retry
    through mss, which reads the composited desktop instead.
    """
    if img is None or getattr(img, "size", 0) == 0:
        return True
    return bool(img.max() == 0)


def _grab_screen_mss(region=None):
    """Cross-platform screen capture using mss library."""
    with mss.mss() as sct:
        if region:
            left, top, x2, y2 = region
            monitor = {
                "left": left,
                "top": top,
                "width": x2 - left + 1,
                "height": y2 - top + 1,
            }
        else:
            # Capture full screen (primary monitor)
            monitor = sct.monitors[1]

        screenshot = sct.grab(monitor)
        # Convert to numpy array
        img = np.array(screenshot)
        # mss returns BGRA, convert to RGB
        return cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)


def find_window_region(window_title):
    """
    Find a game window by title and return its screen region.

    Searches for windows whose title contains the given string
    (case-insensitive). Useful for auto-detecting game window position
    instead of requiring manual --region coordinates.

    Args:
        window_title: Partial or full window title to search for.

    Returns:
        tuple: (left, top, right, bottom) pixel coordinates, or None if not found.
    """
    if IS_WINDOWS and _WIN32_AVAILABLE:
        result = []

        def _enum_callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if window_title.lower() in title.lower():
                    rect = win32gui.GetWindowRect(hwnd)
                    # rect is (left, top, right, bottom)
                    result.append(rect)

        win32gui.EnumWindows(_enum_callback, None)
        if result:
            left, top, right, bottom = result[0]
            # Compensate for window borders / title bar (~30px on Windows 10/11)
            return (left, top, right, bottom)
        return None

    # On Linux, attempt wmctrl-style detection via subprocess
    try:
        import subprocess

        output = subprocess.check_output(
            ["wmctrl", "-lG"], stderr=subprocess.DEVNULL, text=True
        )
        for line in output.strip().split("\n"):
            if window_title.lower() in line.lower():
                parts = line.split()
                # wmctrl -lG format: id desktop x y w h hostname title...
                if len(parts) >= 7:
                    x, y, w, h = (
                        int(parts[2]),
                        int(parts[3]),
                        int(parts[4]),
                        int(parts[5]),
                    )
                    return (x, y, x + w, y + h)
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass

    return None


# Common window titles for supported games (used by --game auto-detect)
GAME_WINDOW_TITLES = {
    "dragon_ball_online": [
        "Dragon Ball Online",
        "DragonBall Online",
        "DBO",
        "DBOG",
        "Ultimate DBO",
        "UltimateDBO",
    ],
    "genshin_impact": ["Genshin Impact", "GenshinImpact", "原神"],
    "world_of_warcraft": ["World of Warcraft", "WoW", "Wow-64"],
    "final_fantasy_xiv": ["FINAL FANTASY XIV", "FFXIV"],
    "guild_wars_2": ["Guild Wars 2"],
    "lost_ark": ["LOST ARK", "Lost Ark"],
    "new_world": ["New World"],
}


def find_game_window(game_id):
    """
    Auto-detect a game window region by game profile ID.

    Tries multiple known window titles for the given game.

    Args:
        game_id: Game identifier from game_profiles (e.g., "dragon_ball_online")

    Returns:
        tuple: (left, top, right, bottom) pixel coordinates, or None if not found.
    """
    titles = GAME_WINDOW_TITLES.get(game_id, [])
    for title in titles:
        region = find_window_region(title)
        if region is not None:
            return region
    return None


def grab_screen(region=None):
    """
    Capture a region of the screen.

    Args:
        region: Optional tuple (left, top, right, bottom) defining the capture area.
                If None, captures the entire screen.

    Returns:
        numpy.ndarray: RGB image array of the captured screen region.

    Cross-platform support:
        - Windows: Uses Win32 API (fast, original implementation)
        - Linux/macOS: Uses mss library (requires: pip install mss)
    """
    # Prefer Win32 on Windows for best performance
    if IS_WINDOWS and _WIN32_AVAILABLE:
        try:
            img = _grab_screen_win32(region)
        except Exception:
            # A GDI failure is not fatal while mss can still read the
            # screen; re-raise only when there is no second path.
            if not _MSS_AVAILABLE:
                raise
            img = None
        if img is not None and not _is_blank(img):
            return img
        if not _MSS_AVAILABLE:
            # Nothing to fall back to -- hand back whatever GDI produced
            # rather than raising on a legitimately black screen.
            if img is not None:
                return img
            raise RuntimeError("Win32 screen capture failed and mss is not installed.")
        # Blank GDI frame (fullscreen-exclusive game, protected output):
        # mss reads the composited desktop and usually succeeds.
        return _grab_screen_mss(region)

    # Fallback to mss (cross-platform)
    if _MSS_AVAILABLE:
        return _grab_screen_mss(region)

    # No screen capture available
    raise RuntimeError(
        "No screen capture method available. "
        "On Windows, install pywin32: pip install pywin32. "
        "On Linux/macOS, install mss: pip install mss"
    )
