# setloglevel_test.py
# Yeh check karta hai ke vosk.SetLogLevel(-1) ke baad Python ke apne print()
# statements kaam karte hain ya nahi.

import os

path = os.environ.get("VOSK_MODEL_PATH", "")
print("A. Test shuru, path:", path)

import vosk
print("B. vosk import ho gaya, yeh line dikh rahi hai na?")

vosk.SetLogLevel(-1)
print("C. SetLogLevel(-1) call ho gaya, YEH LINE DIKH RAHI HAI YA GHAYAB HO GAYI?")

model = vosk.Model(path)
print("D. Model load ho gaya, YEH LINE BHI DIKHNI CHAHIYE.")

print("E. TEST COMPLETE")
