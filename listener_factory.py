# listener_factory.py
# SAM Gateway Listener — Dynamically routes to Vosk (offline) or Google (online)
# based on config.STT_ENGINE, with automatic fallback if Vosk model is unavailable.

import config
import listener as vosk_listener
import listener_google as google_listener

_vosk_available = None


def check_vosk_availability() -> bool:
    """Checks if Vosk model can be successfully loaded."""
    global _vosk_available
    if _vosk_available is not None:
        return _vosk_available

    model = vosk_listener._load_model()
    _vosk_available = model is not None
    return _vosk_available


def listen(timeout=None, phrase_time_limit=None, verbose=True):
    """
    Delegates listen() call to selected STT engine with automatic fallback.
    """
    if timeout is None:
        timeout = config.LISTEN_TIMEOUT
    if phrase_time_limit is None:
        phrase_time_limit = config.PHRASE_TIME_LIMIT

    engine = config.STT_ENGINE

    if engine == "vosk":
        if check_vosk_availability():
            res = vosk_listener.listen(timeout=timeout, phrase_time_limit=phrase_time_limit, verbose=verbose)
            if res is not None:
                return res
        else:
            if verbose:
                print("[SAM][WARNING] Vosk model load nahi hua; Google STT fallback use ho raha hai.")
            return google_listener.listen(timeout=timeout, phrase_time_limit=phrase_time_limit, verbose=verbose)
    
    # Default / Google Engine
    return google_listener.listen(timeout=timeout, phrase_time_limit=phrase_time_limit, verbose=verbose)


def listen_for_wake_word(wake_word: str):
    """
    Delegates wake word polling to selected STT engine with automatic fallback.
    """
    engine = config.STT_ENGINE

    if engine == "vosk":
        if check_vosk_availability():
            return vosk_listener.listen_for_wake_word(wake_word)
        else:
            return google_listener.listen_for_wake_word(wake_word)
    
    return google_listener.listen_for_wake_word(wake_word)
