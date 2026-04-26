#!/usr/bin/env python3
"""
memory_tier_manager.py — Unified orchestrator for the tiered memory system.

Search flow:
  1. HotCache (in-process LRU, <1ms)
  2. LanceDB Warm store (ANN + hybrid RRF, ~5-20ms)
  3. SQLite Cold store (FTS5 fallback, optional)

Also exposes store(), delete(), promote(), demote(), stats().

Usage:
    from memory_tier_manager import TierManager
    mgr = TierManager()
    results = mgr.search("cascade proxy configuration", k=5)
    mgr.store({"title": "...", "content": "..."})
    print(mgr.stats())
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# ── path setup ────────────────────────────────────────────────────────────────
_SCRIPTS = Path(__file__).parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from memory_hot_cache import HotCache, get_hot_cache
from memory_lance_store import LanceWarmStore
from memory_cold_store import ColdStore
from memory_db import MemoryDB

_WORKSPACE = Path(os.environ.get("OPENCLAW_WORKSPACE", Path.home() / ".openclaw" / "workspace"))
_DB_PATH = _WORKSPACE / "ai-memory.db"
_LANCE_PATH = _WORKSPACE / "lance_memory"

# ── lazy model ────────────────────────────────────────────────────────────────
_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
    return _model


class TierManager:
    """
    Orchestrates Hot, Warm, and Cold memory tiers.

    Parameters
    ----------
    db_path      : Path to ai-memory.db (SQLite)
    lance_path   : Path to LanceDB persistent store
    hot_cache    : HotCache instance (defaults to process-wide singleton)
    auto_sync    : If True, sync SQLite → LanceDB on first search when warm store is empty
    """

    def __init__(
        self,
        db_path: Optional[Path] = None,
        lance_path: Optional[Path] = None,
        hot_cache: Optional[HotCache] = None,
        auto_sync: bool = True,
    ):
        self._db_path = Path(db_path) if db_path else _DB_PATH
        self._lance_path = Path(lance_path) if lance_path else _LANCE_PATH
        self._hot = hot_cache or get_hot_cache()
        self._warm = LanceWarmStore(db_path=self._lance_path)
        self._cold = ColdStore(db_path=self._db_path)
        self._db = MemoryDB(db_path=self._db_path)
        self._auto_sync = auto_sync
        self._searches = 0
        self._hot_hits = 0

    # ── SEARCH ────────────────────────────────────────────────────────────────

    def search(
        self,
        query: str,
        k: int = 10,
        include_cold: bool = False,
        namespace: Optional[str] = None,
    ) -> List[Dict]:
        """
        Tiered search: Hot → Warm (hybrid RRF) → Cold (optional FTS5).

        Returns a ranked list of dicts, each with a '_score' and '_tier' field.
        Higher _score = better match.
        """
        self._searches += 1
        model = _get_model()

        # Auto-sync on first use if warm store is empty
        if self._auto_sync and self._warm.count() == 0:
            self._warm.sync_from_sqlite(self._db_path, model)

        # Phase 1 — Warm vector + FTS5 hybrid
        fts_results = self._db.search_fts(query, namespace=namespace, limit=k)
        # Apply namespace filter to warm results after retrieval
        warm_results = self._warm.hybrid_search(query, fts_results, model, k=k)

        if namespace:
            warm_results = [r for r in warm_results if r.get("namespace") == namespace]

        # Phase 2 — Hot cache promotion for top result
        for result in warm_results[:3]:
            self._hot.put(result)

        # Phase 3 — Cold fallback
        cold_results = []
        if include_cold:
            cold_hits = self._cold.search_fts(query, limit=5)
            for hit in cold_hits:
                hit["_tier"] = "cold"
                hit["_score"] = 0.01  # cold results rank below warm
                cold_results.append(hit)

        combined = warm_results + cold_results
        combined.sort(key=lambda r: r.get("_score", 0), reverse=True)
        return combined[:k]

    # ── STORE ─────────────────────────────────────────────────────────────────

    def store(
        self,
        title: str,
        content: str,
        namespace: str = "workspace",
        tier: str = "short",
        tags: Optional[List[str]] = None,
        priority: int = 5,
    ) -> str:
        """
        Write a new memory to SQLite and index it in LanceDB warm store.
        Returns the memory id.
        """
        mem_id = self._db.add(
            title, content,
            namespace=namespace,
            tier=tier,
            tags=tags or [],
            priority=priority,
        )

        # Compute embedding and upsert to warm store
        model = _get_model()
        text = f"{title} {content}"
        emb = model.encode(text, convert_to_numpy=True)
        mem_dict = {
            "id": abs(hash(mem_id)) % (2 ** 31),
            "namespace": namespace,
            "title": title,
            "content": content,
            "tags": str(tags or []),
            "priority": float(priority),
            "tier": "warm",
            "access_count": 0,
            "last_accessed_at": "",
        }
        self._warm.upsert(mem_dict, emb)
        return mem_id

    # ── GET ───────────────────────────────────────────────────────────────────

    def get(self, memory_id: str) -> Optional[Dict]:
        """Fetch a single memory by id. Checks hot cache first."""
        cached = self._hot.get(memory_id)
        if cached:
            self._hot_hits += 1
            return cached

        result = self._db.get(memory_id)
        if result:
            self._hot.put(result)
        return result

    # ── DELETE ────────────────────────────────────────────────────────────────

    def delete(self, memory_id: str) -> bool:
        """Remove from all tiers."""
        self._hot.invalidate(memory_id)
        int_id = abs(hash(memory_id)) % (2 ** 31)
        self._warm.delete(int_id)
        return self._db.delete(memory_id)

    # ── PROMOTE / DEMOTE ──────────────────────────────────────────────────────

    def promote_to_warm(self, memory_id: str) -> Optional[Dict]:
        """
        Move a cold (archived) memory back to warm.
        Recomputes embedding and inserts into LanceDB.
        """
        model = _get_model()
        return self._cold.promote(self._db_path, memory_id, self._warm, model)

    def demote_cold_candidates(self, days_inactive: int = 90) -> int:
        """
        Archive memories that haven't been accessed in `days_inactive` days
        and have access_count == 0. Removes them from LanceDB warm store.
        Returns count demoted.
        """
        candidates = self._cold.get_demotion_candidates(
            db_path=self._db_path, days_inactive=days_inactive
        )
        count = 0
        for mid in candidates:
            if self._cold.demote(self._db_path, mid, self._warm):
                self._hot.invalidate(mid)
                count += 1
        return count

    # ── REBUILD ───────────────────────────────────────────────────────────────

    def rebuild_warm_index(self) -> int:
        """
        Full resync: read all SQLite memories, recompute embeddings,
        upsert everything into LanceDB. Returns count synced.
        """
        model = _get_model()
        return self._warm.sync_from_sqlite(self._db_path, model)

    # ── STATS ─────────────────────────────────────────────────────────────────

    def stats(self) -> Dict:
        """Return tier health metrics."""
        db_stats = self._db.stats()
        hot_stats = self._hot.stats()
        warm_count = self._warm.count()
        cold_count = self._cold.count()

        return {
            "tiers": {
                "hot": hot_stats,
                "warm": {"records": warm_count},
                "cold": {"records": cold_count},
            },
            "sqlite": db_stats,
            "searches_this_session": self._searches,
            "hot_cache_hits_this_session": self._hot_hits,
        }


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    import json

    p = argparse.ArgumentParser(description="Elite Memory Tier Manager CLI")
    sub = p.add_subparsers(dest="cmd")

    srch = sub.add_parser("search", help="Tiered hybrid search")
    srch.add_argument("query")
    srch.add_argument("--k", type=int, default=5)
    srch.add_argument("--cold", action="store_true")
    srch.add_argument("--ns")

    store_p = sub.add_parser("store", help="Store a new memory")
    store_p.add_argument("title")
    store_p.add_argument("content")
    store_p.add_argument("--ns", default="workspace")
    store_p.add_argument("--tier", default="short")
    store_p.add_argument("--priority", type=int, default=5)

    sub.add_parser("stats", help="Show tier statistics")
    sub.add_parser("rebuild", help="Rebuild LanceDB warm index from SQLite")

    demote_p = sub.add_parser("demote", help="Demote stale cold candidates")
    demote_p.add_argument("--days", type=int, default=90)

    args = p.parse_args()
    mgr = TierManager()

    if args.cmd == "search":
        results = mgr.search(args.query, k=args.k, include_cold=args.cold, namespace=args.ns)
        for r in results:
            tier = r.get("_tier", "?")
            score = r.get("_score", 0)
            print(f"[{tier}:{score:.4f}] {r.get('title', '?')} — {r.get('namespace', '?')}")

    elif args.cmd == "store":
        mid = mgr.store(args.title, args.content, namespace=args.ns, tier=args.tier, priority=args.priority)
        print(f"Stored id={mid}")

    elif args.cmd == "stats":
        print(json.dumps(mgr.stats(), indent=2))

    elif args.cmd == "rebuild":
        n = mgr.rebuild_warm_index()
        print(f"Rebuilt warm index: {n} records synced")

    elif args.cmd == "demote":
        n = mgr.demote_cold_candidates(days_inactive=args.days)
        print(f"Demoted {n} cold candidates")

    else:
        p.print_help()
