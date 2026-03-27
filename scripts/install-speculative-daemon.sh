#!/bin/bash
# Install Speculative Decoding as persistent daemon
# Runs on boot and keeps service alive

set -euo pipefail

echo "Installing Speculative Decoding persistent daemon..."
echo ""

# Create launch agent plist
PLIST_FILE=~/Library/LaunchAgents/com.momotaro.speculative-decoding.plist

# Unload if already exists
if launchctl list com.momotaro.speculative-decoding >/dev/null 2>&1; then
  echo "Unloading existing service..."
  launchctl unload "$PLIST_FILE" || true
  sleep 2
fi

# Load new plist
echo "Loading service..."
launchctl load "$PLIST_FILE"

# Verify
sleep 5
echo ""
echo "Checking status..."
if launchctl list com.momotaro.speculative-decoding >/dev/null 2>&1; then
  echo "✅ Service loaded in launchd"
else
  echo "⚠️ Service not showing in launchctl (might still be starting)"
fi

# Wait for service to be ready
echo ""
echo "Waiting for service to start (30 seconds)..."
for i in {1..30}; do
  if curl -s http://127.0.0.1:7779/health >/dev/null 2>&1; then
    echo "✅ Service is responding to requests"
    break
  fi
  echo -n "."
  sleep 1
done

echo ""
echo "Testing generation..."
response=$(curl -s -X POST http://127.0.0.1:7779/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test", "max_tokens": 50}')

if echo "$response" | jq -e '.generated_text' >/dev/null 2>&1; then
  echo "✅ Generation working"
else
  echo "❌ Generation failed"
  echo "Response: $response"
  exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ SPECULATIVE DECODING DAEMON INSTALLED"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Configuration:"
echo "  • Plist: $PLIST_FILE"
echo "  • Auto-start: YES (RunAtLoad=true)"
echo "  • Auto-restart: YES (KeepAlive=true)"
echo "  • Endpoint: http://127.0.0.1:7779"
echo "  • Logs: ~/.openclaw/logs/speculative-decoding*.log"
echo ""
echo "Next steps:"
echo "  1. Service will auto-start on next reboot"
echo "  2. Monitor logs: tail -f ~/.openclaw/logs/speculative-decoding.log"
echo "  3. Test: curl http://127.0.0.1:7779/health"
echo "  4. Generate: bash scripts/openclaw-spec.sh generate \"prompt\""
echo ""
echo "To uninstall:"
echo "  launchctl unload ~/Library/LaunchAgents/com.momotaro.speculative-decoding.plist"
echo ""
