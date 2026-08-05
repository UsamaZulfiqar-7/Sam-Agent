# SAM — Apka Personal Voice Automation Agent 🎙️

SAM ek voice-controlled assistant hai jo tumhare Windows laptop pe commands sun kar
apps kholna, web search, system control (volume, lock, shutdown), screenshots,
file dhoondna jaisay kaam khud karta hai.

## Setup (Windows)

### 1. Python install karo
Python 3.9+ chahiye. [python.org](https://python.org) se download karo.
Install karte waqt **"Add Python to PATH"** ka checkbox zaroor tick karo.

### 2. Project files ek folder mein rakho
Sab files ek folder `SAM` mein rakho:
`main.py`, `brain.py`, `actions.py`, `listener.py`, `speaker.py`, `config.py`,
`dependency_setup.py`, `requirements.txt`, plus debug tools
(`temp_audio_check.py`, `test_all_mics.py`).

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
Do tareeqe hain:

**Option A — seedha requirements.txt:**
```
pip install -r requirements.txt
```

**Option B — dependency_setup.py use karo (pyaudio pehle, phir baqi sab):**
```
python dependency_setup.py
```
Yeh `pipwin` use nahi karta (jo Windows Application Control se block ho sakta hai), seedha
`pip install pyaudio` try karta hai. Agar wo bhi fail ho to yeh script tumhe ek wheel link
degi (lfd.uci.edu) jahan se apne Python version ke hisaab se pyaudio wheel download kar sakte ho.

### 6. Microphone check karo (recommended, run karne se pehle)
```
python test_all_mics.py
```
Yeh har mic ko har sample rate pe test karega aur batayega konsa "WORKING" hai.
Agar sab "silent" aayein to Windows Settings check karo (script khud steps bata degi).

Simple quick check ke liye:
```
python temp_audio_check.py
```

### 7. config.py update karo
`config.py` file kholo aur `APP_PATHS` mein apne actual installed apps ke paths daalo.
Path pata karne ke liye Command Prompt mein likho:
```
where chrome
```
ya app ka shortcut Right Click → Properties → "Target" field dekho.

### 8. Agar galat microphone select ho raha ho
`main.py` chalane se pehle SAM khud available mics list print karega. Agar wo galat
device select kare, to us list se sahi number lekar environment variable set karo:
```
set SAM_MICROPHONE_INDEX=2
python main.py
```

### 9. Run karo
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

## Fixed issues (is version mein)
- **listener.py**: mic error hone par cached device index reset nahi ho raha tha
  (`global` statement missing thi) — ab properly reset hota hai taake khraab mic
  dobara try na ho.
- **brain.py**: "hi azi" / "shutdown azi" jaisi purani hardcoded phrases thi jabke
  wake word "sam" hai — ab dynamically `config.py` ke `WAKE_WORD` se match hoti hain.
- **brain.py**: web search ka ek dead/unused regex line thi, hata di aur youtube
  vs. google search ki priority clear kar di.
- **actions.py**: `open_file_or_folder` Windows-only `os.startfile` use karta tha
  bina check kiye — ab IS_WINDOWS check add ki.

## Known limitations
- Internet chahiye speech recognition ke liye (Google Speech API use hoti hai)
- Wake word detection continuous mic listening use karta hai — thora CPU use hoga
- Kuch apps ke paths system-dependent hain, config.py mein update karna zaroori hai

## Future ideas
- Offline wake word detection (Porcupine / openWakeWord)
- Whisper (offline STT) taake Google API dependency khatam ho
- GUI overlay (system tray icon)
- Custom skills plugin system

## Contributors
- Ana Chahia Mera
