from __future__ import annotations

import asyncio
import subprocess
import tempfile
from pathlib import Path
from typing import Callable, Sequence


class TtsService:
    def __init__(
        self,
        command: list[str] | None = None,
        *,
        speakers: Sequence[Callable[[str], None]] | None = None,
    ) -> None:
        self._command = command
        self._speakers = speakers or (
            speak_with_powershell,
            speak_with_pyttsx3,
            speak_with_edge_tts,
        )

    def speak(self, text: str) -> None:
        if self._command:
            command = [part.replace("{text}", text) for part in self._command]
            subprocess.run(command, check=True)
            return

        errors: list[str] = []
        for speaker in self._speakers:
            try:
                speaker(text)
                return
            except Exception as error:
                errors.append(f"{speaker.__name__}: {error}")
        raise RuntimeError("All TTS backends failed. " + " | ".join(errors))


def speak_with_edge_tts(text: str) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = str(Path(temp_dir) / "voice.mp3")
        asyncio.run(_save_edge_tts(text, output_path))
        subprocess.run(build_powershell_mp3_playback_command(output_path), check=True)


async def _save_edge_tts(text: str, output_path: str) -> None:
    import edge_tts

    communicate = edge_tts.Communicate(text, "ja-JP-NanamiNeural")
    await communicate.save(output_path)


def speak_with_pyttsx3(text: str) -> None:
    import pyttsx3

    engine = pyttsx3.init()
    for voice in engine.getProperty("voices"):
        voice_id = getattr(voice, "id", "")
        voice_name = getattr(voice, "name", "")
        languages = " ".join(str(language) for language in getattr(voice, "languages", []))
        haystack = f"{voice_id} {voice_name} {languages}".lower()
        if "japan" in haystack or "ja" in haystack or "haruka" in haystack:
            engine.setProperty("voice", voice_id)
            break
    engine.say(text)
    engine.runAndWait()


def speak_with_powershell(text: str) -> None:
    subprocess.run(build_powershell_speech_command(text), check=True)


def build_powershell_mp3_playback_command(path: str) -> list[str]:
    escaped_path = path.replace("'", "''")
    script = (
        "Add-Type -AssemblyName PresentationCore; "
        "$player = New-Object System.Windows.Media.MediaPlayer; "
        "$player.Open([Uri]'" + escaped_path + "'); "
        "$player.Play(); "
        "Start-Sleep -Seconds 5; "
        "$player.Close();"
    )
    return [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-Command",
        script,
    ]


def build_powershell_speech_command(text: str) -> list[str]:
    escaped = text.replace("'", "''")
    script = (
        "Add-Type -AssemblyName System.Speech; "
        "$speaker = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        "try { $speaker.SelectVoiceByHints("
        "[System.Speech.Synthesis.VoiceGender]::NotSet, "
        "[System.Speech.Synthesis.VoiceAge]::NotSet, 0, "
        "(New-Object System.Globalization.CultureInfo('ja-JP'))"
        ") } catch {}; "
        "$speaker.Speak('" + escaped + "');"
    )
    return [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-Command",
        script,
    ]
