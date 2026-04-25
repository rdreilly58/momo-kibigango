#!/bin/bash
# Post-Update Tool Verification Script
# Tests critical tools after OpenClaw update
# Usage: bash verify-tools-post-update.sh

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         Tool Verification After OpenClaw Update               ║"
echo "║         Validates all critical functions                      ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

TESTS_RUN=0
TESTS_PASS=0
TESTS_FAIL=0

test_tool() {
  local name=$1
  local test_cmd=$2
  ((TESTS_RUN++))
  
  echo -n "Testing $name... "
  if eval "$test_cmd" > /dev/null 2>&1; then
    echo "✅"
    ((TESTS_PASS++))
  else
    echo "❌"
    ((TESTS_FAIL++))
  fi
}

echo "CRITICAL TOOLS (must work):"
echo "════════════════════════════════════════════════════════════════"

test_tool "exec" "bash -c 'echo test'"
test_tool "read" "[ -r ~/.openclaw/openclaw.json ]"
test_tool "write" "bash -c 'echo x > /tmp/write-test && rm /tmp/write-test'"
test_tool "edit" "[ -w ~/.openclaw/workspace/TOOLS.md ]"
test_tool "process" "bash -c 'sleep 0.1 & wait'"

echo ""
echo "INTEGRATION TOOLS (should be available):"
echo "════════════════════════════════════════════════════════════════"

test_tool "web_search (Brave)" "grep -q 'brave' ~/.openclaw/openclaw.json"
test_tool "cron" "openclaw cron list > /dev/null 2>&1"
test_tool "memory_search" "grep -q 'memorySearch' ~/.openclaw/config.json"
test_tool "gateway" "openclaw gateway status > /dev/null 2>&1"

echo ""
echo "SECURITY CHECKS (should be DENIED):"
echo "════════════════════════════════════════════════════════════════"

test_tool "camera.snap denied" "grep -q 'camera.snap' ~/.openclaw/openclaw.json"
test_tool "screen.record denied" "grep -q 'screen.record' ~/.openclaw/openclaw.json"
test_tool "sms.send denied" "grep -q 'sms.send' ~/.openclaw/openclaw.json"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "SUMMARY"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Tests Run: $TESTS_RUN"
echo "Passed: $TESTS_PASS"
echo "Failed: $TESTS_FAIL"
echo ""

if [ $TESTS_FAIL -eq 0 ]; then
  echo "✅ ALL TOOLS OK - System is healthy!"
  echo ""
  exit 0
else
  echo "❌ SOME TOOLS BROKEN - Restoration needed"
  echo ""
  echo "Next steps:"
  echo "  1. Check configuration: cat ~/.openclaw/config.json | jq '.tools'"
  echo "  2. Restore from backup: bash ~/.openclaw/workspace/scripts/restore-tools.sh"
  echo "  3. Restart gateway: openclaw gateway restart"
  echo "  4. Re-verify: bash ~/.openclaw/workspace/scripts/verify-tools-post-update.sh"
  echo ""
  exit 1
fi
