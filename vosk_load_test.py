# vosk_load_test.py
# Isolated test — sirf yeh check karta hai ke Vosk model load hota hai ya nahi,
# bina kisi doosri complexity ke.

import os
import sys

path = os.environ.get("VOSK_MODEL_PATH", "")
print(f"1. VOSK_MODEL_PATH environment variable: '{path}'")
print(f"2. Path exists as folder: {os.path.isdir(path)}")

if not os.path.isdir(path):
    print("STOP: Folder nahi mila is path par. Path check karo.")
    sys.exit(1)

print("3. Folder ke andar files/folders:")
try:
    for item in os.listdir(path):
        print(f"   - {item}")
except Exception as exc:
    print(f"   listdir error: {exc}")

print("4. Ab vosk import kar rahe hain...")
try:
    import vosk
    print(f"   vosk package version location: {vosk.__file__}")
except Exception as exc:
    print(f"   FAILED to import vosk: {exc}")
    sys.exit(1)

print("5. Ab model load kar rahe hain (isme 5-15 second lag sakte hain)...")
try:
    model = vosk.Model(path)
    print("6. SUCCESS! Model load ho gaya bina kisi masle ke.")
except Exception as exc:
    print(f"6. FAILED: Model load nahi ho saka: {exc}")
    sys.exit(1)

print("\n=== TEST COMPLETE — SAB THEEK HAI ===")
