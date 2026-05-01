#!/usr/bin/env bash
# backup-encrypt.sh — Encrypt a backup archive with AES-256
# Passphrase stored in macOS Keychain under service "OpenClawBackupKey"
# Usage: bash backup-encrypt.sh <archive.tar.gz>
#
# On success: creates <archive>.gpg and removes the unencrypted original.
# Returns 0 on success, 1 on failure.

set -euo pipefail
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

KEYCHAIN_SERVICE="OpenClawBackupKey"
KEYCHAIN_ACCOUNT="momotaro"

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <archive.tar.gz>" >&2
  exit 1
fi

ARCHIVE="$1"

if [[ ! -f "$ARCHIVE" ]]; then
  echo "Error: archive not found: $ARCHIVE" >&2
  exit 1
fi

# ── Retrieve or generate passphrase ───────────────────────────────────────────
PASSPHRASE=$(security find-generic-password -s "$KEYCHAIN_SERVICE" -a "$KEYCHAIN_ACCOUNT" -w 2>/dev/null || true)

if [[ -z "$PASSPHRASE" ]]; then
  echo "[backup-encrypt] No keychain entry found — generating new passphrase..."
  PASSPHRASE=$(openssl rand -base64 48)
  security add-generic-password \
    -s "$KEYCHAIN_SERVICE" \
    -a "$KEYCHAIN_ACCOUNT" \
    -w "$PASSPHRASE" \
    -U \
    2>/dev/null || {
      echo "Error: failed to store passphrase in keychain" >&2
      exit 1
    }
  echo "[backup-encrypt] ✅ Passphrase stored in keychain: service=$KEYCHAIN_SERVICE account=$KEYCHAIN_ACCOUNT"
fi

# ── Encrypt ────────────────────────────────────────────────────────────────────
OUTPUT="${ARCHIVE}.gpg"
gpg --batch --yes \
    --symmetric \
    --cipher-algo AES256 \
    --passphrase-fd 0 \
    --output "$OUTPUT" \
    "$ARCHIVE" <<< "$PASSPHRASE"

if [[ $? -eq 0 && -f "$OUTPUT" ]]; then
  # Remove unencrypted original
  rm -f "$ARCHIVE"
  echo "[backup-encrypt] ✅ Encrypted: $OUTPUT"
  exit 0
else
  echo "[backup-encrypt] ❌ Encryption failed" >&2
  exit 1
fi
