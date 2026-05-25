from __future__ import annotations

from dataclasses import dataclass, fields
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class AppConfig:
    mode: int = 0
    box_width: int = 500
    box_height: int = 500
    duplicate_window_seconds: float = 3.0
    ocr_command: list[str] | None = None
    tts_command: list[str] | None = None
    capture_dir: str = ".ocr_voice_captures"
    hotkey: str = "<ctrl>+<shift>+o"
    min_selection_width: int = 8
    min_selection_height: int = 8
    right_click_button: str = "right"
    fallback_hotkey: str = "<ctrl>+<space>"
    show_overlay: bool = True
    overlay_opacity: float = 0.45
    border_color: str = "#00D1FF"
    use_gui: bool = True

    def __post_init__(self) -> None:
        if self.mode not in (0, 1):
            raise ValueError("mode must be 0 or 1")
        if self.box_width <= 0 or self.box_height <= 0:
            raise ValueError("box_width and box_height must be positive")
        if self.min_selection_width <= 0 or self.min_selection_height <= 0:
            raise ValueError("minimum selection size must be positive")
        if self.duplicate_window_seconds < 0:
            raise ValueError("duplicate_window_seconds must be non-negative")
        if not 0.0 <= self.overlay_opacity <= 1.0:
            raise ValueError("overlay_opacity must be between 0.0 and 1.0")


def load_config(path: str | Path | None = None) -> AppConfig:
    if path is None:
        return AppConfig()

    config_path = Path(path)
    if not config_path.exists():
        return AppConfig()

    with config_path.open("r", encoding="utf-8") as file:
        raw = json.load(file)

    if not isinstance(raw, dict):
        raise ValueError("config file must contain a JSON object")

    valid_names = {field.name for field in fields(AppConfig)}
    overrides: dict[str, Any] = {key: value for key, value in raw.items() if key in valid_names}
    return AppConfig(**overrides)
