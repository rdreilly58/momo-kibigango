#!/bin/bash
# test_progress_notify.sh — Test suite for progress communication features
#
# Tests:
#   1.  Script exists and is executable
#   2.  SOUL.md: Progress Communication Protocol section present
#   3.  SOUL.md: Subagent forwarding instructions present
#   4.  SOUL.md: "never go silent" rule present
#   5.  settings.json: PreToolUse hook configured
#   6.  Hook exits 0 with no credentials (safe no-op)
#   7.  Hook exits 0 for non-heavy tools (Read, Edit, Grep, Glob)
#   8.  Hook exits 0 when throttled (state file fresh)
#   9.  Hook fires and updates state file for heavy tool + long silence
#  10.  Correct Telegram label for each heavy tool type
#  11.  Bash/Agent/mcp__ tools all pass the heavy-tool filter
#  12.  curl not called if throttled
#  13.  Hook handles malformed JSON gracefully (exits 0)
#  14.  Hook handles missing state file (treats as long silence)
#
# Usage: bash Tests/test_progress_notify.sh

set -uo pipefail   # -e intentionally OFF so test failures don't abort the suite

WORKSPACE="$HOME/.openclaw/workspace"
HOOK="$WORKSPACE/scripts/progress-notify-hook.sh"
SOUL="$WORKSPACE/SOUL.md"
SETTINGS="$HOME/.claude/settings.json"
RESULTS_LOG="$WORKSPACE/Tests/test_progress_notify.log"

PASS=0; FAIL=0; SKIP=0; TOTAL=0

# ── Colours ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; BOLD='\033[1m'; NC='\033[0m'

# ── Framework ─────────────────────────────────────────────────────────────────
pass() {
    echo -e "  ${GREEN}PASS${NC}  $1"
    echo "PASS: $1" >> "$RESULTS_LOG"
    PASS=$((PASS + 1)); TOTAL=$((TOTAL + 1))
}
fail() {
    echo -e "  ${RED}FAIL${NC}  $1"
    echo "FAIL: $1" >> "$RESULTS_LOG"
    FAIL=$((FAIL + 1)); TOTAL=$((TOTAL + 1))
}
skip() {
    echo -e "  ${YELLOW}SKIP${NC}  $1"
    echo "SKIP: $1" >> "$RESULTS_LOG"
    SKIP=$((SKIP + 1))
}
section() {
    echo ""
    echo -e "${BLUE}${BOLD}══════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}${BOLD}  $1${NC}"
    echo -e "${BLUE}${BOLD}══════════════════════════════════════════════════════${NC}"
    echo "" >> "$RESULTS_LOG"
    echo "=== $1 ===" >> "$RESULTS_LOG"
}

# ── Temp environment setup ────────────────────────────────────────────────────
TMP_DIR=$(mktemp -d)
TMP_WORKSPACE="$TMP_DIR/workspace"
TMP_LOG_DIR="$TMP_DIR/logs"
TMP_BIN="$TMP_DIR/bin"

mkdir -p "$TMP_WORKSPACE/config" "$TMP_LOG_DIR" "$TMP_BIN"

# Fake briefing.env with test credentials
cat > "$TMP_WORKSPACE/config/briefing.env" << 'EOF'
TELEGRAM_BOT_TOKEN=test_fake_token_for_testing
TELEGRAM_CHAT_ID=999888777
EOF

# Fake curl: logs calls to curl-calls.log, exits 0
cat > "$TMP_BIN/curl" << 'EOF'
#!/bin/bash
echo "curl_called: $*" >> "$TMP_LOG_DIR/curl-calls.log"
exit 0
EOF
chmod +x "$TMP_BIN/curl"

# Inject TMP_LOG_DIR reference into the fake curl
sed -i '' "s|\$TMP_LOG_DIR|${TMP_LOG_DIR}|g" "$TMP_BIN/curl" 2>/dev/null || \
  sed -i "s|\$TMP_LOG_DIR|${TMP_LOG_DIR}|g" "$TMP_BIN/curl" 2>/dev/null || true

# Helper: run hook with a given tool_name JSON payload
run_hook() {
    local tool_name="$1"
    local payload="{\"tool_name\":\"${tool_name}\",\"session_id\":\"test-session\",\"transcript_path\":\"/tmp/test.jsonl\"}"

    PATH="$TMP_BIN:$PATH" \
    OPENCLAW_TEST_WORKSPACE="$TMP_WORKSPACE" \
    OPENCLAW_TEST_LOG_DIR="$TMP_LOG_DIR" \
    bash "$HOOK" <<< "$payload"
    return $?
}

