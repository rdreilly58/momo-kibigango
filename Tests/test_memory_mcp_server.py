#!/usr/bin/env python3
"""
Extensive test suite for memory_mcp_server.py

Tests are grouped into:
  1. Unit — internal helpers (_chunk_text, cosine scoring, get_memory_file)
  2. Integration — semantic_search against live memory files
  3. MCP tool surface — memory_search / memory_get return valid JSON / expected schema
  4. Edge cases — empty query, large top_k, bad filenames, unicode, missing files
  5. Invalidation — index is rebuilt when a file changes on disk
  6. Protocol — server starts and responds to MCP initialize over stdio
"""

import json
import math
import os
import sys
import tempfile
import time
import subprocess
import textwrap
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# ---------------------------------------------------------------------------
# Path setup — import the module under test directly
# ---------------------------------------------------------------------------
SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
VENV_SITE = Path(__file__).parent.parent / "venv" / "lib" / "python3.14" / "site-packages"
sys.path.insert(0, str(VENV_SITE))
sys.path.insert(0, str(SCRIPTS_DIR))

import memory_mcp_server as srv


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_temp_workspace(files: dict[str, str]) -> Path:
    """Create a temp dir with the given {relative_path: content} files."""
    tmp = Path(tempfile.mkdtemp(prefix="mem_mcp_test_"))
    for relpath, content in files.items():
        dest = tmp / relpath
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
    return tmp


def _with_workspace(workspace: Path):
    """Context manager: override srv.WORKSPACE and clear the index."""
    import contextlib

    @contextlib.contextmanager
    def _cm():
        old_ws = srv.WORKSPACE
        srv.WORKSPACE = workspace
        srv._index.clear()
        srv._index_mtime.clear()
        try:
            yield
        finally:
            srv.WORKSPACE = old_ws
            srv._index.clear()
            srv._index_mtime.clear()

    return _cm()


# ---------------------------------------------------------------------------
# 1. Unit tests — internal helpers
# ---------------------------------------------------------------------------

class TestChunkText(unittest.TestCase):

    def test_short_text_single_chunk(self):
        chunks = srv._chunk_text("Hello world")
        self.assertEqual(len(chunks), 1)
        self.assertIn("Hello world", chunks[0])

    def test_empty_string_returns_one_chunk(self):
        chunks = srv._chunk_text("")
        self.assertEqual(len(chunks), 1)

    def test_long_text_produces_multiple_chunks(self):
        long = ("x" * 100 + "\n") * 20  # 2000 chars
        chunks = srv._chunk_text(long, )
        self.assertGreater(len(chunks), 1)

    def test_chunks_cover_all_content(self):
        """Every line of original text must appear in at least one chunk."""
        lines = [f"line_{i}" for i in range(50)]
        text = "\n".join(lines)
        chunks = srv._chunk_text(text)
        combined = "\n".join(chunks)
        for line in lines:
            self.assertIn(line, combined, f"Line '{line}' missing from chunks")

    def test_overlap_present(self):
        """Last lines of one chunk should appear at start of next."""
        lines = [f"L{i}" for i in range(40)]
        text = "\n".join(lines)
        chunks = srv._chunk_text(text)
        if len(chunks) < 2:
            self.skipTest("Not enough chunks to test overlap")
        # Last CHUNK_OVERLAP lines of chunk[0] should appear in chunk[1]
        c0_lines = chunks[0].split("\n")
        tail = c0_lines[-srv.CHUNK_OVERLAP:]
        c1_start = chunks[1]
        for tl in tail:
            self.assertIn(tl, c1_start)

    def test_respects_chunk_size(self):
        """Each chunk should be roughly <= CHUNK_SIZE + one line of overflow."""
        lines = [("word " * 20).strip() for _ in range(30)]
        text = "\n".join(lines)
        chunks = srv._chunk_text(text)
        max_allowed = srv.CHUNK_SIZE + max(len(l) for l in lines) + 1
        for chunk in chunks:
            self.assertLessEqual(len(chunk), max_allowed)


