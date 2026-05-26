from __future__ import annotations

import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from typing import Callable

from .config import AppConfig, TriggerConfig, load_config, save_trigger_config
from .geometry import Rect, rect_from_points
from .screen import primary_monitor_rect
from .tts import TtsService
from .trigger import format_trigger_label, keyboard_trigger_from_tk_parts, mouse_trigger_from_tk_button


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
    def __init__(self, config: AppConfig, *, config_path: str | Path | None = "config.json") -> None:
        self._config = config
        self._config_path = Path(config_path or "config.json")
        self._on_trigger_changed: Callable[[AppConfig], None] | None = None
        self._waiting_for_trigger = False
        self.root = tk.Tk()
        self.root.title("OCR Voice")
        self.root.geometry("560x340")
        self.root.minsize(520, 320)
        self.messages: "queue.Queue[str]" = queue.Queue()
        self.logger = GuiLog(self.messages)
        self.selection_overlay = SelectionOverlay(self.root, config)
        self._status_var = tk.StringVar(value="Ready")
        self._trigger_var = tk.StringVar(value=format_trigger_label(config.trigger))
        self._last_message_var = tk.StringVar(
            value=f"Press {format_trigger_label(config.trigger)} to select Japanese text."
        )
        self._build(config)
        self._poll_messages()

    def run_listener(self, target) -> None:
        thread = threading.Thread(target=target, daemon=True)
        thread.start()

    def set_trigger_changed_callback(self, callback: Callable[[AppConfig], None]) -> None:
        self._on_trigger_changed = callback

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

        trigger_row = ttk.Frame(frame)
        trigger_row.pack(fill="x", pady=(8, 0))
        ttk.Label(trigger_row, text="Trigger:").pack(side="left")
        ttk.Label(trigger_row, textvariable=self._trigger_var).pack(side="left", padx=(6, 0))
        ttk.Button(trigger_row, text="Change...", command=self._start_trigger_capture).pack(side="right")
        ttk.Button(trigger_row, text="Reset", command=self._reset_trigger).pack(side="right", padx=(0, 8))

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
                "3. Press the trigger, drag around Japanese text, and release."
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

    def _start_trigger_capture(self) -> None:
        if self._waiting_for_trigger:
            return
        self._waiting_for_trigger = True
        self.logger("Press a key combo or mouse button. Esc cancels.")
        self.root.focus_force()
        self.root.bind("<KeyPress>", self._capture_key_trigger)
        self.root.bind("<ButtonPress>", self._capture_mouse_trigger)

    def _capture_key_trigger(self, event: tk.Event) -> str | None:
        if getattr(event, "keysym", "") == "Escape":
            self._cancel_trigger_capture()
            self.logger("Trigger change cancelled.")
            return "break"

        trigger = keyboard_trigger_from_tk_parts(str(event.keysym), int(event.state))
        if trigger is None:
            return "break"
        self._apply_trigger(trigger)
        return "break"

    def _capture_mouse_trigger(self, event: tk.Event) -> str | None:
        trigger = mouse_trigger_from_tk_button(int(event.num))
        if trigger is None:
            self.logger("Left mouse button is not allowed as a global trigger.")
            return "break"
        self._apply_trigger(trigger)
        return "break"

    def _reset_trigger(self) -> None:
        self._apply_trigger(TriggerConfig(type="keyboard", value="<ctrl>+<shift>+o"))

    def _cancel_trigger_capture(self) -> None:
        self._waiting_for_trigger = False
        self.root.unbind("<KeyPress>")
        self.root.unbind("<ButtonPress>")

    def _apply_trigger(self, trigger: TriggerConfig) -> None:
        self._cancel_trigger_capture()
        try:
            save_trigger_config(self._config_path, trigger)
            self._config = load_config(self._config_path)
        except Exception as error:
            self.logger(f"Trigger save failed: {error}")
            return

        self._trigger_var.set(format_trigger_label(trigger))
        self._last_message_var.set(f"Press {format_trigger_label(trigger)} to select Japanese text.")
        self.selection_overlay = SelectionOverlay(self.root, self._config)
        if self._on_trigger_changed is not None:
            self._on_trigger_changed(self._config)
        self.logger(f"Trigger changed to {format_trigger_label(trigger)}.")

    def _poll_messages(self) -> None:
        while True:
            try:
                message = self.messages.get_nowait()
            except queue.Empty:
                break
            self._status_var.set("Status")
            self._last_message_var.set(message)
        self.root.after(100, self._poll_messages)
