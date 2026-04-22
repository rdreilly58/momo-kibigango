#!/usr/bin/env python3
"""
test_elite_memory_v2.py — Test suite for Elite Long-Term Memory v2 (tiered system).

Tests: HotCache, LanceWarmStore, ColdStore, TierManager.
Run:   python3 Tests/test_elite_memory_v2.py
       python3 -m pytest Tests/test_elite_memory_v2.py -v
"""

from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# ── path setup ────────────────────────────────────────────────────────────────
_WORKSPACE = Path(__file__).parent.parent
_SCRIPTS = _WORKSPACE / "scripts"
sys.path.insert(0, str(_SCRIPTS))


# ═══════════════════════════════════════════════════════════════════════════════
# 1. HOT CACHE TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestHotCache(unittest.TestCase):

    def setUp(self):
        from memory_hot_cache import HotCache
        self.cache = HotCache(max_size=3, ttl_seconds=60)

    def test_put_and_get(self):
        """Basic put/get round-trip."""
        self.cache.put({"id": "a1", "title": "Alpha"})
        result = self.cache.get("a1")
        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "Alpha")

    def test_miss_returns_none(self):
        """Getting a non-existent key returns None."""
        self.assertIsNone(self.cache.get("nonexistent"))

    def test_lru_eviction(self):
        """When cache fills beyond max_size, oldest entry is evicted."""
        for i in range(4):
            self.cache.put({"id": str(i), "title": f"Mem {i}"})
        # id=0 was inserted first and never re-accessed — should be evicted
        self.assertIsNone(self.cache.get("0"))
        # ids 1, 2, 3 should still be present
        self.assertIsNotNone(self.cache.get("1"))
        self.assertIsNotNone(self.cache.get("3"))

    def test_ttl_expiry(self):
        """Entries expire after TTL seconds."""
        cache = __import__("memory_hot_cache").HotCache(max_size=10, ttl_seconds=0.05)
        cache.put({"id": "x", "title": "Ephemeral"})
        self.assertIsNotNone(cache.get("x"))
        time.sleep(0.1)
        self.assertIsNone(cache.get("x"))

    def test_invalidate(self):
        """invalidate() removes a specific entry."""
        self.cache.put({"id": "b2", "title": "Beta"})
        self.cache.invalidate("b2")
        self.assertIsNone(self.cache.get("b2"))

    def test_stats_hit_rate(self):
        """stats() correctly tracks hits and misses."""
        self.cache.put({"id": "c3", "title": "Gamma"})
        self.cache.get("c3")   # hit
        self.cache.get("miss") # miss
        s = self.cache.stats()
        self.assertEqual(s["hits"], 1)
        self.assertEqual(s["misses"], 1)
        self.assertAlmostEqual(s["hit_rate"], 0.5, places=2)

    def test_lru_access_refreshes_order(self):
        """Accessing an entry refreshes its LRU position, preventing premature eviction."""
        for i in range(3):
            self.cache.put({"id": str(i), "title": f"Mem {i}"})
        # Access id=0 to refresh it
        self.cache.get("0")
        # Insert a 4th entry — id=1 (second oldest) should be evicted, not id=0
        self.cache.put({"id": "3", "title": "Mem 3"})
        self.assertIsNotNone(self.cache.get("0"), "id=0 should survive (refreshed)")
        self.assertIsNone(self.cache.get("1"), "id=1 should be evicted (oldest unused)")

    def test_clear(self):
        """clear() flushes all entries."""
        self.cache.put({"id": "z", "title": "Zeta"})
        self.cache.clear()
        self.assertIsNone(self.cache.get("z"))
        self.assertEqual(self.cache.stats()["size"], 0)


