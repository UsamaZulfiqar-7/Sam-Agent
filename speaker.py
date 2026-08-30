# speaker.py
# SAM ka bolne wala hissa (offline TTS - pyttsx3)

import pyttsx3
import threading
import queue
from config import VOICE_RATE, VOICE_VOLUME

_speech_queue = queue.Queue()
_engine = None
_speaker_thread = None
_lock = threading.Lock()


def _init_engine():
    global _engine
    if _engine is None:
        try:
            _engine = pyttsx3.init()
            _engine.setProperty("rate", VOICE_RATE)
            _engine.setProperty("volume", VOICE_VOLUME)
        except Exception as exc:
            print(f"[SAM][ERROR] TTS engine init failed: {exc}")
            _engine = False
    return _engine


def _process_queue():
    """Worker thread loop processing speech items in queue."""
    engine = _init_engine()
    if not engine:
        return

    while True:
        text = _speech_queue.get()
        if text is None:
            break
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as exc:
            print(f"[SAM][ERROR] TTS playback error: {exc}")
        finally:
            _speech_queue.task_done()


def speak(text: str, wait: bool = True):
    """
    SAM ko text bolwane ke liye.
    wait=True: Sync playback (subsequent audio processing waits until spoken)
    wait=False: Async background playback via queue
    """
    if not isinstance(text, str) or not text.strip():
        return

    print(f"[SAM] {text}")
    engine = _init_engine()
    if not engine:
        return

    if wait:
        with _lock:
            try:
                engine.say(text)
                engine.runAndWait()
            except Exception as exc:
                print(f"[SAM][ERROR] TTS speak error: {exc}")
    else:
        global _speaker_thread
        if _speaker_thread is None or not _speaker_thread.is_alive():
            _speaker_thread = threading.Thread(target=_process_queue, daemon=True)
            _speaker_thread.start()
        _speech_queue.put(text)