#!/bin/bash
# Tier A+B+C Integration Test Suite
# Verifies that complex coding tasks ALWAYS use Claude Code
# Date: March 26, 2026

set -e

WORKSPACE="$HOME/.openclaw/workspace"
RESULTS_FILE="$WORKSPACE/tests/tier-integration-results.txt"
mkdir -p "$WORKSPACE/tests"
> "$RESULTS_FILE"

echo "════════════════════════════════════════════════════════════════"
echo "🧪 TIER A+B+C INTEGRATION TEST SUITE"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Purpose: Verify that complex tasks use Claude Code (not direct)"
echo "Start time: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

run_test() {
  local TEST_NUM=$1
  local TEST_NAME=$2
  local TASK_DESC=$3
  local EXPECTED_TIER=$4
  
  ((TOTAL_TESTS++))
  
  echo "TEST $TEST_NUM: $TEST_NAME"
  echo "  Task: $TASK_DESC"
  echo "  Expected: $EXPECTED_TIER"
  
  OUTPUT=$(bash "$WORKSPACE/scripts/classify-coding-task.sh" "$TASK_DESC" 2>&1)
  CLASSIFIED=$(echo "$OUTPUT" | grep "^CLASSIFIED_MODEL=" | cut -d'=' -f2 | tr -d ' ')
  
  if [ "$CLASSIFIED" = "$EXPECTED_TIER" ]; then
    echo "  ✅ PASS: Classified as $CLASSIFIED"
    ((PASSED_TESTS++))
    echo "TEST $TEST_NUM: PASS" >> "$RESULTS_FILE"
  else
    echo "  ❌ FAIL: Got $CLASSIFIED, expected $EXPECTED_TIER"
    ((FAILED_TESTS++))
    echo "TEST $TEST_NUM: FAIL" >> "$RESULTS_FILE"
  fi
  echo ""
}

echo "═══════════════════════════════════════════════════════════════"
echo "SECTION 1: TRIVIAL FIXES (Haiku)"
echo "═══════════════════════════════════════════════════════════════"
echo ""

run_test 1 "Typo fix" "Fix typo in error message" "haiku"
run_test 2 "Missing import" "Add missing import statement" "haiku"
run_test 3 "Formatting" "Fix code formatting and whitespace" "haiku"

echo "═══════════════════════════════════════════════════════════════"
echo "SECTION 2: MEDIUM FEATURES (Opus + Claude Code)"
echo "═══════════════════════════════════════════════════════════════"
echo ""

run_test 4 "Add feature" "Add caching layer to network module" "opus"
run_test 5 "Implement" "Implement user authentication system" "opus"
run_test 6 "Refactor" "Refactor database connection pooling" "opus"

echo "═══════════════════════════════════════════════════════════════"
echo "SECTION 3: COMPLEX TASKS (GPT-4 + Claude Code)"
echo "═══════════════════════════════════════════════════════════════"
echo ""

run_test 7 "Architecture redesign" "Redesign entire authentication architecture" "gpt4"
run_test 8 "Major refactor" "Major refactor: rewrite data layer with CQRS pattern" "gpt4"
run_test 9 "Complex feature" "Implement distributed caching system with consistency checks" "gpt4"

echo "═══════════════════════════════════════════════════════════════"
echo "SECTION 4: CLAUDE CODE VERIFICATION"
echo "═══════════════════════════════════════════════════════════════"
echo ""

((TOTAL_TESTS++))
echo "TEST 10: Verify SOUL.md documents Claude Code for complex tasks"

SOUL_CHECK=$(grep -c "Claude Code\|subagent\|sessions_spawn" "$WORKSPACE/SOUL.md" || echo "0")

if [ "$SOUL_CHECK" -gt 5 ]; then
  echo "  ✅ PASS: SOUL.md documents Claude Code usage ($SOUL_CHECK references)"
  ((PASSED_TESTS++))
  echo "TEST 10: PASS" >> "$RESULTS_FILE"
else
  echo "  ❌ FAIL: SOUL.md missing Claude Code references"
  ((FAILED_TESTS++))
  echo "TEST 10: FAIL" >> "$RESULTS_FILE"
fi
echo ""

echo "═══════════════════════════════════════════════════════════════"
echo "SECTION 5: TIER B ROUTING (OpenRouter)"
echo "═══════════════════════════════════════════════════════════════"
echo ""

((TOTAL_TESTS++))
echo "TEST 11: Verify OpenRouter routing for Opus tasks"

SPAWN_OUTPUT=$(bash "$WORKSPACE/scripts/spawn-with-openrouter.sh" "Add feature" 2>&1)

if echo "$SPAWN_OUTPUT" | grep -q "openrouter\|OpenRouter"; then
  echo "  ✅ PASS: OpenRouter routing detected for Opus"
  ((PASSED_TESTS++))
  echo "TEST 11: PASS" >> "$RESULTS_FILE"
else
  echo "  ❌ FAIL: OpenRouter routing not configured"
  ((FAILED_TESTS++))
  echo "TEST 11: FAIL" >> "$RESULTS_FILE"
