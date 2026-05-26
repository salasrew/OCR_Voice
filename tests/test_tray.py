import unittest

from ocr_voice.tray import tray_menu_labels


class TrayTests(unittest.TestCase):
    def test_tray_menu_exposes_show_help_test_voice_and_exit(self):
        self.assertEqual(tray_menu_labels(), ["Show", "Help", "Test Voice", "Exit"])


if __name__ == "__main__":
    unittest.main()