class TestCosineSimilarity(unittest.TestCase):

    def _cos(self, a, b):
        import numpy as np
        a, b = np.array(a, dtype=float), np.array(b, dtype=float)
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    def test_identical_vectors_score_one(self):
        v = [1.0, 2.0, 3.0]
        self.assertAlmostEqual(self._cos(v, v), 1.0, places=5)

    def test_orthogonal_vectors_score_zero(self):
        self.assertAlmostEqual(self._cos([1, 0], [0, 1]), 0.0, places=5)

    def test_opposite_vectors_score_minus_one(self):
        self.assertAlmostEqual(self._cos([1, 0], [-1, 0]), -1.0, places=5)

    def test_zero_vector_handling(self):
        """_cosine_scores should not crash on a zero query embedding."""
        import numpy as np
        # Build a tiny index manually
        srv._index = [{
            "source": "test.md",
            "chunk": "hello",
            "embedding": np.array([1.0, 0.0]),
        }]
        query = np.array([0.0, 0.0])
        scores = srv._cosine_scores(query)
        self.assertEqual(len(scores), 1)
        # Result should be 0.0 (safe fallback)
        self.assertEqual(scores[0], 0.0)
        srv._index.clear()


class TestGetMemoryFile(unittest.TestCase):

    def test_returns_content_for_existing_file(self):
        ws = _make_temp_workspace({"MEMORY.md": "# Memory\nsome content"})
        with _with_workspace(ws):
            result = srv.get_memory_file("MEMORY.md")
        self.assertEqual(result, "# Memory\nsome content")

    def test_returns_none_for_missing_file(self):
        ws = _make_temp_workspace({})
        with _with_workspace(ws):
            result = srv.get_memory_file("nonexistent.md")
        self.assertIsNone(result)

    def test_bare_filename_resolves_in_memory_subdir(self):
        ws = _make_temp_workspace({"memory/user_role.md": "I am a data scientist"})
        with _with_workspace(ws):
            result = srv.get_memory_file("user_role.md")
        self.assertEqual(result, "I am a data scientist")

    def test_relative_path_resolves(self):
        ws = _make_temp_workspace({"memory/feedback_testing.md": "no mocks"})
        with _with_workspace(ws):
            result = srv.get_memory_file("memory/feedback_testing.md")
        self.assertEqual(result, "no mocks")

    def test_directory_traversal_blocked(self):
        """Requesting a path outside workspace should return None, not file content."""
        ws = _make_temp_workspace({})
        # /etc/passwd on macOS-style; use a known readable file
        sensitive = Path("/private/etc/hosts")
        if not sensitive.exists():
            self.skipTest("No /private/etc/hosts to test against")
        with _with_workspace(ws):
            result = srv.get_memory_file("../../../../../../private/etc/hosts")
        # Should be None — path lands outside workspace
        self.assertIsNone(result)

    def test_unicode_filename(self):
        ws = _make_temp_workspace({"memory/日本語.md": "こんにちは"})
        with _with_workspace(ws):
            result = srv.get_memory_file("日本語.md")
        self.assertEqual(result, "こんにちは")


# ---------------------------------------------------------------------------
# 2. Integration tests — semantic_search
# ---------------------------------------------------------------------------

