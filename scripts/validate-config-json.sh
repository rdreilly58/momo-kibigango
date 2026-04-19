#!/bin/bash
# validate-config-json.sh — JSON syntax guard for ~/.openclaw/config.json
#
# Validates that a file is valid JSON before it gets used.
# Exit 0 = valid. Exit 1 = invalid (prints error with position).
#
# Usage:
#   validate-config-json.sh                          # validate config.json
#   validate-config-json.sh /path/to/file.json       # validate any JSON file
#   validate-config-json.sh --help

set -uo pipefail

TARGET="${1:-$HOME/.openclaw/config.json}"

if [ "${TARGET}" = "--help" ] || [ "${TARGET}" = "-h" ]; then
  cat <<'EOF'
Usage: validate-config-json.sh [file]

Validates a JSON file. Defaults to ~/.openclaw/config.json.

Examples:
  validate-config-json.sh                       # check config.json
  validate-config-json.sh /tmp/new-config.json  # check before applying
  validate-config-json.sh - < /tmp/config.json  # check from stdin

Exit codes:
  0  Valid JSON
  1  Parse error (position printed)
  2  File not found
EOF
  exit 0
fi

# Stdin mode
if [ "${TARGET}" = "-" ]; then
  python3 -c "
import json, sys
try:
    json.load(sys.stdin)
    print('✅ Valid JSON')
    sys.exit(0)
except json.JSONDecodeError as e:
    print(f'❌ JSON parse error: {e}', file=sys.stderr)
    sys.exit(1)
"
  exit $?
fi

if [ ! -f "$TARGET" ]; then
  echo "❌ File not found: $TARGET" >&2
  exit 2
fi

python3 -c "
import json, sys

path = sys.argv[1]
try:
    with open(path) as f:
        raw = f.read()
    json.loads(raw)
    size_kb = len(raw) / 1024
    print(f'✅ Valid JSON ({size_kb:.1f} KB): {path}')
    sys.exit(0)
except json.JSONDecodeError as e:
    # Show context around the error
    lines = raw.splitlines()
    lineno = e.lineno - 1
    col = e.colno - 1
    print(f'❌ JSON parse error in {path}', file=sys.stderr)
    print(f'   Line {e.lineno}, col {e.colno}: {e.msg}', file=sys.stderr)
    if 0 <= lineno < len(lines):
        print(f'', file=sys.stderr)
        if lineno > 0:
            print(f'   {lineno:4d}: {lines[lineno-1]}', file=sys.stderr)
        print(f'   {e.lineno:4d}: {lines[lineno]}', file=sys.stderr)
        print(f'         {\" \" * col}^ here', file=sys.stderr)
    sys.exit(1)
except PermissionError:
    print(f'❌ Permission denied: {path}', file=sys.stderr)
    sys.exit(1)
" "$TARGET"
