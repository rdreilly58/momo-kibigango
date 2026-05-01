#!/bin/bash
# agent-router.sh — Analyze a task and suggest the appropriate agent (and optionally the host)
#
# Usage:
#   agent=$(bash agent-router.sh "wire system health check to cron")
#   # → outputs: ops
#
#   bash agent-router.sh --explain "refactor memory search"
#   # → outputs agent name + reasoning
#
#   bash agent-router.sh --host "train ML model"
#   # → outputs: local  (or mac-aws, or skip)
#   # Calls host-router.sh with the derived task_type for that task.
#
#   bash agent-router.sh --host --explain "train ML model"
#   # → outputs: agent name + host decision + reasoning

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Parse flags
TASK=""
EXPLAIN=0
HOST_ROUTE=0

for arg in "$@"; do
  case "$arg" in
    --explain) EXPLAIN=1 ;;
    --host)    HOST_ROUTE=1 ;;
    *)         TASK="$arg" ;;
  esac
done

if [ -z "$TASK" ]; then
  echo "Usage: agent-router.sh [--explain] [--host] <task>" >&2
  exit 1
fi

# ── Agent classification (Python) ─────────────────────────────────────────────
AGENT_RESULT=$(python3 - "$TASK" "$EXPLAIN" << 'PYTHON_EOF'
import sys, re

task = sys.argv[1].lower()
explain = sys.argv[2] == "1"

# Pattern → (agent, reason, host_task_type)
# host_task_type maps to host-router.sh task_type vocabulary
# ORDER MATTERS — first match wins. More-specific patterns first.
routes = [
    # Finance — money / banking / receipts
    (r'expense|receipt|invoic|capital one|bank of america|fidelity|credit card|debt|budget|spent\b|owe|paycheck|statement|csv|pdf import', 'finance', 'general',
     'Personal finance management'),
    # Code — explicit coding verbs (matched BEFORE memory/research, so "refactor memory search" → code)
    (r'\bwrite code\b|\bimplement\b|\brefactor\b|\bfix\s+(the\s+)?(bug|crash|error|issue)\b|\bbugfix\b|\badd feature\b|\bedit file\b|\bcoding\b|create .*(function|method|class)|\bmodify\b|\bdebug\b|\brewrite\b|\bport\s+(to|from)\b', 'code', 'code',
     'Code implementation and modification'),
    # Code — ML/AI specialised
    (r'\btrain\b|finetune|fine.?tune|\bembedding\b|torch|pytorch|tensorflow|\bcuda\b|\bgpu\b', 'code', 'ml',
     'ML/AI training — may prefer high-RAM host'),
    # Code — iOS specialised
    (r'\bios\b|xcode|\bswift\b|iphone|ipad|simulator|provisioning', 'code', 'ios',
     'iOS/Swift development — prefers mac-aws (Xcode)'),
    # Ops — infra and scheduling
    (r'cron|schedul|dead.?man|health.?check|monitor|quota|collect.?metrics|allocat', 'ops', 'ops',
     'System operations, cron wiring, monitoring'),
    (r'keychain|secret|deploy|infra|server|disk|log rotation|permission|sudo|launchctl|launchd|brew\b|reboot|shutdown', 'ops', 'ops',
     'Infrastructure and system administration'),
    # Memory — only after code/ops/finance had a chance
    (r'\bremember\b|daily.?note|lesson.?learn|consolidat|\bprune\b|session.?summar|forgot|update memory|MEMORY\.md|memory file', 'memory', 'general',
     'Memory management and session documentation'),
    # Research — catch-all for understand/find/look up
    (r'\bfind\b|\bsearch\b|explor|how does|what does|read docs|investigat|where|lookup|understand|research|review|summari[sz]e', 'research', 'general',
     'Code exploration and external research'),
]

matched_agent = ""
matched_host_type = "general"
matched_reason = "Unable to classify task"

for pattern, agent, host_type, reason in routes:
    if re.search(pattern, task):
        matched_agent = agent
        matched_host_type = host_type
        matched_reason = reason
        break

# Output: agent|host_type|reason (pipe-delimited for bash parsing)
print(f"{matched_agent}|{matched_host_type}|{matched_reason}")
PYTHON_EOF
)

AGENT=$(echo "$AGENT_RESULT" | cut -d'|' -f1)
HOST_TASK_TYPE=$(echo "$AGENT_RESULT" | cut -d'|' -f2)
REASON=$(echo "$AGENT_RESULT" | cut -d'|' -f3)

# ── Host routing (optional) ───────────────────────────────────────────────────
if [ "$HOST_ROUTE" -eq 1 ]; then
  HOST=$(bash "$SCRIPT_DIR/host-router.sh" "$HOST_TASK_TYPE" route 2>/dev/null || echo "skip")
  if [ "$EXPLAIN" -eq 1 ]; then
    echo "agent: ${AGENT:-unknown} — $REASON"
    echo "host:  $HOST (task_type=$HOST_TASK_TYPE)"
  else
    echo "$HOST"
  fi
  [ "$HOST" != "skip" ]
  exit $?
fi

# ── Agent-only output (original behaviour) ───────────────────────────────────
if [ "$EXPLAIN" -eq 1 ]; then
  echo "${AGENT:-unknown}: $REASON"
else
  printf "%s" "$AGENT"
fi