# ═══════════════════════════════════════════════════════════════════════════════
# 2. LANCE WARM STORE TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestLanceWarmStore(unittest.TestCase):

    def _make_model(self):
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)

    def _make_store(self, tmpdir):
        from memory_lance_store import LanceWarmStore
        return LanceWarmStore(db_path=Path(tmpdir) / "lance")

    def test_upsert_and_search(self):
        """Upsert a memory then retrieve it via vector search."""
        model = self._make_model()
        with tempfile.TemporaryDirectory() as tmpdir:
            store = self._make_store(tmpdir)
            emb = model.encode("LanceDB vector store integration test")
            store.upsert({
                "id": 42, "title": "VectorTest", "content": "LanceDB vector store integration test",
                "namespace": "workspace", "priority": 7, "tier": "warm",
                "access_count": 0, "last_accessed_at": "", "tags": "[]",
            }, emb)
            results = store.search("vector store test", model, k=5)
            self.assertTrue(len(results) > 0, "Should return at least one result")
            self.assertEqual(results[0]["title"], "VectorTest")
            self.assertIn("_score", results[0])
            self.assertGreater(results[0]["_score"], 0.5)

    def test_upsert_updates_existing(self):
        """Upserting with the same id updates the record."""
        model = self._make_model()
        with tempfile.TemporaryDirectory() as tmpdir:
            store = self._make_store(tmpdir)
            emb1 = model.encode("Original content")
            store.upsert({"id": 1, "title": "Original", "content": "Original content",
                          "namespace": "workspace", "priority": 5, "tier": "warm",
                          "access_count": 0, "last_accessed_at": "", "tags": "[]"}, emb1)
            emb2 = model.encode("Updated content")
            store.upsert({"id": 1, "title": "Updated", "content": "Updated content",
                          "namespace": "workspace", "priority": 5, "tier": "warm",
                          "access_count": 1, "last_accessed_at": "", "tags": "[]"}, emb2)
            self.assertEqual(store.count(), 1)
            results = store.search("Updated", model, k=5)
            self.assertEqual(results[0]["title"], "Updated")

    def test_delete(self):
        """Deleting a record removes it from the store."""
        model = self._make_model()
        with tempfile.TemporaryDirectory() as tmpdir:
            store = self._make_store(tmpdir)
            emb = model.encode("Temporary memory")
            store.upsert({"id": 99, "title": "ToDelete", "content": "Temporary memory",
                          "namespace": "workspace", "priority": 5, "tier": "warm",
                          "access_count": 0, "last_accessed_at": "", "tags": "[]"}, emb)
            self.assertEqual(store.count(), 1)
            store.delete(99)
            self.assertEqual(store.count(), 0)

    def test_hybrid_rrf_combines_scores(self):
        """Hybrid search should fuse vector + FTS5 results using RRF."""
        model = self._make_model()
        with tempfile.TemporaryDirectory() as tmpdir:
            store = self._make_store(tmpdir)
            # Insert two memories
            for i, (title, content) in enumerate([
                ("CascadeProxy", "cascade proxy configuration nginx"),
                ("UnrelatedTopic", "breakfast cereal oat milk"),
            ]):
                emb = model.encode(content)
                store.upsert({"id": i + 1, "title": title, "content": content,
                              "namespace": "workspace", "priority": 5, "tier": "warm",
                              "access_count": 0, "last_accessed_at": "", "tags": "[]"}, emb)

            fts_results = [{"id": 1, "title": "CascadeProxy", "priority": 5}]
            results = store.hybrid_search("cascade proxy", fts_results, model, k=5)
            self.assertTrue(len(results) > 0)
            # CascadeProxy should rank first (present in both vector and FTS5)
            self.assertEqual(results[0]["title"], "CascadeProxy")

    def test_sync_from_sqlite(self):
        """sync_from_sqlite reads from a real SQLite DB and upserts to LanceDB."""
        model = self._make_model()
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a minimal SQLite DB
            db_file = Path(tmpdir) / "test.db"
            con = sqlite3.connect(str(db_file))
            con.execute("""CREATE TABLE memories (
                id TEXT PRIMARY KEY, tier TEXT, namespace TEXT,
                title TEXT, content TEXT, tags TEXT, priority REAL,
                confidence REAL, source TEXT, access_count INTEGER,
                created_at TEXT, updated_at TEXT, last_accessed_at TEXT,
                expires_at TEXT, metadata TEXT, embedding BLOB
            )""")
            con.execute("""INSERT INTO memories VALUES (
                'uuid-1','short','workspace','SyncTest','Content for sync test',
                '[]',5,1.0,'test',0,'2026-01-01','2026-01-01',NULL,NULL,'{}',NULL
            )""")
            con.commit()
            con.close()

            store = self._make_store(tmpdir)
            count = store.sync_from_sqlite(db_file, model)
            self.assertEqual(count, 1)
            self.assertEqual(store.count(), 1)
            results = store.search("sync test content", model, k=5)
            self.assertTrue(len(results) > 0)


