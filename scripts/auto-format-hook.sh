#!/bin/bash
# auto-format-hook.sh — PostToolUse code formatting
#
# Registered as a PostToolUse hook (matcher: Write|Edit) in ~/.claude/settings.json
# Fires after Write and Edit tool use. Runs ruff on .py files.
#
# Why: Claude generates well-formatted code but the last 10% (trailing whitespace,
# import order, line length) causes CI failures. Hook handles it automatically.
#
# NEVER fails loudly — tool output must not be affected by hook errors.
# Always exits 0.

WORKSPACE="${OPENCLAW_TEST_WORKSPACE:-$HOME/.openclaw/workspace}"
RUFF="$WORKSPACE/venv/bin/ruff"
LOG_DIR="${OPENCLAW_TEST_LOG_DIR:-$HOME/.openclaw/logs}"
LOG_FILE="$LOG_DIR/auto-format.log"

mkdir -p "$LOG_DIR"

_log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] [auto-format] $*" >> "$LOG_FILE" 2>/dev/null || true
}

# ── 1. Read stdin ─────────────────────────────────────────────────────────────
STDIN_DATA=""
if read -t 2 -r STDIN_DATA 2>/dev/null; then
  while IFS= read -t 0.1 -r line 2>/dev/null; do
    STDIN_DATA="${STDIN_DATA}${line}"
  done
fi

if [ -z "$STDIN_DATA" ]; then
  exit 0
fi

# ── 2. Extract file path from tool input ──────────────────────────────────────
FILE_PATH=$(echo "$STDIN_DATA" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    inp = d.get('tool_input', {})
    path = inp.get('file_path', inp.get('path', ''))
    print(path, end='')
except Exception:
    pass
" 2>/dev/null || true)

_log "Tool fired, file: ${FILE_PATH:-none}"

if [ -z "$FILE_PATH" ] || [ ! -f "$FILE_PATH" ]; then
  exit 0
fi

# ── 3. Format based on extension ─────────────────────────────────────────────
case "$FILE_PATH" in
  *.py)
    if [ -x "$RUFF" ]; then
      "$RUFF" format --quiet "$FILE_PATH" 2>/dev/null \
        && _log "Formatted (ruff): $FILE_PATH" \
        || _log "ruff format failed (non-fatal): $FILE_PATH"
    else
      _log "ruff not found at $RUFF — skipping"
    fi
    ;;
  *)
    _log "No formatter for extension: $FILE_PATH — skipping"
    ;;
esac

exit 0
