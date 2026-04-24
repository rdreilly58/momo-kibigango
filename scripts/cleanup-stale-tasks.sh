#!/bin/bash
# cleanup-stale-tasks.sh — Abandon queued tasks that never got dispatched
#
# Cron: 0 9 * * * (daily at 9am)
# Marks any task in 'queued' state with null started_at older than 24h as 'abandoned'.

WORKSPACE="${HOME}/.openclaw/workspace"
STATE="$WORKSPACE/STATE.yaml"
LOG="$HOME/.openclaw/logs/task-cleanup.log"

mkdir -p "$(dirname "$LOG")"

python3 - <<PYEOF 2>&1 | tee -a "$LOG"
import yaml, datetime, sys

STATE = "$STATE"

try:
    with open(STATE) as f:
        state = yaml.safe_load(f)
except Exception as e:
    print(f"[cleanup] ERROR reading {STATE}: {e}")
    sys.exit(0)

now = datetime.datetime.now(datetime.timezone.utc)
cutoff = now - datetime.timedelta(hours=24)
abandoned = 0
queued_remaining = 0

for task in state.get('tasks', []):
    if task['status'] == 'queued' and task.get('started_at') is None:
        created = datetime.datetime.fromisoformat(str(task['created_at']))
        if created.tzinfo is None:
            created = created.replace(tzinfo=datetime.timezone.utc)
        if created < cutoff:
            task['status'] = 'abandoned'
            task['result_summary'] = f'Auto-abandoned: queued >{int((now-created).total_seconds()/3600)}h without dispatch'
            abandoned += 1
        else:
            queued_remaining += 1

state['updated_at'] = now.isoformat()
with open(STATE, 'w') as f:
    yaml.dump(state, f, default_flow_style=False, allow_unicode=True)

ts = now.strftime('%Y-%m-%d %H:%M')
print(f"[{ts}] cleanup-stale-tasks: abandoned={abandoned}, still_queued={queued_remaining}")
PYEOF
