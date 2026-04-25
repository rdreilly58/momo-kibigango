#!/bin/bash
# error-digest.sh — Daily error aggregation digest via Telegram
#
# Scans key log files for errors/failures from the last 24h,
# deduplicates, and sends one consolidated Telegram message.
# Designed to run as part of the evening briefing cron (~5 PM).
#
# Usage: bash error-digest.sh [--hours N]  (default: 24h)
# Cron:  Runs inside evening-briefing-full-ga4.sh (sourced) or standalone.

set -uo pipefail

# Load secrets and notification helpers
set -a; source "$HOME/.openclaw/.env" 2>/dev/null || true; set +a
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/notify.sh
source "$SCRIPT_DIR/lib/notify.sh"

LOG_DIR="$HOME/.openclaw/logs"
WORKSPACE="$HOME/.openclaw/workspace"
HOURS="${1:-24}"
CUTOFF=$(date -v-${HOURS}H '+%s' 2>/dev/null || date -d "${HOURS} hours ago" '+%s')
TIMESTAMP=$(date '+%Y-%m-%d %H:%M %Z')
TMP=$(mktemp /tmp/error-digest.XXXXXX)
trap 'rm -f "$TMP"' EXIT

# ── Scan logs for errors ──────────────────────────────────────────────────────
TOTAL_ERRORS=0

scan_log() {
  local label="$1"
  local log_file="$2"
  local tail_lines="${3:-100}"

  [ -f "$log_file" ] || return 0

  local hits
  hits=$(tail -n "$tail_lines" "$log_file" | \
    sed 's/\x1b\[[0-9;]*m//g' | \
    grep -iE "ERROR|FAIL|❌|STALE|CRITICAL|exception" 2>/dev/null | \
    grep -v "grep\|Already ran\|Skipping\|disable_web_page_preview" || true)

  if [ -n "$hits" ]; then
    local count
    count=$(echo "$hits" | wc -l | tr -d ' ')
    TOTAL_ERRORS=$((TOTAL_ERRORS + count))
    # First unique-ish line as representative sample
    local sample
    sample=$(echo "$hits" | sort -u | head -1 | cut -c1-120)
    echo "  [${label}] ${count}x — ${sample}" >> "$TMP"
  fi
}

scan_log "Watchdog"      "$LOG_DIR/session-watchdog.log"         50
scan_log "Health"        "$LOG_DIR/health-check.log"             100
scan_log "Quota"         "$LOG_DIR/quota-monitor.log"            100
scan_log "Quota-errors"  "$LOG_DIR/quota-monitor.error.log"      50
scan_log "Daily-reset"   "$LOG_DIR/daily-reset.log"              30
scan_log "Auto-flush"    "$LOG_DIR/session-context-flush.log"    30
scan_log "Telegraph"     "$LOG_DIR/telegraph.log"                50
scan_log "Auto-update"   "$LOG_DIR/updates.log"                  50
scan_log "Morning brief" "/tmp/morning-briefing.log"             50
scan_log "Evening brief" "/tmp/evening-briefing.log"             50
scan_log "Cron jobs"     "$LOG_DIR/metrics.cron.log"             50

# ── Cron outcomes ─────────────────────────────────────────────────────────────
# Append last line of key operational logs as a status summary
{
  echo ""
  echo "Cron outcomes (last run):"
  for f in \
    "$LOG_DIR/session-watchdog.log" \
    "$LOG_DIR/session-context-flush.log" \
    "$LOG_DIR/health-check.log" \
    "$LOG_DIR/quota-monitor.log"
  do
    [ -f "$f" ] || continue
    label=$(basename "$f" .log)
    last=$(tail -1 "$f" | cut -c1-100)
    echo "  ${label}: ${last}"
  done
} >> "$TMP"

# ── Build and send message ────────────────────────────────────────────────────
echo "[$TIMESTAMP] [digest] Total errors found: $TOTAL_ERRORS"

if [ "$TOTAL_ERRORS" -eq 0 ]; then
  STATUS_ICON="✅"
  STATUS_LINE="All systems OK — no errors in last ${HOURS}h."
else
  STATUS_ICON="⚠️"
  STATUS_LINE="${TOTAL_ERRORS} error(s) detected in last ${HOURS}h."
fi

MESSAGE="${STATUS_ICON} <b>OpenClaw Daily Error Digest</b>
${STATUS_LINE}

$(cat "$TMP")

<i>${TIMESTAMP}</i>"

echo "$MESSAGE"
notify_telegram "$MESSAGE" "HTML"
echo "[$TIMESTAMP] [digest] Digest sent."
