#!/bin/bash
# host-router.sh — Resolve which host should run a given task
#
# Inputs:
#   $1 — task type: "gpu" | "ios" | "ml" | "ops" | "code" | "general" (default: general)
#   $2 — mode: "route" (default) | "status" | "health"
#
# Output (route mode):
#   Prints one of: "local" | "mac-aws" | "skip"
#   Exit 0 = routable host found
#   Exit 1 = all hosts down, nothing to route to (caller should abort or queue)
#
# Host registry (static; no new infra):
#   local     = M4 Max Mac mini (always present, the only live host today)
#   mac-aws   = AWS dedicated Mac host (momotaro-mac tag), present when
#               ~/.openclaw/workspace/aws-config/mac-instance-allocated.json
#               has status=ALLOCATED_AND_READY
#
# Health signals consumed:
#   ~/.openclaw/logs/health-check.log   (written by system-health-check.sh every 2h)
#   The mac-instance-allocated.json config file
#
# Usage examples:
#   host-router.sh                          # route a general task → local/mac-aws/skip
#   host-router.sh gpu                      # prefer mac-aws for GPU-capable work
#   host-router.sh ios                      # prefer mac-aws (Xcode) if available
#   host-router.sh general status           # print human-readable host status table
#   host-router.sh general health           # exit 0 if any host healthy, 1 if all down

set -euo pipefail

TASK_TYPE="${1:-general}"
MODE="${2:-route}"

WORKSPACE="$HOME/.openclaw/workspace"
LOG_DIR="$HOME/.openclaw/logs"
HEALTH_LOG="$LOG_DIR/health-check.log"
AWS_CONFIG="$WORKSPACE/aws-config/mac-instance-allocated.json"
HOST_STATE_LOG="$LOG_DIR/host-router.log"

mkdir -p "$LOG_DIR"

# ── Logging helper ────────────────────────────────────────────────────────────
_log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$HOST_STATE_LOG"
}

# ── Local host health ─────────────────────────────────────────────────────────
# Reads the last health-check.log entry. Local is considered UP unless the log
# shows an ERROR in the last 3 hours and disk is critical (>90%).
# Returns: 0 = healthy, 1 = degraded/down
local_host_healthy() {
    # If health log doesn't exist yet, assume local is healthy (brand-new install)
    if [ ! -f "$HEALTH_LOG" ]; then
        return 0
    fi

    # Check log freshness — if last run was >4h ago, flag WARN but stay up
    LAST_RUN_TS=$(grep -oE '^\[[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}\]' "$HEALTH_LOG" \
        | tail -1 | tr -d '[]' 2>/dev/null || echo "")
    if [ -n "$LAST_RUN_TS" ]; then
        LAST_EPOCH=$(date -j -f "%Y-%m-%d %H:%M:%S" "$LAST_RUN_TS" "+%s" 2>/dev/null || echo 0)
        NOW_EPOCH=$(date +%s)
        AGE_HOURS=$(( (NOW_EPOCH - LAST_EPOCH) / 3600 ))
        if [ "$AGE_HOURS" -gt 4 ]; then
            _log "WARN local health-check.log is ${AGE_HOURS}h stale"
        fi
    fi

    # Fatal signal: disk >90% in the last log block
    if tail -50 "$HEALTH_LOG" | grep -q "ERROR: Disk Space"; then
        _log "ERROR local host: disk critical per health-check.log"
        return 1
    fi

    # Fatal signal: memory files missing
    if tail -50 "$HEALTH_LOG" | grep -q "ERROR: Memory Files"; then
        _log "ERROR local host: memory files missing per health-check.log"
        return 1
    fi

    return 0
}

