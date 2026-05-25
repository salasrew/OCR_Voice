import unittest

from ocr_voice.geometry import Rect, centered_rect, rect_from_points


class GeometryTests(unittest.TestCase):
    def test_centered_rect_places_cursor_in_middle(self):
        rect = centered_rect(500, 300, width=200, height=120)

        self.assertEqual(rect, Rect(left=400, top=240, width=200, height=120))

    def test_centered_rect_clamps_to_screen_origin(self):
        rect = centered_rect(20, 10, width=200, height=120)

        self.assertEqual(rect, Rect(left=0, top=0, width=200, height=120))

    def test_rect_from_points_normalizes_reverse_drag(self):
        rect = rect_from_points(300, 250, 120, 80)

        self.assertEqual(rect, Rect(left=120, top=80, width=180, height=170))


if __name__ == "__main__":
    unittest.main()
