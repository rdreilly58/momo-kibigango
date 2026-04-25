#!/bin/bash
# agent-router.sh — Analyze a task and suggest the appropriate agent
#
# Usage:
#   agent=$(bash agent-router.sh "wire system health check to cron")
#   # → outputs: ops
#
#   bash agent-router.sh --explain "refactor memory search"
#   # → outputs agent name + reasoning

TASK="${1:-}"
EXPLAIN="${2:---explain}"

if [ -z "$TASK" ]; then
  echo "Usage: agent-router.sh <task> [--explain]" >&2
  exit 1
fi

python3 << 'PYTHON_EOF'
import sys, re

task = sys.argv[1].lower()
explain = len(sys.argv) > 2 and sys.argv[2] == '--explain'

# Pattern → (agent, reason)
routes = [
    (r'cron|schedule|dead.?man|health.?check|monitor|quota|collect.?metrics|allocat', 'ops', 'System operations, cron wiring, monitoring'),
    (r'keychain|secret|deploy|infra|server|disk|log rotation|permission|sudo|launchctl', 'ops', 'Infrastructure and system administration'),
    (r'memor|remember|daily.?note|lesson.?learn|consolidat|prune|session.?summar|forgot', 'memory', 'Memory management and session documentation'),
    (r'find|search|explore|how does|what does|read docs|investigat|where|lookup|understand', 'research', 'Code exploration and external research'),
    (r'write code|implement|refactor|fix bug|add feature|edit file|coding|create.*function|modify|debug', 'code', 'Code implementation and modification'),
]

for pattern, agent, reason in routes:
    if re.search(pattern, task):
        if explain:
            print(f"{agent}: {reason}")
        else:
            print(agent, end='')
        sys.exit(0)

if explain:
    print("unknown: Unable to classify task")
else:
    print("", end='')
PYTHON_EOF