run_hook_silent() {
    run_hook "$1" 2>/dev/null
    return $?
}

# Helper: count curl calls
curl_call_count() {
    [ -f "$TMP_LOG_DIR/curl-calls.log" ] && wc -l < "$TMP_LOG_DIR/curl-calls.log" | tr -d ' ' || echo 0
}

reset_curl_log() {
    rm -f "$TMP_LOG_DIR/curl-calls.log"
}

reset_state() {
    rm -f "$TMP_LOG_DIR/progress-notify-last.txt"
    reset_curl_log
}

set_last_notify_age() {
    # Set state file to NOW minus N seconds
    local seconds_ago="$1"
    local ts=$(($(date +%s) - seconds_ago))
    echo "$ts" > "$TMP_LOG_DIR/progress-notify-last.txt"
}

> "$RESULTS_LOG"

# ════════════════════════════════════════════════════════════════════════════════
section "1. FILE EXISTENCE AND PERMISSIONS"
# ════════════════════════════════════════════════════════════════════════════════

[ -f "$HOOK" ] && pass "Hook script exists" || fail "Hook script missing: $HOOK"
[ -x "$HOOK" ] && pass "Hook script is executable" || fail "Hook script not executable"

# ════════════════════════════════════════════════════════════════════════════════
section "2. SOUL.MD CONTENT"
# ════════════════════════════════════════════════════════════════════════════════

grep -q "Progress Communication Protocol" "$SOUL" 2>/dev/null && \
    pass "SOUL.md: Progress Communication Protocol section present" || \
    fail "SOUL.md: Missing 'Progress Communication Protocol' section"

grep -q "Subagent Progress Forwarding" "$SOUL" 2>/dev/null && \
    pass "SOUL.md: Subagent progress forwarding section present" || \
    fail "SOUL.md: Missing 'Subagent Progress Forwarding' section"

grep -q "never go silent\|Never go silent" "$SOUL" 2>/dev/null && \
    pass "SOUL.md: 'Never go silent' rule present" || \
    fail "SOUL.md: Missing 'Never go silent' rule"

grep -q "Phase Announcements" "$SOUL" 2>/dev/null && \
    pass "SOUL.md: Phase Announcements section present" || \
    fail "SOUL.md: Missing 'Phase Announcements' section"

grep -q "mcp__openclaw__sessions_send" "$SOUL" 2>/dev/null && \
    pass "SOUL.md: subagent sessions_send instruction present" || \
    fail "SOUL.md: Missing sessions_send reference in subagent instructions"

# ════════════════════════════════════════════════════════════════════════════════
section "3. SETTINGS.JSON CONFIGURATION"
# ════════════════════════════════════════════════════════════════════════════════

if [ -f "$SETTINGS" ]; then
    grep -q "PreToolUse" "$SETTINGS" 2>/dev/null && \
        pass "settings.json: PreToolUse hook key present" || \
        fail "settings.json: PreToolUse hook key missing (may need manual approval)"

    grep -q "progress-notify-hook.sh" "$SETTINGS" 2>/dev/null && \
        pass "settings.json: progress-notify-hook.sh registered" || \
        fail "settings.json: progress-notify-hook.sh not registered"
else
    skip "settings.json not found — skipping hook registration checks"
fi

# ════════════════════════════════════════════════════════════════════════════════
section "4. HOOK: SAFE NO-OPS"
# ════════════════════════════════════════════════════════════════════════════════

# Test: exits 0 with no credentials
reset_state
result=$(PATH="$TMP_BIN:$PATH" \
    OPENCLAW_TEST_WORKSPACE="$TMP_DIR/no-such-workspace" \
    OPENCLAW_TEST_LOG_DIR="$TMP_LOG_DIR" \
    bash "$HOOK" <<< '{"tool_name":"Agent","session_id":"s1"}' 2>/dev/null; echo $?)
[ "$result" = "0" ] && pass "Hook exits 0 when no credentials configured" || \
    fail "Hook exits non-zero when no credentials (got: $result)"

