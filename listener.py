# listener.py
# SAM ka sunne wala hissa (microphone se speech-to-text)

import speech_recognition as sr
from config import LISTEN_TIMEOUT, PHRASE_TIME_LIMIT

recognizer = sr.Recognizer()
recognizer.energy_threshold = 150
recognizer.dynamic_energy_threshold = True
recognizer.dynamic_energy_adjustment_damping = 0.15
recognizer.dynamic_energy_adjustment_ratio = 1.5
recognizer.pause_threshold = 0.8
recognizer.non_speaking_duration = 0.5


def _log_microphone_state(source):
    """Print helpful microphone diagnostics when available."""
    try:
        if hasattr(source, "stream") and hasattr(source.stream, "sample_rate"):
            print(f"Microphone sample rate: {source.stream.sample_rate}")
    except Exception:
        pass


def _get_microphone():
    """Prefer the system default input device, then fall back to the first available microphone."""
    try:
        import os
        import pyaudio

        preferred_index = os.getenv("SAM_MICROPHONE_INDEX")
        if preferred_index:
            try:
                device_index = int(preferred_index)
                print(f"Using configured microphone device index: {device_index}")
                return sr.Microphone(device_index=device_index)
            except ValueError:
                print(f"Invalid SAM_MICROPHONE_INDEX value: {preferred_index}")

        pa = pyaudio.PyAudio()
        try:
            device_count = pa.get_device_count()
            preferred_names = ["microphone", "mic", "array", "capture", "input"]
            for index in range(device_count):
                info = pa.get_device_info_by_index(index)
                if not info or int(info.get("maxInputChannels", 0)) <= 0:
                    continue
                name = str(info.get("name") or "").lower()
                if any(token in name for token in preferred_names):
                    print(f"Using microphone device index: {index} ({info.get('name')})")
                    return sr.Microphone(device_index=index)

            default_info = pa.get_default_input_device_info()
            if default_info and "index" in default_info:
                device_index = int(default_info["index"])
                print(f"Using default microphone device index: {device_index}")
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
            if any(token in name.lower() for token in ["default", "array", "mic", "capture", "input"]):
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

    for attempt in range(2):
        try:
            with mic as source:
                _log_microphone_state(source)
                recognizer.adjust_for_ambient_noise(source, duration=0.3)
                if timeout is not None and timeout <= 0:
                    print("Listening timeout is zero; skipping capture.")
                    return None

                try:
                    audio = recognizer.listen(
                        source,
                        timeout=max(timeout if timeout is not None else 5, 3),
                        phrase_time_limit=max(phrase_time_limit, 5),
                    )
                except sr.WaitTimeoutError:
                    if attempt == 0:
                        print("No speech detected on first attempt; retrying once with a longer capture window.")
                        continue
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
