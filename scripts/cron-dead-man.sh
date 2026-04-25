#!/bin/bash
# cron-dead-man.sh — Dead-man monitor for all registered cron jobs.
#
# Reads heartbeat files from ~/.openclaw/logs/cron-heartbeats/<name>.json
# and alerts via Telegram if any job's last-run is older than its max-age.
#
# Jobs are categorised by criticality tier — each tier has a different
# alerting threshold and behaviour:
#
#   CRITICAL  — alert immediately on first miss; Telegram + daily log
#   IMPORTANT — alert after first miss during active hours; Telegram
#   ROUTINE   — log only; no Telegram (checked by daily error-digest)
#
# Usage:
#   bash cron-dead-man.sh [--verbose] [--dry-run]
#
# Cron (hourly, offset to not clash with other jobs):
#   23 * * * * bash ~/.openclaw/workspace/scripts/cron-dead-man.sh >> ~/.openclaw/logs/cron-dead-man.log 2>&1

set -uo pipefail

# Load secrets and notification helpers
set -a; source "$HOME/.openclaw/.env" 2>/dev/null || true; set +a
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/notify.sh
source "$SCRIPT_DIR/lib/notify.sh"

WORKSPACE="$HOME/.openclaw/workspace"
HB_DIR="$HOME/.openclaw/logs/cron-heartbeats"
LOG_DIR="$HOME/.openclaw/logs"
LOG_FILE="$LOG_DIR/cron-dead-man.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
VERBOSE=0
DRY_RUN=0

while [[ $# -gt 0 ]]; do
  case $1 in
    --verbose) VERBOSE=1 ;;
    --dry-run) DRY_RUN=1 ;;
  esac
  shift
done

mkdir -p "$HB_DIR" "$LOG_DIR"

_log() { echo "[$TIMESTAMP] $*" | tee -a "$LOG_FILE" 2>/dev/null; }
_vlog() { [ $VERBOSE -eq 1 ] && _log "$*" || true; }

# ── Job registry ──────────────────────────────────────────────────────────────
# Format: "job-name:max_age_seconds:tier"
# max_age = 2–3× the schedule interval (buffer for slow runs / weekends)
#
# Tiers: critical | important | routine

JOB_REGISTRY=(
  # CRITICAL — core session infrastructure
  "session-watchdog:5400:critical"          # hourly cron → alert if >90min
  "daily-session-reset:93600:critical"       # daily 4am → alert if >26h

  # IMPORTANT — user-facing outputs
  "morning-briefing:93600:important"         # daily 6am → 26h
  "evening-briefing:93600:important"         # daily 5pm → 26h
  "system-health-check:14400:important"      # every 2h → 4h
  "observer-agent:14400:important"           # every 2h → 4h
  "github-backup:14400:important"            # every 2h → 4h
  "quota-monitoring:21600:important"         # every 4h → 6h
  "spending-cap-check:9000:important"        # hourly → 2.5h
  "backup-openclaw:93600:important"          # daily 3:15 → 26h
  "restore-drill:691200:routine"             # weekly Sun → 8d

  # ROUTINE — non-critical maintenance
  "auto-flush-session-context:93600:routine" # daily midnight → 26h
  "status-page-update:7200:routine"          # every 30min → 2h
  "error-digest:93600:routine"               # daily 4:45pm → 26h
  "collect-daily-metrics:93600:routine"      # daily 10pm → 26h
  "session-checkpoint:7200:routine"          # per-session → 2h
)

# ── Alert dedup: only alert once per job per 2h window ───────────────────────
_already_alerted() {
  local job="$1"
  local alert_stamp="$HB_DIR/.alert-${job}"
  if [ -f "$alert_stamp" ]; then
    local age
    age=$(python3 -c "import time,os; print(int(time.time()-os.path.getmtime('$alert_stamp')))" 2>/dev/null || echo 99999)
    [ "$age" -lt 7200 ] && return 0  # alerted within 2h
  fi
  touch "$alert_stamp" 2>/dev/null || true
  return 1
}

