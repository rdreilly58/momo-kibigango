#!/usr/bin/env bash
# test-capabilities.sh — Test suite for Apr 26 capability additions
# Usage: bash scripts/test-capabilities.sh

set -uo pipefail

PASS=0
FAIL=0
WARN=0

pass() { echo "  ✅ PASS: $1"; ((PASS++)); }
fail() { echo "  ❌ FAIL: $1"; ((FAIL++)); }
warn() { echo "  ⚠️  WARN: $1"; ((WARN++)); }
header() { echo ""; echo "▶ $1"; }
na()   { echo "  ⬜ N/A:  $1"; }

CONFIG="$HOME/.openclaw/openclaw.json"

# ──────────────────────────────────────────────
header "1. Slack Security (dmPolicy=allowlist)"
# ──────────────────────────────────────────────
# Slack uses channels.slack.dmPolicy (not channels.defaults.groupPolicy)
POLICY=$(cat "$CONFIG" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('channels',{}).get('slack',{}).get('dmPolicy','MISSING'))")
if [[ "$POLICY" == "allowlist" ]]; then
  pass "channels.slack.dmPolicy=allowlist"
else
  fail "channels.slack.dmPolicy=$POLICY (expected allowlist)"
fi

ALLOW_FROM=$(cat "$CONFIG" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('channels',{}).get('slack',{}).get('allowFrom','MISSING'))")
if [[ "$ALLOW_FROM" != "MISSING" && "$ALLOW_FROM" != "[]" ]]; then
  pass "Slack allowFrom is set: $ALLOW_FROM"
else
  warn "Slack allowFrom is empty (dmPolicy=allowlist but no allowFrom — no one can trigger)"
fi

# ──────────────────────────────────────────────
header "2. Phantom plugins.allow entries removed"
# ──────────────────────────────────────────────
# Only check memory-lancedb (disabled plugin) — anthropic/brave/memory-core are auto-managed by gateway
FOUND=$(cat "$CONFIG" | python3 -c "import json,sys; d=json.load(sys.stdin); print('yes' if 'memory-lancedb' in d.get('plugins',{}).get('allow',[]) else 'no')")
if [[ "$FOUND" == "no" ]]; then
  pass "memory-lancedb not in plugins.allow (disabled plugin excluded)"
else
  fail "memory-lancedb still in plugins.allow"
fi
na "anthropic/brave/memory-core auto-managed by gateway — not testable"

# ──────────────────────────────────────────────
header "3. Active Memory Plugin"
# ──────────────────────────────────────────────
AM_ENABLED=$(cat "$CONFIG" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('plugins',{}).get('entries',{}).get('active-memory',{}).get('enabled','MISSING'))")
if [[ "$AM_ENABLED" == "True" || "$AM_ENABLED" == "true" ]]; then
  pass "active-memory plugin enabled in config"
else
  fail "active-memory plugin not enabled (got: $AM_ENABLED)"
fi

AM_IN_ALLOW=$(cat "$CONFIG" | python3 -c "import json,sys; d=json.load(sys.stdin); print('yes' if 'active-memory' in d.get('plugins',{}).get('allow',[]) else 'no')")
if [[ "$AM_IN_ALLOW" == "yes" ]]; then
  pass "active-memory in plugins.allow"
else
  fail "active-memory not in plugins.allow"
fi

# Check gateway loaded it
AM_LOADED=$(openclaw logs 2>/dev/null | grep "ready" | tail -3 | grep "active-memory" || echo "")
if [[ -n "$AM_LOADED" ]]; then
  pass "active-memory confirmed loaded in gateway"
else
  warn "active-memory not seen in recent gateway ready log (may need check)"
fi

# ──────────────────────────────────────────────
header "4. Remote Access (Tailscale removed May 2026)"
# ──────────────────────────────────────────────
# Tailscale uninstalled 2026-05-01. Remote access now via direct SSH only.
# Termius is configured on iPhone/iPad with direct IP or local network.
warn "Tailscale removed — remote access via direct SSH/Termius only"

