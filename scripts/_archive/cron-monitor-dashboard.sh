#!/bin/bash
# Cron Job Monitoring Dashboard
# Tracks cron job execution, failures, and health
# Usage: bash cron-monitor-dashboard.sh [--watch] [--json]

set -e

MONITOR_DIR=~/.openclaw/cron-monitor
JOBS_LOG=$MONITOR_DIR/jobs.log
FAILURES_LOG=$MONITOR_DIR/failures.log
JSON_MODE=0
WATCH_MODE=0

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --json) JSON_MODE=1; shift ;;
    --watch) WATCH_MODE=1; shift ;;
    *) shift ;;
  esac
done

# Initialize monitoring directory
mkdir -p $MONITOR_DIR

# Create log files if they don't exist
touch $JOBS_LOG $FAILURES_LOG

# Helper functions
record_job_status() {
  local job_name=$1
  local status=$2
  local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
  
  echo "$timestamp | $job_name | $status" >> $JOBS_LOG
}

record_failure() {
  local job_name=$1
  local error=$2
  local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
  
  echo "$timestamp | $job_name | $error" >> $FAILURES_LOG
}

get_job_stats() {
  local job_name=$1
  
  # Count recent executions (last 7 days)
  local total=$(grep "$job_name" $JOBS_LOG 2>/dev/null | wc -l)
  local failures=$(grep "$job_name" $FAILURES_LOG 2>/dev/null | wc -l)
  local success=$((total - failures))
  
  if [ $total -eq 0 ]; then
    echo "0 0 0"
  else
    local success_rate=$((success * 100 / total))
    echo "$total $failures $success_rate"
  fi
}

check_job_queue() {
  # Get current queue depth from cron
  local queue_depth=$(openclaw cron list 2>/dev/null | grep -c "running" || echo "0")
  echo $queue_depth
}

get_last_failure() {
  local job_name=$1
  tail -1 $FAILURES_LOG 2>/dev/null | grep "$job_name" | cut -d'|' -f1-3 || echo "None"
}

print_dashboard() {
  echo ""
  echo "========================================================================"
  echo "Cron Job Monitoring Dashboard — $(date '+%Y-%m-%d %H:%M:%S')"
  echo "========================================================================"
  echo ""
  
  echo "QUEUE STATUS"
  echo "---"
  local queue=$(check_job_queue)
  if [ "$queue" -eq "0" ]; then
    echo "  Current queue depth: $queue (healthy)"
  else
    echo "  Current queue depth: $queue ($(($queue)) jobs running)"
  fi
  
  echo ""
  echo "JOB STATISTICS"
  echo "---"
  
  # Get all jobs from cron
  local jobs=$(openclaw cron list 2>/dev/null | tail -n +2 | awk '{print $1}' | sort | uniq)
  
  for job in $jobs; do
    read total failures rate <<< "$(get_job_stats "$job")"
    
    if [ $total -eq 0 ]; then
      echo "  $job: No executions recorded"
    else
      if [ $rate -ge 90 ]; then
        status="✓ Healthy"
      elif [ $rate -ge 70 ]; then
        status="⚠ Degraded"
      else
        status="✗ Failing"
      fi
      
      printf "  %-40s %3d%% (%d/%d) %s\n" "$job:" "$rate" "$((total - failures))" "$total" "$status"
    fi
  done
  
  echo ""
  echo "RECENT FAILURES (Last 10)"
  echo "---"
  
  if [ ! -s $FAILURES_LOG ]; then
    echo "  No failures recorded (72h clean)"
  else
    tail -10 $FAILURES_LOG | while read line; do
      echo "  $line"
    done
  fi
  
  echo ""
  echo "ALERTS"
  echo "---"
  
  # Check for jobs with >3 consecutive failures
  local consecutive_failures=0
  if [ -s $FAILURES_LOG ]; then
    consecutive_failures=$(tail -3 $FAILURES_LOG | wc -l)
  fi
  
  if [ $consecutive_failures -ge 3 ]; then
    echo "  ⚠ Alert: 3+ consecutive failures detected"
    echo "    Last failing job: $(tail -1 $FAILURES_LOG)"
  fi
  
  if [ "$queue" -gt "5" ]; then
    echo "  ⚠ Alert: Queue depth >5 (possible starvation)"
  fi
  
  if [ ! -f $JOBS_LOG ] || [ ! -s $JOBS_LOG ]; then
    echo "  ⚠ Alert: No job execution history (monitoring inactive)"
  fi
  
  echo ""
  echo "========================================================================"
}

# Main execution
if [ $WATCH_MODE -eq 1 ]; then
  while true; do
    clear
    print_dashboard
    sleep 10
  done
else
  print_dashboard
fi

echo "Monitor logs:"
echo "  Executions: $JOBS_LOG"
echo "  Failures: $FAILURES_LOG"
