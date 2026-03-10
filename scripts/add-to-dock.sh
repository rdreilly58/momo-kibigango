#!/bin/bash
# add-to-dock.sh — Add OpenClawGateway to macOS Dock

# Kill Dock to allow modifications
killall Dock

sleep 1

# Use Python to modify the Dock plist directly
python3 << 'PYTHON'
import os
import plistlib

dock_plist = os.path.expanduser("~/Library/Preferences/com.apple.dock.plist")
app_path = "/Applications/OpenClawGateway.app"

# Load Dock preferences
with open(dock_plist, 'rb') as f:
    dock = plistlib.load(f)

# Check if app is already in Dock
persistent_apps = dock.get('persistent-apps', [])
app_exists = any(app.get('tile-data', {}).get('file-label') == 'OpenClawGateway' 
                 for app in persistent_apps if app.get('tile-data'))

if not app_exists:
    # Create dock item
    dock_item = {
        'tile-data': {
            'file-label': 'OpenClawGateway',
            'file-type': 41,
            'file-mod-date': 0
        },
        'tile-type': 'file-tile'
    }
    
    # Add to persistent apps
    dock['persistent-apps'].append(dock_item)
    
    # Save updated plist
    with open(dock_plist, 'wb') as f:
        plistlib.dump(dock, f)
    
    print("[dock] ✓ OpenClawGateway added to Dock")
else:
    print("[dock] Already in Dock")

PYTHON

sleep 1

# Relaunch Dock
open -a Dock

sleep 2

echo "✓ Dock updated"
echo "✓ OpenClawGateway added to Dock with peach icon! 🍑"
