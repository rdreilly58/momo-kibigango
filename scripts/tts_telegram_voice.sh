#!/usr/bin/env bash
# tts_telegram_voice.sh "<reply text>" [SYSTEM|VoiceName]
# Converts text to a Telegram-compatible OGG/Opus voice note.
# Prints the generated .ogg path to stdout.

set -euo pipefail

TEXT="${1:-}"
VOICE="${2:-SYSTEM}"

if [[ -z "$TEXT" ]]; then
  echo "Usage: tts_telegram_voice.sh '<text>' [SYSTEM|VoiceName]" >&2
  exit 1
fi

TMPDIR_BASE="${TMPDIR:-/tmp}"
AIFF="$(mktemp "${TMPDIR_BASE}/tts_XXXXXX").aiff"
OGG="$(mktemp "${TMPDIR_BASE}/tts_XXXXXX").ogg"

cleanup() { rm -f "$AIFF"; }
trap cleanup EXIT

if [[ "$VOICE" == "SYSTEM" ]]; then
  say "$TEXT" -o "$AIFF"
else
  say -v "$VOICE" "$TEXT" -o "$AIFF"
fi

ffmpeg -y -i "$AIFF" -c:a libopus -b:a 64k -vbr on -compression_level 10 "$OGG" 2>/dev/null

echo "$OGG"
