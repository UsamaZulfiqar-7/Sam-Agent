import unittest
from unittest.mock import patch

import listener
import speech_recognition as sr


class ListenerTests(unittest.TestCase):
    def test_listen_returns_none_when_microphone_is_unavailable(self):
        class BrokenMicrophone:
            def __init__(self, *args, **kwargs):
                raise OSError("No microphone available")

        with patch("listener.sr.Microphone", BrokenMicrophone):
            self.assertIsNone(listener.listen(timeout=0.1, phrase_time_limit=1))

    def test_listen_retries_once_after_initial_timeout(self):
        class FakeSource:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        with patch("listener._get_microphone", return_value=FakeSource()), patch("listener.recognizer.adjust_for_ambient_noise"), patch("listener.recognizer.listen", side_effect=[sr.WaitTimeoutError(), "audio"]), patch("listener.recognizer.recognize_google", return_value="hello world") as mock_recognize:
            result = listener.listen(timeout=1, phrase_time_limit=2)

        self.assertEqual(result, "hello world")
        self.assertEqual(mock_recognize.call_count, 1)


if __name__ == "__main__":
    unittest.main()
