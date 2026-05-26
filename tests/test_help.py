import unittest

from ocr_voice.help_content import help_sections, help_text


class HelpContentTests(unittest.TestCase):
    def test_help_sections_cover_ocr_tts_and_capture_notes(self):
        sections = help_sections()

        self.assertEqual([section.title for section in sections], ["Japanese OCR", "Japanese TTS", "Capture Notes"])

        text = help_text()

        self.assertIn("Windows Japanese OCR language capability", text)
        self.assertIn("Japanese Windows voice", text)
        self.assertIn("Test Voice", text)
        self.assertIn("borderless-windowed", text)
        self.assertIn("Captured images are deleted", text)


if __name__ == "__main__":
    unittest.main()
