#!/usr/bin/env python3
"""
agent_coordinator.py — Multi-Agent State Coordinator for OpenClaw
Manages STATE.yaml: task submission, lifecycle transitions, dependency enforcement.
"""

from __future__ import annotations

import argparse
import json
import os
import secrets
import sys
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    import warnings
    warnings.warn(
        "pyyaml not available; falling back to JSON for state storage. "
        "Install with: pip3 install pyyaml",
        RuntimeWarning,
    )
    _YAML_AVAILABLE = False

# ---------------------------------------------------------------------------
# Constants & Paths
# ---------------------------------------------------------------------------

WORKSPACE = Path(os.environ.get("OPENCLAW_WORKSPACE", Path.home() / ".openclaw/workspace"))
STATE_FILE = WORKSPACE / "STATE.yaml"
AGENT_DIR_FILE = WORKSPACE / "agent-directory.yaml"
LOCK_FILE = WORKSPACE / ".state.lock"
DEFAULT_MAX_CONCURRENT = 4

# Default agent-directory content (used for bootstrap)
_DEFAULT_AGENT_DIRECTORY = {
    "version": 1,
    "agent_types": {
        "coding": {
            "description": "Software implementation, debugging, refactoring",
            "default_model": "claude-opus-4-6",
            "fallback_model": "claude-haiku-4-5-20251001",
            "max_concurrent": 3,
            "timeout_seconds": 900,
            "context_files": ["SESSION_CONTEXT.md", "STATUS.md"],
        },
        "observer": {
            "description": "Read-only workspace scanning and memory updates",
            "default_model": "claude-haiku-4-5-20251001",
            "fallback_model": "claude-haiku-4-5-20251001",
            "max_concurrent": 1,
            "timeout_seconds": 300,
            "context_files": ["SESSION_CONTEXT.md"],
        },
        "research": {
            "description": "Web search, summarization, analysis",
            "default_model": "claude-sonnet-4-6",
            "fallback_model": "claude-haiku-4-5-20251001",
            "max_concurrent": 2,
            "timeout_seconds": 600,
            "context_files": ["SESSION_CONTEXT.md"],
        },
        "ops": {
            "description": "Infrastructure, cron, deployment",
            "default_model": "claude-sonnet-4-6",
            "fallback_model": "claude-haiku-4-5-20251001",
            "max_concurrent": 1,
            "timeout_seconds": 600,
            "context_files": ["SESSION_CONTEXT.md", "STATUS.md"],
        },
    },
}

