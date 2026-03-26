#!/bin/bash
# Check API Key Age & Rotation Due Dates
# Alerts when keys are approaching rotation deadline
# Usage: bash check-api-key-age.sh [--days N] [--json]

set -e

DAYS_WARNING=30  # Alert if due within N days
JSON_MODE=0
TODAY=$(date +%s)

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --days) DAYS_WARNING=$2; shift 2 ;;
    --json) JSON_MODE=1; shift ;;
    *) shift ;;
  esac
done

# API Key Configuration (Last Rotation Date + Rotation Interval in days)
declare -A KEYS=(
  ["Brave Search"]="|2026-03-24|90|HIGH"
  ["OpenRouter"]="|2026-01-15|90|HIGH"
  ["Hugging Face"]="|2025-09-15|180|MEDIUM"
  ["Cloudflare"]="|2025-10-01|180|HIGH"
  ["Telegraph"]="|2025-11-20|180|MEDIUM"
  ["1Password"]="|2025-03-20|365|CRITICAL"
  ["Google Cloud"]="|2025-04-10|365|HIGH"
)

calculate_days_until_rotation() {
  local last_rotation=$1
  local interval=$2
  
  # Convert last rotation date to timestamp
  local rotation_ts=$(date -j -f "%Y-%m-%d" "$last_rotation" +%s 2>/dev/null || echo 0)
  
  if [ $rotation_ts -eq 0 ]; then
    echo "UNKNOWN"
    return
  fi
  
  local due_ts=$((rotation_ts + interval * 86400))
  local days_left=$(((due_ts - TODAY) / 86400))
  
  echo $days_left
}

print_header() {
  echo ""
  echo "========================================================================"
  echo "API Key Age & Rotation Status — $(date '+%Y-%m-%d %H:%M:%S')"
  echo "========================================================================"
  echo ""
}

print_key_status() {
  local name=$1
  local last_rotation=$2
  local interval=$3
  local priority=$4
  
  local days_left=$(calculate_days_until_rotation "$last_rotation" "$interval")
  local due_date=$(date -j -v+"$interval"d -f "%Y-%m-%d" "$last_rotation" +"%Y-%m-%d" 2>/dev/null || echo "UNKNOWN")
  
  if [ "$days_left" = "UNKNOWN" ]; then
    printf "  %-20s | Last: %s | Due: UNKNOWN | Status: ⚠ (Invalid date)\n" "$name" "$last_rotation"
  else
    if [ $days_left -lt 0 ]; then
      status="🔴 OVERDUE"
      days_text="$((days_left * -1)) days ago"
    elif [ $days_left -lt $DAYS_WARNING ]; then
      status="🟡 ALERT"
      days_text="$days_left days"
    elif [ $days_left -lt $((DAYS_WARNING * 2)) ]; then
      status="🟠 WARNING"
      days_text="$days_left days"
    else
      status="🟢 OK"
      days_text="$days_left days"
    fi
    
    printf "  %-20s | Last: %s | Due: %s | %s | %s\n" "$name" "$last_rotation" "$due_date" "$status" "$days_text"
  fi
}

print_dashboard() {
  print_header
  
  echo "KEY STATUS (Warning threshold: $DAYS_WARNING days)"
  echo "---"
  
  # Print each key
  for key_name in "${!KEYS[@]}"; do
    IFS='|' read -r _ last_rotation interval priority <<< "${KEYS[$key_name]}"
    print_key_status "$key_name" "$last_rotation" "$interval" "$priority"
  done
  
  echo ""
  echo "ALERTS & ACTIONS"
  echo "---"
  
  local alerts=0
  
  # Check for overdue or soon-due keys
  for key_name in "${!KEYS[@]}"; do
    IFS='|' read -r _ last_rotation interval priority <<< "${KEYS[$key_name]}"
    local days_left=$(calculate_days_until_rotation "$last_rotation" "$interval")
    
    if [ "$days_left" != "UNKNOWN" ]; then
      if [ $days_left -lt 0 ]; then
        echo "  ⚠️ OVERDUE: $key_name (rotated $((days_left * -1)) days ago)"
        echo "     Action: Rotate immediately!"
        ((alerts++))
      elif [ $days_left -lt $DAYS_WARNING ]; then
        echo "  ⚠️ ALERT: $key_name (due in $days_left days on $due_date)"
        echo "     Action: Schedule rotation this week"
        ((alerts++))
      fi
    fi
  done
  
  if [ $alerts -eq 0 ]; then
    echo "  ✓ No urgent rotations needed"
    echo "  ✓ All keys within safe rotation window"
  fi
  
  echo ""
  echo "ROTATION SCHEDULE"
  echo "---"
  echo "  90 days:  Brave Search, OpenRouter"
  echo "  180 days: Hugging Face, Cloudflare, Telegraph"
  echo "  365 days: 1Password, Google Cloud"
  
  echo ""
  echo "========================================================================"
}

print_json() {
  local json="{\"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\", \"keys\": ["
  
  local first=1
  for key_name in "${!KEYS[@]}"; do
    IFS='|' read -r _ last_rotation interval priority <<< "${KEYS[$key_name]}"
    local days_left=$(calculate_days_until_rotation "$last_rotation" "$interval")
    local due_date=$(date -j -v+"$interval"d -f "%Y-%m-%d" "$last_rotation" +"%Y-%m-%d" 2>/dev/null || echo "UNKNOWN")
    
    if [ $first -eq 0 ]; then
      json="$json,"
    fi
    
    json="$json{\"name\": \"$key_name\", \"last_rotation\": \"$last_rotation\", \"interval_days\": $interval, \"due_date\": \"$due_date\", \"days_left\": $days_left, \"priority\": \"$priority\"}"
    first=0
  done
  
  json="$json]}"
  echo "$json" | jq '.' 2>/dev/null || echo "$json"
}

# Main execution
if [ $JSON_MODE -eq 1 ]; then
  print_json
else
  print_dashboard
fi
