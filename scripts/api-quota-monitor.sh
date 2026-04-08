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
  local log_output="[$TIMESTAMP] $service:"

  # Determine if 'used' is numeric
  local is_used_numeric=0
  if [[ "$used" =~ ^[0-9]+$ ]]; then
    is_used_numeric=1
  fi

  # Determine if 'limit' is numeric
  local is_limit_numeric=0
  if [[ "$limit" =~ ^[0-9]+$ ]]; then
    is_limit_numeric=1
  fi

  # Handle non-numeric or special limits/usages first
  if [ "$is_used_numeric" -eq 0 ] || [ "$is_limit_numeric" -eq 0 ] || \
     [ -z "$limit" ] || [ "$limit" = "unknown" ] || [ "$limit" = "Unlimited" ] || \
     [ "$limit" = "OK" ] || [ "$limit" = "N/A" ] || [ "$limit" = "FAILED" ]; then
    log_output+=" $used/$limit $unit"
    echo "$log_output" >> "$LOG_DIR/quota.log"
    [ $VERBOSE -eq 1 ] && echo "✅ $service: $used/$limit $unit"
    return
  fi

  # If we reach here, both 'used' and 'limit' are numeric
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

  log_output+=" $used/$limit $unit ($percentage%) — $status"
  echo "$log_output" >> "$LOG_DIR/quota.log"
}


# Check Brave Search API quota
check_brave_quota() {
  # Retrieve Brave API key from1 Keychain
  local BRAVE_API_KEY=$(security find-generic-password -s BraveSearchAPI -a openclaw -w 2>/dev/null)
  if [ -z "$BRAVE_API_KEY" ]; then
    report_quota "Brave Search API" "Not configured" "N/A" "status"
    return
  fi

  # Note: Brave doesn't expose quota via API, so we estimate based on daily limits
  # 1000 queries/month = ~33/day
  
  # For now, just indicate status
  # Use the retrieved BRAVE_API_KEY
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
  
  check_brave_quota || true
  check_openai_quota || true
  check_huggingface_quota || true
  check_local_embeddings || true
  check_cloudflare_quota || true
  check_aws_quota || true
  
  echo ""
  echo "Log: $LOG_DIR/quota.log"
  echo ""
  
  # Check if any critical quotas exceeded
  if grep -q "EXCEEDED\|ERROR" "$LOG_DIR/quota.log" 2>/dev/null || true; then
    if [ $SEND_ALERT -eq 1 ]; then
      echo -e "${RED}⚠️ ALERT: API quota issues detected${NC}"
      echo "See $LOG_DIR/quota.log for details"
    fi
  fi
}

main "$@"
