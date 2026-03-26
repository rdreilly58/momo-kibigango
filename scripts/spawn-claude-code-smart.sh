#!/bin/bash
# Smart Claude Code Spawning
# Analyzes task complexity and spawns with appropriate model (Haiku/Opus/GPT-4)
# Usage: bash spawn-claude-code-smart.sh "Task description"

set -e

TASK_DESCRIPTION="${1:-}"

if [ -z "$TASK_DESCRIPTION" ]; then
  echo "Usage: bash spawn-claude-code-smart.sh \"Task description\""
  echo "Example: bash spawn-claude-code-smart.sh \"Fix missing semicolon in App.swift\""
  exit 1
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

# Determine timeout based on model
case "$CLASSIFIED_MODEL" in
  haiku)
    TIMEOUT=30  # Faster timeout for simple tasks
    THINKING="off"
    ;;
  opus)
    TIMEOUT=120  # Standard timeout
    THINKING="medium"
    ;;
  gpt-4)
    TIMEOUT=180  # Longer timeout for complex tasks
    THINKING="full"
    ;;
esac

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
    echo "  ✅ Ultra-cheap: \$0.0001 per 1K tokens (150x savings vs Opus)"
    ;;
  opus)
    echo "  ✅ Balanced: \$0.015 per 1K tokens (standard)"
    ;;
  gpt-4)
    echo "  💰 Premium: \$0.03 per 1K tokens (2x Opus cost, but best quality)"
    ;;
esac
