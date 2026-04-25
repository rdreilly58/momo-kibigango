#!/bin/bash
# test_subagents.sh — Validate subagent definitions + related infrastructure
# Tests: YAML frontmatter, file integrity, settings.json wiring, cron, hook
#
# Usage: bash scripts/tests/test_subagents.sh

PASS=0
FAIL=0
AGENTS_DIR="$HOME/.claude/agents"
SETTINGS="$HOME/.claude/settings.json"
WORKSPACE="$HOME/.openclaw/workspace"

_pass() { ((PASS++)); echo "  ✅ $1"; }
_fail() { ((FAIL++)); echo "  ❌ $1"; }

echo "═══════════════════════════════════════════════"
echo " Subagent & Infrastructure Test Suite"
echo " $(date '+%Y-%m-%d %H:%M:%S')"
echo "═══════════════════════════════════════════════"
echo ""

# ─────────────────────────────────────────────────
# 1. Agent file existence
# ─────────────────────────────────────────────────
echo "▸ 1. Agent file existence"
for agent in ops code research memory; do
  if [ -f "$AGENTS_DIR/${agent}.md" ]; then
    _pass "${agent}.md exists"
  else
    _fail "${agent}.md missing"
  fi
done
echo ""

# ─────────────────────────────────────────────────
# 2. YAML frontmatter structure
# ─────────────────────────────────────────────────
echo "▸ 2. YAML frontmatter structure"
for agent in ops code research memory; do
  FILE="$AGENTS_DIR/${agent}.md"
  [ -f "$FILE" ] || continue

  # Check opens with ---
  if head -1 "$FILE" | grep -q '^---$'; then
    _pass "${agent}.md starts with ---"
  else
    _fail "${agent}.md missing opening ---"
  fi

  # Check closing ---
  if awk 'NR>1' "$FILE" | grep -q '^---$'; then
    _pass "${agent}.md has closing ---"
  else
    _fail "${agent}.md missing closing ---"
  fi

  # Required fields
  for field in name description model tools; do
    if grep -q "^${field}:" "$FILE"; then
      _pass "${agent}.md has ${field} field"
    else
      _fail "${agent}.md missing ${field} field"
    fi
  done
done
echo ""

# ─────────────────────────────────────────────────
# 3. Agent name matches filename
# ─────────────────────────────────────────────────
echo "▸ 3. Agent name matches filename"
for agent in ops code research memory; do
  FILE="$AGENTS_DIR/${agent}.md"
  [ -f "$FILE" ] || continue
  NAME_VAL=$(grep '^name:' "$FILE" | head -1 | sed 's/^name: *//')
  if [ "$NAME_VAL" = "$agent" ]; then
    _pass "${agent}.md name field matches filename"
  else
    _fail "${agent}.md name='$NAME_VAL' doesn't match filename '$agent'"
  fi
done
echo ""

# ─────────────────────────────────────────────────
# 4. Model field is valid
# ─────────────────────────────────────────────────
echo "▸ 4. Model field validation"
for agent in ops code research memory; do
  FILE="$AGENTS_DIR/${agent}.md"
  [ -f "$FILE" ] || continue
  MODEL=$(grep '^model:' "$FILE" | head -1 | sed 's/^model: *//')
  case "$MODEL" in
    opus|sonnet|haiku)
      _pass "${agent}.md model='$MODEL' is valid"
      ;;
    *)
      _fail "${agent}.md model='$MODEL' — expected opus|sonnet|haiku"
      ;;
  esac
done
echo ""

