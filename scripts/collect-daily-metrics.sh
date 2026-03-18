#!/bin/bash
# collect-daily-metrics.sh
# Automatically collect and summarize daily GPU metrics
# Called daily via cron: 0 22 * * * /path/to/collect-daily-metrics.sh

set -e

LOGS_DIR="$HOME/.openclaw/logs"
METRICS_DIR="$LOGS_DIR/metrics"
MEMORY_DIR="$HOME/.openclaw/workspace/memory"
USAGE_LOG="$LOGS_DIR/gpu-usage.jsonl"
TODAY=$(date +%Y-%m-%d)

# Create directories if needed
mkdir -p "$METRICS_DIR"
mkdir -p "$MEMORY_DIR"

echo "📊 Collecting daily metrics for $TODAY..."

# Check if we have any logs for today
if [ ! -f "$USAGE_LOG" ] || [ ! -s "$USAGE_LOG" ]; then
  echo "⚠️  No metrics logged yet for $TODAY"
  TOTAL_REQUESTS=0
  GPU_REQUESTS=0
  CPU_REQUESTS=0
  GPU_PERCENTAGE=0
  AVG_GPU_LATENCY=0
  AVG_CPU_LATENCY=0
  TOTAL_COST=0
else
  # Count requests by route
  TOTAL_REQUESTS=$(wc -l < "$USAGE_LOG")
  GPU_REQUESTS=$(grep -c '"route":"gpu"' "$USAGE_LOG" || echo 0)
  CPU_REQUESTS=$(grep -c '"route":"cpu"' "$USAGE_LOG" || echo 0)
  
  # Calculate percentages
  if [ $TOTAL_REQUESTS -gt 0 ]; then
    GPU_PERCENTAGE=$((GPU_REQUESTS * 100 / TOTAL_REQUESTS))
  else
    GPU_PERCENTAGE=0
  fi
  
  # Calculate latencies (using jq)
  if [ $GPU_REQUESTS -gt 0 ]; then
    AVG_GPU_LATENCY=$(grep '"route":"gpu"' "$USAGE_LOG" | jq '.latency_ms' 2>/dev/null | \
      awk '{sum+=$1; count++} END {if (count>0) printf "%.0f", sum/count; else print "0"}')
  else
    AVG_GPU_LATENCY=0
  fi
  
  if [ $CPU_REQUESTS -gt 0 ]; then
    AVG_CPU_LATENCY=$(grep '"route":"cpu"' "$USAGE_LOG" | jq '.latency_ms' 2>/dev/null | \
      awk '{sum+=$1; count++} END {if (count>0) printf "%.0f", sum/count; else print "0"}')
  else
    AVG_CPU_LATENCY=0
  fi
  
  # Calculate total cost
  TOTAL_COST=$(jq -r '.cost' "$USAGE_LOG" 2>/dev/null | \
    awk '{sum+=$1} END {printf "%.2f", sum}')
fi

# Calculate time saved
if [ $GPU_REQUESTS -gt 0 ] && [ $AVG_CPU_LATENCY -gt 0 ] && [ $AVG_GPU_LATENCY -gt 0 ]; then
  TIME_SAVED_PER_REQUEST=$((AVG_CPU_LATENCY - AVG_GPU_LATENCY))
  TOTAL_TIME_SAVED=$((GPU_REQUESTS * TIME_SAVED_PER_REQUEST))
  HOURS_SAVED=$(echo "scale=2; $TOTAL_TIME_SAVED / 3600" | bc 2>/dev/null || echo "0")
else
  TIME_SAVED_PER_REQUEST=0
  TOTAL_TIME_SAVED=0
  HOURS_SAVED=0
fi

# Create daily summary JSON
cat > "$METRICS_DIR/$TODAY-summary.json" << EOF
{
  "date": "$TODAY",
  "total_requests": $TOTAL_REQUESTS,
  "gpu_requests": $GPU_REQUESTS,
  "cpu_requests": $CPU_REQUESTS,
  "gpu_percentage": $GPU_PERCENTAGE,
  "avg_gpu_latency_ms": $AVG_GPU_LATENCY,
  "avg_cpu_latency_ms": $AVG_CPU_LATENCY,
  "time_saved_total_seconds": $TOTAL_TIME_SAVED,
  "time_saved_hours": $HOURS_SAVED,
  "total_cost": $TOTAL_COST,
  "collected_at": "$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
}
EOF

echo "✅ Daily summary saved: $METRICS_DIR/$TODAY-summary.json"

# Create markdown checkin summary
cat > "$MEMORY_DIR/DAILY_METRICS_$TODAY.md" << EOF
# Daily Metrics Summary - $TODAY

## Quick Stats
- **Total Requests:** $TOTAL_REQUESTS
- **GPU Requests:** $GPU_REQUESTS
- **CPU Requests:** $CPU_REQUESTS
- **GPU Usage:** ${GPU_PERCENTAGE}%

## Performance
- **Avg GPU Latency:** ${AVG_GPU_LATENCY}ms
- **Avg CPU Latency:** ${AVG_CPU_LATENCY}ms
- **Time Saved (Total):** ${HOURS_SAVED} hours
- **Time Saved Per Request:** ${TIME_SAVED_PER_REQUEST}ms

## Cost
- **Total Cost:** \$$TOTAL_COST
- **GPU Instance Base:** \$32.67/day
- **Cost Per Request:** \$(echo "scale=4; $TOTAL_COST / $TOTAL_REQUESTS" | bc 2>/dev/null || echo "N/A")

## Summary
Generated automatically at $(date '+%Y-%m-%d %H:%M:%S %Z')

---

**Next:** Review March 20 for go/no-go decision
EOF

echo "✅ Markdown summary saved: $MEMORY_DIR/DAILY_METRICS_$TODAY.md"

# Append to CSV summary
CSV_FILE="$METRICS_DIR/daily-summary.csv"
echo "$TODAY,$GPU_REQUESTS,$CPU_REQUESTS,$TOTAL_REQUESTS,$GPU_PERCENTAGE,$AVG_GPU_LATENCY,$TOTAL_TIME_SAVED,$TOTAL_COST" >> "$CSV_FILE"

echo "✅ CSV updated: $CSV_FILE"

# Print summary
cat << EOF

═══════════════════════════════════════════════════════════════
📊 DAILY METRICS SUMMARY - $TODAY
═══════════════════════════════════════════════════════════════

Usage:
  Total Requests:    $TOTAL_REQUESTS
  GPU Requests:      $GPU_REQUESTS
  CPU Requests:      $CPU_REQUESTS
  GPU Percentage:    ${GPU_PERCENTAGE}%

Performance:
  GPU Latency:       ${AVG_GPU_LATENCY}ms
  CPU Latency:       ${AVG_CPU_LATENCY}ms
  Time Saved:        ${HOURS_SAVED} hours

Cost:
  Total Cost:        \$$TOTAL_COST
  Cost Per Request:  \$(echo "scale=4; $TOTAL_COST / $TOTAL_REQUESTS" | bc 2>/dev/null || echo "N/A")

═══════════════════════════════════════════════════════════════

Files created:
  📊 JSON: $METRICS_DIR/$TODAY-summary.json
  📝 Markdown: $MEMORY_DIR/DAILY_METRICS_$TODAY.md
  📈 CSV: $METRICS_DIR/daily-summary.csv

EOF

exit 0
