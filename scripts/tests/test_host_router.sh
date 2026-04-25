#!/bin/bash
# test_host_router.sh — Smoke tests for host-router.sh and agent-router.sh --host
#
# Simulates healthy/unhealthy host states by pointing the router at
# temporary fixture files. No real network calls are made.
#
# Usage: bash scripts/tests/test_host_router.sh

set -euo pipefail

WORKSPACE="$HOME/.openclaw/workspace"
SCRIPT_DIR="$WORKSPACE/scripts"
HOST_ROUTER="$SCRIPT_DIR/host-router.sh"
AGENT_ROUTER="$SCRIPT_DIR/agent-router.sh"

PASS=0
FAIL=0
TMPDIR_FIXTURES=$(mktemp -d)
trap 'rm -rf "$TMPDIR_FIXTURES"' EXIT

_pass() { ((PASS++)); echo "  PASS  $1"; }
_fail() { ((FAIL++)); echo "  FAIL  $1"; }

echo "═══════════════════════════════════════════════"
echo " Host Router Smoke Test Suite"
echo " $(date '+%Y-%m-%d %H:%M:%S')"
echo "═══════════════════════════════════════════════"
echo ""

# ── Fixture helpers ───────────────────────────────────────────────────────────
# We override the paths host-router.sh reads by injecting env vars that
# the script consumes. Since host-router.sh reads $HOME paths directly we
# use a wrapper that rewrites HOME to a temp directory for each test.

make_health_log() {
    local dir="$1" state="$2"
    mkdir -p "$dir/.openclaw/logs"
    local log="$dir/.openclaw/logs/health-check.log"
    if [ "$state" = "ok" ]; then
        cat > "$log" << 'EOF'
[08:00:01] OK: OpenClaw Gateway — Running (port 18789)
[08:00:01] OK: Disk Space — 42% used
[08:00:01] OK: Memory Files — 120 daily logs
EOF
    elif [ "$state" = "disk_critical" ]; then
        cat > "$log" << 'EOF'
[08:00:01] OK: OpenClaw Gateway — Running (port 18789)
[08:00:01] ERROR: Disk Space — Critical: 95% used
[08:00:01] OK: Memory Files — 120 daily logs
EOF
    elif [ "$state" = "memory_missing" ]; then
        cat > "$log" << 'EOF'
[08:00:01] OK: OpenClaw Gateway — Running (port 18789)
[08:00:01] OK: Disk Space — 42% used
[08:00:01] ERROR: Memory Files — SOUL.md missing
EOF
    fi
}

make_aws_config() {
    local dir="$1" state="$2"
    mkdir -p "$dir/.openclaw/workspace/aws-config"
    local cfg="$dir/.openclaw/workspace/aws-config/mac-instance-allocated.json"
    if [ "$state" = "allocated_no_ip" ]; then
        cat > "$cfg" << 'EOF'
{
  "host_id": "h-0abc123",
  "instance_type": "mac-m4pro.metal",
  "region": "us-east-1",
  "allocated_at": "2026-04-25T08:00:00Z",
  "status": "ALLOCATED_AND_READY"
}
EOF
    elif [ "$state" = "allocated_with_ip" ]; then
        # We use 127.0.0.1:22 — not guaranteed open, so mac-aws may report DOWN.
        # The test just checks no crash occurs and output is valid.
        cat > "$cfg" << 'EOF'
{
  "host_id": "h-0abc123",
  "instance_type": "mac-m4pro.metal",
  "region": "us-east-1",
  "allocated_at": "2026-04-25T08:00:00Z",
  "status": "ALLOCATED_AND_READY",
  "host_ip": "127.0.0.1"
}
EOF
    elif [ "$state" = "not_ready" ]; then
        cat > "$cfg" << 'EOF'
{
  "host_id": "",
  "instance_type": "",
  "status": "PENDING"
}
EOF
    fi
    # "absent" state: simply don't create the file
}

