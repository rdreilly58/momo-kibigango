#!/bin/bash
# session-watchdog.sh — Session Staleness Monitor & Reconnect Guard
#
# Runs every 60 min (2x the 30min heartbeat interval).
# If the main session hasn't responded in >60 min, sends a Telegram alert
# and attempts to wake the session via openclaw agent.
#
# Usage: bash session-watchdog.sh [--force]
# Cron:  0 * * * * bash ~/.openclaw/workspace/scripts/session-watchdog.sh >> ~/.openclaw/logs/session-watchdog.log 2>&1

set -uo pipefail

# ── Config ──────────────────────────────────────────────────────────────────
SESSIONS_FILE="$HOME/.openclaw/agents/main/sessions/sessions.json"
SESSION_KEY="agent:main:main"
STALE_THRESHOLD_SEC=3600        # 60 min = 2x 30min heartbeat
WARN_THRESHOLD_SEC=2700         # 45 min = warn (no alert yet)
LOG_DIR="$HOME/.openclaw/logs"
LOG_FILE="$LOG_DIR/session-watchdog.log"
WORKSPACE="$HOME/.openclaw/workspace"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# ── Idempotency guard: once per hour ─────────────────────────────────────────
LOCK_FILE="/tmp/session-watchdog-$(date +%Y-%m-%d-%H).lock"
if [ -f "$LOCK_FILE" ] && [ "${1:-}" != "--force" ]; then
  echo "[$TIMESTAMP] [watchdog] Already ran this hour (lock: $LOCK_FILE). Skipping."
  exit 0
fi
touch "$LOCK_FILE"

mkdir -p "$LOG_DIR"
echo "[$TIMESTAMP] [watchdog] Starting session watchdog check..."

# ── Read Telegram credentials from config.json ───────────────────────────────
TELEGRAM_BOT_TOKEN=$(python3 -c "
import json, sys
try:
    c = json.load(open('$HOME/.openclaw/config.json'))
    print(c.get('telegram', {}).get('botToken', ''))
except Exception as e:
    sys.exit(0)
" 2>/dev/null || true)

TELEGRAM_CHAT_ID=$(python3 -c "
import json, sys
try:
    c = json.load(open('$HOME/.openclaw/config.json'))
    print(c.get('telegram', {}).get('chatId', ''))
except Exception as e:
    sys.exit(0)
" 2>/dev/null || true)

send_telegram() {
  local text="$1"
  if [ -n "${TELEGRAM_BOT_TOKEN:-}" ] && [ -n "${TELEGRAM_CHAT_ID:-}" ]; then
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
      -d "chat_id=${TELEGRAM_CHAT_ID}" \
      -d "text=${text}" \
      -d "parse_mode=HTML" > /dev/null 2>&1 || true
  else
    echo "[$TIMESTAMP] [watchdog] ⚠️  No Telegram credentials — skipping alert"
  fi
}

# ── Check sessions.json exists ───────────────────────────────────────────────
if [ ! -f "$SESSIONS_FILE" ]; then
  echo "[$TIMESTAMP] [watchdog] ❌ sessions.json not found: $SESSIONS_FILE"
  send_telegram "⚠️ <b>OpenClaw Watchdog</b>: sessions.json missing — agent may not be running."
  exit 1
fi

# ── Read updatedAt for main session ──────────────────────────────────────────
UPDATED_MS=$(python3 -c "
import json, sys
try:
    d = json.load(open('$SESSIONS_FILE'))
    s = d.get('$SESSION_KEY', {})
    print(int(s.get('updatedAt', 0)))
except Exception as e:
    print(0)
" 2>/dev/null || echo 0)

if [ "$UPDATED_MS" -eq 0 ]; then
  echo "[$TIMESTAMP] [watchdog] ⚠️  Could not read updatedAt from session — session may be missing"
  send_telegram "⚠️ <b>OpenClaw Watchdog</b>: Could not read main session timestamp. Session key missing?"
  exit 1
fi

# ── Compute age ───────────────────────────────────────────────────────────────
NOW_MS=$(python3 -c "import time; print(int(time.time() * 1000))")
AGE_MS=$((NOW_MS - UPDATED_MS))
AGE_SEC=$((AGE_MS / 1000))
AGE_MIN=$((AGE_SEC / 60))

echo "[$TIMESTAMP] [watchdog] Main session age: ${AGE_MIN}m ${AGE_SEC}s (threshold: $((STALE_THRESHOLD_SEC / 60))m)"

# ── Healthy ───────────────────────────────────────────────────────────────────
if [ "$AGE_SEC" -lt "$WARN_THRESHOLD_SEC" ]; then
  echo "[$TIMESTAMP] [watchdog] ✅ Session healthy (age: ${AGE_MIN}m)"
  exit 0
fi

# ── Warning zone (45–60 min) ─────────────────────────────────────────────────
if [ "$AGE_SEC" -lt "$STALE_THRESHOLD_SEC" ]; then
  echo "[$TIMESTAMP] [watchdog] ⚠️  Session idle ${AGE_MIN}m — approaching stale threshold. Attempting wake..."
  # Gentle ping — no alert yet
  openclaw agent --message "WATCHDOG_PING: Still alive? Please respond HEARTBEAT_OK." --deliver > /dev/null 2>&1 || true
  exit 0
fi

# ── STALE ─────────────────────────────────────────────────────────────────────
echo "[$TIMESTAMP] [watchdog] ❌ Session STALE — last activity ${AGE_MIN}m ago. Alerting + attempting restart..."

# 1. Send Telegram alert
LAST_SEEN=$(python3 -c "
import datetime, sys
ts = $UPDATED_MS / 1000
dt = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
print(dt)
" 2>/dev/null || echo "unknown")

send_telegram "🚨 <b>OpenClaw Watchdog Alert</b>

Main session has been silent for <b>${AGE_MIN} minutes</b> (last seen: ${LAST_SEEN}).

Attempting automatic restart. If this message repeats, the session may need manual recovery."

# 2. Attempt to restart via openclaw agent
echo "[$TIMESTAMP] [watchdog] Sending restart ping via openclaw agent..."
PING_RESULT=$(openclaw agent \
  --message "WATCHDOG: Session detected stale after ${AGE_MIN}m silence. Please respond HEARTBEAT_OK and resume normal operation." \
  --deliver 2>&1) && {
  echo "[$TIMESTAMP] [watchdog] ✅ Restart ping delivered"
  send_telegram "✅ <b>OpenClaw Watchdog</b>: Restart ping delivered. Session should recover within 2–3 minutes."
} || {
  echo "[$TIMESTAMP] [watchdog] ❌ Restart ping failed: $PING_RESULT"
  send_telegram "❌ <b>OpenClaw Watchdog</b>: Restart ping FAILED. Manual intervention required.

Error: ${PING_RESULT:0:200}"
}

echo "[$TIMESTAMP] [watchdog] Done."
