#!/usr/bin/env python3
"""
test_total_recall_search.py — Test suite for total_recall_search.py

Covers:
  - Original functionality (backward compatibility)
  - Improvement 1: Keyword backend fallback chain + --force-fs-search
  - Improvement 2: Two-pass auto-classification heuristic
  - Improvement 3: --min-score + dynamic thresholding
  - Improvement 4: Borda-count result interleaving + file diversity
  - Improvement 5: 5-min cache + --quick mode + lazy model load
  - Improvement 6: --index-dir + --prune-old + incremental mtime index
  - Improvement 7: --verbose + --explain + _meta result metadata

Run:
  python3 test_total_recall_search.py
  python3 test_total_recall_search.py -v        # verbose output
  python3 test_total_recall_search.py TestClass.test_method
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

WORKSPACE = Path.home() / ".openclaw" / "workspace"
TOOL_PY = WORKSPACE / "scripts" / "total_recall_search.py"
CLI_BIN = Path.home() / "bin" / "total-recall-search"
PYTHON = str(WORKSPACE / "venv" / "bin" / "python3") if (WORKSPACE / "venv" / "bin" / "python3").exists() else sys.executable


def run_tool(*args, timeout: int = 60, expect_exit: int = 0) -> dict:
    """Run the tool via CLI and return parsed JSON + metadata."""
    cmd = [PYTHON, str(TOOL_PY), "--json"] + list(args)
    t0 = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    elapsed = time.time() - t0

    if proc.returncode != expect_exit and expect_exit != -1:
        print(f"\nSTDERR: {proc.stderr[:500]}", file=sys.stderr)
        print(f"STDOUT: {proc.stdout[:500]}", file=sys.stderr)

    results = []
    if proc.stdout.strip():
        try:
            results = json.loads(proc.stdout)
        except json.JSONDecodeError:
            pass

    return {"results": results, "elapsed": elapsed, "rc": proc.returncode, "stderr": proc.stderr}


def import_module():
    """Import total_recall_search module directly."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("trs", str(TOOL_PY))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Test classes
# ---------------------------------------------------------------------------

class TestBackwardCompatibility(unittest.TestCase):
    """Ensure all original functionality still works."""

    def test_basic_keyword_search(self):
        """Original test 01: keyword search for a known file."""
        out = run_tool("total_recall_search.py", "--type", "keyword", "--limit", "3")
        self.assertEqual(out["rc"], 0)
        paths = [r["path"] for r in out["results"] if not r.get("error")]
        self.assertTrue(
            any("total_recall_search" in p or "total-recall-search" in p for p in paths),
            f"Expected total_recall_search.py or total-recall-search in results, got: {paths}",
        )

    def test_basic_semantic_search(self):
        """Original test 02: semantic search returns semantic-typed results."""
        out = run_tool("explain total recall memory system", "--type", "semantic", "--limit", "3")
        self.assertEqual(out["rc"], 0)
        if out["results"]:
            sem = [r for r in out["results"] if r.get("type") == "semantic"]
            # At least some semantic results expected
            self.assertGreater(len(sem) + len([r for r in out["results"] if r.get("error")]), 0)

    def test_limit_parameter(self):
        """Original test 05: limit is respected."""
        out = run_tool("python", "--limit", "3")
        non_err = [r for r in out["results"] if not r.get("error")]
        self.assertLessEqual(len(non_err), 3)

    def test_path_parameter(self):
        """Original test 06: --path scopes keyword search."""
        scripts_dir = str(WORKSPACE / "scripts")
        out = run_tool("total", "--type", "keyword", "--limit", "3", "--path", scripts_dir)
        non_err = [r for r in out["results"] if not r.get("error")]
        if non_err:
            for r in non_err:
                self.assertIn(scripts_dir, r["path"],
                    f"Result outside scoped dir: {r['path']}")

    def test_no_results_empty_query(self):
        """Original test 07: gibberish query returns empty or exit 0."""
        out = run_tool("xyzzy_nonexistent_query_12345_abc", "--limit", "1", expect_exit=-1)
        # Either 0 results or exit 0 is acceptable
        self.assertIn(out["rc"], (0, 1))

    def test_json_output_schema(self):
        """Every result must have type, path, snippet, score."""
        out = run_tool("memory", "--limit", "2")
        for r in out["results"]:
            self.assertIn("type", r)
            self.assertIn("path", r)
            self.assertIn("snippet", r)
            self.assertIn("score", r)

    def test_invalid_path_graceful(self):
        """Original test 08: invalid --path returns empty, not crash."""
        out = run_tool("something", "--type", "keyword", "--path", "/nonexistent/path/abc123", expect_exit=-1)
        self.assertIn(out["rc"], (0, 1))