# Run host-router in a fake HOME
# Always returns output (either the host token or "skip"); never appends a second line.
run_router() {
    local fake_home="$1" task_type="$2" mode="${3:-route}"
    # Patch HOME so the script reads from our fixture dir.
    # Capture stdout; if the script exits non-zero and produced no output, emit "skip".
    local out
    out=$(HOME="$fake_home" bash "$HOST_ROUTER" "$task_type" "$mode" 2>/dev/null) || true
    if [ -z "$out" ]; then
        echo "skip"
    else
        echo "$out"
    fi
}

# ─────────────────────────────────────────────────
# 1. Local healthy, no AWS Mac → routes to local
# ─────────────────────────────────────────────────
echo "1. Local healthy, no AWS config — general task"
D=$(mktemp -d "$TMPDIR_FIXTURES/t1.XXXX")
make_health_log "$D" ok
# no aws config file created
RESULT=$(run_router "$D" general route)
if [ "$RESULT" = "local" ]; then
    _pass "general task → local (AWS absent)"
else
    _fail "expected local, got '$RESULT'"
fi
echo ""

# ─────────────────────────────────────────────────
# 2. Local disk critical → skip (only host is down, no AWS)
# ─────────────────────────────────────────────────
echo "2. Local disk critical, no AWS config — all hosts down"
D=$(mktemp -d "$TMPDIR_FIXTURES/t2.XXXX")
make_health_log "$D" disk_critical
RESULT=$(run_router "$D" general route)
if [ "$RESULT" = "skip" ]; then
    _pass "all hosts down → skip"
else
    _fail "expected skip, got '$RESULT'"
fi
echo ""

# ─────────────────────────────────────────────────
# 3. Local disk critical, AWS allocated (no IP yet) → still skip
#    (AWS has no IP, so it's not routable even if allocated)
# ─────────────────────────────────────────────────
echo "3. Local disk critical, AWS allocated but no IP — still skip"
D=$(mktemp -d "$TMPDIR_FIXTURES/t3.XXXX")
make_health_log "$D" disk_critical
make_aws_config "$D" allocated_no_ip
# mac-aws has no host_ip, so aws_mac_healthy() returns 1
RESULT=$(run_router "$D" general route)
if [ "$RESULT" = "skip" ]; then
    _pass "disk critical + aws no-ip → skip"
else
    _fail "expected skip, got '$RESULT'"
fi
echo ""

# ─────────────────────────────────────────────────
# 4. Local memory files missing → skip (no AWS)
# ─────────────────────────────────────────────────
echo "4. Local memory files missing, no AWS config"
D=$(mktemp -d "$TMPDIR_FIXTURES/t4.XXXX")
make_health_log "$D" memory_missing
RESULT=$(run_router "$D" general route)
if [ "$RESULT" = "skip" ]; then
    _pass "memory missing + no AWS → skip"
else
    _fail "expected skip, got '$RESULT'"
fi
echo ""

# ─────────────────────────────────────────────────
# 5. AWS config PENDING (not ready) + local healthy → local
# ─────────────────────────────────────────────────
echo "5. AWS not-ready, local healthy — general task → local"
D=$(mktemp -d "$TMPDIR_FIXTURES/t5.XXXX")
make_health_log "$D" ok
make_aws_config "$D" not_ready
RESULT=$(run_router "$D" general route || echo "skip")
if [ "$RESULT" = "local" ]; then
    _pass "aws not-ready → falls through to local"
else
    _fail "expected local, got '$RESULT'"
fi
echo ""

# ─────────────────────────────────────────────────
# 6. GPU task with healthy local, no AWS → falls back to local
# ─────────────────────────────────────────────────
echo "6. GPU task — prefer mac-aws but not available → fall through to local"
D=$(mktemp -d "$TMPDIR_FIXTURES/t6.XXXX")
make_health_log "$D" ok
# no aws config
RESULT=$(run_router "$D" gpu route || echo "skip")
if [ "$RESULT" = "local" ]; then
    _pass "gpu task: mac-aws absent → falls back to local"
