import unittest

from ocr_voice.app import build_hotkey_bindings
from ocr_voice.config import AppConfig


class AppTests(unittest.TestCase):
    def test_hotkey_bindings_use_configured_hotkey(self):
        calls = []

        bindings = build_hotkey_bindings(AppConfig(hotkey="<alt>+j"), lambda: calls.append("snip"))

        self.assertEqual(list(bindings.keys()), ["<alt>+j"])

        bindings["<alt>+j"]()

        self.assertEqual(calls, ["snip"])


if __name__ == "__main__":
    unittest.main()
