#!/bin/bash
# Smart Claude Code Spawning
# Analyzes task complexity and spawns with appropriate model (Haiku/Opus/GPT-4)
# Usage: bash spawn-claude-code-smart.sh "Task description"

set -e

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
TASK_DESCRIPTION="${1:-}"

if [ -z "$TASK_DESCRIPTION" ]; then
  echo "Usage: bash spawn-claude-code-smart.sh \"Task description\""
  echo "Example: bash spawn-claude-code-smart.sh \"Fix missing semicolon in App.swift\""
  exit 1
fi

# Submit task to coordinator (non-blocking)
COORDINATOR_TASK_ID=""
if command -v python3 &>/dev/null; then
  _COORD_RESULT=$(python3 "$WORKSPACE/scripts/agent_coordinator.py" \
    submit --task "${TASK_DESCRIPTION:-coding task}" --type coding --priority 7 2>/dev/null || echo '{}')
  COORDINATOR_TASK_ID=$(echo "$_COORD_RESULT" | python3 -c \
    "import sys,json; print(json.load(sys.stdin).get('task_id',''))" 2>/dev/null || true)
fi

echo "🚀 SMART CLAUDE CODE SPAWNER"
echo "============================"
echo "Task: $TASK_DESCRIPTION"
echo ""

# Classify the task
echo "Step 1: Classifying task complexity..."
CLASSIFIER_OUTPUT=$(bash ~/.openclaw/workspace/scripts/classify-coding-task.sh "$TASK_DESCRIPTION" 2>&1)

# Extract model from output
CLASSIFIED_MODEL=$(echo "$CLASSIFIER_OUTPUT" | grep "^CLASSIFIED_MODEL=" | cut -d'=' -f2)
CLASSIFIED_ALIAS=$(echo "$CLASSIFIER_OUTPUT" | grep "^CLASSIFIED_MODEL_ALIAS=" | cut -d'=' -f2)

echo "Step 2: Task classified as: $CLASSIFIED_MODEL"
echo "        Model: $CLASSIFIED_ALIAS"
echo ""

# Timeout and thinking come from classifier output (already set via CLASSIFIED_TIMEOUT/CLASSIFIED_THINKING)
TIMEOUT="${CLASSIFIED_TIMEOUT:-60}"
THINKING="${CLASSIFIED_THINKING:-off}"

echo "Step 3: Spawning Claude Code subagent..."
echo "        Model: $CLASSIFIED_ALIAS"
echo "        Timeout: ${TIMEOUT}s"
echo "        Thinking: $THINKING"
echo ""

# Build the spawn command
echo "Step 4: Executing..."
echo ""

# Show the command that would be run (for reference)
cat << SPAWN_CMD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Command (reference):
  sessions_spawn(
    runtime="subagent",
    task="$TASK_DESCRIPTION",
    model="$CLASSIFIED_ALIAS",
    timeoutSeconds=$TIMEOUT
  )
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SPAWN_CMD

echo ""
echo "✅ Ready to spawn. Model selected: $CLASSIFIED_MODEL"
echo ""
echo "Note: In actual implementation, this would call:"
echo "  sessions_spawn(runtime='subagent', task='...', model='$CLASSIFIED_ALIAS')"
echo ""
echo "Cost Impact:"
case "$CLASSIFIED_MODEL" in
  haiku)
    echo "  ✅ Ultra-cheap: Haiku (~150x savings vs Opus)"
    ;;
  sonnet)
    echo "  ✅ Balanced: Sonnet (default for most tasks)"
    ;;
  opus)
    echo "  💰 Deep reasoning: Opus (reserved for hard problems)"
    ;;
esac

if [ -n "$COORDINATOR_TASK_ID" ]; then
  echo "COORDINATOR_TASK_ID=$COORDINATOR_TASK_ID"
fi
