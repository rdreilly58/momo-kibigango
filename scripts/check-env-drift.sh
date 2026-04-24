#!/bin/bash
# check-env-drift.sh — Detect key mismatches between the two .env files
#
# Alerts if a key exists in one file but not the other, or if values differ.
# Cron: add to weekly quota monitor or run standalone.
# Usage: bash scripts/check-env-drift.sh

ENV_A="$HOME/.openclaw/.env"
ENV_B="$HOME/.openclaw/workspace/.env"

DRIFT=0

_extract_keys() {
  # Only check actual secrets (keys ending in _KEY, _TOKEN, _ID, _SECRET)
  # Skip model config vars like OBSERVER_MODEL, OBSERVER_FALLBACK_MODEL
  grep -E "^[A-Z_]+(_KEY|_TOKEN|_ID|_SECRET)=" "$1" 2>/dev/null | cut -d= -f1 | sort
}

_get_val() {
  grep "^${2}=" "$1" 2>/dev/null | head -1 | cut -d= -f2-
}

echo "Checking .env drift between:"
echo "  A: $ENV_A"
echo "  B: $ENV_B"
echo ""

KEYS_A=$(_extract_keys "$ENV_A")
KEYS_B=$(_extract_keys "$ENV_B")

# Keys in A but not B
while IFS= read -r key; do
  if ! echo "$KEYS_B" | grep -q "^${key}$"; then
    echo "⚠️  $key: in ~/.openclaw/.env but missing from workspace/.env"
    ((DRIFT++)) || true
  fi
done <<< "$KEYS_A"

# Keys in B but not A
while IFS= read -r key; do
  if ! echo "$KEYS_A" | grep -q "^${key}$"; then
    echo "⚠️  $key: in workspace/.env but missing from ~/.openclaw/.env"
    ((DRIFT++)) || true
  fi
done <<< "$KEYS_B"

# Keys in both — check value drift (compare masked first 8 chars)
ALL_KEYS=$(echo -e "$KEYS_A\n$KEYS_B" | sort -u)
while IFS= read -r key; do
  val_a=$(_get_val "$ENV_A" "$key")
  val_b=$(_get_val "$ENV_B" "$key")
  if [ -n "$val_a" ] && [ -n "$val_b" ] && [ "$val_a" != "$val_b" ]; then
    echo "❌  $key: VALUES DIFFER between the two files"
    ((DRIFT++)) || true
  fi
done <<< "$ALL_KEYS"

echo ""
if [ "$DRIFT" -eq 0 ]; then
  echo "✅ No drift detected — both .env files are in sync"
else
  echo "⚠️  $DRIFT drift issue(s) found"
  echo "   Fix: run bash scripts/load-secrets-from-keychain.sh --write-env"
  echo "   Then copy missing keys to workspace/.env"
  exit 1
fi
