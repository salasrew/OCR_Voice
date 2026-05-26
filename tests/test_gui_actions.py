import unittest

from ocr_voice.gui_actions import UiActionQueue


class UiActionQueueTests(unittest.TestCase):
    def test_drain_runs_submitted_actions_in_order(self):
        calls = []
        actions = UiActionQueue()

        actions.submit(lambda: calls.append("show"))
        actions.submit(lambda: calls.append("help"))

        actions.drain()

        self.assertEqual(calls, ["show", "help"])


if __name__ == "__main__":
    unittest.main()
