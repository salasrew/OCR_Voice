from __future__ import annotations

from pathlib import Path
import time
from typing import Protocol

from .config import AppConfig
from .geometry import Rect, centered_rect


class CaptureService(Protocol):
    def capture(self, rect: Rect) -> str:
        raise NotImplementedError


class OcrService(Protocol):
    def recognize(self, image_path: str) -> str:
        raise NotImplementedError


class TtsService(Protocol):
    def speak(self, text: str) -> None:
        raise NotImplementedError


class OverlayService(Protocol):
    def show(self, rect: Rect) -> None:
        raise NotImplementedError

    def update(self, rect: Rect) -> None:
        raise NotImplementedError

    def hide(self) -> None:
        raise NotImplementedError


class OcrVoiceController:
    def __init__(
        self,
        config: AppConfig,
        capture: CaptureService,
        ocr: OcrService,
        tts: TtsService,
        *,
        clock=time.monotonic,
        logger=print,
        overlay: OverlayService | None = None,
    ) -> None:
        self._config = config
        self._box_width = config.box_width
        self._box_height = config.box_height
        self._capture = capture
        self._ocr = ocr
        self._tts = tts
        self._clock = clock
        self._logger = logger
        self._overlay = overlay
        self._last_text = ""
        self._last_spoken_at = 0.0
        self._last_cursor: tuple[int, int] | None = None
        self.preview_rect: Rect | None = None

    def on_right_click_pressed(self, cursor_x: int, cursor_y: int) -> None:
        self._last_cursor = (cursor_x, cursor_y)
        rect = self._rect_for_cursor(cursor_x, cursor_y)
        if self._config.mode == 0:
            self._capture_and_speak(rect)
            return

        self.preview_rect = rect
        if self._config.show_overlay and self._overlay is not None:
            self._overlay.show(rect)

    def on_mouse_moved(self, cursor_x: int, cursor_y: int) -> None:
        self._last_cursor = (cursor_x, cursor_y)
        if self._config.mode == 1 and self.preview_rect is not None:
            self.preview_rect = self._rect_for_cursor(cursor_x, cursor_y)
            if self._config.show_overlay and self._overlay is not None:
                self._overlay.update(self.preview_rect)

    def on_right_click_released(self, cursor_x: int, cursor_y: int) -> None:
        self._last_cursor = (cursor_x, cursor_y)
        if self._config.mode != 1:
            return

        rect = self._rect_for_cursor(cursor_x, cursor_y)
        self.preview_rect = None
        if self._config.show_overlay and self._overlay is not None:
            self._overlay.hide()
        self._capture_and_speak(rect)

    def trigger_at(self, cursor_x: int, cursor_y: int) -> None:
        self._capture_and_speak(self._rect_for_cursor(cursor_x, cursor_y))

    def process_selection(self, rect: Rect) -> None:
        if self._is_selection_too_small(rect):
            self._logger("Selection too small.")
            return
        self._capture_and_speak(rect, report_empty=True)

    def set_box_size(self, width: int, height: int) -> None:
        self._box_width = max(50, min(1400, int(width)))
        self._box_height = max(50, min(1400, int(height)))
        if self.preview_rect is not None and self._last_cursor is not None:
            self.preview_rect = self._rect_for_cursor(*self._last_cursor)
            if self._config.show_overlay and self._overlay is not None:
                self._overlay.update(self.preview_rect)

    def on_scroll(self, cursor_x: int, cursor_y: int, delta_y: int) -> None:
        if self._config.mode != 1 or self.preview_rect is None:
            return

        self._last_cursor = (cursor_x, cursor_y)
        step = 40 if delta_y > 0 else -40
        self.set_box_size(self._box_width + step, self._box_height + step)

    def _rect_for_cursor(self, cursor_x: int, cursor_y: int) -> Rect:
        return centered_rect(
            cursor_x,
            cursor_y,
            width=self._box_width,
            height=self._box_height,
        )

    def _is_selection_too_small(self, rect: Rect) -> bool:
        return (
            rect.width < self._config.min_selection_width
            or rect.height < self._config.min_selection_height
        )

    def _capture_and_speak(self, rect: Rect, *, report_empty: bool = False) -> None:
        image_path: str | None = None
        try:
            image_path = self._capture.capture(rect)
            text = normalize_text(self._ocr.recognize(image_path))
        except Exception as error:
            self._logger(f"OCR failed: {error}")
            self._delete_capture(image_path)
            return
        try:
            if not text:
                if report_empty:
                    self._logger("No text recognized.")
                return
            if self._is_duplicate(text):
                return

            self._last_text = text
            self._last_spoken_at = self._clock()
            try:
                self._tts.speak(text)
            except Exception as error:
                self._logger(f"TTS failed: {error}")
        finally:
            self._delete_capture(image_path)

    def _delete_capture(self, image_path: str | None) -> None:
        if image_path is None:
            return
        try:
            Path(image_path).unlink(missing_ok=True)
        except OSError as error:
            self._logger(f"Capture cleanup failed: {error}")

    def _is_duplicate(self, text: str) -> bool:
        if text != self._last_text:
            return False
        elapsed = self._clock() - self._last_spoken_at
        return elapsed < self._config.duplicate_window_seconds


def normalize_text(text: str) -> str:
    return " ".join(text.split())