# Test: exits 0 for non-heavy tools
reset_state
for tool in Read Edit Write Grep Glob LS NotebookRead; do
    exit_code=0
    run_hook_silent "$tool" || exit_code=$?
    calls=$(curl_call_count)
    [ "$exit_code" = "0" ] && [ "$calls" = "0" ] && \
        pass "Hook is no-op for non-heavy tool: $tool" || \
        fail "Hook incorrectly acted on non-heavy tool: $tool (exit=$exit_code curl_calls=$calls)"
    reset_curl_log
done

# ════════════════════════════════════════════════════════════════════════════════
section "5. HOOK: THROTTLE LOGIC"
# ════════════════════════════════════════════════════════════════════════════════

# Set last notify to 10 seconds ago (below threshold)
set_last_notify_age 10
reset_curl_log
run_hook_silent "Agent"
calls=$(curl_call_count)
[ "$calls" = "0" ] && pass "Hook throttled when last notify was 10s ago" || \
    fail "Hook fired when should be throttled (calls=$calls)"

# Set last notify to 30 seconds ago (still below 75s threshold)
set_last_notify_age 30
reset_curl_log
run_hook_silent "Bash"
calls=$(curl_call_count)
[ "$calls" = "0" ] && pass "Hook throttled when last notify was 30s ago" || \
    fail "Hook fired when should be throttled at 30s (calls=$calls)"

# Set last notify to exactly threshold-1 seconds ago
THRESHOLD=75
set_last_notify_age $((THRESHOLD - 1))
reset_curl_log
OPENCLAW_TEST_SILENCE_THRESHOLD=$THRESHOLD run_hook_silent "Agent"
calls=$(curl_call_count)
[ "$calls" = "0" ] && pass "Hook throttled when 1s below threshold" || \
    fail "Hook fired when 1s below threshold (calls=$calls)"

# ════════════════════════════════════════════════════════════════════════════════
section "6. HOOK: FIRES ON LONG SILENCE"
# ════════════════════════════════════════════════════════════════════════════════

# Use a low threshold (5s) to avoid needing actual time to pass
LOW_THRESHOLD=5
set_last_notify_age 10  # 10s ago, above 5s threshold
reset_curl_log

PATH="$TMP_BIN:$PATH" \
OPENCLAW_TEST_WORKSPACE="$TMP_WORKSPACE" \
OPENCLAW_TEST_LOG_DIR="$TMP_LOG_DIR" \
OPENCLAW_TEST_SILENCE_THRESHOLD=$LOW_THRESHOLD \
bash "$HOOK" <<< '{"tool_name":"Agent","session_id":"s1"}' 2>/dev/null

calls=$(curl_call_count)
[ "$calls" -ge 1 ] && pass "Hook fires curl when heavy tool + silence > threshold" || \
    fail "Hook did not fire curl for heavy tool with long silence (calls=$calls)"

# State file should be updated
state_ts=$(cat "$TMP_LOG_DIR/progress-notify-last.txt" 2>/dev/null || echo 0)
now=$(date +%s)
age=$((now - state_ts))
[ "$age" -le 5 ] && pass "State file updated after firing" || \
    fail "State file not updated (age=${age}s, expected <= 5s)"

# ════════════════════════════════════════════════════════════════════════════════
section "7. HOOK: HEAVY TOOL FILTER"
# ════════════════════════════════════════════════════════════════════════════════

LOW_THRESHOLD=5

for tool in Agent Bash mcp__openclaw__sessions_spawn mcp__openclaw__web_search mcp__openclaw__memory_get; do
    set_last_notify_age 10
    reset_curl_log

    PATH="$TMP_BIN:$PATH" \
    OPENCLAW_TEST_WORKSPACE="$TMP_WORKSPACE" \
    OPENCLAW_TEST_LOG_DIR="$TMP_LOG_DIR" \
    OPENCLAW_TEST_SILENCE_THRESHOLD=$LOW_THRESHOLD \
    bash "$HOOK" <<< "{\"tool_name\":\"${tool}\",\"session_id\":\"s1\"}" 2>/dev/null

    calls=$(curl_call_count)
    [ "$calls" -ge 1 ] && pass "Heavy tool passes filter: $tool" || \
        fail "Heavy tool did not pass filter: $tool (calls=$calls)"
done

# ════════════════════════════════════════════════════════════════════════════════
section "8. HOOK: MESSAGE CONTENT"
# ════════════════════════════════════════════════════════════════════════════════

LOW_THRESHOLD=5
set_last_notify_age 120  # 2 minutes silence
reset_curl_log

