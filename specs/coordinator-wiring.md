# Coordinator Wiring Spec
**Version:** 1.0  
**Date:** 2026-04-22  
**Depends on:** specs/multi-agent-state-coordinator.md (already implemented)

---

## 1. Goal

Wire `scripts/agent_coordinator.py` into all existing workflows so that every
agent task is tracked in `STATE.yaml` from submit → running → done/failed.
No new features. No architectural changes. Minimal, targeted edits only.

---

## 2. New Methods Required in agent_coordinator.py

Two methods needed to support the wiring:

### 2a. `StateManager.find_by_session(session_id: str) -> dict | None`
Returns the first task whose `session_id` field matches, or None.
CLI: `python3 agent_coordinator.py find-session --session <id>` → `{"ok": true, "task": {...}}`

### 2b. `StateManager.timeout_check() -> list[dict]`
Returns running tasks whose elapsed time since `started_at` exceeds the
`timeout_seconds` for their `agent_type` (looked up from agent-directory.yaml).
CLI: `python3 agent_coordinator.py timeout-check` → `{"ok": true, "tasks": [...]}`

### 2c. `start` CLI: make `--session` optional
Currently `start` requires `--session`. Make it optional (default: `null`).
This allows observer-agent.sh to call `start` without a real session ID.

---

## 3. Files to Modify

### 3a. `scripts/task_router.py`

**Where:** `TaskRouter.route()` return value (currently returns a plain dict).

**Change:** After computing the routing result, submit the task to the
coordinator and include `coordinator_task_id` in the returned dict.
If coordinator submission fails (any exception), log a warning and continue —
coordinator is non-blocking, never breaks routing.

```python
# At end of route():
try:
    import subprocess, json as _json, os as _os
    _coord = _os.path.join(_os.path.dirname(__file__), "agent_coordinator.py")
    _result = subprocess.run(
        ["python3", _coord, "submit",
         "--task", user_input[:200],
         "--type", _agent_type_for(complexity),  # see mapping below
         "--priority", str(_priority_for(complexity))],
        capture_output=True, text=True, timeout=5
    )
    result["coordinator_task_id"] = _json.loads(_result.stdout).get("task_id")
except Exception:
    result["coordinator_task_id"] = None
return result
```

**Complexity → agent_type mapping** (add as module-level dict):
```python
COMPLEXITY_TO_AGENT_TYPE = {
    "SIMPLE": "research",
    "COMPLEX": "coding",
}
COMPLEXITY_TO_PRIORITY = {
    "SIMPLE": 3,
    "COMPLEX": 7,
}
```

### 3b. `scripts/spawn-claude-code-smart.sh`

**Where:** Top of script, after argument parsing (before classify call).

**Change:** Submit task to coordinator; store task_id in env var.
At end of script, print task_id so caller can use it.

```bash
# After argument parsing, before classify:
COORDINATOR_TASK_ID=""
if command -v python3 &>/dev/null; then
  _COORD_RESULT=$(python3 "$WORKSPACE/scripts/agent_coordinator.py" \
    submit --task "${TASK:-coding task}" --type coding --priority 7 2>/dev/null)
  COORDINATOR_TASK_ID=$(echo "$_COORD_RESULT" | python3 -c \
    "import sys,json; print(json.load(sys.stdin).get('task_id',''))" 2>/dev/null || true)
fi

# At very end of script (before exit):
if [ -n "$COORDINATOR_TASK_ID" ]; then
  echo "COORDINATOR_TASK_ID=$COORDINATOR_TASK_ID"
fi
```

### 3c. `scripts/spawn-with-openrouter.sh`

**Same pattern as 3b** — submit at top, print task_id at end.
Use `--type coding --priority 7`.

### 3d. `scripts/observer-agent.sh`

**Most complete lifecycle** — cron script with clear start and end.

**Where (start):** After initial setup, before the main observation logic.

```bash
# Submit + immediately start (observer has no external session ID)
_COORD_RESULT=$(python3 "$WORKSPACE/scripts/agent_coordinator.py" \
  submit --task "Observer agent run $(date +%Y-%m-%dT%H:%M)" \
  --type observer --priority 3 2>/dev/null || echo '{}')
COORDINATOR_TASK_ID=$(echo "$_COORD_RESULT" | python3 -c \
  "import sys,json; print(json.load(sys.stdin).get('task_id',''))" 2>/dev/null || true)

if [ -n "$COORDINATOR_TASK_ID" ]; then
  python3 "$WORKSPACE/scripts/agent_coordinator.py" \
    start --id "$COORDINATOR_TASK_ID" --model "claude-haiku-4-5-20251001" \
    >/dev/null 2>&1 || true
fi
```

**Where (end):** Just before the `cron-heartbeat.sh` call at the bottom.

```bash
if [ -n "$COORDINATOR_TASK_ID" ]; then
  if [ "$OBSERVER_EXIT_CODE" -eq 0 ]; then
    python3 "$WORKSPACE/scripts/agent_coordinator.py" \
      complete --id "$COORDINATOR_TASK_ID" \
      --summary "Observer completed: $COMMITS_FOUND new commits, $MEMORY_UPDATES memory updates" \
      >/dev/null 2>&1 || true
  else
    python3 "$WORKSPACE/scripts/agent_coordinator.py" \
      fail --id "$COORDINATOR_TASK_ID" \
      --error "Observer exited with code $OBSERVER_EXIT_CODE" \
      >/dev/null 2>&1 || true
  fi
fi
```

Note: `OBSERVER_EXIT_CODE` and the summary vars need to be captured before the
final `cron-heartbeat.sh` call. Read the existing script to find the right spot.

### 3e. `scripts/session-watchdog.sh`