# ═══════════════════════════════════════════════════════════════════════════════
# 3. COLD STORE TESTS
# ═══════════════════════════════════════════════════════════════════════════════

def _make_test_db(tmpdir: str) -> Path:
    """Create a minimal SQLite test database with both tables."""
    db_file = Path(tmpdir) / "test_memory.db"
    con = sqlite3.connect(str(db_file))
    con.execute("PRAGMA foreign_keys=ON")
    con.execute("""CREATE TABLE memories (
        id TEXT PRIMARY KEY, tier TEXT, namespace TEXT,
        title TEXT, content TEXT, tags TEXT, priority REAL,
        confidence REAL, source TEXT, access_count INTEGER DEFAULT 0,
        created_at TEXT, updated_at TEXT, last_accessed_at TEXT,
        expires_at TEXT, metadata TEXT DEFAULT '{}', embedding BLOB
    )""")
    con.execute("""CREATE TABLE archived_memories (
        id TEXT PRIMARY KEY, tier TEXT, namespace TEXT,
        title TEXT, content TEXT, tags TEXT, priority REAL,
        confidence REAL, source TEXT, access_count INTEGER DEFAULT 0,
        created_at TEXT, updated_at TEXT, last_accessed_at TEXT,
        expires_at TEXT, metadata TEXT DEFAULT '{}', archived_at TEXT,
        archive_reason TEXT
    )""")
    con.execute("""CREATE TABLE memory_links (
        source_id TEXT, target_id TEXT, relation TEXT, created_at TEXT,
        PRIMARY KEY (source_id, target_id, relation),
        FOREIGN KEY (source_id) REFERENCES memories(id) ON DELETE CASCADE,
        FOREIGN KEY (target_id) REFERENCES memories(id) ON DELETE CASCADE
    )""")
    con.execute("""CREATE VIRTUAL TABLE memories_fts USING fts5(
        title, content, tags, content=memories, content_rowid=rowid
    )""")
    # Minimal triggers for FTS5 sync
    con.execute("""CREATE TRIGGER memories_ai AFTER INSERT ON memories BEGIN
        INSERT INTO memories_fts(rowid, title, content, tags)
        VALUES (new.rowid, new.title, new.content, new.tags);
    END""")
    con.commit()
    con.close()
    return db_file


