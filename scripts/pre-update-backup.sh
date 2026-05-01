#!/usr/bin/env bash
# pre-update-backup.sh — Config snapshot before openclaw update
# Run automatically before any openclaw update to ensure rollback is possible.
#
# Usage: bash scripts/pre-update-backup.sh
# Returns: 0 always (non-blocking — update should not be stopped by backup failure)

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

OUTPUT_DIR="$HOME/tmp/pre-update-backups"
LOG_FILE="$HOME/.openclaw/logs/pre-update-backup.log"
KEEP_BACKUPS=5

log() {
  local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $*"
  echo "$msg"
  echo "$msg" >> "$LOG_FILE" 2>/dev/null || true
}

{
  mkdir -p "$OUTPUT_DIR"
  mkdir -p "$(dirname "$LOG_FILE")"

  log "Pre-update config snapshot starting..."

  openclaw backup create \
    --only-config \
    --output "$OUTPUT_DIR" \
    --verify \
    2>&1 && log "✅ Config snapshot created in $OUTPUT_DIR" || log "⚠️ Snapshot failed (non-fatal)"

  # Keep last 5 pre-update backups
  BACKUPS=$(ls -t "$OUTPUT_DIR"/*.tar.gz 2>/dev/null | tail -n +$((KEEP_BACKUPS + 1)))
  if [[ -n "$BACKUPS" ]]; then
    echo "$BACKUPS" | xargs rm -f
    log "  Rotated old pre-update backups (kept ${KEEP_BACKUPS})"
  fi

  log "Pre-update backup done."
} || true

exit 0
