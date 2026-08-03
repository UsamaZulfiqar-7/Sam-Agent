# listener.py
# SAM ka sunne wala hissa (microphone se speech-to-text)

import speech_recognition as sr
from config import LISTEN_TIMEOUT, PHRASE_TIME_LIMIT

recognizer = sr.Recognizer()
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True


def _get_microphone():
    """Prefer the system default input device, then fall back to the first available microphone."""
    try:
        import pyaudio

        pa = pyaudio.PyAudio()
        try:
            default_info = pa.get_default_input_device_info()
            if default_info and "index" in default_info:
                device_index = int(default_info["index"])
                print(f"Using microphone device index: {device_index}")
                return sr.Microphone(device_index=device_index)
        finally:
            pa.terminate()
    except Exception as exc:
        print(f"PyAudio device lookup failed: {exc}")

    try:
        mic_list = sr.Microphone.list_microphone_names()
        if not mic_list:
            return None
        for index, name in enumerate(mic_list):
            if "default" in name.lower() or "array" in name.lower() or "mic" in name.lower():
                print(f"Using fallback microphone device index: {index}")
                return sr.Microphone(device_index=index)
        return sr.Microphone(device_index=0)
    except Exception as exc:
        print(f"Microphone discovery error: {exc}")
        return None


def listen(timeout=LISTEN_TIMEOUT, phrase_time_limit=PHRASE_TIME_LIMIT):
    """
    Mic se audio record karke text mein convert karta hai.
    Kuch na suna to None return karega.
    """
    mic = _get_microphone()
    if mic is None:
        print("No microphone device detected.")
        return None

    try:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.2)
            if timeout is not None and timeout <= 0:
                print("Listening timeout is zero; skipping capture.")
                return None

            try:
                audio = recognizer.listen(
                    source,
                    timeout=timeout if timeout is not None else 5,
                    phrase_time_limit=phrase_time_limit,
                )
            except sr.WaitTimeoutError:
                print("No speech detected within timeout.")
                return None
            except OSError as exc:
                print(f"Mic capture error: {exc}")
                return None
    except OSError as exc:
        print(f"Mic setup error: {exc}")
        return None

    try:
        text = recognizer.recognize_google(audio, language="en-US")
        print(f"[Aap] {text}")
        return text.lower().strip() if text else None
    except sr.UnknownValueError:
        return None
    except sr.RequestError as exc:
        print(f"Internet connection check karo — speech recognition ke liye internet chahiye: {exc}")
        return None
    except Exception as exc:
        print(f"Speech recognition error: {exc}")
        return None


def listen_for_wake_word(wake_word: str):
    """
    Continuously sunta rehta hai jab tak wake word ('sam') na bole jaye.
    """
    try:
        text = listen(timeout=3, phrase_time_limit=3)
    except Exception as exc:
        print(f"Wake-word listening error: {exc}")
        return False

    if text and wake_word in text:
        return True
    return False
