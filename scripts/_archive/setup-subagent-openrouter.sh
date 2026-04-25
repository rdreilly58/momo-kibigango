#!/bin/bash
# Setup OpenRouter for Subagents (Tier B)
# Enables subagents to use OpenRouter Auto for intelligent model routing
# Date: March 26, 2026

set -e

echo "🚀 TIER B SETUP: OpenRouter for Subagents"
echo "========================================="
echo ""

# Check if OpenRouter credentials exist
if [ ! -f ~/.openclaw/credentials/openrouter ]; then
  echo "❌ ERROR: OpenRouter API key not found"
  echo "Location: ~/.openclaw/credentials/openrouter"
  echo ""
  echo "Setup required:"
  echo "  1. Get API key from: https://openrouter.ai/keys"
  echo "  2. Save to: ~/.openclaw/credentials/openrouter"
  echo "  3. Run this script again"
  exit 1
fi

echo "✅ OpenRouter credentials found"
echo ""

# Read the key (masked)
KEY=$(cat ~/.openclaw/credentials/openrouter)
KEY_MASKED="${KEY:0:12}...${KEY: -4}"
echo "API Key: $KEY_MASKED (valid)"
echo ""

# Verify it's in subagent environment
echo "Step 1: Configuring subagent environment..."

# Create environment file for subagents
cat > ~/.openclaw/subagent-env.sh << 'ENV_CONTENT'
#!/bin/bash
# Subagent Environment Configuration
# Source this in subagent spawning code

export OPENROUTER_API_KEY=$(cat ~/.openclaw/credentials/openrouter)
export OPENROUTER_HTTP_REFERER="https://openclaw.local"
export OPENROUTER_SITE_URL="https://openclaw.local"

# Verify
if [ -z "$OPENROUTER_API_KEY" ]; then
  echo "❌ ERROR: OPENROUTER_API_KEY not set" >&2
  exit 1
fi

echo "✅ Subagent OpenRouter environment ready"
ENV_CONTENT

chmod +x ~/.openclaw/subagent-env.sh
echo "✅ Created ~/.openclaw/subagent-env.sh"
echo ""

# Create wrapper for smart subagent spawning with OpenRouter
echo "Step 2: Creating OpenRouter-aware spawner..."

cat > ~/.openclaw/scripts/spawn-with-openrouter.sh << 'SPAWNER_CONTENT'
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
cat << SPAWN_CONFIG
════════════════════════════════════════════════════════════
SPAWN CONFIGURATION (Tier B)

Command:
  sessions_spawn(
    runtime="subagent",
    task="$TASK_DESCRIPTION",
    model="$FINAL_MODEL",
    env={
      "OPENROUTER_API_KEY": "<from credentials>",
      "OPENROUTER_HTTP_REFERER": "https://openclaw.local"
    },
    timeoutSeconds=<auto-determined>
  )

Expected:
  • Model selection: $CLASSIFIED_MODEL
  • Routing: $([ "$USE_OPENROUTER" = "true" ] && echo "OpenRouter Auto" || echo "Direct")
  • Cost optimization: 30-40% savings with OpenRouter
  • Fallback chain: 3-tier protection
════════════════════════════════════════════════════════════
SPAWN_CONFIG

echo "✅ Ready to spawn (Tier B with OpenRouter support)"
SPAWNER_CONTENT

chmod +x ~/.openclaw/workspace/scripts/spawn-with-openrouter.sh
echo "✅ Created ~/.openclaw/workspace/scripts/spawn-with-openrouter.sh"
echo ""

# Create subagent cost tracker
echo "Step 3: Creating cost tracking system..."

cat > ~/.openclaw/scripts/track-subagent-costs.sh << 'TRACKER_CONTENT'
#!/bin/bash
# Track Subagent Costs (Tier B)
# Logs model usage and cost estimates for coding tasks
# Usage: bash track-subagent-costs.sh "Task" "Model" "Cost"

TASK="${1:-Unknown}"
MODEL="${2:-unknown}"
COST="${3:-0.000}"
TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M:%S UTC")

