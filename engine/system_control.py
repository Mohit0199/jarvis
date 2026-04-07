"""
engine/system_control.py
PC system controls: volume, screenshot, battery, shutdown/restart.
Uses pyautogui (already installed) + psutil (new).
"""

import os
import time
import psutil
import pyautogui
from engine.command import speak


# ─── Volume Controls ───

def volume_up(steps: int = 5):
    """Increases system volume by `steps` key presses."""
    for _ in range(steps):
        pyautogui.press("volumeup")
    speak("Volume up, Mohit.")


def volume_down(steps: int = 5):
    """Decreases system volume by `steps` key presses."""
    for _ in range(steps):
        pyautogui.press("volumedown")
    speak("Turned it down a notch.")


def mute_volume():
    """Toggles mute."""
    pyautogui.press("volumemute")
    speak("Muted.")


# ─── Screenshot ───

def take_screenshot():
    """Takes a screenshot and saves to a local folder."""
    try:
        # Save to a generic relative directory in the project
        save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "screenshots")
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        filename = f"jarvis_screenshot_{int(time.time())}.png"
        filepath = os.path.join(save_dir, filename)
        screenshot = pyautogui.screenshot()
        screenshot.save(filepath)
        speak("Screenshot taken.")
        print(f"📸 Screenshot saved: {filepath}")
    except Exception as e:
        speak("Screenshot failed. Sorry about that.")
        print(f"❌ Screenshot error: {e}")


# ─── Battery ───

def battery_status():
    """Reports battery percentage and charging status."""
    try:
        battery = psutil.sensors_battery()
        if battery is None:
            speak("I can't detect a battery — you might be on a desktop, Mohit.")
            return
        percent = int(battery.percent)
        charging = battery.power_plugged

        if charging:
            speak(f"Battery is at {percent} percent and currently charging.")
        elif percent <= 15:
            speak(f"Battery is critically low at {percent} percent. Plug in now, Mohit!")
        elif percent <= 30:
            speak(f"Battery is at {percent} percent — getting low.")
        else:
            speak(f"Battery is at {percent} percent. You're good.")

        print(f"🔋 Battery: {percent}% | Charging: {charging}")
    except Exception as e:
        speak("Couldn't read battery status.")
        print(f"❌ Battery error: {e}")


# ─── System Power ───

def shutdown_pc():
    """Shuts down the PC after a brief delay."""
    speak("Shutting down in 5 seconds. Goodbye, Mohit.")
    time.sleep(5)
    os.system("shutdown /s /t 1")


def restart_pc():
    """Restarts the PC after a brief delay."""
    speak("Restarting in 5 seconds. I'll be right back.")
    time.sleep(5)
    os.system("shutdown /r /t 1")