# ─────────────────────────────────────────────────
# 5. Tools field not empty
# ─────────────────────────────────────────────────
echo "▸ 5. Tools field validation"
for agent in ops code research memory; do
  FILE="$AGENTS_DIR/${agent}.md"
  [ -f "$FILE" ] || continue
  TOOLS=$(grep '^tools:' "$FILE" | head -1 | sed 's/^tools: *//')
  if [ -n "$TOOLS" ] && [ ${#TOOLS} -gt 3 ]; then
    _pass "${agent}.md tools='$TOOLS'"
  else
    _fail "${agent}.md tools field empty or too short"
  fi
done
echo ""

# ─────────────────────────────────────────────────
# 6. Description length (should be meaningful)
# ─────────────────────────────────────────────────
echo "▸ 6. Description quality"
for agent in ops code research memory; do
  FILE="$AGENTS_DIR/${agent}.md"
  [ -f "$FILE" ] || continue
  DESC=$(grep '^description:' "$FILE" | head -1 | sed 's/^description: *//')
  DESC_LEN=${#DESC}
  if [ "$DESC_LEN" -ge 20 ]; then
    _pass "${agent}.md description length=$DESC_LEN (>= 20)"
  else
    _fail "${agent}.md description too short ($DESC_LEN chars)"
  fi
done
echo ""

# ─────────────────────────────────────────────────
# 7. Body content exists (below frontmatter)
# ─────────────────────────────────────────────────
echo "▸ 7. Body content exists"
for agent in ops code research memory; do
  FILE="$AGENTS_DIR/${agent}.md"
  [ -f "$FILE" ] || continue
  # Count lines after second ---
  BODY_LINES=$(awk 'BEGIN{n=0} /^---$/{n++; next} n>=2{print}' "$FILE" | wc -l | tr -d ' ')
  if [ "$BODY_LINES" -ge 5 ]; then
    _pass "${agent}.md has $BODY_LINES body lines"
  else
    _fail "${agent}.md body too short ($BODY_LINES lines)"
  fi
done
echo ""

# ─────────────────────────────────────────────────
# 8. No secrets in agent files
# ─────────────────────────────────────────────────
echo "▸ 8. No secrets in agent files"
for agent in ops code research memory; do
  FILE="$AGENTS_DIR/${agent}.md"
  [ -f "$FILE" ] || continue
  if perl -ne 'exit 1 if /(?:API_KEY|SECRET|PASSWORD|TOKEN)\s*[:=]\s*\S{8,}/' "$FILE" 2>/dev/null; then
    _pass "${agent}.md — no secrets detected"
  else
    _fail "${agent}.md — possible secret found!"
  fi
done
echo ""

# ─────────────────────────────────────────────────
# 9. Research agent is read-only (no Write/Edit tools)
# ─────────────────────────────────────────────────
echo "▸ 9. Research agent constraints"
FILE="$AGENTS_DIR/research.md"
if [ -f "$FILE" ]; then
  TOOLS=$(grep '^tools:' "$FILE" | head -1)
  if echo "$TOOLS" | grep -qiE 'Write|Edit'; then
    _fail "research.md has Write/Edit tools — should be read-only"
  else
    _pass "research.md is read-only (no Write/Edit)"
  fi
  if grep -qi "never.*edit\|never.*modif\|never.*creat" "$FILE"; then
    _pass "research.md body states read-only constraint"
  else
    _fail "research.md body should state read-only constraint"
  fi
fi
echo ""

# ─────────────────────────────────────────────────
# 10. BRAVE_API_KEY wiring
# ─────────────────────────────────────────────────
echo "▸ 10. BRAVE_API_KEY wiring"
if python3 -c "import json; d=json.load(open('$SETTINGS')); assert d.get('env',{}).get('BRAVE_API_KEY','')" 2>/dev/null; then
  _pass "BRAVE_API_KEY in settings.json env"
else
  _fail "BRAVE_API_KEY missing from settings.json env"
fi

if security find-generic-password -s "OpenclawBrave" -a "openclaw" -w >/dev/null 2>&1; then
  _pass "BRAVE_API_KEY in macOS Keychain"
else
  _fail "BRAVE_API_KEY missing from Keychain"
fi
echo ""

# ─────────────────────────────────────────────────
# 11. Test-runner hook in settings.json
# ─────────────────────────────────────────────────
echo "▸ 11. Test-runner hook"
if python3 -c "
import json
d = json.load(open('$SETTINGS'))
hooks = d.get('hooks', {}).get('PostToolUse', [])
found = any(
    'test-runner' in h.get('command', '')
    for entry in hooks
    for h in entry.get('hooks', [])
)
assert found
" 2>/dev/null; then
  _pass "test-runner-hook.sh wired in PostToolUse"
else
  _fail "test-runner-hook.sh NOT in PostToolUse hooks"
fi

if [ -x "$WORKSPACE/scripts/test-runner-hook.sh" ]; then
  _pass "test-runner-hook.sh is executable"
else
  _fail "test-runner-hook.sh not executable"
fi
echo ""

# ─────────────────────────────────────────────────
# 12. Cost tracking cron
# ─────────────────────────────────────────────────
echo "▸ 12. Cost tracking cron"
if crontab -l 2>/dev/null | grep -q "subagent-cost-report"; then
  _pass "subagent-cost-report.sh in crontab"
else
  _fail "subagent-cost-report.sh NOT in crontab"
fi

if [ -f "$WORKSPACE/scripts/subagent-cost-report.sh" ]; then
  _pass "subagent-cost-report.sh exists"
else
  _fail "subagent-cost-report.sh missing"
fi

if [ -f "$WORKSPACE/scripts/track-subagent-costs.sh" ]; then
  _pass "track-subagent-costs.sh exists"
else
  _fail "track-subagent-costs.sh missing"
fi
echo ""

# ─────────────────────────────────────────────────
# 13. Script archive integrity
# ─────────────────────────────────────────────────
echo "▸ 13. Script archive"
ARCHIVE_DIR="$WORKSPACE/scripts/_archive"
if [ -d "$ARCHIVE_DIR" ]; then
  ARCHIVE_COUNT=$(ls -1 "$ARCHIVE_DIR" 2>/dev/null | wc -l | tr -d ' ')
  _pass "_archive/ exists with $ARCHIVE_COUNT files"
else
  _fail "_archive/ directory missing"
fi

ACTIVE_COUNT=$(ls -1 "$WORKSPACE/scripts/"*.sh 2>/dev/null | wc -l | tr -d ' ')
if [ "$ACTIVE_COUNT" -lt 80 ]; then
  _pass "Active scripts reduced to $ACTIVE_COUNT (was 150+)"
else
  _fail "Still $ACTIVE_COUNT active scripts — expected < 80"
fi
echo ""

# ─────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────
TOTAL=$((PASS + FAIL))
echo "═══════════════════════════════════════════════"
echo " Results: $PASS/$TOTAL passed, $FAIL failed"
echo "═══════════════════════════════════════════════"

if [ "$FAIL" -eq 0 ]; then
  echo " 🎉 All tests passed!"
  exit 0
else
  echo " ⚠️  $FAIL test(s) failed — review above"
  exit 1
fi
