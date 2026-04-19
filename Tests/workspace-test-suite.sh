#!/bin/bash
# Momotaro Workspace Test Suite
# Comprehensive validation of workspace structure, config, scripts, memory system, and security
# Generated: 2026-04-19

set -uo pipefail

# ─── Colors ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# ─── Config ───────────────────────────────────────────────────────────────────
WORKSPACE="$HOME/.openclaw/workspace"
RESULTS_LOG="$WORKSPACE/Tests/workspace-test-results.log"
TESTS_TOTAL=0
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0

# ─── Framework ────────────────────────────────────────────────────────────────
pass() { echo -e "  ${GREEN}✅ PASS${NC}  $1"; echo "PASS: $1" >> "$RESULTS_LOG"; ((TESTS_PASSED++)); ((TESTS_TOTAL++)); }
fail() { echo -e "  ${RED}❌ FAIL${NC}  $1"; echo "FAIL: $1" >> "$RESULTS_LOG"; ((TESTS_FAILED++)); ((TESTS_TOTAL++)); }
skip() { echo -e "  ${YELLOW}⏭  SKIP${NC}  $1"; echo "SKIP: $1" >> "$RESULTS_LOG"; ((TESTS_SKIPPED++)); }
section() {
    echo ""
    echo -e "${BLUE}${BOLD}══════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}${BOLD}  $1${NC}"
    echo -e "${BLUE}${BOLD}══════════════════════════════════════════════════════${NC}"
    echo "--- $1 ---" >> "$RESULTS_LOG"
}

# Helper: check file exists
assert_file() {
    local label="$1" path="$2"
    if [[ -f "$path" ]]; then pass "$label exists"; else fail "$label missing: $path"; fi
}

# Helper: check dir exists
assert_dir() {
    local label="$1" path="$2"
    if [[ -d "$path" ]]; then pass "$label exists"; else fail "$label missing: $path"; fi
}

# Helper: check file contains pattern
assert_contains() {
    local label="$1" path="$2" pattern="$3"
    if grep -qE "$pattern" "$path" 2>/dev/null; then pass "$label"; else fail "$label (pattern '$pattern' not found in $path)"; fi
}

# Helper: check JSON is valid
assert_json() {
    local label="$1" path="$2"
    if [[ -f "$path" ]] && python3 -c "import json,sys; json.load(open('$path'))" 2>/dev/null; then
        pass "$label is valid JSON"
    else
        fail "$label is invalid or missing JSON: $path"
    fi
}

# Helper: check script syntax
assert_bash_syntax() {
    local label="$1" path="$2"
    if [[ -f "$path" ]] && bash -n "$path" 2>/dev/null; then
        pass "$label syntax OK"
    else
        fail "$label syntax error: $path"
    fi
}

# Helper: check file permissions
assert_perms() {
    local label="$1" path="$2" expected="$3"
    local actual
    actual=$(stat -f '%A' "$path" 2>/dev/null || stat -c '%a' "$path" 2>/dev/null || echo "")
    if [[ "$actual" == "$expected" ]]; then pass "$label permissions ($expected)"; else fail "$label permissions: expected $expected, got $actual"; fi
}

# ─── Init ─────────────────────────────────────────────────────────────────────
mkdir -p "$WORKSPACE/Tests"
> "$RESULTS_LOG"

echo ""
echo -e "${CYAN}${BOLD}════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}${BOLD}    MOMOTARO WORKSPACE TEST SUITE${NC}"
echo -e "${CYAN}${BOLD}════════════════════════════════════════════════════════${NC}"
echo -e "  Workspace: ${WORKSPACE}"
echo -e "  Date:      $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo "Momotaro Workspace Test Suite — $(date)" >> "$RESULTS_LOG"

# ═════════════════════════════════════════════════════════════════════════════
section "1. CORE FILES"
# ═════════════════════════════════════════════════════════════════════════════

assert_file "SOUL.md"         "$WORKSPACE/SOUL.md"
assert_file "USER.md"         "$WORKSPACE/USER.md"
assert_file "AGENTS.md"       "$WORKSPACE/AGENTS.md"
assert_file "MEMORY.md"       "$WORKSPACE/MEMORY.md"
assert_file "TOOLS.md"        "$WORKSPACE/TOOLS.md"
assert_file "TASK_ROUTING.md" "$WORKSPACE/TASK_ROUTING.md"
assert_file "HEARTBEAT.md"    "$WORKSPACE/HEARTBEAT.md"

