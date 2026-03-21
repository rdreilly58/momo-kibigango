#!/bin/bash
# open-game-in-studio.sh - Opens a game in Roblox Studio with instructions
# Usage: ./open-game-in-studio.sh <game_folder>

set -e

GAME_DIR="$1"
[[ -z "$GAME_DIR" ]] && GAME_DIR="$HOME/.games/momotaro-rpg"

STUDIO_APP="/Applications/RobloxStudio.app/Contents/MacOS/RobloxStudio"

if [[ ! -d "$GAME_DIR" ]]; then
    echo "❌ ERROR: Game directory not found: $GAME_DIR"
    exit 1
fi

if [[ ! -x "$STUDIO_APP" ]]; then
    echo "❌ ERROR: Roblox Studio not found at $STUDIO_APP"
    exit 1
fi

echo "🎮 Opening Roblox Studio..."
echo ""
echo "⚠️  IMPORTANT: Studio will open with a BLANK place."
echo "   You must manually add the scripts."
echo ""

# Kill any existing Roblox Studio process
pkill -f RobloxStudio || true
sleep 1

# Launch Studio with no place (opens blank)
"$STUDIO_APP" &
STUDIO_PID=$!

sleep 5

echo ""
echo "╔════════════════════════════════════════════╗"
echo "║   ROBLOX STUDIO OPENED - SETUP REQUIRED    ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "📋 FOLLOW THESE STEPS:"
echo ""
echo "1️⃣  CREATE A NEW BLANK PLACE"
echo "    • File → New"
echo "    • Or use the Start Page to create a new place"
echo ""
echo "2️⃣  ADD SCRIPTS TO SERVERSCRIPTSERVICE"
echo ""
echo "    For each script below:"
echo "    • Right-click ServerScriptService in Explorer"
echo "    • Insert Object → Script"
echo "    • Replace script content with file contents"
echo ""
echo "    Scripts to add:"
ls -1 "$GAME_DIR/scripts/"*.lua | while read f; do
    echo "      📄 $(basename "$f")"
done
echo ""
echo "3️⃣  SAVE THE PLACE"
echo "    • File → Save As"
echo "    • Save as: Momotaro RPG"
echo ""
echo "4️⃣  TEST THE GAME"
echo "    • Press F5 to run the game in Studio"
echo "    • Use Plugin → Game Testing → Run Game Tests"
echo ""
echo "5️⃣  PUBLISH (optional)"
echo "    • File → Save to Roblox"
echo ""
echo "📂 Script files location:"
echo "   $GAME_DIR/scripts/"
echo ""
echo "💡 TIP: Open a second Terminal window and run:"
echo "   cat $GAME_DIR/scripts/[scriptname].lua"
echo "   Then copy/paste the content into Studio"
echo ""

# Wait for Studio process
wait $STUDIO_PID 2>/dev/null || true

echo "Studio closed."
