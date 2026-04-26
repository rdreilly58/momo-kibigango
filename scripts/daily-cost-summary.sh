#!/bin/bash
# daily-cost-summary.sh — Summarise today's subagent cost log
#
# Reads ~/.openclaw/logs/subagent-costs/YYYY-MM-DD.log
# Tallies estimated costs and prints a summary to stdout (caller redirects to summaries.log)
# Exits silently if no log file for today.
#
# Wired in crontab: 30 23 * * * bash /Users/rreilly/.openclaw/workspace/scripts/daily-cost-summary.sh >> ~/.openclaw/logs/subagent-costs/summaries.log 2>&1

TODAY=$(date +%Y-%m-%d)
LOG_DIR="$HOME/.openclaw/logs/subagent-costs"
TODAY_LOG="$LOG_DIR/${TODAY}.log"
SUMMARIES_LOG="$LOG_DIR/summaries.log"

# Exit silently if no log for today
if [ ! -f "$TODAY_LOG" ] || [ ! -s "$TODAY_LOG" ]; then
  exit 0
fi

TASK_COUNT=$(grep -c "Est. Cost:" "$TODAY_LOG" 2>/dev/null || echo 0)

if [ "$TASK_COUNT" -eq 0 ]; then
  exit 0
fi

# Sum all cost values
TOTAL_COST=$(grep "Est. Cost:" "$TODAY_LOG" 2>/dev/null \
  | sed 's/.*\$\([0-9.]*\).*/\1/' \
  | awk '{sum+=$1} END {printf "%.4f", sum}')

# Count by model
HAIKU_COUNT=$(grep -c "Model:.*haiku" "$TODAY_LOG" 2>/dev/null || echo 0)
SONNET_COUNT=$(grep -c "Model:.*sonnet" "$TODAY_LOG" 2>/dev/null || echo 0)
OPUS_COUNT=$(grep -c "Model:.*opus" "$TODAY_LOG" 2>/dev/null || echo 0)

AVG=$(awk "BEGIN {if ($TASK_COUNT > 0) printf \"%.4f\", $TOTAL_COST / $TASK_COUNT; else print \"0.0000\"}")

echo "================================================"
echo "DAILY COST SUMMARY — ${TODAY}"
echo "================================================"
echo "Tasks tracked : ${TASK_COUNT}"
printf "Total cost    : \$%s\n" "$TOTAL_COST"
printf "Avg per task  : \$%s\n" "$AVG"
echo ""
echo "Model breakdown:"
[ "$HAIKU_COUNT" -gt 0 ]  && printf "  haiku  : %d tasks\n" "$HAIKU_COUNT"
[ "$SONNET_COUNT" -gt 0 ] && printf "  sonnet : %d tasks\n" "$SONNET_COUNT"
[ "$OPUS_COUNT" -gt 0 ]   && printf "  opus   : %d tasks\n" "$OPUS_COUNT"
echo "Log: ${TODAY_LOG}"
echo "================================================"
