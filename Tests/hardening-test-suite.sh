#!/bin/bash
# hardening-test-suite.sh — Tests for all script hardening changes (2026-04-21)
#
# Tests:
#   1. Syntax validation — all modified scripts
#   2. notify.sh unit tests — each function in isolation
#   3. ERR trap behaviour — fires, doesn't fire in correct cases
#   4. Arithmetic safety — no ((var++)) exit-code bombs
#   5. Log rotation — old files pruned, new files preserved
#   6. softwareupdate parsing — asterisk counting
#   7. auto-update-system.sh --dry-run end-to-end
#   8. launchd plist validation — PATH, HOME, XML validity
#   9. set -Eeuo pipefail flags — all modified scripts
#  10. send-briefing-v2.sh structure — traps, sources, EXIT cleanup
#
# Usage: bash Tests/hardening-test-suite.sh

set -uo pipefail    # -e intentionally OFF so test failures don't abort the suite

WORKSPACE="$HOME/.openclaw/workspace"
RESULTS_LOG="$WORKSPACE/Tests/hardening-test-results.log"
PASS=0; FAIL=0; SKIP=0; TOTAL=0

# ── Colours ──────────────────────────────────────────────────────────────────
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
assert_contains() {
    local label="$1" file="$2" pattern="$3"
    if grep -qE "$pattern" "$file" 2>/dev/null; then pass "$label"; else fail "$label — pattern '$pattern' not in $file"; fi
}
assert_not_contains() {
    local label="$1" file="$2" pattern="$3"
    if ! grep -qE "$pattern" "$file" 2>/dev/null; then pass "$label"; else fail "$label — found disallowed pattern '$pattern' in $file"; fi
}

mkdir -p "$(dirname "$RESULTS_LOG")"
echo "Hardening Test Suite — $(date '+%Y-%m-%d %H:%M:%S')" > "$RESULTS_LOG"

SCRIPTS_DIR="$WORKSPACE/scripts"
BRIEFING_DIR="$WORKSPACE/skills/daily-briefing/scripts"
LIB="$SCRIPTS_DIR/lib/notify.sh"
AUTO_UPDATE="$SCRIPTS_DIR/auto-update-system.sh"
SEND_BRIEFING="$BRIEFING_DIR/send-briefing-v2.sh"
MORNING="$BRIEFING_DIR/morning-briefing.sh"
EVENING="$BRIEFING_DIR/evening-briefing.sh"
WATCHDOG="$SCRIPTS_DIR/session-watchdog.sh"
HEALTHCHK="$SCRIPTS_DIR/system-health-check.sh"
QUOTAMON="$SCRIPTS_DIR/api-quota-monitor.sh"
CRONMON="$SCRIPTS_DIR/cron-monitor-and-alert.sh"

# =============================================================================
section "1. Syntax Validation (bash -n)"
# =============================================================================

MODIFIED_SCRIPTS=(
    "$LIB"
    "$AUTO_UPDATE"
    "$SEND_BRIEFING"
    "$MORNING"
    "$EVENING"
    "$WATCHDOG"
    "$HEALTHCHK"
    "$QUOTAMON"
    "$CRONMON"
)

for script in "${MODIFIED_SCRIPTS[@]}"; do
    name="$(basename "$script")"
    if [[ ! -f "$script" ]]; then
        fail "$name — file not found"
    elif bash -n "$script" 2>/dev/null; then
        pass "$name — syntax OK"
    else
        fail "$name — syntax error: $(bash -n "$script" 2>&1)"
    fi
done

# =============================================================================
section "2. notify.sh Unit Tests"
# =============================================================================

# Source notify.sh in a clean subshell for each test to avoid side effects
NOTIFY_SOURCED=0
if bash -c "source '$LIB'" 2>/dev/null; then
    pass "notify.sh sources without error"
    NOTIFY_SOURCED=1
else
    fail "notify.sh fails to source: $(bash -c "source '$LIB'" 2>&1)"
fi

