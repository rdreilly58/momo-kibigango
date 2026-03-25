#!/bin/bash
# System Health Check — Monitor API quotas, services, disk, memory, git sync
# Usage: system-health-check.sh [--json] [--alert]

set -e

WORKSPACE="$HOME/.openclaw/workspace"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
JSON_MODE="${1:-}"
ALERT_MODE="${2:-}"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Initialize results
RESULTS=()
STATUS="HEALTHY"

# Helper function to add check result
check_result() {
    local name="$1"
    local status="$2"
    local message="$3"
    
    RESULTS+=("name:$name|status:$status|message:$message")
    
    if [ "$status" = "CRITICAL" ]; then
        STATUS="CRITICAL"
    elif [ "$status" = "WARNING" ] && [ "$STATUS" != "CRITICAL" ]; then
        STATUS="WARNING"
    fi
}

echo "🏥 OpenClaw System Health Check"
echo "Time: $TIMESTAMP"
echo ""

# 1. API Quotas Check
echo "📊 API Quotas:"
if [ -f "$WORKSPACE/TOOLS.secrets.local" ]; then
    source "$WORKSPACE/TOOLS.secrets.local" 2>/dev/null || true
    
    # Brave Search quota (simple check - just verify connectivity)
    if curl -s -f "https://api.search.brave.com/res/v1/web/search?q=test&count=1" \
        -H "X-Subscription-Token: $BRAVE_API_KEY" > /dev/null 2>&1; then
        echo "✅ Brave Search API: Operational"
        check_result "brave_search" "OK" "API responding normally"
    else
        echo "❌ Brave Search API: Failed"
        check_result "brave_search" "CRITICAL" "API not responding"
        STATUS="CRITICAL"
    fi
    
    # Cloudflare quota check
    if curl -s -f https://api.cloudflare.com/client/v4/zones \
        -H "Authorization: Bearer $CLOUDFLARE_TOKEN" > /dev/null 2>&1; then
        echo "✅ Cloudflare API: Operational"
        check_result "cloudflare" "OK" "API responding normally"
    else
        echo "❌ Cloudflare API: Failed"
        check_result "cloudflare" "CRITICAL" "API not responding"
        STATUS="CRITICAL"
    fi
else
    echo "⚠️ TOOLS.secrets.local not found"
    check_result "credentials" "WARNING" "Cannot load API credentials"
fi

# 2. Disk Space Check
echo ""
echo "💾 Disk Space:"
DISK_USAGE=$(df "$WORKSPACE" | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    echo "✅ Disk: ${DISK_USAGE}% used (healthy)"
    check_result "disk_space" "OK" "${DISK_USAGE}% used"
elif [ "$DISK_USAGE" -lt 95 ]; then
    echo "⚠️ Disk: ${DISK_USAGE}% used (warning)"
    check_result "disk_space" "WARNING" "${DISK_USAGE}% used"
else
    echo "❌ Disk: ${DISK_USAGE}% used (critical)"
    check_result "disk_space" "CRITICAL" "${DISK_USAGE}% used"
    STATUS="CRITICAL"
fi

# 3. Memory Check
echo ""
echo "🧠 Memory Usage:"
if command -v free &> /dev/null; then
    MEM_USAGE=$(free | awk 'NR==2 {printf "%.0f", ($3/$2)*100}')
else
    # macOS version
    MEM_USAGE=$(vm_stat | grep 'Pages free' | awk '{print int(($3 / 4194304) * 100)}' 2>/dev/null || echo "N/A")
fi

if [ "$MEM_USAGE" != "N/A" ]; then
    if [ "$MEM_USAGE" -lt 80 ]; then
        echo "✅ Memory: ${MEM_USAGE}% used (healthy)"
        check_result "memory" "OK" "${MEM_USAGE}% used"
    elif [ "$MEM_USAGE" -lt 95 ]; then
        echo "⚠️ Memory: ${MEM_USAGE}% used (warning)"
        check_result "memory" "WARNING" "${MEM_USAGE}% used"
    else
        echo "❌ Memory: ${MEM_USAGE}% used (critical)"
        check_result "memory" "CRITICAL" "${MEM_USAGE}% used"
        STATUS="CRITICAL"
    fi
else
    echo "⚠️ Memory: Cannot determine"
    check_result "memory" "WARNING" "Unable to measure"
fi

# 4. Git Sync Status
echo ""
echo "📦 Git Sync Status:"
cd "$WORKSPACE" 2>/dev/null || true
if [ -d .git ]; then
    UNCOMMITTED=$(git status --short | wc -l)
    if [ "$UNCOMMITTED" -eq 0 ]; then
        echo "✅ Git: All changes committed"
        check_result "git_sync" "OK" "Repository clean"
    else
        echo "⚠️ Git: $UNCOMMITTED uncommitted changes"
        check_result "git_sync" "WARNING" "$UNCOMMITTED uncommitted files"
    fi
    
    # Check last commit time
    LAST_COMMIT=$(git log -1 --format=%ci 2>/dev/null || echo "N/A")
    echo "   Last commit: $LAST_COMMIT"
else
    echo "⚠️ Git: Not a git repository"
    check_result "git_sync" "WARNING" "Not a git repository"
fi

# 5. Python venv Check
echo ""
echo "🐍 Python Environment:"
if [ -d "$WORKSPACE/venv" ]; then
    echo "✅ venv: Found"
    check_result "python_venv" "OK" "Virtual environment available"
else
    echo "⚠️ venv: Not found"
    check_result "python_venv" "WARNING" "Virtual environment missing"
fi

# Summary
echo ""
echo "════════════════════════════════════════"
if [ "$STATUS" = "HEALTHY" ]; then
    echo -e "${GREEN}✅ Overall Status: HEALTHY${NC}"
elif [ "$STATUS" = "WARNING" ]; then
    echo -e "${YELLOW}⚠️ Overall Status: WARNING${NC}"
else
    echo -e "${RED}❌ Overall Status: CRITICAL${NC}"
fi
echo "════════════════════════════════════════"

# Output JSON if requested
if [ "$JSON_MODE" = "--json" ]; then
    echo ""
    echo "JSON Output:"
    echo "{"
    echo "  \"timestamp\": \"$TIMESTAMP\","
    echo "  \"status\": \"$STATUS\","
    echo "  \"checks\": ["
    
    for i in "${!RESULTS[@]}"; do
        IFS='|' read -r name status msg <<< "${RESULTS[$i]}"
        IFS=':' read -r _ name <<< "$name"
        IFS=':' read -r _ status <<< "$status"
        IFS=':' read -r _ msg <<< "$msg"
        
        echo "    {\"check\": \"$name\", \"status\": \"$status\", \"message\": \"$msg\"}"
        [ $i -lt $((${#RESULTS[@]} - 1)) ] && echo ","
    done
    echo "  ]"
    echo "}"
fi

exit 0
