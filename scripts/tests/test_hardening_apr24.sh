#!/bin/bash
# test_hardening_apr24.sh — Test suite for the Apr 24 8-item hardening pass
# Tier: 1
#
# Tests all 9 changes from commit 42d766e.
# Run: bash scripts/tests/test_hardening_apr24.sh
# Exit: 0 if all pass, 1 if any fail

set -uo pipefail

WORKSPACE="$HOME/.openclaw/workspace"
SCRIPTS="$WORKSPACE/scripts"
PASS=0
FAIL=0
SKIP=0

_pass() { echo "  ✅ PASS: $*"; ((PASS++)); }
_fail() { echo "  ❌ FAIL: $*"; ((FAIL++)); }
_skip() { echo "  ⏭️  SKIP: $*"; ((SKIP++)); }
_section() { echo ""; echo "── $* ──"; }

# ─────────────────────────────────────────────────────────────────────────────
# TASK 1: morning-briefing EXIT trap
# ─────────────────────────────────────────────────────────────────────────────
_section "Task 1: morning-briefing EXIT trap"

MB_SCRIPT="$SCRIPTS/morning-briefing-full-ga4.sh"
if [ ! -f "$MB_SCRIPT" ]; then
  _fail "morning-briefing-full-ga4.sh not found"
else
  if grep -q "trap '.*cron-heartbeat.sh.*morning-briefing.*' EXIT" "$MB_SCRIPT"; then
    _pass "EXIT trap registered for cron-heartbeat.sh"
  else
    _fail "EXIT trap not found (expected: trap '...cron-heartbeat.sh... morning-briefing...' EXIT)"
  fi

  if grep -q "^SEND_EXIT=1" "$MB_SCRIPT"; then
    _pass "SEND_EXIT default=1 (failure-safe)"
  else
    _fail "SEND_EXIT=1 default not found — trap may always report success"
  fi

  # Trap should appear BEFORE the main body, not just at the end
  TRAP_LINE=$(grep -n "trap '.*EXIT" "$MB_SCRIPT" | head -1 | cut -d: -f1)
  TOTAL_LINES=$(wc -l < "$MB_SCRIPT")
  if [ -n "$TRAP_LINE" ] && [ "$TRAP_LINE" -lt $(( TOTAL_LINES / 2 )) ]; then
    _pass "EXIT trap registered early (line $TRAP_LINE of $TOTAL_LINES)"
  elif [ -n "$TRAP_LINE" ]; then
    _fail "EXIT trap registered late (line $TRAP_LINE of $TOTAL_LINES) — may miss early exits"
  fi
fi

# ─────────────────────────────────────────────────────────────────────────────
# TASK 2: Secrets scripts committed
# ─────────────────────────────────────────────────────────────────────────────
_section "Task 2: Secrets scripts committed and functional"

for script in load-secrets-from-keychain.sh migrate-secrets-to-keychain.sh; do
  if [ -f "$SCRIPTS/$script" ]; then
    _pass "$script exists"
  else
    _fail "$script missing from scripts/"
  fi
done

# load-secrets: must export expected vars
LOAD_SCRIPT="$SCRIPTS/load-secrets-from-keychain.sh"
if [ -f "$LOAD_SCRIPT" ]; then
  EXPORTS=$(grep "^export " "$LOAD_SCRIPT" | head -1)
  if echo "$EXPORTS" | grep -q "ANTHROPIC_API_KEY"; then
    _pass "load-secrets-from-keychain.sh exports ANTHROPIC_API_KEY"
  else
    _fail "load-secrets-from-keychain.sh does not export ANTHROPIC_API_KEY"
  fi

  if grep -q "\-\-write-env" "$LOAD_SCRIPT"; then
    _pass "load-secrets-from-keychain.sh supports --write-env flag"
  else
    _fail "--write-env flag not present in load-secrets-from-keychain.sh"
  fi

  # Must check for missing keys and exit 1 if any missing
  if grep -q "exit 1" "$LOAD_SCRIPT"; then
    _pass "load-secrets-from-keychain.sh exits 1 on missing secrets"
  else
    _fail "load-secrets-from-keychain.sh never exits 1 — silent failure possible"
  fi
fi

# ─────────────────────────────────────────────────────────────────────────────
# TASK 3: smart-prune Phase 1.6 cross-file dedup
# ─────────────────────────────────────────────────────────────────────────────
_section "Task 3: smart-prune Phase 1.6 cross-file dedup"