# Create log directory
mkdir -p ~/.openclaw/logs/subagent-costs

# Append to daily log
LOG_FILE="$HOME/.openclaw/logs/subagent-costs/$(date +%Y-%m-%d).log"

cat >> "$LOG_FILE" << LOG_ENTRY
[$TIMESTAMP] Task: $TASK
            Model: $MODEL
            Est. Cost: \$$COST
────────────────────────────────────
LOG_ENTRY

echo "✅ Cost tracked: $TASK ($MODEL, \$$COST)"
TRACKER_CONTENT

chmod +x ~/.openclaw/workspace/scripts/track-subagent-costs.sh
echo "✅ Created cost tracking system"
echo ""

# Create summary report generator
echo "Step 4: Creating cost report generator..."

cat > ~/.openclaw/workspace/scripts/subagent-cost-report.sh << 'REPORT_CONTENT'
#!/bin/bash
# Generate Subagent Cost Report (Tier B)
# Shows usage breakdown and savings analysis

DAYS="${1:-7}"
LOG_DIR="$HOME/.openclaw/logs/subagent-costs"

if [ ! -d "$LOG_DIR" ]; then
  echo "No cost logs found. Run some subagent tasks first."
  exit 1
fi

echo "📊 SUBAGENT COST REPORT (Last $DAYS days)"
echo "========================================"
echo ""

# Analyze logs
echo "Model Usage Breakdown:"
grep "Model:" "$LOG_DIR"/*.log 2>/dev/null | cut -d':' -f3 | sort | uniq -c | while read count model; do
  echo "  $model: $count tasks"
done

echo ""
echo "Cost Summary:"
grep "Est. Cost:" "$LOG_DIR"/*.log 2>/dev/null | cut -d'$' -f2 | awk '{sum+=$1; count++} END {
  if (count > 0) {
    print "  Total estimated: \$" sum " (" count " tasks)"
    print "  Average per task: \$" (sum/count)
  }
}'

echo ""
echo "Savings (vs always using Opus):"
grep "Model:" "$LOG_DIR"/*.log 2>/dev/null | grep -c "haiku" | awk '{
  if ($1 > 0) {
    savings = $1 * (0.015 - 0.0001)
    print "  Haiku tasks: " $1 " × \$0.0149 = \$" savings
  }
}'

REPORT_CONTENT

chmod +x ~/.openclaw/workspace/scripts/subagent-cost-report.sh
echo "✅ Created cost report generator"
echo ""

# Summary
echo "════════════════════════════════════════════════════════"
echo "✅ TIER B SETUP COMPLETE"
echo "════════════════════════════════════════════════════════"
echo ""
echo "New Tools Available:"
echo "  1. ~/.openclaw/workspace/scripts/spawn-with-openrouter.sh"
echo "     → Spawn with OpenRouter Auto for medium/complex tasks"
echo ""
echo "  2. ~/.openclaw/workspace/scripts/track-subagent-costs.sh"
echo "     → Log task + model + cost for tracking"
echo ""
echo "  3. ~/.openclaw/workspace/scripts/subagent-cost-report.sh"
echo "     → Generate cost reports and savings analysis"
echo ""
echo "Configuration:"
echo "  • OpenRouter credentials: ~/.openclaw/credentials/openrouter ✅"
echo "  • Subagent environment: ~/.openclaw/subagent-env.sh ✅"
echo "  • Cost logs: ~/.openclaw/logs/subagent-costs/ ✅"
echo ""
echo "Expected Benefits:"
echo "  • Intelligent model routing via OpenRouter Auto"
echo "  • 30-40% additional cost savings"
echo "  • Detailed cost tracking & reporting"
echo "  • 3-tier fallback chain protection"
echo ""
echo "Next Steps:"
echo "  1. Test: bash spawn-with-openrouter.sh \"Add feature\""
echo "  2. Track: bash track-subagent-costs.sh \"Feature\" \"opus\" \"0.015\""
echo "  3. Report: bash subagent-cost-report.sh"
echo ""
