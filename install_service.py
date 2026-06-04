"""
Utility script to install/uninstall the Windows Service.
Run with admin privileges.

Usage:
    python install_service.py --install    # Install service
    python install_service.py --remove     # Remove service
    python install_service.py --start      # Start service
    python install_service.py --stop       # Stop service
    python install_service.py --status     # Check status
"""

import sys
import win32serviceutil
import win32service
import win32event
from service import ClientService


def install_service():
    """Install the Windows Service."""
    try:
        win32serviceutil.InstallService(
            ClientService,
            ClientService._svc_name_,
            displayName=ClientService._svc_display_name_,
            description=ClientService._svc_description_,
            startType=win32service.SERVICE_AUTO_START
        )
        print(f"✓ Service '{ClientService._svc_display_name_}' installed successfully")
        print(f"  Service name: {ClientService._svc_name_}")
        print(f"  Start type: Automatic")
    except Exception as e:
        print(f"✗ Installation failed: {e}")
        sys.exit(1)


def remove_service():
    """Remove the Windows Service."""
    try:
        win32serviceutil.RemoveService(ClientService._svc_name_)
        print(f"✓ Service '{ClientService._svc_display_name_}' removed successfully")
    except Exception as e:
        print(f"✗ Removal failed: {e}")
        sys.exit(1)


def start_service():
    """Start the Windows Service."""
    try:
        win32serviceutil.StartService(ClientService._svc_name_)
        print(f"✓ Service '{ClientService._svc_name_}' started")
    except Exception as e:
        print(f"✗ Failed to start service: {e}")
        sys.exit(1)


def stop_service():
    """Stop the Windows Service."""
    try:
        win32serviceutil.StopService(ClientService._svc_name_)
        print(f"✓ Service '{ClientService._svc_name_}' stopped")
    except Exception as e:
        print(f"✗ Failed to stop service: {e}")
        sys.exit(1)


def check_status():
    """Check service status."""
    try:
        status = win32serviceutil.QueryServiceStatus(ClientService._svc_name_)
        state = status[1]
        states = {
            1: "STOPPED",
            2: "START_PENDING",
            3: "STOP_PENDING",
            4: "RUNNING",
            5: "CONTINUE_PENDING",
            6: "PAUSE_PENDING",
            7: "PAUSED"
        }
        print(f"✓ Service status: {states.get(state, 'UNKNOWN')}")
    except Exception as e:
        print(f"✗ Failed to check status: {e}")
        sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == '--install':
        install_service()
    elif command == '--remove':
        remove_service()
    elif command == '--start':
        start_service()
    elif command == '--stop':
        stop_service()
    elif command == '--status':
        check_status()
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)
