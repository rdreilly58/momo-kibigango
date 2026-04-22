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
OPENCLAW_CONFIG="${OPENCLAW_TEST_OPENCLAW_CONFIG:-$HOME/.openclaw/config.json}"
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
# Primary source: ~/.openclaw/config.json (managed by openclaw gateway)
if [ -z "${TELEGRAM_BOT_TOKEN:-}" ] && [ -f "$OPENCLAW_CONFIG" ] && command -v python3 &>/dev/null; then
  TELEGRAM_BOT_TOKEN=$(python3 -c "
import json, sys
try:
    d = json.load(open('$OPENCLAW_CONFIG'))
    print(d.get('telegram', {}).get('botToken', ''), end='')
except Exception: pass
" 2>/dev/null || true)
  TELEGRAM_CHAT_ID=$(python3 -c "
import json, sys
try:
    d = json.load(open('$OPENCLAW_CONFIG'))
    print(d.get('telegram', {}).get('chatId', ''), end='')
except Exception: pass
" 2>/dev/null || true)
fi

# Fallback: briefing.env (legacy)
if [ -z "${TELEGRAM_BOT_TOKEN:-}" ] && [ -f "$ENV_FILE" ]; then
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

# ── 5. Guard: throttle by silence window (with mkdir lock to prevent concurrent sends) ──
# mkdir is atomic on POSIX — only one invocation wins; others exit silently
LOCK_DIR="${STATE_FILE}.lockdir"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

NOW=$(date +%s)
LAST_NOTIFY=0

if [ -f "$STATE_FILE" ]; then
  LAST_NOTIFY=$(cat "$STATE_FILE" 2>/dev/null || echo 0)
fi

ELAPSED=$((NOW - LAST_NOTIFY))

# Treat missing state file (epoch delta > 1 year) as "first run" — no elapsed display
FIRST_RUN=0
[ "$ELAPSED" -gt 31536000 ] && FIRST_RUN=1

if [ "$FIRST_RUN" -eq 0 ] && [ "$ELAPSED" -lt "$SILENCE_THRESHOLD" ]; then
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

if [ "$FIRST_RUN" -eq 1 ]; then
  MESSAGE="⚙️ Still working — ${TOOL_LABEL}"
elif [ "$ELAPSED" -ge 3600 ]; then
  ELAPSED_MSG="$((ELAPSED / 3600))h $(( (ELAPSED % 3600) / 60 ))m elapsed"
  MESSAGE="⚙️ Still working — ${TOOL_LABEL} (${ELAPSED_MSG})"
elif [ "$ELAPSED" -ge 60 ]; then
  ELAPSED_MSG="$((ELAPSED / 60))m $((ELAPSED % 60))s elapsed"
  MESSAGE="⚙️ Still working — ${TOOL_LABEL} (${ELAPSED_MSG})"
else
  MESSAGE="⚙️ Still working — ${TOOL_LABEL} (${ELAPSED}s elapsed)"
fi

# ── 7. Send Telegram notification ────────────────────────────────────────────
# Update timestamp before sending so concurrent invocations are blocked even if send is slow
echo "$NOW" > "$STATE_FILE"

_log "Sending: $MESSAGE (tool=$TOOL_NAME elapsed=${ELAPSED}s)"

# openclaw CLI routes through openclaw.json token — the only working delivery path
SENT=0
if command -v openclaw &>/dev/null && [ -n "${TELEGRAM_CHAT_ID:-}" ]; then
  if openclaw message send \
      --channel telegram \
      --target "$TELEGRAM_CHAT_ID" \
      --message "$MESSAGE" \
      >/dev/null 2>&1; then
    SENT=1
    _log "Sent via openclaw (tool=$TOOL_NAME)"
  else
    _log "openclaw send failed (non-fatal)"
  fi
fi

[ "$SENT" -eq 0 ] && _log "Notification not delivered (openclaw unavailable or failed)"

exit 0
