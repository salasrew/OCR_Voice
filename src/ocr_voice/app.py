from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Callable

from .capture import MssCaptureService
from .config import AppConfig, load_config
from .controller import OcrVoiceController
from .gui import StatusGui
from .ocr import AutoOcrService
from .tts import TtsService


def build_controller(config: AppConfig, *, logger=print, overlay=None) -> OcrVoiceController:
    capture = MssCaptureService(config.capture_dir)
    ocr = AutoOcrService(config.ocr_command)
    tts = TtsService(config.tts_command)
    return OcrVoiceController(config, capture, ocr, tts, logger=logger, overlay=overlay)


def run(config_path: str | Path | None = "config.json") -> None:
    config = load_config(config_path)
    if config.use_gui:
        gui = StatusGui(config)
        controller = build_controller(config, logger=gui.logger)
        gui.run_listener(lambda: start_hotkey_listener(config, lambda: gui.start_selection(controller.process_selection)))
        gui.mainloop()
        return

    controller = build_controller(config)
    start_mouse_listener(controller, config)


def build_hotkey_bindings(config: AppConfig, on_activate: Callable[[], None]) -> dict[str, Callable[[], None]]:
    return {config.hotkey: on_activate}


def start_hotkey_listener(config: AppConfig, on_activate: Callable[[], None]) -> None:
    try:
        from pynput import keyboard
    except ImportError as error:
        raise RuntimeError("Hotkey listener requires pynput: pip install pynput") from error

    print(f"OCR Voice running. Press {config.hotkey} to select text.")
    with keyboard.GlobalHotKeys(build_hotkey_bindings(config, on_activate)) as listener:
        listener.join()


def start_mouse_listener(controller: OcrVoiceController, config: AppConfig) -> None:
    try:
        from pynput import mouse
    except ImportError as error:
        raise RuntimeError("Mouse listener requires pynput: pip install pynput") from error

    pressed = False

    def on_click(x: int, y: int, button: Any, is_pressed: bool) -> None:
        nonlocal pressed
        if button != mouse.Button.right:
            return

        if is_pressed:
            pressed = True
            controller.on_right_click_pressed(x, y)
            return

        if pressed:
            pressed = False
            controller.on_right_click_released(x, y)

    def on_move(x: int, y: int) -> None:
        if pressed:
            controller.on_mouse_moved(x, y)

    def on_scroll(x: int, y: int, dx: int, dy: int) -> None:
        if pressed:
            controller.on_scroll(x, y, dy)

    print(
        f"OCR Voice running: mode={config.mode}, box={config.box_width}x{config.box_height}. "
        "Press Ctrl+C to quit."
    )
    with mouse.Listener(on_click=on_click, on_move=on_move, on_scroll=on_scroll) as listener:
        listener.join()


def main() -> None:
    parser = argparse.ArgumentParser(description="Hotkey Japanese OCR voice prototype.")
    parser.add_argument(
        "--config",
        default="config.json",
        help="Path to config JSON. Missing file uses defaults.",
    )
    args = parser.parse_args()
    run(args.config)


if __name__ == "__main__":
    main()