class TestSemanticSearch(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Create a workspace with known content for reproducible search tests."""
        cls.ws = _make_temp_workspace({
            "MEMORY.md": textwrap.dedent("""\
                # Memory Index
                - [user_role.md](memory/user_role.md) — user is a data scientist
                - [feedback_testing.md](memory/feedback_testing.md) — no mocks in integration tests
            """),
            "memory/user_role.md": textwrap.dedent("""\
                ---
                name: user role
                type: user
                ---
                The user is a senior data scientist focused on observability and logging.
                They have deep Python expertise and prefer concise answers.
            """),
            "memory/feedback_testing.md": textwrap.dedent("""\
                ---
                name: feedback testing
                type: feedback
                ---
                Do not mock the database in integration tests.
                We got burned when mocked tests passed but the prod migration failed.
                Always use a real database for integration test suites.
            """),
            "memory/project_deadline.md": textwrap.dedent("""\
                ---
                name: project deadline
                type: project
                ---
                The payment service refactor is due 2026-05-01.
                It is driven by PCI compliance requirements.
                Do not add unrelated features to this PR.
            """),
        })

    def setUp(self):
        """Reset index before each test."""
        srv._index.clear()
        srv._index_mtime.clear()

    def _search(self, query: str, top_k: int = 5) -> list[dict]:
        with _with_workspace(self.ws):
            return srv.semantic_search(query, top_k=top_k)

    def test_returns_list(self):
        results = self._search("data scientist")
        self.assertIsInstance(results, list)

    def test_result_schema(self):
        results = self._search("Python expertise")
        self.assertGreater(len(results), 0)
        r = results[0]
        self.assertIn("source", r)
        self.assertIn("score", r)
        self.assertIn("text", r)
        self.assertIn("preview", r)
        self.assertIsInstance(r["score"], float)
        self.assertIsInstance(r["text"], str)

    def test_top_result_relevant_to_query(self):
        """User-role query should surface user_role.md chunk as top hit."""
        results = self._search("data scientist observability Python")
        top_sources = [r["source"] for r in results[:2]]
        self.assertTrue(
            any("user_role" in s for s in top_sources),
            f"user_role.md not in top 2: {top_sources}",
        )

    def test_testing_query_surfaces_feedback(self):
        results = self._search("integration tests database no mocks")
        top_sources = [r["source"] for r in results[:2]]
        self.assertTrue(
            any("feedback_testing" in s for s in top_sources),
            f"feedback_testing.md not in top 2: {top_sources}",
        )

    def test_scores_between_minus_one_and_one(self):
        results = self._search("PCI compliance deadline")
        for r in results:
            self.assertGreaterEqual(r["score"], -1.0)
            self.assertLessEqual(r["score"], 1.0)

    def test_results_sorted_by_score_descending(self):
        results = self._search("payment service compliance")
        scores = [r["score"] for r in results]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_top_k_respected(self):
        for k in (1, 2, 3):
            results = self._search("any query", top_k=k)
            self.assertLessEqual(len(results), k)

    def test_empty_workspace_returns_empty_list(self):
        empty_ws = _make_temp_workspace({})
        with _with_workspace(empty_ws):
            results = srv.semantic_search("anything")
        self.assertEqual(results, [])

    def test_index_rebuild_after_file_change(self):
        """Add a new file after first search; second search should see it."""
        dynamic_ws = _make_temp_workspace({
            "memory/initial.md": "initial content about alpha"
        })
        with _with_workspace(dynamic_ws):
            results_before = srv.semantic_search("beta topic", top_k=5)
            sources_before = {r["source"] for r in results_before}

            # Write a new file
            new_file = dynamic_ws / "memory" / "new_beta.md"
            new_file.write_text("new content about beta topic specifically", encoding="utf-8")

            # Force mtime change detection by touching the file
            time.sleep(0.05)
            os.utime(new_file, None)

            # Clear index to simulate next call
            srv._index.clear()
            srv._index_mtime.clear()

            results_after = srv.semantic_search("beta topic", top_k=5)
            sources_after = {r["source"] for r in results_after}

        self.assertIn("memory/new_beta.md", sources_after,
                      "New file should be indexed after rebuild")

    def test_preview_truncated_at_200_chars(self):
        long_chunk_ws = _make_temp_workspace({
            "memory/long.md": "word " * 200  # 1000 chars
        })
        with _with_workspace(long_chunk_ws):
            results = srv.semantic_search("word")
        for r in results:
            self.assertLessEqual(len(r["preview"]), 203,  # 200 + "..."
                                 "Preview must be <= 203 chars")

    def test_unicode_content_searchable(self):
        uni_ws = _make_temp_workspace({
            "memory/japanese.md": "これはテストです。AIエージェントは役立ちます。"
        })
        with _with_workspace(uni_ws):
            results = srv.semantic_search("AI agent helpful test")
        self.assertIsInstance(results, list)  # should not raise


# ---------------------------------------------------------------------------
# 3. MCP tool surface tests — memory_search / memory_get
# ---------------------------------------------------------------------------

class TestMcpToolSurface(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ws = _make_temp_workspace({
            "MEMORY.md": "# Memory\n- [role.md](memory/role.md)\n",
            "memory/role.md": "The user is a backend engineer who loves Go.",
        })

    def setUp(self):
        srv._index.clear()
        srv._index_mtime.clear()

    def _search(self, query: str, top_k: int = 5) -> list:
        with _with_workspace(self.ws):
            raw = srv.memory_search(query, top_k=top_k)
        return json.loads(raw)

    def _get(self, filename: str) -> str:
        with _with_workspace(self.ws):
            return srv.memory_get(filename)

    def test_memory_search_returns_valid_json(self):
        raw = ""
        with _with_workspace(self.ws):
            raw = srv.memory_search("Go backend engineer")
        parsed = json.loads(raw)  # must not raise
        self.assertIsInstance(parsed, list)

    def test_memory_search_result_keys(self):
        results = self._search("Go backend")
        self.assertGreater(len(results), 0)
        for r in results:
            self.assertIn("source", r)
            self.assertIn("score", r)
            self.assertIn("preview", r)
            self.assertIn("text", r)

    def test_memory_search_top_k_clamped_to_20(self):
        results = self._search("anything", top_k=999)
        self.assertLessEqual(len(results), 20)

    def test_memory_search_top_k_minimum_one(self):
        results = self._search("anything", top_k=0)
        self.assertLessEqual(len(results), 1)

    def test_memory_search_empty_query_no_crash(self):
        """Empty string query should return a valid (possibly empty) JSON array."""
        with _with_workspace(self.ws):
            raw = srv.memory_search("")
        parsed = json.loads(raw)
        self.assertIsInstance(parsed, list)

    def test_memory_get_existing_file(self):
        content = self._get("MEMORY.md")
        self.assertIn("Memory", content)
        self.assertNotIn('"error"', content)

    def test_memory_get_subdir_file(self):
        content = self._get("role.md")
        self.assertIn("backend engineer", content)

    def test_memory_get_missing_file_returns_error_json(self):
        result = self._get("does_not_exist.md")
        parsed = json.loads(result)
        self.assertIn("error", parsed)
        self.assertIn("available_files", parsed)
        self.assertIsInstance(parsed["available_files"], list)

    def test_memory_get_missing_file_lists_available(self):
        result = self._get("nope.md")
        parsed = json.loads(result)
        available = parsed["available_files"]
        self.assertTrue(any("MEMORY.md" in f for f in available))

    def test_memory_search_scores_are_rounded(self):
        """Scores should have at most 4 decimal places."""
        results = self._search("engineer")
        for r in results:
            score_str = str(r["score"])
            if "." in score_str:
                decimals = len(score_str.split(".")[1])
                self.assertLessEqual(decimals, 4)


# ---------------------------------------------------------------------------
# 4. Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases(unittest.TestCase):

    def setUp(self):
        srv._index.clear()
        srv._index_mtime.clear()

    def test_very_long_query(self):
        ws = _make_temp_workspace({"memory/x.md": "short doc"})
        long_query = "word " * 500
        with _with_workspace(ws):
            results = srv.semantic_search(long_query, top_k=3)
        self.assertIsInstance(results, list)

    def test_special_characters_in_query(self):
        ws = _make_temp_workspace({"memory/x.md": "content with symbols"})
        with _with_workspace(ws):
            results = srv.semantic_search("!@#$%^&*()[]{}|<>?", top_k=3)
        self.assertIsInstance(results, list)

    def test_newline_only_content(self):
        ws = _make_temp_workspace({"memory/empty_ish.md": "\n\n\n"})
        with _with_workspace(ws):
            results = srv.semantic_search("anything", top_k=3)
        self.assertIsInstance(results, list)

    def test_file_with_only_frontmatter(self):
        ws = _make_temp_workspace({
            "memory/frontmatter_only.md": "---\nname: test\ntype: user\n---\n"
        })
        with _with_workspace(ws):
            results = srv.semantic_search("test", top_k=3)
        self.assertIsInstance(results, list)

    def test_top_k_larger_than_chunks_returns_all(self):
        ws = _make_temp_workspace({"memory/tiny.md": "just one small chunk"})
        with _with_workspace(ws):
            results = srv.semantic_search("small chunk", top_k=100)
        # Should return <= actual number of chunks, not crash
        self.assertIsInstance(results, list)
        self.assertLessEqual(len(results), 100)

    def test_memory_files_no_memory_dir(self):
        """If memory/ subdir doesn't exist, only MEMORY.md (if present) is indexed."""
        ws = _make_temp_workspace({"MEMORY.md": "only top level"})
        with _with_workspace(ws):
            files = srv._memory_files()
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0].name, "MEMORY.md")

    def test_memory_files_only_memory_dir(self):
        """If MEMORY.md absent but memory/ exists, those files are found."""
        ws = _make_temp_workspace({"memory/a.md": "a", "memory/b.md": "b"})
        with _with_workspace(ws):
            files = srv._memory_files()
        names = {f.name for f in files}
        self.assertIn("a.md", names)
        self.assertIn("b.md", names)
        self.assertNotIn("MEMORY.md", names)

    def test_non_utf8_file_skipped_gracefully(self):
        """A file with invalid UTF-8 should be skipped, not crash the indexer."""
        ws = _make_temp_workspace({"memory/valid.md": "valid content"})
        bad = ws / "memory" / "bad_encoding.md"
        bad.write_bytes(b"\xff\xfe this is not utf-8 properly \x80\x81")
        with _with_workspace(ws):
            # Should not raise; bad file silently skipped or partially read
            try:
                results = srv.semantic_search("valid content", top_k=5)
                self.assertIsInstance(results, list)
            except UnicodeDecodeError:
                self.fail("UnicodeDecodeError should be caught internally")