class TestColdStore(unittest.TestCase):

    def setUp(self):
        from memory_cold_store import ColdStore
        self._tmpdir_obj = tempfile.TemporaryDirectory()
        self.tmpdir = self._tmpdir_obj.name
        self.db_file = _make_test_db(self.tmpdir)
        self.store = ColdStore(db_path=self.db_file)

    def tearDown(self):
        self._tmpdir_obj.cleanup()

    def test_count_empty(self):
        """Cold store count starts at 0 on empty archive."""
        self.assertEqual(self.store.count(), 0)

    def test_demotion_candidates(self):
        """get_demotion_candidates returns stale zero-access memories."""
        con = sqlite3.connect(str(self.db_file))
        con.execute("""INSERT INTO memories VALUES (
            'stale-1','short','workspace','StaleMemory','Never accessed',
            '[]',3,1.0,'test',0,'2025-01-01','2025-01-01',NULL,NULL,'{}',NULL
        )""")
        con.execute("""INSERT INTO memories VALUES (
            'active-1','short','workspace','ActiveMemory','Accessed recently',
            '[]',5,1.0,'test',5,'2026-04-01','2026-04-22','2026-04-22',NULL,'{}',NULL
        )""")
        con.commit()
        con.close()

        candidates = self.store.get_demotion_candidates(
            db_path=self.db_file, days_inactive=90
        )
        self.assertIn("stale-1", candidates)
        self.assertNotIn("active-1", candidates)

    def test_demote_moves_to_archive(self):
        """demote() moves a memory from memories to archived_memories."""
        con = sqlite3.connect(str(self.db_file))
        con.execute("""INSERT INTO memories VALUES (
            'demote-me','short','workspace','DemoteTarget','Will be archived',
            '[]',3,1.0,'test',0,'2025-01-01','2025-01-01',NULL,NULL,'{}',NULL
        )""")
        con.commit()
        con.close()

        mock_lance = MagicMock()
        result = self.store.demote(self.db_file, "demote-me", mock_lance)
        self.assertTrue(result)

        # Verify moved
        con = sqlite3.connect(str(self.db_file))
        in_active = con.execute("SELECT id FROM memories WHERE id='demote-me'").fetchone()
        in_archive = con.execute("SELECT id FROM archived_memories WHERE id='demote-me'").fetchone()
        con.close()
        self.assertIsNone(in_active)
        self.assertIsNotNone(in_archive)

    def test_promote_restores_memory(self):
        """promote() moves archived memory back to active and calls lance upsert."""
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)

        con = sqlite3.connect(str(self.db_file))
        con.execute("""INSERT INTO archived_memories VALUES (
            'promote-me','short','workspace','PromoteTarget','Cold memory to restore',
            '[]',5,1.0,'test',2,'2025-06-01','2025-06-01',NULL,NULL,'{}',
            '2025-07-01','ttl_expired'
        )""")
        con.commit()
        con.close()

        mock_lance = MagicMock()
        result = self.store.promote(self.db_file, "promote-me", mock_lance, model)

        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "PromoteTarget")
        mock_lance.upsert.assert_called_once()

        # Verify removed from archive
        con = sqlite3.connect(str(self.db_file))
        in_archive = con.execute(
            "SELECT id FROM archived_memories WHERE id='promote-me'"
        ).fetchone()
        con.close()
        self.assertIsNone(in_archive)

    def test_search_fts_fallback(self):
        """search_fts falls back to LIKE when no FTS table exists on archive."""
        con = sqlite3.connect(str(self.db_file))
        con.execute("""INSERT INTO archived_memories VALUES (
            'arch-1','long','workspace','ArchivedProxy','proxy configuration for nginx',
            '[]',4,1.0,'test',1,'2025-01-01','2025-01-01',NULL,NULL,'{}',
            '2025-06-01','manual'
        )""")
        con.commit()
        con.close()

        results = self.store.search_fts("proxy", limit=5)
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]["title"], "ArchivedProxy")


