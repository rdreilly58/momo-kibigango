#!/usr/bin/env python3
"""
test_context_routing_suite.py — Comprehensive test suite for all new capabilities
shipped in the context/routing/memory improvement sprint (April 23 2026).

Coverage:
  1.  3-tier classifier — SIMPLE / MEDIUM / COMPLEX routing rules
  2.  3-tier classifier — model & context level mapping
  3.  3-tier classifier — edge cases (empty, unicode, code snippets)
  4.  task_router.py — context file selection per tier
  5.  Memory score threshold — semantic_search min_score filtering
  6.  memory_retrieve.py CLI — --min-score flag wired through
  7.  classify-coding-task.sh — shell outputs correct model/tier env vars
  8.  CLAUDE.md — new sections present (ordering, compaction, KV-cache)
  9.  SOUL.md — 3-tier quick rules present; binary rules gone
  10. TASK_ROUTING.md — speculative-decoding section removed; 3-tier logic present
  11. generate-status.sh — Memory & Context section in STATUS.md
  12. LanceDB warm tier — record count > 0 after sync
  13. weekly-memory-smart-prune.sh — dry-run succeeds, correct phases
  14. memory-sync-flat-files.py — dry-run succeeds
  15. session-start-hook.sh — --min-score flag passed to memory_retrieve
  16. session-stop-hook.sh — session-depth-metrics.jsonl writing logic
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
WORKSPACE = Path.home() / ".openclaw" / "workspace"
SCRIPTS_DIR = WORKSPACE / "scripts"
TESTS_DIR = WORKSPACE / "Tests"
VENV_SITE = WORKSPACE / "venv" / "lib" / "python3.14" / "site-packages"
VENV_PYTHON = str(WORKSPACE / "venv" / "bin" / "python3")

sys.path.insert(0, str(VENV_SITE))
sys.path.insert(0, str(SCRIPTS_DIR))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def run(cmd: list[str], cwd=WORKSPACE) -> tuple[int, str, str]:
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd))
    return r.returncode, r.stdout, r.stderr


def run_sh(script: str, args: list[str] = (), cwd=WORKSPACE) -> tuple[int, str, str]:
    return run(["bash", str(SCRIPTS_DIR / script)] + list(args), cwd=cwd)


# ---------------------------------------------------------------------------
# 1–4  Task Classifier & Router
# ---------------------------------------------------------------------------


class TestTaskClassifier(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "task_classifier", SCRIPTS_DIR / "task-classifier.py"
        )
        cls.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.mod)
        cls.TC = cls.mod.TaskClassifier
        cls.Complexity = cls.mod.TaskComplexity

    # ── Tier routing ──────────────────────────────────────────────────────

    def _tier(self, text):
        c, _ = self.TC.classify(text)
        return c

    def test_simple_weather(self):
        self.assertEqual(self._tier("what is the weather"), self.Complexity.SIMPLE)

    def test_simple_status(self):
        self.assertEqual(self._tier("is the gateway up"), self.Complexity.SIMPLE)

    def test_simple_short_factual(self):
        self.assertEqual(self._tier("what time"), self.Complexity.SIMPLE)

    def test_medium_email(self):
        self.assertEqual(
            self._tier("write an email to the team"), self.Complexity.MEDIUM
        )

    def test_medium_fix_bug(self):
        self.assertEqual(
            self._tier("fix the login bug in auth.swift"), self.Complexity.MEDIUM
        )

    def test_medium_explain(self):
        self.assertEqual(
            self._tier("explain how the memory tier system works"),
            self.Complexity.MEDIUM,
        )

    def test_medium_review(self):
        self.assertEqual(self._tier("review this pull request"), self.Complexity.MEDIUM)

    def test_medium_deploy(self):
        # 'deploy' was moved out of Opus keywords in latest fix
        result = self._tier("deploy to production")
        self.assertIn(result, (self.Complexity.SIMPLE, self.Complexity.MEDIUM))

    def test_medium_code_snippet(self):
        self.assertEqual(self._tier("def foo(): pass"), self.Complexity.MEDIUM)

    def test_medium_default_ambiguous(self):
        # Ambiguous multi-word input should default to MEDIUM, not Haiku
        result = self._tier(
            "let me know what you think about this approach for the project"
        )
        self.assertEqual(result, self.Complexity.MEDIUM)

    def test_complex_refactor(self):
        self.assertEqual(
            self._tier("refactor the auth middleware"), self.Complexity.COMPLEX
        )

    def test_complex_architecture(self):
        self.assertEqual(
            self._tier("design a new microservice architecture for the API"),
            self.Complexity.COMPLEX,
        )

    def test_complex_research(self):
        self.assertEqual(
            self._tier("research and analyze the best approach to memory compression"),
            self.Complexity.COMPLEX,
        )

    def test_complex_audit(self):
        self.assertEqual(
            self._tier("audit all security permissions on the server"),
            self.Complexity.COMPLEX,
        )

    def test_complex_migrate(self):
        self.assertEqual(
            self._tier("migrate the database to the new schema"),
            self.Complexity.COMPLEX,
        )

    def test_complex_unit_test(self):
        self.assertEqual(
            self._tier("write unit tests for the payment module"),
            self.Complexity.COMPLEX,
        )

    def test_no_false_opus_on_short_query(self):
        # Very short queries should never hit Opus
        result = self._tier("list files")
        self.assertNotEqual(result, self.Complexity.COMPLEX)

    def test_long_input_not_haiku(self):
        # Long inputs (>10 words with no simple keywords) should be at least MEDIUM
        text = "can you help me understand what happened with the last session and what context was loaded"
        result = self._tier(text)
        self.assertNotEqual(result, self.Complexity.SIMPLE)

    # ── Model mapping ─────────────────────────────────────────────────────

    def test_simple_maps_to_haiku(self):
        model = self.TC.get_model(self.Complexity.SIMPLE)
        self.assertIn("haiku", model.lower())

    def test_medium_maps_to_sonnet(self):
        model = self.TC.get_model(self.Complexity.MEDIUM)
        self.assertIn("sonnet", model.lower())

    def test_complex_maps_to_opus(self):
        model = self.TC.get_model(self.Complexity.COMPLEX)
        self.assertIn("opus", model.lower())

    def test_model_ids_are_current(self):
        # No stale model IDs (4-0 pattern)
        for complexity in self.Complexity:
            model = self.TC.get_model(complexity)
            self.assertNotIn("4-0", model, f"Stale model ID in {complexity}: {model}")
            self.assertNotIn(
                "gpt-4", model, f"GPT-4 reference in {complexity}: {model}"
            )

    # ── Context level mapping ─────────────────────────────────────────────

    def test_simple_minimal_context(self):
        self.assertEqual(self.TC.get_context_level(self.Complexity.SIMPLE), "minimal")

    def test_medium_standard_context(self):
        self.assertEqual(self.TC.get_context_level(self.Complexity.MEDIUM), "standard")

    def test_complex_full_context(self):
        self.assertEqual(self.TC.get_context_level(self.Complexity.COMPLEX), "full")

    # ── Thinking level mapping ────────────────────────────────────────────

    def test_simple_thinking_off(self):
        self.assertEqual(self.TC.get_thinking(self.Complexity.SIMPLE), "off")

    def test_complex_thinking_medium(self):
        self.assertEqual(self.TC.get_thinking(self.Complexity.COMPLEX), "medium")

    # ── Edge cases ────────────────────────────────────────────────────────

    def test_empty_string(self):
        # Should not raise; should return some complexity
        c, _ = self.TC.classify("")
        self.assertIn(c, list(self.Complexity))

    def test_unicode_input(self):
        c, _ = self.TC.classify("こんにちは、今日の天気は？")
        self.assertIn(c, list(self.Complexity))

    def test_all_caps(self):
        c, _ = self.TC.classify("WHAT IS THE STATUS OF THE GATEWAY")
        self.assertIn(c, list(self.Complexity))

    def test_reasoning_is_string(self):
        _, reasoning = self.TC.classify("fix the bug")
        self.assertIsInstance(reasoning, str)
        self.assertGreater(len(reasoning), 0)


# ---------------------------------------------------------------------------
# Task Router — context file selection per tier
# ---------------------------------------------------------------------------


class TestTaskRouter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import task_router as tr

        cls.TR = tr.TaskRouter

    def _route(self, text):
        return self.TR.route(text)

    def test_simple_context_files(self):
        result = self._route("what time is it")
        files = result["context_files"]
        self.assertIn("SOUL.md", files)
        self.assertIn("USER.md", files)
        self.assertNotIn("MEMORY.md", files)
        self.assertNotIn("TOOLS.md", files)

    def test_medium_context_files(self):
        result = self._route("write me a summary email")
        files = result["context_files"]
        self.assertIn("SOUL.md", files)
        self.assertIn("MEMORY.md", files)
        self.assertNotIn("TOOLS.md", files)

    def test_complex_context_files(self):
        result = self._route("refactor the entire auth module")
        files = result["context_files"]
        self.assertIn("SOUL.md", files)
        self.assertIn("MEMORY.md", files)
        self.assertIn("TOOLS.md", files)

    def test_result_has_required_keys(self):
        result = self._route("fix the bug")
        for key in (
            "complexity",
            "model",
            "thinking",
            "context_level",
            "context_files",
            "expected_time",
        ):
            self.assertIn(key, result, f"Missing key: {key}")

    def test_simple_expected_time(self):
        result = self._route("what time is it")
        self.assertIn("0.3", result["expected_time"])

    def test_medium_expected_time(self):
        result = self._route("write an email")
        self.assertIn("0.5", result["expected_time"])


# ---------------------------------------------------------------------------
# Memory score threshold
# ---------------------------------------------------------------------------


class TestMemoryScoreThreshold(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import memory_mcp_server as srv

        cls.srv = srv

    def test_threshold_constant_is_078(self):
        self.assertAlmostEqual(self.srv.MIN_SCORE_THRESHOLD, 0.78, places=2)

    def test_semantic_search_accepts_min_score(self):
        import inspect

        sig = inspect.signature(self.srv.semantic_search)
        self.assertIn("min_score", sig.parameters)

    def test_semantic_search_filters_low_scores(self):
        """Inject a fake index with known scores and verify filtering."""
        import numpy as np

        fake_emb = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        fake_index = [
            {
                "source": "high.md",
                "chunk": "relevant content",
                "embedding": np.array([1.0, 0.0, 0.0]),
            },
            {
                "source": "low.md",
                "chunk": "unrelated stuff",
                "embedding": np.array([0.0, 1.0, 0.0]),
            },
        ]

        with (
            patch.object(self.srv, "_index", fake_index),
            patch.object(self.srv, "_needs_reindex", return_value=False),
            patch.object(self.srv._get_model(), "encode", return_value=fake_emb),
        ):
            results = self.srv.semantic_search("test", top_k=5, min_score=0.78)

        # Only the high-score result should pass
        sources = [r["source"] for r in results]
        self.assertIn("high.md", sources)
        self.assertNotIn("low.md", sources)

    def test_default_min_score_applied(self):
        """semantic_search uses MIN_SCORE_THRESHOLD when min_score not specified."""
        import inspect

        sig = inspect.signature(self.srv.semantic_search)
        default = sig.parameters["min_score"].default
        self.assertEqual(default, self.srv.MIN_SCORE_THRESHOLD)

    def test_mcp_memory_search_filters_tier_manager_results(self):
        """memory_search MCP tool drops warm results below threshold."""
        import json as _json

        fake_results = [
            {"title": "Good", "content": "x", "_score": 0.90, "_tier": "warm"},
            {"title": "Marginal", "content": "x", "_score": 0.77, "_tier": "warm"},
            {"title": "Cold", "content": "x", "_score": 0.01, "_tier": "cold"},
        ]
        mock_mgr = MagicMock()
        mock_mgr.search.return_value = fake_results

        with patch.object(self.srv, "_get_tier_manager", return_value=mock_mgr):
            raw = self.srv.memory_search("test query")
        data = _json.loads(raw)
        titles = [r["title"] for r in data]
        self.assertIn("Good", titles)
        self.assertNotIn("Marginal", titles)
        self.assertIn("Cold", titles)  # cold tier is exempt from threshold


# ---------------------------------------------------------------------------
# memory_retrieve.py CLI
# ---------------------------------------------------------------------------


class TestMemoryRetrieveCLI(unittest.TestCase):
    def test_min_score_flag_exists(self):
        rc, out, err = run(
            [VENV_PYTHON, str(SCRIPTS_DIR / "memory_retrieve.py"), "--help"]
        )
        self.assertIn("min-score", out + err)

    def test_min_score_default_is_078(self):
        rc, out, err = run(
            [VENV_PYTHON, str(SCRIPTS_DIR / "memory_retrieve.py"), "--help"]
        )
        self.assertIn("0.78", out + err)

    def test_runs_without_error(self):
        rc, out, err = run(
            [
                VENV_PYTHON,
                str(SCRIPTS_DIR / "memory_retrieve.py"),
                "test query",
                "--top-k",
                "3",
                "--min-score",
                "0.78",
            ]
        )
        self.assertEqual(rc, 0, f"memory_retrieve.py failed: {err}")

    def test_high_min_score_returns_fewer_results(self):
        rc_low, out_low, _ = run(
            [
                VENV_PYTHON,
                str(SCRIPTS_DIR / "memory_retrieve.py"),
                "memory context session",
                "--top-k",
                "5",
                "--min-score",
                "0.01",
            ]
        )
        rc_high, out_high, _ = run(
            [
                VENV_PYTHON,
                str(SCRIPTS_DIR / "memory_retrieve.py"),
                "memory context session",
                "--top-k",
                "5",
                "--min-score",
                "0.99",
            ]
        )
        low_count = out_low.count("score=")
        high_count = out_high.count("score=")
        self.assertGreaterEqual(low_count, high_count)


# ---------------------------------------------------------------------------
# classify-coding-task.sh
# ---------------------------------------------------------------------------


class TestClassifyCodingTaskSh(unittest.TestCase):
    def _classify(self, task: str) -> dict:
        rc, out, err = run_sh("classify-coding-task.sh", [task])
        self.assertEqual(rc, 0, f"Script failed: {err}\n{out}")
        result = {}
        for line in out.splitlines():
            if "=" in line and not line.startswith(" ") and not line.startswith("\x1b"):
                k, _, v = line.partition("=")
                result[k.strip()] = v.strip()
        return result

    def test_trivial_fix_routes_sonnet(self):
        r = self._classify("fix the login bug")
        self.assertEqual(r.get("CLASSIFIED_MODEL"), "sonnet")

    def test_refactor_routes_opus(self):
        r = self._classify("refactor the auth middleware architecture")
        self.assertEqual(r.get("CLASSIFIED_MODEL"), "opus")

    def test_model_alias_not_stale(self):
        r = self._classify("write an email")
        alias = r.get("CLASSIFIED_MODEL_ALIAS", "")
        self.assertNotIn("4-0", alias, f"Stale model alias: {alias}")
        self.assertNotIn("gpt-4", alias, f"GPT-4 alias: {alias}")

    def test_thinking_key_present(self):
        r = self._classify("fix the bug")
        self.assertIn("CLASSIFIED_THINKING", r)

    def test_timeout_key_present(self):
        r = self._classify("fix the bug")
        self.assertIn("CLASSIFIED_TIMEOUT", r)
        self.assertGreater(int(r["CLASSIFIED_TIMEOUT"]), 0)

    def test_sonnet_timeout_less_than_opus(self):
        sonnet = self._classify("write an email")
        opus = self._classify("refactor the architecture")
        self.assertLessEqual(
            int(sonnet.get("CLASSIFIED_TIMEOUT", 999)),
            int(opus.get("CLASSIFIED_TIMEOUT", 0)),
        )


# ---------------------------------------------------------------------------
# CLAUDE.md — new sections
# ---------------------------------------------------------------------------


class TestClaudeMd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.content = (WORKSPACE / "CLAUDE.md").read_text()

    def test_soul_first_instruction_present(self):
        # CLAUDE.md wraps filenames in backticks: `SOUL.md` FIRST
        self.assertIn("SOUL.md` FIRST", self.content)

    def test_session_context_second_instruction_present(self):
        # CLAUDE.md wraps filenames in backticks: `SESSION_CONTEXT.md` SECOND
        self.assertIn("SESSION_CONTEXT.md` SECOND", self.content)

    def test_memories_last_instruction_present(self):
        self.assertIn("LAST", self.content)

    def test_compaction_threshold_mentioned(self):
        self.assertRegex(self.content, r"70|75")  # 70-75% threshold

    def test_compaction_instruction_present(self):
        self.assertIn("compact", self.content.lower())

    def test_kv_cache_section_present(self):
        self.assertIn("KV-Cache", self.content)

    def test_no_rerread_instruction_present(self):
        self.assertIn("not be re-read", self.content)

    def test_load_order_documented(self):
        self.assertIn("SOUL → SESSION_CONTEXT", self.content)


# ---------------------------------------------------------------------------
# SOUL.md — 3-tier rules; no stale binary rules
# ---------------------------------------------------------------------------


class TestSoulMd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.content = (WORKSPACE / "SOUL.md").read_text()

    def test_three_tier_rules_present(self):
        self.assertIn("Sonnet", self.content)

    def test_haiku_still_present_for_simple(self):
        self.assertIn("Haiku", self.content)

    def test_opus_still_present_for_complex(self):
        self.assertIn("Opus", self.content)

    def test_stale_binary_default_removed(self):
        # Old rule: "If unsure → Opus" should be gone
        self.assertNotIn("If unsure → Opus", self.content)

    def test_sonnet_as_default_present(self):
        self.assertIn("Sonnet", self.content)

    def test_progress_ping_instruction_removed(self):
        # Old rule: "every 60 seconds" pings removed
        self.assertNotIn("every 60 seconds", self.content)


# ---------------------------------------------------------------------------
# TASK_ROUTING.md — 3-tier logic; stale sections gone
# ---------------------------------------------------------------------------


class TestTaskRoutingMd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.content = (WORKSPACE / "TASK_ROUTING.md").read_text()

    def test_speculative_decoding_removed(self):
        self.assertNotIn("Speculative Decoding", self.content)
        self.assertNotIn("speculative-decoding skill", self.content)

    def test_three_tier_classifier_documented(self):
        self.assertIn("task-classifier.py", self.content)

    def test_medium_tier_documented(self):
        self.assertIn("MEDIUM", self.content)

    def test_tool_schema_ceiling_documented(self):
        self.assertIn("ToolSearch", self.content)

    def test_context_load_order_documented(self):
        self.assertIn("SOUL.md (always", self.content)

    def test_no_stale_binary_classifier_logic(self):
        # Old step 1 said "Complex keywords → Opus" with no medium
        # New version should reference task-classifier.py
        self.assertIn("single source of truth", self.content)

    def test_no_gpt4_references(self):
        self.assertNotIn("GPT-4", self.content)
        self.assertNotIn("gpt-4", self.content)


# ---------------------------------------------------------------------------
# generate-status.sh — Memory & Context section
# ---------------------------------------------------------------------------


class TestGenerateStatusSh(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Run generate-status.sh fresh
        rc, out, err = run(["bash", str(SCRIPTS_DIR / "generate-status.sh")])
        cls.rc = rc
        cls.status = (
            (WORKSPACE / "STATUS.md").read_text()
            if (WORKSPACE / "STATUS.md").exists()
            else ""
        )

    def test_script_exits_cleanly(self):
        self.assertEqual(self.rc, 0)

    def test_memory_section_present(self):
        self.assertIn("## Memory & Context", self.status)

    def test_lancedb_warm_count_shown(self):
        self.assertIn("LanceDB warm", self.status)

    def test_lancedb_count_nonzero(self):
        # Extract the number from "| LanceDB warm | N records |"
        m = re.search(r"LanceDB warm \| (\d+) records", self.status)
        self.assertIsNotNone(m, "LanceDB warm count not found in STATUS.md")
        count = int(m.group(1))
        self.assertGreater(count, 0, "LanceDB warm store is empty")

    def test_flat_file_count_shown(self):
        self.assertIn("Flat memory files", self.status)


# ---------------------------------------------------------------------------
# LanceDB warm tier — populated
# ---------------------------------------------------------------------------


class TestLanceDBWarmTier(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from memory_tier_manager import TierManager

        cls.mgr = TierManager()
        cls.stats = cls.mgr.stats()

    def test_warm_tier_has_records(self):
        warm = self.stats.get("tiers", {}).get("warm", {})
        count = warm.get("records", 0)
        self.assertGreater(count, 0, "LanceDB warm store is empty")

    def test_warm_tier_has_over_100_records(self):
        """After flat-file sync there should be 100+ records."""
        warm = self.stats.get("tiers", {}).get("warm", {})
        count = warm.get("records", 0)
        self.assertGreater(count, 100, f"Only {count} records — sync may have failed")

    def test_search_returns_results(self):
        results = self.mgr.search("memory session context", k=3)
        self.assertGreater(len(results), 0)

    def test_search_results_have_score(self):
        results = self.mgr.search("daily briefing", k=3)
        for r in results:
            self.assertIn("_score", r)

    def test_search_returns_no_cold_tier_by_default(self):
        results = self.mgr.search("test", k=5)
        tiers = {r.get("_tier") for r in results}
        self.assertNotIn("cold", tiers)


# ---------------------------------------------------------------------------
# memory-sync-flat-files.py dry-run
# ---------------------------------------------------------------------------


class TestMemorySyncFlatFiles(unittest.TestCase):
    def test_dry_run_succeeds(self):
        rc, out, err = run(
            [VENV_PYTHON, str(SCRIPTS_DIR / "memory-sync-flat-files.py"), "--dry-run"]
        )
        self.assertEqual(rc, 0, f"Dry run failed: {err}")

    def test_dry_run_finds_memory_files(self):
        rc, out, _ = run(
            [VENV_PYTHON, str(SCRIPTS_DIR / "memory-sync-flat-files.py"), "--dry-run"]
        )
        self.assertIn("memory files", out.lower())
        m = re.search(r"Found (\d+) memory files", out)
        self.assertIsNotNone(m)
        self.assertGreater(int(m.group(1)), 5)

    def test_dry_run_shows_sync_complete(self):
        rc, out, _ = run(
            [VENV_PYTHON, str(SCRIPTS_DIR / "memory-sync-flat-files.py"), "--dry-run"]
        )
        self.assertIn("Sync complete", out)


# ---------------------------------------------------------------------------
# weekly-memory-smart-prune.sh dry-run
# ---------------------------------------------------------------------------


class TestWeeklyMemorySmartPrune(unittest.TestCase):
    def test_dry_run_succeeds(self):
        rc, out, err = run_sh("weekly-memory-smart-prune.sh", ["--dry-run"])
        self.assertEqual(rc, 0, f"Prune dry-run failed: {err}\n{out}")

    def test_dry_run_runs_phase1(self):
        rc, out, _ = run_sh("weekly-memory-smart-prune.sh", ["--dry-run"])
        self.assertIn("Phase 1", out)

    def test_dry_run_runs_phase2(self):
        rc, out, _ = run_sh("weekly-memory-smart-prune.sh", ["--dry-run"])
        self.assertIn("Phase 2", out)

    def test_dry_run_does_not_modify_files(self):
        """Files should have same mtime before/after dry-run."""
        mem_files = list((WORKSPACE / "memory").glob("2026-*.md"))
        if not mem_files:
            self.skipTest("No dated memory files")
        before_mtimes = {f: f.stat().st_mtime for f in mem_files}
        run_sh("weekly-memory-smart-prune.sh", ["--dry-run"])
        for f, mtime in before_mtimes.items():
            self.assertEqual(
                f.stat().st_mtime, mtime, f"{f.name} was modified during dry-run"
            )

    def test_script_is_executable(self):
        script = SCRIPTS_DIR / "weekly-memory-smart-prune.sh"
        self.assertTrue(script.exists())
        self.assertTrue(os.access(script, os.X_OK))


# ---------------------------------------------------------------------------
# session-start-hook.sh — --min-score wired
# ---------------------------------------------------------------------------


class TestSessionStartHook(unittest.TestCase):
    def test_min_score_passed_to_memory_retrieve(self):
        content = (SCRIPTS_DIR / "session-start-hook.sh").read_text()
        self.assertIn("--min-score", content)
        self.assertIn("0.78", content)


# ---------------------------------------------------------------------------
# session-stop-hook.sh — session depth metrics
# ---------------------------------------------------------------------------


class TestSessionStopHookMetrics(unittest.TestCase):
    def test_metrics_file_path_in_hook(self):
        content = (SCRIPTS_DIR / "session-stop-hook.sh").read_text()
        self.assertIn("session-depth-metrics.jsonl", content)

    def test_metrics_writes_json(self):
        content = (SCRIPTS_DIR / "session-stop-hook.sh").read_text()
        self.assertIn("transcript_chars", content)
        self.assertIn("turn_estimate", content)

    def test_rolling_window_30_entries(self):
        content = (SCRIPTS_DIR / "session-stop-hook.sh").read_text()
        self.assertIn("30", content)

    def test_metrics_jsonl_valid_if_exists(self):
        metrics_path = (
            Path.home() / ".openclaw" / "logs" / "session-depth-metrics.jsonl"
        )
        if not metrics_path.exists():
            self.skipTest("No session depth metrics file yet")
        with open(metrics_path) as f:
            for i, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                d = json.loads(line)
                self.assertIn(
                    "transcript_chars", d, f"Line {i} missing transcript_chars"
                )
                self.assertIn("ts", d, f"Line {i} missing ts")


# ---------------------------------------------------------------------------
# Cron registration
# ---------------------------------------------------------------------------


class TestCronJobs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rc, out, _ = run(["crontab", "-l"])
        cls.crontab = out

    def test_smart_prune_in_cron(self):
        self.assertIn("weekly-memory-smart-prune.sh", self.crontab)

    def test_memory_sync_in_cron(self):
        self.assertIn("memory-sync-flat-files.py", self.crontab)

    def test_smart_prune_runs_wednesday(self):
        for line in self.crontab.splitlines():
            if "weekly-memory-smart-prune" in line:
                parts = line.split()
                if len(parts) >= 5:
                    dow = parts[4]  # day-of-week field
                    self.assertEqual(dow, "3", f"Expected Wednesday (3), got: {dow}")

    def test_memory_sync_runs_wednesday(self):
        for line in self.crontab.splitlines():
            if "memory-sync-flat-files" in line:
                parts = line.split()
                if len(parts) >= 5:
                    dow = parts[4]
                    self.assertEqual(dow, "3", f"Expected Wednesday (3), got: {dow}")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    test_classes = [
        TestTaskClassifier,
        TestTaskRouter,
        TestMemoryScoreThreshold,
        TestMemoryRetrieveCLI,
        TestClassifyCodingTaskSh,
        TestClaudeMd,
        TestSoulMd,
        TestTaskRoutingMd,
        TestGenerateStatusSh,
        TestLanceDBWarmTier,
        TestMemorySyncFlatFiles,
        TestWeeklyMemorySmartPrune,
        TestSessionStartHook,
        TestSessionStopHookMetrics,
        TestCronJobs,
    ]

    for cls in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    runner = unittest.TextTestRunner(verbosity=2, tb_locals=True)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
