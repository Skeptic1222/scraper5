#!/usr/bin/env python3
"""
FastCGI Handler for Enhanced Media Scraper Flask Application
Provides proper WSGI entry point for IIS FastCGI deployment
"""
import os
import sys

# Add application directory to Python path
app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, app_dir)

# Set environment for production
os.environ.setdefault("FLASK_ENV", "production")
os.environ.setdefault("FLASK_DEBUG", "0")

try:
    # Import the Flask application
    from app import app as application
    
    # Configure for FastCGI
    if __name__ == "__main__":
        # This is executed by wfastcgi
        from wfastcgi import WSGIServer
        WSGIServer(application).run()
    else:
        # This allows direct import of application
        pass
        
except Exception as e:
    # Log the error and provide a minimal error response
    import logging
    import traceback
    
    logging.basicConfig(level=logging.ERROR)
    logging.error(f"FastCGI handler failed to start: {e}")
    logging.error(traceback.format_exc())
    
    # Provide a minimal WSGI application for error display
    def error_application(environ, start_response):
        status = '500 Internal Server Error'
        headers = [('Content-Type', 'text/html')]
        start_response(status, headers)
        
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Application Error</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .error {{ background-color: #f8d7da; border: 1px solid #f5c6cb; 
                         color: #721c24; padding: 15px; border-radius: 4px; }}
            </style>
        </head>
        <body>
            <h1>Enhanced Media Scraper - Application Error</h1>
            <div class="error">
                <h3>Application failed to start</h3>
                <p>Error: {str(e)}</p>
                <p>Check the application logs for more details.</p>
            </div>
        </body>
        </html>
        """.encode('utf-8')
        
        return [error_html]
    
    application = error_application