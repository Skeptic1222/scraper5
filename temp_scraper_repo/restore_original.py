#!/usr/bin/env python3
"""
Restore the original Enhanced Media Scraper application with proper template rendering
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import re
import mimetypes

class OriginalAppHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        if self.path in ['/', '/scraper', '/scraper/']:
            self.serve_index()
        elif self.path.startswith('/scraper/static/'):
            # Remove /scraper/ prefix and serve static file
            static_path = self.path[9:]  # Remove '/scraper/' (9 chars)
            self.serve_static(static_path)
        elif self.path.startswith('/static/'):
            self.serve_static(self.path)
        else:
            self.send_error(404, f"Path not found: {self.path}")

    def serve_index(self):
        """Serve the main application page with proper template rendering"""
        try:
            # Read base template
            with open('templates/base.html', 'r', encoding='utf-8') as f:
                base_html = f.read()

            # Read index template
            with open('templates/index.html', 'r', encoding='utf-8') as f:
                index_html = f.read()

            # Extract blocks from index template
            title_match = re.search(r'{% block title %}(.*?){% endblock %}', index_html, re.DOTALL)
            content_match = re.search(r'{% block content %}(.*?){% endblock %}', index_html, re.DOTALL)

            title = title_match.group(1) if title_match else 'Enhanced Media Scraper'
            content = content_match.group(1) if content_match else index_html

            # Replace blocks in base template
            html = base_html
            html = re.sub(r'{% block title %}.*?{% endblock %}', title, html, flags=re.DOTALL)
            html = re.sub(r'{% block content %}.*?{% endblock %}', content, html, flags=re.DOTALL)

            # Replace Flask template variables
            html = self.replace_template_vars(html)

            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))

        except FileNotFoundError:
            # If templates are missing, serve splash page
            self.serve_splash()

    def serve_splash(self):
        """Serve the splash page"""
        try:
            with open('templates/splash.html', 'r', encoding='utf-8') as f:
                html = f.read()

            html = self.replace_template_vars(html)

            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))

        except FileNotFoundError:
            # Fallback HTML
            html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced Media Scraper v3.0</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <h1>Enhanced Media Scraper v3.0</h1>
        <p>The application is starting...</p>
    </div>
</body>
</html>"""
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))

    def replace_template_vars(self, html):
        """Replace Jinja2 template variables with actual values"""
        # Static file URLs
        html = re.sub(r'{{\s*url_for\(["\']static["\']\s*,\s*filename\s*=\s*["\'](.+?)["\']\)\s*}}',
                     r'/scraper/static/\1', html)

        # Auth URLs
        html = html.replace('{{ url_for("auth.login") }}', '/scraper/auth/login')
        html = html.replace('{{ url_for("auth.logout") }}', '/scraper/auth/logout')
        html = html.replace('{{ url_for("index") }}', '/scraper')

        # APP_BASE variable
        html = html.replace('{{ APP_BASE }}', '/scraper')
        html = html.replace('{{APP_BASE}}', '/scraper')

        # Remove if statements for now
        html = re.sub(r'{%\s*if\s+.*?%}', '', html)
        html = re.sub(r'{%\s*endif\s*%}', '', html)
        html = re.sub(r'{%\s*else\s*%}', '', html)
        html = re.sub(r'{%\s*for\s+.*?%}', '', html)
        html = re.sub(r'{%\s*endfor\s*%}', '', html)

        # Remove comments
        html = re.sub(r'{#.*?#}', '', html)

        # User info (default values)
        html = html.replace('{{ user_info.name }}', 'Guest User')
        html = html.replace('{{ user_info.email }}', 'guest@example.com')
        html = html.replace('{{ user_info.picture }}', '/scraper/static/images/default-avatar.png')
        html = html.replace('{{ user_info.is_admin }}', 'false')

        # Config values
        html = html.replace('{{ config.DEBUG }}', 'false')
        html = html.replace('{{ STATIC_VER }}', str(os.path.getmtime(__file__)))

        # Server sources JSON
        html = html.replace('{{ server_sources_json|safe }}', '{"categories": {}}')

        return html

    def serve_static(self, path):
        """Serve static files"""
        if path.startswith('/'):
            path = path[1:]

        # Security check
        if '..' in path:
            self.send_error(403, "Forbidden")
            return

        try:
            # Debug: print the path we're trying to serve
            print(f"[DEBUG] Serving static file: {path}")

            full_path = os.path.join(os.getcwd(), path)
            print(f"[DEBUG] Full path: {full_path}")

            # Check if file exists
            if not os.path.exists(full_path):
                print(f"[DEBUG] File does not exist: {full_path}")
                self.send_error(404, f"File not found: {path}")
                return

            with open(full_path, 'rb') as f:
                content = f.read()

            mime_type, _ = mimetypes.guess_type(full_path)
            if not mime_type:
                if path.endswith('.css'):
                    mime_type = 'text/css'
                elif path.endswith('.js'):
                    mime_type = 'application/javascript'
                else:
                    mime_type = 'application/octet-stream'

            self.send_response(200)
            self.send_header('Content-Type', mime_type)
            self.send_header('Content-Length', str(len(content)))
            self.send_header('Cache-Control', 'public, max-age=3600')
            self.end_headers()
            self.wfile.write(content)
            print(f"[DEBUG] Successfully served: {path}")

        except FileNotFoundError:
            self.send_error(404, f"File not found: {path}")
        except Exception as e:
            print(f"[DEBUG] Error serving {path}: {str(e)}")
            self.send_error(500, f"Server error: {str(e)}")

    def do_POST(self):
        """Handle POST requests"""
        self.do_GET()

    def do_HEAD(self):
        """Handle HEAD requests"""
        if self.path in ['/', '/scraper', '/scraper/']:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
        else:
            self.send_error(404)

    def log_message(self, format, *args):
        """Suppress logs"""
        pass

if __name__ == '__main__':
    os.chdir('C:\\inetpub\\wwwroot\\scraper')
    port = 8080

    print("=" * 60)
    print("RESTORING ORIGINAL Enhanced Media Scraper v3.0")
    print("=" * 60)
    print(f"Starting server on port {port}...")
    print(f"Access the application at: http://localhost/scraper")
    print("This serves the ORIGINAL templates with proper rendering")
    print("=" * 60)

    server = HTTPServer(('127.0.0.1', port), OriginalAppHandler)
    server.serve_forever()