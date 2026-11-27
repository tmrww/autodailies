"""Interactive coordinate and RGB pixel sampler for a target window.

Run on Windows, hover your mouse over a UI element in the target window,
and press F8 to print its normalized (x, y) coordinates and RGB color.
Press Esc to exit.
"""

from pynput import keyboard, mouse

from src.vision import ScreenVision
from src.window import WindowManager

TARGET_WINDOW = "Notepad"  # Change to "Genshin Impact", "Honkai: Star Rail", etc.


def main() -> None:
    wm = WindowManager(TARGET_WINDOW)
    if not wm.find_window():
        print(f"Could not find a visible window matching '{TARGET_WINDOW}'.")
        return

    vision = ScreenVision()
    mouse_ctrl = mouse.Controller()
    print(f"Attached to '{TARGET_WINDOW}'.")
    print("Hover over a point and press [F8] to sample, or [Esc] to quit.\n")

    def on_press(key: keyboard.Key | keyboard.KeyCode | None) -> bool | None:
        if key == keyboard.Key.esc:
            print("Exiting picker.")
            return False

        if key == keyboard.Key.f8:
            rect = wm.get_rect()
            if not rect:
                print("Window lost.")
                return None

            sx, sy = mouse_ctrl.position
            nx, ny = rect.screen_to_norm(int(sx), int(sy))
            rgb = vision.get_pixel_rgb(rect, nx, ny)
            print(f"norm=({nx:.4f}, {ny:.4f})  screen=({int(sx)}, {int(sy)})  rgb={rgb}")
        return None

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


if __name__ == "__main__":
    main()
