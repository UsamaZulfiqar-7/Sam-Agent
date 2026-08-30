from __future__ import annotations
# listener.py (VOSK / OFFLINE VERSION)
# SAM ka sunne wala hissa — ab poori tarah OFFLINE chalta hai (Vosk engine).
# Koi internet dependency nahi speech-to-text ke liye — Google API ka network
# issue is version mein bilkul nahi aayega.
#
# SETUP (ek baar ka kaam):
# 1. pip install vosk pyaudio
# 2. Model download karo: https://alphacephei.com/vosk/models
#    "vosk-model-small-en-us-0.15" (~40MB) download karo, ZIP extract karo,
#    aur extracted folder ka path neeche VOSK_MODEL_PATH mein set karo.

import os
import json
import time
import struct

from config import LISTEN_TIMEOUT, PHRASE_TIME_LIMIT, VOSK_MODEL_PATH
print(">>> LISTENER.PY (VOSK VERSION) — MODULE LOADED <<<", flush=True)

# ============================================================
# CONFIG
# ============================================================

SAMPLE_RATE = 16000
CHUNK = 4000

# Silence detection settings (VAD-lite): itni der silence rehne par capture
# stop kar dete hain (agar kuch bola ja chuka ho)
SILENCE_AMPLITUDE_THRESHOLD = 30  # Lowered from 300 to 30 so soft speech is picked up
SILENCE_DURATION_TO_STOP = 1.2  # seconds

_model = None
_recognizer_class = None
_cached_device_index = None
_startup_done = False


def _load_model():
    """Vosk model ek baar load karta hai (baar baar load karna slow hota)."""
    global _model
    if _model is not None:
        return _model

    if not os.path.isdir(VOSK_MODEL_PATH):
        print(f"[SAM][ERROR] Vosk model nahi mila: {VOSK_MODEL_PATH}")
        print("[SAM][ERROR] https://alphacephei.com/vosk/models se model download "
              "karo aur VOSK_MODEL_PATH set karo (config ya environment variable se).")
        return None

    try:
        import vosk
        vosk.SetLogLevel(-1)  # vosk ki apni verbose logging band karo
        _model = vosk.Model(VOSK_MODEL_PATH)
        print(f"[SAM] Vosk model load ho gaya: {VOSK_MODEL_PATH}")
        return _model
    except Exception as exc:
        print(f"[SAM][ERROR] Vosk model load nahi ho saka: {exc}")
        return None


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


def _get_device_index():
    """Best microphone device index dhoondta hai (pyaudio ke through)."""
    global _cached_device_index

    _startup_diagnostics()

    if _cached_device_index is not None:
        return _cached_device_index

    import pyaudio

    preferred_index = os.getenv("SAM_MICROPHONE_INDEX")
    if preferred_index:
        try:
            idx = int(preferred_index)
            _cached_device_index = idx
            print(f"Using configured mic index: {idx}")
            return idx
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
                return i

        if candidates:
            i, info, channels = candidates[0]
            _cached_device_index = i
            print(f">> Selected mic (multi-ch): [{i}] {info['name']} ({channels}ch)")
            return i

        default_info = pa.get_default_input_device_info()
        if default_info and "index" in default_info:
            idx = int(default_info["index"])
            _cached_device_index = idx
            print(f">> Using default device: [{idx}] {default_info.get('name')}")
            return idx
    except Exception as exc:
        print(f"[SAM][ERROR] Mic device lookup failed: {exc}")
    finally:
        pa.terminate()

    return None


def _amplitude(chunk_bytes: bytes) -> int:
    if not chunk_bytes:
        return 0
    count = len(chunk_bytes) // 2
    if count == 0:
        return 0
    samples = struct.unpack(f"<{count}h", chunk_bytes[:count * 2])
    return max(abs(s) for s in samples)


