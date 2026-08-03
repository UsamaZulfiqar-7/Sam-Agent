import unittest
from unittest.mock import patch

import listener


class ListenerTests(unittest.TestCase):
    def test_listen_returns_none_when_microphone_is_unavailable(self):
        class BrokenMicrophone:
            def __init__(self, *args, **kwargs):
                raise OSError("No microphone available")

        with patch("listener.sr.Microphone", BrokenMicrophone):
            self.assertIsNone(listener.listen(timeout=0.1, phrase_time_limit=1))


if __name__ == "__main__":
    unittest.main()
