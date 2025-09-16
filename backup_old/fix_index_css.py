#!/usr/bin/env python
"""Fix duplicate CSS variables in index.html"""

import re

# Read the file
with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the second :root declaration and remove it along with the dark theme navbar fix
# The pattern looks for the duplicate CSS variables section
pattern = r'(\s*/\* CSS Variables for themes \*/\s*:root\s*{[^}]+}\s*/\* Dark theme navbar fix \*/\s*\[data-theme="dark"\]\s*:root\s*{[^}]+})'

# Replace with empty string
content = re.sub(pattern, '', content, flags=re.DOTALL)

# Write back
with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed duplicate CSS variables!") 