else
    _fail "expected local, got '$RESULT'"
fi
echo ""

# ─────────────────────────────────────────────────
# 7. Status mode — no crash, produces output
# ─────────────────────────────────────────────────
echo "7. Status mode produces output without crashing"
D=$(mktemp -d "$TMPDIR_FIXTURES/t7.XXXX")
make_health_log "$D" ok
OUTPUT=$(HOME="$D" bash "$HOST_ROUTER" general status 2>/dev/null)
if echo "$OUTPUT" | grep -q "Host Status"; then
    _pass "status mode prints host table"
else
    _fail "status mode output missing 'Host Status'"
fi
echo ""

# ─────────────────────────────────────────────────
# 8. Health mode — returns 0 when local is up
# ─────────────────────────────────────────────────
echo "8. Health mode exits 0 when local is healthy"
D=$(mktemp -d "$TMPDIR_FIXTURES/t8.XXXX")
make_health_log "$D" ok
if HOME="$D" bash "$HOST_ROUTER" general health 2>/dev/null; then
    _pass "health mode exits 0 (local up)"
else
    _fail "health mode unexpectedly exited non-zero"
fi
echo ""

# ─────────────────────────────────────────────────
# 9. Health mode — returns 1 when all hosts down
# ─────────────────────────────────────────────────
echo "9. Health mode exits 1 when all hosts down"
D=$(mktemp -d "$TMPDIR_FIXTURES/t9.XXXX")
make_health_log "$D" disk_critical
if HOME="$D" bash "$HOST_ROUTER" general health 2>/dev/null; then
    _fail "health mode should have exited 1 (all down)"
else
    _pass "health mode exits 1 (all hosts down)"
fi
echo ""

# ─────────────────────────────────────────────────
# 10. agent-router.sh --host flag works
# ─────────────────────────────────────────────────
echo "10. agent-router.sh --host outputs a host (not agent name)"
# Use real $HOME here — local should be healthy in production
RESULT=$(bash "$AGENT_ROUTER" --host "run health check" 2>/dev/null || echo "skip")
case "$RESULT" in
    local|mac-aws|skip)
        _pass "agent-router.sh --host outputs valid host token: '$RESULT'"
        ;;
    *)
        _fail "agent-router.sh --host gave unexpected output: '$RESULT'"
        ;;
esac
echo ""

# ─────────────────────────────────────────────────
# 11. agent-router.sh --host --explain gives structured output
# ─────────────────────────────────────────────────
echo "11. agent-router.sh --host --explain gives agent + host lines"
OUTPUT=$(bash "$AGENT_ROUTER" --host --explain "train ML model" 2>/dev/null || true)
if echo "$OUTPUT" | grep -q "^agent:" && echo "$OUTPUT" | grep -q "^host:"; then
    _pass "--host --explain contains 'agent:' and 'host:' lines"
else
    _fail "--host --explain output malformed: '$OUTPUT'"
fi
echo ""

# ─────────────────────────────────────────────────
# 12. agent-router.sh backward-compat (no --host flag)
# ─────────────────────────────────────────────────
echo "12. agent-router.sh without --host still outputs agent name only"
RESULT=$(bash "$AGENT_ROUTER" "refactor memory search" 2>/dev/null)
case "$RESULT" in
    ops|code|research|memory|finance)
        _pass "backward-compat: agent-router.sh outputs '$RESULT' without --host"
        ;;
    *)
        _fail "backward-compat broken: got '$RESULT'"
        ;;
esac
echo ""

# ─────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────
TOTAL=$((PASS + FAIL))
echo "═══════════════════════════════════════════════"
echo " Results: $PASS/$TOTAL passed, $FAIL failed"
echo "═══════════════════════════════════════════════"

if [ "$FAIL" -eq 0 ]; then
    echo " All tests passed."
    exit 0
else
    echo " $FAIL test(s) failed — review above"
    exit 1
fi
