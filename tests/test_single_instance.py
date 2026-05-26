import unittest

from ocr_voice.single_instance import SingleInstanceLock, instance_mutex_name


class FakeBackend:
    def __init__(self, *, already_running: bool):
        self.already_running = already_running
        self.closed = []

    def acquire(self, name):
        return object(), self.already_running

    def release(self, handle):
        self.closed.append(handle)


class SingleInstanceTests(unittest.TestCase):
    def test_mutex_name_is_stable_for_app(self):
        self.assertEqual(instance_mutex_name(), r"Local\OCRVoice.SingleInstance")

    def test_lock_acquires_when_no_existing_instance(self):
        backend = FakeBackend(already_running=False)

        lock = SingleInstanceLock(backend=backend)

        self.assertTrue(lock.acquire())
        lock.release()
        self.assertEqual(len(backend.closed), 1)

    def test_lock_rejects_when_existing_instance_owns_mutex(self):
        backend = FakeBackend(already_running=True)

        lock = SingleInstanceLock(backend=backend)

        self.assertFalse(lock.acquire())
        self.assertEqual(len(backend.closed), 1)


if __name__ == "__main__":
    unittest.main()
