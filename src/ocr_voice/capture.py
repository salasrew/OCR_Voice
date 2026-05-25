from __future__ import annotations

from pathlib import Path
from time import time_ns

from .geometry import Rect


class MssCaptureService:
    def __init__(self, capture_dir: str | Path) -> None:
        self._capture_dir = Path(capture_dir)
        self._capture_dir.mkdir(parents=True, exist_ok=True)

    def capture(self, rect: Rect) -> str:
        try:
            import mss
            from PIL import Image
        except ImportError as error:
            raise RuntimeError(
                "Screen capture requires optional packages: pip install mss pillow"
            ) from error

        output_path = self._capture_dir / f"capture-{time_ns()}.png"
        with mss.mss() as screen:
            raw = screen.grab(rect.as_mss)
            image = Image.frombytes("RGB", raw.size, raw.rgb)
            image.save(output_path)
        return str(output_path)
