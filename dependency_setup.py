import subprocess
import sys
from pathlib import Path
from typing import Optional


def get_pyaudio_install_help(platform_name: Optional[str] = None) -> str:
    """Return a Windows-safe install hint for PyAudio."""
    platform_name = platform_name or sys.platform
    if platform_name.startswith("win"):
        return (
            "PyAudio installation via pipwin is not recommended here because pipwin can be blocked by Windows Application Control.\n"
            "Try: py -m pip install pyaudio\n"
            "If that still fails, install a wheel that matches your Python version from "
            "https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio"
        )
    return "Try: python -m pip install pyaudio"


def install_requirements(requirements_path: Optional[str] = None) -> int:
    """Install project requirements without relying on pipwin."""
    requirements_path = Path(requirements_path or "requirements.txt")
    python_executable = sys.executable

    try:
        subprocess.check_call([python_executable, "-m", "pip", "install", "pyaudio"])
    except subprocess.CalledProcessError as exc:
        print(get_pyaudio_install_help())
        return exc.returncode

    try:
        subprocess.check_call([python_executable, "-m", "pip", "install", "-r", str(requirements_path)])
    except subprocess.CalledProcessError as exc:
        return exc.returncode

    return 0


if __name__ == "__main__":
    raise SystemExit(install_requirements())
