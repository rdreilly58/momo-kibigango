#!/bin/bash
# auto-flush-session-context.sh — Pre-reset SESSION_CONTEXT.md generator
#
# Runs 10 min before the openclaw daily session reset (configured at 0 1 * * *).
# Also runs every 3h during the day as a mid-session safety net (catches mid-day resets).
# Writes a structured context snapshot from file state — no live session needed.
# Even if the agent is dead/stale, the next session wakes up oriented.
#
# Usage: bash auto-flush-session-context.sh
# Crons:
#   50 0 * * *      bash ~/.openclaw/workspace/scripts/auto-flush-session-context.sh >> ~/.openclaw/logs/session-context-flush.log 2>&1
#   0 6,9,12,15,18,21 * * *  bash ~/.openclaw/workspace/scripts/auto-flush-session-context.sh >> ~/.openclaw/logs/session-context-flush.log 2>&1
#
# Note: The 2h recency guard means the agent's own manual flush always wins —
# the 3h cron only fires when the agent hasn't written anything in >2h (idle/dead).

set -uo pipefail

WORKSPACE="$HOME/.openclaw/workspace"
OUT="$WORKSPACE/SESSION_CONTEXT.md"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M %Z')
TODAY=$(date '+%Y-%m-%d')
YESTERDAY=$(date -v-1d '+%Y-%m-%d' 2>/dev/null || date -d '1 day ago' '+%Y-%m-%d')
LOG_DIR="$HOME/.openclaw/logs"

mkdir -p "$LOG_DIR"
echo "[$TIMESTAMP] [auto-flush] Building SESSION_CONTEXT.md from file state..."

# ── 1. Check if a fresh manual flush already happened recently ───────────────
# Skip auto-flush if file was written in the last 2 hours (agent did it manually)
if [ -f "$OUT" ]; then
  LAST_MOD=$(python3 -c "import os,time; print(int(time.time() - os.path.getmtime('$OUT')))" 2>/dev/null || echo 99999)
  if [ "$LAST_MOD" -lt 7200 ]; then
    echo "[$TIMESTAMP] [auto-flush] SESSION_CONTEXT.md is fresh (${LAST_MOD}s old) — skipping auto-flush."
    exit 0
  fi
fi

# ── 2. Gather signals from file state ────────────────────────────────────────

# Recent git commits (last 3, short)
RECENT_COMMITS=$(cd "$WORKSPACE" && git log --oneline -3 2>/dev/null | sed 's/^/  /' || echo "  (no commits)")

# Today's daily memory file — last 20 non-empty lines
DAILY_FILE="$WORKSPACE/memory/$TODAY.md"
if [ -f "$DAILY_FILE" ]; then
  DAILY_SUMMARY=$(grep -v '^#\|^$\|^---' "$DAILY_FILE" 2>/dev/null | tail -20 | head -10 | tr '\n' ' ' | sed 's/  */ /g' | cut -c1-400)
else
  DAILY_SUMMARY="(no daily log for $TODAY)"
fi

# Last heartbeat log line
HB_LAST=$(tail -1 "$LOG_DIR/heartbeat.log" 2>/dev/null || echo "(no heartbeat log)")

# Watchdog log — last stale event if any
WATCHDOG_LAST=$(grep -E "STALE|ERROR|healthy" "$LOG_DIR/session-watchdog.log" 2>/dev/null | tail -1 || echo "(no watchdog log)")

# Things 3 pending tasks (best effort)
THINGS_TODAY=$(things today --json 2>/dev/null | python3 -c "
import json,sys
try:
    tasks = json.load(sys.stdin)
    for t in tasks[:5]: print(' -', t.get('title',''))
except: pass
" 2>/dev/null || things today 2>/dev/null | tail -n +2 | grep -v "^---\|^$" | cut -f2 | head -5 | sed 's/^/  - /' || echo "  (Things unavailable)")

# Most recently modified skill or config (signals what was being worked on)
RECENT_FILE=$(find "$WORKSPACE/scripts" "$WORKSPACE/skills" "$WORKSPACE/config" -newer "$WORKSPACE/HEARTBEAT.md" -name "*.sh" -o -name "*.json" -o -name "*.py" 2>/dev/null | head -3 | sed 's|.*/||' | tr '\n' ', ' | sed 's/,$//')
RECENT_FILE="${RECENT_FILE:-(no recent file changes detected)}"

# ── 3. Write context snapshot ─────────────────────────────────────────────────
cat > "$OUT" << SNAPSHOT
# SESSION_CONTEXT.md — Pre-Compaction Flush

**Purpose:** Written by the agent just before context compaction or daily reset. Startup reads this first as lightweight recovery. Keep to ~1 paragraph max. Overwrite on every flush (no history).

---

[$TIMESTAMP] Auto-flushed before daily reset (openclaw resets at 01:00).
Active: Session auto-context from file state — no live session at flush time. Recent commits: $(echo "$RECENT_COMMITS" | tr '\n' ';' | sed 's/; */; /g' | cut -c1-200). Daily log: $DAILY_SUMMARY. Recently modified: $RECENT_FILE. Things today: $(echo "$THINGS_TODAY" | tr '\n' ',' | sed 's/,$//'). Next: Resume from Bob's next message — check MEMORY.md + today's daily log for full context. Blocked: none known.
SNAPSHOT

echo "[$TIMESTAMP] [auto-flush] Written: $OUT"

# ── 4. Write session context to ai-memory.db ─────────────────────────────────
CONTEXT_CONTENT=$(cat "$OUT" | grep -v '^#\|^---\|^$\|\*\*Purpose' | head -5 | tr '\n' ' ' | sed 's/  */ /g')
python3 "$WORKSPACE/scripts/memory_db.py" add \
  "Session context $(date +%Y-%m-%d)" \
  "$CONTEXT_CONTENT" \
  --tier working \
  --ns workspace \
  --tags "session,context,auto-flush" \
  >> "$LOG_DIR/session-context-flush.log" 2>&1 || true

echo "[$TIMESTAMP] [auto-flush] Done."
