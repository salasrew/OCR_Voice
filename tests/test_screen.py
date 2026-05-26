import unittest

from ocr_voice.screen import monitor_to_rect


class ScreenTests(unittest.TestCase):
    def test_monitor_to_rect_uses_physical_monitor_bounds(self):
        monitor = {"left": 0, "top": 0, "width": 2560, "height": 1440}

        rect = monitor_to_rect(monitor)

        self.assertEqual(rect.left, 0)
        self.assertEqual(rect.top, 0)
        self.assertEqual(rect.width, 2560)
        self.assertEqual(rect.height, 1440)


if __name__ == "__main__":
    unittest.main()
