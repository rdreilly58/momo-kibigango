#!/bin/bash
# Start OpenClaw Gateway with Brave Search API key
# This bypasses the launchctl plist issue by directly starting the Gateway process
# with BRAVE_API_KEY in the environment

set -e

echo "🚀 Starting OpenClaw Gateway with Brave Search API..."
echo ""

# Set the API key
export BRAVE_API_KEY="REDACTED_BRAVE_API_TOKEN"

# Kill any existing Gateway process
pkill -f "openclaw.*gateway" 2>/dev/null || true
sleep 2

# Create logs directory if needed
mkdir -p ~/.openclaw/logs

# Start Gateway in background
echo "Starting process (PID will follow)..."
nohup /opt/homebrew/opt/node/bin/node /opt/homebrew/lib/node_modules/openclaw/dist/index.js gateway --port 18789 > ~/.openclaw/logs/gateway-manual.log 2>&1 &

# Wait for it to start
sleep 3

# Check if it started
if pgrep -f "openclaw.*gateway" > /dev/null; then
    PID=$(pgrep -f "openclaw.*gateway" | head -1)
    echo ""
    echo "✅ Gateway started successfully"
    echo "   PID: $PID"
    echo "   API Key: Set in environment"
    echo "   Port: 18789"
    echo "   Logs: ~/.openclaw/logs/gateway-manual.log"
    echo ""
    echo "Gateway is ready. You can now use web_search()!"
else
    echo ""
    echo "❌ Gateway failed to start"
    echo "Last 20 lines of log:"
    tail -20 ~/.openclaw/logs/gateway-manual.log
    exit 1
fi
