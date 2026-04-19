#!/bin/bash
# Session Startup Validation — Verify all systems ready before starting
# Usage: session-startup-check.sh

WORKSPACE="$HOME/.openclaw/workspace"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "🍑 Momotaro Session Startup Check"
echo "Time: $TIMESTAMP"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

STATUS="OK"
CHECKS=0
PASSED=0

# Helper function
check_file() {
    local name="$1"
    local path="$2"
    CHECKS=$((CHECKS + 1))
    
    if [ -f "$path" ]; then
        echo -e "${GREEN}✅${NC} $name: $(basename $path)"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}❌${NC} $name: Missing ($path)"
        STATUS="FAILED"
    fi
}

check_dir() {
    local name="$1"
    local path="$2"
    CHECKS=$((CHECKS + 1))
    
    if [ -d "$path" ]; then
        echo -e "${GREEN}✅${NC} $name: $(basename $path)"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}❌${NC} $name: Missing ($path)"
        STATUS="FAILED"
    fi
}

# 1. Core Files Check
echo "📋 Core Configuration Files:"
check_file "Soul" "$WORKSPACE/SOUL.md"
check_file "User" "$WORKSPACE/USER.md"
check_file "Tools" "$WORKSPACE/TOOLS.md"
check_file "Agents" "$WORKSPACE/AGENTS.md"
check_file "Identity" "$WORKSPACE/IDENTITY.md"

# 2. Credentials Check
echo ""
echo "🔐 Credentials:"
if [ -f "$WORKSPACE/TOOLS.secrets.local" ]; then
    PERMS=$(ls -l "$WORKSPACE/TOOLS.secrets.local" | awk '{print $1}')
    if [[ "$PERMS" == *"600"* ]] || [[ "$PERMS" == "-rw-------" ]]; then
        echo -e "${GREEN}✅${NC} Credentials: Secure (600 perms)"
        PASSED=$((PASSED + 1))
    else
        echo -e "${YELLOW}⚠️${NC} Credentials: File exists but permissions may be wrong ($PERMS)"
    fi
    CHECKS=$((CHECKS + 1))
else
    echo -e "${RED}❌${NC} Credentials: TOOLS.secrets.local not found"
    STATUS="FAILED"
    CHECKS=$((CHECKS + 1))
fi

# 3. Python Environment
echo ""
echo "🐍 Python Environment:"
check_dir "venv" "$WORKSPACE/venv"

if [ -d "$WORKSPACE/venv" ]; then
    if [ -f "$WORKSPACE/venv/bin/activate" ]; then
        echo -e "${GREEN}✅${NC} venv: Activation script found"
        PASSED=$((PASSED + 1))
    else
        echo -e "${YELLOW}⚠️${NC} venv: Missing activation script"
    fi
    CHECKS=$((CHECKS + 1))
fi

# 4. Git Status
echo ""
echo "📦 Git Repository:"
cd "$WORKSPACE" 2>/dev/null || true

if [ -d .git ]; then
    echo -e "${GREEN}✅${NC} Git: Repository initialized"
    PASSED=$((PASSED + 1))
    CHECKS=$((CHECKS + 1))
    
    UNCOMMITTED=$(git status --short | wc -l)
    if [ "$UNCOMMITTED" -eq 0 ]; then
        echo -e "${GREEN}✅${NC} Git: All changes committed"
        PASSED=$((PASSED + 1))
    else
        echo -e "${YELLOW}⚠️${NC} Git: $UNCOMMITTED uncommitted changes"
    fi
    CHECKS=$((CHECKS + 1))
    
    LAST_COMMIT=$(git log -1 --format=%ci 2>/dev/null | cut -d' ' -f1-2)
    echo "   Last commit: $LAST_COMMIT"
else
    echo -e "${RED}❌${NC} Git: Not a git repository"
    STATUS="FAILED"
    CHECKS=$((CHECKS + 1))
fi

# 5. API Connectivity
echo ""
echo "🌐 API Connectivity:"

# Brave Search
if command -v curl &> /dev/null; then
    if curl -s -f "https://api.search.brave.com/res/v1/web/search?q=test&count=1" \
        -H "X-Subscription-Token: $(grep BRAVE_API_KEY $WORKSPACE/TOOLS.secrets.local 2>/dev/null | cut -d'"' -f2)" \
        > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC} Brave Search: Operational"
        PASSED=$((PASSED + 1))
    else
        echo -e "${YELLOW}⚠️${NC} Brave Search: Not responding (may be temporary)"
    fi
    CHECKS=$((CHECKS + 1))
else
    echo -e "${YELLOW}⚠️${NC} curl: Not available"
fi

# 6. Memory Files
echo ""
echo "💾 Memory Files:"
check_file "MEMORY.md" "$WORKSPACE/MEMORY.md"
check_dir "memory/" "$WORKSPACE/memory"

if [ -d "$WORKSPACE/memory" ]; then
    COUNT=$(ls "$WORKSPACE/memory"/*.md 2>/dev/null | wc -l)
    echo "   Memory entries: $COUNT files"
fi

# Summary
echo ""
echo "════════════════════════════════════════"
echo "Startup Check: $PASSED/$CHECKS passed"

if [ "$STATUS" = "OK" ]; then
    echo -e "${GREEN}✅ Status: READY TO START${NC}"
    exit 0
else
    echo -e "${RED}❌ Status: ISSUES FOUND (fix above)${NC}"
    exit 1
fi
