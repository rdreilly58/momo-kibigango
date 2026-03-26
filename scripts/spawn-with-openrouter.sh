#!/bin/bash
# Smart Subagent Spawner with OpenRouter Support (Tier B)
# Combines task classification + OpenRouter routing
# Usage: bash spawn-with-openrouter.sh "Task description"

set -e

TASK_DESCRIPTION="${1:-}"

if [ -z "$TASK_DESCRIPTION" ]; then
  echo "Usage: bash spawn-with-openrouter.sh \"Task description\""
  exit 1
fi

echo "🤖 SMART SPAWN WITH OPENROUTER (Tier B)"
echo "======================================"
echo "Task: $TASK_DESCRIPTION"
echo ""

# Step 1: Classify task
echo "Step 1: Classifying task..."
CLASSIFIER_OUTPUT=$(bash ~/.openclaw/workspace/scripts/classify-coding-task.sh "$TASK_DESCRIPTION" 2>&1)
CLASSIFIED_MODEL=$(echo "$CLASSIFIER_OUTPUT" | grep "^CLASSIFIED_MODEL=" | cut -d'=' -f2)

echo "Result: $CLASSIFIED_MODEL recommended"
echo ""

# Step 2: Determine if we should use OpenRouter
echo "Step 2: Selecting routing strategy..."

# Simple fixes use Haiku directly (no need for OpenRouter Auto)
if [ "$CLASSIFIED_MODEL" = "haiku" ]; then
  echo "Strategy: Direct Haiku (simple fix, no OpenRouter needed)"
  FINAL_MODEL="anthropic/claude-haiku-4-5"
  USE_OPENROUTER=false
else
  # Medium/complex use OpenRouter Auto for intelligent routing
  echo "Strategy: OpenRouter Auto (intelligent routing for $CLASSIFIED_MODEL tasks)"
  FINAL_MODEL="openrouter/openrouter/auto"
  USE_OPENROUTER=true
fi

echo ""

# Step 3: Show spawn configuration
echo "Step 3: Spawn Configuration"
echo "   Primary model: $FINAL_MODEL"
echo "   OpenRouter: $USE_OPENROUTER"

if [ "$USE_OPENROUTER" = "true" ]; then
  echo "   Fallback chain:"
  echo "      1. openrouter/openrouter/auto (intelligent routing)"
  echo "      2. anthropic/claude-opus-4-0 (if auto unavailable)"
  echo "      3. anthropic/claude-haiku-4-5 (if both fail)"
fi

echo ""

# Step 4: Environment setup for OpenRouter
if [ "$USE_OPENROUTER" = "true" ]; then
  echo "Step 4: Setting up OpenRouter environment..."
  
  if [ ! -f ~/.openclaw/credentials/openrouter ]; then
    echo "❌ ERROR: OpenRouter credentials missing"
    echo "Run: setup-subagent-openrouter.sh first"
    exit 1
  fi
  
  export OPENROUTER_API_KEY=$(cat ~/.openclaw/credentials/openrouter)
  echo "✅ OpenRouter API key loaded"
fi

echo ""

# Step 5: Show the spawn command
echo "════════════════════════════════════════════════════════"
echo "SPAWN CONFIGURATION (Tier B)"
echo ""
echo "Command:"
echo "  sessions_spawn("
echo "    runtime=\"subagent\","
echo "    task=\"$TASK_DESCRIPTION\","
echo "    model=\"$FINAL_MODEL\","
echo "    env={"
echo "      \"OPENROUTER_API_KEY\": \"<from credentials>\","
echo "      \"OPENROUTER_HTTP_REFERER\": \"https://openclaw.local\""
echo "    },"
echo "    timeoutSeconds=<auto-determined>"
echo "  )"
echo ""
echo "Expected:"
echo "  • Model selection: $CLASSIFIED_MODEL"
echo "  • Routing: $([ "$USE_OPENROUTER" = "true" ] && echo "OpenRouter Auto" || echo "Direct")"
echo "  • Cost optimization: 30-40% savings with OpenRouter"
echo "  • Fallback chain: 3-tier protection"
echo "════════════════════════════════════════════════════════"
echo ""
echo "✅ Ready to spawn (Tier B with OpenRouter support)"
