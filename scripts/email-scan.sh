#!/bin/bash
# email-scan.sh - Scan ReillyDesignStudio and personal emails for important messages

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "📧 Email Scan — $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Function to scan an account
scan_account() {
  local account=$1
  local label=$2
  
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "$label"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  
  # Unread count
  unread=$(himalaya --account "$account" envelope list --output json 2>/dev/null | grep -c '"Unseen"' || echo "0")
  echo -e "📬 Unread: ${GREEN}$unread${NC}"
  
  # Recent important emails
  echo ""
  echo "📨 Recent Messages (Last 5):"
  himalaya --account "$account" envelope list --page-size 5 --output plain 2>/dev/null | while read -r line; do
    if [[ ! -z "$line" ]]; then
      echo "   $line"
    fi
  done
  
  echo ""
}

# Scan ReillyDesignStudio account
scan_account "rds" "🍑 ReillyDesignStudio (robert.reilly@reillydesignstudio.com)"

echo ""
echo "✓ Email scan complete"