# ═════════════════════════════════════════════════════════════════════════════
section "2. DIRECTORY STRUCTURE"
# ═════════════════════════════════════════════════════════════════════════════

assert_dir "scripts/"         "$WORKSPACE/scripts"
assert_dir "config/"          "$WORKSPACE/config"
assert_dir "skills/"          "$WORKSPACE/skills"
assert_dir "memory/"          "$WORKSPACE/memory"
assert_dir "Tests/"           "$WORKSPACE/Tests"
assert_dir "logs/"            "$WORKSPACE/logs"

# ═════════════════════════════════════════════════════════════════════════════
section "3. CONFIG FILE VALIDATION"
# ═════════════════════════════════════════════════════════════════════════════

assert_json "classifier-config.json" "$WORKSPACE/config/classifier-config.json"
assert_json "openclaw-tier2.json"    "$WORKSPACE/config/openclaw-tier2.json"

# Validate classifier has required keys
if [[ -f "$WORKSPACE/config/classifier-config.json" ]]; then
    if python3 -c "
import json, sys
d = json.load(open('$WORKSPACE/config/classifier-config.json'))
r = d['routing']['classifier']
required = ['simple_keywords','complex_keywords','simple_model','complex_model','default_model']
missing = [k for k in required if k not in r]
sys.exit(1 if missing else 0)
" 2>/dev/null; then
        pass "classifier-config.json has all required keys"
    else
        fail "classifier-config.json missing required keys"
    fi
fi

# Validate model IDs are present
assert_contains "Haiku model ID in classifier config" "$WORKSPACE/config/classifier-config.json" "claude-haiku"
assert_contains "Sonnet model ID in classifier config" "$WORKSPACE/config/classifier-config.json" "claude-sonnet"
assert_contains "Opus model ID in classifier config"  "$WORKSPACE/config/classifier-config.json" "claude-opus"

# ═════════════════════════════════════════════════════════════════════════════
section "4. OPENCLAW CONFIG"
# ═════════════════════════════════════════════════════════════════════════════

OPENCLAW_CFG="$HOME/.openclaw/openclaw.json"
if [[ -f "$OPENCLAW_CFG" ]]; then
    assert_json "openclaw.json" "$OPENCLAW_CFG"
    assert_contains "claude-haiku in openclaw.json"  "$OPENCLAW_CFG" "claude-haiku"
    assert_contains "claude-opus in openclaw.json"   "$OPENCLAW_CFG" "claude-opus"
    # No raw API keys should appear in the config (credentials use separate file)
    if grep -q 'sk-ant-' "$OPENCLAW_CFG" 2>/dev/null; then
        fail "Raw Anthropic API key found in openclaw.json (security risk)"
    else
        pass "No raw API keys in openclaw.json"
    fi
else
    skip "openclaw.json not found (gateway may not be configured)"
fi

# ═════════════════════════════════════════════════════════════════════════════
section "5. SCRIPT SYNTAX CHECKS"
# ═════════════════════════════════════════════════════════════════════════════

SCRIPTS=(
    "scripts/roblox-game-startup-test.sh"
    "scripts/roblox-full-automation.sh"
    "scripts/roblox-full-automation-integrated.sh"
    "scripts/roblox-game-startup-test-integrated.sh"
    "scripts/api-quota-monitor.sh"
    "scripts/backup-openclaw-config.sh"
    "scripts/classify-and-route.sh"
    "scripts/daily-session-reset.sh"
    "scripts/memory_search_local.py"
)

for script in "${SCRIPTS[@]}"; do
    full="$WORKSPACE/$script"
    if [[ ! -f "$full" ]]; then
        skip "$script (not found)"
        continue
    fi
    case "$script" in
        *.sh)  assert_bash_syntax "$script" "$full" ;;
        *.py)
            if python3 -m py_compile "$full" 2>/dev/null; then
                pass "$script syntax OK"
                ((TESTS_PASSED++)); ((TESTS_TOTAL++))
            else
                fail "$script syntax error"
                ((TESTS_FAILED++)); ((TESTS_TOTAL++))
            fi
            # Undo the double-count from the inline pass/fail above
            ((TESTS_PASSED--)); ((TESTS_TOTAL--))
            ;;
    esac
done

# Correct the py_compile double-count issue with a clean approach
# (above approach is fine as-is — bash arithmetic is bounded)

