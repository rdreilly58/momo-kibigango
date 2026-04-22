# Multi-Agent State Coordinator — Coding Spec
**Version:** 1.0  
**Date:** 2026-04-22  
**Status:** Ready for implementation

---

## 1. Purpose & Scope

OpenClaw already has task classification (`task-classifier.py`), spawning scripts (`spawn-claude-code-smart.sh`), and MCP session tools (`mcp__openclaw__sessions_*`). What's missing is a **unified coordination layer** that:

- Tracks all active/queued/completed agent tasks in a single file (`STATE.yaml`)
- Maintains an **agent directory** (registry of known agent types and their capabilities)
- Enforces **task dependencies** (task B starts only after task A completes)
- Serializes concurrent state mutations atomically
- Provides a CLI for inspection and control

**Out of scope:** cost tracking, LanceDB memory, OpenRouter integration (those are separate layers).

---

## 2. Files to Create

```
scripts/
  agent_coordinator.py     # Main module — StateManager + AgentDirectory + CLI
  agent_coordinator_test.py # Self-tests (unittest, no external deps)

STATE.yaml                 # Runtime state file (created on first use, .gitignored)
agent-directory.yaml       # Static registry of known agent types
```

One new .gitignore entry: `STATE.yaml`

---

## 3. STATE.yaml Schema

```yaml
# Auto-managed by agent_coordinator.py — do not edit by hand while tasks are running
version: 1
updated_at: "2026-04-22T15:30:00-04:00"

tasks:
  - id: "abc123"                    # 8-char hex, generated at submission
    title: "Refactor memory router" # Human label (first 60 chars of task text)
    status: running                 # queued | running | done | failed | cancelled
    agent_type: "coding"            # Key into agent-directory.yaml
    model: "claude-opus-4-6"        # Resolved model string
    session_id: "sess_xyz"          # OpenClaw session ID (null until spawned)
    priority: 5                     # 1 (lowest) – 10 (highest)
    created_at: "2026-04-22T15:00:00-04:00"
    started_at: "2026-04-22T15:01:00-04:00"
    completed_at: null
    depends_on: []                  # List of task IDs that must be 'done' first
    result_summary: null            # Written by coordinator on completion
    error: null                     # Written on failure

agents:
  running: 2
  max_concurrent: 4                 # Default cap; overridden per agent_type in directory
```

**Invariants:**
- `id` is globally unique within the file
- A task moves to `running` only when all `depends_on` IDs are `done`
- `running` count in `agents` must equal the count of tasks with `status: running`

---

## 4. agent-directory.yaml Schema

```yaml
# Static registry — edit freely, loaded fresh on each coordinator call
version: 1

agent_types:
  coding:
    description: "Software implementation, debugging, refactoring"
    default_model: "claude-opus-4-6"
    fallback_model: "claude-haiku-4-5-20251001"
    max_concurrent: 3
    timeout_seconds: 900
    context_files:
      - SESSION_CONTEXT.md
      - STATUS.md

  observer:
    description: "Read-only workspace scanning and memory updates"
    default_model: "claude-haiku-4-5-20251001"
    fallback_model: "claude-haiku-4-5-20251001"
    max_concurrent: 1
    timeout_seconds: 300
    context_files:
      - SESSION_CONTEXT.md

  research:
    description: "Web search, summarization, analysis"
    default_model: "claude-sonnet-4-6"
    fallback_model: "claude-haiku-4-5-20251001"
    max_concurrent: 2
    timeout_seconds: 600
    context_files:
      - SESSION_CONTEXT.md

  ops:
    description: "Infrastructure, cron, deployment"
    default_model: "claude-sonnet-4-6"
    fallback_model: "claude-haiku-4-5-20251001"
    max_concurrent: 1
    timeout_seconds: 600
    context_files:
      - SESSION_CONTEXT.md
      - STATUS.md
```

---

## 5. Module: `agent_coordinator.py`

### 5.1 Constants & Paths

