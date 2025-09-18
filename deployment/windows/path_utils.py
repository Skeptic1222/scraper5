"""
Windows Path Utilities for Enhanced Media Scraper
Handles Windows-specific path operations and file system access
"""
import os
import sys
import platform
import logging
from pathlib import Path
import tempfile

# Configure logging
logger = logging.getLogger(__name__)

# Platform detection
IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"


class WindowsPathManager:
    """Manages Windows-specific path operations"""
    
    def __init__(self):
        self.is_windows = IS_WINDOWS
        self.temp_dir = None
        self.app_data_dir = None
        self.logs_dir = None
        self._setup_directories()
    
    def _setup_directories(self):
        """Setup Windows-specific directories"""
        if self.is_windows:
            # Use Windows-specific directories
            self.app_data_dir = Path(os.environ.get("LOCALAPPDATA", "C:\\ProgramData")) / "EnhancedMediaScraper"
            self.temp_dir = Path(tempfile.gettempdir()) / "EnhancedMediaScraper"
            self.logs_dir = self.app_data_dir / "logs"
        else:
            # Use Unix-style directories
            self.app_data_dir = Path.home() / ".enhanced_media_scraper"
            self.temp_dir = Path("/tmp") / "enhanced_media_scraper"
            self.logs_dir = self.app_data_dir / "logs"
        
        # Create directories
        for directory in [self.app_data_dir, self.temp_dir, self.logs_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_app_data_path(self) -> Path:
        """Get application data directory path"""
        return self.app_data_dir
    
    def get_temp_path(self) -> Path:
        """Get temporary directory path"""
        return self.temp_dir
    
    def get_logs_path(self) -> Path:
        """Get logs directory path"""
        return self.logs_dir
    
    def normalize_path(self, path: str) -> str:
        """Normalize path for current platform"""
        if not path:
            return ""
        
        # Convert to Path object and resolve
        normalized = Path(path).resolve()
        
        if self.is_windows:
            # Ensure Windows path format
            return str(normalized).replace("/", "\\")
        else:
            # Ensure Unix path format
            return str(normalized).replace("\\", "/")
    
    def get_safe_filename(self, filename: str) -> str:
        """Get a safe filename for the current platform"""
        if not filename:
            return "unnamed_file"
        
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*' if self.is_windows else '/'
        safe_name = filename
        
        for char in invalid_chars:
            safe_name = safe_name.replace(char, "_")
        
        # Remove leading/trailing whitespace and dots
        safe_name = safe_name.strip(". ")
        
        # Ensure not empty
        if not safe_name:
            safe_name = "unnamed_file"
        
        # Windows filename length limit
        if self.is_windows and len(safe_name) > 255:
            name_part = safe_name[:250]
            extension = ""
            if "." in safe_name:
                parts = safe_name.rsplit(".", 1)
                if len(parts) == 2:
                    name_part = parts[0][:250]
                    extension = "." + parts[1][:4]  # Limit extension too
            safe_name = name_part + extension
        
        return safe_name
    
    def get_asset_storage_path(self) -> Path:
        """Get path for storing downloaded assets"""
        storage_path = self.app_data_dir / "assets"
        storage_path.mkdir(parents=True, exist_ok=True)
        return storage_path
    
    def get_database_path(self, db_name: str = "scraper.db") -> Path:
        """Get database file path"""
        return self.app_data_dir / db_name
    
    def ensure_writable_path(self, path: Path) -> bool:
        """Ensure a path is writable, create if necessary"""
        try:
            path.mkdir(parents=True, exist_ok=True)
            
            # Test write access
            test_file = path / ".write_test"
            test_file.write_text("test")
            test_file.unlink()
            
            return True
        except (OSError, PermissionError) as e:
            logger.error(f"Path not writable: {path} - {e}")
            return False
    
    def get_config_path(self) -> Path:
        """Get configuration file path"""
        if self.is_windows:
            # Windows: Use LOCALAPPDATA
            config_dir = Path(os.environ.get("LOCALAPPDATA", "C:\\ProgramData")) / "EnhancedMediaScraper"
        else:
            # Unix: Use home directory
            config_dir = Path.home() / ".config" / "enhanced_media_scraper"
        
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "config.json"
    
    def get_pid_file_path(self) -> Path:
        """Get PID file path for service management"""
        return self.temp_dir / "enhanced_media_scraper.pid"
    
    def is_path_safe(self, path: str) -> bool:
        """Check if a path is safe (within allowed directories)"""
        try:
            resolved_path = Path(path).resolve()
            
            # Check if path is within our app directories
            safe_roots = [
                self.app_data_dir,
                self.temp_dir,
                Path.cwd(),  # Current working directory
            ]
            
            for root in safe_roots:
                try:
                    resolved_path.relative_to(root.resolve())
                    return True
                except ValueError:
                    continue
            
            return False
        except (OSError, ValueError):
            return False


# Global path manager instance
path_manager = WindowsPathManager()


def get_path_manager() -> WindowsPathManager:
    """Get the global path manager instance"""
    return path_manager


def init_windows_paths():
    """Initialize Windows-specific paths and logging"""
    if IS_WINDOWS:
        logger.info("Initializing Windows path management")
        
        # Setup Windows-specific logging
        log_file = path_manager.get_logs_path() / "windows_deployment.log"
        
        # Add file handler if not already present
        root_logger = logging.getLogger()
        if not any(isinstance(h, logging.FileHandler) for h in root_logger.handlers):
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(
                logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
            root_logger.addHandler(file_handler)
        
        logger.info(f"Windows paths initialized:")
        logger.info(f"  App Data: {path_manager.get_app_data_path()}")
        logger.info(f"  Temp: {path_manager.get_temp_path()}")
        logger.info(f"  Logs: {path_manager.get_logs_path()}")
        logger.info(f"  Config: {path_manager.get_config_path()}")


if __name__ == "__main__":
    # Test the path manager
    init_windows_paths()
    pm = get_path_manager()
    
    print(f"Platform: {'Windows' if pm.is_windows else 'Unix'}")
    print(f"App Data: {pm.get_app_data_path()}")
    print(f"Temp Dir: {pm.get_temp_path()}")
    print(f"Logs Dir: {pm.get_logs_path()}")
    print(f"Config: {pm.get_config_path()}")
    print(f"Database: {pm.get_database_path()}")
    
    # Test safe filename
    test_names = [
        "normal_file.txt",
        "file with spaces.jpg",
        "file<>:with|bad?chars*.png",
        "",
        "very_long_filename_that_exceeds_normal_limits_and_should_be_truncated_properly_without_breaking_the_extension.jpg"
    ]
    
    print("\nSafe filename tests:")
    for name in test_names:
        safe = pm.get_safe_filename(name)
        print(f"  '{name}' -> '{safe}'")