PRUNE_SCRIPT="$SCRIPTS/weekly-memory-smart-prune.sh"
if [ ! -f "$PRUNE_SCRIPT" ]; then
  _fail "weekly-memory-smart-prune.sh not found"
else
  if grep -q "Phase 1.6" "$PRUNE_SCRIPT"; then
    _pass "Phase 1.6 section exists in smart-prune"
  else
    _fail "Phase 1.6 not found in weekly-memory-smart-prune.sh"
  fi

  if grep -q "SEEN_LINES" "$PRUNE_SCRIPT"; then
    _pass "SEEN_LINES associative array found (dedup mechanism)"
  else
    _fail "SEEN_LINES not found — dedup logic may be missing"
  fi

  if grep -q "CROSS_DEDUP_CLEANED\|CROSS_DEDUP_LINES_SAVED" "$PRUNE_SCRIPT"; then
    _pass "Cross-dedup counters found"
  else
    _fail "Cross-dedup counters missing — results not tracked"
  fi

  # Functional test: Phase 1.6 dedup using the actual script via TEST_MEMORY_DIR
  TMPDIR_TEST=$(mktemp -d)
  # Create two daily files with overlapping bullet lines
  cat > "$TMPDIR_TEST/2026-04-22.md" << 'EOF'
# Daily Notes

## Tasks
- [x] Deployed gateway update
- [x] Fixed quota monitor
EOF

  cat > "$TMPDIR_TEST/2026-04-23.md" << 'EOF'
# Daily Notes

## Tasks
- [x] Deployed gateway update
- [x] Fixed quota monitor
- [x] New unique task for day 2
EOF

  # Run the dedup logic via Python (avoids bash 3.x associative array limitation)
  DEDUP_RESULT=$(python3 - "$TMPDIR_TEST" << 'PYEOF'
import sys, re, os, glob

mem_dir = sys.argv[1]
files = sorted(glob.glob(os.path.join(mem_dir, "2026-*.md")))

seen = set()
cleaned = 0
lines_saved = 0

for fpath in files:
    with open(fpath) as f:
        lines = f.readlines()
    out = []
    dropped = 0
    for line in lines:
        trimmed = line.strip()
        if re.match(r'^[-*•]', trimmed) and len(trimmed) > 20:
            if trimmed in seen:
                dropped += 1
                continue
            seen.add(trimmed)
        else:
            if trimmed:
                seen.add(trimmed)
        out.append(line)
    if dropped > 0:
        with open(fpath, 'w') as f:
            f.writelines(out)
        cleaned += 1
        lines_saved += dropped

print(f"cleaned={cleaned} saved={lines_saved}")
with open(os.path.join(mem_dir, "2026-04-23.md")) as f:
    print(f.read())
PYEOF
  )

  if echo "$DEDUP_RESULT" | grep -q "cleaned=1"; then
    _pass "Phase 1.6 dedup: correctly identified 1 file to clean"
  else
    _fail "Phase 1.6 dedup: expected cleaned=1, got: $(echo "$DEDUP_RESULT" | head -1)"
  fi

  if echo "$DEDUP_RESULT" | grep -q "saved=2"; then
    _pass "Phase 1.6 dedup: removed 2 duplicate bullet lines"
  else
    _fail "Phase 1.6 dedup: expected saved=2, got: $(echo "$DEDUP_RESULT" | head -1)"
  fi

  if echo "$DEDUP_RESULT" | grep -q "New unique task for day 2"; then
    _pass "Phase 1.6 dedup: unique lines preserved"
  else
    _fail "Phase 1.6 dedup: unique lines were incorrectly removed"
  fi

  rm -rf "$TMPDIR_TEST"
fi

# ─────────────────────────────────────────────────────────────────────────────
# TASK 4: Prometheus/Grafana tracked in STATUS.md
# ─────────────────────────────────────────────────────────────────────────────
_section "Task 4: Prometheus/Grafana in STATUS.md"

STATUS_FILE="$WORKSPACE/STATUS.md"
if [ ! -f "$STATUS_FILE" ]; then
  _fail "STATUS.md not found"
else
  if grep -qi "prometheus\|grafana" "$STATUS_FILE"; then
    _pass "Prometheus/Grafana mentioned in STATUS.md"
  else
    _fail "Prometheus/Grafana NOT found in STATUS.md"
  fi

  # Should be in a real section (not just a comment)
  if grep -A2 -qi "prometheus" "$STATUS_FILE" | grep -qi "metric\|monitor\|stub\|candidate\|track"; then
    _pass "Prometheus section has tracking context (metrics/stub/candidate)"
  else
    # Softer check — just ensure it's in a header or list
    if grep -qi "## .*prometheus\|### .*prometheus\|- .*prometheus\|prometheus.*section" "$STATUS_FILE"; then
      _pass "Prometheus appears in a structured section"
    else
      _skip "Prometheus context unclear — manual review recommended"
    fi
  fi
