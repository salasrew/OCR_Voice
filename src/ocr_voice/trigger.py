from __future__ import annotations

from typing import Any

from .config import TriggerConfig


MOUSE_LABELS = {
    "right": "Right Mouse Button",
    "middle": "Middle Mouse Button",
    "x1": "Mouse Button 4",
    "x2": "Mouse Button 5",
}

MODIFIER_KEYSYMS = {
    "Shift_L",
    "Shift_R",
    "Control_L",
    "Control_R",
    "Alt_L",
    "Alt_R",
}


def normalize_mouse_button(value: str) -> str | None:
    normalized = value.lower().replace("button.", "").replace("mouse.", "")
    aliases = {
        "right": "right",
        "middle": "middle",
        "button8": "x1",
        "button9": "x2",
        "x1": "x1",
        "x2": "x2",
    }
    return aliases.get(normalized)


def is_mouse_trigger(button: Any, trigger: TriggerConfig) -> bool:
    if trigger.type != "mouse":
        return False
    name = getattr(button, "name", str(button))
    return normalize_mouse_button(str(name)) == trigger.value


def format_trigger_label(trigger: TriggerConfig) -> str:
    if trigger.type == "mouse":
        return MOUSE_LABELS.get(trigger.value, trigger.value)

    replacements = {
        "<ctrl>": "Ctrl",
        "<ctrl_l>": "Ctrl",
        "<ctrl_r>": "Ctrl",
        "<shift>": "Shift",
        "<shift_l>": "Shift",
        "<shift_r>": "Shift",
        "<alt>": "Alt",
        "<alt_l>": "Alt",
        "<alt_r>": "Alt",
    }
    parts = []
    for part in trigger.value.split("+"):
        parts.append(replacements.get(part, part.strip("<>").upper()))
    return "+".join(parts)


def keyboard_trigger_from_tk_parts(keysym: str, state: int) -> TriggerConfig | None:
    if keysym in MODIFIER_KEYSYMS:
        return None

    parts: list[str] = []
    if state & 0x0004:
        parts.append("<ctrl>")
    if state & 0x0001:
        parts.append("<shift>")
    if state & 0x0008 or state & 0x20000:
        parts.append("<alt>")

    key = keysym.lower()
    if len(key) != 1:
        key = f"<{key}>"
    parts.append(key)
    return TriggerConfig(type="keyboard", value="+".join(parts))


def mouse_trigger_from_tk_button(button_number: int) -> TriggerConfig | None:
    values = {
        2: "middle",
        3: "right",
        8: "x1",
        9: "x2",
    }
    value = values.get(button_number)
    if value is None:
        return None
    return TriggerConfig(type="mouse", value=value)