def listen(timeout=LISTEN_TIMEOUT, phrase_time_limit=PHRASE_TIME_LIMIT, verbose=True):
    """
    Mic se audio record karke Vosk (offline) se text mein convert karta hai.
    Kuch na suna to None return karega.
    """
    model = _load_model()
    if model is None:
        return None

    device_index = _get_device_index()
    if device_index is None:
        print("[SAM][ERROR] Koi microphone device nahi mila.")
        return None

    try:
        import pyaudio
        import vosk
    except ImportError as exc:
        print(f"[SAM][ERROR] Missing package: {exc}. 'pip install vosk pyaudio' chalao.")
        return None

    recognizer = vosk.KaldiRecognizer(model, SAMPLE_RATE)
    pa = pyaudio.PyAudio()

    # Determine max channels supported by the selected device
    try:
        dev_info = pa.get_device_info_by_index(device_index)
        max_ch = int(dev_info.get("maxInputChannels", 1))
    except Exception:
        max_ch = 1

    stream = None
    stream_channels = 1
    # Try opening 1 channel first, then fallback to device native channels if needed
    for ch in [1, max_ch] if max_ch > 1 else [1]:
        try:
            stream = pa.open(
                format=pyaudio.paInt16,
                channels=ch,
                rate=SAMPLE_RATE,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=CHUNK,
            )
            stream_channels = ch
            break
        except Exception:
            continue

    if stream is None:
        print(f"[SAM][ERROR] Mic stream open nahi ho saka (device index {device_index}).")
        pa.terminate()
        return None

    if verbose:
        print("  (listening — offline mode, Vosk...)")

    start_time = time.time()
    last_speech_time = None
    heard_any_speech = False
    max_duration = max(timeout if timeout is not None else 5, phrase_time_limit, 5)

    try:
        while True:
            elapsed = time.time() - start_time
            if elapsed > max_duration:
                break

            raw_data = stream.read(CHUNK, exception_on_overflow=False)
            
            # If multi-channel stream opened, extract mono (channel 0)
            if stream_channels > 1:
                count = len(raw_data) // (2 * stream_channels)
                if count > 0:
                    samples = struct.unpack(f"<{count * stream_channels}h", raw_data[:count * 2 * stream_channels])
                    mono_samples = samples[::stream_channels]
                    data = struct.pack(f"<{count}h", *mono_samples)
                else:
                    data = raw_data
            else:
                data = raw_data

            amp = _amplitude(data)

            if amp > SILENCE_AMPLITUDE_THRESHOLD:
                heard_any_speech = True
                last_speech_time = time.time()

            recognizer.AcceptWaveform(data)

            # Agar speech ho chuki hai aur ab thodi der se silence hai, capture khatam karo
            if heard_any_speech and last_speech_time is not None:
                if time.time() - last_speech_time > SILENCE_DURATION_TO_STOP:
                    break
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()

    result = json.loads(recognizer.FinalResult())
    text = result.get("text", "").strip()

    if text:
        print(f"[Aap] {text}")
        return text.lower().strip()

    if not heard_any_speech and verbose:
        print("[SAM][INFO] Kuch awaaz nahi aayi (silence/timeout).")
    elif verbose:
        print("[SAM][INFO] Awaaz aayi lekin samajh nahi payi (unclear speech).")

    return None


def listen_for_wake_word(wake_word: str):
    """
    Continuously sunta rehta hai jab tak wake word ('friend') na bola jaye.
    """
    try:
        text = listen(timeout=5, phrase_time_limit=4, verbose=False)
    except Exception as exc:
        print(f"[SAM][ERROR] Wake-word listening error: {exc}")
        return False

    if not text:
        return False

    w = wake_word.lower().strip()
    # 'friend' ke phonetic / common variations check karte hain:
    phonetic_variations = {w, "friend", "friends", "frend", "fred", "hey friend", "hi friend", "hello friend"}

    words = set(text.split())
    if w in text or any(v in words for v in phonetic_variations):
        return True

    print(f"[SAM][INFO] Kuch suna lekin wake word '{wake_word}' nahi tha: '{text}'")
    return False

