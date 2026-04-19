#!/bin/bash
# safe-config-write.sh — Atomic JSON-validated write for config.json
#
# Validates JSON BEFORE touching the live file. Creates a timestamped backup.
# Use this instead of direct writes to ~/.openclaw/config.json.
#
# Usage:
#   safe-config-write.sh < new-config.json          # write from stdin
#   safe-config-write.sh /tmp/new-config.json       # write from file
#   safe-config-write.sh /tmp/new.json --target /path/to/other.json

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VALIDATE="$SCRIPT_DIR/validate-config-json.sh"

# Parse args
SOURCE_FILE=""
TARGET_FILE="$HOME/.openclaw/config.json"
STDIN_MODE=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target) TARGET_FILE="$2"; shift 2 ;;
    --help|-h)
      cat <<'EOF'
Usage: safe-config-write.sh [source_file] [--target path]

Writes new content to ~/.openclaw/config.json (or --target path) with:
  1. JSON validation (aborts on parse error)
  2. Timestamped backup of the current file
  3. Atomic write (temp file → mv)

Examples:
  cat edited.json | safe-config-write.sh            # stdin
  safe-config-write.sh /tmp/new-config.json         # from file
  safe-config-write.sh /tmp/foo.json --target ~/.openclaw/openclaw.json
EOF
      exit 0 ;;
    -*) echo "Unknown option: $1" >&2; exit 1 ;;
    *) SOURCE_FILE="$1"; shift ;;
  esac
done

# Determine input: file or stdin
if [ -z "$SOURCE_FILE" ]; then
  STDIN_MODE=true
  TMP_INPUT=$(mktemp /tmp/config-write-input.XXXXXX.json)
  trap 'rm -f "$TMP_INPUT"' EXIT
  cat > "$TMP_INPUT"
  SOURCE_FILE="$TMP_INPUT"
fi

if [ ! -f "$SOURCE_FILE" ]; then
  echo "❌ Source file not found: $SOURCE_FILE" >&2
  exit 1
fi

# Step 1: Validate JSON
echo "🔍 Validating JSON..."
if ! bash "$VALIDATE" "$SOURCE_FILE"; then
  echo "" >&2
  echo "❌ Write ABORTED — fix JSON errors before saving to $TARGET_FILE" >&2
  exit 1
fi

# Step 2: Backup existing file
if [ -f "$TARGET_FILE" ]; then
  BACKUP="${TARGET_FILE}.backup-$(date +%s)"
  cp "$TARGET_FILE" "$BACKUP"
  echo "💾 Backed up: $BACKUP"
fi

# Step 3: Atomic write (write to tmp alongside target, then mv)
TARGET_DIR="$(dirname "$TARGET_FILE")"
TMP_OUT=$(mktemp "$TARGET_DIR/.config-write-tmp.XXXXXX")
trap 'rm -f "$TMP_OUT" "${TMP_INPUT:-}"' EXIT

# Pretty-print for readability (optional: swap with cp if you want exact bytes)
python3 -c "
import json, sys
with open(sys.argv[1]) as f:
    data = json.load(f)
with open(sys.argv[2], 'w') as f:
    json.dump(data, f, indent=2)
    f.write('\n')
" "$SOURCE_FILE" "$TMP_OUT"

mv "$TMP_OUT" "$TARGET_FILE"
echo "✅ Written: $TARGET_FILE"
