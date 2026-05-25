import unittest
from unittest.mock import patch

from ocr_voice.process import run_hidden


class ProcessTests(unittest.TestCase):
    def test_run_hidden_uses_create_no_window_on_windows(self):
        with patch("ocr_voice.process.os.name", "nt"), patch(
            "ocr_voice.process.subprocess.run"
        ) as run:
            run_hidden(["powershell", "-Command", "echo ok"], check=True)

        self.assertEqual(run.call_args.kwargs["creationflags"], 0x08000000)
        self.assertTrue(run.call_args.kwargs["check"])

    def test_run_hidden_preserves_explicit_creationflags(self):
        with patch("ocr_voice.process.os.name", "nt"), patch(
            "ocr_voice.process.subprocess.run"
        ) as run:
            run_hidden(["tool"], creationflags=123)

        self.assertEqual(run.call_args.kwargs["creationflags"], 123)


if __name__ == "__main__":
    unittest.main()
