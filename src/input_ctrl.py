import random
import sys
import time

from src.window import Rect

IS_WINDOWS = sys.platform == "win32"
if IS_WINDOWS:
    import pydirectinput
    pydirectinput.PAUSE = 0.02


class InputController:
    def __init__(self, dry_run: bool = not IS_WINDOWS) -> None:
        self.dry_run = dry_run or not IS_WINDOWS

    def click_norm(
        self,
        rect: Rect,
        norm_x: float,
        norm_y: float,
        button: str = "left",
        jitter_px: int = 2,
    ) -> None:
        sx, sy = rect.norm_to_screen(norm_x, norm_y)
        if jitter_px > 0:
            sx += random.randint(-jitter_px, jitter_px)
            sy += random.randint(-jitter_px, jitter_px)

        if self.dry_run:
            print(f"[DRY RUN] click ({sx}, {sy}) norm=({norm_x:.4f}, {norm_y:.4f}) button={button}")
            return

        pydirectinput.moveTo(sx, sy)
        time.sleep(0.03)
        pydirectinput.click(button=button)

    def press_key(self, key: str, hold_seconds: float = 0.05) -> None:
        if self.dry_run:
            print(f"[DRY RUN] press '{key}' ({hold_seconds:.2f}s)")
            return

        pydirectinput.keyDown(key)
        time.sleep(hold_seconds)
        pydirectinput.keyUp(key)
