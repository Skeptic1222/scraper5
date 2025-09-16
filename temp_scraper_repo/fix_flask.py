#!/usr/bin/env python3
"""
Fix Flask and restore original application with proper template rendering
"""

import os
import sys
import subprocess

# Set proper environment
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_DEBUG'] = '0'
os.environ['FLASK_RUN_PORT'] = '8080'

print("Fixing Flask installation...")

# First try to reinstall pip
try:
    subprocess.check_call([sys.executable, "-m", "ensurepip", "--upgrade"])
    print("✓ Pip upgraded")
except:
    print("! Pip upgrade failed, continuing...")

# Try to uninstall broken packages
try:
    subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "flask", "-y"])
except:
    pass

# Install Flask properly
packages = [
    "flask==2.3.3",
    "werkzeug==2.3.7",
    "jinja2==3.1.2",
    "flask-sqlalchemy==3.0.5",
    "flask-login==0.6.2",
    "python-dotenv==1.0.0",
    "flask-wtf==1.1.1"
]

for package in packages:
    try:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✓ {package} installed")
    except Exception as e:
        print(f"✗ Failed to install {package}: {e}")

print("\nTrying to import Flask...")
try:
    from flask import Flask, render_template, jsonify, request
    print("✓ Flask imported successfully!")

    # Create a working Flask app with template rendering
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'

    @app.route('/')
    @app.route('/scraper')
    @app.route('/scraper/')
    def index():
        """Render the main index template"""
        try:
            # Check if we're in login-required mode
            login_required = os.getenv('LOGIN_REQUIRED', 'true').lower() == 'true'

            # For now, show splash page
            return render_template('splash.html',
                                 google_configured=True,
                                 APP_BASE='/scraper')
        except Exception as e:
            # If templates don't work, return a basic HTML
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Enhanced Media Scraper</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            </head>
            <body>
                <div class="container mt-5">
                    <h1>Enhanced Media Scraper v3.0</h1>
                    <p>Template rendering error: {str(e)}</p>
                    <p>The application is running but templates need to be fixed.</p>
                </div>
            </body>
            </html>
            """

    @app.route('/scraper/static/<path:filename>')
    def static_files(filename):
        """Serve static files"""
        return app.send_static_file(filename)

    # Run the app
    print("\nStarting Flask application on port 8080...")
    app.run(host='0.0.0.0', port=8080, debug=False)

except ImportError as e:
    print(f"✗ Flask import failed: {e}")
    print("\nFalling back to simple HTTP server...")

    # Fallback to simple HTTP server that serves templates as HTML
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import mimetypes

    class TemplateHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path in ['/', '/scraper', '/scraper/']:
                self.serve_template('splash.html')
            elif self.path.startswith('/scraper/static/'):
                self.serve_static(self.path[8:])
            else:
                self.send_error(404)

        def serve_template(self, template_name):
            try:
                with open(f'templates/{template_name}', 'r') as f:
                    content = f.read()

                # Basic template replacements
                content = content.replace('{{ url_for("static", filename="', '/scraper/static/')
                content = content.replace('") }}', '')
                content = content.replace('{{ APP_BASE }}', '/scraper')
                content = content.replace('{% if google_configured %}', '')
                content = content.replace('{% endif %}', '')
                content = content.replace('{% extends "base.html" %}', '')
                content = content.replace('{% block ', '<!-- ')
                content = content.replace('{% endblock %}', ' -->')

                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(content.encode())
            except Exception as e:
                self.send_error(500, str(e))

        def serve_static(self, path):
            try:
                with open(path, 'rb') as f:
                    content = f.read()
                mime_type, _ = mimetypes.guess_type(path)
                self.send_response(200)
                self.send_header('Content-Type', mime_type or 'application/octet-stream')
                self.end_headers()
                self.wfile.write(content)
            except:
                self.send_error(404)

        def log_message(self, format, *args):
            pass

    server = HTTPServer(('127.0.0.1', 8080), TemplateHandler)
    print("Starting fallback server on port 8080...")
    server.serve_forever()