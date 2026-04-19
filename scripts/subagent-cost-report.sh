#!/bin/bash
# Generate Subagent Cost Report (Tier B)
# Shows usage breakdown and savings analysis

DAYS="${1:-7}"
LOG_DIR="$HOME/.openclaw/logs/subagent-costs"

if [ ! -d "$LOG_DIR" ]; then
  echo "📊 No cost logs found yet. Run some subagent tasks first."
  echo "   Location: $LOG_DIR"
  exit 0
fi

echo "📊 SUBAGENT COST REPORT (Last $DAYS days)"
echo "========================================"
echo ""

# Count tasks by model
echo "Model Usage Breakdown:"
if [ -f "$LOG_DIR"/*.log ]; then
  grep "Model:" "$LOG_DIR"/*.log 2>/dev/null | cut -d':' -f3 | tr -d ' ' | sort | uniq -c | while read count model; do
    printf "  %-10s: %d tasks\n" "$model" "$count"
  done
else
  echo "  (No logs found)"
fi

echo ""
echo "Cost Summary:"
TOTAL_COST=$(grep "Est. Cost:" "$LOG_DIR"/*.log 2>/dev/null | cut -d'$' -f2 | awk '{sum+=$1} END {print sum}')
TASK_COUNT=$(grep "Est. Cost:" "$LOG_DIR"/*.log 2>/dev/null | wc -l)

if [ "$TASK_COUNT" -gt 0 ]; then
  printf "  Total estimated: \$%.4f (%d tasks)\n" "$TOTAL_COST" "$TASK_COUNT"
  AVG=$(awk "BEGIN {printf \"%.4f\", $TOTAL_COST / $TASK_COUNT}")
  printf "  Average per task: \$%s\n" "$AVG"
else
  echo "  (No costs tracked yet)"
fi

echo ""
echo "Savings Analysis (vs always using Opus):"
HAIKU_COUNT=$(grep "Model:" "$LOG_DIR"/*.log 2>/dev/null | grep -c "haiku" || echo "0")

if [ "$HAIKU_COUNT" -gt 0 ]; then
  SAVINGS=$(echo "scale=4; $HAIKU_COUNT * 0.0149" | bc)
  printf "  Haiku tasks: %d × \$0.0149 savings = \$%.4f\n" "$HAIKU_COUNT" "$SAVINGS"
fi

echo ""
echo "Logs location: $LOG_DIR/"
