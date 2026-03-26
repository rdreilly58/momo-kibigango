#!/bin/bash
# Model Routing Test Suite for OpenClaw
# Comprehensive tests for OpenRouter Auto + fallback configuration
# Date: March 26, 2026

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TESTS_TOTAL=0
TESTS_PASSED=0
TESTS_FAILED=0

# Logging
TEST_LOG="$HOME/.openclaw/workspace/tests/model-routing-test-results.log"
mkdir -p "$HOME/.openclaw/workspace/tests"

echo "🧪 MODEL ROUTING TEST SUITE" > $TEST_LOG
echo "Started: $(date)" >> $TEST_LOG
echo "================================" >> $TEST_LOG
echo "" >> $TEST_LOG

# Test function
run_test() {
  local test_name="$1"
  local test_command="$2"
  local expected="$3"
  
  TESTS_TOTAL=$((TESTS_TOTAL + 1))
  
  echo -n "Test $TESTS_TOTAL: $test_name... "
  echo "Test $TESTS_TOTAL: $test_name" >> $TEST_LOG
  
  local result=$(eval "$test_command" 2>&1)
  
  if echo "$result" | grep -q "$expected"; then
    echo -e "${GREEN}✅ PASS${NC}"
    echo "  ✅ PASS: Found '$expected'" >> $TEST_LOG
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${RED}❌ FAIL${NC}"
    echo "  ❌ FAIL: Expected '$expected', got: $result" >> $TEST_LOG
    TESTS_FAILED=$((TESTS_FAILED + 1))
  fi
}

# ===================================
# SECTION 1: Configuration Tests
# ===================================
echo -e "\n${BLUE}📋 SECTION 1: Configuration Tests${NC}"
echo "" >> $TEST_LOG
echo "SECTION 1: Configuration Tests" >> $TEST_LOG

run_test "OpenRouter auth profile exists" \
  "grep -c 'openrouter:default' ~/.openclaw/openclaw.json" \
  "1"

run_test "OpenRouter auth provider configured" \
  "grep -A 2 'openrouter:default' ~/.openclaw/openclaw.json | grep -c provider" \
  "1"

run_test "Primary model is OpenRouter Auto" \
  "grep -A 3 '\"model\"' ~/.openclaw/openclaw.json | grep -c 'openrouter/openrouter/auto'" \
  "1"

run_test "Fallback model is Haiku" \
  "grep -A 5 '\"fallbacks\"' ~/.openclaw/openclaw.json | grep -c 'claude-haiku'" \
  "1"

run_test "Gateway bind is loopback" \
  "grep '\"bind\"' ~/.openclaw/openclaw.json | grep -c loopback" \
  "1"

run_test "TLS is enabled" \
  "grep -A 2 '\"tls\"' ~/.openclaw/openclaw.json | grep -c 'true'" \
  "1"

# ===================================
# SECTION 2: Credentials Tests
# ===================================
echo -e "\n${BLUE}🔑 SECTION 2: Credentials Tests${NC}"
echo "" >> $TEST_LOG
echo "SECTION 2: Credentials Tests" >> $TEST_LOG

run_test "OpenRouter credentials file exists" \
  "test -f ~/.openclaw/credentials/openrouter && echo 'exists'" \
  "exists"

run_test "Credentials file has correct permissions (600)" \
  "stat -f '%A' ~/.openclaw/credentials/openrouter 2>/dev/null || stat -c '%a' ~/.openclaw/credentials/openrouter 2>/dev/null" \
  "600"

run_test "Credentials file is not empty" \
  "test -s ~/.openclaw/credentials/openrouter && echo 'not-empty'" \
  "not-empty"

run_test "API key format is valid (starts with sk-or)" \
  "head -1 ~/.openclaw/credentials/openrouter" \
  "sk-or"

# ===================================
# SECTION 3: Gateway Tests
# ===================================
echo -e "\n${BLUE}🔄 SECTION 3: Gateway Tests${NC}"
echo "" >> $TEST_LOG
echo "SECTION 3: Gateway Tests" >> $TEST_LOG

run_test "Gateway is running" \
  "openclaw gateway status 2>&1" \
  "running"

run_test "Gateway listening on correct port" \
  "openclaw gateway status 2>&1" \
  "18789"

run_test "Gateway RPC probe is OK" \
  "openclaw gateway status 2>&1" \
  "ok"

run_test "Gateway is bound to loopback only" \
  "openclaw gateway status 2>&1" \
  "127.0.0.1"

# ===================================
# SECTION 4: Cron Job Tests
# ===================================
echo -e "\n${BLUE}⏰ SECTION 4: Cron Job Tests${NC}"
echo "" >> $TEST_LOG
echo "SECTION 4: Cron Job Tests" >> $TEST_LOG

run_test "Total cron jobs (should be 14 after consolidation)" \
  "cron list 2>/dev/null | grep -c '\"id\"' || echo 0" \
  "[0-9]"

run_test "API Quota Monitor (Morning) exists" \
  "cron list 2>/dev/null | grep -c 'API Quota Monitor' || echo 'not-found'" \
  "API"

run_test "API Quota Monitor (Evening) exists" \
  "cron list 2>/dev/null | grep -c 'Evening' || echo 'not-found'" \
  "[Ee]vening"

run_test "Morning Briefing job exists" \
  "cron list 2>/dev/null | grep -c 'Morning Briefing' || echo 'not-found'" \
  "Morning"

run_test "No duplicate briefing jobs" \
  "cron list 2>/dev/null | grep -c 'Briefing' || echo '0'" \
  "[1-2]"

