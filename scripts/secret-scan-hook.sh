#!/bin/bash
# secret-scan-hook.sh — PreToolUse credential/secret detection guard
#
# Registered as a PreToolUse hook (matcher: Bash|Write) in ~/.claude/settings.json
# Fires before Bash and Write tool calls. Blocks execution if credential patterns
# are detected in the command or file content.
#
# Why: Autonomous cron agents and direct tool calls can accidentally write or
# execute commands containing secrets. This is the last line of defense before
# credentials reach a terminal or file.
#
# Detection targets:
#   - AWS access keys (AKIA...)
#   - PEM/private key blocks (-----BEGIN ... KEY-----)
#   - High-entropy credential assignments (password=, secret=, api_key=, token=)
#
# Block protocol: exit 1 + JSON {"decision":"block","reason":"..."} to stdout
# Pass protocol:  exit 0 (no output required)
#
# NEVER crashes loudly on internal errors — defaults to pass on exception.

LOG_DIR="${OPENCLAW_TEST_LOG_DIR:-$HOME/.openclaw/logs}"
LOG_FILE="$LOG_DIR/secret-scan.log"

mkdir -p "$LOG_DIR"

_log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] [secret-scan] $*" >> "$LOG_FILE" 2>/dev/null || true
}

_block() {
  local reason="$1"
  _log "BLOCKED: $reason"
  printf '{"decision":"block","reason":"%s — review before proceeding"}' "$reason"
  exit 1
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

# ── 2. Extract scannable content ──────────────────────────────────────────────
RESULT=$(echo "$STDIN_DATA" | python3 - <<'PYEOF'
import sys, json, re

try:
    raw = sys.stdin.read()
    d = json.loads(raw)
    inp = d.get('tool_input', {})
    # Bash: command field; Write: content + file_path
    parts = [
        inp.get('command', ''),
        inp.get('content', ''),
        inp.get('file_path', ''),
    ]
    text = '\n'.join(p for p in parts if p)

    issues = []

    # AWS access key
    if re.search(r'AKIA[0-9A-Z]{16}', text):
        issues.append('AWS access key (AKIA...)')

    # PEM blocks
    if '-----BEGIN' in text and 'KEY' in text:
        issues.append('PEM private key block')

    # High-entropy credential assignments
    cred_pattern = re.compile(
        r'(?i)(?:password|passwd|secret|api_key|apikey|auth_token|access_token)'
        r'\s*[=:]\s*["\x27]([A-Za-z0-9+/=_\-]{20,})["\x27]'
    )
    if cred_pattern.search(text):
        issues.append('credential assignment')

    if issues:
        print('BLOCK:' + ', '.join(issues), end='')
    else:
        print('PASS', end='')

except Exception as e:
    # On any error, default to pass — don't block legitimate work
    print('PASS', end='')
PYEOF
)

_log "Scan result: $RESULT"

if [[ "$RESULT" == BLOCK:* ]]; then
  REASON="${RESULT#BLOCK:}"
  _block "$REASON"
fi

exit 0
