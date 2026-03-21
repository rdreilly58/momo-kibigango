#!/bin/bash
# load-game-from-github.sh - Clone GitHub repo and load game in Studio
# Usage: ./load-game-from-github.sh <github-url> [output-dir]
# Example: ./load-game-from-github.sh https://github.com/rdreilly58/momotaro-roblox-rpg

set -e

GITHUB_URL="$1"
OUTPUT_DIR="${2:-$HOME/.games}"

if [[ -z "$GITHUB_URL" ]]; then
    echo "❌ Usage: $0 <github-url> [output-dir]"
    echo "Example: $0 https://github.com/rdreilly58/momotaro-roblox-rpg"
    exit 1
fi

# Extract repo name from URL
REPO_NAME=$(basename "$GITHUB_URL" .git)
GAME_DIR="$OUTPUT_DIR/$REPO_NAME"

echo "🎮 Loading game from GitHub..."
echo "Repository: $GITHUB_URL"
echo "Target directory: $GAME_DIR"
echo ""

# Clone if not exists
if [[ -d "$GAME_DIR" ]]; then
    echo "📁 Updating existing repository..."
    cd "$GAME_DIR"
    git pull origin main 2>/dev/null || git pull origin master 2>/dev/null || true
else
    echo "📥 Cloning repository..."
    mkdir -p "$OUTPUT_DIR"
    git clone "$GITHUB_URL" "$GAME_DIR"
fi

cd "$GAME_DIR"

# Check for scripts directory
if [[ ! -d "scripts" ]]; then
    echo "⚠️  No 'scripts' directory found in repo!"
    echo "Expected structure: repo/scripts/*.lua"
    exit 1
fi

echo "✅ Repository ready: $GAME_DIR"
echo ""
echo "📋 Scripts found:"
ls -1 scripts/*.lua 2>/dev/null | sed 's/^/   📄 /' || echo "   (none)"
echo ""
echo "Next: Run game startup automation"
echo "  bash run-game-with-output-capture.sh '$GAME_DIR'"
