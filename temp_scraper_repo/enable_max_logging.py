#!/usr/bin/env python3
"""
Enable maximum logging and debugging for all components
Configures MS Edge and browser logs to save to project folder
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime

# Create logging directories
log_dir = Path("debug_logs")
log_dir.mkdir(exist_ok=True)

browser_log_dir = log_dir / "browser"
browser_log_dir.mkdir(exist_ok=True)

app_log_dir = log_dir / "app"
app_log_dir.mkdir(exist_ok=True)

playwright_log_dir = log_dir / "playwright"
playwright_log_dir.mkdir(exist_ok=True)

# Configure Python logging
logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "detailed": {
            "format": "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "simple": {
            "format": "%(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": str(app_log_dir / f"debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
            "mode": "a"
        },
        "error_file": {
            "class": "logging.FileHandler",
            "level": "ERROR",
            "formatter": "detailed",
            "filename": str(app_log_dir / "errors.log"),
            "mode": "a"
        }
    },
    "loggers": {
        "": {
            "level": "DEBUG",
            "handlers": ["console", "file", "error_file"]
        },
        "werkzeug": {
            "level": "DEBUG",
            "handlers": ["console", "file"]
        },
        "flask": {
            "level": "DEBUG",
            "handlers": ["console", "file"]
        },
        "sqlalchemy": {
            "level": "INFO",
            "handlers": ["console", "file"]
        },
        "urllib3": {
            "level": "DEBUG",
            "handlers": ["console", "file"]
        },
        "requests": {
            "level": "DEBUG",
            "handlers": ["console", "file"]
        },
        "pyodbc": {
            "level": "DEBUG",
            "handlers": ["console", "file"]
        }
    }
}

# Save logging config
with open("logging_config.json", "w") as f:
    json.dump(logging_config, f, indent=2)

# Create browser logging configuration for MS Edge
edge_prefs = {
    "download": {
        "default_directory": str(Path.cwd() / "downloads"),
        "prompt_for_download": False
    },
    "profile": {
        "default_content_settings": {
            "popups": 0
        }
    },
    "safebrowsing": {
        "enabled": False
    }
}

# MS Edge launch arguments for maximum logging
edge_args = [
    "--enable-logging",
    "--v=1",
    "--dump-dom",
    "--enable-features=NetworkService,NetworkServiceInProcess",
    "--log-level=0",
    f"--log-file={browser_log_dir / 'edge.log'}",
    "--enable-chrome-browser-cloud-management",
    "--disable-background-timer-throttling",
    "--disable-backgrounding-occluded-windows",
    "--disable-renderer-backgrounding",
    "--disable-features=TranslateUI",
    "--disable-ipc-flooding-protection",
    "--disable-dev-shm-usage",
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-gpu",
    "--disable-web-security",
    "--disable-features=IsolateOrigins,site-per-process",
    "--allow-running-insecure-content",
    "--disable-blink-features=AutomationControlled",
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
]

# Playwright configuration for debugging
playwright_config = {
    "browser": "chromium",
    "channel": "msedge",
    "headless": False,
    "devtools": True,
    "slowMo": 500,
    "timeout": 60000,
    "viewport": {"width": 1920, "height": 1080},
    "ignoreHTTPSErrors": True,
    "bypassCSP": True,
    "locale": "en-US",
    "timezoneId": "America/New_York",
    "geolocation": {"latitude": 40.7128, "longitude": -74.0060},
    "permissions": ["geolocation", "notifications", "camera", "microphone"],
    "extraHTTPHeaders": {
        "Accept-Language": "en-US,en;q=0.9"
    },
    "recordVideo": {
        "dir": str(playwright_log_dir / "videos"),
        "size": {"width": 1920, "height": 1080}
    },
    "recordHar": {
        "path": str(playwright_log_dir / f"network_{datetime.now().strftime('%Y%m%d_%H%M%S')}.har"),
        "mode": "full"
    },
    "args": edge_args,
    "downloadsPath": str(Path.cwd() / "downloads"),
    "tracesDir": str(playwright_log_dir / "traces")
}

# Save configurations
with open("edge_config.json", "w") as f:
    json.dump({"preferences": edge_prefs, "args": edge_args}, f, indent=2)

with open("playwright_config.json", "w") as f:
    json.dump(playwright_config, f, indent=2)

# Create environment variables file for debugging
debug_env = """
# Debug Environment Variables
export DEBUG=True
export FLASK_DEBUG=1
export FLASK_ENV=development
export PYTHONUNBUFFERED=1
export WERKZEUG_DEBUG_PIN=off
export LOG_LEVEL=DEBUG
export SQLALCHEMY_ECHO=True
export BROWSER_LOG_DIR=debug_logs/browser
export APP_LOG_DIR=debug_logs/app
export PLAYWRIGHT_LOG_DIR=debug_logs/playwright
export ENABLE_PROFILING=True
export TRACE_SQL=True
export LOG_REQUESTS=True
export LOG_RESPONSES=True
export CAPTURE_SCREENSHOTS=True
export SAVE_HTML_SNAPSHOTS=True
export NETWORK_LOG=True
export CONSOLE_LOG=True
export PERFORMANCE_LOG=True
"""

with open(".env.debug", "w") as f:
    f.write(debug_env)

# Create JavaScript injection for browser console logging
browser_console_logger = """
// Browser Console Logger - Captures all console output
(function() {
    const originalLog = console.log;
    const originalError = console.error;
    const originalWarn = console.warn;
    const originalInfo = console.info;
    const originalDebug = console.debug;

    const logs = [];
    const maxLogs = 1000;

    function captureLog(type, args) {
        const log = {
            type: type,
            timestamp: new Date().toISOString(),
            message: Array.from(args).map(arg => {
                try {
                    if (typeof arg === 'object') {
                        return JSON.stringify(arg, null, 2);
                    }
                    return String(arg);
                } catch (e) {
                    return '[Unable to stringify]';
                }
            }).join(' '),
            stack: new Error().stack
        };

        logs.push(log);
        if (logs.length > maxLogs) {
            logs.shift();
        }

        // Send to server
        try {
            fetch('/api/browser-log', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(log)
            }).catch(() => {});
        } catch (e) {}

        return log;
    }

    console.log = function() {
        captureLog('log', arguments);
        originalLog.apply(console, arguments);
    };

    console.error = function() {
        captureLog('error', arguments);
        originalError.apply(console, arguments);
    };

    console.warn = function() {
        captureLog('warn', arguments);
        originalWarn.apply(console, arguments);
    };

    console.info = function() {
        captureLog('info', arguments);
        originalInfo.apply(console, arguments);
    };

    console.debug = function() {
        captureLog('debug', arguments);
        originalDebug.apply(console, arguments);
    };

    // Capture unhandled errors
    window.addEventListener('error', function(e) {
        captureLog('error', [e.message, e.filename, e.lineno, e.colno, e.error]);
    });

    // Capture unhandled promise rejections
    window.addEventListener('unhandledrejection', function(e) {
        captureLog('error', ['Unhandled Promise Rejection:', e.reason]);
    });

    // Expose logs for debugging
    window.__browserLogs = logs;
    window.__getBrowserLogs = () => logs;
    window.__clearBrowserLogs = () => logs.length = 0;

    console.log('[Browser Logger] Console logging enabled - all output will be captured');
})();
"""

with open("static/js/browser-console-logger.js", "w") as f:
    f.write(browser_console_logger)

print("""
✅ Maximum logging and debugging enabled!

📁 Log Directories Created:
- debug_logs/browser/    - Browser and MS Edge logs
- debug_logs/app/        - Application logs
- debug_logs/playwright/ - Playwright test logs

📝 Configuration Files Created:
- logging_config.json    - Python logging configuration
- edge_config.json       - MS Edge browser configuration
- playwright_config.json - Playwright test configuration
- .env.debug            - Debug environment variables

🔧 Features Enabled:
- Full DEBUG level logging for all components
- MS Edge browser console logging
- Network request/response logging
- SQL query logging
- Error stack traces
- Performance profiling
- Video recording for Playwright tests
- HAR file generation for network analysis
- Browser console output capture
- Automatic screenshot capture on errors

🚀 To activate:
1. Source debug environment: source .env.debug
2. Include browser logger in HTML: <script src="/static/js/browser-console-logger.js"></script>
3. Run tests with Playwright config
""")