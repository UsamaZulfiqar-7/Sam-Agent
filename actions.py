# actions.py
# Yahan actual kaam perform hote hain - apps kholna, web search, system control, etc.

import os
import subprocess
import datetime
import webbrowser
import platform

from config import APP_PATHS, WEBSITES, SCREENSHOT_DIR

IS_WINDOWS = platform.system() == "Windows"


def open_app(app_name: str) -> str:
    app_name = app_name.lower().strip()
    path = APP_PATHS.get(app_name)
    if not path:
        return f"Mujhe '{app_name}' ka path nahi pata. config.py mein add kar do."
    try:
        expanded = os.path.expandvars(path)
        if IS_WINDOWS:
            os.startfile(expanded)
        else:
            subprocess.Popen(expanded)
        return f"{app_name} khol raha hoon."
    except Exception as e:
        return f"{app_name} khulne mein masla aa gaya: {e}"


def open_website(site_name: str) -> str:
    site_name = site_name.lower().strip()
    url = WEBSITES.get(site_name, None)
    if not url:
        if "." in site_name:
            url = "https://" + site_name.replace(" ", "")
        else:
            return f"Mujhe '{site_name}' website nahi pata."
    webbrowser.open(url)
    return f"{site_name} khol raha hoon."


def web_search(query: str) -> str:
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webbrowser.open(url)
    return f"'{query}' search kar raha hoon."


def youtube_search(query: str) -> str:
    url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    webbrowser.open(url)
    return f"YouTube pe '{query}' search kar raha hoon."


def take_screenshot() -> str:
    try:
        import pyautogui
        target_dir = os.path.expandvars(SCREENSHOT_DIR)
        os.makedirs(target_dir, exist_ok=True)
        filename = datetime.datetime.now().strftime("screenshot_%Y%m%d_%H%M%S.png")
        filepath = os.path.join(target_dir, filename)
        img = pyautogui.screenshot()
        img.save(filepath)
        return f"Screenshot save ho gaya: {filepath}"
    except Exception as e:
        return f"Screenshot lene mein masla: {e}"


def system_volume(action: str) -> str:
    """action: 'up', 'down', 'mute'"""
    try:
        import pyautogui
        if action == "up":
            for _ in range(5):
                pyautogui.press("volumeup")
            return "Volume barha diya."
        elif action == "down":
            for _ in range(5):
                pyautogui.press("volumedown")
            return "Volume kam kar diya."
        elif action == "mute":
            pyautogui.press("volumemute")
            return "Mute kar diya."
        return "Samajh nahi aaya volume ka kya karna hai."
    except Exception as e:
        return f"Volume control mein masla: {e}"


def tell_time() -> str:
    now = datetime.datetime.now().strftime("%I:%M %p")
    return f"Abhi time hai {now}"


def tell_date() -> str:
    today = datetime.datetime.now().strftime("%d %B, %Y")
    return f"Aaj ki date hai {today}"


def shutdown_pc(delay_sec=30) -> str:
    if not IS_WINDOWS:
        return "Yeh feature sirf Windows pe kaam karta hai."
    try:
        subprocess.run(["shutdown", "/s", "/t", str(int(delay_sec))], check=True)
        return f"PC {delay_sec} seconds mein shutdown ho jayega. Cancel karne ke liye 'shutdown cancel karo' bolo."
    except Exception as e:
        return f"Shutdown command execute nahi ho sakti: {e}"


def cancel_shutdown() -> str:
    if not IS_WINDOWS:
        return "Yeh feature sirf Windows pe kaam karta hai."
    try:
        subprocess.run(["shutdown", "/a"], check=True)
        return "Shutdown cancel kar diya."
    except Exception as e:
        return f"Shutdown cancel nahi ho saka: {e}"


def lock_pc() -> str:
    if not IS_WINDOWS:
        return "Yeh feature sirf Windows pe kaam karta hai."
    try:
        subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], check=True)
        return "PC lock kar raha hoon."
    except Exception as e:
        return f"PC lock nahi ho saka: {e}"


def _is_safe_path(path: str) -> bool:
    """Checks if path exists and prevents basic traversal attacks."""
    try:
        resolved = os.path.realpath(path)
        return os.path.exists(resolved)
    except Exception:
        return False


def open_file_or_folder(path: str) -> str:
    if not IS_WINDOWS:
        return "Yeh feature sirf Windows pe kaam karta hai."
    try:
        expanded = os.path.expandvars(os.path.expanduser(path))
        if not _is_safe_path(expanded):
            return f"Path nahi mila ya unsafe hai: {path}"
        os.startfile(expanded)
        return f"Khol raha hoon: {path}"
    except Exception as e:
        return f"Nahi khul saka: {e}"


def search_files(filename: str, search_dir: str = None, max_depth: int = 3) -> str:
    """User folder mein fast file search with depth limits and directory pruning."""
    if search_dir is None:
        search_dir = os.path.expanduser("~")
    
    EXCLUDE_DIRS = {"appdata", ".git", "node_modules", "$recycle.bin", "system volume information", "venv", "__pycache__"}
    matches = []
    base_depth = search_dir.rstrip(os.sep).count(os.sep)

    try:
        for root, dirs, files in os.walk(search_dir):
            # Prune excluded directories
            dirs[:] = [d for d in dirs if d.lower() not in EXCLUDE_DIRS]
            
            # Check current depth limit
            current_depth = root.count(os.sep) - base_depth
            if current_depth > max_depth:
                dirs[:] = []
                continue

            for f in files:
                if filename.lower() in f.lower():
                    matches.append(os.path.join(root, f))
                    if len(matches) >= 5:
                        break
            if len(matches) >= 5:
                break
    except Exception as e:
        return f"File search error: {e}"

    if matches:
        return "Mila:\n" + "\n".join(matches)
    return f"'{filename}' naam ki koi file nahi mili."