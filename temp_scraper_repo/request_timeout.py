"""
Request Timeout Middleware
Provides configurable timeout for Flask requests
"""

import logging
import signal
from functools import wraps

from flask import g, jsonify, request
from werkzeug.exceptions import RequestTimeout

logger = logging.getLogger(__name__)

class TimeoutError(Exception):
    """Custom timeout exception"""
    pass

def timeout_handler(signum, frame):
    """Signal handler for timeout"""
    raise TimeoutError("Request processing timeout")

def add_timeout_middleware(app, default_timeout=30):
    """
    Add timeout middleware to Flask app

    Args:
        app: Flask application instance
        default_timeout: Default timeout in seconds (30s default)
    """

    @app.before_request
    def before_request():
        """Set up timeout for each request"""
        # Get timeout from config or use default
        timeout = app.config.get('REQUEST_TIMEOUT', default_timeout)

        # Special cases for longer operations
        if request.endpoint in ['search_download.search_media', 'search_download.download_url']:
            timeout = 60  # 60 seconds for download operations
        elif request.endpoint and 'api' in request.endpoint:
            timeout = 45  # 45 seconds for API calls

        g.timeout = timeout

        # Note: signal-based timeout only works on Unix systems
        # For Windows/IIS deployment, rely on IIS timeout settings
        try:
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout)
        except (AttributeError, ValueError):
            # Signal not available on Windows
            logger.debug("Signal-based timeout not available on this platform")

    @app.after_request
    def after_request(response):
        """Cancel timeout after successful request"""
        try:
            signal.alarm(0)  # Cancel the alarm
        except (AttributeError, ValueError):
            pass
        return response

    @app.errorhandler(TimeoutError)
    def handle_timeout(e):
        """Handle timeout errors"""
        logger.warning(f"Request timeout: {request.url} after {g.get('timeout', default_timeout)}s")
        return jsonify({
            'error': 'Request timeout',
            'message': 'The request took too long to process. Please try again.'
        }), 504

    @app.errorhandler(RequestTimeout)
    def handle_werkzeug_timeout(e):
        """Handle Werkzeug timeout errors"""
        logger.warning(f"Werkzeug timeout: {request.url}")
        return jsonify({
            'error': 'Request timeout',
            'message': 'The request exceeded the maximum allowed time.'
        }), 504

def timeout_decorator(seconds=30):
    """
    Decorator to add custom timeout to specific routes

    Usage:
        @app.route('/slow-operation')
        @timeout_decorator(seconds=60)
        def slow_operation():
            # Your code here
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Store original timeout
            original_timeout = g.get('timeout', 30)
            g.timeout = seconds

            try:
                signal.alarm(seconds)
            except (AttributeError, ValueError):
                pass

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                # Restore original timeout
                g.timeout = original_timeout
                try:
                    signal.alarm(0)
                except (AttributeError, ValueError):
                    pass

        return wrapper
    return decorator

def configure_iis_timeout(web_config_path='/mnt/c/inetpub/wwwroot/scraper/web.config'):
    """
    Generate IIS web.config with proper timeout settings
    """
    web_config_content = """<?xml version="1.0" encoding="utf-8"?>
<configuration>
    <system.webServer>
        <!-- FastCGI timeout settings -->
        <fastCgi>
            <application fullPath="C:\\Python39\\python.exe"
                         arguments="C:\\inetpub\\wwwroot\\scraper\\app.py"
                         maxInstances="4"
                         idleTimeout="300"
                         activityTimeout="30"
                         requestTimeout="90"
                         instanceMaxRequests="10000">
                <environmentVariables>
                    <environmentVariable name="PYTHONPATH" value="C:\\inetpub\\wwwroot\\scraper" />
                </environmentVariables>
            </application>
        </fastCgi>

        <!-- HTTP Runtime settings -->
        <httpRuntime executionTimeout="90" maxRequestLength="52428800" />

        <!-- Request filtering -->
        <security>
            <requestFiltering>
                <requestLimits maxAllowedContentLength="52428800" />
            </requestFiltering>
        </security>

        <!-- URL Rewrite rules for /scraper prefix -->
        <rewrite>
            <rules>
                <rule name="Scraper App" stopProcessing="true">
                    <match url="^scraper/?(.*)" />
                    <action type="Rewrite" url="app.py/{R:1}" />
                </rule>
            </rules>
        </rewrite>
    </system.webServer>

    <!-- Application settings -->
    <appSettings>
        <add key="REQUEST_TIMEOUT" value="30" />
        <add key="DATABASE_TIMEOUT" value="30" />
    </appSettings>
</configuration>"""

    try:
        with open(web_config_path, 'w') as f:
            f.write(web_config_content)
        logger.info(f"IIS web.config created at {web_config_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to create web.config: {str(e)}")
        return False