# ═══════════════════════════════════════════════════════════════════════════════
# 4. TIER MANAGER TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestTierManager(unittest.TestCase):

    def setUp(self):
        self._tmpdir_obj = tempfile.TemporaryDirectory()
        self.tmpdir = self._tmpdir_obj.name
        self.db_file = _make_test_db(self.tmpdir)
        self.lance_path = Path(self.tmpdir) / "lance"
        self._setup_db_schema()

    def tearDown(self):
        self._tmpdir_obj.cleanup()

    def _setup_db_schema(self):
        """Add schema_version and namespace_meta tables required by MemoryDB."""
        con = sqlite3.connect(str(self.db_file))
        con.execute("CREATE TABLE IF NOT EXISTS schema_version (version INTEGER)")
        con.execute("INSERT OR IGNORE INTO schema_version VALUES (7)")
        con.execute("""CREATE TABLE IF NOT EXISTS namespace_meta (
            namespace TEXT PRIMARY KEY, standard_id TEXT,
            parent_namespace TEXT, updated_at TEXT
        )""")
        con.commit()
        con.close()

    def _make_manager(self):
        from memory_tier_manager import TierManager
        from memory_hot_cache import HotCache
        # Fresh isolated HotCache per test
        hot = HotCache(max_size=10, ttl_seconds=60)
        return TierManager(
            db_path=self.db_file,
            lance_path=self.lance_path,
            hot_cache=hot,
            auto_sync=False,
        )

    def test_store_and_search(self):
        """store() writes to SQLite + LanceDB; search() retrieves the record."""
        mgr = self._make_manager()
        mgr.store("TierManagerTest", "Content for tier manager search test",
                  namespace="workspace", tier="short", priority=7)
        results = mgr.search("tier manager search", k=5)
        self.assertTrue(len(results) > 0)
        titles = [r.get("title") for r in results]
        self.assertIn("TierManagerTest", titles)

    def test_search_returns_score_and_tier(self):
        """All search results must have _score and _tier fields."""
        mgr = self._make_manager()
        mgr.store("ScoreTest", "Importance of scoring in search results")
        results = mgr.search("scoring search results", k=5)
        for r in results:
            self.assertIn("_score", r, "Result missing _score")
            self.assertIn("_tier", r, "Result missing _tier")

    def test_get_hits_hot_cache(self):
        """Second get() call for same id is served from hot cache."""
        mgr = self._make_manager()
        # Insert directly into SQLite to have a known id
        con = sqlite3.connect(str(self.db_file))
        con.execute("""INSERT INTO memories VALUES (
            'hot-test-id','short','workspace','HotCacheTest','Hot cache retrieval test',
            '[]',5,1.0,'test',0,'2026-04-22','2026-04-22',NULL,NULL,'{}',NULL
        )""")
        con.commit()
        con.close()

        # First get — SQLite hit, goes into hot cache
        result1 = mgr.get("hot-test-id")
        self.assertIsNotNone(result1)
        # Second get — should come from hot cache
        result2 = mgr.get("hot-test-id")
        self.assertIsNotNone(result2)
        self.assertEqual(result2["title"], "HotCacheTest")

    def test_delete_removes_from_all_tiers(self):
        """delete() removes from SQLite, LanceDB, and hot cache."""
        mgr = self._make_manager()
        mem_id = mgr.store("DeleteTest", "Memory to be deleted across all tiers")
        # Ensure it's in hot cache
        mgr.get(mem_id)
        result = mgr.delete(mem_id)
        self.assertTrue(result)
        self.assertIsNone(mgr.get(mem_id))

    def test_stats_returns_tier_info(self):
        """stats() returns non-empty tier breakdown."""
        mgr = self._make_manager()
        mgr.store("StatsTest", "Testing the stats method")
        s = mgr.stats()
        self.assertIn("tiers", s)
        self.assertIn("hot", s["tiers"])
        self.assertIn("warm", s["tiers"])
        self.assertIn("cold", s["tiers"])
        self.assertIn("searches_this_session", s)

    def test_rebuild_warm_index(self):
        """rebuild_warm_index() syncs all SQLite memories into LanceDB."""
        con = sqlite3.connect(str(self.db_file))
        for i in range(3):
            con.execute(f"""INSERT INTO memories VALUES (
                'rebuild-{i}','short','workspace','RebuildMem{i}','Rebuild test content {i}',
                '[]',5,1.0,'test',0,'2026-04-22','2026-04-22',NULL,NULL,'{{}}',NULL
            )""")
        con.commit()
        con.close()

        mgr = self._make_manager()
        count = mgr.rebuild_warm_index()
        self.assertEqual(count, 3)
        self.assertEqual(mgr._warm.count(), 3)

    def test_namespace_isolation(self):
        """Searching with a namespace filter only returns matching namespace results."""
        mgr = self._make_manager()
        mgr.store("WorkspaceMem", "Belongs to workspace namespace", namespace="workspace")
        mgr.store("PersonalMem", "Belongs to personal namespace", namespace="personal")
        results = mgr.search("namespace", k=10, namespace="workspace")
        for r in results:
            self.assertEqual(r.get("namespace"), "workspace",
                             f"Expected namespace=workspace, got {r.get('namespace')}")

    def test_include_cold_searches_archive(self):
        """include_cold=True causes ColdStore.search_fts to be called."""
        mgr = self._make_manager()
        # Add a cold memory directly to archived_memories
        con = sqlite3.connect(str(self.db_file))
        con.execute("""INSERT INTO archived_memories VALUES (
            'cold-mem','long','workspace','ColdKeyword','Archived cold memory keyword data',
            '[]',4,1.0,'test',0,'2025-01-01','2025-01-01',NULL,NULL,'{}',
            '2025-06-01','manual'
        )""")
        con.commit()
        con.close()

        results = mgr.search("cold keyword data", k=10, include_cold=True)
        tiers = [r.get("_tier") for r in results]
        self.assertIn("cold", tiers, "Cold tier results should appear when include_cold=True")