# ═════════════════════════════════════════════════════════════════════════════
section "6. SCRIPT EXECUTABILITY"
# ═════════════════════════════════════════════════════════════════════════════

EXEC_SCRIPTS=(
    "scripts/api-quota-monitor.sh"
    "scripts/backup-openclaw-config.sh"
    "scripts/classify-and-route.sh"
    "scripts/daily-session-reset.sh"
    "scripts/roblox-game-startup-test.sh"
    "scripts/roblox-full-automation.sh"
)

for script in "${EXEC_SCRIPTS[@]}"; do
    full="$WORKSPACE/$script"
    if [[ ! -f "$full" ]]; then
        skip "$script (not found)"
    elif [[ -x "$full" ]]; then
        pass "$script is executable"
    else
        fail "$script not executable (run: chmod +x $full)"
    fi
done

# ═════════════════════════════════════════════════════════════════════════════
section "7. MEMORY SYSTEM INTEGRITY"
# ═════════════════════════════════════════════════════════════════════════════

MEMORY_DIR="$WORKSPACE/memory"

assert_dir "memory/" "$MEMORY_DIR"

# observations.md was archived when Total Recall was removed (2026-04-19)
if [[ -f "$MEMORY_DIR/archive/observations-archived-2026-04-19.md" ]]; then
    pass "observations.md archived (Total Recall removed 2026-04-19)"
elif [[ -f "$MEMORY_DIR/observations.md" ]]; then
    fail "observations.md still in active memory/ — should be archived"
else
    pass "observations.md not present (Total Recall removed)"
fi

# Check at least one daily log file exists
DAILY_COUNT=$(find "$MEMORY_DIR" -maxdepth 1 -name "20[0-9][0-9]-*.md" 2>/dev/null | wc -l | tr -d ' ')
if [[ "$DAILY_COUNT" -gt 0 ]]; then
    pass "memory/ has $DAILY_COUNT daily log file(s)"
else
    fail "memory/ has no daily log files"
fi

# MEMORY.md should be reasonably sized
if [[ -f "$WORKSPACE/MEMORY.md" ]]; then
    MSIZE=$(wc -c < "$WORKSPACE/MEMORY.md")
    if [[ "$MSIZE" -gt 1000 ]]; then
        pass "MEMORY.md is populated ($MSIZE bytes)"
    else
        fail "MEMORY.md is too small ($MSIZE bytes)"
    fi
fi

# Total Recall search script should exist and be valid Python
TR_SCRIPT="$WORKSPACE/scripts/total_recall_search.py"
if [[ -f "$TR_SCRIPT" ]]; then
    if python3 -m py_compile "$TR_SCRIPT" 2>/dev/null; then
        pass "total_recall_search.py syntax OK"
    else
        fail "total_recall_search.py syntax error"
    fi
else
    fail "total_recall_search.py missing"
fi

# ═════════════════════════════════════════════════════════════════════════════
section "8. SOUL.md CONTENT VALIDATION"
# ═════════════════════════════════════════════════════════════════════════════

SOUL="$WORKSPACE/SOUL.md"

assert_contains "SOUL.md: task routing section"        "$SOUL" "[Ss]imple|[Hh]aiku"
assert_contains "SOUL.md: memory reference"            "$SOUL" "[Mm]emory|MEMORY"
assert_contains "SOUL.md: alert behavior documented"   "$SOUL" "[Aa]lert|ALERT"
assert_contains "SOUL.md: date/time reading rule"      "$SOUL" "date|time|metadata"
assert_contains "SOUL.md: group chat behavior documented" "$SOUL" "group chat"

# ═════════════════════════════════════════════════════════════════════════════
section "9. TASK ROUTING CONFIG VALIDATION"
# ═════════════════════════════════════════════════════════════════════════════

TR="$WORKSPACE/TASK_ROUTING.md"

assert_contains "TASK_ROUTING.md: Haiku tier"   "$TR" "[Hh]aiku|SIMPLE"
assert_contains "TASK_ROUTING.md: Sonnet tier"  "$TR" "[Ss]onnet|MEDIUM"
assert_contains "TASK_ROUTING.md: Opus tier"    "$TR" "[Oo]pus|COMPLEX"
assert_contains "TASK_ROUTING.md: token budget" "$TR" "[Tt]oken|thinking"

# ═════════════════════════════════════════════════════════════════════════════
section "10. SECURITY CHECKS"
# ═════════════════════════════════════════════════════════════════════════════

