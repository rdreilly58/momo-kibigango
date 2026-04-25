#!/bin/bash
# run-test-tier.sh — Tier-aware test runner.
#
# OpenClaw classifies its shell tests into three tiers based on cost and
# blast-radius:
#
#   Tier 1 — fast, hermetic, no network. Sub-second. Runs on every
#            PostToolUse Write|Edit hook (test-runner-hook.sh) and
#            blocks nothing. Default tier when annotation missing.
#   Tier 2 — medium. Touches the local filesystem or starts subprocesses.
#            Up to ~30s. Runs on demand and on pre-commit.
#   Tier 3 — slow / integration. Hits real services (Telegram, Grafana,
#            ntfy, AWS), or seeds large fixtures. May exceed 30s.
#            Runs nightly via cron, never on a hook.
#
# Tier is declared by a single comment line near the top of the test file:
#
#     # Tier: 1
#
# Files without this annotation are treated as Tier 1.
#
# Usage:
#   run-test-tier.sh                       # tier 1 (default — fast suite)
#   run-test-tier.sh 1                     # explicit tier 1
#   run-test-tier.sh 2                     # tier 2 only
#   run-test-tier.sh 3                     # tier 3 only (nightly)
#   run-test-tier.sh all                   # all tiers
#   run-test-tier.sh 1 --quiet             # suppress per-test output
#   run-test-tier.sh 1 --json              # machine-readable summary
#
# Exit code: 0 if all selected tests pass, 1 if any fails or no tests match.

set -uo pipefail

set -a; source "$HOME/.openclaw/.env" 2>/dev/null || true; set +a
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$(cd "$SCRIPT_DIR/.." && pwd)"
TESTS_DIR="$WORKSPACE/scripts/tests"
LOG_FILE="$HOME/.openclaw/logs/test-tier.log"
HB_DIR="$HOME/.openclaw/logs/cron-heartbeats"

mkdir -p "$HB_DIR" "$(dirname "$LOG_FILE")"

TIER="${1:-1}"
QUIET=0
JSON=0
shift 2>/dev/null || true
while [[ $# -gt 0 ]]; do
  case $1 in
    --quiet) QUIET=1 ;;
    --json)  JSON=1; QUIET=1 ;;
  esac
  shift
done

case "$TIER" in
  1|2|3|all) ;;
  *) echo "Usage: $0 [1|2|3|all] [--quiet] [--json]" >&2; exit 2 ;;
esac

_log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"; }
_say() { [ $QUIET -eq 0 ] && echo "$*" || true; }

# Extract tier annotation from a file. Defaults to 1 when missing.
file_tier() {
  local f="$1"
  local t
  t=$(head -20 "$f" 2>/dev/null | grep -m1 -E '^# Tier:[[:space:]]*[123]' \
        | sed -E 's/^# Tier:[[:space:]]*([123]).*/\1/')
  echo "${t:-1}"
}

# Discover tests
selected=()
for f in "$TESTS_DIR"/test_*.sh; do
  [ -f "$f" ] || continue
  ft=$(file_tier "$f")
  if [ "$TIER" = "all" ] || [ "$TIER" = "$ft" ]; then
    selected+=("$f")
  fi
done

if [ ${#selected[@]} -eq 0 ]; then
  _say "No tests matched tier=$TIER under $TESTS_DIR"
  _log "no-tests tier=$TIER"
  [ $JSON -eq 1 ] && echo '{"tier":"'$TIER'","total":0,"passed":0,"failed":0,"results":[]}'
  exit 1
fi

_say "Running tier=$TIER (${#selected[@]} test files) under $TESTS_DIR"
_say "─────────────────────────────────────────────"

passed=0
failed=0
failed_files=()
results_json="["

for f in "${selected[@]}"; do
  name=$(basename "$f")
  t0=$(python3 -c "import time;print(time.time())")
  bash "$f" > /tmp/test-tier-out.$$ 2>&1
  rc=$?
  t1=$(python3 -c "import time;print(time.time())")
  dur=$(awk "BEGIN { printf \"%.2f\", $t1 - $t0 }")

  status="PASS"
  if [ $rc -ne 0 ]; then
    status="FAIL"
    failed=$((failed + 1))
    failed_files+=("$name")
  else
    passed=$((passed + 1))
  fi

  _say "  $status  ($dur s)  $name"
  if [ "$status" = "FAIL" ] && [ $QUIET -eq 0 ]; then
    sed 's/^/    /' /tmp/test-tier-out.$$ | tail -10
  fi

  # JSON accumulator (ASCII-escape for safety; names are filenames so no quotes)
  [ "$results_json" != "[" ] && results_json+=", "
  results_json+="{\"file\":\"$name\",\"tier\":\"$(file_tier "$f")\",\"status\":\"$status\",\"duration_sec\":$dur,\"exit_code\":$rc}"
done
rm -f /tmp/test-tier-out.$$

results_json+="]"

_say "─────────────────────────────────────────────"
_say "tier=$TIER  passed=$passed  failed=$failed  total=${#selected[@]}"

_log "tier=$TIER passed=$passed failed=$failed total=${#selected[@]}"
[ $failed -gt 0 ] && _log "failed: ${failed_files[*]}"

# Heartbeat
python3 -c "
import json, time, datetime as dt
json.dump({
    'last_run': dt.datetime.utcnow().isoformat() + 'Z',
    'last_run_ts': int(time.time()),
    'exit_code': $failed,
    'tier': '$TIER',
    'passed': $passed,
    'failed': $failed,
}, open('$HB_DIR/test-tier-${TIER}.json', 'w'))
" 2>/dev/null || true

if [ $JSON -eq 1 ]; then
  echo "{\"tier\":\"$TIER\",\"total\":${#selected[@]},\"passed\":$passed,\"failed\":$failed,\"results\":$results_json}"
fi

[ $failed -gt 0 ] && exit 1
exit 0
