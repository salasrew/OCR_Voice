from __future__ import annotations

import ctypes
from typing import Any, Protocol


ERROR_ALREADY_EXISTS = 183


class InstanceBackend(Protocol):
    def acquire(self, name: str) -> tuple[Any, bool]:
        raise NotImplementedError

    def release(self, handle: Any) -> None:
        raise NotImplementedError


def instance_mutex_name() -> str:
    return r"Local\OCRVoice.SingleInstance"


class WindowsMutexBackend:
    def __init__(self) -> None:
        self._kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

    def acquire(self, name: str) -> tuple[Any, bool]:
        handle = self._kernel32.CreateMutexW(None, False, name)
        if not handle:
            raise OSError(ctypes.get_last_error(), "CreateMutexW failed")
        return handle, ctypes.get_last_error() == ERROR_ALREADY_EXISTS

    def release(self, handle: Any) -> None:
        self._kernel32.CloseHandle(handle)


class SingleInstanceLock:
    def __init__(self, *, backend: InstanceBackend | None = None, name: str | None = None) -> None:
        self._backend = backend or WindowsMutexBackend()
        self._name = name or instance_mutex_name()
        self._handle: Any | None = None

    def acquire(self) -> bool:
        handle, already_running = self._backend.acquire(self._name)
        if already_running:
            self._backend.release(handle)
            return False
        self._handle = handle
        return True

    def release(self) -> None:
        if self._handle is None:
            return
        self._backend.release(self._handle)
        self._handle = None