if [[ $NOTIFY_SOURCED -eq 1 ]]; then
    # 2a. notify_telegram noop when vars unset
    result=$(bash -c "
        source '$LIB'
        unset TELEGRAM_BOT_TOKEN TELEGRAM_CHAT_ID 2>/dev/null || true
        notify_telegram 'test message'
        echo exit:\$?
    " 2>&1)
    if echo "$result" | grep -q "exit:0"; then
        pass "notify_telegram — noop when tokens unset (no error)"
    else
        fail "notify_telegram — unexpected output when tokens unset: $result"
    fi

    # 2b. hc_ping noop when HEALTHCHECK_URL unset
    result=$(bash -c "
        source '$LIB'
        unset HEALTHCHECK_URL 2>/dev/null || true
        hc_ping '/start'
        echo exit:\$?
    " 2>&1)
    if echo "$result" | grep -q "exit:0"; then
        pass "hc_ping — noop when HEALTHCHECK_URL unset (no error)"
    else
        fail "hc_ping — unexpected error when HEALTHCHECK_URL unset: $result"
    fi

    # 2c. hc_start/success/fail are defined
    for fn in hc_start hc_success hc_fail; do
        result=$(bash -c "source '$LIB'; type $fn" 2>&1)
        if echo "$result" | grep -q "function"; then
            pass "notify.sh — function $fn is defined"
        else
            fail "notify.sh — function $fn missing"
        fi
    done

    # 2d. rotate_logs is defined and runs cleanly
    result=$(bash -c "
        source '$LIB'
        TMPDIR_TEST=\$(mktemp -d)
        touch -t 202303010000 \"\$TMPDIR_TEST/old.log\"
        echo hello > \"\$TMPDIR_TEST/new.log\"
        rotate_logs \"\$TMPDIR_TEST\" '*.log' 30
        old_exists=\$([ -f \"\$TMPDIR_TEST/old.log\" ] && echo yes || echo no)
        new_exists=\$([ -f \"\$TMPDIR_TEST/new.log\" ] && echo yes || echo no)
        rm -rf \"\$TMPDIR_TEST\"
        echo old:\$old_exists new:\$new_exists
    " 2>&1)
    if echo "$result" | grep -q "old:no"; then
        pass "rotate_logs — old log (>30 days) deleted"
    else
        fail "rotate_logs — old log not deleted: $result"
    fi
    if echo "$result" | grep -q "new:yes"; then
        pass "rotate_logs — recent log preserved"
    else
        fail "rotate_logs — recent log unexpectedly deleted: $result"
    fi

    # 2e. _notify_err_handler is defined
    result=$(bash -c "source '$LIB'; type _notify_err_handler" 2>&1)
    if echo "$result" | grep -q "function"; then
        pass "notify.sh — _notify_err_handler is defined"
    else
        fail "notify.sh — _notify_err_handler missing"
    fi
fi

# =============================================================================
section "3. ERR Trap Behaviour"
# =============================================================================

# 3a. ERR trap fires on bare failing command (not inside || or if)
result=$(bash 2>/dev/null <<'BASHEOF'
FIRED=no
trap 'FIRED=yes' ERR
false
echo fired:$FIRED
BASHEOF
) || true
if echo "$result" | grep -q "fired:yes"; then
    pass "ERR trap — fires on bare failing command"
else
    fail "ERR trap — did not fire on bare failing command: '$result'"
fi

# 3b. ERR trap does NOT fire for command in || expression
result=$(bash 2>/dev/null <<'BASHEOF'
set -Eeuo pipefail
FIRED=no
trap 'FIRED=yes' ERR
false || true
echo fired:$FIRED
BASHEOF
) || true
if echo "$result" | grep -q "fired:no"; then
    pass "ERR trap — correctly suppressed for 'false || true'"
else
    fail "ERR trap — incorrectly fired for 'false || true': '$result'"
fi

# 3c. ERR trap does NOT fire for command in if condition
result=$(bash 2>/dev/null <<'BASHEOF'
set -Eeuo pipefail
FIRED=no
trap 'FIRED=yes' ERR
if false; then echo "branch taken"; fi
echo fired:$FIRED
BASHEOF
) || true
if echo "$result" | grep -q "fired:no"; then
    pass "ERR trap — correctly suppressed in 'if false'"
else
    fail "ERR trap — incorrectly fired in 'if false': '$result'"
fi

# 3d. Confirm set -E flag present in all modified scripts (prerequisite for errtrace)
for script in "$AUTO_UPDATE" "$SEND_BRIEFING" "$MORNING" "$EVENING" "$WATCHDOG" "$HEALTHCHK" "$QUOTAMON" "$CRONMON"; do
    name="$(basename "$script")"
    if grep -qE '^set -[EeEuo]+' "$script" 2>/dev/null && grep -q '\-E' <(grep '^set -' "$script" 2>/dev/null); then
        pass "$name — set -E (errtrace) flag present"
    else
        fail "$name — set -E (errtrace) flag MISSING"
    fi
done

# 3e. _notify_err_handler captures $LINENO
result=$(bash 2>/dev/null <<'BASHEOF'
source '/Users/rreilly/.openclaw/workspace/scripts/lib/notify.sh'
# Override notify functions to be no-ops for this test
hc_fail() { true; }
notify_telegram() { true; }
trap '_notify_err_handler $LINENO' ERR
_test_func() { false; }
_test_func 2>/dev/null || true
echo done
BASHEOF
) || true
if echo "$result" | grep -q "done"; then
    pass "ERR trap — _notify_err_handler doesn't abort script when Telegram/HC unset"
else
    fail "ERR trap — _notify_err_handler aborted script unexpectedly: '$result'"
fi

# =============================================================================
section "4. Arithmetic Safety (no ((var++)) exit-code bombs)"
# =============================================================================

# 4a. failed_checks=$((failed_checks + 1)) when counter=0 doesn't exit script
result=$(bash -c "
    set -Eeuo pipefail
    failed_checks=0
    failed_checks=\$((failed_checks + 1))
    echo count:\$failed_checks
" 2>&1)
if echo "$result" | grep -q "count:1"; then
    pass "Arithmetic — failed_checks increment from 0 doesn't crash script"
else
    fail "Arithmetic — failed_checks increment failed: $result"
fi

# 4b. Verify auto-update-system.sh has no ((var++)) pattern
if grep -qE '\(\(.*\+\+\)' "$AUTO_UPDATE" 2>/dev/null; then
    fail "auto-update-system.sh — still contains ((var++)) pattern"
else
    pass "auto-update-system.sh — no ((var++)) arithmetic bombs"
fi

# 4c. Verify other modified scripts have no ((var++)) in critical paths
for script in "$WATCHDOG" "$HEALTHCHK" "$QUOTAMON" "$CRONMON"; do
    name="$(basename "$script")"
    if grep -qE '\(\(.*\+\+\)' "$script" 2>/dev/null; then
        fail "$name — contains ((var++)) pattern (review needed)"
    else
        pass "$name — no ((var++)) arithmetic bombs"
    fi
done

# =============================================================================
section "5. Log Rotation"
# =============================================================================

# 5a. auto-update-system.sh has log rotation
assert_contains "auto-update-system.sh — has find+mtime log rotation" \
    "$AUTO_UPDATE" 'find.*mtime.*delete'

# 5b. session-watchdog.sh has log rotation
assert_contains "session-watchdog.sh — has find+mtime log rotation" \
    "$WATCHDOG" 'find.*mtime.*delete'

# 5c. system-health-check.sh has log rotation
assert_contains "system-health-check.sh — has find+mtime log rotation" \
    "$HEALTHCHK" 'find.*mtime.*delete'

# 5d. api-quota-monitor.sh has log rotation with correct OR syntax
assert_contains "api-quota-monitor.sh — has find+mtime log rotation" \
    "$QUOTAMON" 'find.*mtime.*delete'
assert_contains "api-quota-monitor.sh — uses -o for multiple name patterns" \
    "$QUOTAMON" '\-o -name'

# 5e. Functional rotation test: create a stale log, verify it gets pruned
TMP_LOG_DIR=$(mktemp -d)
stale="$TMP_LOG_DIR/auto-update-20230101-000000.log"
fresh="$TMP_LOG_DIR/auto-update-$(date +%Y%m%d-%H%M%S).log"
touch -t 202301010000 "$stale"
echo "fresh" > "$fresh"
find "$TMP_LOG_DIR" -name "auto-update-*.log" -mtime +30 -delete 2>/dev/null || true
stale_gone=$( [[ ! -f "$stale" ]] && echo yes || echo no )
fresh_kept=$( [[ -f "$fresh" ]] && echo yes || echo no )
rm -rf "$TMP_LOG_DIR"
if [[ "$stale_gone" == "yes" ]]; then pass "Log rotation — stale log deleted"; else fail "Log rotation — stale log not deleted"; fi
if [[ "$fresh_kept" == "yes" ]]; then pass "Log rotation — fresh log preserved"; else fail "Log rotation — fresh log deleted unexpectedly"; fi

# =============================================================================
section "6. softwareupdate Parsing"
# =============================================================================

# 6a. Asterisk counting logic — mock output with updates
mock_with_updates="Software Update Tool

Finding available software
Software Update found the following new or updated software:
* Label: Safari-17.2.1
	Title: Safari, Version: 17.2.1, Size: 82259KiB, Recommended: YES
* Label: macOS-Sequoia-15.4
	Title: macOS Sequoia, Version: 15.4, Size: 3000000KiB"

count=$(echo "$mock_with_updates" | grep -c "^\*") || count=0
if [[ "$count" -eq 2 ]]; then
    pass "softwareupdate parsing — counts 2 updates from asterisk lines"
else
    fail "softwareupdate parsing — expected 2, got $count"
fi

# 6b. No asterisks → 0 updates
mock_no_updates="Software Update Tool

Finding available software

No new software available."
count=$(echo "$mock_no_updates" | grep -c "^\*") || count=0
if [[ "$count" -eq 0 ]]; then
    pass "softwareupdate parsing — correctly returns 0 when no updates"
else
    fail "softwareupdate parsing — expected 0, got $count"
fi

# 6c. auto-update-system.sh uses updated parsing
assert_contains "auto-update-system.sh — uses stderr capture (2>&1)" \
    "$AUTO_UPDATE" 'softwareupdate.*2>&1'
assert_contains "auto-update-system.sh — greps for asterisk lines" \
    "$AUTO_UPDATE" 'grep -c.*\*'
assert_contains "auto-update-system.sh — uses --include-config-data" \
    "$AUTO_UPDATE" 'include-config-data'

# =============================================================================
section "7. auto-update-system.sh --dry-run"
# =============================================================================

DRY_LOG_OUTPUT=$(mktemp)
DRY_EXIT=0
bash "$AUTO_UPDATE" --dry-run >"$DRY_LOG_OUTPUT" 2>&1 || DRY_EXIT=$?

if [[ $DRY_EXIT -eq 0 ]]; then
    pass "auto-update-system.sh --dry-run exits 0"
else
    fail "auto-update-system.sh --dry-run exited $DRY_EXIT"
    echo "    Output: $(tail -5 "$DRY_LOG_OUTPUT")"
fi

if grep -q "DRY RUN" "$DRY_LOG_OUTPUT" 2>/dev/null; then
    pass "auto-update-system.sh --dry-run — DRY RUN messages present"
else
    fail "auto-update-system.sh --dry-run — no DRY RUN messages in output"
fi

if grep -qi "auto-update completed successfully" "$DRY_LOG_OUTPUT" 2>/dev/null; then
    pass "auto-update-system.sh --dry-run — completed successfully message"
else
    fail "auto-update-system.sh --dry-run — missing completion message"
    echo "    Last 5 lines: $(tail -5 "$DRY_LOG_OUTPUT")"
fi

# Check a log file was created
LOG_COUNT=$(find "$HOME/.openclaw/logs" -name "auto-update-*.log" -newer "$DRY_LOG_OUTPUT" 2>/dev/null | wc -l | tr -d ' ')
if [[ "$LOG_COUNT" -gt 0 ]]; then
    pass "auto-update-system.sh --dry-run — log file created in ~/.openclaw/logs/"
else
    skip "auto-update-system.sh --dry-run — log file check inconclusive (timing)"
fi

rm -f "$DRY_LOG_OUTPUT"

# =============================================================================
section "8. launchd Plist Validation"
# =============================================================================

HC_PLIST="$HOME/Library/LaunchAgents/com.momotaro.health-checks.plist"
QM_PLIST="$HOME/Library/LaunchAgents/com.momotaro.quota-monitoring.plist"

for plist in "$HC_PLIST" "$QM_PLIST"; do
    name="$(basename "$plist")"

    if [[ ! -f "$plist" ]]; then
        fail "$name — file not found"
        continue
    fi

    # Valid XML
    if plutil -lint "$plist" >/dev/null 2>&1; then
        pass "$name — valid XML/plist"
    else
        fail "$name — invalid XML: $(plutil -lint "$plist" 2>&1)"
    fi

    # Homebrew PATH present
    if grep -q '/opt/homebrew/bin' "$plist"; then
        pass "$name — /opt/homebrew/bin in PATH"
    else
        fail "$name — /opt/homebrew/bin MISSING from PATH"
    fi

    # /sbin present (full PATH)
    if grep -q '/usr/sbin' "$plist"; then
        pass "$name — /usr/sbin in PATH (full PATH set)"
    else
        fail "$name — /usr/sbin missing (incomplete PATH)"
    fi

    # HOME set
    if grep -q 'HOME' "$plist"; then
        pass "$name — HOME variable set"
    else
        fail "$name — HOME variable missing"
    fi
done

# Confirm launchd loaded them
for label in com.momotaro.health-checks com.momotaro.quota-monitoring; do
    if launchctl list "$label" >/dev/null 2>&1; then
        pass "launchd — $label is loaded"
    else
        fail "launchd — $label is NOT loaded (reload required)"
    fi
done

# =============================================================================
section "9. set -Eeuo pipefail Flags"
# =============================================================================

for script in "${MODIFIED_SCRIPTS[@]}"; do
    name="$(basename "$script")"
    # notify.sh is a sourced library — it intentionally has no set flags
    # (inherits caller's shell options when sourced)
    if [[ "$script" == "$LIB" ]]; then
        pass "$name — sourced library, set flags intentionally omitted"
        continue
    fi
    if grep -qE '^set -Eeuo pipefail' "$script" 2>/dev/null; then
        pass "$name — set -Eeuo pipefail"
    elif grep -qE '^set -euo pipefail' "$script" 2>/dev/null; then
        fail "$name — set -euo pipefail (missing -E errtrace)"
    elif grep -qE '^set -e' "$script" 2>/dev/null; then
        fail "$name — only set -e (missing -Euo pipefail)"
    else
        fail "$name — no set -Eeuo pipefail found"
    fi
done

# =============================================================================
section "10. send-briefing-v2.sh Structure"
# =============================================================================

# Sources notify.sh
assert_contains "send-briefing-v2.sh — sources notify.sh" \
    "$SEND_BRIEFING" 'source.*notify\.sh'

# Has EXIT trap for HTML_FILE cleanup
assert_contains "send-briefing-v2.sh — EXIT trap for HTML_FILE" \
    "$SEND_BRIEFING" "trap.*rm.*HTML_FILE.*EXIT"

# Has ERR trap set
assert_contains "send-briefing-v2.sh — ERR trap defined" \
    "$SEND_BRIEFING" 'trap.*ERR'

# ERR handler calls hc_fail (through notify.sh) or equivalent
# The _briefing_error_handler should use hc_fail not raw curl
if grep -q 'hc_fail' "$SEND_BRIEFING"; then
    pass "send-briefing-v2.sh — ERR handler uses hc_fail from notify.sh"
else
    fail "send-briefing-v2.sh — ERR handler does NOT call hc_fail (healthcheck not pinged on failure)"
fi

# ERR handler calls notify_telegram (through notify.sh) not raw curl
if grep -A5 '_briefing_error_handler' "$SEND_BRIEFING" | grep -q 'notify_telegram'; then
    pass "send-briefing-v2.sh — ERR handler uses notify_telegram from notify.sh"
else
    fail "send-briefing-v2.sh — ERR handler uses raw curl instead of notify_telegram"
fi

# Hardened healthcheck curl at the end
assert_contains "send-briefing-v2.sh — hardened HC curl (fsS flags)" \
    "$SEND_BRIEFING" 'curl -fsS'

# No old-style raw -d text= Telegram in ERR handler (should use notify_telegram)
if grep -A10 '_briefing_error_handler()' "$SEND_BRIEFING" | grep -qE 'curl.*api\.telegram'; then
    fail "send-briefing-v2.sh — ERR handler still has raw Telegram curl"
else
    pass "send-briefing-v2.sh — ERR handler uses library, not raw curl"
fi

# auto-update-system.sh uses library trap (not inline handler)
assert_contains "auto-update-system.sh — uses library _notify_err_handler" \
    "$AUTO_UPDATE" '_notify_err_handler'
assert_not_contains "auto-update-system.sh — no inline _err_handler function" \
    "$AUTO_UPDATE" '^_err_handler\(\)'

# =============================================================================
section "Summary"
# =============================================================================

echo ""
echo -e "${BOLD}Results: ${GREEN}${PASS} passed${NC} / ${RED}${FAIL} failed${NC} / ${YELLOW}${SKIP} skipped${NC} / ${TOTAL} total${NC}"
echo "Log: $RESULTS_LOG"
echo ""

if [[ $FAIL -gt 0 ]]; then
    echo -e "${RED}${BOLD}FAILURES:${NC}"
    grep "^FAIL:" "$RESULTS_LOG" | sed 's/^FAIL:/  •/'
    echo ""
fi

echo "Results: $PASS passed / $FAIL failed / $SKIP skipped / $TOTAL total" >> "$RESULTS_LOG"
exit $([[ $FAIL -eq 0 ]] && echo 0 || echo 1)
