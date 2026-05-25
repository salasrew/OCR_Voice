import unittest

from ocr_voice.ocr import AutoOcrService, CommandOcrService, OcrCommandError


class OcrTests(unittest.TestCase):
    def test_missing_ocr_command_raises_clear_error(self):
        service = CommandOcrService(["missing-ocr-command-for-test", "{image}"])

        with self.assertRaises(OcrCommandError) as context:
            service.recognize("capture.png")

        self.assertIn("missing-ocr-command-for-test", str(context.exception))

    def test_auto_ocr_uses_microsoft_ocr_first(self):
        calls = []

        class FakeMicrosoftOcr:
            def recognize(self, image_path):
                calls.append(("microsoft", image_path))
                return "日本語"

        service = AutoOcrService(
            command=["unused-command", "{image}"],
            microsoft_factory=lambda: FakeMicrosoftOcr(),
        )

        self.assertEqual(service.recognize("capture.png"), "日本語")
        self.assertEqual(calls, [("microsoft", "capture.png")])

    def test_auto_ocr_falls_back_to_command_when_microsoft_fails(self):
        class FailingMicrosoftOcr:
            def recognize(self, image_path):
                raise OcrCommandError("Microsoft OCR failed")

        class FakeCommandOcr:
            def __init__(self, command):
                self.command = command

            def recognize(self, image_path):
                return f"{self.command[0]}:{image_path}"

        service = AutoOcrService(
            command=["ocr-cli", "{image}"],
            microsoft_factory=lambda: FailingMicrosoftOcr(),
            command_factory=FakeCommandOcr,
        )

        self.assertEqual(service.recognize("capture.png"), "ocr-cli:capture.png")

    def test_auto_ocr_reports_microsoft_setup_when_no_fallback_exists(self):
        class FailingMicrosoftOcr:
            def recognize(self, image_path):
                raise OcrCommandError("Japanese OCR language is unavailable")

        service = AutoOcrService(
            command=None,
            microsoft_factory=lambda: FailingMicrosoftOcr(),
        )

        with self.assertRaises(OcrCommandError) as context:
            service.recognize("capture.png")

        self.assertIn("Microsoft OCR failed", str(context.exception))
        self.assertIn("Japanese OCR language is unavailable", str(context.exception))
        self.assertIn("ocr_command", str(context.exception))


if __name__ == "__main__":
    unittest.main()