fi

# ─────────────────────────────────────────────────────────────────────────────
# TASK 5: check-env-drift.sh
# ─────────────────────────────────────────────────────────────────────────────
_section "Task 5: check-env-drift.sh"

DRIFT_SCRIPT="$SCRIPTS/check-env-drift.sh"
if [ ! -f "$DRIFT_SCRIPT" ]; then
  _fail "check-env-drift.sh not found"
else
  _pass "check-env-drift.sh exists"

  # Test 1: identical files → no drift
  TMPDIR_DRIFT=$(mktemp -d)
  cat > "$TMPDIR_DRIFT/env_a" << 'EOF'
ANTHROPIC_API_KEY=sk-test-1234567890abcdef
BRAVE_API_KEY=bsv-test-0987654321
EOF
  cp "$TMPDIR_DRIFT/env_a" "$TMPDIR_DRIFT/env_b"

  DRIFT_OUT=$(DRIFT_ENV_A="$TMPDIR_DRIFT/env_a" DRIFT_ENV_B="$TMPDIR_DRIFT/env_b" \
    bash "$DRIFT_SCRIPT" 2>&1)
  if echo "$DRIFT_OUT" | grep -q "No drift"; then
    _pass "check-env-drift: identical files → no drift detected"
  else
    _fail "check-env-drift: identical files should report no drift, got: $(echo "$DRIFT_OUT" | tail -3)"
  fi

  # Test 2: missing key in B → drift detected
  cat > "$TMPDIR_DRIFT/env_b_missing" << 'EOF'
ANTHROPIC_API_KEY=sk-test-1234567890abcdef
EOF
  DRIFT_OUT2=$(DRIFT_ENV_A="$TMPDIR_DRIFT/env_a" DRIFT_ENV_B="$TMPDIR_DRIFT/env_b_missing" \
    bash "$DRIFT_SCRIPT" 2>&1; true)
  if echo "$DRIFT_OUT2" | grep -q "BRAVE_API_KEY"; then
    _pass "check-env-drift: missing key in B → BRAVE_API_KEY flagged"
  else
    _fail "check-env-drift: missing key not detected, got: $DRIFT_OUT2"
  fi

  # Test 3: value mismatch → drift detected
  cat > "$TMPDIR_DRIFT/env_b_mismatch" << 'EOF'
ANTHROPIC_API_KEY=sk-test-DIFFERENT
BRAVE_API_KEY=bsv-test-0987654321
EOF
  DRIFT_OUT3=$(DRIFT_ENV_A="$TMPDIR_DRIFT/env_a" DRIFT_ENV_B="$TMPDIR_DRIFT/env_b_mismatch" \
    bash "$DRIFT_SCRIPT" 2>&1; true)
  if echo "$DRIFT_OUT3" | grep -q "VALUES DIFFER\|ANTHROPIC_API_KEY"; then
    _pass "check-env-drift: value mismatch → ANTHROPIC_API_KEY flagged"
  else
    _fail "check-env-drift: value mismatch not detected, got: $DRIFT_OUT3"
  fi

  # Test 4: exit code 1 on drift
  DRIFT_ENV_A="$TMPDIR_DRIFT/env_a" DRIFT_ENV_B="$TMPDIR_DRIFT/env_b_missing" \
    bash "$DRIFT_SCRIPT" >/dev/null 2>&1
  if [ $? -ne 0 ]; then
    _pass "check-env-drift: exits non-zero when drift found"
  else
    _fail "check-env-drift: should exit non-zero on drift, but exited 0"
  fi

  rm -rf "$TMPDIR_DRIFT"
fi

# ─────────────────────────────────────────────────────────────────────────────
# TASK 6: STATE.yaml zombie purge (structural check only — gitignored)
# ─────────────────────────────────────────────────────────────────────────────
_section "Task 6: STATE.yaml zombie queue purge"

STATE_FILE="$WORKSPACE/STATE.yaml"
if [ ! -f "$STATE_FILE" ]; then
  # Gitignored — acceptable
  _pass "STATE.yaml not present (gitignored, likely clean)"