**Where:** In the staleness check loop (where stale sessions are detected).

**Change:** When a session is deemed stale (>60 min silence), look up its
task in coordinator and call `fail`.

```bash
# After determining session $SESSION_ID is stale:
_TASK=$(python3 "$WORKSPACE/scripts/agent_coordinator.py" \
  find-session --session "$SESSION_ID" 2>/dev/null || echo '{}')
_TASK_ID=$(echo "$_TASK" | python3 -c \
  "import sys,json; d=json.load(sys.stdin); print(d.get('task',{}).get('id',''))" 2>/dev/null || true)
if [ -n "$_TASK_ID" ]; then
  python3 "$WORKSPACE/scripts/agent_coordinator.py" \
    fail --id "$_TASK_ID" \
    --error "Session $SESSION_ID stale >60m — watchdog triggered" \
    >/dev/null 2>&1 || true
fi
```

**Also add at end of session-watchdog.sh** (after main logic, before heartbeat):
```bash
# Fail any tasks that have exceeded their timeout
_TIMED_OUT=$(python3 "$WORKSPACE/scripts/agent_coordinator.py" \
  timeout-check 2>/dev/null | python3 -c \
  "import sys,json; [print(t['id']) for t in json.load(sys.stdin).get('tasks',[])]" 2>/dev/null || true)
for _TID in $_TIMED_OUT; do
  python3 "$WORKSPACE/scripts/agent_coordinator.py" \
    fail --id "$_TID" --error "Exceeded agent_type timeout limit" \
    >/dev/null 2>&1 || true
done
```

### 3f. `scripts/daily-session-reset.sh`

**Where:** At end of script, before exit.

```bash
# Purge old done/failed/cancelled tasks (keep last 20)
python3 "$WORKSPACE/scripts/agent_coordinator.py" purge --keep 20 \
  >/dev/null 2>&1 || true
```

### 3g. `scripts/session-stop-hook.sh`

**Where:** After session summarizer runs successfully (hook fires on Stop event).

The hook receives the session transcript. If the hook can extract a session_id
from the hook payload (stdin JSON has `session_id`), look it up in coordinator.

```bash
# Read session_id from stdin payload (already read earlier in the hook)
SESSION_ID=$(echo "$HOOK_PAYLOAD" | python3 -c \
  "import sys,json; print(json.load(sys.stdin).get('session_id',''))" 2>/dev/null || true)

if [ -n "$SESSION_ID" ]; then
  _TASK=$(python3 "$WORKSPACE/scripts/agent_coordinator.py" \
    find-session --session "$SESSION_ID" 2>/dev/null || echo '{}')
  _TASK_ID=$(echo "$_TASK" | python3 -c \
    "import sys,json; d=json.load(sys.stdin); print(d.get('task',{}).get('id',''))" 2>/dev/null || true)
  if [ -n "$_TASK_ID" ]; then
    python3 "$WORKSPACE/scripts/agent_coordinator.py" \
      complete --id "$_TASK_ID" --summary "Session ended cleanly" \
      >/dev/null 2>&1 || true
  fi
fi
```

**Read the existing hook first** to find where stdin is read, and reuse that
variable — don't read stdin twice.

---

## 4. Safety Rules (apply to every integration point)

1. **Never block the workflow.** Every coordinator call is wrapped in `>/dev/null 2>&1 || true` (bash) or `except Exception: pass` (Python). Coordinator failures are silent.
2. **Never read stdin twice.** If the hook already reads stdin into a variable, reuse that variable.
3. **`WORKSPACE` var.** Use `WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"` — don't hardcode paths.
4. **`--session` is optional.** For self-managing processes (observer-agent, daily-reset), pass no session.
5. **Minimal diff.** Add coordinator calls only — do not refactor surrounding code.

---

## 5. Tests to Add: `scripts/agent_coordinator_test.py`

Add a new test class `TestWiringHelpers` to the existing test file:

```
TestWiringHelpers:
  test_find_by_session_found        — submit→start with session_id, find_by_session returns it
  test_find_by_session_not_found    — find_by_session on unknown session_id returns None
  test_find_by_session_cli          — CLI find-session --session <id> returns ok:true with task
  test_timeout_check_no_overdue     — running task within timeout not returned
  test_timeout_check_overdue        — running task past timeout IS returned
  test_timeout_check_cli            — CLI timeout-check returns ok:true with tasks list
  test_start_without_session        — start with session_id=null succeeds
  test_start_without_session_cli    — CLI start --id <id> (no --session) succeeds
```

---

## 6. Acceptance Criteria

- [ ] All 8 new tests pass alongside existing 45 (53 total)
- [ ] `task_router.py route()` returns dict with `coordinator_task_id` key
- [ ] `spawn-claude-code-smart.sh` prints `COORDINATOR_TASK_ID=<id>` on success
- [ ] `observer-agent.sh` leaves a `done` or `failed` task in STATE.yaml after a dry run
- [ ] `session-watchdog.sh` calls `timeout-check` (verify by running with fake stale STATE.yaml)
- [ ] `daily-session-reset.sh` calls `purge` (verify by running with done tasks in STATE.yaml)
- [ ] No coordinator call ever causes a non-zero exit in any wired script

---

## 7. Implementation Order

1. Add `find_by_session`, `timeout_check`, make `--session` optional → run existing 45 tests + 8 new
2. Modify `task_router.py`
3. Modify `spawn-claude-code-smart.sh` + `spawn-with-openrouter.sh`
4. Modify `observer-agent.sh`
5. Modify `session-watchdog.sh`
6. Modify `daily-session-reset.sh`
7. Modify `session-stop-hook.sh`
8. Final: run full test suite (53 tests), dry-run each modified script
