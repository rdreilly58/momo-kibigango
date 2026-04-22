#!/bin/bash
# test_daily_session_reset.sh — Test suite for daily-session-reset.sh
#
# Tests the session summary / daily notes functionality added in
# commit e634d5b (fix: agent-written session summaries replace broken hook)
#
# Usage: bash Tests/test_daily_session_reset.sh

set -uo pipefail

SCRIPT="$(cd "$(dirname "$0")/.." && pwd)/scripts/daily-session-reset.sh"
TODAY=$(date +%Y-%m-%d)
PASS=0
FAIL=0
TMPDIR_BASE=""

# ── Helpers ───────────────────────────────────────────────────────────────────

setup() {
    TMPDIR_BASE=$(mktemp -d /tmp/test-daily-reset-XXXXXX)
    mkdir -p "$TMPDIR_BASE/memory/archive"
    # Minimal MEMORY.md so the size check doesn't crash
    echo "# MEMORY" > "$TMPDIR_BASE/MEMORY.md"
    export OPENCLAW_TEST_WORKSPACE="$TMPDIR_BASE"
}

teardown() {
    rm -rf "$TMPDIR_BASE"
    unset OPENCLAW_TEST_WORKSPACE
}

pass() { echo "  ✅ $1"; PASS=$((PASS + 1)); }
fail() { echo "  ❌ $1"; FAIL=$((FAIL + 1)); }

assert_file_exists() {
    local path="$1" label="$2"
    [ -f "$path" ] && pass "$label" || fail "$label (file not found: $path)"
}

assert_contains() {
    local file="$1" pattern="$2" label="$3"
    grep -q "$pattern" "$file" 2>/dev/null && pass "$label" || fail "$label (pattern not found: '$pattern' in $file)"
}

assert_not_contains() {
    local file="$1" pattern="$2" label="$3"
    grep -q "$pattern" "$file" 2>/dev/null && fail "$label (unexpected pattern found: '$pattern')" || pass "$label"
}

assert_count() {
    local file="$1" pattern="$2" expected="$3" label="$4"
    local actual
    actual=$(grep -c "$pattern" "$file" 2>/dev/null || echo 0)
    [ "$actual" -eq "$expected" ] && pass "$label" || fail "$label (expected $expected occurrences, got $actual)"
}

# ── Test Cases ────────────────────────────────────────────────────────────────

test_template_creation() {
    echo ""
    echo "▶ Template creation"
    setup
    local daily="$TMPDIR_BASE/memory/$TODAY.md"

    bash "$SCRIPT" > /dev/null 2>&1

    assert_file_exists "$daily" "daily notes file created at correct path"
    assert_contains "$daily" "^# Daily Notes" "file has correct H1 header"
    assert_contains "$daily" "^## Session Start" "file has Session Start section"
    assert_contains "$daily" "^## Tasks" "file has Tasks section"
    assert_contains "$daily" "^## Learnings" "file has Learnings section"
    assert_contains "$daily" "^## Issues Encountered" "file has Issues Encountered section"
    assert_contains "$daily" "^## End of Day Summary" "file has End of Day Summary section"

    # Date should be expanded, not literal
    assert_not_contains "$daily" '\$(date)' 'date variable is expanded (not literal)'
    assert_contains "$daily" "$(date +%Y)" "expanded date contains current year"

    teardown
}

test_idempotent_creation() {
    echo ""
    echo "▶ Idempotent creation (file not overwritten)"
    setup
    local daily="$TMPDIR_BASE/memory/$TODAY.md"

    # Pre-seed with sentinel content
    mkdir -p "$(dirname "$daily")"
    echo "# EXISTING FILE - do not overwrite" > "$daily"

    bash "$SCRIPT" > /dev/null 2>&1

    assert_contains "$daily" "EXISTING FILE" "pre-existing file is not overwritten"
    teardown
}

test_log_flag_appends_to_summary() {
    echo ""
    echo "▶ --log flag appends to End of Day Summary"
    setup

    bash "$SCRIPT" > /dev/null 2>&1
    bash "$SCRIPT" --log "Test summary entry ABC123" > /dev/null 2>&1

    local daily="$TMPDIR_BASE/memory/$TODAY.md"
    assert_contains "$daily" "Test summary entry ABC123" "summary text appears in file"
    assert_contains "$daily" "^## End of Day Summary" "End of Day Summary section preserved"
    teardown
}

