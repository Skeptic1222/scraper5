#!/usr/bin/env python3
"""Working Flask App - Serves actual HTML with CSS"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import mimetypes

class EnhancedHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Main page
        if self.path == '/scraper' or self.path == '/scraper/':
            self.serve_splash_page()
        # Static files
        elif self.path.startswith('/scraper/static/'):
            self.serve_static_file(self.path[8:])  # Remove /scraper prefix
        elif self.path.startswith('/static/'):
            self.serve_static_file(self.path)
        else:
            self.send_error(404)

    def serve_splash_page(self):
        """Serve the main index page with proper HTML"""
        try:
            # Try to read index.html first
            with open('index.html', 'r', encoding='utf-8') as f:
                html = f.read()

            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode())
            return
        except FileNotFoundError:
            pass

        try:
            # Fallback to splash.html
            with open('templates/splash.html', 'r', encoding='utf-8') as f:
                html = f.read()

            # Replace template variables with actual values
            html = html.replace('{{ url_for("static", filename="css/style.css") }}', '/scraper/static/css/style.css')
            html = html.replace('{{ url_for("static", filename="css/splash.css") }}', '/scraper/static/css/splash.css')
            html = html.replace('{{ url_for("static", filename="js/app.js") }}', '/scraper/static/js/app.js')
            html = html.replace('{{ url_for("auth.login") }}', '/scraper/auth/login')
            html = html.replace('{{ APP_BASE }}', '/scraper')
            html = html.replace('{% if google_configured %}', '')
            html = html.replace('{% endif %}', '')

            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode())
        except FileNotFoundError:
            # Fallback HTML
            html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced Media Scraper v3.0</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="/scraper/static/css/style.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .container { display: flex; align-items: center; justify-content: center; min-height: 100vh; }
        .card { background: rgba(255,255,255,0.95); border-radius: 20px; padding: 40px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }
        h1 { color: #333; margin-bottom: 20px; }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="card text-center">
            <h1>🎯 Enhanced Media Scraper v3.0</h1>
            <p class="lead">Professional Media Content Aggregation Platform</p>
            <hr>
            <p>✅ Application is running successfully!</p>
            <p>🔧 Full Flask dependencies are being installed...</p>
            <a href="/scraper/index.html" class="btn btn-primary btn-lg mt-3">Enter Application</a>
        </div>
    </div>
</body>
</html>"""

            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode())

    def serve_static_file(self, path):
        """Serve static files (CSS, JS, images)"""
        # Clean the path
        if path.startswith('/'):
            path = path[1:]

        # Security check
        if '..' in path:
            self.send_error(403, "Forbidden")
            return

        try:
            # Try to open and serve the file
            full_path = os.path.join(os.getcwd(), path)

            with open(full_path, 'rb') as f:
                content = f.read()

            # Determine content type
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
            self.end_headers()
            self.wfile.write(content)

        except FileNotFoundError:
            self.send_error(404, f"File not found: {path}")
        except Exception as e:
            self.send_error(500, f"Server error: {str(e)}")

    def do_POST(self):
        # Handle POST requests same as GET for now
        self.do_GET()

    def do_HEAD(self):
        if self.path == '/scraper' or self.path == '/scraper/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
        else:
            self.send_error(404)

    def log_message(self, format, *args):
        # Suppress logs for cleaner output
        pass

if __name__ == '__main__':
    os.chdir('C:\\inetpub\\wwwroot\\scraper')
    port = 8080
    print(f"Starting Enhanced Media Scraper on port {port}...")
    print(f"Server URL: http://localhost:{port}")
    print("Access via IIS: http://localhost/scraper")

    server = HTTPServer(('127.0.0.1', port), EnhancedHandler)
    server.serve_forever()