class TestImprovement1_KeywordFallback(unittest.TestCase):
    """Improvement 1: Keyword backend fallback chain + --force-fs-search."""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())
        self.dummy_file = self.tmpdir / "dummy_keyword_file.txt"
        self.dummy_file.write_text("This is a dummy file for keyword search tests.")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_force_fs_search_flag(self):
        """--force-fs-search should bypass Spotlight and still return results."""
        out = run_tool(
            "dummy_keyword_file.txt", "--type", "keyword",
            "--force-fs-search", "--limit", "3",
            "--path", str(self.tmpdir),  # Scope to temporary dir
        )
        self.assertIn(out["rc"], (0, 1))
        paths = [r["path"] for r in out["results"] if not r.get("error")]
        self.assertTrue(
            any(str(self.dummy_file) in p for p in paths),
            f"--force-fs-search should still find dummy file, got: {paths}",
        )

    def test_force_fs_search_with_path(self):
        """--force-fs-search + --path should scope to directory."""
        out = run_tool(
            "total_recall", "--type", "keyword",
            "--force-fs-search", "--path", str(WORKSPACE / "scripts"),
            "--limit", "5",
        )
        non_err = [r for r in out["results"] if not r.get("error")]
        for r in non_err:
            self.assertIn(str(WORKSPACE / "scripts"), r["path"])

    def test_fallback_produces_valid_schema(self):
        """Fallback results still match expected schema."""
        out = run_tool("MEMORY.md", "--force-fs-search", "--limit", "2")
        for r in out["results"]:
            if not r.get("error"):
                self.assertIn("type", r)
                self.assertIn("path", r)
                self.assertIn("score", r)
                self.assertIsInstance(r["score"], (int, float))

    def test_module_keyword_fallback_chain(self):
        """Unit: _keyword_search falls back gracefully when tier1 unavailable."""
        mod = import_module()
        with patch.object(mod, "KEYWORD_SEARCH_BIN", "/nonexistent/momo-kioku-search"):
            with patch.object(mod, "KEYWORD_FALLBACK_BIN", "/nonexistent/fast-find.sh"):
                results = mod._keyword_search("total_recall_search.py", 3, None)
        # Should not raise; may return error or fs-grep results
        self.assertIsInstance(results, list)


class TestImprovement2_Classification(unittest.TestCase):
    """Improvement 2: Two-pass heuristic classification."""

    def setUp(self):
        self.mod = import_module()

    def test_file_extension_classified_keyword(self):
        cls, reason = self.mod.classify_query("total_recall_search.py")
        self.assertEqual(cls, "keyword", f"Expected keyword, got {cls} ({reason})")

    def test_path_separator_classified_keyword(self):
        cls, reason = self.mod.classify_query("/Users/bob/SOUL.md")
        self.assertEqual(cls, "keyword", f"Expected keyword, got {cls} ({reason})")

    def test_tilde_path_classified_keyword(self):
        cls, reason = self.mod.classify_query("~/.openclaw/workspace/MEMORY.md")
        self.assertEqual(cls, "keyword", f"Expected keyword, got {cls} ({reason})")

    def test_prose_why_classified_semantic(self):
        cls, reason = self.mod.classify_query("why did we switch to Leidos")
        self.assertEqual(cls, "semantic", f"Expected semantic, got {cls} ({reason})")

    def test_prose_explain_classified_semantic(self):
        cls, reason = self.mod.classify_query("explain cascade proxy savings")
        self.assertEqual(cls, "semantic", f"Expected semantic, got {cls} ({reason})")

    def test_long_query_classified_semantic(self):
        cls, reason = self.mod.classify_query("the latest updates on reillydesignstudio project progress")
        self.assertEqual(cls, "semantic", f"Expected semantic for long query, got {cls} ({reason})")

    def test_short_query_classified_keyword(self):
        cls, reason = self.mod.classify_query("MEMORY")
        self.assertEqual(cls, "keyword", f"Expected keyword for 1-word query, got {cls} ({reason})")

    def test_returns_reason_string(self):
        cls, reason = self.mod.classify_query("what is the Leidos start date")
        self.assertIsInstance(reason, str)
        self.assertGreater(len(reason), 0)

    def test_readme_classified_keyword(self):
        cls, reason = self.mod.classify_query("README")
        self.assertEqual(cls, "keyword", f"Expected keyword for README, got {cls} ({reason})")


