#!/bin/bash
# memory-incremental-sync.sh — Fast warm-index sync (delta only)
#
# Runs every 30 minutes via cron (see `openclaw cron list`).
# Reads the last-sync watermark from namespace_meta and re-embeds only memories
# whose updated_at is newer. Typical no-op runtime: ~10ms.
# Falls back to a full clean rebuild on cold start (no watermark yet).
#
# The weekly consolidation cron still does a full rebuild as a periodic anchor
# (truncate + re-embed everything), so this script is purely the fast path.

set -uo pipefail

WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"
LOG_DIR="$HOME/.openclaw/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/memory-incremental-sync.log"

VENV_PY="$WORKSPACE/venv/bin/python3"
if [ ! -x "$VENV_PY" ]; then
  VENV_PY="$(command -v python3)"
fi

ts() { date '+%Y-%m-%d %H:%M:%S %Z'; }

# Capture timing + diagnostics
{
  echo "==========================================="
  echo "[$(ts)] memory-incremental-sync starting"
  RESULT=$("$VENV_PY" "$WORKSPACE/scripts/memory_tier_manager.py" sync 2>&1 | grep -v "Loading weights\|UNEXPECTED\|BertModel\|^----\|^Notes\|^Key\|^embeddings.position_ids\|can be ignored\|^$" | tail -20)
  echo "$RESULT"
  echo "[$(ts)] memory-incremental-sync done"
  echo ""
} >> "$LOG_FILE" 2>&1

# Echo the last sync result to stdout for cron capture
tail -10 "$LOG_FILE"
