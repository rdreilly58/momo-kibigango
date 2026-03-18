#!/bin/bash
# weekly-metrics-summary.sh
# Generate weekly metrics summary from daily logs
# Called weekly via cron: 0 9 * * 1 /path/to/weekly-metrics-summary.sh

set -e

METRICS_DIR="$HOME/.openclaw/logs/metrics"
MEMORY_DIR="$HOME/.openclaw/workspace/memory"
WEEK_START=$(date -d 'last Monday' +%Y-%m-%d)
WEEK_END=$(date +%Y-%m-%d)
WEEK_NUMBER=$(date +%V)
YEAR=$(date +%Y)

mkdir -p "$METRICS_DIR"
mkdir -p "$MEMORY_DIR"

echo "📊 Generating weekly metrics summary..."
echo "Week starting: $WEEK_START, ending: $WEEK_END"

# Aggregate data from daily summaries
TOTAL_REQUESTS=0
TOTAL_GPU_REQUESTS=0
TOTAL_CPU_REQUESTS=0
TOTAL_TIME_SAVED=0
TOTAL_COST=0
DAILY_COUNTS=0

# Sum up all daily data
for daily_file in "$METRICS_DIR"/*-summary.json; do
  if [ -f "$daily_file" ]; then
    TOTAL_REQUESTS=$(echo "$TOTAL_REQUESTS + $(jq '.total_requests' "$daily_file" 2>/dev/null || echo 0)" | bc)
    TOTAL_GPU_REQUESTS=$(echo "$TOTAL_GPU_REQUESTS + $(jq '.gpu_requests' "$daily_file" 2>/dev/null || echo 0)" | bc)
    TOTAL_CPU_REQUESTS=$(echo "$TOTAL_CPU_REQUESTS + $(jq '.cpu_requests' "$daily_file" 2>/dev/null || echo 0)" | bc)
    TOTAL_TIME_SAVED=$(echo "$TOTAL_TIME_SAVED + $(jq '.time_saved_total_seconds' "$daily_file" 2>/dev/null || echo 0)" | bc)
    TOTAL_COST=$(echo "$TOTAL_COST + $(jq '.total_cost' "$daily_file" 2>/dev/null || echo 0)" | bc)
    DAILY_COUNTS=$((DAILY_COUNTS + 1))
  fi
done

# Calculate averages
if [ $DAILY_COUNTS -gt 0 ]; then
  AVG_GPU_PERCENTAGE=$((TOTAL_GPU_REQUESTS * 100 / TOTAL_REQUESTS))
  AVG_REQUESTS_PER_DAY=$((TOTAL_REQUESTS / DAILY_COUNTS))
  TOTAL_HOURS_SAVED=$(echo "scale=2; $TOTAL_TIME_SAVED / 3600" | bc)
  TOTAL_DAYS_SAVED=$(echo "scale=2; $TOTAL_HOURS_SAVED / 8" | bc)
else
  AVG_GPU_PERCENTAGE=0
  AVG_REQUESTS_PER_DAY=0
  TOTAL_HOURS_SAVED=0
  TOTAL_DAYS_SAVED=0
fi

# Calculate cost efficiency
DAILY_COST=$(echo "scale=2; $TOTAL_COST / $DAILY_COUNTS" | bc 2>/dev/null || echo "0")
GPU_INSTANCE_COST=$(echo "scale=2; 32.67 * $DAILY_COUNTS" | bc 2>/dev/null || echo "0")

# Cloud API equivalent (assume $0.05/request)
CLOUD_EQUIVALENT=$(echo "scale=2; $TOTAL_REQUESTS * 0.05" | bc 2>/dev/null || echo "0")

# Estimated savings
ESTIMATED_SAVINGS=$(echo "scale=2; $CLOUD_EQUIVALENT - $GPU_INSTANCE_COST" | bc 2>/dev/null || echo "0")

# Create weekly JSON summary
cat > "$METRICS_DIR/week-$WEEK_NUMBER-$YEAR-summary.json" << EOF
{
  "week": $WEEK_NUMBER,
  "year": $YEAR,
  "period": "$WEEK_START to $WEEK_END",
  "days_tracked": $DAILY_COUNTS,
  "total_requests": $TOTAL_REQUESTS,
  "gpu_requests": $TOTAL_GPU_REQUESTS,
  "cpu_requests": $TOTAL_CPU_REQUESTS,
  "gpu_percentage": $AVG_GPU_PERCENTAGE,
  "avg_requests_per_day": $AVG_REQUESTS_PER_DAY,
  "total_time_saved_hours": $TOTAL_HOURS_SAVED,
  "total_time_saved_days": $TOTAL_DAYS_SAVED,
  "total_cost": $TOTAL_COST,
  "daily_cost_average": $DAILY_COST,
  "gpu_instance_cost": $GPU_INSTANCE_COST,
  "cloud_api_equivalent": $CLOUD_EQUIVALENT,
  "estimated_savings": $ESTIMATED_SAVINGS,
  "generated_at": "$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
}
EOF

echo "✅ Weekly JSON summary: $METRICS_DIR/week-$WEEK_NUMBER-$YEAR-summary.json"

# Create markdown weekly report
cat > "$MEMORY_DIR/WEEKLY_METRICS_W$WEEK_NUMBER-$YEAR.md" << EOF
# Weekly Metrics Report - Week $WEEK_NUMBER, $YEAR

**Period:** $WEEK_START to $WEEK_END  
**Days Tracked:** $DAILY_COUNTS

## 📊 Usage Metrics

| Metric | Value |
|--------|-------|
| Total Requests | $TOTAL_REQUESTS |
| GPU Requests | $TOTAL_GPU_REQUESTS |
| CPU Requests | $TOTAL_CPU_REQUESTS |
| GPU Usage Rate | ${AVG_GPU_PERCENTAGE}% |
| Avg Requests/Day | $AVG_REQUESTS_PER_DAY |

## ⚡ Performance Metrics

| Metric | Value |
|--------|-------|
| Time Saved (Total) | $TOTAL_HOURS_SAVED hours ($TOTAL_DAYS_SAVED work days) |
| Avg Requests/Day | $AVG_REQUESTS_PER_DAY |

## 💰 Cost & ROI Metrics

| Metric | Value |
|--------|-------|
| GPU Instance Cost | \$$GPU_INSTANCE_COST |
| Cloud API Equivalent | \$$CLOUD_EQUIVALENT |
| **Estimated Savings** | **\$$ESTIMATED_SAVINGS** |
| Cost Per Request | \$(echo "scale=4; $TOTAL_COST / $TOTAL_REQUESTS" | bc 2>/dev/null || echo "N/A") |
| Daily Cost Average | \$$DAILY_COST |

## 🎯 Key Takeaways

- GPU is being used ${AVG_GPU_PERCENTAGE}% of the time
- Average \$${DAILY_COST}/day in actual costs
- Equivalent cloud API would cost \$$CLOUD_EQUIVALENT
- **Weekly savings estimate: \$$ESTIMATED_SAVINGS**
- Time saved: equivalent to ${TOTAL_DAYS_SAVED} work days

## 📈 Trend

Compare with previous weeks to identify trends in usage and cost efficiency.

---

Generated: $(date '+%Y-%m-%d %H:%M:%S %Z')
EOF

echo "✅ Weekly markdown report: $MEMORY_DIR/WEEKLY_METRICS_W$WEEK_NUMBER-$YEAR.md"

# Print summary
cat << EOF

═══════════════════════════════════════════════════════════════
📊 WEEKLY METRICS SUMMARY - Week $WEEK_NUMBER, $YEAR
═══════════════════════════════════════════════════════════════

Period: $WEEK_START to $WEEK_END ($DAILY_COUNTS days)

Usage:
  Total Requests:     $TOTAL_REQUESTS
  GPU Requests:       $TOTAL_GPU_REQUESTS
  CPU Requests:       $TOTAL_CPU_REQUESTS
  GPU Usage Rate:     ${AVG_GPU_PERCENTAGE}%
  Avg Requests/Day:   $AVG_REQUESTS_PER_DAY

Performance:
  Time Saved:         $TOTAL_HOURS_SAVED hours ($TOTAL_DAYS_SAVED days)

Cost Analysis:
  GPU Instance Cost:  \$$GPU_INSTANCE_COST
  Cloud Equivalent:   \$$CLOUD_EQUIVALENT
  Savings:            \$$ESTIMATED_SAVINGS
  Cost Per Request:   \$(echo "scale=4; $TOTAL_COST / $TOTAL_REQUESTS" | bc 2>/dev/null || echo "N/A")

═══════════════════════════════════════════════════════════════

Files created:
  📊 JSON: $METRICS_DIR/week-$WEEK_NUMBER-$YEAR-summary.json
  📝 Markdown: $MEMORY_DIR/WEEKLY_METRICS_W$WEEK_NUMBER-$YEAR.md

EOF

exit 0