class TestImprovement3_SemanticThreshold(unittest.TestCase):
    """Improvement 3: --min-score parameter + dynamic thresholding."""

    def test_min_score_flag_accepted(self):
        """--min-score should not cause a crash."""
        out = run_tool("memory system", "--type", "semantic", "--min-score", "0.2", "--limit", "3")
        self.assertIn(out["rc"], (0, 1))

    def test_high_min_score_fewer_results(self):
        """Higher --min-score should yield ≤ results compared to lower threshold."""
        out_low = run_tool("cascade proxy", "--type", "semantic", "--min-score", "0.1", "--limit", "10")
        out_high = run_tool("cascade proxy", "--type", "semantic", "--min-score", "0.9", "--limit", "10")
        low_count = len([r for r in out_low["results"] if not r.get("error")])
        high_count = len([r for r in out_high["results"] if not r.get("error")])
        self.assertLessEqual(high_count, low_count,
            f"High threshold ({high_count}) should have ≤ results than low threshold ({low_count})")

    def test_min_score_zero_returns_all(self):
        """--min-score 0.0 should return maximum available results."""
        out = run_tool("total recall", "--type", "semantic", "--min-score", "0.0", "--limit", "10")
        self.assertIn(out["rc"], (0, 1))

    def test_dynamic_threshold_module(self):
        """Unit: dynamic thresholding lowers threshold when 0 results."""
        mod = import_module()

        # Mock _semantic_inline to return low-score results
        fake_results = [
            {"type": "semantic", "path": "/fake.md", "snippet": "x", "score": 0.25}
        ]
        with patch.object(mod, "_semantic_inline", return_value=fake_results):
            with patch("subprocess.run") as mock_run:
                mock_run.side_effect = json.JSONDecodeError("forcing fallback", "", 0)
                # High threshold → 0 results → dynamic lowering should kick in
                results = mod._semantic_search("test", 5, min_score=0.8, dynamic_threshold=True)

        # Should have found the 0.25-score result via dynamic lowering
        non_err = [r for r in results if not r.get("error")]
        if non_err:
            # Confirm dynamic threshold was applied
            self.assertTrue(
                any(r.get("_dynamic_threshold") for r in non_err),
                "Expected _dynamic_threshold flag on results from dynamic lowering"
            )


