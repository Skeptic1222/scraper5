#!/usr/bin/env python3
"""
Add 'implemented' flags to all sources in sources_data.py
Marks 7 working sources as implemented: True, rest as False
"""

IMPLEMENTED_SOURCES = {
    'google_images',
    'bing_images',
    'duckduckgo_images',
    'yahoo_images',
    'unsplash',
    'pexels',
    'pixabay'
}

def update_sources_data():
    """Read sources_data.py, add implemented flags, write back"""

    with open('sources_data.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Split into lines
    lines = content.split('\n')
    new_lines = []

    for i, line in enumerate(lines):
        new_lines.append(line)

        # If this line defines a source with an 'id'
        if "'id':" in line and '{' in line:
            # Extract the id value
            id_part = line.split("'id':")[1].split(',')[0].strip().strip("'").strip('"')

            # Check if this source is implemented
            is_implemented = id_part in IMPLEMENTED_SOURCES

            # Check if next line already has 'implemented' key
            if i + 1 < len(lines) and "'implemented':" not in lines[i + 1]:
                # Find the indentation level
                indent = len(line) - len(line.lstrip())

                # If line ends with }, add before the }
                if line.rstrip().endswith('},'):
                    # Remove the }, from current line
                    new_lines[-1] = line.rstrip()[:-2] + ','
                    # Add implemented flag
                    new_lines.append(' ' * indent + f" 'implemented': {str(is_implemented)}}},")
                elif line.rstrip().endswith(','):
                    # Add implemented flag on next line
                    new_lines.append(' ' * indent + f" 'implemented': {str(is_implemented)},")

    # Write back
    with open('sources_data_updated.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))

    print(f"[OK] Updated sources_data.py")
    print(f"[OK] {len(IMPLEMENTED_SOURCES)} sources marked as implemented: True")
    print(f"[OK] Remaining sources marked as implemented: False")
    print(f"\n[INFO] Review sources_data_updated.py before replacing original")

if __name__ == '__main__':
    update_sources_data()
