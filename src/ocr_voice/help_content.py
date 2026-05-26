from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HelpSection:
    title: str
    body: str


def help_sections() -> list[HelpSection]:
    return [
        HelpSection(
            title="Japanese OCR",
            body=(
                "OCR uses Microsoft Windows OCR first. Japanese recognition requires the "
                "Windows Japanese OCR language capability. Install Japanese from Windows "
                "Settings > Time & language > Language & region, then add the Japanese "
                "language features if OCR fails or returns no text."
            ),
        ),
        HelpSection(
            title="Japanese TTS",
            body=(
                "TTS uses Microsoft Windows speech first. Japanese playback requires an "
                "installed Japanese Windows voice. Install it from Windows Settings > "
                "Time & language > Speech or the Japanese language options. Use Test Voice "
                "to verify speech output."
            ),
        ),
        HelpSection(
            title="Capture Notes",
            body=(
                "Use borderless-windowed game mode if the overlay, trigger, or capture does "
                "not work. Exclusive fullscreen and protected windows may block global "
                "input hooks or screen capture. Captured images are deleted after OCR/TTS "
                "finishes."
            ),
        ),
        HelpSection(
            title="System Tray",
            body=(
                "Closing the main window hides OCR Voice to the Windows system tray. Use "
                "the tray menu to Show the window, open Help, run Test Voice, or Exit the "
                "app completely."
            ),
        ),
    ]


def help_text() -> str:
    return "\n\n".join(f"{section.title}\n{section.body}" for section in help_sections())