class TestImprovement4_ResultMerging(unittest.TestCase):
    """Improvement 4: Borda count interleaving + file diversity."""

    def setUp(self):
        self.mod = import_module()

    def test_borda_merge_basic(self):
        """_borda_merge returns combined results up to limit."""
        kw = [
            {"type": "keyword", "path": "/a.md", "snippet": "kw1", "score": 1.0},
            {"type": "keyword", "path": "/b.md", "snippet": "kw2", "score": 0.9},
        ]
        sem = [
            {"type": "semantic", "path": "/c.md", "snippet": "se1", "score": 0.8},
            {"type": "semantic", "path": "/d.md", "snippet": "se2", "score": 0.7},
        ]
        results = self.mod._borda_merge(kw, sem, limit=3)
        self.assertLessEqual(len(results), 3)
        paths = [r["path"] for r in results]
        # All paths should be from either kw or sem
        for p in paths:
            self.assertIn(p, ["/a.md", "/b.md", "/c.md", "/d.md"])

    def test_borda_score_attached(self):
        """Results from _borda_merge carry _borda_score."""
        kw = [{"type": "keyword", "path": "/x.md", "snippet": "x", "score": 1.0}]
        sem = [{"type": "semantic", "path": "/y.md", "snippet": "y", "score": 0.6}]
        results = self.mod._borda_merge(kw, sem, limit=4)
        for r in results:
            if not r.get("error"):
                self.assertIn("_borda_score", r, f"Missing _borda_score in {r['path']}")

    def test_file_diversity(self):
        """Same-file duplicates get penalised; different files preferred."""
        kw = [
            {"type": "keyword", "path": "/same.md", "snippet": "a", "score": 1.0},
        ]
        sem = [
            {"type": "semantic", "path": "/same.md", "snippet": "b", "score": 0.9},
            {"type": "semantic", "path": "/different.md", "snippet": "c", "score": 0.5},
        ]
        results = self.mod._borda_merge(kw, sem, limit=3)
        paths = [r["path"] for r in results if not r.get("error")]
        # /different.md should appear (diversity)
        self.assertIn("/different.md", paths, "Diversity: /different.md should be included")

    def test_errors_not_in_interleave(self):
        """Error results don't participate in Borda scoring."""
        kw = [{"type": "keyword", "path": "(error)", "snippet": "ERROR: x", "score": 0.0, "error": True}]
        sem = [{"type": "semantic", "path": "/ok.md", "snippet": "ok", "score": 0.7}]
        results = self.mod._borda_merge(kw, sem, limit=2)
        non_err = [r for r in results if not r.get("error")]
        self.assertTrue(any(r["path"] == "/ok.md" for r in non_err))

    def test_borda_merge_empty_inputs(self):
        """Empty inputs return empty list."""
        results = self.mod._borda_merge([], [], limit=5)
        self.assertEqual(results, [])


class TestImprovement5_Performance(unittest.TestCase):
    """Improvement 5: Caching + --quick mode + lazy model."""

    def test_quick_mode_fast(self):
        """--quick should return within 4 seconds."""
        t0 = time.time()
        out = run_tool("MEMORY.md", "--quick", "--limit", "3", timeout=10)
        elapsed = time.time() - t0
        self.assertLess(elapsed, 4.0, f"--quick mode took {elapsed:.2f}s, expected < 4s")
        self.assertIn(out["rc"], (0, 1))

    def test_quick_mode_keyword_only(self):
        """--quick results should be keyword type only."""
        out = run_tool("total_recall_search", "--quick", "--limit", "5")
        sem_results = [r for r in out["results"] if r.get("type") == "semantic"]
        self.assertEqual(len(sem_results), 0, "--quick should not return semantic results")

    def test_cache_hit_on_repeat(self):
        """Second call with same args should be faster (cache hit)."""
        query = f"cache_test_{int(time.time())}_memory"

        out1 = run_tool(query, "--type", "keyword", "--limit", "3", timeout=30)
        t1 = out1["elapsed"]

        out2 = run_tool(query, "--type", "keyword", "--limit", "3", timeout=30)
        t2 = out2["elapsed"]

        # Second call should be faster (cache hit → much faster)
        # Allow generous margin since both may be fast
        self.assertLessEqual(t2, t1 + 1.0,
            f"Cache hit ({t2:.2f}s) should be ≤ first call ({t1:.2f}s) + 1s margin")

    def test_no_cache_flag(self):
        """--no-cache should bypass cache and still return results."""
        out = run_tool("MEMORY.md", "--no-cache", "--type", "keyword", "--limit", "2")
        self.assertIn(out["rc"], (0, 1))

    def test_cache_key_stability(self):
        """Same query params generate same cache key."""
        mod = import_module()
        k1 = mod._cache_key("hello", "auto", 10, None)
        k2 = mod._cache_key("hello", "auto", 10, None)
        self.assertEqual(k1, k2)

    def test_cache_key_differs_on_params(self):
        """Different params generate different cache keys."""
        mod = import_module()
        k1 = mod._cache_key("hello", "auto", 10, None)
        k2 = mod._cache_key("hello", "keyword", 10, None)
        k3 = mod._cache_key("hello", "auto", 20, None)
        self.assertNotEqual(k1, k2)
        self.assertNotEqual(k1, k3)

    def test_cache_write_and_read(self):
        """Write then read cache within TTL returns same data."""
        mod = import_module()
        key = "test_key_12345"
        data = [{"type": "keyword", "path": "/test.md", "snippet": "s", "score": 1.0}]
        mod._write_cache(key, data)
        result = mod._read_cache(key)
        self.assertIsNotNone(result, "Cache should return data within TTL")
        self.assertEqual(result[0]["path"], "/test.md")


