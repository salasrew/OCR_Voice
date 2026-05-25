# Snip OCR Voice Design

## Goal

Rework OCR Voice into a cleaner Windows-first tool that behaves like a small Snipaste-style OCR reader:

1. The user presses a global hotkey.
2. The screen shows a dark selection overlay.
3. The user drags a rectangle around Japanese text.
4. The app captures that selected region.
5. OCR extracts text from the image.
6. TTS speaks the recognized Japanese text.

The primary validation artifact is an executable at `dist/OCRVoice/OCRVoice.exe`. Zip archives are release artifacts only and should not be produced during normal development validation unless explicitly requested.

## User Workflow

Default flow:

- Start `OCRVoice.exe`.
- The app runs in the background with a small status window.
- Press the configured hotkey to start selection. The default is `Ctrl+Shift+O`.
- Drag a region on screen.
- Release the mouse button to OCR and speak the captured text.
- Press `Esc` during selection to cancel.

The first implementation should target windowed or borderless-windowed games. Exclusive fullscreen and protected games may block overlay or screen capture; the app should report that limitation clearly instead of trying to hide it.

## Scope

In scope:

- Configurable global hotkey starts selection.
- Snip-style overlay supports drag-to-select and cancel.
- Selected rectangle is captured to a temporary capture path.
- Existing command-based OCR adapter remains the first OCR path.
- Existing TTS fallback chain remains usable.
- A small status UI displays ready state, OCR config state, last recognized text, and last error.
- Build script creates an exe for local validation without creating a zip.

Out of scope for this pass:

- Automatic OCR around the cursor.
- Right-click mode 0 and mode 1 behavior.
- Mouse-wheel box resizing.
- Built-in OCR engine integration.
- Release packaging as zip.
- Installer creation.

## Architecture

The project should be reorganized around one clear pipeline:

```text
HotkeyListener
  -> SelectionOverlay
  -> ScreenCaptureService
  -> OcrService
  -> TextNormalizer
  -> TtsService
  -> StatusReporter
```

### Components

- `AppConfig`
  - Holds hotkey, capture directory, OCR command, TTS command, overlay opacity, border color, and GUI preference.
  - Uses `Ctrl+Shift+O` as the default hotkey, but allows the user to change it in `config.json`.
  - Removes or deprecates right-click-only settings after migration.

- `HotkeyListener`
  - Listens for the configured hotkey.
  - Starts selection by calling a narrow application service method.
  - Does not know about OCR or TTS.

- `SelectionOverlay`
  - Owns the full-screen transparent/dimmed UI.
  - Tracks drag start, current pointer, selected rectangle, cancel, and finish.
  - Returns a `Rect` or a cancellation result.

- `ScreenCaptureService`
  - Captures a `Rect` to an image file.
  - Keeps implementation behind an interface so tests do not require screen access.

- `OcrService`
  - Receives an image path and returns text.
  - Keeps the command adapter as the first backend.

- `TextNormalizer`
  - Collapses whitespace and rejects empty text.
  - May later handle OCR cleanup for Japanese punctuation, but this pass should stay minimal.

- `TtsService`
  - Receives normalized text and speaks it.
  - Keeps existing command, Edge TTS, pyttsx3, and PowerShell fallback behavior unless testing shows a specific backend should be removed.

- `StatusGui`
  - Displays readiness, OCR command configuration, current action, last text, and errors.
  - Starts minimized or compact by default if that proves less intrusive during testing.

## Data Flow

Successful capture:

```text
Configured hotkey pressed
  -> show overlay
  -> user drags rectangle
  -> capture selected rect
  -> run OCR command
  -> normalize text
  -> speak text
  -> update status UI
```

Cancellation:

```text
Configured hotkey pressed
  -> show overlay
  -> Esc or invalid tiny selection
  -> hide overlay
  -> no OCR, no TTS
```

Failure:

```text
capture/OCR/TTS error
  -> hide overlay if needed
  -> report concise error in status UI
  -> keep app running
```

## Error Handling

- Missing `ocr_command`: app starts, hotkey works, but attempting OCR reports a configuration error.
- OCR command not found or non-zero exit: report the command failure and keep listening.
- Empty OCR output: report "No text recognized" without speaking.
- TTS failure: report the backend errors after OCR succeeds.
- Overlay/capture unavailable in a game: report that windowed or borderless-windowed mode may be required.

## Build And Validation

Normal validation build:

```text
dist/OCRVoice/OCRVoice.exe
dist/OCRVoice/config.json
```

The build script should not create `OCRVoice-size.zip`, `OCRVoice-gui/`, or `OCRVoice-size/` at the repo root. Those names should be treated as old generated artifacts and ignored or removed from the normal workflow.

Release packaging can be added later as a separate explicit command such as `build_release.bat`.

## Testing Strategy

Fast tests:

- Config loads hotkey and OCR/TTS settings.
- Hotkey listener uses the configured hotkey instead of a hard-coded shortcut.
- Rect normalization rejects tiny/zero selections.
- Application pipeline calls capture, OCR, normalizer, and TTS in order.
- Empty OCR output does not call TTS.
- OCR and TTS failures are reported without crashing.

Manual validation:

- Run the exe.
- Press the configured hotkey.
- Drag a region over visible Japanese text.
- Confirm the selected region is captured.
- Confirm OCR command receives the image path.
- Confirm recognized Japanese is spoken.
- Confirm `Esc` cancels selection.

## Migration Notes

The current right-click controller can be used as a reference for duplicate suppression, error isolation, and test fakes, but the interaction model should not stay centered on fixed cursor boxes. The cleaner model is user-selected region first, OCR/TTS second.

Existing build outputs and capture folders should not be considered source. They should be excluded from version control and generated only when needed for validation.
