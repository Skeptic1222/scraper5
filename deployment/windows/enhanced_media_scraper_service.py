#!/usr/bin/env python3
"""
Enhanced Media Scraper Windows Service
Provides Windows Service wrapper for Flask application
"""
import os
import sys
import win32serviceutil
import win32service
import win32event
import logging
import time
import threading
import subprocess

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, parent_dir)

class EnhancedMediaScraperService(win32serviceutil.ServiceFramework):
    """Windows Service for Enhanced Media Scraper"""
    
    _svc_name_ = "EnhancedMediaScraper"
    _svc_display_name_ = "Enhanced Media Scraper Service"
    _svc_description_ = "Web scraping application with database-driven asset management"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.stop_requested = False
        self.app_process = None
        
        # Configure logging
        self.setup_logging()
        
    def setup_logging(self):
        """Configure service logging"""
        log_dir = os.path.join(parent_dir, "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, "service.log")
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def SvcStop(self):
        """Stop the service"""
        self.logger.info("Enhanced Media Scraper Service stopping...")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.stop_requested = True
        
        # Stop the Flask app process
        if self.app_process:
            try:
                self.app_process.terminate()
                self.app_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.logger.warning("Force killing Flask process")
                self.app_process.kill()
            except Exception as e:
                self.logger.error(f"Error stopping Flask process: {e}")
        
        win32event.SetEvent(self.hWaitStop)
        
    def SvcDoRun(self):
        """Main service entry point"""
        self.logger.info("Enhanced Media Scraper Service starting...")
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        
        try:
            self.main_loop()
        except Exception as e:
            self.logger.error(f"Service error: {e}")
            self.SvcStop()
            
    def main_loop(self):
        """Main service loop"""
        while not self.stop_requested:
            try:
                # Start Flask application
                self.start_flask_app()
                
                # Monitor the process
                while not self.stop_requested and self.app_process and self.app_process.poll() is None:
                    time.sleep(5)
                    
                if not self.stop_requested and self.app_process and self.app_process.poll() is not None:
                    self.logger.warning("Flask process died, restarting...")
                    time.sleep(10)  # Wait before restart
                    
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                time.sleep(30)  # Wait before retry
                
    def start_flask_app(self):
        """Start the Flask application process"""
        app_script = os.path.join(parent_dir, "app.py")
        python_exe = sys.executable
        
        # Set environment variables
        env = os.environ.copy()
        env.update({
            "FLASK_ENV": "production",
            "FLASK_RUN_PORT": "8080",  # Use port 8080 for IIS
            "PYTHONPATH": parent_dir,
        })
        
        try:
            self.logger.info(f"Starting Flask app: {python_exe} {app_script}")
            self.app_process = subprocess.Popen(
                [python_exe, app_script],
                cwd=parent_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            self.logger.info(f"Flask app started with PID: {self.app_process.pid}")
            
            # Start output monitoring thread
            monitor_thread = threading.Thread(target=self.monitor_output, daemon=True)
            monitor_thread.start()
            
        except Exception as e:
            self.logger.error(f"Failed to start Flask app: {e}")
            raise
            
    def monitor_output(self):
        """Monitor Flask application output"""
        if not self.app_process:
            return
            
        try:
            for line in iter(self.app_process.stdout.readline, b''):
                if self.stop_requested:
                    break
                line_str = line.decode('utf-8', errors='ignore').strip()
                if line_str:
                    self.logger.info(f"Flask: {line_str}")
        except Exception as e:
            self.logger.error(f"Output monitoring error: {e}")


def install_service():
    """Install the Windows service"""
    try:
        win32serviceutil.InstallService(
            EnhancedMediaScraperService,
            EnhancedMediaScraperService._svc_name_,
            EnhancedMediaScraperService._svc_display_name_,
            description=EnhancedMediaScraperService._svc_description_
        )
        print("✅ Service installed successfully")
    except Exception as e:
        print(f"❌ Service installation failed: {e}")


def remove_service():
    """Remove the Windows service"""
    try:
        win32serviceutil.RemoveService(EnhancedMediaScraperService._svc_name_)
        print("✅ Service removed successfully")
    except Exception as e:
        print(f"❌ Service removal failed: {e}")


def start_service():
    """Start the Windows service"""
    try:
        win32serviceutil.StartService(EnhancedMediaScraperService._svc_name_)
        print("✅ Service started successfully")
    except Exception as e:
        print(f"❌ Service start failed: {e}")


def stop_service():
    """Stop the Windows service"""
    try:
        win32serviceutil.StopService(EnhancedMediaScraperService._svc_name_)
        print("✅ Service stopped successfully")
    except Exception as e:
        print(f"❌ Service stop failed: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "install":
            install_service()
        elif sys.argv[1] == "remove":
            remove_service()
        elif sys.argv[1] == "start":
            start_service()
        elif sys.argv[1] == "stop":
            stop_service()
        else:
            win32serviceutil.HandleCommandLine(EnhancedMediaScraperService)
    else:
        win32serviceutil.HandleCommandLine(EnhancedMediaScraperService)