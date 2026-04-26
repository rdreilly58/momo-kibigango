#!/usr/bin/env bash
# backup-openclaw.sh — Full state backup of ~/.openclaw → iCloud offsite
# Uses native `openclaw backup create` for complete coverage (~3GB).
# iCloud has 277GB free — 5GB is no problem.
#
# Usage: bash scripts/backup-openclaw.sh [--notify] [--dry-run]

set -euo pipefail

# ── Config ────────────────────────────────────────────────────────────────────
ICLOUD_BACKUP_DIR="$HOME/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Backups"
KEEP_ICLOUD=7      # days of iCloud backups to keep
TELEGRAM_CHAT_ID="8755120444"
TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"

# ── Args ──────────────────────────────────────────────────────────────────────
NOTIFY=false
DRY_RUN=false
for arg in "$@"; do
  case $arg in
    --notify) NOTIFY=true ;;
    --dry-run) DRY_RUN=true ;;
  esac
done

# ── Helpers ───────────────────────────────────────────────────────────────────
log() { echo "[$(date '+%H:%M:%S')] $*"; }

telegram_notify() {
  local msg="$1"
  if [[ "$NOTIFY" == true && -n "$TELEGRAM_BOT_TOKEN" ]]; then
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
      -d chat_id="$TELEGRAM_CHAT_ID" \
      -d text="$msg" \
      -d parse_mode="Markdown" > /dev/null 2>&1 || true
  fi
}

fail() {
  local msg="$1"
  log "❌ FAILED: $msg"
  telegram_notify "⚠️ *OpenClaw Backup FAILED*
Error: $msg
Time: $(date '+%Y-%m-%d %H:%M EDT')"
  exit 1
}

# ── Pre-flight ─────────────────────────────────────────────────────────────────
TIMESTAMP=$(date -u '+%Y-%m-%dT%H-%M-%SZ')
log "OpenClaw Full State Backup — $TIMESTAMP"
[[ "$DRY_RUN" == true ]] && log "DRY RUN mode"

mkdir -p "$ICLOUD_BACKUP_DIR"

# ── Step 1: Full backup via openclaw backup create ─────────────────────────────
log "Step 1: Running openclaw backup create (full state → iCloud)..."
log "  Output: $ICLOUD_BACKUP_DIR"
log "  Estimated size: ~3GB — includes all of ~/.openclaw + workspace"

if [[ "$DRY_RUN" == true ]]; then
  log "  Would run: openclaw backup create --output '$ICLOUD_BACKUP_DIR' --verify"
else
  openclaw backup create \
    --output "$ICLOUD_BACKUP_DIR" \
    --verify \
    2>&1 | tee /tmp/openclaw-backup-last.log || fail "openclaw backup create failed"

  # Find the archive just created
  ARCHIVE_PATH=$(ls -t "$ICLOUD_BACKUP_DIR"/*.tar.gz 2>/dev/null | head -1)
  [[ -z "$ARCHIVE_PATH" ]] && fail "No archive found after backup"
  ARCHIVE_SIZE=$(du -sh "$ARCHIVE_PATH" | cut -f1)
  ARCHIVE_NAME=$(basename "$ARCHIVE_PATH")
  log "  ✅ Archive: $ARCHIVE_NAME ($ARCHIVE_SIZE)"
fi

# ── Step 2: Keep config-latest.json in iCloud (fast restore reference) ─────────
log "Step 2: Updating config-latest.json in iCloud..."
if [[ "$DRY_RUN" == false ]]; then
  cp "$HOME/.openclaw/openclaw.json" "$ICLOUD_BACKUP_DIR/config-latest.json" 2>/dev/null || true
  log "  ✅ config-latest.json updated"
fi

# ── Step 3: Rotate old iCloud backups ──────────────────────────────────────────
log "Step 3: Rotating old iCloud backups (keep ${KEEP_ICLOUD} days)..."
if [[ "$DRY_RUN" == false ]]; then
  find "$ICLOUD_BACKUP_DIR" -name "*-openclaw-backup.tar.gz" -mtime +${KEEP_ICLOUD} -delete 2>/dev/null || true
  ICLOUD_COUNT=$(ls "$ICLOUD_BACKUP_DIR"/*.tar.gz 2>/dev/null | wc -l | tr -d ' ')
  log "  iCloud backups retained: $ICLOUD_COUNT"
fi

# ── Done ───────────────────────────────────────────────────────────────────────
log "✅ Backup complete!"

if [[ "$DRY_RUN" == false ]]; then
  MSG="✅ *OpenClaw Full Backup Complete*
📦 \`$ARCHIVE_NAME\`
💾 Size: $ARCHIVE_SIZE
☁️ iCloud: syncing
📁 iCloud copies: $ICLOUD_COUNT
🗓 $(date '+%Y-%m-%d %H:%M EDT')"
  telegram_notify "$MSG"
  echo ""
  echo "Archive: $ARCHIVE_PATH"
fi
