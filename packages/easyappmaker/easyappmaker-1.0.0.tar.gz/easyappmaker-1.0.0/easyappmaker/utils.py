import datetime
import os

def log(message: str):
    """Simple logger with timestamp"""
    time = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{time}] {message}")

def clear_console():
    """Clears the console screen."""
    os.system("cls" if os.name == "nt" else "clear")

def ask_user(prompt: str) -> str:
    """Gets input with a prompt and trims spaces."""
    return input(prompt + " ").strip()