_DEFAULT_STATE = {
    "version": 1,
    "updated_at": "",
    "tasks": [],
    "agents": {
        "running": 0,
        "max_concurrent": DEFAULT_MAX_CONCURRENT,
    },
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat()


def _dump(data: dict) -> str:
    if _YAML_AVAILABLE:
        return yaml.dump(data, default_flow_style=False, sort_keys=False)
    return json.dumps(data, indent=2)


def _load_text(text: str) -> dict:
    if _YAML_AVAILABLE:
        return yaml.safe_load(text) or {}
    return json.loads(text)


# ---------------------------------------------------------------------------
# Lock
# ---------------------------------------------------------------------------


@contextmanager
def _acquire_lock(lock_path: Path, timeout: float = 5.0):
    """Acquire a mkdir-based POSIX atomic lock."""
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


# ---------------------------------------------------------------------------
# AgentDirectory
# ---------------------------------------------------------------------------


class AgentDirectory:
    """Loads agent-directory.yaml and provides lookup helpers."""

    def __init__(self, path: Path = None):
        self._path = path if path is not None else AGENT_DIR_FILE
        self._data = self._load()

    def _load(self) -> dict:
        if not self._path.exists():
            # Bootstrap the file — handle concurrent bootstrap races gracefully
            self._path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self._path.with_suffix(".yaml.tmp")
            try:
                tmp.write_text(_dump(_DEFAULT_AGENT_DIRECTORY))
                os.replace(tmp, self._path)
            except (FileNotFoundError, OSError):
                # Another thread already bootstrapped the file; clean up our tmp
                try:
                    tmp.unlink(missing_ok=True)
                except Exception:
                    pass
            # If file still missing (shouldn't happen), return defaults in-memory
            if not self._path.exists():
                return _DEFAULT_AGENT_DIRECTORY
        text = self._path.read_text()
        return _load_text(text)

    def get(self, agent_type: str) -> dict:
        """Return agent type config. Raises KeyError if unknown."""
        types = self._data.get("agent_types", {})
        if agent_type not in types:
            raise KeyError(f"Unknown agent type: {agent_type!r}")
        return types[agent_type]

    def list_types(self) -> list:
        return list(self._data.get("agent_types", {}).keys())

    def resolve_model(self, agent_type: str) -> str:
        return self.get(agent_type)["default_model"]

    def max_concurrent(self, agent_type: str) -> int:
        return self.get(agent_type)["max_concurrent"]


# ---------------------------------------------------------------------------
# StateManager
# ---------------------------------------------------------------------------


class StateManager:
    """
    Atomic read-modify-write over STATE.yaml using a mkdir lock.
    All public methods acquire the lock, mutate state, release.
    """

    def __init__(self, workspace: Path = None, agent_dir_path: Path = None):
        self._workspace = workspace if workspace is not None else WORKSPACE
        self._state_file = self._workspace / "STATE.yaml"
        self._lock_file = self._workspace / ".state.lock"
        self._agent_dir = AgentDirectory(
            agent_dir_path if agent_dir_path is not None else (self._workspace / "agent-directory.yaml")
        )

    @contextmanager
    def _lock(self):
        with _acquire_lock(self._lock_file):
            yield

    def _load(self) -> dict:
        if not self._state_file.exists():
            state = dict(_DEFAULT_STATE)
            state["updated_at"] = _now_iso()
            state["tasks"] = []
            state["agents"] = {"running": 0, "max_concurrent": DEFAULT_MAX_CONCURRENT}
            return state
        text = self._state_file.read_text()
        data = _load_text(text)
        if not data:
            data = dict(_DEFAULT_STATE)
            data["updated_at"] = _now_iso()
            data["tasks"] = []
            data["agents"] = {"running": 0, "max_concurrent": DEFAULT_MAX_CONCURRENT}
        return data

    def _save(self, state: dict) -> None:
        state["updated_at"] = _now_iso()
        self._state_file.parent.mkdir(parents=True, exist_ok=True)
        tmp = self._state_file.with_suffix(".yaml.tmp")
        tmp.write_text(_dump(state))
        os.replace(tmp, self._state_file)

    def _gen_id(self, existing_ids: set) -> str:
        while True:
            new_id = secrets.token_hex(4)
            if new_id not in existing_ids:
                return new_id

    def _has_cycle(self, new_id: str, depends_on: list, tasks_by_id: dict) -> bool:
        visited = set()

        def dfs(tid):
            if tid == new_id:
                return True
            if tid in visited:
                return False
            visited.add(tid)
            task = tasks_by_id.get(tid)
            if not task:
                return False
            return any(dfs(dep) for dep in task.get("depends_on", []))

        return any(dfs(dep) for dep in depends_on)

    def submit(self, task_text: str, agent_type: str = "coding",
               priority: int = 5, depends_on: list = None) -> str:
        """Append a new task in 'queued' status. Returns the new task ID."""
        depends_on = depends_on or []

        # Validate agent_type (raises KeyError → convert to ValueError)
        try:
            self._agent_dir.get(agent_type)
        except KeyError as e:
            raise ValueError(str(e)) from e

        model = self._agent_dir.resolve_model(agent_type)

        with self._lock():
            state = self._load()
            tasks = state.setdefault("tasks", [])
            tasks_by_id = {t["id"]: t for t in tasks}
            existing_ids = set(tasks_by_id.keys())

            # Validate depends_on IDs exist
            for dep_id in depends_on:
                if dep_id not in tasks_by_id:
                    raise ValueError(f"depends_on ID not found: {dep_id!r}")

            # Cycle detection
            new_id = self._gen_id(existing_ids)
            if self._has_cycle(new_id, depends_on, tasks_by_id):
                raise ValueError(f"Circular dependency detected for task {new_id!r}")

            task = {
                "id": new_id,
                "title": task_text[:60],
                "status": "queued",
                "agent_type": agent_type,
                "model": model,
                "session_id": None,
                "priority": priority,
                "created_at": _now_iso(),
                "started_at": None,
                "completed_at": None,
                "depends_on": depends_on,
                "result_summary": None,
                "error": None,
            }
            tasks.append(task)
            self._save(state)
            return new_id

    def start(self, task_id: str, session_id: str, model: str) -> None:
        """Transition task from 'queued' → 'running'."""
        with self._lock():
            state = self._load()
            tasks = state.setdefault("tasks", [])
            tasks_by_id = {t["id"]: t for t in tasks}

            task = tasks_by_id.get(task_id)
            if task is None:
                raise RuntimeError(f"Task not found: {task_id!r}")
            if task["status"] != "queued":
                raise RuntimeError(
                    f"Task {task_id!r} is not queued (status={task['status']!r})"
                )

            # Check dependencies
            for dep_id in task.get("depends_on", []):
                dep = tasks_by_id.get(dep_id)
                if dep is None or dep["status"] != "done":
                    raise RuntimeError(
                        f"Dependency {dep_id!r} is not done (required by {task_id!r})"
                    )

            # Check per-type max_concurrent
            agent_type = task["agent_type"]
            try:
                type_max = self._agent_dir.max_concurrent(agent_type)
            except KeyError:
                type_max = DEFAULT_MAX_CONCURRENT

            running_of_type = sum(
                1 for t in tasks
                if t["agent_type"] == agent_type and t["status"] == "running"
            )
            if running_of_type >= type_max:
                raise RuntimeError(
                    f"agent_type {agent_type!r} is at max_concurrent ({type_max})"
                )

            # Check global max_concurrent
            agents_info = state.setdefault("agents", {})
            global_max = agents_info.get("max_concurrent", DEFAULT_MAX_CONCURRENT)
            global_running = agents_info.get("running", 0)
            if global_running >= global_max:
                raise RuntimeError(
                    f"Global max_concurrent ({global_max}) reached"
                )

            task["status"] = "running"
            task["session_id"] = session_id
            task["model"] = model
            task["started_at"] = _now_iso()
            agents_info["running"] = global_running + 1
            self._save(state)

    def complete(self, task_id: str, result_summary: str = "") -> None:
        """Transition task from 'running' → 'done'."""
        with self._lock():
            state = self._load()
            tasks = state.setdefault("tasks", [])
            tasks_by_id = {t["id"]: t for t in tasks}

            task = tasks_by_id.get(task_id)
            if task is None:
                raise RuntimeError(f"Task not found: {task_id!r}")
            if task["status"] != "running":
                raise RuntimeError(
                    f"Task {task_id!r} is not running (status={task['status']!r})"
                )

            task["status"] = "done"
            task["completed_at"] = _now_iso()
            task["result_summary"] = result_summary

            agents_info = state.setdefault("agents", {})
            agents_info["running"] = max(0, agents_info.get("running", 1) - 1)
            self._save(state)

    def fail(self, task_id: str, error: str) -> None:
        """Transition task from 'running' → 'failed'."""
        with self._lock():
            state = self._load()
            tasks = state.setdefault("tasks", [])
            tasks_by_id = {t["id"]: t for t in tasks}

            task = tasks_by_id.get(task_id)
            if task is None:
                raise RuntimeError(f"Task not found: {task_id!r}")
            if task["status"] != "running":
                raise RuntimeError(
                    f"Task {task_id!r} is not running (status={task['status']!r})"
                )

            task["status"] = "failed"
            task["error"] = error
            task["completed_at"] = _now_iso()

            agents_info = state.setdefault("agents", {})
            agents_info["running"] = max(0, agents_info.get("running", 1) - 1)
            self._save(state)

    def cancel(self, task_id: str) -> None:
        """Cancel a 'queued' task (cannot cancel running tasks)."""
        with self._lock():
            state = self._load()
            tasks = state.setdefault("tasks", [])
            tasks_by_id = {t["id"]: t for t in tasks}

            task = tasks_by_id.get(task_id)
            if task is None:
                raise RuntimeError(f"Task not found: {task_id!r}")
            if task["status"] == "running":
                raise RuntimeError(
                    f"Cannot cancel a running task: {task_id!r}"
                )
            task["status"] = "cancelled"
            self._save(state)

    def list_tasks(self, status: str = None) -> list:
        """Return tasks, optionally filtered by status."""
        with self._lock():
            state = self._load()
        tasks = state.get("tasks", [])
        if status is not None:
            tasks = [t for t in tasks if t["status"] == status]
        return tasks

    def get_task(self, task_id: str):
        """Return a single task dict or None."""
        with self._lock():
            state = self._load()
        tasks_by_id = {t["id"]: t for t in state.get("tasks", [])}
        return tasks_by_id.get(task_id)

    def ready_to_run(self) -> list:
        """
        Return queued tasks whose depends_on are all 'done'
        and whose agent_type is not at max_concurrent.
        Sorted by priority descending, then created_at ascending.
        """
        with self._lock():
            state = self._load()

        tasks = state.get("tasks", [])
        tasks_by_id = {t["id"]: t for t in tasks}

        # Count running per agent_type
        running_by_type = {}
        for t in tasks:
            if t["status"] == "running":
                at = t["agent_type"]
                running_by_type[at] = running_by_type.get(at, 0) + 1

        agents_info = state.get("agents", {})
        global_max = agents_info.get("max_concurrent", DEFAULT_MAX_CONCURRENT)
        global_running = agents_info.get("running", 0)

        result = []
        for task in tasks:
            if task["status"] != "queued":
                continue

            # Check all deps done
            deps_ok = all(
                tasks_by_id.get(dep_id, {}).get("status") == "done"
                for dep_id in task.get("depends_on", [])
            )
            if not deps_ok:
                continue

            # Check per-type cap
            agent_type = task["agent_type"]
            try:
                type_max = self._agent_dir.max_concurrent(agent_type)
            except KeyError:
                type_max = DEFAULT_MAX_CONCURRENT

            if running_by_type.get(agent_type, 0) >= type_max:
                continue

            # Check global cap
            if global_running >= global_max:
                continue

            result.append(task)

        result.sort(key=lambda t: (-t["priority"], t["created_at"]))
        return result

    def purge_done(self, keep_last: int = 20) -> int:
        """Remove old done/failed/cancelled tasks beyond keep_last. Returns count removed."""
        with self._lock():
            state = self._load()
            tasks = state.get("tasks", [])

            terminal = [t for t in tasks if t["status"] in ("done", "failed", "cancelled")]
            active = [t for t in tasks if t["status"] not in ("done", "failed", "cancelled")]

            # Sort terminal by completed_at or created_at, keep most recent keep_last
            terminal.sort(key=lambda t: t.get("completed_at") or t.get("created_at") or "")
            to_remove = terminal[: max(0, len(terminal) - keep_last)]
            keep_terminal = terminal[max(0, len(terminal) - keep_last):]

            state["tasks"] = active + keep_terminal
            self._save(state)
            return len(to_remove)

    def find_by_session(self, session_id: str) -> dict | None:
        """Return the first task whose session_id field matches, or None."""
        with self._lock():
            state = self._load()
        for task in state.get("tasks", []):
            if task.get("session_id") == session_id:
                return task
        return None

    def timeout_check(self) -> list:
        """Return running tasks whose elapsed time exceeds their agent_type timeout."""
        with self._lock():
            state = self._load()

        now = datetime.now(timezone.utc).astimezone()
        result = []
        for task in state.get("tasks", []):
            if task.get("status") != "running":
                continue
            started_at_str = task.get("started_at")
            if not started_at_str:
                continue
            try:
                started_at = datetime.fromisoformat(started_at_str)
                elapsed = (now - started_at).total_seconds()
            except (ValueError, TypeError):
                continue
            try:
                cfg = self._agent_dir.get(task.get("agent_type", "coding"))
                timeout_seconds = cfg.get("timeout_seconds", 900)
            except KeyError:
                timeout_seconds = 900
            if elapsed > timeout_seconds:
                result.append(task)
        return result

    def get_status_summary(self) -> dict:
        """Return counts by status plus agents.running."""
        with self._lock():
            state = self._load()

        tasks = state.get("tasks", [])
        counts = {}
        for t in tasks:
            counts[t["status"]] = counts.get(t["status"], 0) + 1

        agents_info = state.get("agents", {})
        return {
            "counts": counts,
            "agents_running": agents_info.get("running", 0),
            "agents_max_concurrent": agents_info.get("max_concurrent", DEFAULT_MAX_CONCURRENT),
        }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _ok(**kwargs) -> dict:
    return {"ok": True, **kwargs}


def _err(msg: str) -> dict:
    return {"ok": False, "error": msg}


def _print_and_exit(data: dict, code: int = 0):
    print(json.dumps(data))
    sys.exit(code)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="OpenClaw multi-agent state coordinator"
    )
    sub = parser.add_subparsers(dest="command")

    # submit
    p_submit = sub.add_parser("submit", help="Submit a new task")
    p_submit.add_argument("--task", required=True, help="Task description")
    p_submit.add_argument("--type", dest="agent_type", default="coding")
    p_submit.add_argument("--priority", type=int, default=5)
    p_submit.add_argument("--depends-on", dest="depends_on", default="",
                          help="Comma-separated task IDs")

    # start
    p_start = sub.add_parser("start", help="Transition task to running")
    p_start.add_argument("--id", required=True)
    p_start.add_argument("--session", required=False, default=None)
    p_start.add_argument("--model", default=None)

    # find-session
    p_find_session = sub.add_parser("find-session", help="Find task by session_id")
    p_find_session.add_argument("--session", required=True)

    # timeout-check
    sub.add_parser("timeout-check", help="List running tasks that have exceeded their timeout")

    # complete
    p_complete = sub.add_parser("complete", help="Mark task as done")
    p_complete.add_argument("--id", required=True)
    p_complete.add_argument("--summary", default="")

    # fail
    p_fail = sub.add_parser("fail", help="Mark task as failed")
    p_fail.add_argument("--id", required=True)
    p_fail.add_argument("--error", required=True)

    # cancel
    p_cancel = sub.add_parser("cancel", help="Cancel a queued task")
    p_cancel.add_argument("--id", required=True)

    # list
    p_list = sub.add_parser("list", help="List tasks")
    p_list.add_argument("--status", default=None,
                        choices=["queued", "running", "done", "failed", "cancelled"])

    # ready
    sub.add_parser("ready", help="Tasks that can start right now")

    # status
    sub.add_parser("status", help="Summary: counts by status + agents.running")

    # purge
    p_purge = sub.add_parser("purge", help="Remove old completed tasks")
    p_purge.add_argument("--keep", type=int, default=20)

    # agents
    sub.add_parser("agents", help="List agent types from directory")

    return parser


