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
routes = [
    (r'cron|schedule|dead.?man|health.?check|monitor|quota|collect.?metrics|allocat', 'ops', 'ops',
     'System operations, cron wiring, monitoring'),
    (r'keychain|secret|deploy|infra|server|disk|log rotation|permission|sudo|launchctl', 'ops', 'ops',
     'Infrastructure and system administration'),
    (r'memor|remember|daily.?note|lesson.?learn|consolidat|prune|session.?summar|forgot', 'memory', 'general',
     'Memory management and session documentation'),
    (r'find|search|explore|how does|what does|read docs|investigat|where|lookup|understand', 'research', 'general',
     'Code exploration and external research'),
    (r'train|finetune|fine.?tune|embedding|torch|pytorch|tensorflow|cuda|gpu', 'code', 'ml',
     'ML/AI training — may prefer high-RAM host'),
    (r'ios|xcode|swift|iphone|ipad|simulator|provisioning', 'code', 'ios',
     'iOS/Swift development — prefers mac-aws (Xcode)'),
    (r'write code|implement|refactor|fix bug|add feature|edit file|coding|create.*function|modify|debug', 'code', 'code',
     'Code implementation and modification'),
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