# ── Check one job ─────────────────────────────────────────────────────────────
check_job() {
  local job_name="$1"
  local max_age="$2"
  local tier="$3"
  local hb_file="$HB_DIR/${job_name}.json"

  # Never-run: heartbeat file doesn't exist yet
  if [ ! -f "$hb_file" ]; then
    _vlog "SKIP  [$tier] $job_name — no heartbeat yet (never ran or new job)"
    return 0  # Grace period for new installs
  fi

  # Check age
  local age exit_code last_run
  age=$(python3 -c "
import json, time
d = json.load(open('$hb_file'))
print(int(time.time() - d.get('last_run_ts', 0)))
" 2>/dev/null || echo 999999)
  exit_code=$(python3 -c "import json; d=json.load(open('$hb_file')); print(d.get('exit_code',0))" 2>/dev/null || echo 0)
  last_run=$(python3 -c "import json; d=json.load(open('$hb_file')); print(d.get('last_run','?')[:16].replace('T',' '))" 2>/dev/null || echo "?")

  local age_min=$(( age / 60 ))
  local max_min=$(( max_age / 60 ))

  if [ "$age" -lt "$max_age" ]; then
    _vlog "OK    [$tier] $job_name — last run ${age_min}m ago (limit: ${max_min}m) exit=$exit_code"
    return 0
  fi

  # MISSED
  _log "MISS  [$tier] $job_name — last run ${age_min}m ago (limit: ${max_min}m) last=${last_run}"

  # Write to daily notes
  local today hh_mm
  today=$(date +%Y-%m-%d)
  hh_mm=$(date +%H:%M)
  local daily_file="$WORKSPACE/memory/$today.md"
  if [ -f "$daily_file" ]; then
    echo "- [$hh_mm] ⚠️ Cron missed [$tier]: $job_name — last ran ${age_min}m ago (limit ${max_min}m)" \
      >> "$daily_file" 2>/dev/null || true
  fi

  # Alert logic by tier
  if [ "$tier" = "critical" ]; then
    if ! _already_alerted "$job_name"; then
      local msg="🚨 <b>OpenClaw Dead-Man Alert</b>

<b>CRITICAL cron missed:</b> <code>${job_name}</code>
Last run: ${last_run} (${age_min}m ago)
Limit: ${max_min}m

Check <code>~/.openclaw/logs/</code> for details."
      [ $DRY_RUN -eq 0 ] && notify_telegram "$msg" "HTML"
      _log "ALERT sent for critical job: $job_name"
    else
      _log "ALERT deduped for $job_name (alerted within 2h)"
    fi

  elif [ "$tier" = "important" ]; then
    if ! _already_alerted "$job_name"; then
      local msg="⚠️ <b>OpenClaw Dead-Man Warning</b>

<b>IMPORTANT cron missed:</b> <code>${job_name}</code>
Last run: ${last_run} (${age_min}m ago)
Limit: ${max_min}m"
      [ $DRY_RUN -eq 0 ] && send_telegram "$msg"
      _log "ALERT sent for important job: $job_name"
    fi

  else
    _log "NOTE  routine job missed: $job_name (no alert — check error-digest)"
  fi

  return 1
}

# ── Main ──────────────────────────────────────────────────────────────────────
_log "Dead-man check starting (${#JOB_REGISTRY[@]} jobs)"

missed_critical=0
missed_important=0
missed_routine=0
ok=0

for entry in "${JOB_REGISTRY[@]}"; do
  IFS=':' read -r jname max_age tier <<< "$entry"
  if check_job "$jname" "$max_age" "$tier"; then
    ok=$((ok + 1))
  else
    case "$tier" in
      critical)  missed_critical=$((missed_critical + 1)) ;;
      important) missed_important=$((missed_important + 1)) ;;
      *)         missed_routine=$((missed_routine + 1)) ;;
    esac
  fi
done

total_missed=$((missed_critical + missed_important + missed_routine))
_log "Done — OK: $ok | Missed: $total_missed (critical=$missed_critical important=$missed_important routine=$missed_routine)"

exit $( [ $total_missed -gt 0 ] && echo 1 || echo 0 )
