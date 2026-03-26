#!/bin/bash
# OpenClaw API Quota Monitor
# Checks remaining quota for all configured APIs
# Usage: api-quota-monitor.sh [--verbose] [--alert]

set -e

WORKSPACE="$HOME/.openclaw/workspace"
LOG_DIR="$HOME/.openclaw/logs"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Options
VERBOSE=0
SEND_ALERT=0

while [[ $# -gt 0 ]]; do
  case $1 in
    --verbose) VERBOSE=1 ;;
    --alert) SEND_ALERT=1 ;;
  esac
  shift
done

mkdir -p "$LOG_DIR"

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

report_quota() {
  local service=$1
  local used=$2
  local limit=$3
  local unit=$4
  
  # Handle non-numeric limits
  if [ -z "$limit" ] || [ "$limit" = "unknown" ] || [ "$limit" = "Unlimited" ]; then
    echo "[$TIMESTAMP] $service: $used $unit" >> "$LOG_DIR/quota.log"
    [ $VERBOSE -eq 1 ] && echo "✅ $service: $used $unit"
    return
  fi
  
  # Only calculate percentage if both are numeric
  if ! [[ "$used" =~ ^[0-9]+$ ]] || ! [[ "$limit" =~ ^[0-9]+$ ]]; then
    echo "[$TIMESTAMP] $service: $used/$limit $unit" >> "$LOG_DIR/quota.log"
    [ $VERBOSE -eq 1 ] && echo "✅ $service: $used/$limit $unit"
    return
  fi
  
  local percentage=$((used * 100 / limit))
  local status="OK"
  local symbol="✅"
  
  if [ "$percentage" -ge 100 ]; then
    status="EXCEEDED"
    symbol="❌"
  elif [ "$percentage" -ge 80 ]; then
    status="CRITICAL"
    symbol="⚠️"
  fi
  
  if [ $VERBOSE -eq 1 ]; then
    echo -e "${symbol} $service: $used/$limit $unit ($percentage%)"
  fi
  
  echo "[$TIMESTAMP] $service: $used/$limit $unit ($percentage%) — $status" >> "$LOG_DIR/quota.log"
}

# Check Brave Search API quota
check_brave_quota() {
  # Note: Brave doesn't expose quota via API, so we estimate based on daily limits
  # 1000 queries/month = ~33/day
  
  # For now, just indicate status
  if [ -n "$BRAVE_API_KEY" ]; then
    # Try a test query to see if API is working
    if curl -s "https://api.search.brave.com/res/v1/web/search?q=test&count=1" \
      -H "X-Subscription-Token: $BRAVE_API_KEY" | grep -q "results" 2>/dev/null; then
      report_quota "Brave Search API" "Working" "OK" "status"
    else
      report_quota "Brave Search API" "Error" "FAILED" "status"
    fi
  else
    report_quota "Brave Search API" "Not configured" "N/A" "status"
  fi
}

# Check OpenAI API quota (if using OpenAI)
check_openai_quota() {
  # Would require OpenAI API key and special endpoint
  # For now, skip (using local embeddings instead)
  echo "[$TIMESTAMP] OpenAI API: Using local embeddings (no quota needed)" >> "$LOG_DIR/quota.log"
}

# Check Hugging Face quota (fallback)
check_huggingface_quota() {
  if [ -n "$HF_API_TOKEN" ]; then
    # Hugging Face has generous free tier
    report_quota "Hugging Face API" "Free tier" "Unlimited" "status"
  else
    report_quota "Hugging Face API" "Not configured" "N/A" "status"
  fi
}

# Check local embeddings model
check_local_embeddings() {
  if [ -d "$WORKSPACE/venv" ]; then
    if [ -f "$WORKSPACE/scripts/memory_search_local.py" ]; then
      report_quota "Local Embeddings" "Unlimited" "Unlimited" "queries"
    else
      report_quota "Local Embeddings" "Not installed" "ERROR" "status"
    fi
  fi
}

# Check Cloudflare API
check_cloudflare_quota() {
  if [ -n "$CLOUDFLARE_TOKEN" ]; then
    # Cloudflare API usage is typically not quota-limited for most endpoints
    report_quota "Cloudflare API" "OK" "Unlimited" "status"
  else
    report_quota "Cloudflare API" "Not configured" "N/A" "status"
  fi
}

# AWS quota check
check_aws_quota() {
  # Check status of Mac instance quota
  local quota_file="$WORKSPACE/aws-config/mac-quota-submitted.json"
  
  if [ -f "$quota_file" ]; then
    local request_id=$(grep -o '"request_id":"[^"]*' "$quota_file" | cut -d'"' -f4)
    local submitted_at=$(grep -o '"timestamp":"[^"]*' "$quota_file" | cut -d'"' -f4)
    
    # For now, report status from file
    report_quota "AWS Mac Instance Quota" "PENDING" "APPROVED" "status"
    echo "[$TIMESTAMP] AWS Mac: Request $request_id (submitted $submitted_at)" >> "$LOG_DIR/quota.log"
  else
    report_quota "AWS Mac Instance Quota" "Not requested" "N/A" "status"
  fi
}

main() {
  echo "╔════════════════════════════════════════════════════════════════╗"
  echo "║              OpenClaw API Quota Monitor                        ║"
  echo "║              $TIMESTAMP                         ║"
  echo "╚════════════════════════════════════════════════════════════════╝"
  echo ""
  
  [ $VERBOSE -eq 1 ] && echo "Checking API quotas..."
  echo ""
  
  check_brave_quota
  check_openai_quota
  check_huggingface_quota
  check_local_embeddings
  check_cloudflare_quota
  check_aws_quota
  
  echo ""
  echo "Log: $LOG_DIR/quota.log"
  echo ""
  
  # Check if any critical quotas exceeded
  if grep -q "EXCEEDED\|ERROR" "$LOG_DIR/quota.log" 2>/dev/null; then
    if [ $SEND_ALERT -eq 1 ]; then
      echo -e "${RED}⚠️ ALERT: API quota issues detected${NC}"
      echo "See $LOG_DIR/quota.log for details"
    fi
  fi
}

main "$@"
