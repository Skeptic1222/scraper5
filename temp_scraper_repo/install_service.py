"""
Windows Service Configuration for Enhanced Media Scraper
- Installs the application as a Windows service
- Configures automatic startup
- Sets up monitoring and recovery
"""

import os
import sys
import winreg
from pathlib import Path

import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import win32api

class ScraperService(win32serviceutil.ServiceFramework):
    _svc_name_ = "ScraperService"
    _svc_display_name_ = "Enhanced Media Scraper Service"
    _svc_description_ = "Web scraping service with database persistence and OAuth authentication"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.is_alive = True

    def SvcStop(self):
        """Stop the service"""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        self.is_alive = False

    def SvcDoRun(self):
        """Run the service"""
        # Ensure we're in the correct directory
        os.chdir(str(Path(__file__).parent))

        # Add application path to environment
        sys.path.append(str(Path(__file__).parent))

        try:
            # Import and run the production startup script
            from start_production import main
            main()
        except Exception as e:
            servicemanager.LogErrorMsg(f"Service failed: {str(e)}")
            self.SvcStop()

def get_python_path():
    """Get Python installation path from registry"""
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Python\PythonCore\3.9\InstallPath") as key:
            return os.path.join(winreg.QueryValue(key, ""), "python.exe")
    except WindowsError:
        return sys.executable

def configure_service():
    """Configure the Windows service"""
    # Get paths
    python_path = get_python_path()
    script_path = os.path.abspath(__file__)
    working_dir = os.path.dirname(script_path)

    # Create service command
    service_cmd = f'"{python_path}" "{script_path}" --startup auto install'

    try:
        # Remove existing service if it exists
        os.system(f'sc delete "{ScraperService._svc_name_}"')

        # Install service
        os.system(service_cmd)

        # Configure recovery options
        recovery_cmd = (
            f'sc failure "{ScraperService._svc_name_}" '
            'reset= 86400 '  # Reset fail count after 1 day
            'actions= restart/60000/restart/60000/restart/60000'  # Restart after 1 minute, up to 3 times
        )
        os.system(recovery_cmd)

        # Configure delayed start
        delayed_start_cmd = f'sc config "{ScraperService._svc_name_}" start= delayed-auto'
        os.system(delayed_start_cmd)

        print("[SUCCESS] Service installed and configured successfully")
        print(f"Service Name: {ScraperService._svc_name_}")
        print(f"Display Name: {ScraperService._svc_display_name_}")
        print(f"Working Directory: {working_dir}")
        print("Recovery: Auto-restart after 1 minute, up to 3 times")
        print("Startup: Delayed automatic start")

    except Exception as e:
        print(f"[ERROR] Service configuration failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        configure_service()
    else:
        win32serviceutil.HandleCommandLine(ScraperService)