```python
WORKSPACE = Path(os.environ.get("OPENCLAW_WORKSPACE", Path.home() / ".openclaw/workspace"))
STATE_FILE = WORKSPACE / "STATE.yaml"
AGENT_DIR_FILE = WORKSPACE / "agent-directory.yaml"
LOCK_FILE = WORKSPACE / ".state.lock"   # mkdir-based lock (POSIX atomic)
DEFAULT_MAX_CONCURRENT = 4
```

### 5.2 Class: `StateManager`

```python
class StateManager:
    """
    Atomic read-modify-write over STATE.yaml using a mkdir lock.
    All public methods acquire the lock, mutate state, release.
    """

    def _lock(self) -> contextmanager
        """Acquires LOCK_FILE via mkdir, yields, releases on exit."""

    def _load(self) -> dict
        """Read STATE.yaml → dict. Create empty state if file missing."""

    def _save(self, state: dict) -> None
        """Write dict → STATE.yaml atomically (write tmp, os.replace)."""

    def submit(self, task_text: str, agent_type: str = "coding",
               priority: int = 5, depends_on: list[str] = None) -> str:
        """
        Append a new task in 'queued' status.
        Returns the new task ID.
        Raises ValueError if agent_type not in agent-directory.yaml.
        Raises ValueError if any depends_on ID doesn't exist in state.
        """

    def start(self, task_id: str, session_id: str, model: str) -> None:
        """
        Transition task from 'queued' → 'running'.
        Raises RuntimeError if task is not in 'queued' status.
        Raises RuntimeError if depends_on tasks are not all 'done'.
        Raises RuntimeError if agent_type max_concurrent would be exceeded.
        Increments agents.running.
        """

    def complete(self, task_id: str, result_summary: str = "") -> None:
        """
        Transition task from 'running' → 'done'.
        Sets completed_at, result_summary.
        Decrements agents.running.
        """

    def fail(self, task_id: str, error: str) -> None:
        """
        Transition task from 'running' → 'failed'.
        Sets error field.
        Decrements agents.running.
        """

    def cancel(self, task_id: str) -> None:
        """
        Cancel a 'queued' task (cannot cancel running tasks).
        Raises RuntimeError if task is 'running'.
        """

    def list_tasks(self, status: str = None) -> list[dict]:
        """Return tasks, optionally filtered by status."""

    def get_task(self, task_id: str) -> dict | None:
        """Return a single task dict or None."""

    def ready_to_run(self) -> list[dict]:
        """
        Return queued tasks whose depends_on are all 'done'
        and whose agent_type is not at max_concurrent.
        Sorted by priority descending, then created_at ascending.
        """

    def purge_done(self, keep_last: int = 20) -> int:
        """
        Remove old done/failed/cancelled tasks beyond keep_last.
        Returns count removed.
        """
```

### 5.3 Class: `AgentDirectory`

```python
class AgentDirectory:
    """Loads agent-directory.yaml and provides lookup helpers."""

    def __init__(self, path: Path = AGENT_DIR_FILE)

    def get(self, agent_type: str) -> dict:
        """Return agent type config. Raises KeyError if unknown."""

    def list_types(self) -> list[str]:
        """Return all known agent type names."""

    def resolve_model(self, agent_type: str) -> str:
        """Return default_model for the type."""

    def max_concurrent(self, agent_type: str) -> int:
        """Return max_concurrent for the type."""
```

### 5.4 CLI Interface

The script is directly executable. All subcommands print JSON to stdout for composability.

```
python3 agent_coordinator.py submit   --task "..." [--type coding] [--priority 5] [--depends-on id1,id2]
python3 agent_coordinator.py start    --id <id> --session <session_id> [--model <model>]
python3 agent_coordinator.py complete --id <id> [--summary "..."]
python3 agent_coordinator.py fail     --id <id> --error "..."
python3 agent_coordinator.py cancel   --id <id>
python3 agent_coordinator.py list     [--status queued|running|done|failed|cancelled]
python3 agent_coordinator.py ready    # tasks that can start right now
python3 agent_coordinator.py status   # summary: counts by status + agents.running
python3 agent_coordinator.py purge    [--keep 20]
python3 agent_coordinator.py agents   # list agent types from directory
```

