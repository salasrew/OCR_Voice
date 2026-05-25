import unittest

from ocr_voice.tts import TtsService, build_powershell_speech_command, build_powershell_mp3_playback_command


class TtsTests(unittest.TestCase):
    def test_build_powershell_speech_command_escapes_single_quotes(self):
        command = build_powershell_speech_command("今日's 日本語")

        self.assertEqual(command[0], "powershell")
        self.assertIn("今日''s 日本語", command[-1])
        self.assertIn("System.Speech", command[-1])
        self.assertIn("SelectVoiceByHints", command[-1])

    def test_build_powershell_mp3_playback_command_uses_media_player(self):
        command = build_powershell_mp3_playback_command("C:/tmp/voice.mp3")

        self.assertEqual(command[0], "powershell")
        self.assertIn("PresentationCore", command[-1])
        self.assertIn("MediaPlayer", command[-1])

    def test_default_tts_tries_windows_speech_first(self):
        calls = []

        def windows_speech(text):
            calls.append(("windows", text))

        service = TtsService(speakers=(windows_speech,))

        service.speak("日本語")

        self.assertEqual(calls, [("windows", "日本語")])


if __name__ == "__main__":
    unittest.main()
