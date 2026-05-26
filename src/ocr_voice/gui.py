from __future__ import annotations

import queue
import threading
import tkinter as tk
from tkinter import ttk
from typing import Callable

from .config import AppConfig
from .geometry import Rect, rect_from_points
from .screen import primary_monitor_rect
from .tts import TtsService


class GuiLog:
    def __init__(self, messages: "queue.Queue[str]") -> None:
        self._messages = messages

    def __call__(self, message: str) -> None:
        self._messages.put(message)


class SelectionOverlay:
    def __init__(self, root: tk.Tk, config: AppConfig) -> None:
        self._root = root
        self._config = config
        self._window: tk.Toplevel | None = None
        self._canvas: tk.Canvas | None = None
        self._bounds: Rect | None = None
        self._start: tuple[int, int] | None = None
        self._outline_id: int | None = None
        self._on_complete: Callable[[Rect], None] | None = None

    def start(self, on_complete: Callable[[Rect], None]) -> None:
        self._root.after(0, lambda: self._open(on_complete))

    def _open(self, on_complete: Callable[[Rect], None]) -> None:
        if self._window is not None:
            return

        self._on_complete = on_complete
        self._bounds = primary_monitor_rect()
        window = tk.Toplevel(self._root)
        window.overrideredirect(True)
        window.attributes("-topmost", True)
        window.attributes("-alpha", self._config.overlay_opacity)
        window.configure(bg="black")
        window.geometry(
            f"{self._bounds.width}x{self._bounds.height}+{self._bounds.left}+{self._bounds.top}"
        )
        window.focus_force()

        canvas = tk.Canvas(window, highlightthickness=0, bg="black", cursor="crosshair")
        canvas.pack(fill="both", expand=True)
        canvas.bind("<ButtonPress-1>", self._on_press)
        canvas.bind("<B1-Motion>", self._on_drag)
        canvas.bind("<ButtonRelease-1>", self._on_release)
        window.bind("<Escape>", self._cancel)

        self._window = window
        self._canvas = canvas

    def _on_press(self, event: tk.Event) -> None:
        self._start = (int(event.x), int(event.y))
        self._draw_outline(int(event.x), int(event.y))

    def _on_drag(self, event: tk.Event) -> None:
        if self._start is None:
            return
        self._draw_outline(int(event.x), int(event.y))

    def _on_release(self, event: tk.Event) -> None:
        if self._start is None:
            self._cancel()
            return

        start_x, start_y = self._start
        bounds = self._bounds or Rect(left=0, top=0, width=0, height=0)
        rect = rect_from_points(
            start_x,
            start_y,
            int(event.x),
            int(event.y),
            origin_left=bounds.left,
            origin_top=bounds.top,
        )
        on_complete = self._on_complete
        self._clear()
        if on_complete is not None:
            self._root.after(100, lambda: on_complete(rect))

    def _draw_outline(self, current_x: int, current_y: int) -> None:
        if self._canvas is None or self._start is None:
            return

        start_x, start_y = self._start
        if self._outline_id is not None:
            self._canvas.delete(self._outline_id)
        self._outline_id = self._canvas.create_rectangle(
            start_x,
            start_y,
            current_x,
            current_y,
            outline=self._config.border_color,
            width=3,
        )

    def _cancel(self, event: tk.Event | None = None) -> None:
        self._clear()

    def _clear(self) -> None:
        if self._window is not None:
            try:
                self._window.destroy()
            except tk.TclError:
                pass
        self._window = None
        self._canvas = None
        self._bounds = None
        self._start = None
        self._outline_id = None
        self._on_complete = None


class StatusGui:
    def __init__(self, config: AppConfig) -> None:
        self.root = tk.Tk()
        self.root.title("OCR Voice")
        self.root.geometry("520x300")
        self.root.minsize(480, 280)
        self.messages: "queue.Queue[str]" = queue.Queue()
        self.logger = GuiLog(self.messages)
        self.selection_overlay = SelectionOverlay(self.root, config)
        self._status_var = tk.StringVar(value="Ready")
        self._last_message_var = tk.StringVar(value=f"Press {config.hotkey} to select Japanese text.")
        self._build(config)
        self._poll_messages()

    def run_listener(self, target) -> None:
        thread = threading.Thread(target=target, daemon=True)
        thread.start()

    def start_selection(self, processor: Callable[[Rect], None]) -> None:
        self.logger("Selection started.")

        def on_complete(rect: Rect) -> None:
            self.logger(f"Selected {rect.width} x {rect.height}px.")
            threading.Thread(target=lambda: processor(rect), daemon=True).start()

        self.selection_overlay.start(on_complete)

    def mainloop(self) -> None:
        self.root.mainloop()

    def _build(self, config: AppConfig) -> None:
        frame = ttk.Frame(self.root, padding=16)
        frame.pack(fill="both", expand=True)

        title = ttk.Label(frame, text="OCR Voice", font=("Segoe UI", 18, "bold"))
        title.pack(anchor="w")

        ttk.Label(frame, text=f"Hotkey: {config.hotkey}").pack(anchor="w", pady=(8, 0))

        actions = ttk.Frame(frame)
        actions.pack(fill="x", pady=(10, 0))
        ttk.Button(
            actions,
            text="Test Voice",
            command=lambda: self._test_voice(config),
        ).pack(side="left")

        if config.ocr_command:
            ocr_text = "OCR: Microsoft Windows OCR first, command fallback: " + " ".join(config.ocr_command)
        else:
            ocr_text = "OCR: Microsoft Windows OCR first. No external command fallback configured."
        ttk.Label(frame, text=ocr_text, wraplength=460, foreground="#A03A00").pack(anchor="w", pady=(12, 0))

        ttk.Separator(frame).pack(fill="x", pady=12)

        ttk.Label(frame, text="How to use", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        ttk.Label(
            frame,
            text=(
                "1. Set ocr_command in config.json.\n"
                "2. Use borderless-windowed game mode if the overlay is hidden.\n"
                "3. Press the hotkey, drag around Japanese text, and release."
            ),
            justify="left",
        ).pack(anchor="w", pady=(4, 0))

        ttk.Separator(frame).pack(fill="x", pady=12)

        ttk.Label(frame, textvariable=self._status_var, font=("Segoe UI", 10, "bold")).pack(anchor="w")
        ttk.Label(frame, textvariable=self._last_message_var, wraplength=460).pack(anchor="w", pady=(4, 0))

    def _test_voice(self, config: AppConfig) -> None:
        self.logger("Testing voice...")

        def worker() -> None:
            try:
                TtsService(config.tts_command).speak("日本語の音声テストです")
                self.logger("Voice test finished.")
            except Exception as error:
                self.logger(f"Voice test failed: {error}")

        threading.Thread(target=worker, daemon=True).start()

    def _poll_messages(self) -> None:
        while True:
            try:
                message = self.messages.get_nowait()
            except queue.Empty:
                break
            self._status_var.set("Status")
            self._last_message_var.set(message)
        self.root.after(100, self._poll_messages)
