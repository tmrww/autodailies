"""Windows window discovery, focusing, and coordinate normalization."""

from dataclasses import dataclass
import time
import win32con
import win32gui


@dataclass(frozen=True)
class Rect:
    left: int
    top: int
    width: int
    height: int

    @property
    def right(self) -> int:
        return self.left + self.width

    @property
    def bottom(self) -> int:
        return self.top + self.height

    def norm_to_screen(self, norm_x: float, norm_y: float) -> tuple[int, int]:
        """Convert normalized (0.0-1.0) window coordinates to absolute screen pixels."""
        x = self.left + int(round(norm_x * self.width))
        y = self.top + int(round(norm_y * self.height))
        return x, y

    def screen_to_norm(self, screen_x: int, screen_y: int) -> tuple[float, float]:
        """Convert absolute screen pixels to normalized (0.0-1.0) window coordinates."""
        if self.width <= 0 or self.height <= 0:
            return 0.0, 0.0
        nx = (screen_x - self.left) / self.width
        ny = (screen_y - self.top) / self.height
        return round(nx, 4), round(ny, 4)


class WindowManager:
    """Finds, focuses, and tracks a target Windows application window."""

    def __init__(self, title_substring: str) -> None:
        self.title_substring = title_substring.lower()
        self.hwnd: int | None = None

    def find_window(self) -> int | None:
        """Locate the first visible window whose title contains title_substring."""
        matches: list[int] = []

        def _enum_cb(hwnd: int, _: object) -> None:
            if not win32gui.IsWindowVisible(hwnd):
                return
            title = win32gui.GetWindowText(hwnd)
            if self.title_substring in title.lower():
                matches.append(hwnd)

        win32gui.EnumWindows(_enum_cb, None)
        self.hwnd = matches[0] if matches else None
        return self.hwnd

    def is_focused(self) -> bool:
        if not self.hwnd:
            return False
        return win32gui.GetForegroundWindow() == self.hwnd

    def focus(self, wait_seconds: float = 0.25) -> bool:
        """Restore if minimized and bring the target window to the foreground."""
        if not self.hwnd or not win32gui.IsWindow(self.hwnd):
            if not self.find_window():
                return False

        assert self.hwnd is not None
        if win32gui.IsIconic(self.hwnd):
            win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)

        if not self.is_focused():
            try:
                win32gui.SetForegroundWindow(self.hwnd)
            except Exception:
                # Fallback: toggle topmost briefly if Windows blocks SetForegroundWindow
                win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)
            time.sleep(wait_seconds)

        return self.is_focused()

    def get_rect(self) -> Rect | None:
        """Return the window's bounding rectangle in screen coordinates."""
        if not self.hwnd or not win32gui.IsWindow(self.hwnd):
            if not self.find_window():
                return None

        assert self.hwnd is not None
        left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)
        return Rect(left=left, top=top, width=right - left, height=bottom - top)
