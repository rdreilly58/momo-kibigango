#!/bin/bash
# session-watchdog.sh — Session Staleness Monitor & Reconnect Guard
#
# Runs every 60 min (2x the 30min heartbeat interval).
# If the main session hasn't responded in >60 min, sends a Telegram alert
# and attempts to wake the session via openclaw agent.
#
# Usage: bash session-watchdog.sh [--force]
# Cron:  0 * * * * bash ~/.openclaw/workspace/scripts/session-watchdog.sh >> ~/.openclaw/logs/session-watchdog.log 2>&1

set -Eeuo pipefail

# ── Config ──────────────────────────────────────────────────────────────────
SESSIONS_FILE="$HOME/.openclaw/agents/main/sessions/sessions.json"
# Check multiple session keys — if ANY is recent, the agent is alive
# agent:main:main is the web/desktop UI session (often stale when using Telegram/cron)
# We consider the agent alive if any of these updated recently
SESSION_KEYS=("agent:main:main" "agent:main:main:heartbeat" "agent:main:telegram:direct:8755120444")
STALE_THRESHOLD_SEC=3600        # 60 min = 2x 30min heartbeat
WARN_THRESHOLD_SEC=2700         # 45 min = warn (no alert yet)
LOG_DIR="$HOME/.openclaw/logs"
LOG_FILE="$LOG_DIR/session-watchdog.log"
find "$LOG_DIR" -name "session-watchdog*.log" -mtime +30 -delete 2>/dev/null || true
WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# ── Idempotency guard: once per hour ─────────────────────────────────────────
# ── Always write heartbeat on exit ───────────────────────────────────────────
trap 'bash /Users/rreilly/.openclaw/workspace/scripts/cron-heartbeat.sh session-watchdog $?' EXIT

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

# ── Read updatedAt — pick the MOST RECENT across all watched keys ─────────────
UPDATED_MS=$(python3 -c "
import json, sys
keys = ['agent:main:main', 'agent:main:main:heartbeat', 'agent:main:telegram:direct:8755120444']
try:
    d = json.load(open('$SESSIONS_FILE'))
    best = 0
    for k in keys:
        ts = int(d.get(k, {}).get('updatedAt', 0))
        if ts > best:
            best = ts
    print(best)
except Exception as e:
    print(0)
" 2>/dev/null || echo 0)

if [ "$UPDATED_MS" -eq 0 ]; then
  echo "[$TIMESTAMP] [watchdog] ⚠️  Could not read updatedAt from any watched session"
  send_telegram "⚠️ <b>OpenClaw Watchdog</b>: Could not read any session timestamp. Agent may not be running."
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

# Look up stale session in coordinator and mark failed
SESSION_ID="agent:main:main"
_TASK=$(python3 "$WORKSPACE/scripts/agent_coordinator.py" \
  find-session --session "$SESSION_ID" 2>/dev/null || echo '{}')
_TASK_ID=$(echo "$_TASK" | python3 -c \
  "import sys,json; d=json.load(sys.stdin); print(d.get('task',{}).get('id',''))" 2>/dev/null || true)
if [ -n "$_TASK_ID" ]; then
  python3 "$WORKSPACE/scripts/agent_coordinator.py" \
    fail --id "$_TASK_ID" \
    --error "Session $SESSION_ID stale >60m — watchdog triggered" \
    >/dev/null 2>&1 || true
fi

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

# 2. Emergency summarization — save whatever context we can before restart
echo "[$TIMESTAMP] [watchdog] Running emergency session summarizer..."
PYTHON="$WORKSPACE/venv/bin/python3"
SUMMARIZER="$WORKSPACE/scripts/session_summarizer.py"

# Build a stale-session context snapshot from available signals
STALE_CONTEXT="Session went stale after ${AGE_MIN} minutes of silence (last seen: ${LAST_SEEN}).

$(cat "$WORKSPACE/SESSION_CONTEXT.md" 2>/dev/null | head -40 | grep -v '^#\|^---\|^\*\*Purpose' || echo 'No SESSION_CONTEXT.md available.')

Recent commits: $(cd "$WORKSPACE" && git log --oneline -5 2>/dev/null | head -5 || echo 'unavailable')

Daily log excerpt: $(cat "$WORKSPACE/memory/$(date +%Y-%m-%d).md" 2>/dev/null | tail -20 || echo 'no daily log')"

# Only summarize if we have enough context
if [ ${#STALE_CONTEXT} -gt 300 ]; then
  "$PYTHON" "$SUMMARIZER" \
    --text "$STALE_CONTEXT" \
    --no-context \
    --workspace "$WORKSPACE" \
    >> "$LOG_DIR/session-watchdog.log" 2>&1 && \
    echo "[$TIMESTAMP] [watchdog] ✅ Emergency summarizer wrote to daily notes + db" || \
    echo "[$TIMESTAMP] [watchdog] ⚠️  Emergency summarizer failed (non-fatal)"
else
  echo "[$TIMESTAMP] [watchdog] ⚠️  Insufficient context for emergency summary"
fi

# Also write a stale-session marker directly to daily notes (no API needed)
TODAY="$(date +%Y-%m-%d)"
HH_MM="$(date +%H:%M)"
DAILY_FILE="$WORKSPACE/memory/$TODAY.md"
if [ -f "$DAILY_FILE" ]; then
  echo "- [$HH_MM] ⚠️ Session went stale — watchdog detected ${AGE_MIN}m silence. Emergency summary attempted." \
    >> "$DAILY_FILE" 2>/dev/null || true
fi

# 3. Attempt to restart via openclaw agent (send to main agent session)
echo "[$TIMESTAMP] [watchdog] Sending restart ping via openclaw agent..."
PING_RESULT=$(openclaw agent \
  --agent main \
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

# NOTE: cron-heartbeat.sh is called via EXIT trap above — no explicit call needed here.

# Fail any tasks that have exceeded their timeout
_TIMED_OUT=$(python3 "$WORKSPACE/scripts/agent_coordinator.py" \
  timeout-check 2>/dev/null | python3 -c \
  "import sys,json; [print(t['id']) for t in json.load(sys.stdin).get('tasks',[])]" 2>/dev/null || true)
for _TID in $_TIMED_OUT; do
  python3 "$WORKSPACE/scripts/agent_coordinator.py" \
    fail --id "$_TID" --error "Exceeded agent_type timeout limit" \
    >/dev/null 2>&1 || true
done

# ── Dead-man heartbeat ───────────────────────────────────────────────────────
bash /Users/rreilly/.openclaw/workspace/scripts/cron-heartbeat.sh session-watchdog $?
