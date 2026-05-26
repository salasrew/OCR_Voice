import unittest

from ocr_voice.help_window import help_window_size


class HelpWindowTests(unittest.TestCase):
    def test_help_window_uses_scrollable_friendly_size(self):
        self.assertEqual(help_window_size(), "560x460")


if __name__ == "__main__":
    unittest.main()
