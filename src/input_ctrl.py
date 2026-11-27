"""Mouse and keyboard input helpers using pydirectinput."""

import random
import time
import pydirectinput

from src.window import Rect

pydirectinput.PAUSE = 0.02


class InputController:
    """Sends mouse clicks and key presses to the active window."""

    @staticmethod
    def click_norm(
        rect: Rect,
        norm_x: float,
        norm_y: float,
        button: str = "left",
        jitter_px: int = 2,
    ) -> None:
        """Move to normalized coordinates (with tiny optional jitter) and click."""
        sx, sy = rect.norm_to_screen(norm_x, norm_y)
        if jitter_px > 0:
            sx += random.randint(-jitter_px, jitter_px)
            sy += random.randint(-jitter_px, jitter_px)

        pydirectinput.moveTo(sx, sy)
        time.sleep(0.03)
        pydirectinput.click(button=button)

    @staticmethod
    def press_key(key: str, hold_seconds: float = 0.05) -> None:
        """Press and release a key."""
        pydirectinput.keyDown(key)
        time.sleep(hold_seconds)
        pydirectinput.keyUp(key)
