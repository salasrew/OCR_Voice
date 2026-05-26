# OCR Voice

Windows-first prototype for Japanese language learning in games. Press a configurable trigger, drag a Snipaste-style region around Japanese text, OCR the screenshot, and speak the recognized text aloud.

The packaged app opens a small status window showing the configured trigger, OCR configuration state, and latest status or error. OCR uses Microsoft Windows OCR first, and TTS uses Microsoft Windows speech first.

## Workflow

1. Start `OCRVoice.exe` or run the Python module.
2. Press the configured trigger. The default is `Ctrl+Shift+O`.
3. Drag a rectangle around Japanese text.
4. Release the mouse button to capture, OCR, and speak the selected region.
5. Press `Esc` during selection to cancel.

The trigger can be changed in the status window with `Change...`, then pressing a keyboard combo or mouse button. Left mouse button is rejected because it would interfere with normal clicks. `Esc` cancels capture.

The trigger is saved in `config.json`:

```json
{
  "trigger": {
    "type": "keyboard",
    "value": "<ctrl>+<shift>+o"
  }
}
```

Mouse trigger example:

```json
{
  "trigger": {
    "type": "mouse",
    "value": "right"
  }
}
```

The older `hotkey` setting is still supported for existing configs.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
copy config.example.json config.json
```

By default, OCR uses the local Microsoft Windows OCR engine for Japanese. If Windows OCR is unavailable or the quality is not good enough, set `ocr_command` to a command that accepts an image path and prints Japanese text to stdout.

Example shape:

```json
{
  "ocr_command": ["your-ocr-command", "{image}"]
}
```

## Run From Source

```powershell
$env:PYTHONPATH = "src"
python -m ocr_voice --config config.json
```

## Build Exe

```powershell
.\build_package.bat
```

The validation executable is created at:

```text
dist\OCRVoice\OCRVoice.exe
```

The build script does not create a zip. Zip archives are release artifacts and should only be created when explicitly needed.

## Notes

- Japanese OCR requires the Windows Japanese OCR language capability. If recognition fails, install Japanese OCR support from Windows language settings.
- Japanese TTS requires an installed Japanese Windows voice.
- Use windowed or borderless-windowed game mode if the overlay or screenshot capture is blocked.
- Exclusive fullscreen or protected games may block global hotkeys, overlays, or screen capture.
- Captured images are written to `capture_dir`, which defaults to `.ocr_voice_captures`.

## Troubleshooting

The app includes a `Help` button with the same guidance:

- Japanese OCR: install the Windows Japanese OCR language capability from `Settings > Time & language > Language & region` if OCR fails or returns no text.
- Japanese TTS: install a Japanese Windows voice from `Settings > Time & language > Speech` or Japanese language options. Use `Test Voice` to verify playback.
- Capture: use borderless-windowed mode when possible. Exclusive fullscreen or protected windows may block triggers, overlays, or screen capture.
- Captured images are deleted after OCR/TTS finishes.
