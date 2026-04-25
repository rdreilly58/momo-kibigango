#!/usr/bin/env bash
# transcribe_telegram_ogg.sh [path.ogg]
# Transcribes a Telegram voice note using yap CLI (Speech.framework)
# Usage: transcribe_telegram_ogg.sh [path.ogg]
# If no path given, uses the most recent .ogg in ~/.openclaw/media/inbound/

set -euo pipefail

OGG="${1:-}"

if [[ -z "$OGG" ]]; then
  OGG="$(ls -t ~/.openclaw/media/inbound/*.ogg 2>/dev/null | head -1 || true)"
fi

if [[ -z "$OGG" || ! -f "$OGG" ]]; then
  echo "Error: no .ogg file found" >&2
  exit 1
fi

LOCALE="${YAP_LOCALE:-$(defaults read -g AppleLocale 2>/dev/null || echo 'en-US')}"

yap transcribe --locale "$LOCALE" "$OGG"