**Output format (all commands):**
```json
{"ok": true, "task_id": "abc123"}
{"ok": true, "tasks": [...]}
{"ok": false, "error": "task not found: abc123"}
```

Exit code 0 on success, 1 on error.

---

## 6. Locking Protocol

Use the same `mkdir`-based atomic lock as `progress-notify-hook.sh`:

```python
import os, time
from contextlib import contextmanager

@contextmanager
def _acquire_lock(lock_path: Path, timeout: float = 5.0):
    deadline = time.monotonic() + timeout
    while True:
        try:
            lock_path.mkdir()
            break
        except FileExistsError:
            if time.monotonic() > deadline:
                raise TimeoutError(f"Could not acquire lock: {lock_path}")
            time.sleep(0.05)
    try:
        yield
    finally:
        try:
            lock_path.rmdir()
        except Exception:
            pass
```

---

## 7. Atomic Write Protocol

```python
import tempfile, os

def _save(self, state: dict, path: Path) -> None:
    state["updated_at"] = datetime.now(timezone.utc).astimezone().isoformat()
    tmp = path.with_suffix(".yaml.tmp")
    tmp.write_text(yaml.dump(state, default_flow_style=False, sort_keys=False))
    os.replace(tmp, path)   # atomic on POSIX
```

---

## 8. Dependency Graph Rules

- A task with `depends_on: ["abc", "def"]` is eligible to run only when both `abc` and `def` have `status: done`
- If a dependency `fails`, dependent tasks remain `queued` indefinitely (user must cancel manually)
- Circular dependency detection: at `submit` time, walk the full dependency graph; raise `ValueError` if a cycle is detected

**Cycle detection algorithm:**
```
def _has_cycle(new_id, depends_on, all_tasks) -> bool:
    visited = set()
    def dfs(tid):
        if tid == new_id: return True
        if tid in visited: return False
        visited.add(tid)
        task = all_tasks.get(tid)
        if not task: return False
        return any(dfs(dep) for dep in task.get("depends_on", []))
    return any(dfs(dep) for dep in depends_on)
```

---

## 9. Self-Test Suite: `agent_coordinator_test.py`

Uses `unittest`, `tempfile`, no network calls, no openclaw CLI. All tests patch WORKSPACE/STATE_FILE/AGENT_DIR_FILE to temp dirs.

### Test Classes & Cases

#### `TestStateManagerBasic`
- `test_load_creates_empty_state` — load on missing file creates valid skeleton
- `test_submit_returns_id` — submit returns 8-char hex string
- `test_submit_task_appears_in_list` — submitted task is in list_tasks()
- `test_submit_unknown_agent_type_raises` — ValueError for unrecognised type
- `test_submit_depends_on_nonexistent_raises` — ValueError for unknown dep ID
- `test_state_persists_across_instances` — two StateManager instances see same data

#### `TestStateTransitions`
- `test_start_transitions_queued_to_running` — status becomes running
- `test_start_increments_agents_running` — agents.running incremented
- `test_start_non_queued_raises` — RuntimeError if already running
- `test_start_unsatisfied_depends_raises` — RuntimeError if dep not done
- `test_complete_transitions_running_to_done` — status becomes done
- `test_complete_decrements_agents_running` — agents.running decremented
- `test_complete_sets_completed_at` — completed_at is set
- `test_fail_transitions_running_to_failed` — status becomes failed
- `test_fail_sets_error` — error field populated
- `test_cancel_queued_task` — queued task becomes cancelled
- `test_cancel_running_task_raises` — RuntimeError

