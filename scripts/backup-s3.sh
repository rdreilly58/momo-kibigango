#!/usr/bin/env bash
# backup-s3.sh — Upload config-only backup to S3 for off-site redundancy
# Uses existing AWS credentials. Config-only backups are ~10KB each.
#
# Usage: bash scripts/backup-s3.sh [--dry-run]
#
# NOTE: Requires S3 bucket setup. Run once:
#   aws s3 mb s3://momotaro-openclaw-backups --region us-east-1
#   aws s3api put-bucket-versioning --bucket momotaro-openclaw-backups \
#     --versioning-configuration Status=Enabled

set -euo pipefail
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

S3_BUCKET="momotaro-openclaw-backups"
S3_PREFIX="config"
KEEP_S3_OBJECTS=30
TMP_DIR="/tmp/openclaw-s3-backup-$$"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

DRY_RUN=false
for arg in "$@"; do
  [[ "$arg" == "--dry-run" ]] && DRY_RUN=true
done

log() { echo "[$(date '+%H:%M:%S')] $*"; }

cleanup() { rm -rf "$TMP_DIR"; }
trap cleanup EXIT

mkdir -p "$TMP_DIR"

# ── Check AWS CLI ──────────────────────────────────────────────────────────────
if ! command -v aws &>/dev/null; then
  log "❌ AWS CLI not found. Install with: brew install awscli"
  exit 1
fi

# ── Check S3 bucket ────────────────────────────────────────────────────────────
log "Checking S3 bucket: s3://${S3_BUCKET}..."
if ! aws s3 ls "s3://${S3_BUCKET}/" &>/dev/null; then
  log "⚠️ Bucket s3://${S3_BUCKET} not accessible."
  log "   Create it with: aws s3 mb s3://${S3_BUCKET} --region us-east-1"
  log "   Needs S3 bucket setup — exiting."
  exit 1
fi

# ── Create config-only backup ──────────────────────────────────────────────────
log "Creating config-only backup..."
if [[ "$DRY_RUN" == true ]]; then
  log "  [DRY RUN] Would run: openclaw backup create --only-config --output $TMP_DIR"
else
  openclaw backup create --only-config --output "$TMP_DIR" 2>&1 || {
    log "❌ Failed to create config backup"
    exit 1
  }
fi

# ── Find the archive ───────────────────────────────────────────────────────────
ARCHIVE=$(ls -t "$TMP_DIR"/*.tar.gz 2>/dev/null | head -1 || true)
if [[ -z "$ARCHIVE" && "$DRY_RUN" == false ]]; then
  log "❌ No archive found in $TMP_DIR"
  exit 1
fi
[[ "$DRY_RUN" == true ]] && ARCHIVE="$TMP_DIR/YYYY-MM-DD-openclaw-config-backup.tar.gz (simulated)"
log "  Archive: $ARCHIVE"

# ── Encrypt ────────────────────────────────────────────────────────────────────
log "Encrypting..."
if [[ "$DRY_RUN" == true ]]; then
  log "  [DRY RUN] Would run: bash $SCRIPT_DIR/backup-encrypt.sh $ARCHIVE"
  ENCRYPTED="${ARCHIVE}.gpg"
else
  bash "$SCRIPT_DIR/backup-encrypt.sh" "$ARCHIVE"
  ENCRYPTED="${ARCHIVE}.gpg"
  [[ ! -f "$ENCRYPTED" ]] && { log "❌ Encrypted file not found"; exit 1; }
fi

# ── Upload to S3 ───────────────────────────────────────────────────────────────
S3_KEY="${S3_PREFIX}/$(basename "$ENCRYPTED")"
log "Uploading to s3://${S3_BUCKET}/${S3_KEY}..."
if [[ "$DRY_RUN" == true ]]; then
  log "  [DRY RUN] Would run: aws s3 cp $ENCRYPTED s3://${S3_BUCKET}/${S3_KEY}"
else
  aws s3 cp "$ENCRYPTED" "s3://${S3_BUCKET}/${S3_KEY}" && log "  ✅ Uploaded"
fi

# ── Rotate old S3 objects (keep last 30) ──────────────────────────────────────
log "Rotating old S3 objects (keep ${KEEP_S3_OBJECTS})..."
if [[ "$DRY_RUN" == true ]]; then
  log "  [DRY RUN] Would list s3://${S3_BUCKET}/${S3_PREFIX}/ and delete objects beyond ${KEEP_S3_OBJECTS}"
else
  # Get sorted list (oldest first), delete those beyond KEEP limit
  OBJECTS=$(aws s3 ls "s3://${S3_BUCKET}/${S3_PREFIX}/" --recursive \
    | sort \
    | awk '{print $4}' \
    | head -n -${KEEP_S3_OBJECTS})
  if [[ -n "$OBJECTS" ]]; then
    while IFS= read -r obj; do
      aws s3 rm "s3://${S3_BUCKET}/$obj" && log "  Deleted old: $obj" || true
    done <<< "$OBJECTS"
  else
    log "  No old objects to delete"
  fi
fi

log "✅ S3 backup complete"
