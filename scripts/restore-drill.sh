#!/bin/bash
# restore-drill.sh — Verify that a recent backup is actually restorable.
#
# An untested backup is a wish. Once a week, this script:
#   1. Picks the newest snap-*.tar.gz under ~/.openclaw/backups/
#   2. Extracts it to a tmpdir
#   3. Verifies the MANIFEST.sha256 matches all files
#   4. Sanity-checks key payloads:
#         - config.json parses as JSON
#         - ai-memory.db opens via sqlite3 + 'PRAGMA integrity_check'
#         - sessions.json parses as JSON
#         - crontab.txt is non-empty
#   5. Cleans up
#
# Pass/fail goes to a notify_user alert. Failures are critical priority —
# silent backup rot is exactly what kills you in a real incident.
#
# Usage: bash restore-drill.sh [--snap PATH] [--keep]

set -uo pipefail

set -a; source "$HOME/.openclaw/.env" 2>/dev/null || true; set +a
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/notify.sh
source "$SCRIPT_DIR/lib/notify.sh"

BACKUP_DIR="$HOME/.openclaw/backups"
LOG_FILE="$HOME/.openclaw/logs/restore-drill.log"
HB_DIR="$HOME/.openclaw/logs/cron-heartbeats"
SNAP=""
KEEP=0

while [[ $# -gt 0 ]]; do
  case $1 in
    --snap) SNAP="$2"; shift ;;
    --keep) KEEP=1 ;;
  esac
  shift
done

mkdir -p "$HB_DIR" "$(dirname "$LOG_FILE")"

_log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"; }
_fail() {
  local msg="$1"
  _log "FAIL  $msg"
  notify_user "🚨 OpenClaw restore drill FAILED — $msg" "OpenClaw restore drill" "high" "rotating_light,floppy_disk"
  python3 -c "
import json, time, datetime as dt
json.dump({
    'last_run': dt.datetime.utcnow().isoformat() + 'Z',
    'last_run_ts': int(time.time()),
    'exit_code': 1,
}, open('$HB_DIR/restore-drill.json', 'w'))
" 2>/dev/null || true
  exit 1
}

# Pick newest snap if none specified
if [ -z "$SNAP" ]; then
  SNAP=$(ls -1t "$BACKUP_DIR"/snap-*.tar.gz 2>/dev/null | head -1)
fi
[ -z "$SNAP" ] && _fail "no snap-*.tar.gz found under $BACKUP_DIR"
[ -f "$SNAP" ] || _fail "snap not readable: $SNAP"

snap_age_days=$(python3 -c "import os,time; print(int((time.time()-os.path.getmtime('$SNAP'))/86400))" 2>/dev/null || echo 999)
_log "Drilling $SNAP (age ${snap_age_days}d)"
[ "$snap_age_days" -gt 2 ] && _log "WARN  snap is older than 2d — backup-openclaw.sh may be failing"

WORK=$(mktemp -d /tmp/openclaw-drill.XXXXXX)
[ $KEEP -eq 1 ] || trap 'rm -rf "$WORK"' EXIT

# 1. Extract
tar -xzf "$SNAP" -C "$WORK" 2>>"$LOG_FILE" || _fail "tar -xzf failed"
SNAP_DIR=$(find "$WORK" -mindepth 1 -maxdepth 1 -type d | head -1)
[ -d "$SNAP_DIR" ] || _fail "no top-level dir inside snap"
_log "Extracted → $SNAP_DIR"

# 2. Verify MANIFEST.sha256
[ -f "$SNAP_DIR/MANIFEST.sha256" ] || _fail "MANIFEST.sha256 missing from snap"
(cd "$SNAP_DIR" && shasum -a 256 -c MANIFEST.sha256 >>"$LOG_FILE" 2>&1) || _fail "MANIFEST checksum mismatch — snap is corrupted"
_log "  ✓ MANIFEST verified ($(wc -l <"$SNAP_DIR/MANIFEST.sha256" | tr -d ' ') files)"

# 3. Sanity-check payloads
sanity_check() {
  local label="$1"; shift
  if "$@" >>"$LOG_FILE" 2>&1; then
    _log "  ✓ $label"
  else
    _fail "$label"
  fi
}

[ -f "$SNAP_DIR/config.json" ]            && sanity_check "config.json parses"     python3 -c "import json; json.load(open('$SNAP_DIR/config.json'))"
[ -f "$SNAP_DIR/agents/sessions.json" ]   && sanity_check "sessions.json parses"   python3 -c "import json; json.load(open('$SNAP_DIR/agents/sessions.json'))"
[ -f "$SNAP_DIR/ai-memory.db" ]           && sanity_check "ai-memory.db integrity" sh -c "sqlite3 '$SNAP_DIR/ai-memory.db' 'PRAGMA integrity_check;' | grep -q '^ok$'"
[ -f "$SNAP_DIR/crontab.txt" ]            && sanity_check "crontab non-empty"      sh -c "[ -s '$SNAP_DIR/crontab.txt' ]"

# 4. Done
_log "PASS  drill succeeded for $SNAP"
notify_user "✅ OpenClaw restore drill OK — $(basename "$SNAP") (age ${snap_age_days}d)" "OpenClaw restore drill" "low" ""

python3 -c "
import json, time, datetime as dt
json.dump({
    'last_run': dt.datetime.utcnow().isoformat() + 'Z',
    'last_run_ts': int(time.time()),
    'exit_code': 0,
    'snap': '$SNAP',
}, open('$HB_DIR/restore-drill.json', 'w'))
" 2>/dev/null || true

[ $KEEP -eq 1 ] && _log "Restored tree kept at $WORK (--keep)"
exit 0
