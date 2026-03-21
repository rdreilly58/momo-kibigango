#!/bin/bash
# automated-test-workflow.sh - Complete automated testing workflow
# Loads game, validates, opens Studio, and provides test instructions

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${BLUE}ℹ${NC} $1"; }
success() { echo -e "${GREEN}✓${NC} $1"; }
error() { echo -e "${RED}✗${NC} $1"; exit 1; }

# Parse arguments
REPO="${1:-https://github.com/rdreilly58/momotaro-roblox-rpg.git}"
GAME_NAME="${2:-Momotaro RPG}"
OUTPUT_DIR="$HOME/.games/$(basename "$REPO" .git)"

echo ""
echo "╔════════════════════════════════════════╗"
echo "║  Roblox Game Test Automation Workflow  ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Step 1: Load and validate game
log "Step 1/4: Loading and validating game..."
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.."

bash "$SKILL_DIR/scripts/load-github-game.sh" \
    --repo "$REPO" \
    --game-name "$GAME_NAME" \
    --output-dir "$OUTPUT_DIR" \
    --validate-only

success "Game loaded and validated"

# Step 2: Verify plugin installation
log "Step 2/4: Checking plugin installation..."
PLUGIN_DIR="$HOME/Library/Application Support/Roblox/Plugins"

if [[ -f "$PLUGIN_DIR/TestAutomation.lua" ]]; then
    success "Test automation plugin installed"
else
    log "Plugin not found - installing..."
    bash "$SKILL_DIR/scripts/install-plugin.sh"
    success "Plugin installed"
fi

# Step 3: Open Studio and wait
log "Step 3/4: Opening Roblox Studio..."
if [[ -d "/Applications/RobloxStudio.app" ]]; then
    open -a "Roblox Studio" "$OUTPUT_DIR" &
    sleep 3
    success "Studio launched"
else
    error "Roblox Studio not found in /Applications"
fi

# Step 4: Display test instructions
echo ""
log "Step 4/4: Running automated tests..."
echo ""
echo "╔════════════════════════════════════════╗"
echo "║       AUTOMATED TEST INSTRUCTIONS      ║"
echo "╚════════════════════════════════════════╝"
echo ""
echo "📋 In Roblox Studio, follow these steps:"
echo ""
echo "1️⃣  Import Scripts into ServerScriptService:"
echo "   • Open ServerScriptService"
echo "   • Right-click → Insert Object → Script"
echo "   • Copy/paste each script from: $OUTPUT_DIR/scripts/"
echo ""
echo "2️⃣  Run Automated Tests:"
echo "   • Look for 'Game Testing' toolbar at top"
echo "   • Click 'Run Game Tests' button"
echo "   • Monitor Output window for results"
echo ""
echo "3️⃣  View Test Results:"
echo "   • Output shows real-time progress"
echo "   • Test report printed to console"
echo "   • Check for errors and warnings"
echo ""
echo "4️⃣  Debug Failures (if any):"
echo "   • Review error messages in Output"
echo "   • Check script names match expected"
echo "   • Ensure game structure is correct"
echo ""
echo "📂 Game location: $OUTPUT_DIR"
echo "📄 Report location: $OUTPUT_DIR/LOAD_REPORT.md"
echo ""
echo "╔════════════════════════════════════════╗"
echo "║     Automated Testing is Ready!        ║"
echo "╚════════════════════════════════════════╝"
echo ""

success "Complete workflow ready - follow instructions in Studio"
