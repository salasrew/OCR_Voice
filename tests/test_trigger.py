import unittest

from ocr_voice.config import TriggerConfig
from ocr_voice.trigger import (
    format_trigger_label,
    is_mouse_trigger,
    keyboard_trigger_from_tk_parts,
    mouse_trigger_from_tk_button,
    normalize_mouse_button,
)


class TriggerTests(unittest.TestCase):
    def test_format_trigger_label_handles_keyboard_and_mouse(self):
        self.assertEqual(
            format_trigger_label(TriggerConfig(type="keyboard", value="<ctrl>+<shift>+o")),
            "Ctrl+Shift+O",
        )
        self.assertEqual(
            format_trigger_label(TriggerConfig(type="mouse", value="right")),
            "Right Mouse Button",
        )

    def test_is_mouse_trigger_matches_configured_button_name(self):
        class Button:
            name = "right"

        self.assertTrue(is_mouse_trigger(Button(), TriggerConfig(type="mouse", value="right")))
        self.assertFalse(is_mouse_trigger(Button(), TriggerConfig(type="mouse", value="middle")))

    def test_normalize_mouse_button_rejects_left_click(self):
        self.assertEqual(normalize_mouse_button("right"), "right")
        self.assertEqual(normalize_mouse_button("middle"), "middle")
        self.assertIsNone(normalize_mouse_button("left"))

    def test_keyboard_trigger_from_tk_parts_keeps_modifier_order(self):
        trigger = keyboard_trigger_from_tk_parts("O", state=0x0004 | 0x0001)

        self.assertEqual(trigger, TriggerConfig(type="keyboard", value="<ctrl>+<shift>+o"))

    def test_keyboard_trigger_from_tk_parts_ignores_modifier_only_press(self):
        self.assertIsNone(keyboard_trigger_from_tk_parts("Control_L", state=0x0004))

    def test_mouse_trigger_from_tk_button_allows_non_left_buttons(self):
        self.assertIsNone(mouse_trigger_from_tk_button(1))
        self.assertEqual(mouse_trigger_from_tk_button(3), TriggerConfig(type="mouse", value="right"))
        self.assertEqual(mouse_trigger_from_tk_button(2), TriggerConfig(type="mouse", value="middle"))


if __name__ == "__main__":
    unittest.main()
