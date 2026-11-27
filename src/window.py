from dataclasses import dataclass
import sys
import time

IS_WINDOWS = sys.platform == "win32"
if IS_WINDOWS:
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
        x = self.left + int(round(norm_x * self.width))
        y = self.top + int(round(norm_y * self.height))
        return x, y

    def screen_to_norm(self, screen_x: int, screen_y: int) -> tuple[float, float]:
        if self.width <= 0 or self.height <= 0:
            return 0.0, 0.0
        nx = (screen_x - self.left) / self.width
        ny = (screen_y - self.top) / self.height
        return round(nx, 4), round(ny, 4)


class WindowManager:
    def __init__(
        self,
        title_substring: str,
        dry_run: bool = not IS_WINDOWS,
        mock_size: tuple[int, int] = (1920, 1080),
    ) -> None:
        self.title_substring = title_substring.lower()
        self.dry_run = dry_run or not IS_WINDOWS
        self.mock_size = mock_size
        self.hwnd: int | None = None

    def find_window(self) -> int | None:
        if self.dry_run:
            self.hwnd = 1
            return self.hwnd

        matches: list[int] = []

        def _enum_cb(hwnd: int, _: object) -> None:
            if not win32gui.IsWindowVisible(hwnd):
                return
            if self.title_substring in win32gui.GetWindowText(hwnd).lower():
                matches.append(hwnd)

        win32gui.EnumWindows(_enum_cb, None)
        self.hwnd = matches[0] if matches else None
        return self.hwnd

    def is_focused(self) -> bool:
        if self.dry_run:
            return True
        return bool(self.hwnd and win32gui.GetForegroundWindow() == self.hwnd)

    def focus(self, wait_seconds: float = 0.25) -> bool:
        if self.dry_run:
            return True

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
                # Fallback if Windows blocks SetForegroundWindow
                win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)
            time.sleep(wait_seconds)

        return self.is_focused()

    def get_rect(self) -> Rect | None:
        if self.dry_run:
            return Rect(0, 0, self.mock_size[0], self.mock_size[1])

        if not self.hwnd or not win32gui.IsWindow(self.hwnd):
            if not self.find_window():
                return None

        assert self.hwnd is not None
        left, top, right, bottom = win32gui.GetWindowRect(self.hwnd)
        return Rect(left=left, top=top, width=right - left, height=bottom - top)
