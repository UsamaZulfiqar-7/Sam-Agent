# net_test.py
# Yeh check karta hai ke Python internet (Google) tak pohanch sakta hai ya nahi.
# Agar yeh fail ho, to Windows Firewall/Antivirus Python ko block kar raha hai.

import urllib.request

try:
    resp = urllib.request.urlopen("https://www.google.com", timeout=10)
    print(f"SUCCESS! Status code: {resp.status}")
    print("Python internet tak pohanch sakta hai. Speech recognition ka masla kahin aur hai.")
except Exception as exc:
    print(f"FAILED: {exc}")
    print("Python internet tak nahi pohanch pa raha — Firewall/Antivirus check karo.")