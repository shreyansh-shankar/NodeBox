import os
import requests
import xml.etree.ElementTree as ET

# Create icons directory
os.makedirs("assets/icons", exist_ok=True)

# Base URL for Feather Icons
base_url = "https://raw.githubusercontent.com/feathericons/feather/master/icons/"

# Icons needed
icons = [
    "plus.svg",
    "download.svg",
    "upload.svg",
    "x.svg",
    "file-text.svg",
    "clock.svg",
    "terminal.svg",
    "activity.svg",
    "info.svg",
    "plus-circle.svg",
    "package.svg",
    "file.svg",
    "home.svg",
    "database.svg",
    "bar-chart-2.svg",
    "folder.svg",
    "globe.svg",
    "type.svg",
    "cpu.svg",
    "bell.svg",
]

def make_icon_white(svg_content):
    """Convert SVG to white by modifying stroke attribute"""
    # Parse the SVG
    try:
        # Add XML declaration if missing
        if not svg_content.startswith('<?xml'):
            svg_content = '<?xml version="1.0" encoding="UTF-8"?>' + svg_content

        root = ET.fromstring(svg_content)

        # Update all stroke attributes to white
        for elem in root.iter():
            if 'stroke' in elem.attrib:
                elem.attrib['stroke'] = 'white'
            if 'fill' in elem.attrib and elem.attrib['fill'] != 'none':
                elem.attrib['fill'] = 'white'

        # Return modified SVG
        return ET.tostring(root, encoding='unicode')
    except:
        # Fallback: simple string replacement
        svg_content = svg_content.replace('stroke="currentColor"', 'stroke="white"')
        svg_content = svg_content.replace('stroke="#000"', 'stroke="white"')
        svg_content = svg_content.replace('stroke="#000000"', 'stroke="white"')
        svg_content = svg_content.replace('stroke="black"', 'stroke="white"')
        return svg_content

for icon in icons:
    url = base_url + icon
    response = requests.get(url)
    if response.status_code == 200:
        # Convert to white
        white_svg = make_icon_white(response.text)

        # Save white version
        with open(f"assets/icons/{icon}", "w", encoding="utf-8") as f:
            f.write(white_svg)
        print(f"✓ Downloaded and converted {icon} to white")
    else:
        print(f"✗ Failed to download {icon}")

print("All white icons downloaded!")