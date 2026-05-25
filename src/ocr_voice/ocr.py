from __future__ import annotations

import asyncio
from pathlib import Path
import subprocess
from typing import Callable, Protocol

from .process import run_hidden


class OcrCommandError(RuntimeError):
    pass


class OcrBackend(Protocol):
    def recognize(self, image_path: str) -> str:
        raise NotImplementedError


class MicrosoftOcrService:
    def __init__(self, language_tag: str = "ja-JP") -> None:
        self._language_tag = language_tag

    def recognize(self, image_path: str) -> str:
        try:
            return asyncio.run(self._recognize_async(image_path)).strip()
        except ImportError as error:
            raise OcrCommandError(
                "Microsoft OCR requires WinRT packages. Rebuild with the winrt dependencies installed."
            ) from error
        except Exception as error:
            raise OcrCommandError(f"Microsoft OCR failed: {error}") from error

    async def _recognize_async(self, image_path: str) -> str:
        from winrt.windows.globalization import Language
        from winrt.windows.graphics.imaging import BitmapDecoder
        from winrt.windows.media.ocr import OcrEngine
        from winrt.windows.storage import FileAccessMode, StorageFile

        resolved_path = str(Path(image_path).resolve())
        engine = OcrEngine.try_create_from_language(Language(self._language_tag))
        if engine is None:
            raise OcrCommandError(
                f"Microsoft OCR language is unavailable: {self._language_tag}. "
                "Install the Japanese OCR language capability in Windows settings."
            )

        file = await StorageFile.get_file_from_path_async(resolved_path)
        stream = await file.open_async(FileAccessMode.READ)
        try:
            decoder = await BitmapDecoder.create_async(stream)
            bitmap = await decoder.get_software_bitmap_async()
            result = await engine.recognize_async(bitmap)
            return result.text
        finally:
            close = getattr(stream, "close", None)
            if close is not None:
                close()


class CommandOcrService:
    def __init__(self, command: list[str] | None) -> None:
        self._command = command

    def recognize(self, image_path: str) -> str:
        if not self._command:
            raise OcrCommandError(
                "No OCR command configured. Set ocr_command in config.json."
            )

        command = [part.replace("{image}", image_path) for part in self._command]
        try:
            completed = run_hidden(
                command,
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
        except FileNotFoundError as error:
            raise OcrCommandError(
                f"OCR command not found: {command[0]}. Check config.json ocr_command."
            ) from error
        except subprocess.CalledProcessError as error:
            details = (error.stderr or error.stdout or "").strip()
            if details:
                raise OcrCommandError(f"OCR command failed: {details}") from error
            raise OcrCommandError(f"OCR command failed with exit code {error.returncode}") from error
        return completed.stdout.strip()


class AutoOcrService:
    def __init__(
        self,
        command: list[str] | None,
        *,
        microsoft_factory: Callable[[], OcrBackend] = MicrosoftOcrService,
        command_factory: Callable[[list[str] | None], OcrBackend] = CommandOcrService,
    ) -> None:
        self._command = command
        self._microsoft_factory = microsoft_factory
        self._command_factory = command_factory

    def recognize(self, image_path: str) -> str:
        try:
            return self._microsoft_factory().recognize(image_path)
        except Exception as microsoft_error:
            if self._command:
                return self._command_factory(self._command).recognize(image_path)
            raise OcrCommandError(
                "Microsoft OCR failed and no ocr_command fallback is configured. "
                f"Details: {microsoft_error}"
            ) from microsoft_error
