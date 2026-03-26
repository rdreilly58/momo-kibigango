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
