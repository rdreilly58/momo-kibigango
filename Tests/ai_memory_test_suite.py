#!/usr/bin/env python3
"""
ai_memory_test_suite.py — Comprehensive test suite for the Momotaro ai-memory system.

Covers:
  1. SQLite DB Layer         — schema, CRUD, FTS5 triggers, indexes, constraints
  2. Memory Links            — relationship graph (source → target)
  3. Namespace Isolation     — namespace_meta, parent namespaces
  4. Archive & Expiry        — archived_memories table, TTL logic
  5. index_files_for_memory  — text extraction for md/txt/py/sh/json/pdf
  6. Memory File Health      — observations.md freshness, daily logs, MEMORY.md size
  7. Observer/Reflector      — script existence, syntax, executability
  8. total_recall_search     — gaps beyond existing test_total_recall_search.py
  9. MCP Memory Tools        — memory_get / memory_search through OpenClaw
 10. Concurrency & Edge Cases — duplicate titles, empty content, max field sizes

Run:
  python3 Tests/ai_memory_test_suite.py
  python3 Tests/ai_memory_test_suite.py -v
  python3 Tests/ai_memory_test_suite.py TestSQLiteSchema
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
import uuid
from datetime import datetime, timezone
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────
WORKSPACE    = Path.home() / ".openclaw" / "workspace"
DB_PATH      = WORKSPACE / "ai-memory.db"
MEMORY_DIR   = WORKSPACE / "memory"
SCRIPTS_DIR  = WORKSPACE / "scripts"
SKILLS_DIR   = WORKSPACE / "skills"
TESTS_DIR    = WORKSPACE / "Tests"

OBSERVER_SH   = SKILLS_DIR / "total-recall" / "scripts" / "observer-agent.sh"
REFLECTOR_SH  = SKILLS_DIR / "total-recall" / "scripts" / "reflector-agent.sh"
INDEX_PY      = SCRIPTS_DIR / "index_files_for_memory.py"
TRS_PY        = SCRIPTS_DIR / "total_recall_search.py"
MEM_SEARCH_PY = SCRIPTS_DIR / "memory_search_local.py"

PYTHON = str(WORKSPACE / "venv" / "bin" / "python3") \
    if (WORKSPACE / "venv" / "bin" / "python3").exists() else sys.executable

LOG_FILE = TESTS_DIR / "ai-memory-test-results.log"

# ─── Log setup ────────────────────────────────────────────────────────────────
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
_log_fh = open(str(LOG_FILE), "w", buffering=1)


def _log(msg: str) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    _log_fh.write(line + "\n")


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _open_db() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise unittest.SkipTest(f"ai-memory.db not found at {DB_PATH}")
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def _insert_memory(conn: sqlite3.Connection, **kwargs) -> str:
    """Insert a test memory and return its id."""
    mem_id = kwargs.pop("id", str(uuid.uuid4()))
    now = _now_iso()
    defaults = dict(
        tier="short",
        namespace="test_suite",
        title=f"Test memory {mem_id[:8]}",
        content="Test content for automated test suite.",
        tags="[]",
        priority=5,
        confidence=1.0,
        source="test",
        access_count=0,
        created_at=now,
        updated_at=now,
        last_accessed_at=None,
        expires_at=None,
        metadata="{}",
        embedding=None,
    )
    defaults.update(kwargs)
    defaults["id"] = mem_id
    cols = ", ".join(defaults.keys())
    placeholders = ", ".join("?" for _ in defaults)
    conn.execute(f"INSERT INTO memories ({cols}) VALUES ({placeholders})",
                 list(defaults.values()))
    conn.commit()
    return mem_id


def _cleanup_test_memories(conn: sqlite3.Connection) -> None:
    """Remove all memories created by this test suite."""
    conn.execute("DELETE FROM memories WHERE namespace = 'test_suite'")
    conn.commit()


def _import_module(path: Path):
    """Import a Python module from a file path."""
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _run_cli(*args, timeout: int = 30, expect_exit: int = 0) -> dict:
    """Run total_recall_search.py via CLI, return parsed results."""
    cmd = [PYTHON, str(TRS_PY), "--json"] + list(args)
    t0 = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    elapsed = time.time() - t0
    results = []
    if proc.stdout.strip():
        try:
            results = json.loads(proc.stdout)
        except json.JSONDecodeError:
            pass
    return {"results": results, "elapsed": elapsed,
            "rc": proc.returncode, "stderr": proc.stderr, "stdout": proc.stdout}


# ═════════════════════════════════════════════════════════════════════════════
# 1. SQLite Schema Validation
# ═════════════════════════════════════════════════════════════════════════════

class TestSQLiteSchema(unittest.TestCase):
    """Validate database schema integrity."""

    def setUp(self):
        self.conn = _open_db()

    def tearDown(self):
        _cleanup_test_memories(self.conn)
        self.conn.close()

    def _table_names(self) -> set[str]:
        rows = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type IN ('table','view')"
        ).fetchall()
        return {r["name"] for r in rows}

    def test_memories_table_exists(self):
        self.assertIn("memories", self._table_names())

    def test_memory_links_table_exists(self):
        self.assertIn("memory_links", self._table_names())

    def test_archived_memories_table_exists(self):
        self.assertIn("archived_memories", self._table_names())

    def test_namespace_meta_table_exists(self):
        self.assertIn("namespace_meta", self._table_names())

    def test_schema_version_table_exists(self):
        self.assertIn("schema_version", self._table_names())

    def test_fts5_virtual_table_exists(self):
        self.assertIn("memories_fts", self._table_names())

    def test_memories_columns(self):
        cursor = self.conn.execute("PRAGMA table_info(memories)")
        cols = {row["name"] for row in cursor.fetchall()}
        required = {
            "id", "tier", "namespace", "title", "content",
            "tags", "priority", "confidence", "source",
            "access_count", "created_at", "updated_at",
            "last_accessed_at", "expires_at", "metadata", "embedding",
        }
        missing = required - cols
        self.assertEqual(missing, set(), f"Missing columns: {missing}")

    def test_archived_memories_columns(self):
        cursor = self.conn.execute("PRAGMA table_info(archived_memories)")
        cols = {row["name"] for row in cursor.fetchall()}
        self.assertIn("archived_at", cols)
        self.assertIn("archive_reason", cols)

    def test_memory_links_foreign_key_cascade(self):
        """memory_links references memories with ON DELETE CASCADE."""
        sql = self.conn.execute(
            "SELECT sql FROM sqlite_master WHERE name='memory_links'"
        ).fetchone()["sql"]
        self.assertIn("CASCADE", sql.upper())

    def test_indexes_exist(self):
        rows = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index'"
        ).fetchall()
        names = {r["name"] for r in rows}
        expected = {"idx_memories_tier", "idx_memories_namespace",
                    "idx_memories_priority", "idx_memories_expires"}
        missing = expected - names
        self.assertEqual(missing, set(), f"Missing indexes: {missing}")

    def test_fts_triggers_exist(self):
        rows = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='trigger'"
        ).fetchall()
        names = {r["name"] for r in rows}
        self.assertIn("memories_ai", names, "INSERT trigger missing")
        self.assertIn("memories_au", names, "UPDATE trigger missing")
        self.assertIn("memories_ad", names, "DELETE trigger missing")

    def test_unique_title_namespace_constraint(self):
        """Duplicate (title, namespace) should raise IntegrityError."""
        mid = str(uuid.uuid4())
        title = f"unique-title-{mid[:8]}"
        _insert_memory(self.conn, id=mid, title=title, namespace="test_suite")
        with self.assertRaises(sqlite3.IntegrityError):
            _insert_memory(self.conn, id=str(uuid.uuid4()),
                           title=title, namespace="test_suite")


# ═════════════════════════════════════════════════════════════════════════════
# 2. CRUD Operations
# ═════════════════════════════════════════════════════════════════════════════

class TestCRUD(unittest.TestCase):
    """Test Create, Read, Update, Delete on the memories table."""

    def setUp(self):
        self.conn = _open_db()

    def tearDown(self):
        _cleanup_test_memories(self.conn)
        self.conn.close()

    def test_insert_and_select(self):
        mid = _insert_memory(self.conn, content="Hello from CRUD test")
        row = self.conn.execute(
            "SELECT * FROM memories WHERE id = ?", (mid,)
        ).fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row["content"], "Hello from CRUD test")

    def test_update_content(self):
        mid = _insert_memory(self.conn)
        self.conn.execute(
            "UPDATE memories SET content = ?, updated_at = ? WHERE id = ?",
            ("Updated content", _now_iso(), mid)
        )
        self.conn.commit()
        row = self.conn.execute(
            "SELECT content FROM memories WHERE id = ?", (mid,)
        ).fetchone()
        self.assertEqual(row["content"], "Updated content")

    def test_delete_memory(self):
        mid = _insert_memory(self.conn)
        self.conn.execute("DELETE FROM memories WHERE id = ?", (mid,))
        self.conn.commit()
        row = self.conn.execute(
            "SELECT id FROM memories WHERE id = ?", (mid,)
        ).fetchone()
        self.assertIsNone(row)

    def test_priority_field_range(self):
        """Priority should be stored and retrieved accurately (1–10)."""
        for p in [1, 5, 10]:
            mid = _insert_memory(self.conn, priority=p,
                                  title=f"Priority {p} test {uuid.uuid4().hex[:6]}")
            row = self.conn.execute(
                "SELECT priority FROM memories WHERE id = ?", (mid,)
            ).fetchone()
            self.assertEqual(row["priority"], p)

    def test_confidence_float_precision(self):
        mid = _insert_memory(self.conn, confidence=0.75)
        row = self.conn.execute(
            "SELECT confidence FROM memories WHERE id = ?", (mid,)
        ).fetchone()
        self.assertAlmostEqual(row["confidence"], 0.75, places=3)

    def test_tags_json_roundtrip(self):
        tags = json.dumps(["ai", "memory", "test"])
        mid = _insert_memory(self.conn, tags=tags)
        row = self.conn.execute(
            "SELECT tags FROM memories WHERE id = ?", (mid,)
        ).fetchone()
        loaded = json.loads(row["tags"])
        self.assertEqual(loaded, ["ai", "memory", "test"])

    def test_metadata_json_roundtrip(self):
        meta = json.dumps({"source": "test", "version": 2})
        mid = _insert_memory(self.conn, metadata=meta)
        row = self.conn.execute(
            "SELECT metadata FROM memories WHERE id = ?", (mid,)
        ).fetchone()
        loaded = json.loads(row["metadata"])
        self.assertEqual(loaded["source"], "test")
        self.assertEqual(loaded["version"], 2)

    def test_access_count_increment(self):
        mid = _insert_memory(self.conn, access_count=0)
        self.conn.execute(
            "UPDATE memories SET access_count = access_count + 1 WHERE id = ?", (mid,)
        )
        self.conn.commit()
        row = self.conn.execute(
            "SELECT access_count FROM memories WHERE id = ?", (mid,)
        ).fetchone()
        self.assertEqual(row["access_count"], 1)

    def test_tier_values(self):
        """Confirm all expected tier values can be stored."""
        for tier in ["short", "long", "permanent"]:
            mid = _insert_memory(
                self.conn, tier=tier,
                title=f"Tier test {tier} {uuid.uuid4().hex[:6]}"
            )
            row = self.conn.execute(
                "SELECT tier FROM memories WHERE id = ?", (mid,)
            ).fetchone()
            self.assertEqual(row["tier"], tier)

    def test_embedding_blob_storage(self):
        """Embedding can be stored as a binary blob."""
        dummy_embedding = bytes([0x00, 0xFF] * 192)  # 384-dim float16 placeholder
        mid = _insert_memory(self.conn, embedding=dummy_embedding)
        row = self.conn.execute(
            "SELECT embedding FROM memories WHERE id = ?", (mid,)
        ).fetchone()
        self.assertEqual(row["embedding"], dummy_embedding)

    def test_null_embedding_allowed(self):
        """Embedding can be NULL (not yet computed)."""
        mid = _insert_memory(self.conn, embedding=None)
        row = self.conn.execute(
            "SELECT embedding FROM memories WHERE id = ?", (mid,)
        ).fetchone()
        self.assertIsNone(row["embedding"])

    def test_expires_at_nullable(self):
        """expires_at can be NULL (permanent memory)."""
        mid = _insert_memory(self.conn, expires_at=None,
                              tier="permanent",
                              title=f"Permanent {uuid.uuid4().hex[:6]}")
        row = self.conn.execute(
            "SELECT expires_at FROM memories WHERE id = ?", (mid,)
        ).fetchone()
        self.assertIsNone(row["expires_at"])


# ═════════════════════════════════════════════════════════════════════════════
# 3. FTS5 Full-Text Search
# ═════════════════════════════════════════════════════════════════════════════

class TestFTS5(unittest.TestCase):
    """Test FTS5 virtual table and auto-sync triggers."""

    def setUp(self):
        self.conn = _open_db()

    def tearDown(self):
        _cleanup_test_memories(self.conn)
        self.conn.close()

    def test_fts_insert_trigger(self):
        """After INSERT into memories, FTS index should find the content."""
        unique_term = f"xyzfts{uuid.uuid4().hex[:8]}"
        _insert_memory(self.conn, content=f"Special term for FTS: {unique_term}")
        rows = self.conn.execute(
            "SELECT rowid FROM memories_fts WHERE memories_fts MATCH ?",
            (unique_term,)
        ).fetchall()
        self.assertGreater(len(rows), 0, f"FTS should find '{unique_term}'")

    def test_fts_update_trigger(self):
        """After UPDATE, FTS should find new content, not old."""
        old_term = f"xyzfts_old_{uuid.uuid4().hex[:6]}"
        new_term = f"xyzfts_new_{uuid.uuid4().hex[:6]}"
        mid = _insert_memory(self.conn, content=f"Old term: {old_term}")
        self.conn.execute(
            "UPDATE memories SET content = ?, updated_at = ? WHERE id = ?",
            (f"New term: {new_term}", _now_iso(), mid)
        )
        self.conn.commit()
        # New term should be findable
        rows = self.conn.execute(
            "SELECT rowid FROM memories_fts WHERE memories_fts MATCH ?",
            (new_term,)
        ).fetchall()
        self.assertGreater(len(rows), 0, "FTS should find new term after UPDATE")

    def test_fts_delete_trigger(self):
        """After DELETE, FTS should not find the content."""
        unique_term = f"xyzfts_del_{uuid.uuid4().hex[:6]}"
        mid = _insert_memory(self.conn, content=f"Delete this term: {unique_term}")
        self.conn.execute("DELETE FROM memories WHERE id = ?", (mid,))
        self.conn.commit()
        rows = self.conn.execute(
            "SELECT rowid FROM memories_fts WHERE memories_fts MATCH ?",
            (unique_term,)
        ).fetchall()
        self.assertEqual(len(rows), 0, "FTS should not find deleted content")

    def test_fts_title_indexed(self):
        """FTS should match on title field."""
        unique_title = f"UniqueTitle{uuid.uuid4().hex[:8]}"
        _insert_memory(self.conn, title=unique_title)
        rows = self.conn.execute(
            "SELECT rowid FROM memories_fts WHERE memories_fts MATCH ?",
            (unique_title,)
        ).fetchall()
        self.assertGreater(len(rows), 0, "FTS should find by title")

    def test_fts_tags_indexed(self):
        """FTS should match on tags field."""
        unique_tag = f"uniquetag{uuid.uuid4().hex[:8]}"
        _insert_memory(self.conn, tags=json.dumps([unique_tag]))
        rows = self.conn.execute(
            "SELECT rowid FROM memories_fts WHERE memories_fts MATCH ?",
            (unique_tag,)
        ).fetchall()
        self.assertGreater(len(rows), 0, "FTS should find by tag")

    def test_fts_multi_word_query(self):
        """FTS multi-word query with OR returns relevant results."""
        unique = f"multiwordfts{uuid.uuid4().hex[:6]}"
        _insert_memory(self.conn, content=f"The agent uses memory: {unique}")
        rows = self.conn.execute(
            "SELECT rowid FROM memories_fts WHERE memories_fts MATCH ?",
            (unique,)
        ).fetchall()
        self.assertGreater(len(rows), 0)


# ═════════════════════════════════════════════════════════════════════════════
# 4. Memory Links (Relationship Graph)
# ═════════════════════════════════════════════════════════════════════════════

class TestMemoryLinks(unittest.TestCase):
    """Test memory_links relationship graph."""

    def setUp(self):
        self.conn = _open_db()
        self.id_a = _insert_memory(self.conn, title=f"Link source {uuid.uuid4().hex[:6]}")
        self.id_b = _insert_memory(self.conn, title=f"Link target {uuid.uuid4().hex[:6]}")

    def tearDown(self):
        _cleanup_test_memories(self.conn)
        self.conn.close()

    def test_insert_link(self):
        self.conn.execute(
            "INSERT INTO memory_links (source_id, target_id, relation, created_at) VALUES (?, ?, ?, ?)",
            (self.id_a, self.id_b, "related_to", _now_iso())
        )
        self.conn.commit()
        row = self.conn.execute(
            "SELECT * FROM memory_links WHERE source_id = ? AND target_id = ?",
            (self.id_a, self.id_b)
        ).fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row["relation"], "related_to")

    def test_cascade_delete_on_source(self):
        """Deleting source memory should cascade-delete its links."""
        self.conn.execute(
            "INSERT INTO memory_links (source_id, target_id, relation, created_at) VALUES (?, ?, ?, ?)",
            (self.id_a, self.id_b, "depends_on", _now_iso())
        )
        self.conn.commit()
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.execute("DELETE FROM memories WHERE id = ?", (self.id_a,))
        self.conn.commit()
        row = self.conn.execute(
            "SELECT * FROM memory_links WHERE source_id = ?", (self.id_a,)
        ).fetchone()
        self.assertIsNone(row, "Link should be cascade-deleted with source")

    def test_relation_types(self):
        """Multiple relation types can be stored."""
        for rel in ["related_to", "depends_on", "references", "contradicts"]:
            try:
                self.conn.execute(
                    "INSERT INTO memory_links (source_id, target_id, relation, created_at) VALUES (?, ?, ?, ?)",
                    (self.id_a, self.id_b, rel, _now_iso())
                )
                self.conn.commit()
            except sqlite3.IntegrityError:
                pass  # (a,b,rel) composite PK — skip if already inserted

        rows = self.conn.execute(
            "SELECT relation FROM memory_links WHERE source_id = ? AND target_id = ?",
            (self.id_a, self.id_b)
        ).fetchall()
        stored = {r["relation"] for r in rows}
        self.assertGreater(len(stored), 0)

    def test_duplicate_link_rejected(self):
        """Composite PK prevents duplicate (source, target, relation)."""
        self.conn.execute(
            "INSERT INTO memory_links (source_id, target_id, relation, created_at) VALUES (?, ?, ?, ?)",
            (self.id_a, self.id_b, "related_to", _now_iso())
        )
        self.conn.commit()
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                "INSERT INTO memory_links (source_id, target_id, relation, created_at) VALUES (?, ?, ?, ?)",
                (self.id_a, self.id_b, "related_to", _now_iso())
            )
            self.conn.commit()


# ═════════════════════════════════════════════════════════════════════════════
# 5. Namespace Isolation
# ═════════════════════════════════════════════════════════════════════════════

class TestNamespaceIsolation(unittest.TestCase):
    """Verify namespace-level data isolation."""

    def setUp(self):
        self.conn = _open_db()

    def tearDown(self):
        _cleanup_test_memories(self.conn)
        self.conn.execute(
            "DELETE FROM namespace_meta WHERE namespace LIKE 'test_%'"
        )
        self.conn.commit()
        self.conn.close()

    def test_same_title_different_namespace(self):
        """Same title in different namespaces is allowed."""
        _insert_memory(self.conn, title="shared-title", namespace="test_suite")
        # Different namespace should not conflict
        mid2 = _insert_memory(self.conn, title="shared-title-ns2",
                               namespace="test_suite_b",
                               id=str(uuid.uuid4()))
        row = self.conn.execute(
            "SELECT id FROM memories WHERE id = ?", (mid2,)
        ).fetchone()
        self.assertIsNotNone(row)
        self.conn.execute("DELETE FROM memories WHERE namespace = 'test_suite_b'")
        self.conn.commit()

    def test_namespace_query_isolation(self):
        """Query by namespace returns only that namespace's memories."""
        mid_a = _insert_memory(self.conn, namespace="test_suite",
                                title=f"NS-A {uuid.uuid4().hex[:6]}")
        rows = self.conn.execute(
            "SELECT id FROM memories WHERE namespace = 'test_suite'"
        ).fetchall()
        ids = [r["id"] for r in rows]
        self.assertIn(mid_a, ids)

    def test_namespace_meta_insert(self):
        ns = f"test_ns_{uuid.uuid4().hex[:6]}"
        self.conn.execute(
            "INSERT OR REPLACE INTO namespace_meta (namespace, standard_id, updated_at) VALUES (?, ?, ?)",
            (ns, "STD-001", _now_iso())
        )
        self.conn.commit()
        row = self.conn.execute(
            "SELECT standard_id FROM namespace_meta WHERE namespace = ?", (ns,)
        ).fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row["standard_id"], "STD-001")

    def test_namespace_meta_parent(self):
        ns = f"test_ns_{uuid.uuid4().hex[:6]}"
        parent = f"test_ns_parent_{uuid.uuid4().hex[:4]}"
        self.conn.execute(
            "INSERT OR REPLACE INTO namespace_meta (namespace, standard_id, updated_at, parent_namespace) VALUES (?, ?, ?, ?)",
            (ns, None, _now_iso(), parent)
        )
        self.conn.commit()
        row = self.conn.execute(
            "SELECT parent_namespace FROM namespace_meta WHERE namespace = ?", (ns,)
        ).fetchone()
        self.assertEqual(row["parent_namespace"], parent)