PATH="$TMP_BIN:$PATH" \
OPENCLAW_TEST_WORKSPACE="$TMP_WORKSPACE" \
OPENCLAW_TEST_LOG_DIR="$TMP_LOG_DIR" \
OPENCLAW_TEST_SILENCE_THRESHOLD=$LOW_THRESHOLD \
bash "$HOOK" <<< '{"tool_name":"Agent","session_id":"s1"}' 2>/dev/null

if [ -f "$TMP_LOG_DIR/curl-calls.log" ]; then
    # Message should contain elapsed time
    grep -q "elapsed" "$TMP_LOG_DIR/curl-calls.log" && \
        pass "Message contains elapsed time" || \
        fail "Message missing elapsed time"
    # Message should contain the working indicator
    grep -q "Still working\|working\|spawning subagent" "$TMP_LOG_DIR/curl-calls.log" && \
        pass "Message contains activity description" || \
        fail "Message missing activity description"
    # Should use correct Telegram API URL
    grep -q "api.telegram.org" "$TMP_LOG_DIR/curl-calls.log" && \
        pass "curl targets Telegram API" || \
        fail "curl does not target Telegram API"
else
    fail "No curl log found after firing"
fi

# ════════════════════════════════════════════════════════════════════════════════
section "9. HOOK: RESILIENCE"
# ════════════════════════════════════════════════════════════════════════════════

# Malformed JSON — should exit 0 gracefully
result=$(PATH="$TMP_BIN:$PATH" \
    OPENCLAW_TEST_WORKSPACE="$TMP_WORKSPACE" \
    OPENCLAW_TEST_LOG_DIR="$TMP_LOG_DIR" \
    bash "$HOOK" <<< 'this is not json at all' 2>/dev/null; echo $?)
[ "$result" = "0" ] && pass "Hook exits 0 on malformed JSON" || \
    fail "Hook crashed on malformed JSON (exit=$result)"

# Empty stdin — should exit 0 gracefully
result=$(PATH="$TMP_BIN:$PATH" \
    OPENCLAW_TEST_WORKSPACE="$TMP_WORKSPACE" \
    OPENCLAW_TEST_LOG_DIR="$TMP_LOG_DIR" \
    bash "$HOOK" <<< '' 2>/dev/null; echo $?)
[ "$result" = "0" ] && pass "Hook exits 0 on empty stdin" || \
    fail "Hook crashed on empty stdin (exit=$result)"

# Missing state file — should treat as long silence (not crash)
reset_state  # removes state file
LOW_THRESHOLD=5
result=$(PATH="$TMP_BIN:$PATH" \
    OPENCLAW_TEST_WORKSPACE="$TMP_WORKSPACE" \
    OPENCLAW_TEST_LOG_DIR="$TMP_LOG_DIR" \
    OPENCLAW_TEST_SILENCE_THRESHOLD=$LOW_THRESHOLD \
    bash "$HOOK" <<< '{"tool_name":"Agent","session_id":"s1"}' 2>/dev/null; echo $?)
[ "$result" = "0" ] && pass "Hook exits 0 when state file missing (first run)" || \
    fail "Hook crashed when state file missing (exit=$result)"

# ════════════════════════════════════════════════════════════════════════════════
section "10. HOOK: SYNTAX VALIDATION"
# ════════════════════════════════════════════════════════════════════════════════

bash -n "$HOOK" 2>/dev/null && pass "Hook passes bash -n syntax check" || \
    fail "Hook has syntax errors (bash -n failed)"

# ════════════════════════════════════════════════════════════════════════════════
# Cleanup
# ════════════════════════════════════════════════════════════════════════════════
rm -rf "$TMP_DIR"

# ════════════════════════════════════════════════════════════════════════════════
# Summary
# ════════════════════════════════════════════════════════════════════════════════
echo ""
echo -e "${BLUE}${BOLD}══════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}  Results: ${GREEN}${PASS} passed${NC}  ${RED}${FAIL} failed${NC}  ${YELLOW}${SKIP} skipped${NC}  (${TOTAL} total)${BOLD}${NC}"
echo -e "${BLUE}${BOLD}══════════════════════════════════════════════════════${NC}"
echo ""

if [ "$FAIL" -gt 0 ]; then
    echo -e "${RED}${BOLD}FAILURES:${NC}"
    grep "^FAIL:" "$RESULTS_LOG" | sed 's/^FAIL:/  ✗/' | while IFS= read -r line; do
        echo -e "  ${RED}${line}${NC}"
    done
    echo ""
    exit 1
fi

exit 0
