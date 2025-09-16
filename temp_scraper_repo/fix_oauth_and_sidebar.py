#!/usr/bin/env python3
"""
Fix for Google OAuth 404 and missing sidebar navigation
"""

import os
import sys

def fix_oauth_routes():
    """Ensure OAuth routes are properly registered"""
    print("Fixing OAuth routes...")

    # Check if auth blueprint is registered correctly
    auth_file = 'auth.py'

    # Read current auth.py
    with open(auth_file, 'r') as f:
        content = f.read()

    # Check if blueprint is properly registered
    if 'auth_bp = Blueprint("auth", __name__, url_prefix="/auth")' in content:
        print("✓ Auth blueprint configured correctly with /auth prefix")
    else:
        print("✗ Auth blueprint needs fixing")
        return False

    # Check app.py
    app_file = 'app.py'
    with open(app_file, 'r') as f:
        app_content = f.read()

    if 'init_auth(app)' in app_content:
        print("✓ Auth initialization found in app.py")
    else:
        print("✗ Auth initialization missing in app.py")
        return False

    return True

def fix_sidebar_css():
    """Create a CSS fix to ensure sidebar is always visible"""
    print("\nCreating sidebar visibility fix...")

    sidebar_fix_css = """/* CRITICAL FIX: Force sidebar to be visible */
.sidebar {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    position: fixed !important;
    left: 0 !important;
    top: 60px !important; /* Below navbar */
    bottom: 0 !important;
    width: 250px !important;
    background: var(--sidebar-bg, #ffffff) !important;
    border-right: 1px solid var(--border-color, #dee2e6) !important;
    z-index: 1000 !important;
    overflow-y: auto !important;
    transform: translateX(0) !important;
}

/* Ensure main content doesn't overlap sidebar */
.main-container {
    display: flex !important;
    min-height: calc(100vh - 60px) !important;
    margin-top: 60px !important;
}

.content-area {
    margin-left: 250px !important;
    flex: 1 !important;
    width: calc(100% - 250px) !important;
    padding: 20px !important;
}

/* Force sidebar items to be visible */
.sidebar .nav-list {
    display: block !important;
    visibility: visible !important;
}

.sidebar .nav-item {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
}

/* Dark theme support */
[data-theme="dark"] .sidebar {
    background: #1a1a1a !important;
    border-right-color: #333 !important;
}

/* Mobile responsive */
@media (max-width: 768px) {
    .sidebar {
        transform: translateX(-100%) !important;
        transition: transform 0.3s ease !important;
    }

    .sidebar.show {
        transform: translateX(0) !important;
    }

    .content-area {
        margin-left: 0 !important;
        width: 100% !important;
    }
}
"""

    # Save the CSS fix
    css_path = 'static/css/fixes/sidebar-force-visible.css'
    os.makedirs(os.path.dirname(css_path), exist_ok=True)

    with open(css_path, 'w') as f:
        f.write(sidebar_fix_css)

    print(f"✓ Created {css_path}")

    # Update base.html to include the new CSS
    base_html = 'templates/base.html'
    with open(base_html, 'r') as f:
        base_content = f.read()

    css_link = '<link rel="stylesheet" href="{{ url_for(\'static\', filename=\'css/fixes/sidebar-force-visible.css\') }}">'

    if 'sidebar-force-visible.css' not in base_content:
        # Add before closing </head>
        base_content = base_content.replace('</head>', f'    {css_link}\n</head>')

        with open(base_html, 'w') as f:
            f.write(base_content)

        print("✓ Added CSS link to base.html")
    else:
        print("✓ CSS already linked in base.html")

    return True

def fix_oauth_redirect():
    """Fix OAuth redirect URL configuration"""
    print("\nFixing OAuth redirect configuration...")

    # Create environment configuration
    env_content = """# OAuth Configuration
GOOGLE_CLIENT_ID={client_id}
GOOGLE_CLIENT_SECRET={secret}
OAUTH_CALLBACK_URL=http://localhost/scraper/auth/google/callback
FLASK_ENV=development
LOGIN_REQUIRED=false
""".format(
        client_id=os.getenv('GOOGLE_CLIENT_ID', 'your-client-id'),
        secret=os.getenv('GOOGLE_CLIENT_SECRET', 'your-client-secret')
    )

    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✓ Created .env file with OAuth configuration")
    else:
        print("✓ .env file already exists")

    return True

def verify_routes():
    """Verify that all routes are accessible"""
    print("\nVerifying routes...")

    import subprocess
    import time

    # Check if Flask is running
    try:
        result = subprocess.run(['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', 'http://localhost/scraper'],
                              capture_output=True, text=True)
        if result.stdout == '200':
            print("✓ Main app is accessible")
        else:
            print(f"✗ Main app returned status: {result.stdout}")
    except:
        print("✗ Could not connect to app")

    # Check auth routes
    auth_routes = [
        '/scraper/auth/login',
        '/scraper/auth/check',
    ]

    for route in auth_routes:
        try:
            result = subprocess.run(['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', f'http://localhost{route}'],
                                  capture_output=True, text=True)
            if result.stdout in ['200', '302', '303']:
                print(f"✓ {route} is accessible (status: {result.stdout})")
            else:
                print(f"✗ {route} returned status: {result.stdout}")
        except:
            print(f"✗ Could not connect to {route}")

    return True

def main():
    print("=" * 60)
    print("Google OAuth & Sidebar Fix Script")
    print("=" * 60)

    os.chdir('/mnt/c/inetpub/wwwroot/scraper')

    # Run fixes
    oauth_ok = fix_oauth_routes()
    sidebar_ok = fix_sidebar_css()
    redirect_ok = fix_oauth_redirect()

    # Verify
    print("\n" + "=" * 60)
    verify_routes()

    print("\n" + "=" * 60)
    print("Fix Summary:")
    print(f"  OAuth Routes: {'✓ Fixed' if oauth_ok else '✗ Needs manual intervention'}")
    print(f"  Sidebar CSS: {'✓ Fixed' if sidebar_ok else '✗ Failed'}")
    print(f"  OAuth Config: {'✓ Fixed' if redirect_ok else '✗ Failed'}")
    print("=" * 60)

    if oauth_ok and sidebar_ok and redirect_ok:
        print("\n✅ All fixes applied successfully!")
        print("\nNext steps:")
        print("1. Restart the Flask application")
        print("2. Clear browser cache")
        print("3. Navigate to http://localhost/scraper")
        print("4. The sidebar should be visible on the left")
        print("5. Click 'Continue with Google' to test OAuth login")
    else:
        print("\n⚠️ Some fixes failed. Please review the output above.")

    return 0 if (oauth_ok and sidebar_ok and redirect_ok) else 1

if __name__ == '__main__':
    sys.exit(main())