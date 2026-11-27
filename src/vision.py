import cv2
import mss
import numpy as np

from src.window import Rect


class ScreenVision:
    def __init__(self, image_path: str | None = None) -> None:
        self._sct: mss.mss | None = None
        self._static_frame: np.ndarray | None = None
        if image_path is not None:
            self.load_image(image_path)

    def load_image(self, image_path: str) -> None:
        """Load a static BGR screenshot for offline testing instead of live capture."""
        frame = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if frame is None:
            raise FileNotFoundError(f"Image not found: {image_path}")
        self._static_frame = frame

    def clear_image(self) -> None:
        self._static_frame = None

    def _get_sct(self) -> mss.mss:
        if self._sct is None:
            self._sct = mss.mss()
        return self._sct

    def grab_region(
        self,
        rect: Rect,
        norm_region: tuple[float, float, float, float] = (0.0, 0.0, 1.0, 1.0),
    ) -> np.ndarray:
        x1, y1 = rect.norm_to_screen(norm_region[0], norm_region[1])
        x2, y2 = rect.norm_to_screen(norm_region[2], norm_region[3])

        if self._static_frame is not None:
            h, w = self._static_frame.shape[:2]
            cx1, cy1 = max(0, min(w - 1, x1)), max(0, min(h - 1, y1))
            cx2, cy2 = max(cx1 + 1, min(w, x2)), max(cy1 + 1, min(h, y2))
            return self._static_frame[cy1:cy2, cx1:cx2]

        monitor = {
            "left": x1,
            "top": y1,
            "width": max(1, x2 - x1),
            "height": max(1, y2 - y1),
        }
        raw = np.array(self._get_sct().grab(monitor))
        return raw[:, :, :3]

    def get_pixel_rgb(self, rect: Rect, norm_x: float, norm_y: float) -> tuple[int, int, int]:
        sx, sy = rect.norm_to_screen(norm_x, norm_y)

        if self._static_frame is not None:
            h, w = self._static_frame.shape[:2]
            cx = max(0, min(w - 1, sx))
            cy = max(0, min(h - 1, sy))
            b, g, r = self._static_frame[cy, cx]
            return int(r), int(g), int(b)

        raw = np.array(self._get_sct().grab({"left": sx, "top": sy, "width": 1, "height": 1}))
        b, g, r = raw[0, 0, :3]
        return int(r), int(g), int(b)

    def is_pixel_color(
        self,
        rect: Rect,
        norm_x: float,
        norm_y: float,
        target_rgb: tuple[int, int, int],
        tolerance: int = 15,
    ) -> bool:
        r, g, b = self.get_pixel_rgb(rect, norm_x, norm_y)
        tr, tg, tb = target_rgb
        return (
            abs(r - tr) <= tolerance
            and abs(g - tg) <= tolerance
            and abs(b - tb) <= tolerance
        )

    def find_template(
        self,
        rect: Rect,
        template_path: str,
        norm_region: tuple[float, float, float, float] = (0.0, 0.0, 1.0, 1.0),
        threshold: float = 0.85,
    ) -> tuple[float, float] | None:
        template = cv2.imread(template_path, cv2.IMREAD_COLOR)
        if template is None:
            raise FileNotFoundError(f"Template not found: {template_path}")

        haystack = self.grab_region(rect, norm_region)
        if haystack.shape[0] < template.shape[0] or haystack.shape[1] < template.shape[1]:
            return None

        result = cv2.matchTemplate(haystack, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        if max_val < threshold:
            return None

        th, tw = template.shape[:2]
        region_x1, region_y1 = rect.norm_to_screen(norm_region[0], norm_region[1])
        center_screen_x = region_x1 + max_loc[0] + tw // 2
        center_screen_y = region_y1 + max_loc[1] + th // 2
        return rect.screen_to_norm(center_screen_x, center_screen_y)
