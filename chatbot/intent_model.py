# intent_model.py
import os
import subprocess
import json
from vosk import Model, KaldiRecognizer
import sounddevice as sd
import queue
import threading
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import make_pipeline
import socket
import webbrowser

# -----------------------------
# 1. Train intent classifier
# -----------------------------
commands = [
    "shutdown system", "restart system", "sleep computer", "lock computer", "sign out user",
    "open downloads folder", "open documents folder", "open desktop folder", "open pictures folder", 
    "create new folder", "delete selected file", "rename file", "copy file", "move file",
    "open notepad", "open calculator", "open paint", "open word", "open excel", "open powerpoint",
    "open chrome", "open edge", "open firefox", "open command prompt", "open powershell",
    "play music", "pause music", "stop music", "next song", "previous song", "increase volume", "decrease volume", "mute volume",
    "open youtube", "open gmail", "open google", "refresh page", "open new tab", "close tab", "switch tab", "open facebook",
    "turn on wifi", "turn off wifi", "turn on bluetooth", "turn off bluetooth", "increase brightness", "decrease brightness",
    "change wallpaper", "enable dark mode", "disable dark mode",
    "minimize window", "maximize window", "close window", "switch window", "snap window left", "snap window right",
    "take screenshot", "open snipping tool", "open task manager", "check system info", "open device manager", "open control panel",
    "check ip address", "open network settings", "open sound settings", "open display settings",
]

labels = [
    "shutdown", "restart", "sleep", "lock", "signout",
    "open_downloads", "open_documents", "open_desktop", "open_pictures",
    "create_folder", "delete_file", "rename_file", "copy_file", "move_file",
    "open_notepad", "open_calc", "open_paint", "open_word", "open_excel", "open_ppt",
    "open_chrome", "open_edge", "open_firefox", "open_cmd", "open_powershell",
    "music_play", "music_pause", "music_stop", "music_next", "music_prev", "volume_up", "volume_down", "volume_mute",
    "browser_youtube", "browser_gmail", "browser_google", "browser_refresh", "browser_newtab", "browser_closetab", "browser_switchtab", "browser_facebook",
    "wifi_on", "wifi_off", "bt_on", "bt_off", "brightness_up", "brightness_down",
    "wallpaper_change", "darkmode_on", "darkmode_off",
    "win_minimize", "win_maximize", "win_close", "win_switch", "win_snap_left", "win_snap_right",
    "screenshot", "snipping_tool", "task_manager", "system_info", "device_manager", "control_panel",
    "ip_check", "network_settings", "sound_settings", "display_settings",
]

# Train model
model_clf = make_pipeline(TfidfVectorizer(), LinearSVC())
model_clf.fit(commands, labels)