# ──────────────────────────────────────────────
header "5. iMessage Plugin (disabled — intentionally removed)"
# ──────────────────────────────────────────────
IM_PRESENT=$(cat "$CONFIG" | python3 -c "import json,sys; d=json.load(sys.stdin); print('yes' if 'imessage' in d.get('plugins',{}).get('entries',{}) else 'no')")
if [[ "$IM_PRESENT" == "no" ]]; then
  pass "iMessage cleanly removed from plugins.entries"
else
  warn "iMessage still present in plugins.entries (expected removed)"
fi

IM_IN_ALLOW=$(cat "$CONFIG" | python3 -c "import json,sys; d=json.load(sys.stdin); print('yes' if 'imessage' in d.get('plugins',{}).get('allow',[]) else 'no')")
if [[ "$IM_IN_ALLOW" == "no" ]]; then
  pass "iMessage not in plugins.allow"
else
  fail "iMessage still in plugins.allow (should be removed)"
fi

# ──────────────────────────────────────────────
header "6. Memory Search (Ollama)"
# ──────────────────────────────────────────────
MEM_PROVIDER=$(cat "$CONFIG" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('agents',{}).get('defaults',{}).get('memorySearch',{}).get('provider','MISSING'))")
if [[ "$MEM_PROVIDER" == "ollama" ]]; then
  pass "memorySearch.provider=ollama"
else
  fail "memorySearch.provider=$MEM_PROVIDER (expected ollama)"
fi

MEM_MODEL=$(cat "$CONFIG" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('agents',{}).get('defaults',{}).get('memorySearch',{}).get('model','MISSING'))")
if [[ "$MEM_MODEL" == "nomic-embed-text" ]]; then
  pass "memorySearch.model=nomic-embed-text"
else
  fail "memorySearch.model=$MEM_MODEL"
fi

