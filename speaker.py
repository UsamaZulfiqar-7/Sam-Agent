# speaker.py
# SAM ka bolne wala hissa (offline TTS - pyttsx3)

import pyttsx3
from config import VOICE_RATE, VOICE_VOLUME

engine = None


def _get_engine():
    global engine
    if engine is None:
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', VOICE_RATE)
            engine.setProperty('volume', VOICE_VOLUME)
        except Exception as exc:
            print(f"TTS init error: {exc}")
            engine = False
    return engine


def speak(text: str):
    """SAM ko yeh text bolwane ke liye"""
    if not isinstance(text, str) or not text.strip():
        return

    print(f"[SAM] {text}")
    tts_engine = _get_engine()
    if not tts_engine:
        return
    try:
        tts_engine.say(text)
        tts_engine.runAndWait()
    except Exception as exc:
        print(f"TTS error: {exc}")