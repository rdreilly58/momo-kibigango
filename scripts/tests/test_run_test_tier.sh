#!/bin/bash
# test_run_test_tier.sh — Validate the tier-aware test runner.
# Tier: 1
#
# Spins up a tmpdir of fixture tests, points the runner at it via env
# overrides, and asserts tier filtering + exit codes.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNNER="$SCRIPT_DIR/../run-test-tier.sh"

[ -x "$RUNNER" ] || { echo "FAIL  runner not executable at $RUNNER"; exit 1; }

FAILED=0
ok()   { echo "  PASS  $*"; }
fail() { echo "  FAIL  $*"; FAILED=1; }

# ── Fixture: temp tests dir with one file per tier + one untagged ────────────
FIXTURE=$(mktemp -d /tmp/runner-test.XXXXXX)
trap 'rm -rf "$FIXTURE"' EXIT
mkdir -p "$FIXTURE/scripts/tests"

cat > "$FIXTURE/scripts/tests/test_t1_pass.sh" <<'EOF'
#!/bin/bash
# Tier: 1
exit 0
EOF
cat > "$FIXTURE/scripts/tests/test_t1_fail.sh" <<'EOF'
#!/bin/bash
# Tier: 1
exit 1
EOF
cat > "$FIXTURE/scripts/tests/test_t2_pass.sh" <<'EOF'
#!/bin/bash
# Tier: 2
exit 0
EOF
cat > "$FIXTURE/scripts/tests/test_t3_pass.sh" <<'EOF'
#!/bin/bash
# Tier: 3
exit 0
EOF
cat > "$FIXTURE/scripts/tests/test_untagged_pass.sh" <<'EOF'
#!/bin/bash
exit 0
EOF
chmod +x "$FIXTURE/scripts/tests/"*.sh

# Symlink the runner inside the fixture so its WORKSPACE resolves correctly.
mkdir -p "$FIXTURE/scripts"
cp "$RUNNER" "$FIXTURE/scripts/run-test-tier.sh"

# Override HOME so the runner's heartbeat/log files don't pollute real ones.
TMP_HOME=$(mktemp -d /tmp/runner-home.XXXXXX)
trap 'rm -rf "$FIXTURE" "$TMP_HOME"' EXIT
mkdir -p "$TMP_HOME/.openclaw/logs"

# ── Test 1: tier 1 picks 2 files (1 pass + 1 fail) and exits 1 ──────────────
echo "1. tier=1 selects 2 files, fails because one is failing"
out=$(HOME="$TMP_HOME" bash "$FIXTURE/scripts/run-test-tier.sh" 1 --json 2>/dev/null)
total=$(echo "$out" | python3 -c "import json,sys;print(json.load(sys.stdin)['total'])")
failed=$(echo "$out" | python3 -c "import json,sys;print(json.load(sys.stdin)['failed'])")
[ "$total" = "3" ] && ok "tier=1 total=3 (2 explicit + 1 untagged-default)" || fail "tier=1 total expected 3, got $total"
[ "$failed" = "1" ] && ok "tier=1 failed=1" || fail "tier=1 failed expected 1, got $failed"

# ── Test 2: tier 2 picks 1 file, exits 0 ────────────────────────────────────
echo "2. tier=2 picks 1 file, all pass"
out=$(HOME="$TMP_HOME" bash "$FIXTURE/scripts/run-test-tier.sh" 2 --json 2>/dev/null)
total=$(echo "$out" | python3 -c "import json,sys;print(json.load(sys.stdin)['total'])")
[ "$total" = "1" ] && ok "tier=2 total=1" || fail "tier=2 total expected 1, got $total"

# ── Test 3: tier 3 picks 1 file ─────────────────────────────────────────────
echo "3. tier=3 picks 1 file"
out=$(HOME="$TMP_HOME" bash "$FIXTURE/scripts/run-test-tier.sh" 3 --json 2>/dev/null)
total=$(echo "$out" | python3 -c "import json,sys;print(json.load(sys.stdin)['total'])")
[ "$total" = "1" ] && ok "tier=3 total=1" || fail "tier=3 total expected 1, got $total"

# ── Test 4: 'all' picks all 5 ───────────────────────────────────────────────
echo "4. tier=all picks all 5 files"
out=$(HOME="$TMP_HOME" bash "$FIXTURE/scripts/run-test-tier.sh" all --json 2>/dev/null)
total=$(echo "$out" | python3 -c "import json,sys;print(json.load(sys.stdin)['total'])")
[ "$total" = "5" ] && ok "tier=all total=5" || fail "tier=all total expected 5, got $total"

# ── Test 5: invalid tier exits 2 ────────────────────────────────────────────
echo "5. invalid tier exits 2"
HOME="$TMP_HOME" bash "$FIXTURE/scripts/run-test-tier.sh" 7 --quiet 2>/dev/null
rc=$?
[ "$rc" = "2" ] && ok "invalid tier exits 2" || fail "invalid tier expected 2, got $rc"

# ── Test 6: untagged file defaults to tier 1 ────────────────────────────────
echo "6. untagged file is included in tier=1"
out=$(HOME="$TMP_HOME" bash "$FIXTURE/scripts/run-test-tier.sh" 1 --json 2>/dev/null)
files=$(echo "$out" | python3 -c "import json,sys;print(','.join(r['file'] for r in json.load(sys.stdin)['results']))")
echo "$files" | grep -q "test_untagged_pass.sh" && ok "untagged included in tier=1" || fail "untagged missing: $files"

echo ""
if [ $FAILED -eq 0 ]; then
  echo "All run-test-tier tests passed."
  exit 0
else
  echo "Some tests FAILED."
  exit 1
fi
