#!/bin/bash
# session-checkpoint-hook.sh — PostToolUse mid-session summarization checkpoint
#
# Registered as a PostToolUse hook in ~/.claude/settings.json
# Fires after every tool use. Uses a per-session turn counter to trigger
# a summarization every CHECKPOINT_INTERVAL tool uses.
#
# Writes to: daily notes + ai-memory.db (NOT SESSION_CONTEXT.md — that's for Stop)
# Never writes SESSION_CONTEXT.md mid-session to avoid stomping live context.
#
# Why: The Stop hook only fires on clean session end. Crashes and timeouts
# produce no summary. Periodic checkpoints ensure work is captured regardless.
#
# NEVER fails loudly — always exits 0.

WORKSPACE="${OPENCLAW_TEST_WORKSPACE:-$HOME/.openclaw/workspace}"
PYTHON="$WORKSPACE/venv/bin/python3"
SUMMARIZER="$WORKSPACE/scripts/session_summarizer.py"
LOG_DIR="$HOME/.openclaw/logs"
LOG_FILE="$LOG_DIR/session-checkpoint.log"
COUNTER_DIR="$LOG_DIR/checkpoint-counters"
CHECKPOINT_INTERVAL=20   # summarize every N tool uses
MIN_TRANSCRIPT_CHARS=400 # skip if transcript too short

mkdir -p "$LOG_DIR" "$COUNTER_DIR"

_log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] [checkpoint] $*" >> "$LOG_FILE" 2>/dev/null || true
}

# ── 1. Read stdin ─────────────────────────────────────────────────────────────
STDIN_DATA=""
if read -t 3 -r STDIN_DATA 2>/dev/null; then
  while IFS= read -t 0.1 -r line 2>/dev/null; do
    STDIN_DATA="${STDIN_DATA}${line}"
  done
fi

# ── 2. Parse hook payload ─────────────────────────────────────────────────────
SESSION_ID=""
TRANSCRIPT_PATH=""

if [ -n "$STDIN_DATA" ]; then
  SESSION_ID=$(echo "$STDIN_DATA" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('session_id', ''), end='')
except Exception: pass
" 2>/dev/null || true)

  TRANSCRIPT_PATH=$(echo "$STDIN_DATA" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('transcript_path', ''), end='')
except Exception: pass
" 2>/dev/null || true)
fi

if [ -z "$SESSION_ID" ]; then
  _log "No session_id — skipping"
  exit 0
fi

# ── 3. Increment per-session turn counter ─────────────────────────────────────
COUNTER_FILE="$COUNTER_DIR/$SESSION_ID.count"
CURRENT_COUNT=0
if [ -f "$COUNTER_FILE" ]; then
  CURRENT_COUNT=$(cat "$COUNTER_FILE" 2>/dev/null || echo 0)
fi
CURRENT_COUNT=$((CURRENT_COUNT + 1))
echo "$CURRENT_COUNT" > "$COUNTER_FILE"

_log "session=$SESSION_ID turn=$CURRENT_COUNT"

# ── 4. Guard: only run at checkpoint interval ─────────────────────────────────
if [ $((CURRENT_COUNT % CHECKPOINT_INTERVAL)) -ne 0 ]; then
  exit 0
fi

_log "Checkpoint reached (turn $CURRENT_COUNT) — running summarizer"

# ── 5. Extract text from transcript ──────────────────────────────────────────
TRANSCRIPT_TEXT=""
if [ -n "$TRANSCRIPT_PATH" ] && [ -f "$TRANSCRIPT_PATH" ]; then
  TRANSCRIPT_TEXT=$(python3 - "$TRANSCRIPT_PATH" << 'PYEOF' 2>/dev/null
import sys, json

path = sys.argv[1]
lines = []
try:
    with open(path, encoding='utf-8') as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            try:
                msg = json.loads(raw)
                role = msg.get('role', '')
                content = msg.get('content', '')
                if isinstance(content, list):
                    # Tool use blocks — extract text parts only
                    parts = [c.get('text', '') for c in content if isinstance(c, dict) and c.get('type') == 'text']
                    content = ' '.join(parts)
                if role in ('user', 'assistant') and content:
                    lines.append(f"{role}: {content}")
            except (json.JSONDecodeError, TypeError):
                pass
except Exception as e:
    sys.exit(0)

print('\n'.join(lines))
PYEOF
)
fi

# ── 6. Guard: transcript too short ───────────────────────────────────────────
TRANSCRIPT_LEN=${#TRANSCRIPT_TEXT}
if [ "$TRANSCRIPT_LEN" -lt "$MIN_TRANSCRIPT_CHARS" ]; then
  _log "Transcript too short (${TRANSCRIPT_LEN} chars) — skipping"
  exit 0
fi

# ── 7. Run summarizer (daily notes + db only; skip SESSION_CONTEXT.md) ───────
_log "Summarizing ${TRANSCRIPT_LEN} chars (checkpoint at turn $CURRENT_COUNT)"

"$PYTHON" "$SUMMARIZER" \
  --text "$TRANSCRIPT_TEXT" \
  --no-context \
  --workspace "$WORKSPACE" \
  >> "$LOG_FILE" 2>&1 || _log "Summarizer exited non-zero (non-fatal)"

_log "Checkpoint summarization complete"

exit 0
