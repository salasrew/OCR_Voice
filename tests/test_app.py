import unittest

from ocr_voice.app import build_hotkey_bindings, should_activate_mouse_trigger
from ocr_voice.config import AppConfig, TriggerConfig


class AppTests(unittest.TestCase):
    def test_hotkey_bindings_use_configured_hotkey(self):
        calls = []

        bindings = build_hotkey_bindings(AppConfig(hotkey="<alt>+j"), lambda: calls.append("snip"))

        self.assertEqual(list(bindings.keys()), ["<alt>+j"])

        bindings["<alt>+j"]()

        self.assertEqual(calls, ["snip"])

    def test_hotkey_bindings_use_keyboard_trigger_when_present(self):
        config = AppConfig(
            hotkey="<ctrl>+<shift>+o",
            trigger=TriggerConfig(type="keyboard", value="<alt>+j"),
        )

        bindings = build_hotkey_bindings(config, lambda: None)

        self.assertEqual(list(bindings.keys()), ["<alt>+j"])

    def test_mouse_trigger_activates_only_configured_button(self):
        class Button:
            name = "right"

        self.assertTrue(
            should_activate_mouse_trigger(
                Button(),
                AppConfig(trigger=TriggerConfig(type="mouse", value="right")),
            )
        )
        self.assertFalse(
            should_activate_mouse_trigger(
                Button(),
                AppConfig(trigger=TriggerConfig(type="mouse", value="middle")),
            )
        )


if __name__ == "__main__":
    unittest.main()
