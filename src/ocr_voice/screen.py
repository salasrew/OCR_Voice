from __future__ import annotations

from collections.abc import Mapping

from .geometry import Rect


def monitor_to_rect(monitor: Mapping[str, int]) -> Rect:
    return Rect(
        left=int(monitor["left"]),
        top=int(monitor["top"]),
        width=int(monitor["width"]),
        height=int(monitor["height"]),
    )


def primary_monitor_rect() -> Rect:
    try:
        import mss
    except ImportError as error:
        raise RuntimeError("Screen bounds require mss: pip install mss") from error

    with mss.mss() as screen:
        return monitor_to_rect(screen.monitors[1])