test_log_flag_multiple_appends() {
    echo ""
    echo "▶ --log flag: multiple entries accumulate"
    setup

    bash "$SCRIPT" > /dev/null 2>&1
    bash "$SCRIPT" --log "First entry ALPHA" > /dev/null 2>&1
    bash "$SCRIPT" --log "Second entry BETA" > /dev/null 2>&1

    local daily="$TMPDIR_BASE/memory/$TODAY.md"
    assert_contains "$daily" "First entry ALPHA" "first entry present"
    assert_contains "$daily" "Second entry BETA" "second entry present"
    teardown
}

test_sourced_log_tasks_section() {
    echo ""
    echo "▶ log_session_entry: appends to Tasks section"
    setup

    bash "$SCRIPT" > /dev/null 2>&1

    # Source the script to get log_session_entry(), then call it
    (
        source "$SCRIPT" 2>/dev/null || true
        log_session_entry "Tasks" "- Implemented feature XYZ" > /dev/null 2>&1
    )

    local daily="$TMPDIR_BASE/memory/$TODAY.md"
    assert_contains "$daily" "Implemented feature XYZ" "task entry appears in file"
    teardown
}

test_sourced_log_learnings_section() {
    echo ""
    echo "▶ log_session_entry: appends to Learnings section"
    setup

    bash "$SCRIPT" > /dev/null 2>&1

    (
        source "$SCRIPT" 2>/dev/null || true
        log_session_entry "Learnings" "- Learned about BSD sed" > /dev/null 2>&1
    )

    local daily="$TMPDIR_BASE/memory/$TODAY.md"
    assert_contains "$daily" "Learned about BSD sed" "learning entry appears in file"
    teardown
}

test_sourced_log_new_section() {
    echo ""
    echo "▶ log_session_entry: creates new section when not found"
    setup

    bash "$SCRIPT" > /dev/null 2>&1

    (
        source "$SCRIPT" 2>/dev/null || true
        log_session_entry "Custom Section" "- Custom content entry" > /dev/null 2>&1
    )

    local daily="$TMPDIR_BASE/memory/$TODAY.md"
    assert_contains "$daily" "^## Custom Section" "new section header created"
    assert_contains "$daily" "Custom content entry" "content appears under new section"
    teardown
}

test_log_creates_file_if_missing() {
    echo ""
    echo "▶ --log creates daily file if it does not exist yet"
    setup
    local daily="$TMPDIR_BASE/memory/$TODAY.md"

    # Don't run main reset — just call --log directly
    bash "$SCRIPT" --log "Entry without pre-existing file" > /dev/null 2>&1

    assert_file_exists "$daily" "daily file created on first --log call"
    assert_contains "$daily" "Entry without pre-existing file" "entry present in new file"
    teardown
}

test_sections_not_duplicated() {
    echo ""
    echo "▶ Section headers not duplicated on repeated resets"
    setup

    bash "$SCRIPT" > /dev/null 2>&1
    # Simulate second reset on same day — file already exists, should skip
    bash "$SCRIPT" > /dev/null 2>&1

    local daily="$TMPDIR_BASE/memory/$TODAY.md"
    assert_count "$daily" "^## Tasks" 1 "Tasks section appears exactly once"
    assert_count "$daily" "^## Learnings" 1 "Learnings section appears exactly once"
    assert_count "$daily" "^## End of Day Summary" 1 "End of Day Summary appears exactly once"
    teardown
}

test_archive_yesterday() {
    echo ""
    echo "▶ Yesterday's file is archived"
    setup
    local yesterday
    yesterday=$(date -v-1d +%Y-%m-%d 2>/dev/null || date -d "1 day ago" +%Y-%m-%d)
    local yfile="$TMPDIR_BASE/memory/$yesterday.md"
    echo "# Yesterday's notes" > "$yfile"

    bash "$SCRIPT" > /dev/null 2>&1

    assert_file_exists "$TMPDIR_BASE/memory/archive/$yesterday.md" "yesterday's file copied to archive"
    assert_file_exists "$yfile" "yesterday's original file still present"
    teardown
}

# ── Run all tests ─────────────────────────────────────────────────────────────

echo "========================================"
echo "  daily-session-reset.sh test suite"
echo "  Script: $SCRIPT"
echo "  Date:   $TODAY"
echo "========================================"

test_template_creation
test_idempotent_creation
test_log_flag_appends_to_summary
test_log_flag_multiple_appends
test_sourced_log_tasks_section
test_sourced_log_learnings_section
test_sourced_log_new_section
test_log_creates_file_if_missing
test_sections_not_duplicated
test_archive_yesterday

echo ""
echo "========================================"
echo "  Results: $PASS passed, $FAIL failed"
echo "========================================"

[ "$FAIL" -eq 0 ] && exit 0 || exit 1
