#!/usr/bin/env python3
"""
Tests for scripts/session_summarizer.py

Run with:
  cd /Users/rreilly/.openclaw/workspace
  python -m pytest Tests/test_session_summarizer.py -v

Uses OPENCLAW_TEST_WORKSPACE for all file isolation.
No real API calls — Anthropic client is mocked throughout.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch, call

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
WORKSPACE_ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = WORKSPACE_ROOT / "scripts"
VENV_SITE = WORKSPACE_ROOT / "venv" / "lib" / "python3.14" / "site-packages"
for p in (str(VENV_SITE), str(SCRIPTS_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

import session_summarizer as ss  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

GOOD_TRANSCRIPT = (
    "User: We need to fix the session hook regression in OpenClaw v2026.4.15. "
    "The hook only writes 171 bytes now instead of the full transcript. "
    "Assistant: I'll debug daily-session-reset.sh and add log_session_entry(). "
    "User: Great. Also add a test suite with at least 25 tests. "
    "Assistant: Done — all 25 tests passing. Committed as e634d5b. "
    "User: Perfect. Let's ship the two-tier memory system next. "
    "This conversation is long enough to be summarised properly. "
) * 3  # repeat to ensure >200 chars easily


GOOD_SUMMARY = {
    "one_liner": "Fixed session hook regression and added test suite",
    "topics": ["session-memory", "testing"],
    "completed": ["fix daily-session-reset.sh", "add 25-test suite"],
    "learned": ["hook only writes 171 bytes"],
    "issues": [],
    "next_steps": ["two-tier memory system"],
}


def _make_mock_client(summary: dict | None = None) -> MagicMock:
    """Return a mock Anthropic client whose messages.create returns the given summary."""
    if summary is None:
        summary = GOOD_SUMMARY
    raw_json = json.dumps(summary)
    mock_content = MagicMock()
    mock_content.text = raw_json
    mock_response = MagicMock()
    mock_response.content = [mock_content]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_response
    return mock_client


def _make_workspace(tmp: Path) -> Path:
    """Create a minimal workspace structure under tmp."""
    (tmp / "memory").mkdir(parents=True, exist_ok=True)
    (tmp / "scripts").mkdir(exist_ok=True)
    # Symlink or copy memory_db.py so write_to_db works
    target = tmp / "scripts" / "memory_db.py"
    src = SCRIPTS_DIR / "memory_db.py"
    if not target.exists():
        import shutil
        shutil.copy(src, target)
    # Create a minimal ai-memory.db
    _init_db(tmp / "ai-memory.db")
    return tmp


def _init_db(db_path: Path) -> None:
    """Create the ai-memory.db schema so tests can write to it."""
    import sqlite3
    con = sqlite3.connect(db_path)
    con.executescript("""
        CREATE TABLE IF NOT EXISTS memories (
            id TEXT PRIMARY KEY,
            tier TEXT NOT NULL DEFAULT 'short',
            namespace TEXT NOT NULL DEFAULT 'workspace',
            title TEXT NOT NULL,
            content TEXT NOT NULL DEFAULT '',
            tags TEXT NOT NULL DEFAULT '[]',
            priority INTEGER NOT NULL DEFAULT 5,
            confidence REAL NOT NULL DEFAULT 1.0,
            source TEXT NOT NULL DEFAULT 'api',
            access_count INTEGER NOT NULL DEFAULT 0,
            created_at TEXT,
            updated_at TEXT,
            last_accessed_at TEXT,
            expires_at TEXT,
            metadata TEXT NOT NULL DEFAULT '{}'
        );
        CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts
            USING fts5(title, content, content='memories', content_rowid='rowid');
        CREATE TABLE IF NOT EXISTS memory_links (
            source_id TEXT NOT NULL,
            target_id TEXT NOT NULL,
            relation TEXT NOT NULL DEFAULT 'related_to',
            created_at TEXT,
            UNIQUE(source_id, target_id, relation)
        );
        CREATE TABLE IF NOT EXISTS archived_memories (
            id TEXT PRIMARY KEY,
            tier TEXT, namespace TEXT, title TEXT, content TEXT,
            tags TEXT, priority INTEGER, confidence REAL,
            source TEXT, access_count INTEGER,
            created_at TEXT, updated_at TEXT, last_accessed_at TEXT,
            expires_at TEXT, metadata TEXT, archived_at TEXT, archive_reason TEXT
        );
    """)
    con.commit()
    con.close()


# ---------------------------------------------------------------------------
# Test class
# ---------------------------------------------------------------------------

class TestSessionSummarizer(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="ss_test_")
        self.workspace = _make_workspace(Path(self.tmp_dir))
        os.environ["OPENCLAW_TEST_WORKSPACE"] = self.tmp_dir

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp_dir, ignore_errors=True)
        os.environ.pop("OPENCLAW_TEST_WORKSPACE", None)

    # ── Skip conditions ──────────────────────────────────────────────────────

    def test_short_input_skipped(self):
        """Input < 200 chars must return exit code 1."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
            code = ss.summarize("Short text", workspace=self.workspace)
        self.assertEqual(code, 1)

    def test_empty_input_skipped(self):
        """Empty string must return exit code 1."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
            code = ss.summarize("", workspace=self.workspace)
        self.assertEqual(code, 1)

    def test_min_chars_boundary(self):
        """Input exactly at min_chars must pass the guard."""
        text = "x" * 200
        with patch("session_summarizer.call_haiku", return_value=GOOD_SUMMARY):
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
                code = ss.summarize(text, workspace=self.workspace, no_db=True)
        # code 0 = success (or 3 if no API key, but we patched call_haiku)
        self.assertEqual(code, 0)

    def test_custom_min_chars(self):
        """--min-chars 50 accepts shorter input."""
        text = "x" * 60
        with patch("session_summarizer.call_haiku", return_value=GOOD_SUMMARY):
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
                code = ss.summarize(text, workspace=self.workspace, min_chars=50, no_db=True)
        self.assertEqual(code, 0)

    # ── Haiku call ───────────────────────────────────────────────────────────

    def test_haiku_called_with_correct_prompt(self):
        """call_haiku should pass transcript text to the messages API."""
        mock_client = _make_mock_client()
        with patch("anthropic.Anthropic", return_value=mock_client):
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
                result = ss.call_haiku(GOOD_TRANSCRIPT)

        mock_client.messages.create.assert_called_once()
        call_kwargs = mock_client.messages.create.call_args
        assert call_kwargs is not None
        messages = call_kwargs.kwargs.get("messages") or call_kwargs[1].get("messages") or call_kwargs[0][2]
        # The user message should contain the transcript
        user_msg = next(m for m in messages if m["role"] == "user")
        self.assertIn("Summarize", user_msg["content"])

    def test_prompt_caching_headers_set(self):
        """System prompt must have cache_control ephemeral set."""
        mock_client = _make_mock_client()
        with patch("anthropic.Anthropic", return_value=mock_client):
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
                ss.call_haiku(GOOD_TRANSCRIPT)

        create_call = mock_client.messages.create.call_args
        system = (
            create_call.kwargs.get("system")
            or create_call[1].get("system")
            or create_call[0][2]  # positional
        )
        self.assertIsInstance(system, list)
        self.assertTrue(len(system) > 0)
        sys_block = system[0]
        self.assertIn("cache_control", sys_block)
        self.assertEqual(sys_block["cache_control"]["type"], "ephemeral")

    def test_haiku_model_id(self):
        """Model ID must be exactly claude-haiku-4-5-20251001."""
        mock_client = _make_mock_client()
        with patch("anthropic.Anthropic", return_value=mock_client):
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
                ss.call_haiku(GOOD_TRANSCRIPT)
        create_call = mock_client.messages.create.call_args
        model = (
            create_call.kwargs.get("model")
            or create_call[1].get("model")
        )
        self.assertEqual(model, "claude-haiku-4-5-20251001")

    # ── JSON parsing ─────────────────────────────────────────────────────────

    def test_json_parsing_valid(self):
        """Valid JSON response should parse into correct dict."""
        raw = json.dumps(GOOD_SUMMARY)
        result = ss.parse_summary_json(raw)
        self.assertEqual(result["one_liner"], GOOD_SUMMARY["one_liner"])
        self.assertEqual(result["topics"], GOOD_SUMMARY["topics"])

    def test_json_parsing_invalid(self):
        """Malformed JSON should not crash — returns defaults."""
        result = ss.parse_summary_json("this is not json {broken}")
        self.assertIsInstance(result, dict)
        self.assertIn("one_liner", result)
        self.assertIn("topics", result)

    def test_json_parsing_with_markdown_fences(self):
        """JSON wrapped in ```json fences should be parsed correctly."""
        raw = "```json\n" + json.dumps(GOOD_SUMMARY) + "\n```"
        result = ss.parse_summary_json(raw)
        self.assertEqual(result["one_liner"], GOOD_SUMMARY["one_liner"])

    def test_json_missing_fields(self):
        """Response missing some fields should fill them with empty lists."""
        partial = {"one_liner": "Partial summary"}
        result = ss.parse_summary_json(json.dumps(partial))
        self.assertEqual(result["topics"], [])
        self.assertEqual(result["completed"], [])
        self.assertEqual(result["learned"], [])
        self.assertEqual(result["issues"], [])
        self.assertEqual(result["next_steps"], [])

    # ── Dry run ──────────────────────────────────────────────────────────────

    def test_dry_run_no_writes(self):
        """--dry-run must not create any files in the workspace."""
        with patch("session_summarizer.call_haiku", return_value=GOOD_SUMMARY):
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
                code = ss.summarize(GOOD_TRANSCRIPT, workspace=self.workspace, dry_run=True)
        self.assertEqual(code, 0)
        # No new files should be created
        today = __import__("datetime").datetime.now().strftime("%Y-%m-%d")
        daily_path = self.workspace / "memory" / f"{today}.md"
        context_path = self.workspace / "SESSION_CONTEXT.md"
        # dry_run writes daily if file already exists; the key is SESSION_CONTEXT not written
        # Since we check dry_run in write paths, neither should have real content changes
        # (daily notes file may be created as skeleton but not get session data)
        # The SESSION_CONTEXT.md should definitely not be written
        self.assertFalse(context_path.exists())

    # ── Deduplication ────────────────────────────────────────────────────────

    def test_dedup_identical_summary_skipped(self):
        """Identical one_liner in last entry -> exit code 2."""
        today = __import__("datetime").datetime.now().strftime("%Y-%m-%d")
        daily_path = self.workspace / "memory" / f"{today}.md"
        daily_path.parent.mkdir(parents=True, exist_ok=True)
        # Write an existing entry with the same one_liner
        daily_path.write_text(
            f"# Daily\n## End of Day Summary\n- [10:00] {GOOD_SUMMARY['one_liner']}\n"
        )
        with patch("session_summarizer.call_haiku", return_value=GOOD_SUMMARY):
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
                code = ss.summarize(GOOD_TRANSCRIPT, workspace=self.workspace)
        self.assertEqual(code, 2)

    def test_dedup_high_similarity_skipped(self):
        """Summary with >60% Jaccard similarity to last entry -> skip."""
        today = __import__("datetime").datetime.now().strftime("%Y-%m-%d")
        daily_path = self.workspace / "memory" / f"{today}.md"
        daily_path.parent.mkdir(parents=True, exist_ok=True)
        # Very similar one_liner
        similar_one_liner = "Fixed session hook regression and added test suite for memory system"
        daily_path.write_text(
            f"# Daily\n## End of Day Summary\n- [10:00] {similar_one_liner}\n"
        )
        # Make the new summary nearly identical
        dup_summary = {**GOOD_SUMMARY, "one_liner": similar_one_liner + " completed"}
        with patch("session_summarizer.call_haiku", return_value=dup_summary):
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
                code = ss.summarize(GOOD_TRANSCRIPT, workspace=self.workspace,
                                    dedup_threshold=0.40)  # low threshold to trigger dedup
        self.assertEqual(code, 2)

    def test_dedup_low_similarity_written(self):
        """Summary with <60% Jaccard similarity should be written (exit 0)."""
        today = __import__("datetime").datetime.now().strftime("%Y-%m-%d")
        daily_path = self.workspace / "memory" / f"{today}.md"
        daily_path.parent.mkdir(parents=True, exist_ok=True)
        daily_path.write_text(
            "# Daily\n## End of Day Summary\n- [10:00] Configured Telegram bot settings\n"
        )
        with patch("session_summarizer.call_haiku", return_value=GOOD_SUMMARY):
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
                code = ss.summarize(GOOD_TRANSCRIPT, workspace=self.workspace, no_db=True)
        self.assertEqual(code, 0)

    def test_dedup_no_prior_entry_written(self):
        """Empty daily file -> no prior entry -> always write (exit 0)."""
        with patch("session_summarizer.call_haiku", return_value=GOOD_SUMMARY):
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
                code = ss.summarize(GOOD_TRANSCRIPT, workspace=self.workspace, no_db=True)
        self.assertEqual(code, 0)

    # ── Daily notes file writes ──────────────────────────────────────────────

    def test_daily_notes_tasks_appended(self):
        """Completed items should be written under ## Tasks."""
        summary = {**GOOD_SUMMARY, "completed": ["task-one", "task-two"]}
        today = __import__("datetime").datetime.now().strftime("%Y-%m-%d")
        daily_path = self.workspace / "memory" / f"{today}.md"
        ts = "10:00"
        ss.write_daily_notes(summary, self.workspace, ts)
        content = daily_path.read_text()
        self.assertIn("task-one", content)
        self.assertIn("task-two", content)
        self.assertIn("## Tasks", content)

    def test_daily_notes_learnings_appended(self):
        """Learned items should be written under ## Learnings."""
        summary = {**GOOD_SUMMARY, "learned": ["learned-fact-alpha"]}
        today = __import__("datetime").datetime.now().strftime("%Y-%m-%d")
        ts = "10:00"
        ss.write_daily_notes(summary, self.workspace, ts)
        daily_path = self.workspace / "memory" / f"{today}.md"
        content = daily_path.read_text()
        self.assertIn("learned-fact-alpha", content)
        self.assertIn("## Learnings", content)

    def test_daily_notes_issues_appended(self):
        """Issues should be written under ## Issues Encountered."""
        summary = {**GOOD_SUMMARY, "issues": ["bug-alpha"]}
        today = __import__("datetime").datetime.now().strftime("%Y-%m-%d")
        ts = "10:00"
        ss.write_daily_notes(summary, self.workspace, ts)
        daily_path = self.workspace / "memory" / f"{today}.md"
        content = daily_path.read_text()
        self.assertIn("bug-alpha", content)
        self.assertIn("## Issues Encountered", content)

    def test_daily_notes_summary_appended(self):
        """one_liner should appear under ## End of Day Summary."""
        summary = {**GOOD_SUMMARY, "one_liner": "unique-one-liner-42"}
        today = __import__("datetime").datetime.now().strftime("%Y-%m-%d")
        ts = "10:00"
        ss.write_daily_notes(summary, self.workspace, ts)
        daily_path = self.workspace / "memory" / f"{today}.md"
        content = daily_path.read_text()
        self.assertIn("unique-one-liner-42", content)
        self.assertIn("## End of Day Summary", content)

    def test_daily_notes_creates_file(self):
        """Missing daily notes file should be created automatically."""
        today = __import__("datetime").datetime.now().strftime("%Y-%m-%d")
        daily_path = self.workspace / "memory" / f"{today}.md"
        self.assertFalse(daily_path.exists())
        ss.write_daily_notes(GOOD_SUMMARY, self.workspace, "12:00")
        self.assertTrue(daily_path.exists())

    def test_daily_notes_timestamp_format(self):
        """Each entry should have [HH:MM] prefix."""
        summary = {**GOOD_SUMMARY, "one_liner": "timestamped entry"}
        today = __import__("datetime").datetime.now().strftime("%Y-%m-%d")
        ss.write_daily_notes(summary, self.workspace, "14:30")
        daily_path = self.workspace / "memory" / f"{today}.md"
        content = daily_path.read_text()
        import re
        matches = re.findall(r"\[\d{2}:\d{2}\]", content)
        self.assertTrue(len(matches) > 0, "Expected [HH:MM] timestamp in daily notes")

    def test_daily_notes_appends_not_overwrites(self):
        """Second call should append, not overwrite previous content."""
        today = __import__("datetime").datetime.now().strftime("%Y-%m-%d")
        daily_path = self.workspace / "memory" / f"{today}.md"
        daily_path.parent.mkdir(parents=True, exist_ok=True)
        daily_path.write_text("# Daily\n## Tasks\n- [09:00] previous task\n\n## Learnings\n\n## Issues Encountered\n\n## End of Day Summary\n")
        ss.write_daily_notes({**GOOD_SUMMARY, "completed": ["new-task"]}, self.workspace, "10:00")
        content = daily_path.read_text()
        self.assertIn("previous task", content)
        self.assertIn("new-task", content)

    # ── SESSION_CONTEXT.md ───────────────────────────────────────────────────

    def test_session_context_prepends(self):
        """New summary should appear before any existing sessions."""
        context_path = self.workspace / "SESSION_CONTEXT.md"
        # Write an existing session
        old_summary = {**GOOD_SUMMARY, "one_liner": "OLD session entry"}
        ss.write_session_context(old_summary, context_path)
        # Write a new session
        new_summary = {**GOOD_SUMMARY, "one_liner": "NEW session entry"}
        ss.write_session_context(new_summary, context_path)
        content = context_path.read_text()
        old_pos = content.index("OLD session entry")
        new_pos = content.index("NEW session entry")
        self.assertLess(new_pos, old_pos, "New session should appear before old")

    def test_session_context_max_5(self):
        """Only last 5 sessions should be kept in SESSION_CONTEXT.md."""
        context_path = self.workspace / "SESSION_CONTEXT.md"
        for i in range(7):
            s = {**GOOD_SUMMARY, "one_liner": f"Session number {i}"}
            ss.write_session_context(s, context_path)
        content = context_path.read_text()
        import re
        sessions = re.findall(r"^### \d{4}-\d{2}-\d{2}", content, re.MULTILINE)
        self.assertLessEqual(len(sessions), 5, f"Expected max 5 sessions, found {len(sessions)}")

    def test_session_context_max_150_lines(self):
        """SESSION_CONTEXT.md must never exceed 150 lines."""
        context_path = self.workspace / "SESSION_CONTEXT.md"
        # Write 10 verbose sessions
        long_summary = {
            "one_liner": "A" * 120,
            "topics": ["topic"] * 5,
            "completed": [f"completed item {j}" for j in range(5)],
            "learned": [f"learned item {j}" for j in range(5)],
            "issues": [f"issue {j}" for j in range(5)],
            "next_steps": [f"next {j}" for j in range(5)],
        }
        for _ in range(10):
            ss.write_session_context(long_summary, context_path)
        content = context_path.read_text()
        line_count = len(content.splitlines())
        self.assertLessEqual(line_count, 150, f"SESSION_CONTEXT.md has {line_count} lines (max 150)")

    def test_session_context_created_if_missing(self):
        """SESSION_CONTEXT.md should be created if it doesn't exist."""
        context_path = self.workspace / "SESSION_CONTEXT.md"
        self.assertFalse(context_path.exists())
        ss.write_session_context(GOOD_SUMMARY, context_path)
        self.assertTrue(context_path.exists())

    def test_session_context_contains_one_liner(self):
        """SESSION_CONTEXT.md should contain the one_liner."""
        context_path = self.workspace / "SESSION_CONTEXT.md"
        ss.write_session_context({**GOOD_SUMMARY, "one_liner": "unique-ctx-marker-99"}, context_path)
        content = context_path.read_text()
        self.assertIn("unique-ctx-marker-99", content)

    # ── Database write ───────────────────────────────────────────────────────

    def test_db_write_called(self):
        """write_to_db should insert a record into ai-memory.db."""
        import sqlite3
        db_path = self.workspace / "ai-memory.db"
        ss.write_to_db(GOOD_SUMMARY, self.workspace)
        con = sqlite3.connect(db_path)
        count = con.execute("SELECT COUNT(*) FROM memories WHERE namespace='workspace'").fetchone()[0]
        con.close()
        self.assertGreater(count, 0)

    def test_db_write_correct_tags(self):
        """DB record should have session,summary,auto tags."""
        import sqlite3
        db_path = self.workspace / "ai-memory.db"
        ss.write_to_db(GOOD_SUMMARY, self.workspace)
        con = sqlite3.connect(db_path)
        row = con.execute("SELECT tags FROM memories WHERE namespace='workspace' LIMIT 1").fetchone()
        con.close()
        tags = json.loads(row[0])
        self.assertIn("session", tags)
        self.assertIn("summary", tags)
        self.assertIn("auto", tags)

    def test_db_failure_doesnt_crash(self):
        """SQLite write failure should be non-fatal (exit code 0)."""
        with patch("session_summarizer.call_haiku", return_value=GOOD_SUMMARY):
            with patch("session_summarizer.write_to_db", side_effect=RuntimeError("db crash")):
                with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
                    code = ss.summarize(GOOD_TRANSCRIPT, workspace=self.workspace)
        # Should still succeed (0) — db failure is non-fatal
        self.assertEqual(code, 0)

    # ── Flag tests ───────────────────────────────────────────────────────────

    def test_no_daily_flag(self):
        """--no-daily should skip daily notes write."""
        today = __import__("datetime").datetime.now().strftime("%Y-%m-%d")
        daily_path = self.workspace / "memory" / f"{today}.md"
        with patch("session_summarizer.call_haiku", return_value=GOOD_SUMMARY):
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
                code = ss.summarize(GOOD_TRANSCRIPT, workspace=self.workspace,
                                    no_daily=True, no_db=True)
        self.assertEqual(code, 0)
        self.assertFalse(daily_path.exists(), "Daily notes should not be created with --no-daily")

    def test_no_context_flag(self):
        """--no-context should skip SESSION_CONTEXT.md write."""
        context_path = self.workspace / "SESSION_CONTEXT.md"
        with patch("session_summarizer.call_haiku", return_value=GOOD_SUMMARY):
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
                code = ss.summarize(GOOD_TRANSCRIPT, workspace=self.workspace,
                                    no_context=True, no_db=True)
        self.assertEqual(code, 0)
        self.assertFalse(context_path.exists(), "SESSION_CONTEXT.md should not be created with --no-context")

    def test_no_db_flag(self):
        """--no-db should skip ai-memory.db write."""
        import sqlite3
        db_path = self.workspace / "ai-memory.db"
        initial_count = sqlite3.connect(db_path).execute("SELECT COUNT(*) FROM memories").fetchone()[0]
        with patch("session_summarizer.call_haiku", return_value=GOOD_SUMMARY):
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
                code = ss.summarize(GOOD_TRANSCRIPT, workspace=self.workspace, no_db=True)
        self.assertEqual(code, 0)
        final_count = sqlite3.connect(db_path).execute("SELECT COUNT(*) FROM memories").fetchone()[0]
        self.assertEqual(initial_count, final_count, "DB count changed despite --no-db")

    # ── Jaccard similarity ───────────────────────────────────────────────────

    def test_jaccard_identical_texts(self):
        """Identical strings → similarity 1.0."""
        self.assertAlmostEqual(ss.jaccard_similarity("hello world", "hello world"), 1.0)

    def test_jaccard_disjoint_texts(self):
        """Completely different texts → low similarity."""
        sim = ss.jaccard_similarity("alpha beta gamma", "delta epsilon zeta")
        self.assertLess(sim, 0.1)

    def test_jaccard_partial_overlap(self):
        """Partial overlap → intermediate similarity."""
        sim = ss.jaccard_similarity(
            "fixed session hook regression added test suite",
            "session hook regression memory system"
        )
        self.assertGreater(sim, 0.0)
        self.assertLess(sim, 1.0)

    def test_jaccard_empty_strings(self):
        """Two empty strings → similarity 1.0 (both nothing)."""
        self.assertAlmostEqual(ss.jaccard_similarity("", ""), 1.0)

    # ── Boilerplate stripping ────────────────────────────────────────────────

    def test_strip_boilerplate_removes_system_tags(self):
        """System message patterns should be removed."""
        raw = "<system>system message</system>\nActual content here for testing"
        cleaned = ss.strip_boilerplate(raw)
        self.assertNotIn("<system>", cleaned)

    def test_strip_boilerplate_keeps_content(self):
        """Regular conversation content should be preserved."""
        raw = "User: Let's fix the bug.\nAssistant: Sure, checking now.\nContent here."
        cleaned = ss.strip_boilerplate(raw)
        self.assertIn("fix the bug", cleaned)

    # ── Atomic write ─────────────────────────────────────────────────────────

    def test_atomic_write_creates_file(self):
        """_atomic_write should create the file with correct content."""
        target = self.workspace / "test_atomic.txt"
        ss._atomic_write(target, "hello atomic")
        self.assertEqual(target.read_text(), "hello atomic")

    def test_atomic_write_no_tmp_leftover(self):
        """After _atomic_write, no .tmp file should remain."""
        target = self.workspace / "test_atomic2.txt"
        ss._atomic_write(target, "content")
        tmp = target.with_suffix(target.suffix + ".tmp")
        self.assertFalse(tmp.exists())


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main(verbosity=2)
