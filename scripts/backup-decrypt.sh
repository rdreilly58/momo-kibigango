#!/usr/bin/env bash
# backup-decrypt.sh — Decrypt an encrypted OpenClaw backup archive
# Passphrase retrieved from macOS Keychain under service "OpenClawBackupKey"
# Usage: bash backup-decrypt.sh <archive.tar.gz.gpg> [output-dir]
#
# Produces: <archive.tar.gz> (removes .gpg extension)
# Returns 0 on success, 1 on failure.

set -euo pipefail
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

KEYCHAIN_SERVICE="OpenClawBackupKey"
KEYCHAIN_ACCOUNT="momotaro"

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <archive.tar.gz.gpg> [output-dir]" >&2
  exit 1
fi

ARCHIVE="$1"
OUTPUT_DIR="${2:-$(dirname "$ARCHIVE")}"

if [[ ! -f "$ARCHIVE" ]]; then
  echo "Error: encrypted archive not found: $ARCHIVE" >&2
  exit 1
fi

# Strip .gpg extension for output path
DECRYPTED_NAME=$(basename "${ARCHIVE%.gpg}")
OUTPUT="$OUTPUT_DIR/$DECRYPTED_NAME"

# ── Retrieve passphrase ────────────────────────────────────────────────────────
PASSPHRASE=$(security find-generic-password -s "$KEYCHAIN_SERVICE" -a "$KEYCHAIN_ACCOUNT" -w 2>/dev/null || true)

if [[ -z "$PASSPHRASE" ]]; then
  echo "Error: no passphrase found in keychain (service=$KEYCHAIN_SERVICE, account=$KEYCHAIN_ACCOUNT)" >&2
  echo "If restoring on a new Mac, you must manually set the passphrase first:" >&2
  echo "  security add-generic-password -s OpenClawBackupKey -a momotaro -w YOUR_PASSPHRASE" >&2
  exit 1
fi

# ── Decrypt ────────────────────────────────────────────────────────────────────
mkdir -p "$OUTPUT_DIR"
gpg --batch \
    --passphrase-fd 0 \
    --decrypt \
    --output "$OUTPUT" \
    "$ARCHIVE" <<< "$PASSPHRASE"

if [[ $? -eq 0 && -f "$OUTPUT" ]]; then
  echo "[backup-decrypt] ✅ Decrypted: $OUTPUT"
  exit 0
else
  echo "[backup-decrypt] ❌ Decryption failed" >&2
  exit 1
fi
