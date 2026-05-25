# Japanese OCR Voice Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python prototype for right-click triggered Japanese OCR near the mouse cursor with TTS playback.

**Architecture:** Keep platform integrations behind adapters. Test configuration, geometry, duplicate suppression, and controller behavior with fakes.

**Tech Stack:** Python 3.11+, pytest, optional `pynput`, optional `mss`, optional `Pillow`, optional `pyttsx3`, optional OwOCR command integration.

---

### Task 1: Core Tests

**Files:**
- Create: `tests/test_config.py`
- Create: `tests/test_geometry.py`
- Create: `tests/test_controller.py`

- [ ] Write failing tests for default config, JSON overrides, centered capture rectangles, duplicate suppression, mode 0 click behavior, and mode 1 press/release behavior.
- [ ] Run `python -m pytest -q` and confirm the tests fail because `ocr_voice` modules do not exist.

### Task 2: Core Modules

**Files:**
- Create: `src/ocr_voice/config.py`
- Create: `src/ocr_voice/geometry.py`
- Create: `src/ocr_voice/controller.py`
- Create: `src/ocr_voice/__init__.py`

- [ ] Implement dataclass config loading from defaults and JSON.
- [ ] Implement rectangle calculation centered around the cursor.
- [ ] Implement duplicate suppression and mode coordination.
- [ ] Run `python -m pytest -q` and confirm tests pass.

### Task 3: Runtime Adapters

**Files:**
- Create: `src/ocr_voice/capture.py`
- Create: `src/ocr_voice/ocr.py`
- Create: `src/ocr_voice/tts.py`
- Create: `src/ocr_voice/app.py`
- Create: `src/ocr_voice/__main__.py`
- Create: `requirements.txt`
- Create: `README.md`
- Create: `config.example.json`

- [ ] Implement screenshot capture through `mss`.
- [ ] Implement external OCR command adapter.
- [ ] Implement TTS through external command or `pyttsx3`.
- [ ] Implement CLI entrypoint with mouse listener.
- [ ] Document setup, modes, and OwOCR integration.

### Task 4: Verification

**Files:**
- Read: all changed files

- [ ] Run `python -m pytest -q`.
- [ ] Run `python -m compileall src tests`.
- [ ] Report dependency/runtime limitations clearly.
