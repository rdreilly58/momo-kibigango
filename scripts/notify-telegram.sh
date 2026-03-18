#!/bin/bash
# notify-telegram.sh
# Send message to Telegram channel via OpenClaw sessions_send
# Usage: ./notify-telegram.sh "Message text"

MESSAGE="$1"
CHANNEL="8755120444"  # Bob's Telegram ID

if [ -z "$MESSAGE" ]; then
  echo "Usage: $0 \"message text\""
  exit 1
fi

# Use OpenClaw's sessions_send via CLI if available, otherwise log
if command -v openclaw &> /dev/null; then
  openclaw message send --channel "$CHANNEL" --text "$MESSAGE" 2>/dev/null || echo "Failed to send via openclaw"
else
  # Fallback: Try to use the CLI that might be available
  # This is a fallback; in production, you'd use the cron job approach
  echo "$MESSAGE" | logger -t gpu-health -p local0.info
fi