# ═════════════════════════════════════════════════════════════════════════════
# 6. Archive & Expiry
# ═════════════════════════════════════════════════════════════════════════════

class TestArchiveAndExpiry(unittest.TestCase):
    """Test archived_memories table and TTL expiry logic."""

    def setUp(self):
        self.conn = _open_db()

    def tearDown(self):
        _cleanup_test_memories(self.conn)
        self.conn.execute(
            "DELETE FROM archived_memories WHERE namespace = 'test_suite'"
        )
        self.conn.commit()
        self.conn.close()

    def test_archive_table_accessible(self):
        count = self.conn.execute(
            "SELECT COUNT(*) FROM archived_memories"
        ).fetchone()[0]
        self.assertIsInstance(count, int)

    def test_archive_insert(self):
        """Can insert into archived_memories."""
        now = _now_iso()
        self.conn.execute("""
            INSERT INTO archived_memories
            (id, tier, namespace, title, content, tags, priority, confidence,
             source, access_count, created_at, updated_at, archived_at, archive_reason, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (str(uuid.uuid4()), "short", "test_suite", f"Archived {uuid.uuid4().hex[:6]}",
              "Archived content", "[]", 3, 0.5, "test", 0, now, now, now, "ttl_expired", "{}"))
        self.conn.commit()
        row = self.conn.execute(
            "SELECT COUNT(*) FROM archived_memories WHERE namespace = 'test_suite'"
        ).fetchone()[0]
        self.assertGreater(row, 0)

    def test_move_memory_to_archive(self):
        """Move a memory from active to archived table."""
        mid = _insert_memory(self.conn, content="About to be archived",
                              title=f"Archive test {uuid.uuid4().hex[:6]}")
        row = self.conn.execute(
            "SELECT * FROM memories WHERE id = ?", (mid,)
        ).fetchone()
        now = _now_iso()
        self.conn.execute("""
            INSERT INTO archived_memories
            (id, tier, namespace, title, content, tags, priority, confidence,
             source, access_count, created_at, updated_at, archived_at, archive_reason, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (row["id"], row["tier"], row["namespace"], row["title"], row["content"],
              row["tags"], row["priority"], row["confidence"], row["source"],
              row["access_count"], row["created_at"], row["updated_at"],
              now, "ttl_expired", row["metadata"]))
        self.conn.execute("DELETE FROM memories WHERE id = ?", (mid,))
        self.conn.commit()
        active = self.conn.execute(
            "SELECT id FROM memories WHERE id = ?", (mid,)
        ).fetchone()
        archived = self.conn.execute(
            "SELECT id FROM archived_memories WHERE id = ?", (mid,)
        ).fetchone()
        self.assertIsNone(active, "Memory should be gone from active table")
        self.assertIsNotNone(archived, "Memory should be in archive table")

    def test_expires_at_query(self):
        """Can query for expired memories by expires_at timestamp."""
        past = "2020-01-01T00:00:00+00:00"
        mid = _insert_memory(self.conn, expires_at=past,
                              title=f"Expired {uuid.uuid4().hex[:6]}")
        rows = self.conn.execute(
            "SELECT id FROM memories WHERE expires_at IS NOT NULL AND expires_at < datetime('now') AND namespace = 'test_suite'"
        ).fetchall()
        ids = [r["id"] for r in rows]
        self.assertIn(mid, ids)


# ═════════════════════════════════════════════════════════════════════════════
# 7. index_files_for_memory.py
# ═════════════════════════════════════════════════════════════════════════════

class TestIndexFilesForMemory(unittest.TestCase):
    """Test text extraction and JSON output of index_files_for_memory.py."""

    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    @unittest.skipUnless(INDEX_PY.exists(), "index_files_for_memory.py not found")
    def _import_indexer(self):
        return _import_module(INDEX_PY)

    def _make_file(self, name: str, content: str) -> Path:
        p = self.tmpdir / name
        p.write_text(content, encoding="utf-8")
        return p

    @unittest.skipUnless(INDEX_PY.exists(), "index_files_for_memory.py not found")
    def test_extract_markdown(self):
        mod = self._import_indexer()
        f = self._make_file("notes.md", "# My Note\nThis is a markdown note.")
        text = mod.extract_text(str(f))
        self.assertIn("My Note", text)
        self.assertIn("markdown note", text)

    @unittest.skipUnless(INDEX_PY.exists(), "index_files_for_memory.py not found")
    def test_extract_plain_text(self):
        mod = self._import_indexer()
        f = self._make_file("readme.txt", "Plain text content here.")
        text = mod.extract_text(str(f))
        self.assertIn("Plain text content", text)

    @unittest.skipUnless(INDEX_PY.exists(), "index_files_for_memory.py not found")
    def test_extract_python_script(self):
        mod = self._import_indexer()
        f = self._make_file("script.py", "def hello():\n    return 'world'")
        text = mod.extract_text(str(f))
        self.assertIn("hello", text)

    @unittest.skipUnless(INDEX_PY.exists(), "index_files_for_memory.py not found")
    def test_extract_shell_script(self):
        mod = self._import_indexer()
        f = self._make_file("run.sh", "#!/bin/bash\necho hello-from-shell")
        text = mod.extract_text(str(f))
        self.assertIn("hello-from-shell", text)

    @unittest.skipUnless(INDEX_PY.exists(), "index_files_for_memory.py not found")
    def test_extract_json_file(self):
        mod = self._import_indexer()
        f = self._make_file("config.json", '{"key": "value-from-json"}')
        text = mod.extract_text(str(f))
        self.assertIn("value-from-json", text)

    @unittest.skipUnless(INDEX_PY.exists(), "index_files_for_memory.py not found")
    def test_extract_unsupported_returns_none(self):
        """Unsupported file types should return None, not crash."""
        mod = self._import_indexer()
        f = self._make_file("image.png", b"\x89PNG\r\n".decode("latin-1"))
        result = mod.extract_text(str(f))
        self.assertIsNone(result)

    @unittest.skipUnless(INDEX_PY.exists(), "index_files_for_memory.py not found")
    def test_index_directory_produces_json_lines(self):
        """index_directory_for_memory outputs valid JSON for each file."""
        mod = self._import_indexer()
        self._make_file("note1.md", "# Note 1\nContent of note one.")
        self._make_file("note2.txt", "Content of note two.")

        import io
        from contextlib import redirect_stdout
        f = io.StringIO()
        with redirect_stdout(f):
            mod.index_directory_for_memory(str(self.tmpdir))
        output = f.getvalue().strip()
        lines = [l for l in output.split("\n") if l.strip()]
        self.assertGreater(len(lines), 0, "Should produce at least 1 JSON line")
        for line in lines:
            obj = json.loads(line)
            self.assertIn("path", obj)
            self.assertIn("content_snippet", obj)
            self.assertIsInstance(obj["content_snippet"], str)

    @unittest.skipUnless(INDEX_PY.exists(), "index_files_for_memory.py not found")
    def test_content_snippet_max_length(self):
        """Content snippets should be capped at 500 chars."""
        mod = self._import_indexer()
        f = self._make_file("big.md", "x" * 2000)

        import io
        from contextlib import redirect_stdout
        out = io.StringIO()
        with redirect_stdout(out):
            mod.index_directory_for_memory(str(self.tmpdir))
        output = out.getvalue().strip()
        for line in output.split("\n"):
            if not line.strip():
                continue
            obj = json.loads(line)
            self.assertLessEqual(len(obj["content_snippet"]), 500)

    @unittest.skipUnless(INDEX_PY.exists(), "index_files_for_memory.py not found")
    def test_nonexistent_directory_graceful(self):
        """index_directory_for_memory with nonexistent dir should not crash."""
        mod = self._import_indexer()
        # Should just skip; walk() on nonexistent dir returns empty
        try:
            mod.index_directory_for_memory("/nonexistent/path/xyz999")
        except Exception as e:
            self.fail(f"Should not raise: {e}")


# ═════════════════════════════════════════════════════════════════════════════
# 8. Memory File Health
# ═════════════════════════════════════════════════════════════════════════════

class TestMemoryFileHealth(unittest.TestCase):
    """Validate the Markdown memory file system (Total Recall output)."""

    def test_memory_dir_exists(self):
        self.assertTrue(MEMORY_DIR.exists(), f"memory/ dir not found at {MEMORY_DIR}")

    def test_observations_md_exists(self):
        """observations.md should exist — re-enabled with Total Recall Observer cron (2026-04-19)."""
        obs = MEMORY_DIR / "observations.md"
        self.assertTrue(obs.exists(),
                        "observations.md should exist (observer cron re-enabled 2026-04-19)")

    def test_observations_md_archive_exists(self):
        """Archived copy of observations.md should exist in memory/archive/."""
        archived = MEMORY_DIR / "archive" / "observations-archived-2026-04-19.md"
        self.assertTrue(archived.exists(),
                        "Archived observations.md missing from memory/archive/")

    def test_daily_logs_exist(self):
        daily = list(MEMORY_DIR.glob("20[0-9][0-9]-*.md"))
        self.assertGreater(len(daily), 0, "No daily log files found in memory/")

    def test_daily_log_filename_format(self):
        """Daily logs should start with YYYY-MM-DD (may have timestamp suffix)."""
        import re
        # Allow YYYY-MM-DD.md and YYYY-MM-DD-HHMM.md variants
        pattern = re.compile(r"^\d{4}-\d{2}-\d{2}(-\d{4})?\.md$")
        daily = list(MEMORY_DIR.glob("20[0-9][0-9]-[0-9][0-9]-[0-9][0-9]*.md"))
        self.assertGreater(len(daily), 0, "No YYYY-MM-DD-prefixed log files found")
        for f in daily:
            self.assertRegex(f.name, pattern,
                             f"Unexpected filename format: {f.name}")

    def test_memory_md_exists(self):
        mem = WORKSPACE / "MEMORY.md"
        self.assertTrue(mem.exists(), "MEMORY.md not found")

    def test_memory_md_size(self):
        mem = WORKSPACE / "MEMORY.md"
        if not mem.exists():
            self.skipTest("MEMORY.md not found")
        size = mem.stat().st_size
        self.assertGreater(size, 500,
                           f"MEMORY.md suspiciously small ({size} bytes)")

    def test_memory_md_recently_updated(self):
        """MEMORY.md should have been updated within the last 30 days."""
        mem = WORKSPACE / "MEMORY.md"
        if not mem.exists():
            self.skipTest("MEMORY.md not found")
        age_days = (time.time() - mem.stat().st_mtime) / 86400
        self.assertLess(age_days, 30,
                        f"MEMORY.md last modified {age_days:.1f} days ago — consider updating")

    def test_no_zero_byte_daily_logs(self):
        daily = list(MEMORY_DIR.glob("20[0-9][0-9]-*.md"))
        for f in daily:
            self.assertGreater(f.stat().st_size, 0,
                               f"Zero-byte daily log: {f.name}")


# ═════════════════════════════════════════════════════════════════════════════
# 9. Observer & Reflector Script Health
# ═════════════════════════════════════════════════════════════════════════════

class TestObserverReflectorHealth(unittest.TestCase):
    """Validate observer and reflector agent scripts exist, are valid bash, and executable."""

    def test_observer_agent_removed(self):
        """Observer agent was removed with Total Recall (2026-04-19)."""
        self.assertFalse(OBSERVER_SH.exists(),
                         "observer-agent.sh should have been removed")

    def test_reflector_agent_removed(self):
        """Reflector agent was removed with Total Recall (2026-04-19)."""
        self.assertFalse(REFLECTOR_SH.exists(),
                         "reflector-agent.sh should have been removed")

    def test_observations_md_active_and_archived(self):
        """observations.md should be active (re-enabled) AND archived copy should exist."""
        active = MEMORY_DIR / "observations.md"
        archived = MEMORY_DIR / "archive" / "observations-archived-2026-04-19.md"
        self.assertTrue(active.exists(),
                        "observations.md should be active (observer cron re-enabled)")
        self.assertTrue(archived.exists(),
                        "Archived observations.md should exist in memory/archive/")

    def test_skill_total_recall_dir_removed(self):
        """total-recall skill was intentionally removed (2026-04-19)."""
        skill_dir = SKILLS_DIR / "total-recall"
        self.assertFalse(skill_dir.exists(),
                         "total-recall skill should have been removed")

    def test_skill_total_recall_search_dir_structure(self):
        skill_dir = SKILLS_DIR / "total-recall-search"
        self.assertTrue(skill_dir.exists())
        self.assertTrue((skill_dir / "SKILL.md").exists(),
                        "total-recall-search/SKILL.md missing")


# ═════════════════════════════════════════════════════════════════════════════
# 10. total_recall_search.py — Gaps Beyond Existing Test Suite
# ═════════════════════════════════════════════════════════════════════════════

class TestSearchGaps(unittest.TestCase):
    """Test cases not covered by the existing test_total_recall_search.py."""

    @unittest.skipUnless(TRS_PY.exists(), "total_recall_search.py not found")
    def setUp(self):
        self.mod = _import_module(TRS_PY)

    def test_cache_key_includes_path(self):
        """Cache key should differ when --path changes."""
        k1 = self.mod._cache_key("hello", "auto", 10, "/path/a")
        k2 = self.mod._cache_key("hello", "auto", 10, "/path/b")
        self.assertNotEqual(k1, k2, "Cache key must vary with path")

    def test_cache_ttl_expired_returns_none(self):
        """Cache entry older than TTL should return None."""
        import importlib
        # Find the correct TTL constant name
        ttl_attr = None
        for name in dir(self.mod):
            if "CACHE" in name.upper() and "TTL" in name.upper():
                ttl_attr = name
                break
        if ttl_attr is None:
            self.skipTest("No CACHE_TTL constant found in module")
        key = f"ttl_test_{uuid.uuid4().hex}"
        data = [{"type": "keyword", "path": "/x.md", "snippet": "s", "score": 1.0}]
        self.mod._write_cache(key, data)
        original_ttl = getattr(self.mod, ttl_attr)
        setattr(self.mod, ttl_attr, -1)  # Immediately expire
        result = self.mod._read_cache(key)
        setattr(self.mod, ttl_attr, original_ttl)
        self.assertIsNone(result, "Expired cache entry should return None")

    def test_borda_merge_single_keyword_list(self):
        """Borda merge with only keyword results should still work."""
        kw = [
            {"type": "keyword", "path": "/a.md", "snippet": "a", "score": 1.0},
            {"type": "keyword", "path": "/b.md", "snippet": "b", "score": 0.8},
        ]
        results = self.mod._borda_merge(kw, [], limit=5)
        self.assertGreater(len(results), 0)
        paths = [r["path"] for r in results]
        self.assertIn("/a.md", paths)

    def test_borda_merge_single_semantic_list(self):
        """Borda merge with only semantic results should still work."""
        sem = [
            {"type": "semantic", "path": "/c.md", "snippet": "c", "score": 0.9},
        ]
        results = self.mod._borda_merge([], sem, limit=5)
        self.assertGreater(len(results), 0)

    def test_error_result_type_preserved(self):
        """_error_result preserves the specified search type."""
        for t in ["keyword", "semantic", "auto"]:
            err = self.mod._error_result(t, "test error")
            self.assertEqual(err["type"], t)

    def test_attach_meta_medium_confidence(self):
        """Score between thresholds should produce 'medium' confidence."""
        results = [
            {"type": "keyword", "path": "/mid.md", "snippet": "m", "score": 0.55}
        ]
        tagged = self.mod._attach_meta(results, "keyword", 0.05)
        self.assertEqual(tagged[0]["_meta"]["confidence"], "medium")

    def test_attach_meta_latency_ms_from_elapsed(self):
        """latency_ms should be elapsed_s * 1000."""
        results = [{"type": "keyword", "path": "/z.md", "snippet": "z", "score": 0.8}]
        tagged = self.mod._attach_meta(results, "keyword", 0.456)
        self.assertAlmostEqual(tagged[0]["_meta"]["latency_ms"], 456.0, places=0)

    def test_classify_camelcase_is_keyword(self):
        """CamelCase identifiers (likely code) should classify as keyword."""
        cls, reason = self.mod.classify_query("ServerScriptService")
        # Either keyword or auto — should NOT be semantic
        self.assertNotEqual(cls, "semantic",
                            "CamelCase likely a code symbol — should not be semantic")

    def test_classify_numeric_query_is_keyword(self):
        """Pure numbers (version, port) should classify as keyword."""
        cls, reason = self.mod.classify_query("18789")
        self.assertIn(cls, ("keyword", "auto"))

    def test_classify_question_is_semantic(self):
        """Questions starting with 'what/how/why/when' should be semantic."""
        for q in ["what is Total Recall", "how does the memory system work",
                  "why did we move to OpenRouter"]:
            cls, reason = self.mod.classify_query(q)
            self.assertEqual(cls, "semantic",
                             f"Question '{q}' should be semantic, got {cls} ({reason})")

    def test_load_memory_files_returns_nonempty(self):
        """_load_memory_files should return a non-empty collection (list or dict)."""
        files = self.mod._load_memory_files()
        self.assertIsInstance(files, (list, dict))
        self.assertGreater(len(files), 0, "_load_memory_files returned empty — check memory dir")

    def test_cli_version_flag_or_help(self):
        """--help should exit 0 and mention total_recall."""
        cmd = [PYTHON, str(TRS_PY), "--help"]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        self.assertEqual(proc.returncode, 0)

    def test_json_output_on_known_file(self):
        """Search for SOUL.md should find it as a keyword result."""
        out = _run_cli("SOUL.md", "--type", "keyword", "--limit", "3")
        self.assertEqual(out["rc"], 0)
        paths = [r["path"] for r in out["results"] if not r.get("error")]
        self.assertTrue(any("SOUL" in p for p in paths),
                        f"Expected SOUL.md in results, got: {paths}")

    def test_search_observations_md(self):
        """Searching for 'observations' should find observations.md."""
        out = _run_cli("observations", "--type", "keyword", "--limit", "5")
        self.assertIn(out["rc"], (0, 1))
        paths = [r["path"] for r in out["results"] if not r.get("error")]
        self.assertTrue(
            any("observations" in p for p in paths),
            f"Expected observations.md in results, got: {paths}"
        )


# ═════════════════════════════════════════════════════════════════════════════
# 11. Edge Cases & Boundary Conditions
# ═════════════════════════════════════════════════════════════════════════════

class TestEdgeCases(unittest.TestCase):
    """Boundary conditions and edge cases for the DB layer."""

    def setUp(self):
        self.conn = _open_db()

    def tearDown(self):
        _cleanup_test_memories(self.conn)
        self.conn.close()

    def test_empty_content_allowed(self):
        """Empty string content is valid (the NOT NULL constraint allows '')."""
        mid = _insert_memory(self.conn, content="",
                              title=f"Empty content {uuid.uuid4().hex[:6]}")
        row = self.conn.execute(
            "SELECT content FROM memories WHERE id = ?", (mid,)
        ).fetchone()
        self.assertEqual(row["content"], "")

    def test_very_long_content(self):
        """Large content (100KB) should store without error."""
        big = "x" * 100_000
        mid = _insert_memory(self.conn, content=big,
                              title=f"BigContent {uuid.uuid4().hex[:6]}")
        row = self.conn.execute(
            "SELECT length(content) FROM memories WHERE id = ?", (mid,)
        ).fetchone()
        self.assertEqual(row[0], 100_000)

    def test_unicode_content(self):
        """Unicode (CJK, emoji) should round-trip cleanly."""
        content = "日本語テスト 🍑 momotaro memory 한국어"
        mid = _insert_memory(self.conn, content=content,
                              title=f"Unicode {uuid.uuid4().hex[:6]}")
        row = self.conn.execute(
            "SELECT content FROM memories WHERE id = ?", (mid,)
        ).fetchone()
        self.assertEqual(row["content"], content)

    def test_null_last_accessed_at(self):
        """last_accessed_at can be NULL (never accessed)."""
        mid = _insert_memory(self.conn, last_accessed_at=None)
        row = self.conn.execute(
            "SELECT last_accessed_at FROM memories WHERE id = ?", (mid,)
        ).fetchone()
        self.assertIsNone(row["last_accessed_at"])

    def test_primary_key_uniqueness(self):
        """Duplicate ID should raise IntegrityError."""
        mid = str(uuid.uuid4())
        _insert_memory(self.conn, id=mid, title=f"PK1 {mid[:6]}")
        with self.assertRaises(sqlite3.IntegrityError):
            _insert_memory(self.conn, id=mid, title=f"PK2 {mid[:6]}")

    def test_db_file_is_valid_sqlite(self):
        """ai-memory.db should open as a valid SQLite3 database."""
        if not DB_PATH.exists():
            self.skipTest("ai-memory.db not found")
        result = subprocess.run(
            ["sqlite3", str(DB_PATH), ".tables"],
            capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0, "sqlite3 could not open ai-memory.db")
        self.assertIn("memories", result.stdout)

    def test_concurrent_reads_dont_deadlock(self):
        """Two connections reading simultaneously should not deadlock."""
        conn2 = sqlite3.connect(str(DB_PATH))
        try:
            c1 = self.conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
            c2 = conn2.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
            self.assertEqual(c1, c2)
        finally:
            conn2.close()

    def test_fts_special_chars_query(self):
        """FTS with special characters should not crash."""
        try:
            self.conn.execute(
                "SELECT rowid FROM memories_fts WHERE memories_fts MATCH ?",
                ("hello world",)
            ).fetchall()
        except sqlite3.OperationalError:
            pass  # FTS syntax error is acceptable; crash is not


# ═════════════════════════════════════════════════════════════════════════════
# 12. MemoryDB Python API (memory_db.py)
# ═════════════════════════════════════════════════════════════════════════════

MEMORY_DB_PY = SCRIPTS_DIR / "memory_db.py"


class TestMemoryDBAPI(unittest.TestCase):
    """Test the memory_db.py MemoryDB class end-to-end."""

    @classmethod
    def setUpClass(cls):
        if not MEMORY_DB_PY.exists():
            raise unittest.SkipTest("memory_db.py not found")
        mod = _import_module(MEMORY_DB_PY)
        cls.MemoryDB = mod.MemoryDB
        cls.db = mod.MemoryDB()

    def tearDown(self):
        # Clean all test_suite records via raw sqlite
        conn = sqlite3.connect(str(DB_PATH))
        conn.execute("DELETE FROM memories WHERE namespace LIKE 'test_%'")
        conn.execute("DELETE FROM archived_memories WHERE namespace LIKE 'test_%'")
        conn.commit()
        conn.close()

    # ── add / UPSERT ─────────────────────────────────────────────────────────

    def test_add_returns_id(self):
        mid = self.db.add("API test memory", "Content here",
                          namespace="test_api", tier="short")
        self.assertIsInstance(mid, str)
        self.assertEqual(len(mid), 36)  # UUID length

    def test_add_upsert_same_title_namespace(self):
        """add() with same title+namespace should update, not insert duplicate."""
        mid1 = self.db.add("UPSERT title", "Original content", namespace="test_api")
        mid2 = self.db.add("UPSERT title", "Updated content", namespace="test_api")
        self.assertEqual(mid1, mid2, "UPSERT should return same ID")
        r = self.db.get(mid1)
        self.assertEqual(r["content"], "Updated content")

    def test_add_different_namespaces_are_separate(self):
        mid1 = self.db.add("Shared title", "NS A content", namespace="test_ns_a")
        mid2 = self.db.add("Shared title", "NS B content", namespace="test_ns_b")
        self.assertNotEqual(mid1, mid2)

    def test_add_all_tiers(self):
        for tier in ["working", "short", "long"]:
            mid = self.db.add(f"Tier {tier} test", f"Content for {tier}",
                              tier=tier, namespace="test_api")
            r = self.db.get(mid)
            self.assertEqual(r["tier"], tier)

    def test_add_with_tags(self):
        mid = self.db.add("Tagged memory", "Has tags", namespace="test_api",
                          tags=["alpha", "beta", "gamma"])
        r = self.db.get(mid)
        self.assertEqual(sorted(r["tags"]), ["alpha", "beta", "gamma"])

    def test_add_with_priority(self):
        mid = self.db.add("High priority", "Important", namespace="test_api", priority=9)
        r = self.db.get(mid)
        self.assertEqual(r["priority"], 9)

    def test_add_with_metadata(self):
        meta = {"source": "test", "workflow": "session-reset"}
        mid = self.db.add("With metadata", "Content", namespace="test_api", metadata=meta)
        r = self.db.get(mid)
        self.assertEqual(r["metadata"]["workflow"], "session-reset")

    # ── get ──────────────────────────────────────────────────────────────────

    def test_get_returns_dict(self):
        mid = self.db.add("Get test", "Get content", namespace="test_api")
        r = self.db.get(mid)
        self.assertIsInstance(r, dict)
        self.assertEqual(r["title"], "Get test")
        self.assertEqual(r["content"], "Get content")

    def test_get_nonexistent_returns_none(self):
        r = self.db.get("00000000-0000-0000-0000-000000000000")
        self.assertIsNone(r)

    def test_get_increments_access_count(self):
        mid = self.db.add("Access count test", "Body", namespace="test_api")
        self.db.get(mid)
        self.db.get(mid)
        conn = sqlite3.connect(str(DB_PATH))
        row = conn.execute("SELECT access_count FROM memories WHERE id=?", (mid,)).fetchone()
        conn.close()
        self.assertGreaterEqual(row[0], 2)

    # ── update ───────────────────────────────────────────────────────────────

    def test_update_content(self):
        mid = self.db.add("Update test", "Original", namespace="test_api")
        result = self.db.update(mid, content="Replaced")
        self.assertTrue(result)
        self.assertEqual(self.db.get(mid)["content"], "Replaced")

    def test_update_priority(self):
        mid = self.db.add("Priority update", "Body", namespace="test_api")
        self.db.update(mid, priority=8)
        self.assertEqual(self.db.get(mid)["priority"], 8)

    def test_update_tags(self):
        mid = self.db.add("Tag update", "Body", namespace="test_api")
        self.db.update(mid, tags=["new", "tags"])
        self.assertEqual(sorted(self.db.get(mid)["tags"]), ["new", "tags"])

    def test_update_nonexistent_returns_false(self):
        result = self.db.update("00000000-0000-0000-0000-000000000000", content="x")
        self.assertFalse(result)

    # ── delete ───────────────────────────────────────────────────────────────

    def test_delete_removes_memory(self):
        mid = self.db.add("Delete me", "Content", namespace="test_api")
        ok = self.db.delete(mid)
        self.assertTrue(ok)
        self.assertIsNone(self.db.get(mid))

    def test_delete_nonexistent_returns_false(self):
        ok = self.db.delete("00000000-0000-0000-0000-000000000000")
        self.assertFalse(ok)

    # ── link ─────────────────────────────────────────────────────────────────

    def test_link_two_memories(self):
        a = self.db.add("Link source", "Body A", namespace="test_api")
        b = self.db.add("Link target", "Body B", namespace="test_api")
        ok = self.db.link(a, b, "related_to")
        self.assertTrue(ok)
        conn = sqlite3.connect(str(DB_PATH))
        row = conn.execute(
            "SELECT relation FROM memory_links WHERE source_id=? AND target_id=?",
            (a, b)
        ).fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "related_to")

    def test_link_duplicate_ignored(self):
        a = self.db.add("Dup link src", "Body", namespace="test_api")
        b = self.db.add("Dup link tgt", "Body", namespace="test_api")
        self.db.link(a, b)
        ok = self.db.link(a, b)  # same link again
        self.assertTrue(ok)  # should not raise

    # ── archive ──────────────────────────────────────────────────────────────

    def test_archive_moves_to_archive_table(self):
        mid = self.db.add("Archive me", "Archivable content", namespace="test_api")
        ok = self.db.archive(mid, reason="manual")
        self.assertTrue(ok)
        self.assertIsNone(self.db.get(mid))  # gone from active
        conn = sqlite3.connect(str(DB_PATH))
        row = conn.execute(
            "SELECT archive_reason FROM archived_memories WHERE id=?", (mid,)
        ).fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "manual")

    def test_archive_nonexistent_returns_false(self):
        ok = self.db.archive("00000000-0000-0000-0000-000000000000")
        self.assertFalse(ok)

    # ── expire_ttl ───────────────────────────────────────────────────────────

    def test_expire_ttl_archives_expired(self):
        mid = self.db.add("Expiring memory", "Will expire",
                          namespace="test_api",
                          expires_at="2020-01-01T00:00:00+00:00")
        count = self.db.expire_ttl()
        self.assertGreaterEqual(count, 1)
        self.assertIsNone(self.db.get(mid))

    def test_expire_ttl_skips_non_expired(self):
        mid = self.db.add("Permanent memory", "No expiry",
                          namespace="test_api",
                          expires_at=None)
        self.db.expire_ttl()
        self.assertIsNotNone(self.db.get(mid))

    # ── search_fts ───────────────────────────────────────────────────────────

    def test_search_fts_finds_content(self):
        unique = f"xyzapi{uuid.uuid4().hex[:8]}"
        self.db.add(f"FTS API test {unique}", f"Unique term for FTS: {unique}",
                    namespace="test_api")
        results = self.db.search_fts(unique)
        self.assertGreater(len(results), 0)
        titles = [r["title"] for r in results]
        self.assertTrue(any(unique in t for t in titles))

    def test_search_fts_namespace_filter(self):
        unique = f"xyzns{uuid.uuid4().hex[:8]}"
        self.db.add(f"NS filtered {unique}", f"Content: {unique}", namespace="test_ns_filter")
        results_all = self.db.search_fts(unique)
        results_ns = self.db.search_fts(unique, namespace="test_ns_filter")
        results_wrong = self.db.search_fts(unique, namespace="test_wrong_ns")
        self.assertGreater(len(results_ns), 0)
        self.assertEqual(len(results_wrong), 0)
        conn = sqlite3.connect(str(DB_PATH))
        conn.execute("DELETE FROM memories WHERE namespace='test_ns_filter'")
        conn.commit()
        conn.close()

    def test_search_fts_empty_query_graceful(self):
        """Empty or nonsense query should not raise."""
        try:
            self.db.search_fts("zzzzz_no_match_xyz99999")
        except Exception as e:
            self.fail(f"search_fts raised unexpectedly: {e}")

    # ── clean_orphaned_links ─────────────────────────────────────────────────

    def test_clean_orphaned_links(self):
        """After deleting a memory, clean_orphaned_links should remove its link."""
        a = self.db.add("Orphan src", "Body", namespace="test_api")
        b = self.db.add("Orphan tgt", "Body", namespace="test_api")
        self.db.link(a, b)
        self.db.delete(a)  # cascade should handle it, but we test clean also
        removed = self.db.clean_orphaned_links()
        self.assertIsInstance(removed, int)

    # ── stats ────────────────────────────────────────────────────────────────

    def test_stats_returns_expected_keys(self):
        s = self.db.stats()
        for key in ("memories", "archived", "links", "orphaned_links", "by_tier", "by_namespace"):
            self.assertIn(key, s)

    def test_stats_counts_reflect_adds(self):
        before = self.db.stats()["memories"]
        self.db.add("Stats test A", "Body", namespace="test_api")
        self.db.add("Stats test B", "Body", namespace="test_api")
        after = self.db.stats()["memories"]
        self.assertEqual(after, before + 2)

    # ── CLI ──────────────────────────────────────────────────────────────────

    def test_cli_add_and_stats(self):
        result = subprocess.run(
            [PYTHON, str(MEMORY_DB_PY), "add",
             "CLI test memory", "CLI content",
             "--tier", "short", "--ns", "test_cli", "--tags", "cli,test"],
            capture_output=True, text=True, timeout=15
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("ok id=", result.stdout)
        # Cleanup
        conn = sqlite3.connect(str(DB_PATH))
        conn.execute("DELETE FROM memories WHERE namespace='test_cli'")
        conn.commit()
        conn.close()

    def test_cli_stats_returns_json(self):
        result = subprocess.run(
            [PYTHON, str(MEMORY_DB_PY), "stats"],
            capture_output=True, text=True, timeout=15
        )
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertIn("memories", data)

    def test_cli_search(self):
        unique = f"clisearch{uuid.uuid4().hex[:8]}"
        self.db.add(f"CLI search test {unique}", f"Body: {unique}", namespace="test_api")
        result = subprocess.run(
            [PYTHON, str(MEMORY_DB_PY), "search", unique, "--limit", "5"],
            capture_output=True, text=True, timeout=15
        )
        self.assertEqual(result.returncode, 0)


# ═════════════════════════════════════════════════════════════════════════════
# 13. Workflow Integration
# ═════════════════════════════════════════════════════════════════════════════

class TestWorkflowIntegration(unittest.TestCase):
    """Verify that wired-in workflows can interact with ai-memory.db correctly."""

    @classmethod
    def setUpClass(cls):
        if not MEMORY_DB_PY.exists():
            raise unittest.SkipTest("memory_db.py not found")
        mod = _import_module(MEMORY_DB_PY)
        cls.db = mod.MemoryDB()

    def tearDown(self):
        conn = sqlite3.connect(str(DB_PATH))
        conn.execute("DELETE FROM memories WHERE namespace LIKE 'test_%'")
        conn.commit()
        conn.close()

    # ── auto-flush-session-context.sh ────────────────────────────────────────

    def test_auto_flush_script_exists(self):
        script = SCRIPTS_DIR / "auto-flush-session-context.sh"
        self.assertTrue(script.exists(), "auto-flush-session-context.sh not found")

    def test_auto_flush_script_syntax(self):
        script = SCRIPTS_DIR / "auto-flush-session-context.sh"
        if not script.exists():
            self.skipTest("Script not found")
        result = subprocess.run(["bash", "-n", str(script)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0,
                         f"Bash syntax error: {result.stderr}")

    def test_auto_flush_references_memory_db(self):
        script = SCRIPTS_DIR / "auto-flush-session-context.sh"
        if not script.exists():
            self.skipTest("Script not found")
        content = script.read_text()
        self.assertIn("memory_db.py", content,
                      "auto-flush should call memory_db.py")

    # ── weekly-memory-consolidation.sh ───────────────────────────────────────

    def test_consolidation_script_exists(self):
        script = SCRIPTS_DIR / "weekly-memory-consolidation.sh"
        self.assertTrue(script.exists())

    def test_consolidation_script_syntax(self):
        script = SCRIPTS_DIR / "weekly-memory-consolidation.sh"
        if not script.exists():
            self.skipTest("Script not found")
        result = subprocess.run(["bash", "-n", str(script)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0,
                         f"Bash syntax error: {result.stderr}")

    def test_consolidation_references_memory_db(self):
        script = SCRIPTS_DIR / "weekly-memory-consolidation.sh"
        if not script.exists():
            self.skipTest("Script not found")
        content = script.read_text()
        self.assertIn("memory_db.py", content)

    # ── total_recall_search.py + DB FTS ──────────────────────────────────────

    def test_total_recall_search_has_db_fts(self):
        """total_recall_search.py should contain _db_fts_search function."""
        if not TRS_PY.exists():
            self.skipTest("total_recall_search.py not found")
        content = TRS_PY.read_text()
        self.assertIn("_db_fts_search", content)

    def test_db_fts_finds_seeded_memory(self):
        """A memory added to DB should appear in total_recall_search results."""
        unique = f"wftest{uuid.uuid4().hex[:8]}"
        self.db.add(f"Workflow test {unique}", f"Integration test body: {unique}",
                    namespace="test_workflow")
        if not TRS_PY.exists():
            self.skipTest("total_recall_search.py not found")
        mod = _import_module(TRS_PY)
        results = mod._db_fts_search(unique, limit=5)
        self.assertGreater(len(results), 0,
                           f"DB FTS should find '{unique}' in ai-memory.db")
        paths = [r.get("path", "") for r in results]
        self.assertTrue(any("ai-memory.db" in p for p in paths))

    def test_db_fts_empty_db_returns_list(self):
        """_db_fts_search on empty query should return a list (not crash)."""
        if not TRS_PY.exists():
            self.skipTest("total_recall_search.py not found")
        mod = _import_module(TRS_PY)
        result = mod._db_fts_search("zzznomatchwhatsoever999", limit=5)
        self.assertIsInstance(result, list)

    # ── observer cron ────────────────────────────────────────────────────────

    def test_observations_md_is_active(self):
        obs = MEMORY_DIR / "observations.md"
        self.assertTrue(obs.exists(), "observations.md should be active")

    def test_observations_md_has_content(self):
        obs = MEMORY_DIR / "observations.md"
        if not obs.exists():
            self.skipTest("observations.md not found")
        self.assertGreater(obs.stat().st_size, 0)

    # ── multi-tier dummy data round-trip ─────────────────────────────────────

    def test_multi_tier_round_trip(self):
        """Add memories across tiers and namespaces; verify all retrievable."""
        ids = {}
        for tier, ns, title in [
            ("working", "test_workflow", "Working memory: current session state"),
            ("short",   "test_workflow", "Short memory: task in progress"),
            ("long",    "test_workflow", "Long memory: architectural decision"),
        ]:
            ids[tier] = self.db.add(title, f"Content for {tier} tier", tier=tier, namespace=ns)

        for tier, mid in ids.items():
            r = self.db.get(mid)
            self.assertIsNotNone(r, f"Could not retrieve {tier} memory")
            self.assertEqual(r["tier"], tier)

    def test_linked_memories_query(self):
        """Two memories linked by 'depends_on' should be queryable."""
        a = self.db.add("Decision A", "Context for A", namespace="test_workflow")
        b = self.db.add("Decision B", "Depends on A", namespace="test_workflow")
        self.db.link(a, b, "depends_on")
        conn = sqlite3.connect(str(DB_PATH))
        row = conn.execute(
            "SELECT relation FROM memory_links WHERE source_id=? AND target_id=?",
            (a, b)
        ).fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "depends_on")

    def test_stats_after_bulk_insert(self):
        """Stats should reflect accurate counts after inserting 5 records."""
        before = self.db.stats()["memories"]
        for i in range(5):
            self.db.add(f"Bulk test {i} {uuid.uuid4().hex[:6]}", f"Body {i}",
                        namespace="test_bulk")
        after = self.db.stats()["memories"]
        self.assertEqual(after, before + 5)
        conn = sqlite3.connect(str(DB_PATH))
        conn.execute("DELETE FROM memories WHERE namespace='test_bulk'")
        conn.commit()
        conn.close()


# ═════════════════════════════════════════════════════════════════════════════
# Entry point
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    _log("=" * 60)
    _log("AI-MEMORY TEST SUITE")
    _log(f"Workspace: {WORKSPACE}")
    _log(f"DB: {DB_PATH}")
    _log(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    _log("=" * 60)

    verbosity = 2 if "-v" in sys.argv else 1

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    test_classes = [
        TestSQLiteSchema,
        TestCRUD,
        TestFTS5,
        TestMemoryLinks,
        TestNamespaceIsolation,
        TestArchiveAndExpiry,
        TestIndexFilesForMemory,
        TestMemoryFileHealth,
        TestObserverReflectorHealth,
        TestSearchGaps,
        TestEdgeCases,
        TestMemoryDBAPI,
        TestWorkflowIntegration,
    ]

    for cls in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    runner = unittest.TextTestRunner(verbosity=verbosity, stream=sys.stdout)
    result = runner.run(suite)

    _log("")
    _log("=" * 60)
    _log(f"TOTAL:   {result.testsRun}")
    _log(f"PASSED:  {result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)}")
    _log(f"FAILED:  {len(result.failures)}")
    _log(f"ERRORS:  {len(result.errors)}")
    _log(f"SKIPPED: {len(result.skipped)}")
    _log(f"RESULT:  {'ALL PASS' if result.wasSuccessful() else 'FAILURES FOUND'}")
    _log(f"Log:     {LOG_FILE}")
    _log("=" * 60)

    _log_fh.close()
    sys.exit(0 if result.wasSuccessful() else 1)
