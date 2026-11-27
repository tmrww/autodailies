import argparse
import sys
import time
from pynput import keyboard

from src.input_ctrl import InputController
from src.vision import ScreenVision
from src.window import WindowManager

TARGET_WINDOW = "Notepad"
TICK_INTERVAL = 0.25


class MacroRunner:
    def __init__(
        self,
        target_window: str,
        dry_run: bool = False,
        image_path: str | None = None,
    ) -> None:
        self.dry_run = dry_run or sys.platform != "win32"
        self.vision = ScreenVision(image_path=image_path)

        mock_size = (1920, 1080)
        if self.vision._static_frame is not None:
            h, w = self.vision._static_frame.shape[:2]
            mock_size = (w, h)

        self.wm = WindowManager(target_window, dry_run=self.dry_run, mock_size=mock_size)
        self.inputs = InputController(dry_run=self.dry_run)
        self.running = True

    def stop(self) -> None:
        self.running = False

    def step(self) -> None:
        if not self.wm.focus():
            print(f"Waiting for window '{self.wm.title_substring}'...")
            time.sleep(1.0)
            return

        rect = self.wm.get_rect()
        if not rect:
            return

        # Add pixel/template rules here, e.g.:
        # if self.vision.is_pixel_color(rect, 0.5, 0.8, (255, 215, 0)):
        #     self.inputs.click_norm(rect, 0.5, 0.8)

        center_rgb = self.vision.get_pixel_rgb(rect, 0.5, 0.5)
        mode = "DRY RUN" if self.dry_run else "LIVE"
        print(f"[{mode}] size={rect.width}x{rect.height} | center_rgb={center_rgb}")

    def run(self) -> None:
        print(f"Starting macro for '{self.wm.title_substring}' (dry_run={self.dry_run}). Press [F12] to stop.")

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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Log inputs instead of sending them")
    parser.add_argument("--image", type=str, default=None, help="Test against a static screenshot file")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    MacroRunner(TARGET_WINDOW, dry_run=args.dry_run, image_path=args.image).run()
