import unittest

from ocr_voice.config import AppConfig
from ocr_voice.controller import OcrVoiceController
from ocr_voice.geometry import Rect


class FakeClock:
    def __init__(self):
        self.now = 100.0

    def __call__(self):
        return self.now


class FakeCapture:
    def __init__(self):
        self.rects = []

    def capture(self, rect):
        self.rects.append(rect)
        return "capture.png"


class FakeOcr:
    def __init__(self, text):
        self.text = text
        self.images = []

    def recognize(self, image_path):
        self.images.append(image_path)
        return self.text


class FakeTts:
    def __init__(self):
        self.spoken = []

    def speak(self, text):
        self.spoken.append(text)


class FailingOcr:
    def recognize(self, image_path):
        raise RuntimeError("ocr unavailable")


class FailingTts:
    def speak(self, text):
        raise RuntimeError("voice unavailable")


class FakeLogger:
    def __init__(self):
        self.messages = []

    def __call__(self, message):
        self.messages.append(message)


class FakeOverlay:
    def __init__(self):
        self.calls = []

    def show(self, rect):
        self.calls.append(("show", rect))

    def update(self, rect):
        self.calls.append(("update", rect))

    def hide(self):
        self.calls.append(("hide",))


def build_controller(mode, text="日本語"):
    clock = FakeClock()
    capture = FakeCapture()
    ocr = FakeOcr(text)
    tts = FakeTts()
    config = AppConfig(mode=mode, box_width=200, box_height=200)
    controller = OcrVoiceController(config, capture, ocr, tts, clock=clock)
    return controller, capture, ocr, tts, clock


class ControllerTests(unittest.TestCase):
    def test_mode_zero_right_click_immediately_captures_and_speaks(self):
        controller, capture, ocr, tts, _ = build_controller(mode=0)

        controller.on_right_click_pressed(300, 250)

        self.assertEqual(capture.rects, [Rect(left=200, top=150, width=200, height=200)])
        self.assertEqual(ocr.images, ["capture.png"])
        self.assertEqual(tts.spoken, ["日本語"])

    def test_mode_one_captures_only_after_release_at_final_position(self):
        controller, capture, _, tts, _ = build_controller(mode=1)

        controller.on_right_click_pressed(300, 250)
        controller.on_mouse_moved(420, 280)

        self.assertEqual(capture.rects, [])
        self.assertEqual(controller.preview_rect, Rect(left=320, top=180, width=200, height=200))

        controller.on_right_click_released(420, 280)

        self.assertEqual(capture.rects, [Rect(left=320, top=180, width=200, height=200)])
        self.assertEqual(tts.spoken, ["日本語"])
        self.assertIsNone(controller.preview_rect)

    def test_duplicate_text_is_not_spoken_inside_duplicate_window(self):
        controller, capture, _, tts, clock = build_controller(mode=0, text="同じ")

        controller.on_right_click_pressed(300, 250)
        clock.now += 1.0
        controller.on_right_click_pressed(300, 250)

        self.assertEqual(len(capture.rects), 2)
        self.assertEqual(tts.spoken, ["同じ"])

    def test_ocr_error_is_reported_without_crashing_controller(self):
        capture = FakeCapture()
        tts = FakeTts()
        logger = FakeLogger()
        controller = OcrVoiceController(
            AppConfig(mode=0),
            capture,
            FailingOcr(),
            tts,
            logger=logger,
        )

        controller.on_right_click_pressed(300, 250)

        self.assertEqual(len(capture.rects), 1)
        self.assertEqual(tts.spoken, [])
        self.assertEqual(logger.messages, ["OCR failed: ocr unavailable"])

    def test_mode_one_updates_overlay_until_release(self):
        capture = FakeCapture()
        overlay = FakeOverlay()
        controller = OcrVoiceController(
            AppConfig(mode=1, box_width=200, box_height=200, show_overlay=True),
            capture,
            FakeOcr("text"),
            FakeTts(),
            overlay=overlay,
        )

        controller.on_right_click_pressed(300, 250)
        controller.on_mouse_moved(420, 280)
        controller.on_right_click_released(420, 280)

        self.assertEqual(
            overlay.calls,
            [
                ("show", Rect(left=200, top=150, width=200, height=200)),
                ("update", Rect(left=320, top=180, width=200, height=200)),
                ("hide",),
            ],
        )

    def test_box_size_can_be_changed_at_runtime(self):
        controller, capture, _, _, _ = build_controller(mode=0)

        controller.set_box_size(500, 500)
        controller.on_right_click_pressed(700, 600)

        self.assertEqual(capture.rects, [Rect(left=450, top=350, width=500, height=500)])

    def test_mouse_wheel_resizes_active_mode_one_preview(self):
        capture = FakeCapture()
        overlay = FakeOverlay()
        controller = OcrVoiceController(
            AppConfig(mode=1, box_width=500, box_height=500, show_overlay=True),
            capture,
            FakeOcr("text"),
            FakeTts(),
            overlay=overlay,
        )

        controller.on_right_click_pressed(700, 600)
        controller.on_scroll(700, 600, 1)
        controller.on_scroll(700, 600, -1)

        self.assertEqual(
            overlay.calls,
            [
                ("show", Rect(left=450, top=350, width=500, height=500)),
                ("update", Rect(left=430, top=330, width=540, height=540)),
                ("update", Rect(left=450, top=350, width=500, height=500)),
            ],
        )

    def test_selected_region_captures_and_speaks(self):
        capture = FakeCapture()
        ocr = FakeOcr(" 日本語\nテスト ")
        tts = FakeTts()
        controller = OcrVoiceController(
            AppConfig(min_selection_width=8, min_selection_height=8),
            capture,
            ocr,
            tts,
        )

        controller.process_selection(Rect(left=10, top=20, width=120, height=80))

        self.assertEqual(capture.rects, [Rect(left=10, top=20, width=120, height=80)])
        self.assertEqual(ocr.images, ["capture.png"])
        self.assertEqual(tts.spoken, ["日本語 テスト"])

    def test_tiny_selected_region_is_ignored(self):
        capture = FakeCapture()
        logger = FakeLogger()
        controller = OcrVoiceController(
            AppConfig(min_selection_width=8, min_selection_height=8),
            capture,
            FakeOcr("text"),
            FakeTts(),
            logger=logger,
        )

        controller.process_selection(Rect(left=10, top=20, width=7, height=80))

        self.assertEqual(capture.rects, [])
        self.assertEqual(logger.messages, ["Selection too small."])

    def test_empty_ocr_output_is_reported_without_tts(self):
        capture = FakeCapture()
        tts = FakeTts()
        logger = FakeLogger()
        controller = OcrVoiceController(
            AppConfig(),
            capture,
            FakeOcr(" \n "),
            tts,
            logger=logger,
        )

        controller.process_selection(Rect(left=10, top=20, width=120, height=80))

        self.assertEqual(len(capture.rects), 1)
        self.assertEqual(tts.spoken, [])
        self.assertEqual(logger.messages, ["No text recognized."])

    def test_selected_region_tts_error_is_reported(self):
        logger = FakeLogger()
        controller = OcrVoiceController(
            AppConfig(),
            FakeCapture(),
            FakeOcr("text"),
            FailingTts(),
            logger=logger,
        )

        controller.process_selection(Rect(left=10, top=20, width=120, height=80))

        self.assertEqual(logger.messages, ["TTS failed: voice unavailable"])


if __name__ == "__main__":
    unittest.main()
