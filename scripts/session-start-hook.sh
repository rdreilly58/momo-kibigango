#!/bin/bash
# session-start-hook.sh — UserPromptSubmit hook for first-prompt memory retrieval
#
# Registered as a UserPromptSubmit hook in ~/.claude/settings.json
# Fires on every user prompt. Guards against re-running within same session
# using a per-session-id marker file.
#
# On first prompt: queries ai-memory.db for recent entries and appends a
# "## Retrieved Memory" section to SESSION_CONTEXT.md so the agent reads
# fresh context when it executes its CLAUDE.md startup instruction.
#
# NEVER fails loudly — always exits 0 (approve the prompt unconditionally).

WORKSPACE="${OPENCLAW_TEST_WORKSPACE:-$HOME/.openclaw/workspace}"
PYTHON="$WORKSPACE/venv/bin/python3"
LOG_DIR="$HOME/.openclaw/logs"
LOG_FILE="$LOG_DIR/session-start-hook.log"
MARKER_DIR="$LOG_DIR/session-markers"
OUT="$WORKSPACE/SESSION_CONTEXT.md"

mkdir -p "$LOG_DIR" "$MARKER_DIR"

_log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] [start-hook] $*" >> "$LOG_FILE" 2>/dev/null || true
}

# ── 1. Read stdin (Claude Code passes hook data as JSON) ─────────────────────
STDIN_DATA=""
if read -t 3 -r STDIN_DATA 2>/dev/null; then
  while IFS= read -t 0.1 -r line 2>/dev/null; do
    STDIN_DATA="${STDIN_DATA}${line}"
  done
fi

# ── 2. Extract session_id and prompt from JSON payload ───────────────────────
SESSION_ID=""
PROMPT_TEXT=""
if [ -n "$STDIN_DATA" ]; then
  SESSION_ID=$(echo "$STDIN_DATA" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('session_id', ''), end='')
except Exception:
    pass
" 2>/dev/null || true)

  PROMPT_TEXT=$(echo "$STDIN_DATA" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('prompt', '')[:200], end='')
except Exception:
    pass
" 2>/dev/null || true)
fi

_log "session_id=${SESSION_ID:-unknown} prompt_len=${#PROMPT_TEXT}"

# ── 3. Guard: only run once per session ──────────────────────────────────────
if [ -n "$SESSION_ID" ]; then
  MARKER="$MARKER_DIR/$SESSION_ID.done"
  if [ -f "$MARKER" ]; then
    _log "Already ran for session $SESSION_ID — skipping"
    exit 0
  fi
  touch "$MARKER" 2>/dev/null || true
  # Clean up markers older than 24h (best effort)
  find "$MARKER_DIR" -name "*.done" -mtime +1 -delete 2>/dev/null || true
fi

# ── 4. Semantic search — embed query, rank by cosine similarity ───────────────
QUERY="${PROMPT_TEXT:-recent session context}"

MEMORIES=$("$PYTHON" "$WORKSPACE/scripts/memory_retrieve.py" "$QUERY" --top-k 5 --min-score 0.78 2>/dev/null \
  || echo "  (semantic retrieval unavailable)")

_log "Retrieved memories (${#MEMORIES} chars) for session start"

# ── 5. Append retrieved section to SESSION_CONTEXT.md ───────────────────────
if [ -f "$OUT" ]; then
  TIMESTAMP=$(date '+%Y-%m-%d %H:%M %Z')
  # Replace any existing Retrieved Memory section, or append
  python3 - "$OUT" "$MEMORIES" "$TIMESTAMP" << 'PYEOF' 2>/dev/null || true
import sys
path, memories, ts = sys.argv[1], sys.argv[2], sys.argv[3]
content = open(path).read()
section = f"\n## Retrieved Memory (session start {ts})\n{memories}\n"
marker = "## Retrieved Memory"
if marker in content:
    # Replace existing section
    import re
    content = re.sub(r'\n## Retrieved Memory.*', section, content, flags=re.DOTALL)
else:
    content = content.rstrip() + section
open(path, 'w').write(content)
PYEOF
  _log "Updated SESSION_CONTEXT.md with retrieved memories"
else
  _log "SESSION_CONTEXT.md not found — skipping update"
fi

# ── 6. Always approve the prompt ─────────────────────────────────────────────
exit 0