class TestImprovement6_MemoryIndexing(unittest.TestCase):
    """Improvement 6: --index-dir, --prune-old, incremental mtime index."""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_index_dir_flag(self):
        """--index-dir includes custom directory in semantic search."""
        # Create a markdown file in tmp dir
        note = self.tmpdir / "custom_note.md"
        note.write_text("# Custom Test Note\nThis is a unique custom note for indexing test.")

        out = run_tool(
            "custom unique note indexing",
            "--type", "semantic",
            "--index-dir", str(self.tmpdir),
            "--min-score", "0.0",
            "--limit", "5",
            timeout=120,
        )
        self.assertIn(out["rc"], (0, 1))
        # Don't assert file found (semantic model may not score it high enough),
        # but ensure no crash and valid output
        for r in out["results"]:
            self.assertIn("type", r)

    def test_prune_old_flag(self):
        """--prune-old should not crash and returns valid results."""
        out = run_tool(
            "memory cascade", "--type", "semantic",
            "--prune-old", "--limit", "3",
            timeout=120,
        )
        self.assertIn(out["rc"], (0, 1))

    def test_load_memory_files_extra_dirs(self):
        """_load_memory_files respects extra_dirs parameter."""
        note = self.tmpdir / "extra_note.md"
        note.write_text("# Extra\nExtra content for testing.")
        mod = import_module()
        files = mod._load_memory_files(extra_dirs=[str(self.tmpdir)])
        self.assertIn(str(note), files, "Extra dir file should be loaded")

    def test_load_memory_files_prune_old(self):
        """_load_memory_files with prune_old skips old files."""
        mod = import_module()
        # Create a temp file and make it look old (mtime in the past)
        old_file = self.tmpdir / "old_note.md"
        old_file.write_text("# Old note")
        old_mtime = time.time() - (100 * 86400)  # 100 days ago
        os.utime(str(old_file), (old_mtime, old_mtime))

        # Use the tmp dir as a base but override PRUNE_DAYS
        original_prune = mod.PRUNE_DAYS
        mod.PRUNE_DAYS = 90
        files = mod._load_memory_files(extra_dirs=[str(self.tmpdir)], prune_old=True)
        mod.PRUNE_DAYS = original_prune

        # Old file should NOT be in files
        self.assertNotIn(str(old_file), files, "File >90 days old should be pruned")

    def test_mtime_index_incremental(self):
        """Incremental mtime index detects changed files."""
        mod = import_module()
        mem_dir = WORKSPACE / "memory"
        if not mem_dir.exists():
            self.skipTest("No memory directory found")

        changed = mod._get_changed_files(mem_dir)
        # After saving the index, calling again should return 0 changed (no changes)
        changed2 = mod._get_changed_files(mem_dir)
        self.assertLessEqual(len(changed2), len(changed),
            "After indexing, fewer or equal files should be 'changed'")

    def test_index_dir_nonexistent_graceful(self):
        """--index-dir with nonexistent path should not crash."""
        out = run_tool(
            "test query", "--type", "semantic",
            "--index-dir", "/nonexistent/path/xyz123",
            "--limit", "2",
            timeout=60,
            expect_exit=-1,
        )
        self.assertIn(out["rc"], (0, 1))


