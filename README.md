# SAM — Apka Personal Voice Automation Agent 🎙️

SAM ek voice-controlled assistant hai jo tumhare Windows laptop pe commands sun kar
apps kholna, web search, system control (volume, lock, shutdown), screenshots,
file dhoondna jaisay kaam khud karta hai.

## Setup (Windows)

### 1. Python install karo
Python 3.9+ chahiye. [python.org](https://python.org) se download karo.
Install karte waqt **"Add Python to PATH"** ka checkbox zaroor tick karo.

### 2. Project files ek folder mein rakho
Sab files (`main.py`, `brain.py`, `actions.py`, `listener.py`, `speaker.py`,
`config.py`, `requirements.txt`) ek folder `SAM` mein rakho.

### 3. Command Prompt kholo us folder mein
```
cd path\to\SAM
```

### 4. Virtual environment (optional lekin recommended)
```
python -m venv venv
venv\Scripts\activate
```

### 5. Dependencies install karo
```
pip install -r requirements.txt
```

**Note:** `pyaudio` Windows pe kabhi kabhi direct install nahi hota. Agar error aaye to:
```
pip install pipwin
pipwin install pyaudio
```

### 6. config.py update karo
`config.py` file kholo aur `APP_PATHS` mein apne actual installed apps ke paths daalo.
Path pata karne ke liye Command Prompt mein likho:
```
where chrome
```
ya app ka shortcut Right Click → Properties → "Target" field dekho.

### 7. Run karo
```
python main.py
```

Ab "SAM" bolo, wo "Ji, boliye" bolega, phir apni command do — jese:
- "Chrome khol do"
- "YouTube pe lofi music search karo"
- "Screenshot le lo"
- "Volume up karo"
- "PC lock kar do"
- "Time kya hai"
- "Exit" — SAM ko band karne ke liye

## Optional: Smarter conversation (Claude API)
Agar chaho ke SAM thora zyada natural baat kare (jab koi built-in command match na ho),
to environment variable set kar do:
```
setx ANTHROPIC_API_KEY "your-api-key-here"
```
Phir naya Command Prompt kholo aur `python main.py` chalao.

## Naye commands add karna
`brain.py` mein `handle_command()` function ke andar naya `if` block add karo,
aur `actions.py` mein corresponding function likho. Structure simple hai —
har feature apna chota function hai jo actions.py mein rehta hai.

## Known limitations
- Internet chahiye speech recognition ke liye (Google Speech API use hoti hai)
- Wake word detection continuous mic listening use karta hai — thora CPU use hoga
- Kuch apps ke paths system-dependent hain, config.py mein update karna zaroori hai

## Future ideas (agar aage le jana ho)
- Offline wake word detection (Porcupine / openWakeWord) taake continuous internet na chahiye
- Whisper (offline STT) taake Google API dependency khatam ho
- GUI overlay (system tray icon)
- WhatsApp/Email automation
- Custom skills plugin system
