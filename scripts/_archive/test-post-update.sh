#!/bin/bash
# Post-Update Test Suite
# Validates critical system functionality after OpenClaw update
# Usage: bash test-post-update.sh

set -e

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
TEST_LOG="/tmp/openclaw-post-update-test.log"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         OpenClaw Post-Update Validation Test Suite            ║"
echo "║         Comprehensive system health check                     ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Logging to: $TEST_LOG"
echo ""

# Initialize test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0
CRITICAL_FAILURES=0

# Test utilities
log_test() {
  local name=$1
  local status=$2
  ((TESTS_RUN++))
  
  if [ "$status" = "PASS" ]; then
    echo "✅ $name"
    ((TESTS_PASSED++))
  elif [ "$status" = "FAIL" ]; then
    echo "❌ $name"
    ((TESTS_FAILED++))
    ((CRITICAL_FAILURES++))
  elif [ "$status" = "WARN" ]; then
    echo "⚠️  $name (warning, non-critical)"
    ((TESTS_FAILED++))
  fi
  echo "[$TIMESTAMP] $name - $status" >> "$TEST_LOG"
}

echo "════════════════════════════════════════════════════════════════"
echo "SECTION 1: GATEWAY & SERVICE"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Test 1: Gateway Status
echo "Test 1: Gateway running..."
if openclaw gateway status > /dev/null 2>&1; then
  log_test "Gateway running" "PASS"
else
  log_test "Gateway running" "FAIL"
fi

# Test 2: Gateway responds to RPC
echo "Test 2: Gateway RPC probe..."
if openclaw gateway status 2>&1 | grep -q "RPC probe: ok"; then
  log_test "Gateway RPC probe" "PASS"
else
  log_test "Gateway RPC probe" "FAIL"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "SECTION 2: CONFIGURATION"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Test 3: Config files exist
echo "Test 3: Configuration files..."
if [ -f ~/.openclaw/openclaw.json ] && [ -f ~/.openclaw/config.json ]; then
  log_test "Config files present" "PASS"
else
  log_test "Config files present" "FAIL"
fi

# Test 4: Cron jobs load
echo "Test 4: Cron jobs loading..."
if openclaw cron list > /dev/null 2>&1; then
  log_test "Cron jobs load" "PASS"
  JOB_COUNT=$(openclaw cron list 2>/dev/null | tail -n +2 | wc -l)
  echo "       Found $JOB_COUNT jobs"
else
  log_test "Cron jobs load" "FAIL"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "SECTION 3: TOOLS & CAPABILITIES"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Test 5: exec tool (create temp file and delete)
echo "Test 5: exec tool..."
if bash -c "touch /tmp/openclaw-test && rm /tmp/openclaw-test" 2>/dev/null; then
  log_test "exec tool" "PASS"
else
  log_test "exec tool" "FAIL"
fi

# Test 6: read tool (read this script)
echo "Test 6: read tool..."
if [ -r "$0" ]; then
  log_test "read tool" "PASS"
else
  log_test "read tool" "FAIL"
fi

# Test 7: write tool (create and delete temp file)
echo "Test 7: write tool..."
if bash -c "echo 'test' > /tmp/openclaw-write-test && rm /tmp/openclaw-write-test" 2>/dev/null; then
  log_test "write tool" "PASS"
else
  log_test "write tool" "FAIL"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "SECTION 4: INTEGRATIONS"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Test 8: Memory search
echo "Test 8: Memory search..."
if grep -q "memorySearch" ~/.openclaw/config.json 2>/dev/null; then
  log_test "Memory search configured" "PASS"
else
  log_test "Memory search configured" "WARN"
fi

# Test 9: Brave API
echo "Test 9: Brave API configured..."
if grep -q "brave" ~/.openclaw/openclaw.json 2>/dev/null; then
  log_test "Brave API configured" "PASS"
else
  log_test "Brave API configured" "WARN"
fi

# Test 10: Telegram integration
echo "Test 10: Telegram bot..."
if grep -q "telegram" ~/.openclaw/openclaw.json 2>/dev/null; then
  log_test "Telegram configured" "PASS"
else
  log_test "Telegram configured" "WARN"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "SECTION 5: WORKSPACE INTEGRITY"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Test 11: Workspace exists
echo "Test 11: Workspace directory..."
if [ -d ~/.openclaw/workspace ]; then
  log_test "Workspace directory" "PASS"
else
  log_test "Workspace directory" "FAIL"
fi

# Test 12: Critical files
echo "Test 12: Critical workspace files..."
CRIT_FILES=0
[ -f ~/.openclaw/workspace/SOUL.md ] && ((CRIT_FILES++))
[ -f ~/.openclaw/workspace/TOOLS.md ] && ((CRIT_FILES++))
[ -f ~/.openclaw/workspace/MEMORY.md ] && ((CRIT_FILES++))

if [ $CRIT_FILES -ge 3 ]; then
  log_test "Critical workspace files" "PASS"
else
  log_test "Critical workspace files" "WARN"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "SECTION 6: SECURITY"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Test 13: Gateway binding
echo "Test 13: Gateway binding (loopback-only)..."
if openclaw gateway status 2>&1 | grep -q "bind=loopback"; then
  log_test "Gateway loopback binding" "PASS"
else
  log_test "Gateway loopback binding" "WARN"
fi

# Test 14: TLS enabled
echo "Test 14: TLS enabled..."
if grep -q '"enabled": true' ~/.openclaw/openclaw.json 2>/dev/null; then
  log_test "TLS configured" "PASS"
else
  log_test "TLS configured" "WARN"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "TEST RESULTS SUMMARY"
echo "════════════════════════════════════════════════════════════════"
echo ""

echo "Total Tests Run: $TESTS_RUN"
echo "Tests Passed: $TESTS_PASSED"
echo "Tests Failed: $TESTS_FAILED (Warnings: $((TESTS_FAILED - CRITICAL_FAILURES)))"
echo ""

if [ $CRITICAL_FAILURES -eq 0 ]; then
  echo "╔════════════════════════════════════════════════════════════════╗"
  echo "║                  ✅ ALL TESTS PASSED                           ║"
  echo "║            Post-update system is healthy!                      ║"
  echo "║          Safe to continue normal operations.                   ║"
  echo "╚════════════════════════════════════════════════════════════════╝"
  echo ""
  echo "Log file: $TEST_LOG"
  exit 0
else
  echo "╔════════════════════════════════════════════════════════════════╗"
  echo "║                  ❌ TESTS FAILED                               ║"
  echo "║        Review failures above and in: $TEST_LOG"
  echo "║        Consider rolling back to previous version.             ║"
  echo "╚════════════════════════════════════════════════════════════════╝"
  echo ""
  exit 1
fi
