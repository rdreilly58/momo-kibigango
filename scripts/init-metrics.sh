#!/bin/bash
# init-metrics.sh
# Initialize metrics tracking system for GPU offload testing
# Run once on March 17 to set up logs and tracking files

set -e

WORKSPACE_DIR="$HOME/.openclaw/workspace"
LOGS_DIR="$HOME/.openclaw/logs"
METRICS_DIR="$LOGS_DIR/metrics"

echo "🚀 Initializing GPU Offload Metrics System"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Create directories
mkdir -p "$METRICS_DIR"
echo "✅ Created metrics directory: $METRICS_DIR"

# Create JSON log file
touch "$LOGS_DIR/gpu-usage.jsonl"
echo "✅ Created JSON log: $LOGS_DIR/gpu-usage.jsonl"

# Create daily tracking file
TODAY=$(date +%Y-%m-%d)
cat > "$METRICS_DIR/$TODAY-tracking.json" << 'EOF'
{
  "date": "DATE_PLACEHOLDER",
  "gpu_requests": 0,
  "cpu_requests": 0,
  "total_requests": 0,
  "gpu_percentage": 0,
  "total_latency_ms": 0,
  "avg_latency_ms": 0,
  "total_tokens_generated": 0,
  "errors": 0,
  "quality_score": null,
  "notes": ""
}
EOF

sed -i.bak "s/DATE_PLACEHOLDER/$TODAY/" "$METRICS_DIR/$TODAY-tracking.json"
rm -f "$METRICS_DIR/$TODAY-tracking.json.bak"
echo "✅ Created daily tracking: $METRICS_DIR/$TODAY-tracking.json"

# Create CSV for historical tracking
cat > "$METRICS_DIR/daily-summary.csv" << 'EOF'
date,gpu_requests,cpu_requests,total_requests,gpu_percentage,avg_latency_ms,total_tokens,errors,quality_score,notes
EOF
echo "✅ Created CSV summary: $METRICS_DIR/daily-summary.csv"

# Create bash function library for logging
cat > "$WORKSPACE_DIR/scripts/metrics-lib.sh" << 'FUNCEOF'
#!/bin/bash
# metrics-lib.sh - Shared functions for logging metrics

# Log a single GPU request to JSON
log_gpu_request() {
  local request_id="$1"
  local route="$2"  # "gpu" or "cpu"
  local tokens_in="$3"
  local tokens_out="$4"
  local latency_ms="$5"
  local duration_seconds="$6"
  local cost="$7"
  local success="$8"
  local error_msg="${9:-}"
  
  local timestamp=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
  local log_file="$HOME/.openclaw/logs/gpu-usage.jsonl"
  
  # Create JSON entry
  cat >> "$log_file" << EOF
{"timestamp":"$timestamp","request_id":"$request_id","route":"$route","tokens_input":$tokens_in,"tokens_output":$tokens_out,"latency_ms":$latency_ms,"duration_seconds":$duration_seconds,"cost":$cost,"success":$success,"error":"$error_msg"}
EOF

  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Logged: $route request ($tokens_out tokens, ${latency_ms}ms)"
}

# Get today's date
get_today() {
  date +%Y-%m-%d
}

# Print current metrics
print_metrics() {
  local log_file="$HOME/.openclaw/logs/gpu-usage.jsonl"
  
  if [ ! -f "$log_file" ] || [ ! -s "$log_file" ]; then
    echo "No metrics logged yet."
    return 0
  fi
  
  local total=$(wc -l < "$log_file")
  local gpu_count=$(grep -c '"route":"gpu"' "$log_file" || echo 0)
  local cpu_count=$(grep -c '"route":"cpu"' "$log_file" || echo 0)
  local gpu_percent=$((gpu_count * 100 / total))
  
  echo ""
  echo "📊 CURRENT METRICS"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "Total requests:   $total"
  echo "GPU requests:     $gpu_count"
  echo "CPU requests:     $cpu_count"
  echo "GPU percentage:   ${gpu_percent}%"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
}
FUNCEOF

chmod +x "$WORKSPACE_DIR/scripts/metrics-lib.sh"
echo "✅ Created metrics library: $WORKSPACE_DIR/scripts/metrics-lib.sh"

# Create daily check-in template
cat > "$METRICS_DIR/DAILY_CHECKIN_TEMPLATE.md" << 'EOF'
# Daily Metrics Check-In

## Date: [INSERT DATE]

### Usage
- How many AI requests did you make today? `___`
- How many routed to GPU? `___`
- How many fell back to CPU? `___`
- Any errors encountered? `___`

### Performance
- Response quality (1-10): `___`
- System reliability (1-10): `___`
- Speed felt good? (1-10): `___`

### Cost/Time
- Estimated time saved today (minutes): `___`
- Issues: `___`

### Notes
```
[Write any observations, bugs, or interesting patterns here]
```

---

**To use this template:**
1. Copy content to a new file
2. Fill in your observations
3. Save as `DAILY_CHECKIN_[DATE].md` in ~/.openclaw/workspace/memory/
EOF

echo "✅ Created check-in template: $METRICS_DIR/DAILY_CHECKIN_TEMPLATE.md"

# Summary
cat << 'EOF'

═══════════════════════════════════════════════════════════════════════════════

✅ METRICS SYSTEM INITIALIZED

Files created:
  📊 JSON log:        ~/.openclaw/logs/gpu-usage.jsonl
  📋 Daily tracking:  ~/.openclaw/logs/metrics/[DATE]-tracking.json
  📈 CSV summary:     ~/.openclaw/logs/metrics/daily-summary.csv
  🔧 Functions:       ~/.openclaw/workspace/scripts/metrics-lib.sh
  📝 Checkin form:    ~/.openclaw/logs/metrics/DAILY_CHECKIN_TEMPLATE.md

Quick start:
  1. Use DAILY_CHECKIN_TEMPLATE.md each day
  2. Copy the metrics-lib.sh functions into your scripts
  3. Call: log_gpu_request [args...] to track requests
  4. Call: print_metrics to see current dashboard

Manual entry example (bash):
  source ~/.openclaw/workspace/scripts/metrics-lib.sh
  log_gpu_request "req-001" "gpu" 156 187 2140 6.7 0.032 true ""
  print_metrics

Ready to start logging on March 17! 🚀

═══════════════════════════════════════════════════════════════════════════════

EOF

echo ""
echo "✅ Setup complete! Ready to track metrics starting March 17."
