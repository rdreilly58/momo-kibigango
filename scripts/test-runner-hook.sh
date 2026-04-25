#!/bin/bash
# test-runner-hook.sh — PostToolUse test runner
#
# Registered as a PostToolUse hook (matcher: Write|Edit) in ~/.claude/settings.json
# Fires after code changes. Finds and runs relevant tests for the changed file.
#
# Strategy:
#   1. Extract file path from hook stdin JSON
#   2. Map file → project and test framework
#   3. Find closest matching test file(s)
#   4. Run tests (with timeout) and log results
#
# NEVER fails loudly — always exits 0.

WORKSPACE="${OPENCLAW_TEST_WORKSPACE:-$HOME/.openclaw/workspace}"
LOG_DIR="${OPENCLAW_TEST_LOG_DIR:-$HOME/.openclaw/logs}"
LOG_FILE="$LOG_DIR/test-runner.log"
VENV_PYTHON="$WORKSPACE/venv/bin/python3"
MAX_TEST_SECONDS=30

mkdir -p "$LOG_DIR"

_log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] [test-runner] $*" >> "$LOG_FILE" 2>/dev/null || true
}

# ── 1. Read stdin ────────────────────────────────────────────────────────────
STDIN_DATA=""
if read -t 2 -r STDIN_DATA 2>/dev/null; then
  while IFS= read -t 0.1 -r line 2>/dev/null; do
    STDIN_DATA="${STDIN_DATA}${line}"
  done
fi

if [ -z "$STDIN_DATA" ]; then
  exit 0
fi

# ── 2. Extract file path ────────────────────────────────────────────────────
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

if [ -z "$FILE_PATH" ] || [ ! -f "$FILE_PATH" ]; then
  exit 0
fi

_log "Changed file: $FILE_PATH"

# ── 3. Skip non-code files and test files themselves ─────────────────────────
case "$FILE_PATH" in
  *.py|*.js|*.ts|*.jsx|*.tsx|*.swift) ;;  # code — continue
  *) _log "Skipping non-code file"; exit 0 ;;
esac

# Don't re-run tests when editing test files (avoid loops)
case "$(basename "$FILE_PATH")" in
  test_*|*_test.*|*.test.*|*Tests.*|*Spec.*) _log "Skipping test file itself"; exit 0 ;;
esac

# Skip files in _archive, node_modules, venv
case "$FILE_PATH" in
  */_archive/*|*/node_modules/*|*/venv/*|*/.git/*) _log "Skipping excluded path"; exit 0 ;;
esac

# ── 4. Find relevant tests ──────────────────────────────────────────────────
BASENAME=$(basename "$FILE_PATH")
FILENAME="${BASENAME%.*}"
EXT="${BASENAME##*.}"
FILEDIR=$(dirname "$FILE_PATH")

find_test_file() {
  local dir="$1" name="$2" ext="$3"
  local candidates=()

  # Check common test locations relative to the file
  for test_dir in "$dir" "$dir/tests" "$dir/../tests" "$dir/../Tests" "$dir/../../Tests" "$dir/../../tests"; do
    [ -d "$test_dir" ] || continue
    for pattern in "test_${name}.${ext}" "${name}_test.${ext}" "${name}.test.${ext}" "${name}Tests.${ext}"; do
      local found=$(find "$test_dir" -maxdepth 1 -name "$pattern" 2>/dev/null | head -1)
      if [ -n "$found" ]; then
        echo "$found"
        return 0
      fi
    done
  done
  return 1
}

TEST_FILE=$(find_test_file "$FILEDIR" "$FILENAME" "$EXT")

if [ -z "$TEST_FILE" ]; then
  _log "No test file found for $FILENAME.$EXT"
  exit 0
fi

_log "Found test: $TEST_FILE"

# ── 5. Run tests ────────────────────────────────────────────────────────────
run_result=""
case "$EXT" in
  py)
    # Use workspace venv pytest, fall back to system
    PYTEST="$WORKSPACE/venv/bin/pytest"
    [ -x "$PYTEST" ] || PYTEST=$(which pytest 2>/dev/null || echo "")
    if [ -n "$PYTEST" ]; then
      run_result=$(timeout "$MAX_TEST_SECONDS" "$PYTEST" "$TEST_FILE" -x -q --tb=short 2>&1) || true
    else
      _log "No pytest found — skipping"
      exit 0
    fi
    ;;
  js|ts|jsx|tsx)
    # Detect project root (nearest package.json)
    PROJECT_ROOT="$FILEDIR"
    while [ "$PROJECT_ROOT" != "/" ] && [ ! -f "$PROJECT_ROOT/package.json" ]; do
      PROJECT_ROOT=$(dirname "$PROJECT_ROOT")
    done
    if [ -f "$PROJECT_ROOT/package.json" ]; then
      # Try npx jest, vitest, or npm test
      if [ -f "$PROJECT_ROOT/node_modules/.bin/jest" ]; then
        run_result=$(cd "$PROJECT_ROOT" && timeout "$MAX_TEST_SECONDS" npx jest "$TEST_FILE" --bail 2>&1) || true
      elif [ -f "$PROJECT_ROOT/node_modules/.bin/vitest" ]; then
        run_result=$(cd "$PROJECT_ROOT" && timeout "$MAX_TEST_SECONDS" npx vitest run "$TEST_FILE" 2>&1) || true
      else
        _log "No JS test runner found in $PROJECT_ROOT"
        exit 0
      fi
    fi
    ;;
  swift)
    _log "Swift tests require Xcode — skipping auto-run"
    exit 0
    ;;
esac

# ── 6. Log results ──────────────────────────────────────────────────────────
if [ -n "$run_result" ]; then
  # Check for failures
  if echo "$run_result" | grep -qiE "(FAILED|FAIL|ERROR|error)" 2>/dev/null; then
    _log "TESTS FAILED for $FILE_PATH:"
    echo "$run_result" | tail -20 >> "$LOG_FILE" 2>/dev/null || true
  else
    _log "Tests passed for $FILE_PATH"
  fi
fi

exit 0
