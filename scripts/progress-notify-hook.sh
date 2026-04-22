#!/bin/bash
# progress-notify-hook.sh — PreToolUse Telegram progress ping
#
# Registered as a PreToolUse hook in ~/.claude/settings.json
# Fires before each tool use. Sends a Telegram message when a "heavy" tool
# is about to run AND Claude has been silent for >= SILENCE_THRESHOLD seconds.
#
# Purpose: Lets Bob know the system is active, not crashed, during long operations.
# Heavy tools: Agent, Bash, mcp__* (these are the silence culprits)
# Throttle: one notification per SILENCE_THRESHOLD seconds max
#
# Requires: TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID in config/briefing.env
# Never fails loudly — always exits 0.

WORKSPACE="${OPENCLAW_TEST_WORKSPACE:-$HOME/.openclaw/workspace}"
ENV_FILE="$WORKSPACE/config/briefing.env"
LOG_DIR="${OPENCLAW_TEST_LOG_DIR:-$HOME/.openclaw/logs}"
LOG_FILE="$LOG_DIR/progress-notify.log"
STATE_FILE="$LOG_DIR/progress-notify-last.txt"
SILENCE_THRESHOLD="${OPENCLAW_TEST_SILENCE_THRESHOLD:-75}"  # seconds — only ping if silent at least this long

# Heavy tools that indicate a long-running operation is starting
HEAVY_TOOLS_PATTERN="^(Agent|Bash|mcp__)"

mkdir -p "$LOG_DIR"

_log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] [progress-notify] $*" >> "$LOG_FILE" 2>/dev/null || true
}

# ── 1. Load Telegram credentials ──────────────────────────────────────────────
if [ -f "$ENV_FILE" ]; then
  # shellcheck source=/dev/null
  source "$ENV_FILE" 2>/dev/null || true
fi

# No-op if credentials not configured
if [ -z "${TELEGRAM_BOT_TOKEN:-}" ] || [ -z "${TELEGRAM_CHAT_ID:-}" ]; then
  exit 0
fi

# ── 2. Read stdin (hook payload) ──────────────────────────────────────────────
STDIN_DATA=""
if read -t 3 -r line 2>/dev/null; then
  STDIN_DATA="$line"
  while IFS= read -t 0.1 -r line 2>/dev/null; do
    STDIN_DATA="${STDIN_DATA}${line}"
  done
fi

if [ -z "$STDIN_DATA" ]; then
  exit 0
fi

# ── 3. Parse tool_name from payload ──────────────────────────────────────────
TOOL_NAME=$(python3 -c "
import sys, json
try:
    d = json.loads('''$STDIN_DATA''')
    print(d.get('tool_name', ''), end='')
except Exception: pass
" 2>/dev/null || true)

# Fallback: try via stdin pipe if inline substitution failed
if [ -z "$TOOL_NAME" ] && [ -n "$STDIN_DATA" ]; then
  TOOL_NAME=$(echo "$STDIN_DATA" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('tool_name', ''), end='')
except Exception: pass
" 2>/dev/null || true)
fi

if [ -z "$TOOL_NAME" ]; then
  exit 0
fi

# ── 4. Guard: only for heavy tools ───────────────────────────────────────────
if ! echo "$TOOL_NAME" | grep -qE "$HEAVY_TOOLS_PATTERN"; then
  exit 0
fi

# ── 5. Guard: throttle by silence window ─────────────────────────────────────
NOW=$(date +%s)
LAST_NOTIFY=0

if [ -f "$STATE_FILE" ]; then
  LAST_NOTIFY=$(cat "$STATE_FILE" 2>/dev/null || echo 0)
fi

ELAPSED=$((NOW - LAST_NOTIFY))

if [ "$ELAPSED" -lt "$SILENCE_THRESHOLD" ]; then
  _log "Throttled: ${ELAPSED}s since last notify (threshold=${SILENCE_THRESHOLD}s, tool=${TOOL_NAME})"
  exit 0
fi

# ── 6. Build message ──────────────────────────────────────────────────────────
# Friendly label for known tool types
case "$TOOL_NAME" in
  Agent)       TOOL_LABEL="spawning subagent" ;;
  Bash)        TOOL_LABEL="running shell command" ;;
  mcp__openclaw__sessions_spawn) TOOL_LABEL="spawning agent session" ;;
  mcp__*)      TOOL_LABEL="calling ${TOOL_NAME#mcp__openclaw__}" ;;
  *)           TOOL_LABEL="running ${TOOL_NAME}" ;;
esac

if [ "$ELAPSED" -ge 3600 ]; then
  ELAPSED_MSG="$((ELAPSED / 3600))h $(( (ELAPSED % 3600) / 60 ))m elapsed"
elif [ "$ELAPSED" -ge 60 ]; then
  ELAPSED_MSG="$((ELAPSED / 60))m $((ELAPSED % 60))s elapsed"
else
  ELAPSED_MSG="${ELAPSED}s elapsed"
fi

MESSAGE="⚙️ Still working — ${TOOL_LABEL} (${ELAPSED_MSG})"

# ── 7. Send Telegram notification ────────────────────────────────────────────
_log "Sending: $MESSAGE (tool=$TOOL_NAME)"

if command -v jq &>/dev/null; then
  BODY=$(jq -n \
    --arg text "$MESSAGE" \
    --arg chat_id "$TELEGRAM_CHAT_ID" \
    '{chat_id: $chat_id, text: $text}')
else
  ESCAPED="${MESSAGE//\"/\\\"}"
  BODY="{\"chat_id\":\"${TELEGRAM_CHAT_ID}\",\"text\":\"${ESCAPED}\"}"
fi

curl -fsS -m 30 --retry 2 \
  -H 'Content-Type: application/json' \
  -d "$BODY" \
  "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  >/dev/null 2>&1 || _log "curl failed (non-fatal)"

# ── 8. Update last-notify timestamp ──────────────────────────────────────────
echo "$NOW" > "$STATE_FILE"

_log "Ping sent for tool=$TOOL_NAME elapsed=${ELAPSED}s"

exit 0
