from __future__ import annotations

import queue
from collections.abc import Callable


class UiActionQueue:
    def __init__(self) -> None:
        self._actions: "queue.Queue[Callable[[], None]]" = queue.Queue()

    def submit(self, action: Callable[[], None]) -> None:
        self._actions.put(action)

    def drain(self) -> None:
        while True:
            try:
                action = self._actions.get_nowait()
            except queue.Empty:
                break
            action()
