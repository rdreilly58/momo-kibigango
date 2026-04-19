#!/bin/bash
# Classify a task and return routing recommendations
# Usage: classify-and-route.sh "user input"

CLASSIFIER="$HOME/.openclaw/workspace/scripts/task-classifier.py"

if [ ! -f "$CLASSIFIER" ]; then
    echo "Error: Classifier not found at $CLASSIFIER"
    exit 1
fi

if [ -z "$1" ]; then
    echo "Usage: classify-and-route.sh \"your task here\""
    exit 1
fi

# Run classifier and capture output
OUTPUT=$(python3 "$CLASSIFIER" "$1")

# Parse output
COMPLEXITY=$(echo "$OUTPUT" | grep "^Complexity:" | awk '{print $2}')
MODEL=$(echo "$OUTPUT" | grep "^Model:" | awk '{print $2}')
THINKING=$(echo "$OUTPUT" | grep "^Thinking:" | awk '{print $2}')
CONTEXT=$(echo "$OUTPUT" | grep "^Context:" | awk '{print $2}')
REASONING=$(echo "$OUTPUT" | grep "^Reasoning:" | cut -d: -f2-)

# Export for use in other scripts
export TASK_COMPLEXITY="$COMPLEXITY"
export TASK_MODEL="$MODEL"
export TASK_THINKING="$THINKING"
export TASK_CONTEXT="$CONTEXT"

# Log routing decision for accuracy review
LOG_DIR="$HOME/.openclaw/logs"
mkdir -p "$LOG_DIR"
echo "$(date '+%Y-%m-%d %H:%M:%S') tier=$COMPLEXITY model=$MODEL words=$(echo "$1" | wc -w | tr -d ' ') input=$(echo "$1" | cut -c1-80 | tr '\n' ' ')" >> "$LOG_DIR/routing.log"

# Output in parseable format
cat <<EOF
{
  "task": "$1",
  "complexity": "$COMPLEXITY",
  "model": "$MODEL",
  "thinking": "$THINKING",
  "context": "$CONTEXT",
  "reasoning": "$REASONING"
}
EOF