# ── AWS Mac host health ───────────────────────────────────────────────────────
# Returns: 0 = allocated and reachable, 1 = not available
aws_mac_healthy() {
    if [ ! -f "$AWS_CONFIG" ]; then
        return 1
    fi

    STATUS=$(jq -r '.status // empty' "$AWS_CONFIG" 2>/dev/null)
    if [ "$STATUS" != "ALLOCATED_AND_READY" ]; then
        return 1
    fi

    # If there's a hostname/IP in the config, attempt a quick TCP ping
    HOST_IP=$(jq -r '.host_ip // empty' "$AWS_CONFIG" 2>/dev/null)
    if [ -n "$HOST_IP" ]; then
        if ! nc -z -w 3 "$HOST_IP" 22 2>/dev/null; then
            _log "WARN mac-aws: allocated but SSH port 22 unreachable at $HOST_IP"
            return 1
        fi
    fi
    # No IP yet (host allocated but instance not launched) — treat as unavailable
    # for routing but not as an error state
    if [ -z "$HOST_IP" ]; then
        _log "INFO mac-aws: dedicated host allocated but no instance IP yet — unavailable for routing"
        return 1
    fi

    return 0
}

# ── Prefer order by task type ─────────────────────────────────────────────────
# Returns a space-separated ordered list of candidate hosts for a given task.
# The router tries them left-to-right and returns the first healthy one.
candidates_for_task() {
    local task="$1"
    case "$task" in
        gpu|ios|xcode|swift)
            # Prefer AWS Mac (Xcode/GPU); fall back to local
            echo "mac-aws local"
            ;;
        ml|train*)
            # ML training prefers AWS Mac for RAM; fall back to local
            echo "mac-aws local"
            ;;
        ops|code|general|*)
            # Everything else: local first (always live), AWS Mac second
            echo "local mac-aws"
            ;;
    esac
}

# ── Health-check a single named host ─────────────────────────────────────────
host_is_healthy() {
    local host="$1"
    case "$host" in
        local)   local_host_healthy ;;
        mac-aws) aws_mac_healthy ;;
        *)       return 1 ;;
    esac
}

# ── Status display ────────────────────────────────────────────────────────────
print_status() {
    echo "Host Status — $(date '+%Y-%m-%d %H:%M:%S')"
    echo "─────────────────────────────────────────────"

    # local
    if local_host_healthy; then
        echo "  local     : UP   (M4 Max Mac mini — primary)"
    else
        echo "  local     : DOWN (check $HEALTH_LOG)"
    fi

    # mac-aws
    if [ -f "$AWS_CONFIG" ]; then
        STATUS=$(jq -r '.status // "unknown"' "$AWS_CONFIG" 2>/dev/null)
        ITYPE=$(jq -r '.instance_type // "?"' "$AWS_CONFIG" 2>/dev/null)
        REGION=$(jq -r '.region // "?"' "$AWS_CONFIG" 2>/dev/null)
        if aws_mac_healthy; then
            echo "  mac-aws   : UP   ($ITYPE in $REGION, status=$STATUS)"
        else
            echo "  mac-aws   : DOWN (status=$STATUS — no reachable instance yet)"
        fi
    else
        echo "  mac-aws   : PENDING (no dedicated host allocated yet — allocator running 3x daily)"
    fi

    echo "─────────────────────────────────────────────"
}

# ── Main routing logic ────────────────────────────────────────────────────────
route_task() {
    local task="$1"
    local candidates
    candidates=$(candidates_for_task "$task")

    for host in $candidates; do
        if host_is_healthy "$host"; then
            _log "INFO route task=$task → $host"
            echo "$host"
            return 0
        else
            _log "INFO route task=$task: $host unhealthy, trying next"
        fi
    done

    # All candidates exhausted
    _log "ERROR route task=$task: all hosts unhealthy — returning skip"
    echo "skip"
    return 1
}

# ── Dispatch ──────────────────────────────────────────────────────────────────
case "$MODE" in
    route)
        route_task "$TASK_TYPE"
        ;;
    status)
        print_status
        ;;
    health)
        # Exit 0 if any host is healthy
        for host in local mac-aws; do
            if host_is_healthy "$host"; then
                exit 0
            fi
        done
        exit 1
        ;;
    *)
        echo "Usage: host-router.sh [task_type] [route|status|health]" >&2
        exit 1
        ;;
esac
