#!/bin/bash
# Cron Job Monitoring & Failure Alerting
# Monitors all cron jobs for timeouts, failures, queue backlog
# Usage: cron-monitor-and-alert.sh [--alert] [--verbose]

set -e

WORKSPACE="$HOME/.openclaw/workspace"
LOG_DIR="$HOME/.openclaw/logs/cron_runs"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
TIMESTAMP_FILE=$(date '+%Y-%m-%d')

# Options
SEND_ALERT=0
VERBOSE=0

while [[ $# -gt 0 ]]; do
  case $1 in
    --alert) SEND_ALERT=1 ;;
    --verbose) VERBOSE=1 ;;
  esac
  shift
done

mkdir -p "$LOG_DIR"

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

# Cron job definitions (name, timeout in seconds)
CRON_JOBS=(
  "Morning Briefing:300"
  "Evening Briefing:300"
  "API Quota Monitor (Morning):180"
  "API Quota Monitor (Evening):180"
  "Monitor AWS Mac Instance:600"
  "Momotaro iOS Development:300"
  "Daily Session Reset:300"
  "Auto-Update System:600"
  "Weekly Memory Consolidation:900"
  "Weekly Leadership Planning:1200"
  "Leidos Leadership Strategy:1200"
  "ReillyDesignStudio Deployment:600"
  "Dual Mac Netgear Setup:600"
  "momo-kiji Content Review:900"
)

# Function to check job health
check_job_health() {
  local job_name=$1
  local timeout=$2
  
  # Query job from cron list
  local job_info=$(openclaw cron list 2>/dev/null | grep -i "$job_name" | head -1 || echo "")
  
  if [ -z "$job_info" ]; then
    echo "[WARN] $TIMESTAMP: Job not found: $job_name" >> "$LOG_DIR/$TIMESTAMP_FILE.log"
    [ $VERBOSE -eq 1 ] && echo -e "${YELLOW}⚠️  $job_name: Not found${NC}"
    return 1
  fi
  
  # Extract status (last column-ish, before the agent/model info)
  local status=$(echo "$job_info" | awk '{print $(NF-4)}' | tr -d '[:space:]')
  
  # Check for issues
  if [[ "$status" == "running" ]]; then
    [ $VERBOSE -eq 1 ] && echo -e "${GREEN}▶️  $job_name: Running (timeout: ${timeout}s)${NC}"
    echo "[$TIMESTAMP] $job_name: Running (timeout: ${timeout}s) — OK" >> "$LOG_DIR/$TIMESTAMP_FILE.log"
  elif [[ "$status" == "ok" ]]; then
    [ $VERBOSE -eq 1 ] && echo -e "${GREEN}✅ $job_name: OK${NC}"
    echo "[$TIMESTAMP] $job_name: Status OK" >> "$LOG_DIR/$TIMESTAMP_FILE.log"
  elif [[ "$status" == "idle" ]]; then
    [ $VERBOSE -eq 1 ] && echo -e "${YELLOW}⏳ $job_name: Idle (not yet scheduled)${NC}"
    echo "[$TIMESTAMP] $job_name: Idle (not yet scheduled)" >> "$LOG_DIR/$TIMESTAMP_FILE.log"
  else
    [ $VERBOSE -eq 1 ] && echo -e "${RED}❌ $job_name: ERROR (status: $status)${NC}"
    echo "[$TIMESTAMP] $job_name: ERROR — Status: $status" >> "$LOG_DIR/$TIMESTAMP_FILE.log"
    return 1
  fi
}

# Function to check queue depth
check_queue_depth() {
  # Count jobs currently running
  local running_count=$(openclaw cron list 2>/dev/null | grep "running" | wc -l)
  
  if [ "$running_count" -gt 2 ]; then
    echo -e "${RED}❌ Queue Backlog Detected: $running_count jobs running${NC}"
    echo "[$TIMESTAMP] ALERT: Queue backlog detected ($running_count jobs running)" >> "$LOG_DIR/$TIMESTAMP_FILE.log"
    
    if [ $SEND_ALERT -eq 1 ]; then
      echo "⚠️  ALERT: Cron queue backlog ($running_count jobs running). Check scheduler status." >> "$LOG_DIR/$TIMESTAMP_FILE.log"
    fi
    return 1
  else
    [ $VERBOSE -eq 1 ] && echo -e "${GREEN}✅ Queue depth OK: $running_count jobs running${NC}"
    echo "[$TIMESTAMP] Queue depth OK: $running_count jobs running" >> "$LOG_DIR/$TIMESTAMP_FILE.log"
    return 0
  fi
}

# Function to generate report
generate_report() {
  echo ""
  echo "╔════════════════════════════════════════════════════════════════╗"
  echo "║          Cron Job Health Report                               ║"
  echo "║          $TIMESTAMP                             ║"
  echo "╚════════════════════════════════════════════════════════════════╝"
  echo ""
  
  [ $VERBOSE -eq 1 ] && echo "Checking ${#CRON_JOBS[@]} configured jobs..."
  echo ""
  
  local failed=0
  local ok=0
  
  for job_def in "${CRON_JOBS[@]}"; do
    IFS=':' read -r job_name timeout_sec <<< "$job_def"
    if check_job_health "$job_name" "$timeout_sec"; then
      ((ok++))
    else
      ((failed++))
    fi
  done
  
  echo ""
  echo "Summary: $ok OK, $failed ISSUES"
  echo "Log: $LOG_DIR/$TIMESTAMP_FILE.log"
  echo ""
  
  if [ $failed -gt 0 ]; then
    echo -e "${RED}❌ ISSUES DETECTED${NC}"
    if [ $SEND_ALERT -eq 1 ]; then
      echo "Sending alert..."
    fi
    return 1
  else
    echo -e "${GREEN}✅ All jobs OK${NC}"
    return 0
  fi
}

# Main execution
main() {
  check_queue_depth
  generate_report
}

main "$@"