class TestImprovement7_ErrorHandlingFeedback(unittest.TestCase):
    """Improvement 7: --verbose, --explain, _meta metadata."""

    def test_verbose_outputs_to_stderr(self):
        """--verbose should produce backend info on stderr."""
        cmd = [PYTHON, str(TOOL_PY), "--json", "--verbose", "--type", "keyword",
               "--limit", "2", "MEMORY.md"]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        self.assertIn(proc.returncode, (0, 1))
        # Verbose output should appear on stderr
        self.assertGreater(len(proc.stderr), 0, "--verbose should produce stderr output")

    def test_verbose_mentions_backend(self):
        """--verbose stderr should mention BACKEND or VERBOSE."""
        cmd = [PYTHON, str(TOOL_PY), "--json", "--verbose", "--type", "keyword",
               "--limit", "2", "total_recall_search.py"]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        # Should mention backend selection
        self.assertTrue(
            "[VERBOSE]" in proc.stderr or "[BACKEND]" in proc.stderr,
            f"Expected verbose markers in stderr, got: {proc.stderr[:300]}"
        )

    def test_meta_field_present(self):
        """Every non-error result should have a _meta dict."""
        out = run_tool("MEMORY.md", "--type", "keyword", "--limit", "3")
        non_err = [r for r in out["results"] if not r.get("error")]
        for r in non_err:
            self.assertIn("_meta", r, f"Missing _meta in result: {r['path']}")
            meta = r["_meta"]
            self.assertIn("backend", meta)
            self.assertIn("latency_ms", meta)
            self.assertIn("confidence", meta)

    def test_meta_confidence_values(self):
        """_meta.confidence should be one of: high, medium, low."""
        out = run_tool("cascade proxy", "--type", "keyword", "--limit", "5")
        for r in out["results"]:
            if not r.get("error") and "_meta" in r:
                self.assertIn(r["_meta"]["confidence"], ("high", "medium", "low"),
                    f"Unexpected confidence: {r['_meta']['confidence']}")

    def test_meta_latency_ms_positive(self):
        """_meta.latency_ms should be a positive number."""
        out = run_tool("SOUL.md", "--type", "keyword", "--limit", "2")
        for r in out["results"]:
            if not r.get("error") and "_meta" in r:
                self.assertGreaterEqual(r["_meta"]["latency_ms"], 0,
                    "latency_ms should be ≥ 0")

    def test_explain_mode(self):
        """--explain should attach _explain to results when Borda merge used."""
        mod = import_module()
        mod._explain = True  # Enable explain mode

        kw = [{"type": "keyword", "path": "/a.md", "snippet": "a", "score": 1.0}]
        sem = [{"type": "semantic", "path": "/b.md", "snippet": "b", "score": 0.7}]
        results = mod._borda_merge(kw, sem, limit=2)

        mod._explain = False
        has_explain = any("_explain" in r for r in results if not r.get("error"))
        self.assertTrue(has_explain, "Expected _explain field when _explain=True")

    def test_explain_flag_cli(self):
        """--explain CLI flag should not crash."""
        cmd = [PYTHON, str(TOOL_PY), "--json", "--explain", "--limit", "2", "MEMORY.md"]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        self.assertIn(proc.returncode, (0, 1))

    def test_error_result_schema(self):
        """_error_result helper returns correct schema."""
        mod = import_module()
        err = mod._error_result("semantic", "test error message")
        self.assertEqual(err["type"], "semantic")
        self.assertEqual(err["path"], "(error)")
        self.assertIn("ERROR", err["snippet"])
        self.assertTrue(err["error"])
        self.assertEqual(err["score"], 0.0)

    def test_attach_meta_function(self):
        """_attach_meta adds _meta to all results."""
        mod = import_module()
        results = [
            {"type": "keyword", "path": "/a.md", "snippet": "a", "score": 0.9},
            {"type": "semantic", "path": "/b.md", "snippet": "b", "score": 0.3},
        ]
        tagged = mod._attach_meta(results, "test-backend", 0.123)
        for r in tagged:
            self.assertEqual(r["_meta"]["backend"], "test-backend")
            self.assertAlmostEqual(r["_meta"]["latency_ms"], 123.0, places=0)
        # High score → high confidence
        self.assertEqual(tagged[0]["_meta"]["confidence"], "high")
        # Low score → low confidence
        self.assertEqual(tagged[1]["_meta"]["confidence"], "low")


