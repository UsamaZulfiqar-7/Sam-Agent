import os
from pathlib import Path

# STT Engine Selection: "vosk" (offline, default) ya "google" (online API)
STT_ENGINE = os.getenv("SAM_STT_ENGINE", "vosk").lower()

# Vosk Offline Model Path Resolution:
# 1. Check environment variable VOSK_MODEL_PATH
# 2. Check workspace relative folder 'vosk-model-small-en-us-0.15'
# 3. Fallback to C:\vosk-model-small-en-us-0.15
_BASE_DIR = Path(__file__).parent.resolve()
_LOCAL_VOSK_DIR = _BASE_DIR / "vosk-model-small-en-us-0.15"

if os.getenv("VOSK_MODEL_PATH"):
    VOSK_MODEL_PATH = os.getenv("VOSK_MODEL_PATH")
elif _LOCAL_VOSK_DIR.exists() and _LOCAL_VOSK_DIR.is_dir():
    VOSK_MODEL_PATH = str(_LOCAL_VOSK_DIR)
else:
    VOSK_MODEL_PATH = r"C:\vosk-model-small-en-us-0.15"

WAKE_WORD = "sam"          # Isko bolne se SAM activate hoga
ASSISTANT_NAME = "SAM"

# Agar tum chahte ho SAM tumhare naam se pukare tumhe
USER_NAME = "Sir"

# Voice settings
VOICE_RATE = 175           # bolne ki speed
VOICE_VOLUME = 1.0

# Kitni der tak "SAM" sunne ke baad wo command sunega (seconds)
LISTEN_TIMEOUT = 5
PHRASE_TIME_LIMIT = 8

# Common apps ke Windows paths (default install locations hain, apne hisaab se update karo)
APP_PATHS = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "vscode": r"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "word": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
    "excel": r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
    "explorer": "explorer.exe",
    "paint": "mspaint.exe",
    "task manager": "taskmgr.exe",
    "cmd": "cmd.exe",
    "spotify": r"C:\Users\%USERNAME%\AppData\Roaming\Spotify\Spotify.exe",
}

# Websites ke shortcuts
WEBSITES = {
    "youtube": "https://youtube.com",
    "gmail": "https://mail.google.com",
    "whatsapp": "https://web.whatsapp.com",
    "github": "https://github.com",
    "linkedin": "https://linkedin.com",
    "chatgpt": "https://chat.openai.com",
    "claude": "https://claude.ai",
}

# Screenshot save location
SCREENSHOT_DIR = r"C:\Users\%USERNAME%\Pictures\SAM_Screenshots"

# Optional: agar galat microphone select ho raha hai, environment variable set kar do
# (Windows CMD mein: set SAM_MICROPHONE_INDEX=2 )
# listener.py startup pe available devices ki list print kar deta hai taake sahi number pata chal sake.