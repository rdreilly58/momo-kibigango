#!/usr/bin/env python3
"""
agent_coordinator_test.py — Self-tests for agent_coordinator.py
All tests use temp directories; no network calls; no openclaw CLI.
"""

import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Ensure scripts/ is on path so we can import agent_coordinator
# ---------------------------------------------------------------------------
_SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(_SCRIPTS_DIR))

# Override WORKSPACE env BEFORE importing so module constants resolve correctly.
# We'll patch per-test via StateManager(workspace=...) constructor args.
import agent_coordinator as ac


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_sm(tmp_path: Path) -> ac.StateManager:
    """Return a StateManager wired to a temp workspace."""
    tmp_path.mkdir(parents=True, exist_ok=True)
    # Copy/bootstrap agent-directory into tmp workspace
    ad_path = tmp_path / "agent-directory.yaml"
    return ac.StateManager(workspace=tmp_path, agent_dir_path=ad_path)


def _run_cli(*args, workspace: Path) -> tuple:
    """Run the coordinator CLI as a subprocess. Returns (returncode, stdout, stderr)."""
    env = os.environ.copy()
    env["OPENCLAW_WORKSPACE"] = str(workspace)
    result = subprocess.run(
        [sys.executable, str(_SCRIPTS_DIR / "agent_coordinator.py")] + list(args),
        capture_output=True,
        text=True,
        env=env,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


# ---------------------------------------------------------------------------
# TestStateManagerBasic
# ---------------------------------------------------------------------------

class TestStateManagerBasic(unittest.TestCase):

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self._ws = Path(self._tmpdir.name)

    def tearDown(self):
        self._tmpdir.cleanup()

    def _sm(self):
        return _make_sm(self._ws)

    def test_load_creates_empty_state(self):
        sm = self._sm()
        with sm._lock():
            state = sm._load()
        self.assertIn("tasks", state)
        self.assertIn("agents", state)
        self.assertIsInstance(state["tasks"], list)
        self.assertEqual(len(state["tasks"]), 0)
        self.assertEqual(state["agents"]["running"], 0)

    def test_submit_returns_id(self):
        sm = self._sm()
        task_id = sm.submit("Do something", agent_type="coding")
        self.assertIsInstance(task_id, str)
        self.assertEqual(len(task_id), 8)
        # Must be hex
        int(task_id, 16)

    def test_submit_task_appears_in_list(self):
        sm = self._sm()
        task_id = sm.submit("My task", agent_type="coding")
        tasks = sm.list_tasks()
        ids = [t["id"] for t in tasks]
        self.assertIn(task_id, ids)

    def test_submit_unknown_agent_type_raises(self):
        sm = self._sm()
        with self.assertRaises(ValueError):
            sm.submit("Task", agent_type="nonexistent_type_xyz")

    def test_submit_depends_on_nonexistent_raises(self):
        sm = self._sm()
        with self.assertRaises(ValueError):
            sm.submit("Task", depends_on=["deadbeef"])

    def test_state_persists_across_instances(self):
        sm1 = _make_sm(self._ws)
        task_id = sm1.submit("Persistent task")

        sm2 = _make_sm(self._ws)
        tasks = sm2.list_tasks()
        ids = [t["id"] for t in tasks]
        self.assertIn(task_id, ids)


# ---------------------------------------------------------------------------
# TestStateTransitions
# ---------------------------------------------------------------------------

class TestStateTransitions(unittest.TestCase):

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self._ws = Path(self._tmpdir.name)

    def tearDown(self):
        self._tmpdir.cleanup()

    def _sm(self):
        return _make_sm(self._ws)

    def _submit_and_start(self, sm, task_text="Test task", agent_type="coding"):
        task_id = sm.submit(task_text, agent_type=agent_type)
        sm.start(task_id, session_id="sess_test", model="claude-opus-4-6")
        return task_id

    def test_start_transitions_queued_to_running(self):
        sm = self._sm()
        task_id = sm.submit("Task A")
        sm.start(task_id, session_id="s1", model="claude-opus-4-6")
        task = sm.get_task(task_id)
        self.assertEqual(task["status"], "running")

    def test_start_increments_agents_running(self):
        sm = self._sm()
        task_id = sm.submit("Task A")
        with sm._lock():
            state_before = sm._load()
        before = state_before["agents"]["running"]
        sm.start(task_id, session_id="s1", model="claude-opus-4-6")
        with sm._lock():
            state_after = sm._load()
        after = state_after["agents"]["running"]
        self.assertEqual(after, before + 1)

    def test_start_non_queued_raises(self):
        sm = self._sm()
        task_id = self._submit_and_start(sm)
        with self.assertRaises(RuntimeError):
            sm.start(task_id, session_id="s2", model="claude-opus-4-6")

    def test_start_unsatisfied_depends_raises(self):
        sm = self._sm()
        dep_id = sm.submit("Dependency")
        task_id = sm.submit("Dependent", depends_on=[dep_id])
        # dep_id is still queued, not done
        with self.assertRaises(RuntimeError):
            sm.start(task_id, session_id="s1", model="claude-opus-4-6")

    def test_complete_transitions_running_to_done(self):
        sm = self._sm()
        task_id = self._submit_and_start(sm)
        sm.complete(task_id, result_summary="All good")
        task = sm.get_task(task_id)
        self.assertEqual(task["status"], "done")

    def test_complete_decrements_agents_running(self):
        sm = self._sm()
        task_id = self._submit_and_start(sm)
        with sm._lock():
            state_running = sm._load()
        running_count = state_running["agents"]["running"]
        sm.complete(task_id)
        with sm._lock():
            state_done = sm._load()
        self.assertEqual(state_done["agents"]["running"], running_count - 1)

    def test_complete_sets_completed_at(self):
        sm = self._sm()
        task_id = self._submit_and_start(sm)
        sm.complete(task_id)
        task = sm.get_task(task_id)
        self.assertIsNotNone(task["completed_at"])

    def test_fail_transitions_running_to_failed(self):
        sm = self._sm()
        task_id = self._submit_and_start(sm)
        sm.fail(task_id, error="Something broke")
        task = sm.get_task(task_id)
        self.assertEqual(task["status"], "failed")

    def test_fail_sets_error(self):
        sm = self._sm()
        task_id = self._submit_and_start(sm)
        sm.fail(task_id, error="Boom!")
        task = sm.get_task(task_id)
        self.assertEqual(task["error"], "Boom!")

    def test_cancel_queued_task(self):
        sm = self._sm()
        task_id = sm.submit("Cancel me")
        sm.cancel(task_id)
        task = sm.get_task(task_id)
        self.assertEqual(task["status"], "cancelled")

    def test_cancel_running_task_raises(self):
        sm = self._sm()
        task_id = self._submit_and_start(sm)
        with self.assertRaises(RuntimeError):
            sm.cancel(task_id)


# ---------------------------------------------------------------------------
# TestDependencies
# ---------------------------------------------------------------------------

class TestDependencies(unittest.TestCase):

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self._ws = Path(self._tmpdir.name)

    def tearDown(self):
        self._tmpdir.cleanup()

    def _sm(self):
        return _make_sm(self._ws)

    def test_ready_to_run_no_deps(self):
        sm = self._sm()
        task_id = sm.submit("No deps")
        ready = sm.ready_to_run()
        ids = [t["id"] for t in ready]
        self.assertIn(task_id, ids)

    def test_ready_to_run_satisfied_deps(self):
        sm = self._sm()
        dep_id = sm.submit("Dep task")
        # Complete dep
        sm.start(dep_id, "s1", "claude-opus-4-6")
        sm.complete(dep_id)
        child_id = sm.submit("Child", depends_on=[dep_id])
        ready = sm.ready_to_run()
        ids = [t["id"] for t in ready]
        self.assertIn(child_id, ids)

    def test_ready_to_run_unsatisfied_deps(self):
        sm = self._sm()
        dep_id = sm.submit("Dep task")  # still queued
        child_id = sm.submit("Child", depends_on=[dep_id])
        ready = sm.ready_to_run()
        ids = [t["id"] for t in ready]
        self.assertNotIn(child_id, ids)

    def test_ready_to_run_failed_deps(self):
        sm = self._sm()
        dep_id = sm.submit("Dep task")
        sm.start(dep_id, "s1", "claude-opus-4-6")
        sm.fail(dep_id, "oops")
        child_id = sm.submit("Child", depends_on=[dep_id])
        ready = sm.ready_to_run()
        ids = [t["id"] for t in ready]
        self.assertNotIn(child_id, ids)

    def test_cycle_detection_direct(self):
        """A task cannot depend on itself."""
        sm = self._sm()
        # First submit a task to get an existing ID, then try to create a
        # self-referential cycle. Since IDs are generated at submit-time, we
        # instead test by patching _has_cycle directly.
        # We'll submit task A, manually grab its id, then try to submit a task
        # that depends on a fake id = new_id (simulate).
        # Simpler: monkeypatch _gen_id to return a fixed value, then submit
        # a task with depends_on=[that_fixed_value] already in state... but
        # the spec says "A depends on A". The cycle detection checks if the
        # new_id appears as a transitive dependency. Since the new task ID is
        # generated at submit time and no existing task has that ID, a direct
        # self-reference is impossible through the public API.
        # We test _has_cycle directly instead.
        tid = "aaaabbbb"
        # A task with ID aaaabbbb that has depends_on=[aaaabbbb]
        result = sm._has_cycle(tid, [tid], {tid: {"depends_on": [tid]}})
        self.assertTrue(result)

    def test_cycle_detection_indirect(self):
        """A→B where B depends on A."""
        sm = self._sm()
        # Simulate: new task is "a", depends on "b"; "b" depends on "a"
        tasks_by_id = {
            "b": {"depends_on": ["a"]},
        }
        result = sm._has_cycle("a", ["b"], tasks_by_id)
        self.assertTrue(result)

    def test_no_false_positive_chain(self):
        """A→B→C linear chain should not be flagged as a cycle."""
        sm = self._sm()
        # Submit A, B, C in order; C depends on B which depends on A
        id_a = sm.submit("Task A")
        id_b = sm.submit("Task B", depends_on=[id_a])
        id_c = sm.submit("Task C", depends_on=[id_b])
        # No exception raised — all three tasks exist
        tasks = sm.list_tasks()
        ids = {t["id"] for t in tasks}
        self.assertIn(id_c, ids)


# ---------------------------------------------------------------------------
# TestMaxConcurrent
# ---------------------------------------------------------------------------

class TestMaxConcurrent(unittest.TestCase):

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self._ws = Path(self._tmpdir.name)

    def tearDown(self):
        self._tmpdir.cleanup()

    def _sm(self):
        return _make_sm(self._ws)

    def test_max_concurrent_blocks_start(self):
        """observer type has max_concurrent=1; starting a second should fail."""
        sm = self._sm()
        id1 = sm.submit("Obs 1", agent_type="observer")
        id2 = sm.submit("Obs 2", agent_type="observer")
        sm.start(id1, "s1", "claude-haiku-4-5-20251001")
        with self.assertRaises(RuntimeError):
            sm.start(id2, "s2", "claude-haiku-4-5-20251001")

    def test_max_concurrent_per_type(self):
        """coding (max 3) and observer (max 1) are independent."""
        sm = self._sm()
        obs_id = sm.submit("Observer task", agent_type="observer")
        code_id = sm.submit("Coding task", agent_type="coding")
        sm.start(obs_id, "s_obs", "claude-haiku-4-5-20251001")
        # coding slot should still be available
        sm.start(code_id, "s_code", "claude-opus-4-6")
        task = sm.get_task(code_id)
        self.assertEqual(task["status"], "running")

    def test_max_concurrent_after_complete_allows_new_start(self):
        """After completing a task, a new one of the same type can start."""
        sm = self._sm()
        id1 = sm.submit("Obs 1", agent_type="observer")
        id2 = sm.submit("Obs 2", agent_type="observer")
        sm.start(id1, "s1", "claude-haiku-4-5-20251001")
        sm.complete(id1)
        # Now the slot is free
        sm.start(id2, "s2", "claude-haiku-4-5-20251001")
        task = sm.get_task(id2)
        self.assertEqual(task["status"], "running")


# ---------------------------------------------------------------------------
# TestReadyToRunOrdering
# ---------------------------------------------------------------------------

class TestReadyToRunOrdering(unittest.TestCase):

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self._ws = Path(self._tmpdir.name)

    def tearDown(self):
        self._tmpdir.cleanup()

    def _sm(self):
        return _make_sm(self._ws)

    def test_ready_sorted_priority_desc(self):
        sm = self._sm()
        id_low = sm.submit("Low priority", priority=2)
        id_high = sm.submit("High priority", priority=9)
        ready = sm.ready_to_run()
        ids = [t["id"] for t in ready]
        self.assertIn(id_low, ids)
        self.assertIn(id_high, ids)
        self.assertLess(ids.index(id_high), ids.index(id_low))

    def test_ready_sorted_created_at_asc_tiebreak(self):
        sm = self._sm()
        id_first = sm.submit("First same priority", priority=5)
        time.sleep(0.01)  # ensure different created_at
        id_second = sm.submit("Second same priority", priority=5)
        ready = sm.ready_to_run()
        ids = [t["id"] for t in ready]
        self.assertLess(ids.index(id_first), ids.index(id_second))


# ---------------------------------------------------------------------------
# TestPurge
# ---------------------------------------------------------------------------

class TestPurge(unittest.TestCase):

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self._ws = Path(self._tmpdir.name)

    def tearDown(self):
        self._tmpdir.cleanup()

    def _sm(self):
        return _make_sm(self._ws)

    def test_purge_removes_old_done(self):
        sm = self._sm()
        ids = []
        for i in range(5):
            tid = sm.submit(f"Task {i}")
            sm.start(tid, f"s{i}", "claude-opus-4-6")
            sm.complete(tid)
            ids.append(tid)
        # keep only 2
        removed = sm.purge_done(keep_last=2)
        self.assertEqual(removed, 3)
        remaining = [t["id"] for t in sm.list_tasks()]
        for rid in ids[:3]:
            self.assertNotIn(rid, remaining)

    def test_purge_keeps_running(self):
        sm = self._sm()
        # Submit and start a running task
        run_id = sm.submit("Running task")
        sm.start(run_id, "s_run", "claude-opus-4-6")
        # Submit done tasks
        for i in range(25):
            tid = sm.submit(f"Done {i}")
            sm.start(tid, f"s{i}", "claude-opus-4-6")
            sm.complete(tid)
        sm.purge_done(keep_last=5)
        task = sm.get_task(run_id)
        self.assertIsNotNone(task)
        self.assertEqual(task["status"], "running")

    def test_purge_returns_count(self):
        sm = self._sm()
        for i in range(10):
            tid = sm.submit(f"Task {i}")
            sm.start(tid, f"s{i}", "claude-opus-4-6")
            sm.complete(tid)
        removed = sm.purge_done(keep_last=3)
        self.assertEqual(removed, 7)


# ---------------------------------------------------------------------------
# TestAtomicWrite
# ---------------------------------------------------------------------------

class TestAtomicWrite(unittest.TestCase):

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self._ws = Path(self._tmpdir.name)

    def tearDown(self):
        self._tmpdir.cleanup()

    def _sm(self):
        return _make_sm(self._ws)

    def test_concurrent_submits(self):
        """10 threads each submit 5 tasks = 50 total; no corruption."""
        ws = self._ws
        # Pre-bootstrap the agent directory so threads don't race on it
        _make_sm(ws)
        errors = []

        def worker(n):
            try:
                sm = _make_sm(ws)
                for i in range(5):
                    sm.submit(f"Thread {n} task {i}")
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(n,)) for n in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual([], errors)
        sm = _make_sm(ws)
        tasks = sm.list_tasks()
        self.assertEqual(len(tasks), 50)
        # Verify no duplicate IDs
        ids = [t["id"] for t in tasks]
        self.assertEqual(len(ids), len(set(ids)))

    def test_lock_timeout(self):
        """Lock held externally causes TimeoutError."""
        ws = self._ws
        lock_path = ws / ".state.lock"
        lock_path.mkdir()
        try:
            with self.assertRaises(TimeoutError):
                with ac._acquire_lock(lock_path, timeout=0.2):
                    pass
        finally:
            try:
                lock_path.rmdir()
            except Exception:
                pass


