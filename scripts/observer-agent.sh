#!/bin/bash
# observer-agent.sh — Total Recall Observer logic
#
# Run by the observer agentTurn cron (ID: 838c7ec2) every 2 hours.
# Checks for new workspace activity and writes observations to
# memory/observations.md and ai-memory.db.
#
# This script is version-controlled; to edit observer behaviour,
# update here then update the cron message to match.

set -euo pipefail

# ── Idempotency lock (prevent concurrent runs) ────────────────────────────────
LOCK_FILE="/tmp/observer-agent-$(date +%Y-%m-%d-%H).lock"
if [ -e "$LOCK_FILE" ]; then
    echo "[observer-agent] Already ran this hour (lock: $LOCK_FILE). Skipping." >&2
    exit 0
fi
touch "$LOCK_FILE"
trap 'rm -f "$LOCK_FILE"' EXIT

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
OBS_FILE="$WORKSPACE/memory/observations.md"
STAMP="$WORKSPACE/memory/.observer-last-run"

# Submit + immediately start coordinator task (observer has no external session ID)
COORDINATOR_TASK_ID=""
_COORD_RESULT=$(python3 "$WORKSPACE/scripts/agent_coordinator.py" \
  submit --task "Observer agent run $(date +%Y-%m-%dT%H:%M)" \
  --type observer --priority 3 2>/dev/null || echo '{}')
COORDINATOR_TASK_ID=$(echo "$_COORD_RESULT" | python3 -c \
  "import sys,json; print(json.load(sys.stdin).get('task_id',''))" 2>/dev/null || true)

if [ -n "$COORDINATOR_TASK_ID" ]; then
  python3 "$WORKSPACE/scripts/agent_coordinator.py" \
    start --id "$COORDINATOR_TASK_ID" --model "claude-haiku-4-5-20251001" \
    >/dev/null 2>&1 || true
fi

# Init stamp if missing (first run or recovery)
if [ ! -f "$STAMP" ]; then
  echo "$(date +%s)" > "$STAMP"
  echo "[observer] Stamp initialised: $(date)"
fi

LAST_RUN=$(cat "$STAMP")
NOW=$(date +%s)
AGE_SECONDS=$(( NOW - LAST_RUN ))

echo "[observer] Last run: ${AGE_SECONDS}s ago"

# Check for new git activity since last run
NEW_COMMITS=$(git -C "$WORKSPACE" log --oneline --since="@${LAST_RUN}" 2>/dev/null || true)

# Check for new/modified memory files since last run
NEW_MEMORY=$(find "$WORKSPACE/memory" -name "*.md" -newer "$STAMP" \
  ! -name "observations.md" 2>/dev/null | head -5 || true)

if [ -z "$NEW_COMMITS" ] && [ -z "$NEW_MEMORY" ]; then
  echo "[observer] No new activity — updating stamp only"
  echo "$(date +%s)" > "$STAMP"
  if [ -n "$COORDINATOR_TASK_ID" ]; then
    python3 "$WORKSPACE/scripts/agent_coordinator.py" \
      complete --id "$COORDINATOR_TASK_ID" \
      --summary "Observer completed: no new activity" \
      >/dev/null 2>&1 || true
  fi
  exit 0
fi

# Build observation entries
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M)

if [ -n "$NEW_COMMITS" ]; then
  COUNT=$(echo "$NEW_COMMITS" | wc -l | tr -d ' ')
  SUMMARY=$(echo "$NEW_COMMITS" | head -3 | tr '\n' '; ' | sed 's/; $//')
  ENTRY="- 🟡 ${TIME} **${COUNT} new commit(s)** — ${SUMMARY} <!-- dc:type=event dc:importance=5.0 dc:date=${DATE} -->"
  echo "$ENTRY" >> "$OBS_FILE"
  python3 "$WORKSPACE/scripts/memory_db.py" add \
    "Observer: ${COUNT} commits ${DATE}" \
    "$SUMMARY" \
    --tier short --ns workspace --tags "observation,auto,commits" 2>/dev/null || true
fi

if [ -n "$NEW_MEMORY" ]; then
  MEM_COUNT=$(echo "$NEW_MEMORY" | wc -l | tr -d ' ')
  MEM_LIST=$(echo "$NEW_MEMORY" | xargs -I{} basename {} | tr '\n' ', ' | sed 's/, $//')
  ENTRY="- 🟢 ${TIME} **${MEM_COUNT} memory file(s) updated** — ${MEM_LIST} <!-- dc:type=fact dc:importance=3.0 dc:date=${DATE} -->"
  echo "$ENTRY" >> "$OBS_FILE"
  python3 "$WORKSPACE/scripts/memory_db.py" add \
    "Observer: memory files updated ${DATE}" \
    "$MEM_LIST" \
    --tier short --ns workspace --tags "observation,auto,memory" 2>/dev/null || true
fi

# Refresh TODAY.md (calendar + email context)
python3 "$WORKSPACE/scripts/get-today-context.py" 2>/dev/null || echo "[observer] TODAY.md refresh skipped"

# Regenerate unified STATUS.md
bash "$WORKSPACE/scripts/generate-status.sh" 2>/dev/null || echo "[observer] STATUS.md refresh skipped"

# Update stamp
echo "$(date +%s)" > "$STAMP"
echo "[observer] Done — observations written"

# Complete coordinator task before heartbeat
COMMITS_FOUND=$(echo "$NEW_COMMITS" | grep -c . 2>/dev/null || echo 0)
MEMORY_UPDATES=$(echo "$NEW_MEMORY" | grep -c . 2>/dev/null || echo 0)
OBSERVER_EXIT_CODE=0
if [ -n "$COORDINATOR_TASK_ID" ]; then
  python3 "$WORKSPACE/scripts/agent_coordinator.py" \
    complete --id "$COORDINATOR_TASK_ID" \
    --summary "Observer completed: $COMMITS_FOUND new commits, $MEMORY_UPDATES memory updates" \
    >/dev/null 2>&1 || true
fi

# ── Dead-man heartbeat ───────────────────────────────────────────────────────
bash /Users/rreilly/.openclaw/workspace/scripts/cron-heartbeat.sh observer-agent $?
