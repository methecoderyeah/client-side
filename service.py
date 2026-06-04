"""
Windows Service for client-side monitoring and control.
Replaces tkinter with native Windows win32 messaging and notifications.
"""

import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import logging
import os
import threading
import time
from pathlib import Path

# Add the service directory to path for imports
SERVICE_DIR = Path(__file__).parent
sys.path.insert(0, str(SERVICE_DIR))

import win32api
import win32gui
import ctypes
from PIL import ImageGrab
import socket_commands
import numpy as np
import psutil
import pyautogui
from cryptography.fernet import Fernet

# Setup logging
log_path = SERVICE_DIR / "logs"
log_path.mkdir(exist_ok=True)
logging.basicConfig(
    filename=str(log_path / "service.log"),
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

cipher = Fernet("uaXbNuTAUXK5o191j94JxiWpCgmBCD3zaft-Ooc2zCg=")

# Global state
freeze_active = False
freeze_end_time = 0
overlay_hwnd = None
commander = None


def get_pid_from_hwnd(hwnd):
    """Get process ID from window handle."""
    pid = ctypes.c_ulong()
    ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return pid.value


def get_open_apps():
    """Enumerate all open applications."""
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


def show_freeze_notification():
    """Display freeze notification using Windows UI."""
    global overlay_hwnd
    try:
        # Use win32 to show a message box or create a borderless window
        # This is a native replacement for tkinter overlay
        overlay_hwnd = ctypes.windll.user32.MessageBoxA(
            0,
            b"eyes on the teacher, not this screen",
            b"FROZEN - Monitoring Active",
            0x00000010 | 0x00001000  # MB_ICONHAND | MB_SYSTEMMODAL
        )
        logger.info("Freeze notification displayed")
    except Exception as e:
        logger.error(f"Error showing notification: {e}")


def create_freeze_window():
    """Create a native Windows borderless freeze window (alternative to MessageBox)."""
    global overlay_hwnd
    try:
        # Register window class
        class_name = "FreezeOverlay"
        wnd_class = ctypes.wintypes.WNDCLASS()
        wnd_class.lpszClassName = class_name
        wnd_class.lpfnWndProc = {
            win32con.WM_DESTROY: lambda hwnd, msg, wparam, lparam: ctypes.windll.user32.PostQuitMessage(0)
        }
        
        # Simplified: Use a native window with win32 API
        logger.info("Creating freeze overlay window")
    except Exception as e:
        logger.error(f"Error creating freeze window: {e}")


def freeze():
    """Activate freeze mode."""
    global freeze_active, freeze_end_time
    freeze_end_time = time.time() + 5
    if not freeze_active:
        freeze_active = True
        logger.info("Freeze activated")
        show_freeze_notification()


def unfreeze():
    """Deactivate freeze mode."""
    global freeze_active, overlay_hwnd
    freeze_active = False
    if overlay_hwnd:
        try:
            ctypes.windll.user32.SendMessageA(overlay_hwnd, win32con.WM_CLOSE, 0, 0)
        except:
            pass
    logger.info("Freeze deactivated")


def freeze_loop():
    """Monitor and enforce freeze mode."""
    while True:
        try:
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

        except Exception as e:
            logger.error(f"Error in freeze_loop: {e}")
        
        time.sleep(0.05)


def freeze_watchdog():
    """Monitor freeze timeout."""
    while True:
        try:
            global freeze_active, freeze_end_time
            if freeze_active and time.time() >= freeze_end_time:
                unfreeze()
        except Exception as e:
            logger.error(f"Error in freeze_watchdog: {e}")
        time.sleep(0.1)


def send_images():
    """Capture and send screen images."""
    try:
        img = ImageGrab.grab()
        rgb = np.array(img)
        commander.messenger.send_image(username, rgb)
        logger.info("Image sent")
    except Exception as e:
        logger.error(f"Error sending images: {e}")


def processes():
    """Get and send process list."""
    try:
        apps = get_open_apps()
        commander.messenger.processes(username, apps)
        logger.info(f"Processes sent: {len(apps)} apps")
        return apps
    except Exception as e:
        logger.error(f"Error getting processes: {e}")
        return []


def port_reset(password, port):
    """Handle port reset command."""
    try:
        decrypted = cipher.decrypt(password).decode()
        if decrypted == "ADMIN_RSegG4sp5BHjDv6KQJFEMmah9Vt3wZ":
            with open(SERVICE_DIR / "socket.txt", "w") as file:
                file.write(str(port))
            logger.info(f"Port reset to {port}")
    except Exception as e:
        logger.error(f"Error in port_reset: {e}")


class ClientService(win32serviceutil.ServiceFramework):
    """Windows Service for client-side monitoring."""
    
    _svc_name_ = "ClientSideMonitor"
    _svc_display_name_ = "Client-Side Monitor Service"
    _svc_description_ = "Monitoring and control client service"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.is_alive = True
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        """Handle service stop."""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_alive = False
        logger.info("Service stop requested")

    def SvcDoRun(self):
        """Main service loop."""
        global commander, username
        
        try:
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, "")
            )
            logger.info("Service started")
            
            username = win32api.GetUserName()
            logger.info(f"Service running as user: {username}")
            
            # Initialize socket commander
            commander = socket_commands.SocketCommands(username)
            
            # Start background threads
            threading.Thread(target=freeze_loop, daemon=True).start()
            threading.Thread(target=freeze_watchdog, daemon=True).start()
            
            # Start socket receivers
            commander.receiver.thread(
                freeze=freeze,
                images=send_images,
                processes=processes,
                port_reset=port_reset
            )
            
            # Service event loop
            while self.is_alive:
                rc = win32event.WaitForSingleObject(self.hWaitStop, 5000)
                if rc == win32event.WAIT_OBJECT_0:
                    logger.info("Service stop event received")
                    break
                    
        except Exception as e:
            logger.error(f"Service error: {e}", exc_info=True)
            servicemanager.LogErrorMsg(f"Service error: {e}")


if __name__ == '__main__':
    if len(sys.argv) == 1:
        # Service is being run by Windows
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingleService(ClientService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        # Manual command-line control
        win32serviceutil.HandleCommandLine(ClientService)
