#!/bin/bash
# roblox-full-automation-integrated.sh - Full pipeline with template.rbxl integration
# Usage: ./roblox-full-automation-integrated.sh <github-url> [auto-start]
#
# This script orchestrates:
# 1. Clone/update game from GitHub
# 2. Use template.rbxl from repo (instead of creating blank)
# 3. Launch Studio with game
# 4. Wait 15 seconds
# 5. Capture and parse output
# 6. Report test results
#
# Example:
#   ./roblox-full-automation-integrated.sh https://github.com/rdreilly58/momotaro-roblox-rpg true

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
echo "║        ROBLOX FULL AUTOMATION PIPELINE (INTEGRATED)            ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "🔗 GitHub: $GITHUB_URL"
echo "📁 Game Dir: $GAME_DIR"
echo "🚀 Auto-Start: $AUTO_START"
echo "🎮 Using: template.rbxl (integrated)"
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

# Verify required files
if [[ ! -d "scripts" ]]; then
    echo "❌ ERROR: No 'scripts' directory in repository!"
    exit 1
fi

if [[ ! -f "template.rbxl" ]]; then
    echo "❌ ERROR: No 'template.rbxl' file in repository!"
    echo "   Please ensure the repository contains a valid template.rbxl"
    exit 1
fi

SCRIPT_COUNT=$(ls -1 scripts/*.lua 2>/dev/null | wc -l)
echo "✅ Repository ready"
echo "   - Scripts found: $SCRIPT_COUNT"
echo "   - Template: template.rbxl ($(wc -l < template.rbxl) lines)"
echo ""

# Phase 2: Run startup test with template.rbxl
echo "═══════════════════════════════════════════════════════════════"
echo "PHASE 2: LAUNCH GAME WITH TEMPLATE & CAPTURE OUTPUT"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Call the modified startup test script
bash ~/.openclaw/workspace/scripts/roblox-game-startup-test-integrated.sh "$GAME_DIR" "$GITHUB_URL"

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