# ---------------------------------------------------------------------------
# TestAgentDirectory
# ---------------------------------------------------------------------------

class TestAgentDirectory(unittest.TestCase):

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self._ws = Path(self._tmpdir.name)
        # AgentDirectory will bootstrap from defaults
        self._ad = ac.AgentDirectory(Path(self._ws) / "agent-directory.yaml")

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_load_known_type(self):
        cfg = self._ad.get("coding")
        self.assertIn("default_model", cfg)
        self.assertIn("max_concurrent", cfg)

    def test_unknown_type_raises(self):
        with self.assertRaises(KeyError):
            self._ad.get("nonexistent_xyz")

    def test_list_types(self):
        types = self._ad.list_types()
        self.assertIn("coding", types)
        self.assertIn("observer", types)
        self.assertIn("research", types)
        self.assertIn("ops", types)

    def test_resolve_model(self):
        model = self._ad.resolve_model("coding")
        self.assertIsInstance(model, str)
        self.assertTrue(len(model) > 0)

    def test_max_concurrent(self):
        val = self._ad.max_concurrent("observer")
        self.assertEqual(val, 1)


# ---------------------------------------------------------------------------
# TestCLI
# ---------------------------------------------------------------------------

class TestCLI(unittest.TestCase):

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self._ws = Path(self._tmpdir.name)

    def tearDown(self):
        self._tmpdir.cleanup()

    def _cli(self, *args):
        return _run_cli(*args, workspace=self._ws)

    def _parse(self, stdout):
        return json.loads(stdout)

    def test_cli_submit(self):
        code, out, err = self._cli("submit", "--task", "Hello world")
        self.assertEqual(code, 0)
        data = self._parse(out)
        self.assertTrue(data["ok"])
        self.assertIn("task_id", data)
        self.assertEqual(len(data["task_id"]), 8)

    def test_cli_list_empty(self):
        code, out, err = self._cli("list")
        self.assertEqual(code, 0)
        data = self._parse(out)
        self.assertTrue(data["ok"])
        self.assertEqual(data["tasks"], [])

    def test_cli_status(self):
        code, out, err = self._cli("status")
        self.assertEqual(code, 0)
        data = self._parse(out)
        self.assertTrue(data["ok"])
        self.assertIn("counts", data)
        self.assertIn("agents_running", data)

    def test_cli_submit_start_complete_flow(self):
        # Submit
        code, out, _ = self._cli("submit", "--task", "Full lifecycle test")
        self.assertEqual(code, 0)
        task_id = self._parse(out)["task_id"]

        # Start
        code, out, _ = self._cli("start", "--id", task_id, "--session", "sess_abc")
        self.assertEqual(code, 0)
        self.assertTrue(self._parse(out)["ok"])

        # Verify running
        code, out, _ = self._cli("list", "--status", "running")
        running_ids = [t["id"] for t in self._parse(out)["tasks"]]
        self.assertIn(task_id, running_ids)

        # Complete
        code, out, _ = self._cli("complete", "--id", task_id, "--summary", "Done!")
        self.assertEqual(code, 0)
        self.assertTrue(self._parse(out)["ok"])

        # Verify done
        code, out, _ = self._cli("list", "--status", "done")
        done_ids = [t["id"] for t in self._parse(out)["tasks"]]
        self.assertIn(task_id, done_ids)

    def test_cli_error_json(self):
        """Bad input exits 1 and returns {"ok": false, "error": "..."}"""
        code, out, _ = self._cli("submit", "--task", "Task", "--type", "bogus_type_xyz")
        self.assertEqual(code, 1)
        data = self._parse(out)
        self.assertFalse(data["ok"])
        self.assertIn("error", data)

    def test_cli_agents(self):
        code, out, _ = self._cli("agents")
        self.assertEqual(code, 0)
        data = self._parse(out)
        self.assertTrue(data["ok"])
        self.assertIn("agent_types", data)
        types = list(data["agent_types"].keys())
        self.assertGreaterEqual(len(types), 4)
        for expected in ("coding", "observer", "research", "ops"):
            self.assertIn(expected, types)


