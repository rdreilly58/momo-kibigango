#!/bin/bash
# gpu-startup-notify.sh
# Wrapper that runs GPU health check and sends result to Telegram via OpenClaw
# Called by cron @reboot
# With retry logic: GPU instance may still be booting when Mac comes up

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Retry logic: AWS instances take 1-3 minutes to fully boot
# First attempt after 30 seconds, then retry every 10 seconds up to 3 minutes
MAX_RETRIES=18  # ~3 minutes total (30s + 18*10s)
RETRY_INTERVAL=10
INITIAL_DELAY=30

echo "🔄 GPU health check starting (with retry logic)..." >> ~/.openclaw/logs/gpu-startup.log

sleep "$INITIAL_DELAY"

for attempt in $(seq 1 $MAX_RETRIES); do
  HEALTH_CHECK_OUTPUT=$("$SCRIPT_DIR/gpu-health-check-quick.sh" 2>&1)
  EXIT_CODE=$?
  
  if [ $EXIT_CODE -eq 0 ]; then
    # Success on this attempt
    echo "✅ GPU check succeeded on attempt $attempt" >> ~/.openclaw/logs/gpu-startup.log
    break
  fi
  
  if [ $attempt -lt $MAX_RETRIES ]; then
    echo "⏳ Attempt $attempt failed, retrying in ${RETRY_INTERVAL}s..." >> ~/.openclaw/logs/gpu-startup.log
    sleep "$RETRY_INTERVAL"
  else
    echo "❌ GPU check failed after $MAX_RETRIES attempts" >> ~/.openclaw/logs/gpu-startup.log
  fi
done

# Log the output
LOG_FILE="$HOME/.openclaw/logs/gpu-startup.log"
mkdir -p "$(dirname "$LOG_FILE")"
{
  echo "=== GPU Startup Check ==="
  date
  echo "$HEALTH_CHECK_OUTPUT"
  echo "Exit code: $EXIT_CODE"
  echo ""
} >> "$LOG_FILE"

# Extract status (first line contains ✅ or ❌)
if echo "$HEALTH_CHECK_OUTPUT" | head -1 | grep -q "^✅"; then
  STATUS="✅ GPU offload startup OK"
  DETAILS="GPU instance is ready for inference"
else
  STATUS="❌ GPU offload setup failed"
  DETAILS=$(echo "$HEALTH_CHECK_OUTPUT" | head -3 | tail -1)
fi

# Store message for OpenClaw to pick up
MESSAGE_FILE="/tmp/gpu-status-$$.txt"
cat > "$MESSAGE_FILE" << EOF
$STATUS

$HEALTH_CHECK_OUTPUT

---
Logged at: $(date)
Check: tail -20 ~/.openclaw/logs/gpu-startup.log
EOF

# Print to stdout (cron will capture via the tee in crontab)
cat "$MESSAGE_FILE"

# Note: Message delivery to Telegram happens via cron job delivery callback
# The actual message sending is handled by OpenClaw's heartbeat or cron delivery system

rm -f "$MESSAGE_FILE"
exit $EXIT_CODE