# -----------------------------
# 2. Command Execution
# -----------------------------
def execute_command(intent: str) -> str:
    try:
        # ----------------- System -----------------
        if intent == "shutdown":
            os.system("shutdown /s /t 1")
            return "Shutdown triggered"
        elif intent == "restart":
            os.system("shutdown /r /t 1")
            return "Restart triggered"
        elif intent == "sleep":
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            return "Computer put to sleep"
        elif intent == "lock":
            os.system("rundll32.exe user32.dll,LockWorkStation")
            return "Computer locked"
        elif intent == "signout":
            os.system("shutdown /l")
            return "User signed out"

        # ----------------- File Explorer -----------------
        elif intent == "open_downloads":
            os.startfile(os.path.expanduser("~/Downloads"))
        elif intent == "open_documents":
            os.startfile(os.path.expanduser("~/Documents"))
        elif intent == "open_desktop":
            os.startfile(os.path.expanduser("~/Desktop"))
        elif intent == "open_pictures":
            os.startfile(os.path.expanduser("~/Pictures"))
        elif intent == "create_folder":
            new_path = os.path.join(os.getcwd(), "New Folder")
            os.makedirs(new_path, exist_ok=True)
            return f"Folder created at {new_path}"
        elif intent == "delete_file":
            # placeholder: deletes "sample.txt" in cwd
            if os.path.exists("sample.txt"):
                os.remove("sample.txt")
                return "sample.txt deleted"
            else:
                return "No file to delete"
        elif intent == "rename_file":
            if os.path.exists("old.txt"):
                os.rename("old.txt", "new.txt")
                return "File renamed"
            else:
                return "old.txt not found"
        elif intent == "copy_file":
            shutil.copy("source.txt", "copy.txt")
            return "File copied"
        elif intent == "move_file":
            shutil.move("move.txt", "moved.txt")
            return "File moved"

        # ----------------- Apps -----------------
        elif intent == "open_notepad":
            os.system("notepad.exe")
        elif intent == "open_calc":
            os.system("calc.exe")
        elif intent == "open_paint":
            os.system("mspaint.exe")
        elif intent == "open_word":
            os.system("start winword")
        elif intent == "open_excel":
            os.system("start excel")
        elif intent == "open_ppt":
            os.system("start powerpnt")

        # ----------------- Browsers -----------------
        elif intent == "open_chrome":
            os.system("start chrome")
        elif intent == "open_edge":
            os.system("start msedge")
        elif intent == "open_firefox":
            os.system("start firefox")
        elif intent == "browser_youtube":
            webbrowser.open("https://youtube.com")
        elif intent == "browser_gmail":
            webbrowser.open("https://mail.google.com")
        elif intent == "browser_google":
            webbrowser.open("https://google.com")
        elif intent == "browser_facebook":
            webbrowser.open("https://facebook.com")
        elif intent == "browser_refresh":
            return "Browser refresh (manual, cannot force)"
        elif intent == "browser_newtab":
            os.system("start chrome --new-tab")
        elif intent == "browser_closetab":
            return "Close tab (not supported programmatically)"
        elif intent == "browser_switchtab":
            return "Switch tab (not supported programmatically)"

        # ----------------- Command line -----------------
        elif intent == "open_cmd":
            os.system("start cmd")
        elif intent == "open_powershell":
            os.system("start powershell")

        # ----------------- Media -----------------
        elif intent == "music_play":
            subprocess.Popen(["start", "wmplayer"], shell=True)
            return "Music player started"
        elif intent == "music_pause":
            return "Music paused (requires media controller integration)"
        elif intent == "music_stop":
            return "Music stopped (requires media controller integration)"
        elif intent == "music_next":
            return "Next song (requires media controller integration)"
        elif intent == "music_prev":
            return "Previous song (requires media controller integration)"
        elif intent == "volume_up":
            os.system("nircmd.exe changesysvolume 5000")
        elif intent == "volume_down":
            os.system("nircmd.exe changesysvolume -5000")
        elif intent == "volume_mute":
            os.system("nircmd.exe mutesysvolume 2")

        # ----------------- Settings -----------------
        elif intent == "wifi_on":
            os.system("netsh interface set interface Wi-Fi enable")
        elif intent == "wifi_off":
            os.system("netsh interface set interface Wi-Fi disable")
        elif intent == "bt_on":
            return "Bluetooth ON (needs 3rd party API)"
        elif intent == "bt_off":
            return "Bluetooth OFF (needs 3rd party API)"
        elif intent == "brightness_up":
            return "Brightness up (needs WMI API)"
        elif intent == "brightness_down":
            return "Brightness down (needs WMI API)"
        elif intent == "wallpaper_change":
            return "Wallpaper changed (requires ctypes SPI call)"
        elif intent == "darkmode_on":
            os.system("reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize /v AppsUseLightTheme /t REG_DWORD /d 0 /f")
            return "Dark mode enabled"
        elif intent == "darkmode_off":
            os.system("reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize /v AppsUseLightTheme /t REG_DWORD /d 1 /f")
            return "Dark mode disabled"

        # ----------------- Window Mgmt -----------------
        elif intent == "win_minimize":
            return "Window minimized (requires pygetwindow/pyautogui)"
        elif intent == "win_maximize":
            return "Window maximized (requires pygetwindow/pyautogui)"
        elif intent == "win_close":
            return "Window closed (requires pygetwindow/pyautogui)"
        elif intent == "win_switch":
            return "Window switched (Alt+Tab simulation needed)"
        elif intent == "win_snap_left":
            return "Window snapped left (not directly possible)"
        elif intent == "win_snap_right":
            return "Window snapped right (not directly possible)"

        # ----------------- System Tools -----------------
        elif intent == "screenshot":
            os.system("snippingtool /clip")
            return "Screenshot captured"
        elif intent == "snipping_tool":
            os.system("snippingtool")
        elif intent == "task_manager":
            os.system("taskmgr")
        elif intent == "system_info":
            os.system("msinfo32")
        elif intent == "device_manager":
            os.system("devmgmt.msc")
        elif intent == "control_panel":
            os.system("control")
        elif intent == "ip_check":
            ip = socket.gethostbyname(socket.gethostname())
            return f"IP Address: {ip}"
        elif intent == "network_settings":
            os.system("ms-settings:network")
        elif intent == "sound_settings":
            os.system("ms-settings:sound")
        elif intent == "display_settings":
            os.system("ms-settings:display")

        else:
            return f"No action mapped for {intent}"

    except Exception as e:
        return f"Error executing {intent}: {e}"

# -----------------------------
# 3. Public API (text → intent → action)
# -----------------------------
def handle_text(text: str) -> dict:
    intent = model_clf.predict([text])[0]
    result = execute_command(intent)
    return {"text": text, "intent": intent, "result": result}

# -----------------------------
# 4. Example usage
# -----------------------------
if __name__ == "__main__":
    while True:
        user_inp = input("Command> ")
        if user_inp.lower() in ["quit", "exit"]:
            break
        response = handle_text(user_inp)
        print(response)
