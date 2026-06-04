import win32api
import win32gui
import ctypes
from PIL import ImageGrab
import socket_commands
import numpy as np
import psutil
import os
import pyautogui
import threading
import time

from overlay import FreezeOverlay, root

freeze_active = False
overlay = None
freeze_end_time = 0


def get_pid_from_hwnd(hwnd):
    pid = ctypes.c_ulong()
    ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return pid.value


def get_open_apps():
    apps = []
    def callback(hwnd, apps):
        if not win32gui.IsWindowVisible(hwnd):
            return True
        title = win32gui.GetWindowText(hwnd)
        if not title.strip():
            return True
        pid = get_pid_from_hwnd(hwnd)
        try:
            proc = psutil.Process(pid)
            apps.append({"pid": pid, "name": proc.name(), "title": title})
        except:
            pass
        return True
    win32gui.EnumWindows(callback, apps)
    return apps


def freeze():
    global freeze_active, overlay, freeze_end_time
    freeze_end_time = time.time() + 5
    if not freeze_active:
        freeze_active = True
        overlay = FreezeOverlay("images/capybara.png", "eyes on the teacher, not this screen")
        overlay.show()


def unfreeze():
    global freeze_active, overlay
    freeze_active = False
    if overlay is not None:
        overlay.hide()
        overlay = None


def freeze_loop():
    while True:
        if freeze_active:
            targets = [
                "GameBar.exe",
                "XboxGameBar.exe",
                "GameBarFTServer.exe",
                "GameBarPresenceWriter.exe"
            ]
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] in targets:
                    try:
                        proc.terminate()
                        proc.wait(timeout=1)
                    except:
                        pass

            os.system("powershell -command \"(New-Object -ComObject Shell.Application).MinimizeAll()\"")

            w, h = pyautogui.size()
            pyautogui.FAILSAFE = False
            pyautogui.moveTo(w - 1, 0, duration=0.05)

        time.sleep(0.05)


def freeze_watchdog():
    global freeze_active, freeze_end_time
    while True:
        if freeze_active and time.time() >= freeze_end_time:
            unfreeze()
        time.sleep(0.1)


def send_images():
    img = ImageGrab.grab()
    rgb = np.array(img)
    commander.messenger.send_image(username, rgb)


def processes():
    apps = get_open_apps()
    commander.messenger.processes(username, apps)
    return apps


def port_reset(password, port):
    pass


username = win32api.GetUserName()
commander = socket_commands.SocketCommands(username)

threading.Thread(target=freeze_loop, daemon=True).start()
threading.Thread(target=freeze_watchdog, daemon=True).start()

commander.receiver.thread(
    freeze=freeze,
    images=send_images,
    processes=processes,
    port_reset=port_reset
)


# ------------------------------------------------------------
# Tkinter mainloop MUST run in the main thread
# ------------------------------------------------------------
root.mainloop()