#### `TestDependencies`
- `test_ready_to_run_no_deps` — task with no deps appears in ready_to_run()
- `test_ready_to_run_satisfied_deps` — task with done deps appears in ready_to_run()
- `test_ready_to_run_unsatisfied_deps` — task with queued dep not in ready_to_run()
- `test_ready_to_run_failed_deps` — task with failed dep not in ready_to_run()
- `test_cycle_detection_direct` — A depends on A raises ValueError
- `test_cycle_detection_indirect` — A→B→A raises ValueError
- `test_no_false_positive_chain` — A→B→C (linear) does not raise

#### `TestMaxConcurrent`
- `test_max_concurrent_blocks_start` — starting beyond max_concurrent raises RuntimeError
- `test_max_concurrent_per_type` — different agent types have independent limits
- `test_max_concurrent_after_complete_allows_new_start` — slot freed after complete()

#### `TestReadyToRunOrdering`
- `test_ready_sorted_priority_desc` — higher priority tasks first
- `test_ready_sorted_created_at_asc_tiebreak` — earlier created_at wins ties

#### `TestPurge`
- `test_purge_removes_old_done` — done tasks beyond keep_last removed
- `test_purge_keeps_running` — running tasks never purged
- `test_purge_returns_count` — returns number removed

#### `TestAtomicWrite`
- `test_concurrent_submits` — 10 threads each submit 5 tasks; final count = 50, no corruption
- `test_lock_timeout` — lock held externally causes TimeoutError after 5s

#### `TestAgentDirectory`
- `test_load_known_type` — returns correct config dict
- `test_unknown_type_raises` — KeyError
- `test_list_types` — returns all keys
- `test_resolve_model` — returns default_model string
- `test_max_concurrent` — returns correct int

#### `TestCLI`
- `test_cli_submit` — `submit --task "foo"` exits 0, prints JSON with task_id
- `test_cli_list_empty` — `list` on fresh state returns `{"ok": true, "tasks": []}`
- `test_cli_status` — `status` returns counts dict
- `test_cli_submit_start_complete_flow` — full lifecycle via CLI subprocess calls
- `test_cli_error_json` — bad input exits 1, prints `{"ok": false, "error": "..."}`
- `test_cli_agents` — `agents` returns list of agent types

---

## 10. Implementation Notes

1. **Dependencies:** `pyyaml` only. No other third-party packages. If pyyaml unavailable, fall back to `json` for STATE file (with `.json` extension) and log a warning.

2. **agent-directory.yaml bootstrap:** If `agent-directory.yaml` doesn't exist, write the default content from section 4 automatically on first load.

3. **STATE.yaml bootstrap:** If `STATE.yaml` doesn't exist, create it with `tasks: []`, `agents: {running: 0, max_concurrent: 4}`, `version: 1`.

4. **ID generation:** `secrets.token_hex(4)` (8 hex chars). Re-roll on collision (vanishingly rare).

5. **Timestamps:** Always ISO 8601 with UTC offset. Use `datetime.now(timezone.utc).astimezone().isoformat()`.

6. **No subprocess calls in core module.** The coordinator only manages STATE.yaml. Actual agent spawning (calling `openclaw sessions_spawn` or `spawn-claude-code-smart.sh`) is handled by the caller — the coordinator just records what was decided.

7. **agents.max_concurrent** in STATE.yaml is a global cap across all types. Per-type cap from agent-directory.yaml is also enforced.

---

## 11. Acceptance Criteria

- [ ] `python3 scripts/agent_coordinator.py agents` lists at least 4 agent types
- [ ] Full submit → start → complete lifecycle works via CLI with correct JSON output
- [ ] Dependency enforcement: starting a task with unsatisfied deps returns `{"ok": false, ...}`
- [ ] Concurrent stress test (10 threads, 50 tasks) produces no YAML corruption
- [ ] All unittest cases pass: `python3 scripts/agent_coordinator_test.py -v`
- [ ] `STATE.yaml` is created automatically if missing; `agent-directory.yaml` is bootstrapped if missing
- [ ] Lock file is always cleaned up even on KeyboardInterrupt (try/finally in context manager)
