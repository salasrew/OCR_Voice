from __future__ import annotations

import threading
from collections.abc import Callable
from typing import Any


TRAY_MENU_LABELS = ["Show", "Help", "Test Voice", "Exit"]


def tray_menu_labels() -> list[str]:
    return list(TRAY_MENU_LABELS)


def create_tray_image() -> Any:
    from PIL import Image, ImageDraw

    image = Image.new("RGB", (64, 64), "#0B5CAD")
    draw = ImageDraw.Draw(image)
    draw.rectangle((8, 8, 56, 56), outline="white", width=4)
    draw.text((16, 22), "OCR", fill="white")
    return image


class TrayApp:
    def __init__(
        self,
        *,
        on_show: Callable[[], None],
        on_help: Callable[[], None],
        on_test_voice: Callable[[], None],
        on_exit: Callable[[], None],
    ) -> None:
        self._on_show = on_show
        self._on_help = on_help
        self._on_test_voice = on_test_voice
        self._on_exit = on_exit
        self._icon: Any | None = None
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread is not None:
            return
        try:
            import pystray
        except ImportError as error:
            raise RuntimeError("System tray support requires pystray: pip install pystray") from error

        self._icon = pystray.Icon(
            "OCRVoice",
            create_tray_image(),
            "OCR Voice",
            pystray.Menu(
                pystray.MenuItem(TRAY_MENU_LABELS[0], lambda icon, item: self._on_show()),
                pystray.MenuItem(TRAY_MENU_LABELS[1], lambda icon, item: self._on_help()),
                pystray.MenuItem(TRAY_MENU_LABELS[2], lambda icon, item: self._on_test_voice()),
                pystray.MenuItem(TRAY_MENU_LABELS[3], lambda icon, item: self._exit()),
            ),
        )
        self._thread = threading.Thread(target=self._icon.run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if self._icon is not None:
            self._icon.stop()
            self._icon = None

    def _exit(self) -> None:
        self.stop()
        self._on_exit()
