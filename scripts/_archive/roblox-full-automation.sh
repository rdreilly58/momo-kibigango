#!/bin/bash
# roblox-full-automation.sh - Full pipeline: GitHub → Loaded Game → Auto-Test
# Usage: ./roblox-full-automation.sh <github-url> [auto-start]
#
# This script orchestrates:
# 1. Clone/update game from GitHub
# 2. Create proper .rbxl game file
# 3. Launch Studio with game
# 4. Wait 15 seconds
# 5. Capture and parse output
# 6. Report test results
#
# Example:
#   ./roblox-full-automation.sh https://github.com/rdreilly58/momotaro-roblox-rpg true

set -e

GITHUB_URL="$1"
AUTO_START="${2:-true}"

if [[ -z "$GITHUB_URL" ]]; then
    echo "❌ Usage: $0 <github-url> [auto-start:true/false]"
    echo ""
    echo "Examples:"
    echo "  $0 https://github.com/rdreilly58/momotaro-roblox-rpg"
    echo "  $0 https://github.com/rdreilly58/momotaro-roblox-rpg true"
    exit 1
fi

# Extract repo name
REPO_NAME=$(basename "$GITHUB_URL" .git)
GAME_DIR="$HOME/.games/$REPO_NAME"

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║        ROBLOX FULL AUTOMATION PIPELINE                        ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "🔗 GitHub: $GITHUB_URL"
echo "📁 Game Dir: $GAME_DIR"
echo "🚀 Auto-Start: $AUTO_START"
echo ""

# Phase 1: Clone/Update from GitHub
echo "═══════════════════════════════════════════════════════════════"
echo "PHASE 1: CLONE/UPDATE FROM GITHUB"
echo "═══════════════════════════════════════════════════════════════"
echo ""

if [[ -d "$GAME_DIR" ]]; then
    echo "📁 Repository already exists, updating..."
    cd "$GAME_DIR"
    git pull origin main 2>/dev/null || git pull origin master 2>/dev/null || echo "Note: Could not pull latest"
else
    echo "📥 Cloning repository..."
    mkdir -p "$HOME/.games"
    git clone "$GITHUB_URL" "$GAME_DIR"
fi

cd "$GAME_DIR"

if [[ ! -d "scripts" ]]; then
    echo "❌ ERROR: No 'scripts' directory in repository!"
    exit 1
fi

SCRIPT_COUNT=$(ls -1 scripts/*.lua 2>/dev/null | wc -l)
echo "✅ Repository ready - $SCRIPT_COUNT scripts found"
echo ""

# Phase 2: Run startup test with auto-capture
echo "═══════════════════════════════════════════════════════════════"
echo "PHASE 2: LAUNCH GAME & CAPTURE OUTPUT"
echo "═══════════════════════════════════════════════════════════════"
echo ""

bash ~/.openclaw/workspace/scripts/roblox-game-startup-test.sh "$GAME_DIR" "$GITHUB_URL"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "✅ AUTOMATION COMPLETE"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📊 Results Location:"
echo "   Test Results: $GAME_DIR/.test_results.txt"
echo "   Output Log: $GAME_DIR/.output_capture.txt"
echo "   Startup Log: $GAME_DIR/.startup.log"
echo ""
echo "📖 To view results:"
echo "   cat $GAME_DIR/.test_results.txt"
echo ""
echo "Studio window is still open for manual testing."
echo "Close when done."
echo ""