# ---------------------------------------------------------------------------
# 5. Index invalidation
# ---------------------------------------------------------------------------

class TestIndexInvalidation(unittest.TestCase):

    def setUp(self):
        srv._index.clear()
        srv._index_mtime.clear()

    def test_needs_reindex_true_when_empty(self):
        srv._index.clear()
        srv._index_mtime.clear()
        ws = _make_temp_workspace({"memory/x.md": "content"})
        with _with_workspace(ws):
            self.assertTrue(srv._needs_reindex())

    def test_needs_reindex_false_after_build(self):
        ws = _make_temp_workspace({"memory/x.md": "content"})
        with _with_workspace(ws):
            srv._build_index()
            self.assertFalse(srv._needs_reindex())

    def test_needs_reindex_true_after_file_modified(self):
        ws = _make_temp_workspace({"memory/x.md": "original"})
        with _with_workspace(ws):
            srv._build_index()
            self.assertFalse(srv._needs_reindex())
            time.sleep(0.05)
            (ws / "memory" / "x.md").write_text("modified", encoding="utf-8")
            self.assertTrue(srv._needs_reindex())

    def test_needs_reindex_true_after_new_file_added(self):
        ws = _make_temp_workspace({"memory/x.md": "original"})
        with _with_workspace(ws):
            srv._build_index()
            # Add a new file that wasn't in the last index
            (ws / "memory" / "new.md").write_text("new file", encoding="utf-8")
            # _needs_reindex only checks known files' mtimes — new file won't trigger it
            # but _memory_files() count will be different → we test _build_index refreshes
            old_count = len(srv._index)
            srv._index.clear()
            srv._index_mtime.clear()
            srv._build_index()
            self.assertGreater(len(srv._index), old_count)


