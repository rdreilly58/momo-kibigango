#!/usr/bin/env bash
# backup-openclaw.sh — OpenClaw backup (workspace via git, state via openclaw backup)
#
# Strategy:
#   - Workspace backup  = git push (already tracked in git, lightweight, fast)
#   - Full state backup = openclaw backup create --no-include-workspace (skips venv, ~132MB vs 16GB)
#   - Config backup     = openclaw backup create --only-config (tiny, fast restore reference)
#   - Encryption        = scripts/backup-encrypt.sh (GPG AES-256, key in macOS Keychain)
#
# Usage: bash scripts/backup-openclaw.sh [--notify] [--dry-run]

set -euo pipefail

# ── Run lock — prevent concurrent/burst runs ───────────────────────────────────
LOCK_FILE="/tmp/openclaw-backup.lock"
if [[ -f "$LOCK_FILE" ]]; then
  LOCK_AGE=$(( $(date +%s) - $(stat -f %m "$LOCK_FILE" 2>/dev/null || echo 0) ))
  if [[ $LOCK_AGE -lt 3600 ]]; then  # lock is < 1 hour old
    echo "[$(date '+%H:%M:%S')] Backup already running (lock age: ${LOCK_AGE}s). Skipping."
    exit 0
  fi
  echo "[$(date '+%H:%M:%S')] Stale lock detected (age: ${LOCK_AGE}s). Proceeding."
fi
touch "$LOCK_FILE"
trap "rm -f '$LOCK_FILE'" EXIT

# Ensure homebrew bin is on PATH for cron-spawned runs
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

# ── Config ────────────────────────────────────────────────────────────────────
ICLOUD_BACKUP_DIR="$HOME/Library/Mobile Documents/com~apple~CloudDocs/OpenClaw-Backups"
WORKSPACE_DIR="$HOME/.openclaw/workspace"
KEEP_ICLOUD=7      # days of daily iCloud backups to keep
TELEGRAM_CHAT_ID="8755120444"
TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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
log "OpenClaw Backup — $TIMESTAMP"
[[ "$DRY_RUN" == true ]] && log "DRY RUN mode"

mkdir -p "$ICLOUD_BACKUP_DIR"

# ── Step 1: Workspace backup via git push ──────────────────────────────────────
log "Step 1: Workspace backup via git push..."
log "  (Workspace is tracked in git — git push IS the workspace backup)"
if [[ "$DRY_RUN" == true ]]; then
  log "  Would run: cd $WORKSPACE_DIR && git push"
else
  cd "$WORKSPACE_DIR"
  git push 2>&1 | tail -3 && log "  ✅ git push complete" || log "  ⚠️ git push failed (non-fatal — continuing)"
  cd - > /dev/null
fi

# ── Step 2: Full state backup (no workspace/venv) ──────────────────────────────
log "Step 2: Full state backup → iCloud (--no-include-workspace)..."
log "  Skips the workspace venv; ~132MB vs 16GB full backup"
log "  Output: $ICLOUD_BACKUP_DIR"

ARCHIVE_PATH=""
ARCHIVE_SIZE=""
ARCHIVE_NAME=""

if [[ "$DRY_RUN" == true ]]; then
  log "  Would run: openclaw backup create --no-include-workspace --output '$ICLOUD_BACKUP_DIR' --verify"
else
  openclaw backup create \
    --no-include-workspace \
    --output "$ICLOUD_BACKUP_DIR" \
    --verify \
    2>&1 | tee /tmp/openclaw-backup-last.log || fail "openclaw backup create failed"

  # Find the archive just created (excludes monthly- prefix)
  ARCHIVE_PATH=$(ls -t "$ICLOUD_BACKUP_DIR"/[0-9]*-openclaw-backup.tar.gz 2>/dev/null | head -1 || true)
  [[ -z "$ARCHIVE_PATH" ]] && fail "No archive found after backup"
  ARCHIVE_SIZE=$(du -sh "$ARCHIVE_PATH" | cut -f1)
  ARCHIVE_NAME=$(basename "$ARCHIVE_PATH")
  log "  ✅ Archive: $ARCHIVE_NAME ($ARCHIVE_SIZE)"

  # Encrypt the archive
  log "  Encrypting archive..."
  bash "$SCRIPT_DIR/backup-encrypt.sh" "$ARCHIVE_PATH" && log "  ✅ Encrypted" || log "  ⚠️ Encryption failed (non-fatal)"