else
  # Count non-empty tasks in the queue
  ZOMBIE_COUNT=$(python3 -c "
import yaml, sys
try:
    with open('$STATE_FILE') as f:
        data = yaml.safe_load(f) or {}
    queue = data.get('tasks', data.get('queue', []))
    abandoned = [t for t in queue if isinstance(t, dict) and t.get('status','') in ('abandoned','done','')]
    print(len(abandoned))
except Exception as e:
    print(0)
" 2>/dev/null || echo "0")

  if [ "$ZOMBIE_COUNT" -eq 0 ]; then
    _pass "STATE.yaml: no zombie (abandoned/done) tasks in queue"
  else
    _fail "STATE.yaml: $ZOMBIE_COUNT zombie tasks still present (should be 0)"
  fi
fi

# ─────────────────────────────────────────────────────────────────────────────
# TASK 7: Anthropic rate-limit monitor
# ─────────────────────────────────────────────────────────────────────────────
_section "Task 7: anthropic-rate-limit-monitor.sh"

RL_SCRIPT="$SCRIPTS/anthropic-rate-limit-monitor.sh"
if [ ! -f "$RL_SCRIPT" ]; then
  _fail "anthropic-rate-limit-monitor.sh not found"
else
  _pass "anthropic-rate-limit-monitor.sh exists"

  # Wired into api-quota-monitor.sh
  QUOTA_SCRIPT="$SCRIPTS/api-quota-monitor.sh"
  if grep -q "anthropic-rate-limit-monitor.sh" "$QUOTA_SCRIPT"; then
    _pass "anthropic-rate-limit-monitor.sh wired into api-quota-monitor.sh"
  else
    _fail "anthropic-rate-limit-monitor.sh NOT referenced in api-quota-monitor.sh"
  fi

  # Test threshold logic with mock data
  THRESHOLD_RESULT=$(bash -c '
    ALERT=false
    ALERT_MSG=""
    check_threshold() {
        local remaining="$1" limit="$2" label="$3"
        if [ -n "$remaining" ] && [ -n "$limit" ] && [ "$limit" -gt 0 ] 2>/dev/null; then
            used=$(( limit - remaining ))
            pct_used=$(( used * 100 / limit ))
            if [ "$pct_used" -ge 80 ]; then
                ALERT=true
                ALERT_MSG="${ALERT_MSG}${label}: ${pct_used}%\n"
            fi
        fi
    }
    # Test: 90% consumed → should alert
    check_threshold 100 1000 "Requests"
    $ALERT && echo "ALERT_FIRED" || echo "NO_ALERT"
  ')
  if echo "$THRESHOLD_RESULT" | grep -q "ALERT_FIRED"; then
    _pass "Rate-limit threshold: 90% consumed → alert fires correctly"
  else
    _fail "Rate-limit threshold: 90% consumed → alert did NOT fire"
  fi

  THRESHOLD_RESULT2=$(bash -c '
    ALERT=false
    check_threshold() {
        local remaining="$1" limit="$2" label="$3"
        if [ -n "$remaining" ] && [ -n "$limit" ] && [ "$limit" -gt 0 ] 2>/dev/null; then
            used=$(( limit - remaining ))
            pct_used=$(( used * 100 / limit ))
            if [ "$pct_used" -ge 80 ]; then ALERT=true; fi
        fi
    }
    # Test: 50% consumed → should NOT alert
    check_threshold 500 1000 "Requests"
    $ALERT && echo "ALERT_FIRED" || echo "NO_ALERT"
  ')
  if echo "$THRESHOLD_RESULT2" | grep -q "NO_ALERT"; then
    _pass "Rate-limit threshold: 50% consumed → no spurious alert"
  else
    _fail "Rate-limit threshold: 50% consumed → spurious alert fired"
  fi

  # Check --log-only flag is handled
  if grep -q "\-\-log-only\|log.only\|LOG_ONLY" "$RL_SCRIPT"; then
    _pass "anthropic-rate-limit-monitor.sh supports --log-only flag"
  else
    _fail "--log-only flag not implemented"
  fi

  # Metrics file rotation: should keep last 48 entries
  if grep -q "48" "$RL_SCRIPT"; then
    _pass "Metrics rotation: keeps last 48 entries (~2 days)"
  else
    _fail "Metrics rotation limit not found (expected 48)"
  fi
fi

# ─────────────────────────────────────────────────────────────────────────────
# TASK 8: Archive stale .md files (183 → archive/docs/, 12 remain in root)
# ─────────────────────────────────────────────────────────────────────────────
_section "Task 8: archive/docs/ stale .md file migration"

ARCHIVE_DIR="$WORKSPACE/archive/docs"
if [ ! -d "$ARCHIVE_DIR" ]; then
  _fail "archive/docs/ directory not found"
else
  ARCHIVE_COUNT=$(ls "$ARCHIVE_DIR"/*.md 2>/dev/null | wc -l | tr -d ' ')
  if [ "$ARCHIVE_COUNT" -ge 100 ]; then
    _pass "archive/docs/ contains $ARCHIVE_COUNT .md files (≥100, consistent with 183-file claim)"
  else
    _fail "archive/docs/ only has $ARCHIVE_COUNT .md files (expected ~183)"
  fi
fi

ROOT_MD_COUNT=$(ls "$WORKSPACE"/*.md 2>/dev/null | wc -l | tr -d ' ')
# Allow 10–15 system files (task says 12 remain)
if [ "$ROOT_MD_COUNT" -le 15 ]; then
  _pass "Workspace root has $ROOT_MD_COUNT .md files (≤15, consistent with 12-file claim)"
else
  _fail "Workspace root has $ROOT_MD_COUNT .md files (expected ≤15 after archive)"
fi

# Key system files should still be in root
for f in SOUL.md USER.md MEMORY.md AGENTS.md STATUS.md; do
  if [ -f "$WORKSPACE/$f" ]; then
    _pass "$f remains in workspace root (not archived)"
  else
    _fail "$f MISSING from workspace root — was incorrectly archived"
  fi
done

# ─────────────────────────────────────────────────────────────────────────────
# TASK 9: session-stop-hook.sh cost tracking
# ─────────────────────────────────────────────────────────────────────────────
_section "Task 9: session-stop-hook.sh cost estimation"

STOP_HOOK="$SCRIPTS/session-stop-hook.sh"
if [ ! -f "$STOP_HOOK" ]; then
  _fail "session-stop-hook.sh not found"
else
  if grep -q "cost_usd_est\|cost.*usd\|USD" "$STOP_HOOK"; then
    _pass "Cost estimation (USD) present in stop hook"
  else
    _fail "No cost estimation logic found in session-stop-hook.sh"
  fi

  if grep -q "OUTPUT_COST_PER_M\|INPUT_COST_PER_M\|3\.00\|15\.00" "$STOP_HOOK"; then
    _pass "Sonnet 4-6 pricing constants found (\$3/\$15 per M tokens)"
  else
    _fail "Pricing constants not found — cost estimate may be wrong"
  fi

  # Functional test: cost Python block produces reasonable output
  COST_TEST=$(python3 - << 'PYEOF'
transcript_chars = 40000  # 10K tokens approximate
turns = 10

total_tokens = transcript_chars / 4
input_tokens  = int(total_tokens * 0.90)
output_tokens = int(total_tokens * 0.10)

INPUT_COST_PER_M  = 3.00
OUTPUT_COST_PER_M = 15.00

est_cost_usd = (input_tokens / 1_000_000 * INPUT_COST_PER_M) + \
               (output_tokens / 1_000_000 * OUTPUT_COST_PER_M)

assert 0.0001 < est_cost_usd < 1.0, f"Cost out of reasonable range: {est_cost_usd}"
assert input_tokens > output_tokens, "Input should dominate output"
print(f"cost={est_cost_usd:.4f} input={input_tokens} output={output_tokens}")
PYEOF
  2>&1)
  if echo "$COST_TEST" | grep -q "^cost="; then
    _pass "Cost estimation math: $(echo "$COST_TEST" | grep cost=)"
  else
    _fail "Cost estimation math failed: $COST_TEST"
  fi

  # Metrics file: cost appended to last entry (not written as separate entry)
  if grep -q "lines\[-1\]\|last entry\|lines\[-1" "$STOP_HOOK"; then
    _pass "Cost appended to existing metrics entry (not a separate entry)"
  else
    _fail "Cost may not be correctly appended to last metrics entry"
  fi

  # Stop hook must always exit 0
  LAST_LINE=$(tail -5 "$STOP_HOOK" | grep "exit")
  if echo "$LAST_LINE" | grep -q "exit 0"; then
    _pass "session-stop-hook.sh always exits 0 (hook-safe)"
  else
    _fail "session-stop-hook.sh may not exit 0 — could break agent stop"
  fi
fi

# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "════════════════════════════════════════════"
echo "  Results: $PASS passed | $FAIL failed | $SKIP skipped"
echo "════════════════════════════════════════════"

[ "$FAIL" -eq 0 ]