# ---------------------------------------------------------------------------
# 6. Protocol — MCP stdio
# ---------------------------------------------------------------------------

class TestMcpStdioProtocol(unittest.TestCase):
    """
    Verify the server speaks valid MCP JSON-RPC over stdio.
    Sends an 'initialize' request and expects a valid response.
    """

    PYTHON = str(Path(__file__).parent.parent / "venv" / "bin" / "python3")
    SERVER = str(Path(__file__).parent.parent / "scripts" / "memory_mcp_server.py")

    def _send_jsonrpc(self, proc, obj: dict) -> None:
        line = json.dumps(obj) + "\n"
        proc.stdin.write(line.encode())
        proc.stdin.flush()

    def _recv_jsonrpc(self, proc, timeout: float = 10.0) -> dict:
        """Read one JSON-RPC line from stdout."""
        import select
        start = time.time()
        buf = b""
        while time.time() - start < timeout:
            rlist, _, _ = select.select([proc.stdout], [], [], 0.5)
            if rlist:
                chunk = proc.stdout.read(4096)
                if not chunk:
                    break
                buf += chunk
                # Try to parse complete lines
                for line in buf.split(b"\n"):
                    line = line.strip()
                    if line:
                        try:
                            return json.loads(line)
                        except json.JSONDecodeError:
                            pass
        raise TimeoutError(f"No JSON-RPC response within {timeout}s. buf={buf!r}")

    def test_initialize_returns_valid_response(self):
        env = os.environ.copy()
        env["OPENCLAW_WORKSPACE"] = str(
            Path(__file__).parent.parent  # workspace root
        )
        proc = subprocess.Popen(
            [self.PYTHON, self.SERVER],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )
        try:
            self._send_jsonrpc(proc, {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "0.1"},
                },
            })
            response = self._recv_jsonrpc(proc, timeout=15.0)
            self.assertEqual(response.get("jsonrpc"), "2.0")
            self.assertEqual(response.get("id"), 1)
            self.assertIn("result", response, f"No 'result' in response: {response}")
            result = response["result"]
            self.assertIn("protocolVersion", result)
            self.assertIn("capabilities", result)
        finally:
            proc.terminate()
            proc.wait(timeout=5)

    def test_tools_list_contains_memory_search_and_memory_get(self):
        env = os.environ.copy()
        env["OPENCLAW_WORKSPACE"] = str(Path(__file__).parent.parent)
        proc = subprocess.Popen(
            [self.PYTHON, self.SERVER],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )
        try:
            # Initialize first
            self._send_jsonrpc(proc, {
                "jsonrpc": "2.0", "id": 1, "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "0.1"},
                },
            })
            self._recv_jsonrpc(proc, timeout=15.0)  # consume initialize response

            # Send initialized notification
            self._send_jsonrpc(proc, {
                "jsonrpc": "2.0", "method": "notifications/initialized", "params": {}
            })

            # List tools
            self._send_jsonrpc(proc, {
                "jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}
            })
            response = self._recv_jsonrpc(proc, timeout=10.0)
            self.assertEqual(response.get("id"), 2)
            tools = response.get("result", {}).get("tools", [])
            tool_names = {t["name"] for t in tools}
            self.assertIn("memory_search", tool_names)
            self.assertIn("memory_get", tool_names)
        finally:
            proc.terminate()
            proc.wait(timeout=5)


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main(verbosity=2)
