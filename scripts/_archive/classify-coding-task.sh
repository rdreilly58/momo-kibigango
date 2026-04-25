#!/bin/bash
# classify-coding-task.sh — Route a task to Haiku / Sonnet / Opus
#
# Delegates to task-classifier.py (single source of truth).
# Outputs CLASSIFIED_MODEL and CLASSIFIED_MODEL_ALIAS for sourcing.
#
# Usage: bash classify-coding-task.sh "Task description"

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
PYTHON="${WORKSPACE}/venv/bin/python3"
CLASSIFIER="${WORKSPACE}/scripts/task-classifier.py"

if [ -z "${1:-}" ]; then
  echo "Usage: classify-coding-task.sh \"Task description\""
  exit 1
fi

TASK_DESCRIPTION="$1"

# Run classifier
OUTPUT=$("$PYTHON" "$CLASSIFIER" "$TASK_DESCRIPTION" 2>/dev/null)

COMPLEXITY=$(echo "$OUTPUT" | grep "^Complexity:" | awk '{print $2}')
MODEL_ID=$(echo  "$OUTPUT" | grep "^Model:"      | awk '{print $2}')
THINKING=$(echo  "$OUTPUT" | grep "^Thinking:"   | awk '{print $2}')
REASONING=$(echo "$OUTPUT" | grep "^Reasoning:"  | cut -d: -f2- | xargs)

# Map complexity to short label and timeout
case "$COMPLEXITY" in
  SIMPLE)
    SHORT_MODEL="haiku"
    TIMEOUT=30
    COLOR='\033[0;32m'
    LABEL="HAIKU (Fast & Cheap)"
    ;;
  MEDIUM)
    SHORT_MODEL="sonnet"
    TIMEOUT=60
    COLOR='\033[0;34m'
    LABEL="SONNET (Balanced)"
    ;;
  COMPLEX)
    SHORT_MODEL="opus"
    TIMEOUT=120
    COLOR='\033[1;33m'
    LABEL="OPUS (Deep Reasoning)"
    ;;
  *)
    # Fallback to Sonnet on unknown
    SHORT_MODEL="sonnet"
    TIMEOUT=60
    COLOR='\033[0;34m'
    LABEL="SONNET (default fallback)"
    ;;
esac

NC='\033[0m'

echo -e "${COLOR}✅ ${LABEL}${NC}"
echo "Task:      $TASK_DESCRIPTION"
echo "Tier:      $COMPLEXITY"
echo "Reasoning: $REASONING"
echo "Thinking:  $THINKING"
echo "Timeout:   ${TIMEOUT}s"
echo ""

# Env vars for sourcing by spawn-claude-code-smart.sh
echo "CLASSIFIED_MODEL=$SHORT_MODEL"
echo "CLASSIFIED_MODEL_ALIAS=$MODEL_ID"
echo "CLASSIFIED_THINKING=$THINKING"
echo "CLASSIFIED_TIMEOUT=$TIMEOUT"
