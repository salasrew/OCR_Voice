import json
import tempfile
import unittest

from ocr_voice.config import AppConfig, load_config


class ConfigTests(unittest.TestCase):
    def test_default_config_uses_mode_zero_and_200_pixel_box(self):
        config = AppConfig()

        self.assertEqual(config.mode, 0)
        self.assertEqual(config.box_width, 500)
        self.assertEqual(config.box_height, 500)
        self.assertEqual(config.duplicate_window_seconds, 3.0)
        self.assertTrue(config.show_overlay)
        self.assertEqual(config.overlay_opacity, 0.45)
        self.assertEqual(config.border_color, "#00D1FF")
        self.assertEqual(config.hotkey, "<ctrl>+<shift>+o")
        self.assertEqual(config.min_selection_width, 8)
        self.assertEqual(config.min_selection_height, 8)

    def test_load_config_merges_json_overrides(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = f"{temp_dir}/config.json"
            with open(config_path, "w", encoding="utf-8") as file:
                json.dump(
                    {
                        "mode": 1,
                        "box_width": 320,
                        "box_height": 180,
                        "show_overlay": False,
                        "hotkey": "<alt>+j",
                        "min_selection_width": 12,
                        "min_selection_height": 10,
                        "ocr_command": ["owocr-image", "{image}"],
                    },
                    file,
                )

            config = load_config(config_path)

        self.assertEqual(config.mode, 1)
        self.assertEqual(config.box_width, 320)
        self.assertEqual(config.box_height, 180)
        self.assertFalse(config.show_overlay)
        self.assertEqual(config.hotkey, "<alt>+j")
        self.assertEqual(config.min_selection_width, 12)
        self.assertEqual(config.min_selection_height, 10)
        self.assertEqual(config.ocr_command, ["owocr-image", "{image}"])


if __name__ == "__main__":
    unittest.main()