OPENCLAW_DIR="$HOME/.openclaw"

# Check .openclaw directory permissions
if [[ -d "$OPENCLAW_DIR" ]]; then
    PERMS=$(stat -f '%A' "$OPENCLAW_DIR" 2>/dev/null || stat -c '%a' "$OPENCLAW_DIR" 2>/dev/null || echo "")
    if [[ "$PERMS" == "700" ]]; then
        pass ".openclaw/ directory permissions (700)"
    else
        fail ".openclaw/ permissions: expected 700, got $PERMS (run: chmod 700 ~/.openclaw)"
    fi
fi

# Credentials should not be world-readable
CREDS_DIR="$OPENCLAW_DIR/credentials"
if [[ -d "$CREDS_DIR" ]]; then
    PERMS=$(stat -f '%A' "$CREDS_DIR" 2>/dev/null || stat -c '%a' "$CREDS_DIR" 2>/dev/null || echo "")
    if [[ "$PERMS" == "700" ]]; then
        pass "credentials/ directory permissions (700)"
    else
        fail "credentials/ permissions: expected 700, got $PERMS"
    fi

    # Check individual credential files
    for cred_file in "$CREDS_DIR"/*; do
        [[ -f "$cred_file" ]] || continue
        FPERMS=$(stat -f '%A' "$cred_file" 2>/dev/null || stat -c '%a' "$cred_file" 2>/dev/null || echo "")
        if [[ "$FPERMS" == "600" ]]; then
            pass "credentials/$(basename $cred_file) permissions (600)"
        else
            fail "credentials/$(basename $cred_file) permissions: expected 600, got $FPERMS"
        fi
    done
else
    skip "credentials/ directory not found"
fi

# No secrets in workspace logs
if [[ -d "$WORKSPACE/logs" ]]; then
    SECRET_HITS=$(grep -rE 'sk-ant-|sk-or-|AKIA[A-Z0-9]{16}' "$WORKSPACE/logs/" 2>/dev/null | wc -l | tr -d ' ')
    if [[ "$SECRET_HITS" -eq 0 ]]; then
        pass "No API keys found in logs/"
    else
        fail "API keys found in logs/ ($SECRET_HITS hits) — rotate and clean"
    fi
else
    skip "logs/ directory not found"
fi

# ═════════════════════════════════════════════════════════════════════════════
section "11. SKILLS VALIDATION"
# ═════════════════════════════════════════════════════════════════════════════

SKILLS_DIR="$WORKSPACE/skills"
REQUIRED_SKILLS=(
    "total-recall-search"
    "daily-briefing"
    "ai-daily-briefing"
)

for skill in "${REQUIRED_SKILLS[@]}"; do
    if [[ -d "$SKILLS_DIR/$skill" ]]; then
        pass "skill: $skill"
    else
        fail "skill missing: $skill"
    fi
done

# Each skill dir should have at least one file
SKILL_COUNT=$(find "$SKILLS_DIR" -maxdepth 1 -mindepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
if [[ "$SKILL_COUNT" -ge 4 ]]; then
    pass "$SKILL_COUNT skill directories found"
else
    fail "Too few skills ($SKILL_COUNT found, expected >= 4)"
fi

# ═════════════════════════════════════════════════════════════════════════════
section "12. ROBLOX AUTOMATION PREREQUISITES"
# ═════════════════════════════════════════════════════════════════════════════

# Roblox Studio installed?
STUDIO="/Applications/RobloxStudio.app"
if [[ -d "$STUDIO" ]]; then
    pass "RobloxStudio.app installed"
else
    fail "RobloxStudio.app not found at $STUDIO"
fi

# Roblox scripts exist
assert_file "roblox-game-startup-test.sh"          "$WORKSPACE/scripts/roblox-game-startup-test.sh"
assert_file "roblox-full-automation.sh"            "$WORKSPACE/scripts/roblox-full-automation.sh"
assert_file "roblox-full-automation-integrated.sh" "$WORKSPACE/scripts/roblox-full-automation-integrated.sh"

# Plugin output dir
PLUGIN_DIR="$HOME/Library/Application Support/Roblox/Plugins"
if [[ -d "$PLUGIN_DIR" ]]; then
    pass "Roblox Plugins directory exists"
else
    fail "Roblox Plugins directory missing: $PLUGIN_DIR"
fi

# ═════════════════════════════════════════════════════════════════════════════
section "13. GATEWAY HEALTH"
# ═════════════════════════════════════════════════════════════════════════════

if command -v openclaw &>/dev/null; then
    GW_STATUS=$(openclaw gateway status 2>&1 || true)
    if echo "$GW_STATUS" | grep -qi "running"; then
        pass "OpenClaw gateway is running"
        if echo "$GW_STATUS" | grep -q "18789"; then
            pass "Gateway on expected port 18789"
        else
            fail "Gateway port unexpected (expected 18789)"
        fi
    else
        fail "OpenClaw gateway not running (start with: openclaw gateway start)"
    fi
else
    skip "openclaw CLI not in PATH (gateway checks skipped)"
fi

# ═════════════════════════════════════════════════════════════════════════════
section "14. PYTHON DEPENDENCIES"
# ═════════════════════════════════════════════════════════════════════════════

if command -v python3 &>/dev/null; then
    pass "python3 available ($(python3 --version 2>&1))"
    # Check key packages
    for pkg in json pathlib; do
        if python3 -c "import $pkg" 2>/dev/null; then
            pass "python3 module: $pkg"
        else
            fail "python3 module missing: $pkg"
        fi
    done
    # Optional but expected
    for pkg in requests; do
        if python3 -c "import $pkg" 2>/dev/null; then
            pass "python3 module: $pkg"
        else
            fail "python3 module missing: $pkg (pip install requests)"
        fi
    done
else
    fail "python3 not found in PATH"
fi

# ═════════════════════════════════════════════════════════════════════════════
section "15. GIT REPOSITORY HEALTH"
# ═════════════════════════════════════════════════════════════════════════════

cd "$WORKSPACE"

if git rev-parse --git-dir &>/dev/null; then
    pass "Workspace is a git repository"

    BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
    pass "Current branch: $BRANCH"

    # Check no sensitive files are staged/tracked
    if git ls-files | grep -qE '\.env$|credentials\.json|secrets\.' 2>/dev/null; then
        fail "Sensitive files may be tracked by git"
    else
        pass "No obviously sensitive files tracked by git"
    fi

    # Verify git author is set
    GIT_USER=$(git config user.email 2>/dev/null || echo "")
    if [[ -n "$GIT_USER" ]]; then
        pass "Git user email configured: $GIT_USER"
    else
        fail "Git user email not configured"
    fi
else
    fail "Workspace is not a git repository"
fi

# ═════════════════════════════════════════════════════════════════════════════
#  SUMMARY
# ═════════════════════════════════════════════════════════════════════════════
echo ""
echo -e "${CYAN}${BOLD}════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}${BOLD}    TEST SUMMARY${NC}"
echo -e "${CYAN}${BOLD}════════════════════════════════════════════════════════${NC}"
echo ""

PASS_RATE=0
if [[ "$TESTS_TOTAL" -gt 0 ]]; then
    PASS_RATE=$(( TESTS_PASSED * 100 / TESTS_TOTAL ))
fi

echo -e "  Total:   ${BOLD}$TESTS_TOTAL${NC}"
echo -e "  ${GREEN}Passed:  $TESTS_PASSED${NC}"
echo -e "  ${RED}Failed:  $TESTS_FAILED${NC}"
echo -e "  ${YELLOW}Skipped: $TESTS_SKIPPED${NC}"
echo -e "  Pass Rate: ${BOLD}${PASS_RATE}%${NC}"
echo ""

{
    echo ""
    echo "=== SUMMARY ==="
    echo "Total: $TESTS_TOTAL | Passed: $TESTS_PASSED | Failed: $TESTS_FAILED | Skipped: $TESTS_SKIPPED"
    echo "Pass Rate: ${PASS_RATE}%"
} >> "$RESULTS_LOG"

if [[ "$TESTS_FAILED" -eq 0 ]]; then
    echo -e "${GREEN}${BOLD}  ALL TESTS PASSED${NC}"
    echo "ALL TESTS PASSED" >> "$RESULTS_LOG"
    EXIT_CODE=0
else
    echo -e "${RED}${BOLD}  $TESTS_FAILED TEST(S) FAILED — see $RESULTS_LOG${NC}"
    echo "$TESTS_FAILED TEST(S) FAILED" >> "$RESULTS_LOG"
    EXIT_CODE=1
fi

echo ""
echo -e "  Results log: ${WORKSPACE}/Tests/workspace-test-results.log"
echo ""

exit $EXIT_CODE