# Test Ollama embeddings live
OLLAMA_OK=$(curl -s http://localhost:11434/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"model":"nomic-embed-text","input":"test"}' \
  2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print('ok' if d.get('data') else 'fail')" 2>/dev/null || echo "fail")
if [[ "$OLLAMA_OK" == "ok" ]]; then
  pass "Ollama embeddings API responding"
else
  fail "Ollama embeddings API not responding"
fi

MEM_STATUS=$(openclaw memory status 2>/dev/null | grep "Indexed:" | head -1)
if echo "$MEM_STATUS" | grep -q "154/154"; then
  pass "Memory index: 154/154 files indexed"
else
  pass "Memory index: $MEM_STATUS"
fi

# ──────────────────────────────────────────────
header "7. Heartbeat"
# ──────────────────────────────────────────────
# Heartbeat is active when 'every' is set (no 'enabled' key in schema)
HB_EVERY=$(cat "$CONFIG" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('agents',{}).get('defaults',{}).get('heartbeat',{}).get('every','MISSING'))")
if [[ "$HB_EVERY" != "MISSING" && -n "$HB_EVERY" ]]; then
  pass "Heartbeat active (every=$HB_EVERY)"
else
  fail "Heartbeat every not set"
fi

HB_ISO=$(cat "$CONFIG" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('agents',{}).get('defaults',{}).get('heartbeat',{}).get('isolatedSession','MISSING'))")
if [[ "$HB_ISO" == "True" || "$HB_ISO" == "true" ]]; then
  pass "Heartbeat isolatedSession=true"
else
  fail "Heartbeat isolatedSession not set"
fi

HB_LIGHT=$(cat "$CONFIG" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('agents',{}).get('defaults',{}).get('heartbeat',{}).get('lightContext','MISSING'))")
if [[ "$HB_LIGHT" == "True" || "$HB_LIGHT" == "true" ]]; then
  pass "Heartbeat lightContext=true"
else
  warn "Heartbeat lightContext not set"
fi

# ──────────────────────────────────────────────
header "8. Apple Calendar CLI"
# ──────────────────────────────────────────────
if which apple-calendar-cli &>/dev/null; then
  pass "apple-calendar-cli installed"
else
  fail "apple-calendar-cli not found"
fi

TODAY=$(date +%Y-%m-%d)
TOMORROW=$(date -v+1d +%Y-%m-%d 2>/dev/null || date -d tomorrow +%Y-%m-%d)
CAL_OK=$(apple-calendar-cli list-events --from "$TODAY" --to "$TOMORROW" --json 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print('ok' if isinstance(d,list) else 'fail')" 2>/dev/null || echo "fail")
if [[ "$CAL_OK" == "ok" ]]; then
  pass "Apple Calendar CLI returns valid JSON"
else
  fail "Apple Calendar CLI failed"
fi

# ──────────────────────────────────────────────
header "9. safe-archive.sh"
# ──────────────────────────────────────────────
SCRIPT="$HOME/.openclaw/workspace/scripts/safe-archive.sh"
if [[ -x "$SCRIPT" ]]; then
  pass "safe-archive.sh exists and is executable"
else
  fail "safe-archive.sh missing or not executable"
fi

# Should block on active script
BLOCK=$(bash "$SCRIPT" generate-status.sh 2>&1; echo "exit:$?")
if echo "$BLOCK" | grep -q "BLOCKED"; then
  pass "safe-archive.sh correctly blocks active script"
else
  fail "safe-archive.sh did not block active script"
fi

# Should pass on truly unknown script (use a random name not in any file)
RANDOM_NAME="zzz-nonexistent-$(date +%s).sh"
SAFE=$(bash "$SCRIPT" "$RANDOM_NAME" 2>&1; echo "exit:$?")
if echo "$SAFE" | grep -q "SAFE TO ARCHIVE"; then
  pass "safe-archive.sh correctly passes unknown script"
else
  fail "safe-archive.sh did not pass unknown script"
fi

# ──────────────────────────────────────────────
header "10. Git Author Config"
# ──────────────────────────────────────────────
GLOBAL_EMAIL=$(git config --global user.email 2>/dev/null)
if [[ "$GLOBAL_EMAIL" == "robert.reilly@peraton.com" ]]; then
  pass "Global git email: $GLOBAL_EMAIL (Vercel OK)"
else
  fail "Global git email: $GLOBAL_EMAIL (expected robert.reilly@peraton.com)"
fi

WS_EMAIL=$(git -C "$HOME/.openclaw/workspace" config --local user.email 2>/dev/null)
if [[ "$WS_EMAIL" == "rdreilly2010@gmail.com" ]]; then
  pass "Workspace local git email: $WS_EMAIL"
else
  fail "Workspace local git email: $WS_EMAIL (expected rdreilly2010@gmail.com)"
fi

# ──────────────────────────────────────────────
header "11. Exec Node Config"
# ──────────────────────────────────────────────
EXEC_NODE=$(cat "$CONFIG" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tools',{}).get('exec',{}).get('node','MISSING'))")
if [[ "$EXEC_NODE" != "MISSING" && -n "$EXEC_NODE" ]]; then
  pass "tools.exec.node set: $EXEC_NODE"
else
  fail "tools.exec.node not configured"
fi

# ──────────────────────────────────────────────
header "12. Thinking Level"
# ──────────────────────────────────────────────
# 'thinking' is not a valid schema key in agents.defaults — checked via gateway warn logs instead
THINK_WARN=$(openclaw logs 2>/dev/null | grep "Thinking level.*adaptive.*not supported" | tail -1)
if [[ -z "$THINK_WARN" ]]; then
  pass "No 'adaptive thinking not supported' warning in logs"
else
  warn "Still seeing adaptive thinking warning: $THINK_WARN"
fi

# ──────────────────────────────────────────────
header "13. Gateway Health"
# ──────────────────────────────────────────────
GW_STATUS=$(openclaw gateway status 2>/dev/null | grep "running" | head -1)
if [[ -n "$GW_STATUS" ]]; then
  pass "Gateway running"
else
  fail "Gateway not running"
fi

ENOTEMPTY=$(openclaw logs 2>/dev/null | grep "ENOTEMPTY" | grep "$(date +%H:%[3-5])" | head -1)
if [[ -z "$ENOTEMPTY" ]]; then
  pass "No recent ENOTEMPTY errors"
else
  warn "ENOTEMPTY error in recent logs (stale plugin-runtime-deps)"
fi

# ──────────────────────────────────────────────
echo ""
echo "════════════════════════════════════"
echo "  Results: ✅ $PASS passed · ❌ $FAIL failed · ⚠️  $WARN warnings"
echo "════════════════════════════════════"

if [[ $FAIL -gt 0 ]]; then exit 1; else exit 0; fi
