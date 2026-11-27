"""Starter pixel-based macro loop with F12 emergency stop."""

import time
from pynput import keyboard

from src.input_ctrl import InputController
from src.vision import ScreenVision
from src.window import WindowManager

TARGET_WINDOW = "Notepad"  # Change to "Genshin Impact", "Honkai: Star Rail", etc.
TICK_INTERVAL = 0.25       # Seconds between screen checks


class MacroRunner:
    def __init__(self, target_window: str) -> None:
        self.wm = WindowManager(target_window)
        self.vision = ScreenVision()
        self.inputs = InputController()
        self.running = True

    def stop(self) -> None:
        self.running = False

    def step(self) -> None:
        """One tick of your macro state machine."""
        if not self.wm.focus():
            print(f"Waiting for window '{self.wm.title_substring}'...")
            time.sleep(1.0)
            return

        rect = self.wm.get_rect()
        if not rect:
            return

        # Example 1: Pixel color check (replace coords/RGB using picker.py)
        # if self.vision.is_pixel_color(rect, norm_x=0.5000, norm_y=0.8000, target_rgb=(255, 215, 0), tolerance=20):
        #     self.inputs.click_norm(rect, 0.5000, 0.8000)
        #     time.sleep(0.5)

        # Example 2: Template image match inside a region
        # match = self.vision.find_template(rect, "assets/claim_btn.png", norm_region=(0.6, 0.7, 1.0, 1.0))
        # if match:
        #     self.inputs.click_norm(rect, match[0], match[1])
        #     time.sleep(0.5)

        # Heartbeat sample at center of window so you can verify capture works
        center_rgb = self.vision.get_pixel_rgb(rect, 0.5, 0.5)
        print(f"Focused | size={rect.width}x{rect.height} | center_rgb={center_rgb}")

    def run(self) -> None:
        print(f"Starting macro for '{self.wm.title_substring}'. Press [F12] to stop.")

        def on_press(key: keyboard.Key | keyboard.KeyCode | None) -> bool | None:
            if key == keyboard.Key.f12:
                print("\n[F12] pressed — stopping macro.")
                self.stop()
                return False
            return None

        listener = keyboard.Listener(on_press=on_press)
        listener.start()

        try:
            while self.running:
                self.step()
                time.sleep(TICK_INTERVAL)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()
            listener.stop()
            print("Macro stopped.")


if __name__ == "__main__":
    MacroRunner(TARGET_WINDOW).run()