def main():
    parser = _build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    sm = StateManager()

    try:
        if args.command == "submit":
            depends_on = [x.strip() for x in args.depends_on.split(",") if x.strip()]
            task_id = sm.submit(
                task_text=args.task,
                agent_type=args.agent_type,
                priority=args.priority,
                depends_on=depends_on,
            )
            _print_and_exit(_ok(task_id=task_id))

        elif args.command == "start":
            # Resolve model: use --model if provided, else default for agent_type
            task = sm.get_task(args.id)
            if task is None:
                _print_and_exit(_err(f"task not found: {args.id}"), 1)
            model = args.model or task.get("model") or "claude-opus-4-6"
            session_id = args.session  # may be None — that's ok
            sm.start(args.id, session_id, model)
            _print_and_exit(_ok(task_id=args.id))

        elif args.command == "complete":
            sm.complete(args.id, args.summary)
            _print_and_exit(_ok(task_id=args.id))

        elif args.command == "fail":
            sm.fail(args.id, args.error)
            _print_and_exit(_ok(task_id=args.id))

        elif args.command == "cancel":
            sm.cancel(args.id)
            _print_and_exit(_ok(task_id=args.id))

        elif args.command == "list":
            tasks = sm.list_tasks(status=args.status)
            _print_and_exit(_ok(tasks=tasks))

        elif args.command == "ready":
            tasks = sm.ready_to_run()
            _print_and_exit(_ok(tasks=tasks))

        elif args.command == "status":
            summary = sm.get_status_summary()
            _print_and_exit(_ok(**summary))

        elif args.command == "purge":
            removed = sm.purge_done(keep_last=args.keep)
            _print_and_exit(_ok(removed=removed))

        elif args.command == "agents":
            ad = AgentDirectory()
            types = ad.list_types()
            details = {t: ad.get(t) for t in types}
            _print_and_exit(_ok(agent_types=details))

        elif args.command == "find-session":
            task = sm.find_by_session(args.session)
            _print_and_exit(_ok(task=task))

        elif args.command == "timeout-check":
            tasks = sm.timeout_check()
            _print_and_exit(_ok(tasks=tasks))

    except (ValueError, RuntimeError, KeyError) as e:
        _print_and_exit(_err(str(e)), 1)
    except TimeoutError as e:
        _print_and_exit(_err(f"Lock timeout: {e}"), 1)
    except Exception as e:
        _print_and_exit(_err(f"Unexpected error: {e}"), 1)


if __name__ == "__main__":
    main()
