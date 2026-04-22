#!/bin/bash
# session-stop-hook.sh — Run session summarizer after agent stop
#
# Registered as a Stop hook in ~/.claude/settings.json
# Input: reads STDIN for conversation context (Claude Code hook protocol)
# Guard: skip if transcript <200 chars; skip if last summary <10 min ago
#
# NEVER fails loudly — agent stop must not be affected by hook errors.
# Always exits 0.

WORKSPACE="${OPENCLAW_TEST_WORKSPACE:-$HOME/.openclaw/workspace}"
PYTHON="$WORKSPACE/venv/bin/python3"
SUMMARIZER="$WORKSPACE/scripts/session_summarizer.py"
LOG_DIR="$HOME/.openclaw/logs"
LOG_FILE="$LOG_DIR/session-summarizer.log"
LAST_SUMMARY_STAMP="$WORKSPACE/memory/.last-summary-run"
MIN_INTERVAL=600  # 10 minutes in seconds

mkdir -p "$LOG_DIR"

_log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] [stop-hook] $*" >> "$LOG_FILE" 2>/dev/null || true
}

_log "Hook triggered"

# ── 1. Read stdin (Claude Code passes hook data as JSON) ─────────────────────
# Read with a short timeout to avoid blocking
STDIN_DATA=""
if read -t 5 -r STDIN_DATA 2>/dev/null; then
  # Got first line; try to read more (non-blocking)
  while IFS= read -t 0.1 -r line 2>/dev/null; do
    STDIN_DATA="${STDIN_DATA}${line}"
  done
fi

# ── 2. Extract transcript from JSON payload ──────────────────────────────────
TRANSCRIPT=""
if [ -n "$STDIN_DATA" ]; then
  # Try to extract transcript field with Python (safest JSON parsing)
  TRANSCRIPT=$(echo "$STDIN_DATA" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    t = data.get('transcript', '')
    print(t, end='')
except Exception:
    pass
" 2>/dev/null || true)
fi

# ── 3. Guard: transcript too short ──────────────────────────────────────────
TRANSCRIPT_LEN=${#TRANSCRIPT}
_log "Transcript length: ${TRANSCRIPT_LEN} chars"

if [ "$TRANSCRIPT_LEN" -lt 200 ]; then
  _log "Transcript too short (${TRANSCRIPT_LEN} < 200) — skipping"
  exit 0
fi

# ── 4. Guard: last summary was recent ────────────────────────────────────────
if [ -f "$LAST_SUMMARY_STAMP" ]; then
  LAST_RUN=$(cat "$LAST_SUMMARY_STAMP" 2>/dev/null || echo 0)
  NOW=$(date +%s)
  ELAPSED=$(( NOW - LAST_RUN ))
  if [ "$ELAPSED" -lt "$MIN_INTERVAL" ]; then
    _log "Last summary was ${ELAPSED}s ago (< ${MIN_INTERVAL}s) — skipping"
    exit 0
  fi
fi

# ── 5. Run summarizer ────────────────────────────────────────────────────────
_log "Running session_summarizer.py (transcript: ${TRANSCRIPT_LEN} chars)"

# Write timestamp before calling (prevents re-entry on long runs)
date +%s > "$LAST_SUMMARY_STAMP" 2>/dev/null || true

EXIT_CODE=0
"$PYTHON" "$SUMMARIZER" --text "$TRANSCRIPT" \
  >> "$LOG_FILE" 2>&1 || EXIT_CODE=$?

_log "session_summarizer.py exited with code ${EXIT_CODE}"

# ── 6. Complete coordinator task for this session ─────────────────────────────
SESSION_ID=$(echo "$STDIN_DATA" | python3 -c \
  "import sys,json; print(json.load(sys.stdin).get('session_id',''))" 2>/dev/null || true)

if [ -n "$SESSION_ID" ]; then
  _TASK=$(python3 "$WORKSPACE/scripts/agent_coordinator.py" \
    find-session --session "$SESSION_ID" 2>/dev/null || echo '{}')
  _TASK_ID=$(echo "$_TASK" | python3 -c \
    "import sys,json; d=json.load(sys.stdin); print(d.get('task',{}).get('id',''))" 2>/dev/null || true)
  if [ -n "$_TASK_ID" ]; then
    python3 "$WORKSPACE/scripts/agent_coordinator.py" \
      complete --id "$_TASK_ID" --summary "Session ended cleanly" \
      >/dev/null 2>&1 || true
  fi
fi

# ── 7. Always exit 0 ─────────────────────────────────────────────────────────
exit 0
