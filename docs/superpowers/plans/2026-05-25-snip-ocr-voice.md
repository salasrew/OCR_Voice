# Snip OCR Voice Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rework OCR Voice into a configurable-hotkey Snipaste-style OCR reader that captures a user-selected region, runs OCR, and speaks recognized Japanese text.

**Architecture:** Keep the OCR/TTS adapters, but replace the right-click fixed-box interaction with a hotkey-driven selection pipeline. Core behavior remains testable with fakes; Tk/pynput/mss integrations stay behind small runtime adapters.

**Tech Stack:** Python 3.10+, unittest, tkinter, pynput, mss, Pillow, edge-tts, pyttsx3, PyInstaller.

---

### Task 1: Core Pipeline And Config

**Files:**
- Modify: `src/ocr_voice/config.py`
- Modify: `src/ocr_voice/controller.py`
- Modify: `tests/test_config.py`
- Modify: `tests/test_controller.py`

- [ ] Add tests for configurable `hotkey`, minimum selection size, successful selected-region OCR/TTS, empty OCR output, OCR failure, and TTS failure reporting.
- [ ] Run `set PYTHONPATH=src && python -m unittest tests.test_config tests.test_controller` and confirm new tests fail for missing behavior.
- [ ] Add `hotkey`, `min_selection_width`, and `min_selection_height` to `AppConfig`.
- [ ] Add selected-region pipeline methods to `OcrVoiceController` while keeping legacy right-click methods temporarily intact.
- [ ] Run the targeted tests and confirm they pass.

### Task 2: Selection Overlay And Hotkey Runtime

**Files:**
- Modify: `src/ocr_voice/gui.py`
- Modify: `src/ocr_voice/app.py`

- [ ] Add a Tk selection overlay that returns a normalized `Rect` or cancellation.
- [ ] Add a configurable global hotkey listener using `pynput.keyboard.GlobalHotKeys`.
- [ ] Wire the hotkey to open the selection overlay and call the selected-region controller path.
- [ ] Keep the status window small and use it for readiness, last text, and errors.

### Task 3: Build Hygiene

**Files:**
- Modify: `.gitignore`
- Modify: `build_package.bat`
- Modify: `config.example.json`
- Modify: `README.md`
- Modify: `pyproject.toml`

- [ ] Ignore old root-level generated artifacts: `OCRVoice-gui/`, `OCRVoice-size/`, and `*.zip`.
- [ ] Ensure `build_package.bat` only creates `dist/OCRVoice/OCRVoice.exe` and `dist/OCRVoice/config.json`; it must not create a zip.
- [ ] Add runtime dependencies to `pyproject.toml`.
- [ ] Update config and README for configurable hotkey and Snip-style workflow.

### Task 4: Verification

**Files:**
- Read: all changed files

- [ ] Run `python -m compileall src tests`.
- [ ] Run `$env:PYTHONPATH='src'; python -m unittest discover -s tests`.
- [ ] Run `build_package.bat` if dependencies are available, producing `dist/OCRVoice/OCRVoice.exe`.
- [ ] Report the exe path and any blocked verification clearly.
