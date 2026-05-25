from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Rect:
    left: int
    top: int
    width: int
    height: int

    @property
    def as_mss(self) -> dict[str, int]:
        return {
            "left": self.left,
            "top": self.top,
            "width": self.width,
            "height": self.height,
        }


def centered_rect(cursor_x: int, cursor_y: int, *, width: int, height: int) -> Rect:
    left = max(0, int(cursor_x - width / 2))
    top = max(0, int(cursor_y - height / 2))
    return Rect(left=left, top=top, width=width, height=height)


def rect_from_points(start_x: int, start_y: int, end_x: int, end_y: int) -> Rect:
    left = min(start_x, end_x)
    top = min(start_y, end_y)
    return Rect(
        left=left,
        top=top,
        width=abs(end_x - start_x),
        height=abs(end_y - start_y),
    )
