#!/usr/bin/env bash
# backup-openclaw.sh — Targeted backup of critical OpenClaw state + iCloud offsite
# Backs up: config, memory, cron, agents, LaunchAgents plists
# Skips: skills (2GB), extensions (1.3GB), envs (1.5GB), plugin-runtime-deps (763MB)
#        workspace (on git), logs, browser cache, ntfy-data
#
# Usage: bash scripts/backup-openclaw.sh [--notify] [--dry-run]

set -euo pipefail

# ── Config ────────────────────────────────────────────────────────────────────
LOCAL_BACKUP_DIR="$HOME/Documents/OpenClaw-Backups"
ICLOUD_BACKUP_DIR="$HOME/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Backups"
OPENCLAW_DIR="$HOME/.openclaw"
KEEP_LOCAL=7       # days of local backups to keep
KEEP_ICLOUD=14     # days of iCloud backups to keep
TELEGRAM_CHAT_ID="8755120444"
TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"

# ── What to back up ───────────────────────────────────────────────────────────
# Critical: config, memory (SQLite+vector), cron, agents, node ID, telegram state
INCLUDE_PATHS=(
  "$OPENCLAW_DIR/openclaw.json"
  "$OPENCLAW_DIR/openclaw.json.last-good"
  "$OPENCLAW_DIR/node.json"
  "$OPENCLAW_DIR/memory"
  "$OPENCLAW_DIR/cron"
  "$OPENCLAW_DIR/agents"
  "$OPENCLAW_DIR/telegram"
  "$OPENCLAW_DIR/flows"
  "$HOME/Library/LaunchAgents/ai.openclaw.gateway.plist"
  "$HOME/Library/LaunchAgents/ai.openclaw.node.plist"
  "$HOME/Library/LaunchAgents/ai.openclaw.metrics-exporter.plist"
  "$HOME/Library/LaunchAgents/ai.openclaw.session-watchdog.plist"
)

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
ARCHIVE_NAME="openclaw-backup-${TIMESTAMP}.tar.gz"
ARCHIVE_PATH="$LOCAL_BACKUP_DIR/$ARCHIVE_NAME"

log "OpenClaw Targeted Backup — $TIMESTAMP"
[[ "$DRY_RUN" == true ]] && log "DRY RUN mode"

mkdir -p "$LOCAL_BACKUP_DIR"
mkdir -p "$ICLOUD_BACKUP_DIR"

# ── Step 1: Build file list ────────────────────────────────────────────────────
log "Step 1: Resolving backup sources..."
EXISTING_PATHS=()
for p in "${INCLUDE_PATHS[@]}"; do
  if [[ -e "$p" ]]; then
    EXISTING_PATHS+=("$p")
    log "  + $(du -sh "$p" 2>/dev/null | cut -f1) — $(basename $p)"
  fi
done
log "  Total sources: ${#EXISTING_PATHS[@]}"

# ── Step 2: Create archive ─────────────────────────────────────────────────────
log "Step 2: Creating archive → $ARCHIVE_NAME"

if [[ "$DRY_RUN" == false ]]; then
  # Write a manifest first
  MANIFEST=$(mktemp)
  echo "{\"created\":\"$TIMESTAMP\",\"sources\":[$(printf '"%s",' "${EXISTING_PATHS[@]}" | sed 's/,$//')]}" > "$MANIFEST"

  # Create tar archive
  tar -czf "$ARCHIVE_PATH" \
    --exclude="$OPENCLAW_DIR/memory/*.log" \
    "${EXISTING_PATHS[@]}" 2>/dev/null || fail "tar failed"

  ARCHIVE_SIZE=$(du -sh "$ARCHIVE_PATH" | cut -f1)
  log "  ✅ Archive: $ARCHIVE_NAME ($ARCHIVE_SIZE)"
else
  ARCHIVE_SIZE="~N/A (dry run)"
  log "  Would create: $ARCHIVE_PATH"
fi

# ── Step 3: Config-only quick backup (always, fast) ───────────────────────────
log "Step 3: Config-only snapshot..."
if [[ "$DRY_RUN" == false ]]; then
  CONFIG_SNAP="$LOCAL_BACKUP_DIR/config-latest.json"
  cp "$OPENCLAW_DIR/openclaw.json" "$CONFIG_SNAP"
  log "  ✅ Config snapshot: config-latest.json"
fi

# ── Step 4: Copy to iCloud ─────────────────────────────────────────────────────
log "Step 4: Uploading to iCloud Drive..."
if [[ "$DRY_RUN" == false ]]; then
  cp "$ARCHIVE_PATH" "$ICLOUD_BACKUP_DIR/$ARCHIVE_NAME" || fail "iCloud copy failed"
  # Also keep a rolling latest symlink
  cp "$OPENCLAW_DIR/openclaw.json" "$ICLOUD_BACKUP_DIR/config-latest.json" 2>/dev/null || true
  log "  ✅ iCloud: $ARCHIVE_NAME"
  log "  ✅ iCloud: config-latest.json (quick restore reference)"
else
  log "  Would copy to: $ICLOUD_BACKUP_DIR/$ARCHIVE_NAME"
fi

# ── Step 5: Rotate old backups ─────────────────────────────────────────────────
log "Step 5: Rotating old backups..."
if [[ "$DRY_RUN" == false ]]; then
  find "$LOCAL_BACKUP_DIR" -name "openclaw-backup-*.tar.gz" -mtime +${KEEP_LOCAL} -delete 2>/dev/null || true
  find "$ICLOUD_BACKUP_DIR" -name "openclaw-backup-*.tar.gz" -mtime +${KEEP_ICLOUD} -delete 2>/dev/null || true
  LOCAL_COUNT=$(ls "$LOCAL_BACKUP_DIR"/openclaw-backup-*.tar.gz 2>/dev/null | wc -l | tr -d ' ')
  ICLOUD_COUNT=$(ls "$ICLOUD_BACKUP_DIR"/openclaw-backup-*.tar.gz 2>/dev/null | wc -l | tr -d ' ')
  log "  Local: $LOCAL_COUNT backups retained (${KEEP_LOCAL}d TTL)"
  log "  iCloud: $ICLOUD_COUNT backups retained (${KEEP_ICLOUD}d TTL)"
fi

# ── Done ───────────────────────────────────────────────────────────────────────
log "✅ Backup complete!"

if [[ "$DRY_RUN" == false ]]; then
  MSG="✅ *OpenClaw Backup Complete*
📦 \`$ARCHIVE_NAME\`
💾 Size: $ARCHIVE_SIZE
☁️ iCloud: uploading
📁 Local: $LOCAL_COUNT | iCloud: $ICLOUD_COUNT
🗓 $(date '+%Y-%m-%d %H:%M EDT')"
  telegram_notify "$MSG"
  echo ""
  echo "Archive: $ARCHIVE_PATH"
  echo "iCloud:  $ICLOUD_BACKUP_DIR/$ARCHIVE_NAME"
fi
