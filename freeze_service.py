import win32serviceutil
import win32service
import win32event
import servicemanager
import threading
import time
import main


class FreezeControlService(win32serviceutil.ServiceFramework):
    _svc_name_ = "FreezeControlService"
    _svc_display_name_ = "Freeze Control Background Service"
    _svc_description_ = "Runs the freeze-control socket listener and overlay system in the background."

    def __init__(self, args):
        super().__init__(args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.running = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.running = False
        win32event.SetEvent(self.stop_event)

    def SvcDoRun(self):
        servicemanager.LogInfoMsg("FreezeControlService: Starting service")

        # Run your program in a thread so the service loop stays alive
        t = threading.Thread(target=self.run_main_program)
        t.start()

        # Wait until stop event is triggered
        win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)

        servicemanager.LogInfoMsg("FreezeControlService: Service stopped")

    def run_main_program(self):
        """
        This is where your existing freeze-control system runs.
        """
        try:
            main.run_background()  # You will create this function
        except Exception as e:
            servicemanager.LogErrorMsg(f"FreezeControlService crashed: {e}")
            time.sleep(5)
