#!/bin/bash
# pre-reboot-quit-apps.sh — Gracefully quit apps known to block shutdown
#
# Why: macOS 26.3 (Tahoe) Mail.app's WebKit child processes regularly refuse
# to terminate cleanly during shutdown, causing 60-90 second hangs.
# Root cause: pageCount > 0 with shutdownPreventingScopeCounter=0 — open IMAP
# connections + rich-content rendering hold shutdown until launchd SIGKILLs them.
#
# Strategy: Quit blocking apps via osascript BEFORE the system shutdown sequence
# starts, so each app gets a chance to flush state cleanly on its own timeline.
#
# Triggers:
#   1. Manual: bash ~/.openclaw/workspace/scripts/pre-reboot-quit-apps.sh
#   2. shutdown-watcher LaunchAgent (com.momotaro.pre-reboot-quit-apps)
#      fires on RunAtLoad + responds to shutdown signal
#   3. Convenience aliases in shell (see TOOLS.md)
#
# Created: 2026-04-30 by Momotaro after Bob's M4 hung 88 sec on Mail shutdown.

set -uo pipefail

LOG_FILE="$HOME/.openclaw/logs/pre-reboot-quit-apps.log"
mkdir -p "$(dirname "$LOG_FILE")"

log() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $*"
    echo "$msg" | tee -a "$LOG_FILE"
}

# Apps that historically block shutdown on this system. Add to this list when new
# offenders appear in /usr/bin/log show ... eventMessage CONTAINS "canTerminateAuxiliaryProcess".
BLOCKING_APPS=(
    "Mail"          # WebKit children refuse to terminate (primary offender)
    "Music"         # Long-running AirPlay sessions
    "Photos"        # iCloud sync workers
    "Safari"        # Many open WebContent processes
)

quit_app() {
    local app="$1"

    # Skip if not running
    if ! pgrep -xq "$app"; then
        log "  ⏭  $app: not running, skip"
        return 0
    fi

    log "  ⏳ $app: running, requesting graceful quit..."

    # Give the app up to 8 s to quit on its own
    osascript -e "tell application \"$app\" to quit" 2>/dev/null &
    local osa_pid=$!

    local waited=0
    while [ $waited -lt 8 ] && pgrep -xq "$app"; do
        sleep 1
        waited=$((waited + 1))
    done

    # Reap the osascript helper if it's still hanging
    kill "$osa_pid" 2>/dev/null || true
    wait "$osa_pid" 2>/dev/null || true

    if pgrep -xq "$app"; then
        log "  ⚠  $app: still running after 8 s, escalating to SIGTERM"
        pkill -TERM -x "$app" 2>/dev/null || true
        sleep 2
        if pgrep -xq "$app"; then
            log "  ⚠  $app: still running after SIGTERM — leaving for shutdown sequence to handle"
        else
            log "  ✅ $app: stopped via SIGTERM"
        fi
    else
        log "  ✅ $app: quit cleanly in ${waited}s"
    fi
}

log "=== pre-reboot-quit-apps started ==="

for app in "${BLOCKING_APPS[@]}"; do
    quit_app "$app"
done

log "=== pre-reboot-quit-apps complete ==="
exit 0
