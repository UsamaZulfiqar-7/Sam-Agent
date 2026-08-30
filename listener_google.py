# listener.py
# SAM ka sunne wala hissa (microphone se speech-to-text)

import speech_recognition as sr
from config import LISTEN_TIMEOUT, PHRASE_TIME_LIMIT

recognizer = sr.Recognizer()
recognizer.energy_threshold = 100  # Lowered to 100 for soft mics
recognizer.dynamic_energy_threshold = True
recognizer.dynamic_energy_adjustment_damping = 0.15
recognizer.dynamic_energy_adjustment_ratio = 1.3
recognizer.pause_threshold = 0.8
recognizer.non_speaking_duration = 0.5


_cached_device_index = None
_startup_done = False


def _startup_diagnostics():
    global _startup_done
    if _startup_done:
        return
    _startup_done = True
    try:
        import pyaudio
        pa = pyaudio.PyAudio()
        try:
            print("\n=== Available Input Devices ===")
            for i in range(pa.get_device_count()):
                info = pa.get_device_info_by_index(i)
                if int(info.get("maxInputChannels", 0)) > 0:
                    print(f"  [{i}] {info['name']}  (channels={info.get('maxInputChannels')})")
            print("===============================")
            print("TIP: Agar galat mic select ho raha hai to environment variable set karo:")
            print("     set SAM_MICROPHONE_INDEX=<number>\n")
        finally:
            pa.terminate()
    except Exception:
        pass


def _get_microphone():
    global _cached_device_index
    _startup_diagnostics()

    if _cached_device_index is not None:
        return sr.Microphone(device_index=_cached_device_index)

    try:
        import os
        import pyaudio

        preferred_index = os.getenv("SAM_MICROPHONE_INDEX")
        if preferred_index:
            try:
                idx = int(preferred_index)
                _cached_device_index = idx
                print(f"Using configured mic index: {idx}")
                return sr.Microphone(device_index=idx)
            except ValueError:
                print(f"Invalid SAM_MICROPHONE_INDEX: {preferred_index}")

        pa = pyaudio.PyAudio()
        try:
            skip_names = ["sound mapper", "loopback", "stereo mix", "what u hear", "pc speaker"]
            real_mic_names = ["microphone", "mic array", "headset", "webcam", "frontmic"]

            candidates = []
            for i in range(pa.get_device_count()):
                info = pa.get_device_info_by_index(i)
                channels = int(info.get("maxInputChannels", 0))
                if channels <= 0:
                    continue
                name = str(info.get("name", "")).lower()
                if any(s in name for s in skip_names):
                    continue
                if any(r in name for r in real_mic_names):
                    candidates.append((i, info, channels))

            for i, info, channels in candidates:
                if channels <= 2:
                    _cached_device_index = i
                    print(f">> Selected mic: [{i}] {info['name']} ({channels}ch)")
                    return sr.Microphone(device_index=i)

            if candidates:
                i, info, channels = candidates[0]
                _cached_device_index = i
                print(f">> Selected mic (multi-ch): [{i}] {info['name']} ({channels}ch)")
                return sr.Microphone(device_index=i)

            try:
                default_info = pa.get_default_input_device_info()
                if default_info and "index" in default_info:
                    idx = int(default_info["index"])
                    _cached_device_index = idx
                    print(f">> Using default device: [{idx}] {default_info.get('name')}")
                    return sr.Microphone(device_index=idx)
            except (IOError, OSError):
                pass

            for i in range(pa.get_device_count()):
                info = pa.get_device_info_by_index(i)
                if int(info.get("maxInputChannels", 0)) <= 0:
                    continue
                name = str(info.get("name", "")).lower()
                if any(s in name for s in skip_names):
                    continue
                _cached_device_index = i
                print(f">> Fallback device: [{i}] {info['name']}")
                return sr.Microphone(device_index=i)

            for i in range(pa.get_device_count()):
                info = pa.get_device_info_by_index(i)
                if int(info.get("maxInputChannels", 0)) > 0:
                    _cached_device_index = i
                    print(f">> Last resort device: [{i}] {info['name']}")
                    return sr.Microphone(device_index=i)

        finally:
            pa.terminate()
    except Exception as exc:
        print(f"PyAudio device lookup failed: {exc}")

    try:
        mic_list = sr.Microphone.list_microphone_names()
        if not mic_list:
            return None
        _cached_device_index = 0
        return sr.Microphone(device_index=0)
    except Exception as exc:
        print(f"Microphone discovery error: {exc}")
        return None


def listen(timeout=LISTEN_TIMEOUT, phrase_time_limit=PHRASE_TIME_LIMIT, verbose=True):
    """
    verbose=True: har outcome (timeout, silence, unclear, no-internet) print karega.
    """
    global _cached_device_index

    mic = _get_microphone()
    if mic is None:
        print("[SAM][ERROR] Koi microphone device mila hi nahi. PyAudio/driver check karo.")
        return None

    for attempt in range(2):
        try:
            with mic as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                if recognizer.energy_threshold < 100:
                    recognizer.energy_threshold = 100
                if verbose:
                    print(f"  (energy_threshold={recognizer.energy_threshold:.0f}, listening...)")

                if timeout is not None and timeout <= 0:
                    if verbose:
                        print("[SAM][INFO] Listening timeout is zero; skipping capture.")
                    return None

                try:
                    audio = recognizer.listen(
                        source,
                        timeout=max(timeout if timeout is not None else 5, 3),
                        phrase_time_limit=max(phrase_time_limit, 5),
                    )
                except sr.WaitTimeoutError:
                    if attempt == 0:
                        if verbose:
                            print("[SAM][INFO] Kuch awaaz nahi aayi (timeout). Dobara try...")
                        continue
                    if verbose:
                        print("[SAM][INFO] Dobara bhi kuch nahi suna. Mic ke bilkul paas, saaf bolo.")
                    return None
                except OSError as exc:
                    print(f"[SAM][ERROR] Mic capture error: {exc}")
                    return None
        except OSError as exc:
            print(f"[SAM][ERROR] Mic setup error: {exc}")
            _cached_device_index = None
            return None

        last_exc = None
        for lang in ("en-US", "en-IN"):
            try:
                text = recognizer.recognize_google(audio, language=lang)
                if text:
                    print(f"[Aap] {text}")
                    return text.lower().strip()
            except sr.UnknownValueError:
                last_exc = "unclear"
                continue
            except sr.RequestError as exc:
                print(f"[SAM][ERROR] Internet check karo — STT ke liye internet chahiye: {exc}")
                return None
            except Exception as exc:
                print(f"[SAM][ERROR] Speech recognition error: {exc}")
                return None

        if last_exc == "unclear" and verbose:
            print("[SAM][INFO] Awaaz aayi lekin samajh nahi payi (unclear speech). Saaf aur zaraa zor se bolo.")
        return None

    return None


def listen_for_wake_word(wake_word: str):
    try:
        text = listen(timeout=5, phrase_time_limit=4, verbose=False)
    except Exception as exc:
        print(f"[SAM][ERROR] Wake-word listening error: {exc}")
        return False

    if text and wake_word in text:
        return True
    if text:
        print(f"[SAM][INFO] Kuch suna lekin wake word '{wake_word}' nahi tha: '{text}'")
    return False