# ---------------------------------------------------------------------------
# TestWiringHelpers
# ---------------------------------------------------------------------------

class TestWiringHelpers(unittest.TestCase):

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self._ws = Path(self._tmpdir.name)

    def tearDown(self):
        self._tmpdir.cleanup()

    def _sm(self):
        return _make_sm(self._ws)

    def _cli(self, *args):
        return _run_cli(*args, workspace=self._ws)

    def _parse(self, stdout):
        return json.loads(stdout)

    def test_find_by_session_found(self):
        """submit→start with session_id, find_by_session returns it."""
        sm = self._sm()
        task_id = sm.submit("Find me by session", agent_type="coding")
        sm.start(task_id, session_id="test-session-abc", model="claude-opus-4-6")
        found = sm.find_by_session("test-session-abc")
        self.assertIsNotNone(found)
        self.assertEqual(found["id"], task_id)
        self.assertEqual(found["session_id"], "test-session-abc")

    def test_find_by_session_not_found(self):
        """find_by_session on unknown session_id returns None."""
        sm = self._sm()
        sm.submit("Some task", agent_type="coding")
        result = sm.find_by_session("no-such-session-xyz")
        self.assertIsNone(result)

    def test_find_by_session_cli(self):
        """CLI find-session --session <id> returns ok:true with task."""
        sm = self._sm()
        task_id = sm.submit("CLI find session test", agent_type="coding")
        sm.start(task_id, session_id="cli-session-999", model="claude-opus-4-6")
        code, out, _ = self._cli("find-session", "--session", "cli-session-999")
        self.assertEqual(code, 0)
        data = self._parse(out)
        self.assertTrue(data["ok"])
        self.assertIsNotNone(data["task"])
        self.assertEqual(data["task"]["id"], task_id)

    def test_timeout_check_no_overdue(self):
        """Running task within timeout is not returned."""
        sm = self._sm()
        task_id = sm.submit("Fresh task", agent_type="coding")
        sm.start(task_id, session_id="s-fresh", model="claude-opus-4-6")
        overdue = sm.timeout_check()
        ids = [t["id"] for t in overdue]
        self.assertNotIn(task_id, ids)

    def test_timeout_check_overdue(self):
        """Running task past timeout IS returned."""
        sm = self._sm()
        task_id = sm.submit("Overdue task", agent_type="coding")
        sm.start(task_id, session_id="s-overdue", model="claude-opus-4-6")
        # Manually backdate started_at to simulate timeout
        with sm._lock():
            state = sm._load()
            for t in state["tasks"]:
                if t["id"] == task_id:
                    from datetime import timedelta
                    past = datetime.now(timezone.utc).astimezone() - timedelta(seconds=1000)
                    t["started_at"] = past.isoformat()
            sm._save(state)
        overdue = sm.timeout_check()
        ids = [t["id"] for t in overdue]
        self.assertIn(task_id, ids)

    def test_timeout_check_cli(self):
        """CLI timeout-check returns ok:true with tasks list."""
        code, out, _ = self._cli("timeout-check")
        self.assertEqual(code, 0)
        data = self._parse(out)
        self.assertTrue(data["ok"])
        self.assertIn("tasks", data)
        self.assertIsInstance(data["tasks"], list)

    def test_start_without_session(self):
        """start with session_id=None succeeds."""
        sm = self._sm()
        task_id = sm.submit("No session task", agent_type="observer")
        # Pass None explicitly — should not raise
        sm.start(task_id, session_id=None, model="claude-haiku-4-5-20251001")
        task = sm.get_task(task_id)
        self.assertEqual(task["status"], "running")
        self.assertIsNone(task["session_id"])

    def test_start_without_session_cli(self):
        """CLI start --id <id> (no --session) succeeds."""
        sm = self._sm()
        task_id = sm.submit("CLI no session", agent_type="observer")
        code, out, _ = self._cli("start", "--id", task_id)
        self.assertEqual(code, 0)
        data = self._parse(out)
        self.assertTrue(data["ok"])
        task = sm.get_task(task_id)
        self.assertEqual(task["status"], "running")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
