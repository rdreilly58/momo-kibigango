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