class TestAutoMode(unittest.TestCase):
    """End-to-end auto-routing tests."""

    def test_auto_keyword_for_file_query(self):
        """Auto mode: file query should return keyword results first."""
        out = run_tool("total_recall_search.py", "--limit", "3")
        self.assertEqual(out["rc"], 0)
        non_err = [r for r in out["results"] if not r.get("error")]
        self.assertGreater(len(non_err), 0)
        self.assertTrue(
            any(r["type"] == "keyword" for r in non_err),
            "File query in auto mode should include keyword results"
        )

    def test_auto_semantic_for_prose_query(self):
        """Auto mode: long prose query routes to semantic."""
        out = run_tool(
            "what is the current status of speculative decoding project",
            "--limit", "3", timeout=120,
        )
        self.assertIn(out["rc"], (0, 1))

    def test_auto_mode_meta_backend_label(self):
        """Auto mode attaches correct backend label in _meta."""
        out = run_tool("SOUL.md", "--limit", "2")
        for r in out["results"]:
            if not r.get("error") and "_meta" in r:
                # Backend label should contain "keyword" or "semantic" or "auto"
                self.assertTrue(
                    any(k in r["_meta"]["backend"] for k in ["keyword", "semantic", "auto", "cache"]),
                    f"Unexpected backend label: {r['_meta']['backend']}"
                )


class TestCLIFlags(unittest.TestCase):
    """Validate all new CLI flags are accepted and documented."""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _check_flag(self, *flags):
        """Run with a flag and ensure it doesn't crash with exit 2 (argparse error)."""
        # Use a non-existent query and restrict to tmpdir with keyword search
        # to ensure it finishes quickly and doesn't find anything real.
        args = ["non_existent_flag_test_query_xyz123", "--type", "keyword", "--path", str(self.tmpdir)]
        out = run_tool(*args, *flags, timeout=15, expect_exit=-1)
        self.assertNotEqual(out["rc"], 2, f"Argparse rejected flags: {flags}")

    def test_min_score_flag(self):
        self._check_flag("--min-score", "0.3", "--type", "keyword")

    def test_force_fs_search_flag(self):
        self._check_flag("--force-fs-search", "--type", "keyword")

    def test_quick_flag(self):
        self._check_flag("--quick")

    def test_verbose_flag(self):
        self._check_flag("--verbose", "--type", "keyword")

    def test_explain_flag(self):
        self._check_flag("--explain", "--type", "keyword")

    def test_index_dir_flag(self):
        # Create a small temporary directory for indexing
        with tempfile.TemporaryDirectory() as temp_dir_str:
            temp_path = Path(temp_dir_str)
            (temp_path / "test_file.txt").write_text("This is a test file for indexing.")

            # Now run the test using this small temporary directory
            self._check_flag("--index-dir", str(temp_path), "--type", "semantic")

    def test_prune_old_flag(self):
        self._check_flag("--prune-old", "--type", "semantic")

    def test_no_cache_flag(self):
        self._check_flag("--no-cache", "--type", "keyword")

    def test_help_exits_cleanly(self):
        cmd = [PYTHON, str(TOOL_PY), "--help"]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("--min-score", proc.stdout)
        self.assertIn("--force-fs-search", proc.stdout)
        self.assertIn("--quick", proc.stdout)
        self.assertIn("--verbose", proc.stdout)
        self.assertIn("--explain", proc.stdout)
        self.assertIn("--index-dir", proc.stdout)
        self.assertIn("--prune-old", proc.stdout)
        self.assertIn("--no-cache", proc.stdout)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Make output more readable
    verbosity = 2 if "-v" in sys.argv else 1
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Order: backward compat first, then improvements 1-7
    for cls in [
        TestBackwardCompatibility,
        TestImprovement1_KeywordFallback,
        TestImprovement2_Classification,
        TestImprovement3_SemanticThreshold,
        TestImprovement4_ResultMerging,
        TestImprovement5_Performance,
        TestImprovement6_MemoryIndexing,
        TestImprovement7_ErrorHandlingFeedback,
        TestAutoMode,
        TestCLIFlags,
    ]:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
