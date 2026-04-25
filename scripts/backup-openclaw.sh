#!/bin/bash
# backup-openclaw.sh — Daily snapshot of OpenClaw state.
#
# Captures the small, high-value state that's hard to reproduce:
#   - ~/.openclaw/config.json
#   - ~/.openclaw/agents/main/sessions/sessions.json
#   - ~/.openclaw/cron/jobs.json + jobs-state.json
#   - ~/.openclaw/workspace/ai-memory.db
#   - ~/.openclaw/workspace/memory/  (lessons-learned, dailies, MEMORY index)
#   - crontab -l output
#
# Skips ~/.openclaw/.env on purpose — secrets stay out of backups. Env
# rotation is documented in config/SECRETS.md instead.
#
# Output: tar.gz at ~/.openclaw/backups/snap-YYYY-MM-DD.tar.gz
# Retention: 30 days (older snaps deleted at the end of each run).

set -uo pipefail

set -a; source "$HOME/.openclaw/.env" 2>/dev/null || true; set +a
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/notify.sh
source "$SCRIPT_DIR/lib/notify.sh"

BACKUP_DIR="$HOME/.openclaw/backups"
TIMESTAMP="$(date '+%Y-%m-%d_%H%M%S')"
DATE="$(date '+%Y-%m-%d')"
SNAP="$BACKUP_DIR/snap-${DATE}.tar.gz"
LOG_FILE="$HOME/.openclaw/logs/backup-openclaw.log"
HB_DIR="$HOME/.openclaw/logs/cron-heartbeats"
RETENTION_DAYS=30

mkdir -p "$BACKUP_DIR" "$HB_DIR" "$(dirname "$LOG_FILE")"

_log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"; }

_log "Starting backup → $SNAP"

# Stage to a tmpdir so we never leave a partial tar in BACKUP_DIR
TMP=$(mktemp -d /tmp/openclaw-backup.XXXXXX)
trap 'rm -rf "$TMP"' EXIT

STAGE="$TMP/snap-$DATE"
mkdir -p "$STAGE"

# Copy individual files (only those that exist)
copy_if_exists() {
  local src="$1"
  local rel="$2"
  if [ -e "$src" ]; then
    mkdir -p "$STAGE/$(dirname "$rel")"
    cp -R "$src" "$STAGE/$rel"
    _log "  + $rel"
  else
    _log "  - skipped (not present): $rel"
  fi
}

copy_if_exists "$HOME/.openclaw/config.json"                        "config.json"
copy_if_exists "$HOME/.openclaw/agents/main/sessions/sessions.json" "agents/sessions.json"
copy_if_exists "$HOME/.openclaw/cron/jobs.json"                     "cron/jobs.json"
copy_if_exists "$HOME/.openclaw/cron/jobs-state.json"               "cron/jobs-state.json"
copy_if_exists "$HOME/.openclaw/workspace/ai-memory.db"             "ai-memory.db"
copy_if_exists "$HOME/.openclaw/workspace/memory"                   "memory"

# Crontab snapshot
crontab -l > "$STAGE/crontab.txt" 2>/dev/null || echo "(no crontab)" > "$STAGE/crontab.txt"
_log "  + crontab.txt"

# Manifest with sha256 of every file — restore drill verifies these.
# Build manifest in tmpdir first to avoid the file listing itself.
(
  cd "$STAGE"
  find . -type f -print0 | sort -z | xargs -0 shasum -a 256 > "$TMP/manifest.tmp" 2>/dev/null
  mv "$TMP/manifest.tmp" MANIFEST.sha256
)
_log "  + MANIFEST.sha256 ($(wc -l <"$STAGE/MANIFEST.sha256" | tr -d ' ') files)"

# Tar it up
(cd "$TMP" && tar -czf "$SNAP" "snap-$DATE")
size=$(du -h "$SNAP" | cut -f1)
_log "Wrote $SNAP ($size)"

# Retention sweep
deleted=$(find "$BACKUP_DIR" -name 'snap-*.tar.gz' -mtime "+$RETENTION_DAYS" -print -delete 2>/dev/null | wc -l | tr -d ' ')
[ "$deleted" -gt 0 ] && _log "Pruned $deleted snap(s) older than ${RETENTION_DAYS}d"

# Heartbeat
python3 -c "
import json, time, datetime as dt
json.dump({
    'last_run': dt.datetime.utcnow().isoformat() + 'Z',
    'last_run_ts': int(time.time()),
    'exit_code': 0,
    'snap': '$SNAP',
}, open('$HB_DIR/backup-openclaw.json', 'w'))
" 2>/dev/null || true

_log "Done"
exit 0
