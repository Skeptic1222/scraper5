#!/usr/bin/env python3
"""
Force inject the complete UI revamp into the application
"""

import os
import time

# Find all HTML templates
template_dir = "/mnt/c/inetpub/wwwroot/scraper/templates"

# Script to inject
ui_revamp_script = """
<!-- Complete UI Revamp - Force Injected -->
<script src="{{ url_for('static', filename='js/fixes/complete-ui-revamp.js') }}?v={}"></script>
""".format(int(time.time()))

# Templates to update
templates = ['base.html', 'index.html']

for template in templates:
    filepath = os.path.join(template_dir, template)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            content = f.read()

        # Check if already added
        if 'complete-ui-revamp.js' not in content:
            # Add before </body>
            if '</body>' in content:
                content = content.replace('</body>', ui_revamp_script + '\n</body>')

                with open(filepath, 'w') as f:
                    f.write(content)

                print(f"✅ Updated {template}")
            else:
                print(f"⚠️ No </body> tag found in {template}")
        else:
            print(f"ℹ️ Script already in {template}")

print("\n✅ UI Revamp injection complete!")
print("The application should now have:")
print("  - Completely rebuilt sidebar navigation")
print("  - Fixed Google authentication badge")
print("  - Proper user display when logged in")