# Japanese OCR Voice Design

## Goal

Build a Windows-first prototype that lets the user trigger Japanese OCR near the mouse cursor with the right mouse button and hear the recognized text spoken aloud.

## Interaction Modes

- Mode 0: Right-click once to OCR a fixed rectangle centered on the current mouse position.
- Mode 1: Hold right-click to show the active rectangle while moving the mouse, then release right-click to OCR the final rectangle.

The default mode is 0. The default OCR rectangle is 200 by 200 pixels. Width, height, OCR command, TTS command, and duplicate suppression are configurable.

## Architecture

The prototype is a Python package with small, testable units:

- Configuration loads defaults and optional JSON overrides.
- Geometry calculates capture rectangles from cursor coordinates.
- Capture grabs a screenshot of a rectangle.
- OCR accepts an image path and returns recognized Japanese text.
- TTS accepts text and speaks it.
- Controller coordinates right-click mode behavior and duplicate suppression.

Runtime adapters may depend on Windows-specific libraries, but core behavior remains testable without those dependencies.

## OCR Strategy

OwOCR is the main reference project because it is focused on Japanese OCR and supports screen capture, clipboard, files, websockets, OneOCR, Manga OCR, and cloud engines. This prototype keeps OCR behind a command adapter so it can call OwOCR later without rewriting the interaction logic.

The first adapter supports an external command template that receives an image path and prints recognized text to stdout.

## TTS Strategy

The first adapter supports either Windows SAPI through `pyttsx3` or an external command template. Japanese voice selection is left to the OS or the user-provided command.

## Risks

Some games, especially exclusive fullscreen or protected games, may block screen capture or global mouse hooks. The app provides a keyboard fallback and keeps the OCR trigger configurable so the input layer can be adjusted after testing against the target game.