# ═══════════════════════════════════════════════════════════════════════════════
# 5. INTEGRATION TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestIntegration(unittest.TestCase):

    def setUp(self):
        self._tmpdir_obj = tempfile.TemporaryDirectory()
        self.tmpdir = self._tmpdir_obj.name
        self.db_file = _make_test_db(self.tmpdir)
        self.lance_path = Path(self.tmpdir) / "lance"
        # Add required tables
        con = sqlite3.connect(str(self.db_file))
        con.execute("CREATE TABLE IF NOT EXISTS schema_version (version INTEGER)")
        con.execute("INSERT OR IGNORE INTO schema_version VALUES (7)")
        con.execute("""CREATE TABLE IF NOT EXISTS namespace_meta (
            namespace TEXT PRIMARY KEY, standard_id TEXT,
            parent_namespace TEXT, updated_at TEXT
        )""")
        con.commit()
        con.close()

    def tearDown(self):
        self._tmpdir_obj.cleanup()

    def test_full_lifecycle(self):
        """
        Store → Search (warm) → Demote → Search with cold → Promote → Search (warm again).
        Full tier lifecycle in one integration test.
        """
        from memory_tier_manager import TierManager
        from memory_hot_cache import HotCache

        hot = HotCache(max_size=10, ttl_seconds=60)
        mgr = TierManager(
            db_path=self.db_file,
            lance_path=self.lance_path,
            hot_cache=hot,
            auto_sync=False,
        )

        # 1. Store a memory
        mem_id = mgr.store(
            "IntegrationLifecycle",
            "Full tier lifecycle test: store, demote, promote",
            namespace="workspace",
            tier="short",
        )
        self.assertIsNotNone(mem_id)

        # 2. Search warm — should find it
        results = mgr.search("full tier lifecycle test", k=5)
        titles = [r.get("title") for r in results]
        self.assertIn("IntegrationLifecycle", titles)

        # 3. Demote it manually
        from memory_cold_store import ColdStore
        cold = ColdStore(db_path=self.db_file)
        cold.demote(self.db_file, mem_id, mgr._warm)

        # 4. Search with cold enabled — should surface it
        results_cold = mgr.search("lifecycle test", k=5, include_cold=True)
        cold_tiers = [r.get("_tier") for r in results_cold]
        self.assertIn("cold", cold_tiers)

        # 5. Promote back to warm
        promoted = mgr.promote_to_warm(mem_id)
        self.assertIsNotNone(promoted)
        self.assertEqual(promoted["title"], "IntegrationLifecycle")

        # 6. Warm search should find it again
        results_final = mgr.search("lifecycle restore", k=5)
        self.assertTrue(len(results_final) > 0)

    def test_embedding_persistence_across_instances(self):
        """
        LanceDB data persists across LanceWarmStore instances
        (simulates process restart).
        """
        from memory_lance_store import LanceWarmStore
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)

        # Instance 1 — write
        store1 = LanceWarmStore(db_path=self.lance_path)
        emb = model.encode("Persistent embedding across restarts")
        store1.upsert({
            "id": 100, "title": "PersistTest",
            "content": "Persistent embedding across restarts",
            "namespace": "workspace", "priority": 5, "tier": "warm",
            "access_count": 0, "last_accessed_at": "", "tags": "[]",
        }, emb)
        del store1

        # Instance 2 — read (simulates new process)
        store2 = LanceWarmStore(db_path=self.lance_path)
        self.assertEqual(store2.count(), 1)
        results = store2.search("persistent embedding", model, k=5)
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]["title"], "PersistTest")


# ═══════════════════════════════════════════════════════════════════════════════
# Entry point
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    test_classes = [
        TestHotCache,
        TestLanceWarmStore,
        TestColdStore,
        TestTierManager,
        TestIntegration,
    ]

    for cls in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