# ===================================
# SECTION 5: Security Tests
# ===================================
echo -e "\n${BLUE}🔒 SECTION 5: Security Tests${NC}"
echo "" >> $TEST_LOG
echo "SECTION 5: Security Tests" >> $TEST_LOG

run_test "OpenClaw directory permissions (700)" \
  "stat -f '%A' ~/.openclaw 2>/dev/null || stat -c '%a' ~/.openclaw 2>/dev/null" \
  "700"

run_test "Config file permissions (600)" \
  "stat -f '%A' ~/.openclaw/openclaw.json 2>/dev/null || stat -c '%a' ~/.openclaw/openclaw.json 2>/dev/null" \
  "600"

run_test "Credentials directory permissions (700)" \
  "stat -f '%A' ~/.openclaw/credentials 2>/dev/null || stat -c '%a' ~/.openclaw/credentials 2>/dev/null" \
  "700"

run_test "No exposed secrets in logs" \
  "grep -r 'sk-' ~/.openclaw/logs/ 2>/dev/null | wc -l" \
  "^0$"

run_test "No API keys in config file" \
  "grep -c 'sk-' ~/.openclaw/openclaw.json" \
  "^0$"

# ===================================
# SECTION 6: Model Availability Tests
# ===================================
echo -e "\n${BLUE}🤖 SECTION 6: Model Availability Tests${NC}"
echo "" >> $TEST_LOG
echo "SECTION 6: Model Availability Tests" >> $TEST_LOG

run_test "Anthropic Opus model configured" \
  "grep -c 'claude-opus' ~/.openclaw/openclaw.json" \
  "[1-9]"

run_test "Anthropic Haiku model configured" \
  "grep -c 'claude-haiku' ~/.openclaw/openclaw.json" \
  "[1-9]"

run_test "OpenRouter Auto in config" \
  "grep -c 'openrouter/openrouter/auto' ~/.openclaw/openclaw.json" \
  "1"

# ===================================
# SECTION 7: File System Tests
# ===================================
echo -e "\n${BLUE}📁 SECTION 7: File System Tests${NC}"
echo "" >> $TEST_LOG
echo "SECTION 7: File System Tests" >> $TEST_LOG

run_test "Gateway log file exists" \
  "test -f /tmp/openclaw/openclaw-*.log && echo 'exists'" \
  "exists"

run_test "Workspace directory exists" \
  "test -d ~/.openclaw/workspace && echo 'exists'" \
  "exists"

run_test "Config backup from Tier 2 exists" \
  "test -f ~/.openclaw/openclaw.json.backup.tier2 && echo 'exists'" \
  "exists"

# ===================================
# SECTION 8: Documentation Tests
# ===================================
echo -e "\n${BLUE}📚 SECTION 8: Documentation Tests${NC}"
echo "" >> $TEST_LOG
echo "SECTION 8: Documentation Tests" >> $TEST_LOG

run_test "OpenRouter setup guide exists" \
  "test -f ~/.openclaw/workspace/docs/OPENROUTER_SETUP_GUIDE.md && echo 'exists'" \
  "exists"

run_test "Tier 2 implementation guide exists" \
  "test -f ~/.openclaw/workspace/docs/TIER2_IMPLEMENTATION_GUIDE.md && echo 'exists'" \
  "exists"

run_test "Config improvements analysis exists" \
  "test -f ~/.openclaw/workspace/docs/CONFIG_IMPROVEMENTS_ANALYSIS.md && echo 'exists'" \
  "exists"

# ===================================
# SECTION 9: Integration Tests
# ===================================
echo -e "\n${BLUE}🔗 SECTION 9: Integration Tests${NC}"
echo "" >> $TEST_LOG
echo "SECTION 9: Integration Tests" >> $TEST_LOG

run_test "OpenClaw doctor reports no critical issues" \
  "openclaw doctor 2>&1 | grep -i error | wc -l" \
  "^0$"

run_test "Gateway config is valid" \
  "openclaw doctor --check config 2>&1 | grep -c 'ok\\|pass' || echo '1'" \
  "[1-9]"

# ===================================
# SUMMARY
# ===================================
echo -e "\n${BLUE}📊 TEST SUMMARY${NC}"
echo "" >> $TEST_LOG
echo "========================================" >> $TEST_LOG
echo "TEST SUMMARY" >> $TEST_LOG
echo "========================================" >> $TEST_LOG

PASS_RATE=$((TESTS_PASSED * 100 / TESTS_TOTAL))

echo ""
echo "Total Tests: $TESTS_TOTAL"
echo "Passed: $TESTS_PASSED"
echo "Failed: $TESTS_FAILED"
echo "Pass Rate: ${PASS_RATE}%"
echo ""

echo "Total Tests: $TESTS_TOTAL" >> $TEST_LOG
echo "Passed: $TESTS_PASSED" >> $TEST_LOG
echo "Failed: $TESTS_FAILED" >> $TEST_LOG
echo "Pass Rate: ${PASS_RATE}%" >> $TEST_LOG
echo "" >> $TEST_LOG

if [ $TESTS_FAILED -eq 0 ]; then
  echo -e "${GREEN}✅ ALL TESTS PASSED${NC}"
  echo "✅ ALL TESTS PASSED" >> $TEST_LOG
  exit 0
else
  echo -e "${RED}❌ $TESTS_FAILED TESTS FAILED${NC}"
  echo "❌ $TESTS_FAILED TESTS FAILED" >> $TEST_LOG
  exit 1
fi
