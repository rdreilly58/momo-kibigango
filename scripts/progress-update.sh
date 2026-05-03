#!/usr/bin/env bash
# progress-update.sh — write/update PROGRESS.md during long tasks
# Usage: progress-update.sh "task name" "current step" "N/T" [--done | --clear]
#   --done   marks task complete
#   --clear  removes PROGRESS.md (task finished, no longer needed)

PROGRESS_FILE="$HOME/.openclaw/workspace/PROGRESS.md"
TASK="${1:-}"
STEP="${2:-}"
STEP_OF="${3:-}"
FLAG="${4:-}"

if [[ "$FLAG" == "--clear" ]]; then
  rm -f "$PROGRESS_FILE"
  exit 0
fi

TS=$(date '+%Y-%m-%d %H:%M %Z')

if [[ "$FLAG" == "--done" ]]; then
  cat > "$PROGRESS_FILE" << MDEOF
# Task Progress

**Status:** ✅ Complete  
**Task:** $TASK  
**Finished:** $TS  
MDEOF
  exit 0
fi

# Read existing completed steps if file exists
PREV_STEPS=""
if [[ -f "$PROGRESS_FILE" ]]; then
  PREV_STEPS=$(awk '/^## Completed/,0' "$PROGRESS_FILE" 2>/dev/null | tail -n +2 || true)
fi

cat > "$PROGRESS_FILE" << MDEOF
# Task Progress

**Status:** 🔄 In progress  
**Task:** $TASK  
**Step:** $STEP ($STEP_OF)  
**Updated:** $TS  

## Completed
$PREV_STEPS
- [$TS] $STEP
MDEOF