fi

# ── Step 3: Config-only backup (fast restore reference) ───────────────────────
log "Step 3: Config-only backup → iCloud..."
if [[ "$DRY_RUN" == true ]]; then
  log "  Would run: openclaw backup create --only-config --output '$ICLOUD_BACKUP_DIR'"
else
  openclaw backup create \
    --only-config \
    --output "$ICLOUD_BACKUP_DIR" \
    2>&1 >> /tmp/openclaw-backup-last.log || log "  ⚠️ Config-only backup failed (non-fatal)"
  log "  ✅ Config-only backup created"
fi

# ── Step 4: Monthly snapshot ───────────────────────────────────────────────────
log "Step 4: Monthly snapshot check..."
if [[ "$DRY_RUN" == false && -n "$ARCHIVE_PATH" ]]; then
  MONTH_TAG=$(date '+%Y-%m')
  MONTHLY_FILE="$ICLOUD_BACKUP_DIR/monthly-${MONTH_TAG}-openclaw-backup.tar.gz"
  if [[ ! -f "$MONTHLY_FILE" && ! -f "${MONTHLY_FILE}.gpg" ]]; then
    cp "$ARCHIVE_PATH" "$MONTHLY_FILE" 2>/dev/null || true
    # Encrypt monthly too
    bash "$SCRIPT_DIR/backup-encrypt.sh" "$MONTHLY_FILE" 2>/dev/null && \
      log "  ✅ Monthly snapshot created & encrypted: monthly-${MONTH_TAG}" || \
      log "  ✅ Monthly snapshot created: monthly-${MONTH_TAG}"
  else
    log "  Monthly snapshot for ${MONTH_TAG} already exists — skipping"
  fi
  # Rotate monthly snapshots older than 90 days
  find "$ICLOUD_BACKUP_DIR" -name "monthly-*-openclaw-backup.tar.gz*" -mtime +90 -delete 2>/dev/null || true
elif [[ "$DRY_RUN" == true ]]; then
  log "  Would create monthly-$(date '+%Y-%m') snapshot if not already present"
fi

# ── Step 5: Rotate old iCloud daily backups ────────────────────────────────────
log "Step 5: Rotating old iCloud daily backups (keep ${KEEP_ICLOUD} days)..."
if [[ "$DRY_RUN" == false ]]; then
  find "$ICLOUD_BACKUP_DIR" -name "[0-9]*-openclaw-backup.tar.gz*" -mtime +${KEEP_ICLOUD} -delete 2>/dev/null || true
  ICLOUD_COUNT=$(ls "$ICLOUD_BACKUP_DIR"/[0-9]*-openclaw-backup.tar.gz* 2>/dev/null | wc -l | tr -d ' ')
  log "  iCloud daily backups retained: $ICLOUD_COUNT"
fi

# ── Done ───────────────────────────────────────────────────────────────────────
log "✅ Backup complete!"

if [[ "$DRY_RUN" == false ]]; then
  MSG="✅ *OpenClaw Backup Complete*
📦 \`$ARCHIVE_NAME\` (encrypted)
💾 Size: $ARCHIVE_SIZE
🔒 GPG AES-256 encrypted
☁️ iCloud: syncing
📁 iCloud copies: $ICLOUD_COUNT
🗓 $(date '+%Y-%m-%d %H:%M EDT')"
  telegram_notify "$MSG"
  echo ""
  echo "Archive: ${ARCHIVE_PATH}.gpg"
fi
