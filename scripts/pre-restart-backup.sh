#!/usr/bin/env bash
# pre-restart-backup.sh — Config snapshot before openclaw gateway restart
# Called before gateway restarts to ensure config is recoverable.
#
# Usage: bash scripts/pre-restart-backup.sh
# Also used by: openclaw gateway restart (call this first)
#
# Example pre-restart sequence:
#   bash ~/.openclaw/workspace/scripts/pre-restart-backup.sh && openclaw gateway restart

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

OUTPUT_DIR="$HOME/.openclaw/restart-backups"
KEEP_BACKUPS=10

log() { echo "[$(date '+%H:%M:%S')] $*"; }

mkdir -p "$OUTPUT_DIR"

log "Pre-restart config snapshot..."
openclaw backup create \
  --only-config \
  --output "$OUTPUT_DIR" \
  2>&1 && log "✅ Config snapshot saved to $OUTPUT_DIR" || {
    log "⚠️ Snapshot failed (non-fatal — proceeding with restart)"
    exit 0
  }

# Keep last 10 restart backups
BACKUPS=$(ls -t "$OUTPUT_DIR"/*.tar.gz 2>/dev/null | tail -n +$((KEEP_BACKUPS + 1)))
if [[ -n "$BACKUPS" ]]; then
  echo "$BACKUPS" | xargs rm -f
  log "  Rotated old restart backups (kept ${KEEP_BACKUPS})"
fi

log "Done."
exit 0
