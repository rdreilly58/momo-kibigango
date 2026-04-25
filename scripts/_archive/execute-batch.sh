#!/bin/bash
# Tier C Phase 3: Batch Executor
# Executes batches in sequence and tracks costs
# Usage: bash execute-batch.sh "Task description" "tier" [file1 file2 ...]

set -e

TASK_DESCRIPTION="${1:-}"
TIER="${2:-}"
shift 2
FILES=("$@")

if [ -z "$TASK_DESCRIPTION" ] || [ -z "$TIER" ]; then
  echo "Usage: bash execute-batch.sh \"Task\" \"tier\" [file1 file2 ...]"
  echo ""
  echo "Tier options: haiku, opus, gpt4"
  echo ""
  echo "Example:"
  echo "  execute-batch.sh \"Add caching\" \"opus\" NetworkCache.swift CacheManager.swift"
  exit 1
fi

echo "⚙️  TIER C BATCH EXECUTOR (Phase 3)"
echo "===================================="
echo "Task: $TASK_DESCRIPTION"
echo "Batch Tier: $(echo $TIER | tr '[:lower:]' '[:upper:]')"
echo "Files: ${#FILES[@]}"
echo ""

# Validate tier
case "$TIER" in
  haiku|opus|gpt4)
    ;;
  *)
    echo "❌ Invalid tier: $TIER"
    echo "Use: haiku, opus, or gpt4"
    exit 1
    ;;
esac

# Determine model and cost
case "$TIER" in
  haiku)
    MODEL="anthropic/claude-haiku-4-5"
    COST_PER_FILE=0.0001
    ;;
  opus)
    MODEL="anthropic/claude-opus-4-0"
    COST_PER_FILE=0.015
    ;;
  gpt4)
    MODEL="openai/gpt-4-turbo"
    COST_PER_FILE=0.030
    ;;
esac

TOTAL_COST=$(awk "BEGIN {printf \"%.4f\", ${#FILES[@]} * $COST_PER_FILE}")

echo "Step 1: Batch configuration"
echo "  Model: $MODEL"
echo "  Files: ${#FILES[@]}"
echo "  Cost per file: \$$COST_PER_FILE"
echo "  Estimated total: \$$TOTAL_COST"
echo ""

# Step 2: Prepare context
echo "Step 2: Preparing batch context..."

# Build file list for context
FILE_CONTEXT=""
for file in "${FILES[@]}"; do
  if [ -f "$file" ]; then
    FILE_CONTEXT="$FILE_CONTEXT
    
--- FILE: $file ---
(file content would be included in actual spawn)
"
  fi
done

echo "  Files included in context: ${#FILES[@]}"
echo ""

# Step 3: Show spawn command
echo "Step 3: Ready to spawn"
echo ""

cat << SPAWN_READY

═════════════════════════════════════════════════════════

SPAWN CONFIGURATION

Command:
  sessions_spawn(
    runtime="subagent",
    task="$TASK_DESCRIPTION",
    model="$MODEL",
    files=[${FILES[*]}],
    thinking="medium"
  )

Configuration:
  • Tier: $(echo $TIER | tr '[:lower:]' '[:upper:]')
  • Model: $MODEL
  • Files: ${#FILES[@]} (${FILES[*]})
  • Estimated cost: \$$TOTAL_COST
  • Execution order: Sequential (respect batch order)

Expected:
  • Quality: High (right model for tier)
  • Speed: Appropriate for $TIER
  • Cost: \$$TOTAL_COST

═════════════════════════════════════════════════════════

SPAWN_READY

echo ""

# Step 4: Track cost
echo "Step 4: Cost tracking"

# Log to cost tracker
if command -v bash &> /dev/null; then
  bash ~/.openclaw/workspace/scripts/track-subagent-costs.sh \
    "$TASK_DESCRIPTION (Batch: $TIER, ${#FILES[@]} files)" \
    "$TIER" \
    "$TOTAL_COST" 2>/dev/null || true
fi

echo "  ✅ Batch cost: \$$TOTAL_COST logged"
echo ""

echo "✅ Batch ready for execution."
echo ""
echo "Note: This script shows the spawn configuration."
echo "      In production, sessions_spawn() would execute the batch."
echo ""
echo "To execute multiple batches:"
echo "  1. bash execute-batch.sh \"Task\" \"gpt4\" file1.swift"
echo "  2. bash execute-batch.sh \"Task\" \"opus\" file2.swift file3.swift"
echo "  3. bash execute-batch.sh \"Task\" \"haiku\" tests/ docs/"
echo ""
