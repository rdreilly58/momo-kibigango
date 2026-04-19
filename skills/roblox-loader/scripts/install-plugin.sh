#!/bin/bash
# install-plugin.sh - Install Roblox Test Automation plugin

set -e

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    PLUGIN_DIR="$HOME/Library/Application Support/Roblox/Plugins"
    OS="macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    PLUGIN_DIR="$HOME/.local/share/Roblox/Plugins"
    OS="Linux"
elif [[ "$OSTYPE" == "msys" ]]; then
    PLUGIN_DIR="$APPDATA/Roblox/Plugins"
    OS="Windows"
else
    echo "❌ Unknown OS: $OSTYPE"
    exit 1
fi

echo "🎮 Roblox Test Automation Plugin Installer"
echo "=========================================="
echo "OS: $OS"
echo "Plugin directory: $PLUGIN_DIR"
echo ""

# Get plugin source
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_SRC="$(dirname "$SCRIPT_DIR")/plugins/TestAutomation.lua"

if [[ ! -f "$PLUGIN_SRC" ]]; then
    echo "❌ ERROR: Plugin source not found: $PLUGIN_SRC"
    exit 1
fi

# Create plugin directory
mkdir -p "$PLUGIN_DIR"
echo "✓ Plugin directory created"

# Copy plugin
cp "$PLUGIN_SRC" "$PLUGIN_DIR/TestAutomation.lua"
echo "✓ Plugin installed: $PLUGIN_DIR/TestAutomation.lua"

# Verify installation
if [[ -f "$PLUGIN_DIR/TestAutomation.lua" ]]; then
    echo ""
    echo "✅ Installation successful!"
    echo ""
    echo "Next steps:"
    echo "1. Close Roblox Studio (if open)"
    echo "2. Reopen Roblox Studio"
    echo "3. Look for 'Game Testing' toolbar"
    echo "4. Click 'Run Game Tests' button to test a loaded game"
    echo ""
else
    echo "❌ Installation failed - plugin not found after copy"
    exit 1
fi
