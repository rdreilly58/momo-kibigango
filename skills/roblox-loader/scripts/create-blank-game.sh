#!/bin/bash
# create-blank-game.sh - Create a blank Roblox game file (.rbxl)
# Usage: ./create-blank-game.sh /path/to/game/

set -e

OUTPUT_DIR="$1"
[[ -z "$OUTPUT_DIR" ]] && OUTPUT_DIR="."

GAME_FILE="$OUTPUT_DIR/game.rbxl"

echo "Creating blank Roblox game file..."

# Create a minimal .rbxl file (XML format inside ZIP)
# This is a barebones Roblox place file

mkdir -p /tmp/roblox_temp
cd /tmp/roblox_temp

# Create minimal RobloxLock.xml
cat > RobloxLock.xml << 'XMLEOF'
<?xml version="1.0" encoding="UTF-8" ?>
<roblox version="4">
</roblox>
XMLEOF

# Package as .rbxl (which is a gzip-compressed XML file)
gzip -c RobloxLock.xml > "$GAME_FILE" || echo "Note: Could not create .rbxl - using XML format instead"

# Fallback: Just copy the XML as .rbxl
if [[ ! -f "$GAME_FILE" ]]; then
    cp RobloxLock.xml "$GAME_FILE"
fi

cd - > /dev/null
rm -rf /tmp/roblox_temp

echo "✅ Blank game created: $GAME_FILE"
echo "Next: Open this in Roblox Studio and add scripts to ServerScriptService"