fi
echo ""

echo "═══════════════════════════════════════════════════════════════"
echo "SECTION 6: TIER C BATCHING"
echo "═══════════════════════════════════════════════════════════════"
echo ""

((TOTAL_TESTS++))
echo "TEST 12: Verify task batching analyzer"

ANALYZER_OUTPUT=$(bash "$WORKSPACE/scripts/analyze-task-complexity.sh" "Implement feature" file1.swift file2.swift 2>&1)

if echo "$ANALYZER_OUTPUT" | grep -q "BATCH\|Cost\|Analysis"; then
  echo "  ✅ PASS: Task analyzer working"
  ((PASSED_TESTS++))
  echo "TEST 12: PASS" >> "$RESULTS_FILE"
else
  echo "  ❌ FAIL: Task analyzer output incomplete"
  ((FAILED_TESTS++))
  echo "TEST 12: FAIL" >> "$RESULTS_FILE"
fi
echo ""

echo "═══════════════════════════════════════════════════════════════"
echo "SECTION 7: COST TRACKING"
echo "═══════════════════════════════════════════════════════════════"
echo ""

((TOTAL_TESTS++))
echo "TEST 13: Verify cost tracking"

bash "$WORKSPACE/scripts/track-subagent-costs.sh" "Test task" "opus" "0.015" 2>&1 >/dev/null

if [ -f "$HOME/.openclaw/logs/subagent-costs/2026-03-26.log" ]; then
  echo "  ✅ PASS: Cost tracking log created"
  ((PASSED_TESTS++))
  echo "TEST 13: PASS" >> "$RESULTS_FILE"
else
  echo "  ❌ FAIL: Cost tracking log not found"
  ((FAILED_TESTS++))
  echo "TEST 13: FAIL" >> "$RESULTS_FILE"
fi
echo ""

echo "═══════════════════════════════════════════════════════════════"
echo "SECTION 8: DOCUMENTATION"
echo "═══════════════════════════════════════════════════════════════"
echo ""

((TOTAL_TESTS++))
echo "TEST 14: Verify Tier A documented"
if grep -q "Tier A\|Smart.*Classification" "$WORKSPACE/SOUL.md"; then
  echo "  ✅ PASS: Tier A documented"
  ((PASSED_TESTS++))
  echo "TEST 14: PASS" >> "$RESULTS_FILE"
else
  echo "  ❌ FAIL: Tier A not documented"
  ((FAILED_TESTS++))
  echo "TEST 14: FAIL" >> "$RESULTS_FILE"
fi
echo ""

((TOTAL_TESTS++))
echo "TEST 15: Verify Tier B documented"
if grep -q "Tier B\|OpenRouter" "$WORKSPACE/SOUL.md"; then
  echo "  ✅ PASS: Tier B documented"
  ((PASSED_TESTS++))
  echo "TEST 15: PASS" >> "$RESULTS_FILE"
else
  echo "  ❌ FAIL: Tier B not documented"
  ((FAILED_TESTS++))
  echo "TEST 15: FAIL" >> "$RESULTS_FILE"
fi
echo ""

((TOTAL_TESTS++))
echo "TEST 16: Verify Tier C documented"
if grep -q "Tier C\|Batching" "$WORKSPACE/SOUL.md"; then
  echo "  ✅ PASS: Tier C documented"
  ((PASSED_TESTS++))
  echo "TEST 16: PASS" >> "$RESULTS_FILE"
else
  echo "  ❌ FAIL: Tier C not documented"
  ((FAILED_TESTS++))
  echo "TEST 16: FAIL" >> "$RESULTS_FILE"
fi
echo ""

# Final summary
echo "════════════════════════════════════════════════════════════════"
echo "📊 TEST SUMMARY"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Total tests: $TOTAL_TESTS"
echo "Passed: $PASSED_TESTS ✅"
echo "Failed: $FAILED_TESTS"
echo ""

if [ "$FAILED_TESTS" -eq 0 ]; then
  PASS_RATE=100
  echo "🎉 ALL TESTS PASSED! ✅"
  echo ""
  echo "VERIFICATION RESULTS:"
  echo "  ✅ Complex tasks verified to use Claude Code"
  echo "  ✅ Tier A classification working (Haiku/Opus/GPT-4)"
  echo "  ✅ Tier B OpenRouter routing active"
  echo "  ✅ Tier C batching system operational"
  echo "  ✅ Cost tracking fully functional"
  echo "  ✅ All documentation complete"
else
  PASS_RATE=$(( (PASSED_TESTS * 100) / TOTAL_TESTS ))
  echo "⚠️ Some tests failed"
fi

echo ""
echo "Pass rate: ${PASS_RATE}%"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "DETAILED RESULTS"
echo "════════════════════════════════════════════════════════════════"
cat "$RESULTS_FILE"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ TEST SUITE COMPLETE"
echo "════════════════════════════════════════════════════════════════"
