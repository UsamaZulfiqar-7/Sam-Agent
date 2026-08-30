from __future__ import annotations
# brain.py
# Yahan decide hota hai ke command ka matlab kya hai aur konsi action call honi chahiye.
# Pehle simple rule-based matching try hoti hai (fast, offline, free).
# Agar kuch samajh na aaye aur ANTHROPIC_API_KEY set ho, to Claude se madad li jati hai (optional).

import re
import os
import actions
from config import APP_PATHS, WEBSITES, USER_NAME, ASSISTANT_NAME, WAKE_WORD

def is_direct_command(text: str) -> bool:
    """Checks if input text is a known direct action command."""
    if not text:
        return False
    t = text.lower().strip()
    wake = WAKE_WORD.lower()
    
    keywords = [
        "open", "khol", "start", "time", "date", "tareekh", "youtube",
        "search", "dhoondo", "screenshot", "volume", "lock", "shutdown",
        "cancel", "find file", "file dhoondo", "exit", "band ho jao", "bye", "stop", "hello", "hi", "salam"
    ]
    return any(kw in t for kw in keywords)


def handle_command(text: str) -> tuple[str, bool]:

    """
    text: user ne jo bola (already lowercase)
    Returns: (response_text, should_exit)
    """
    if not text:
        return "Mujhe kuch sunayi nahi diya.", False

    t = text.lower().strip()
    wake = WAKE_WORD.lower()

    # ---- Exit commands ----
    if any(w in t for w in ["exit", "band ho jao", "bye", f"shutdown {wake}", "stop listening"]):
        return "Theek hai, phir milte hain!", True

    # ---- Greetings ----
    if any(w in t for w in ["hello", f"hi {wake}", f"hey {wake}", "salam"]):
        return f"Salam {USER_NAME}! Kya karu aapke liye?", False

    # ---- Time / Date ----
    if ("time" in t and "kya" in t) or t.strip() in ["time", "what time is it"]:
        return actions.tell_time(), False
    if "date" in t or "tareekh" in t:
        return actions.tell_date(), False


    # ---- Open app ----
    m = re.search(r"(open|khol|khol do|start)\s+(.+)", t)
    if m:
        target = m.group(2).strip()
        target = re.sub(r"\b(please|kar do|karo|do)\b", "", target).strip()

        if target in APP_PATHS:
            return actions.open_app(target), False
        if target in WEBSITES:
            return actions.open_website(target), False
        for app in APP_PATHS:
            if app in target:
                return actions.open_app(app), False
        for site in WEBSITES:
            if site in target:
                return actions.open_website(site), False
        if "\\" in target or "/" in target or ":" in target:
            return actions.open_file_or_folder(target), False
        return f"Mujhe '{target}' nahi pata kaise kholna hai. config.py mein add kar do.", False

    # ---- YouTube search (checked before generic web search) ----
    if "youtube" in t:
        query = re.sub(r"\b(youtube|pe|par|search|karo|play|chalao)\b", "", t).strip()
        if query:
            return actions.youtube_search(query), False
        return actions.open_website("youtube"), False

    # ---- Web search ----
    if "search" in t or "dhoondo" in t:
        query = re.sub(r"\b(search|for|google pe|on google|karo|dhoondo)\b", "", t).strip()
        if query:
            return actions.web_search(query), False

    # ---- Screenshot ----
    if "screenshot" in t:
        return actions.take_screenshot(), False

    # ---- Volume ----
    if "volume" in t:
        if "up" in t or "barhao" in t or "tez" in t:
            return actions.system_volume("up"), False
        if "down" in t or "kam" in t:
            return actions.system_volume("down"), False
        if "mute" in t:
            return actions.system_volume("mute"), False

    # ---- Lock PC ----
    if ("lock" in t and "pc" in t) or "lock kar" in t:
        return actions.lock_pc(), False

    # ---- Shutdown / Cancel shutdown ----
    if "cancel" in t and "shutdown" in t:
        return actions.cancel_shutdown(), False
    if "shutdown" in t or "band kar do computer" in t or "pc band" in t:
        return actions.shutdown_pc(30), False

    # ---- File search ----
    m = re.search(r"find file\s+(.+)|file dhoondo\s+(.+)|search file\s+(.+)", t)
    if m:
        fname = next(g for g in m.groups() if g)
        return actions.search_files(fname.strip()), False

    # ---- Fallback: try Claude API if key available ----
    api_response = try_claude_fallback(text)
    if api_response:
        return api_response, False

    return "Sorry, yeh command samajh nahi aayi. Thora clearly bolo ya alfaz change karo.", False


def try_claude_fallback(text: str):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=200,
            messages=[{
                "role": "user",
                "content": f"Tum '{ASSISTANT_NAME}' naam ka ek friendly Roman Urdu voice assistant ho. "
                            f"User ne yeh bola: '{text}'. Chota, natural, Roman Urdu mein jawab do (max 2 lines)."
            }]
        )
        return msg.content[0].text
    except Exception:
        return None