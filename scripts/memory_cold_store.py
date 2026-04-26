#!/usr/bin/env python3
"""
memory_cold_store.py — Cold tier logic for the tiered memory system.

Works on top of the existing SQLite archived_memories table.
"""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional

_DB_PATH = Path.home() / ".openclaw" / "workspace" / "ai-memory.db"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def _conn(db_path: Path):
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def _row_to_dict(row) -> dict:
    d = dict(row)
    for field in ("tags", "metadata"):
        if field in d and isinstance(d[field], str):
            try:
                d[field] = json.loads(d[field])
            except (json.JSONDecodeError, TypeError):
                pass
    return d


class ColdStore:
    """
    Cold tier — operates on SQLite archived_memories table.
    No embeddings are stored here; they are recomputed on promotion.
    """

    def __init__(self, db_path: Optional[Path] = None):
        self._db_path = Path(db_path) if db_path else _DB_PATH

    def search_fts(self, query: str, limit: int = 5) -> list[dict]:
        """
        Run FTS5 search on archived_memories using a simple LIKE fallback
        (archived_memories does not have an FTS5 virtual table in the current schema).
        Falls back to LIKE search if no FTS table exists.
        Returns list of dicts.
        """
        with _conn(self._db_path) as con:
            # Try FTS5 virtual table first (may not exist)
            try:
                rows = con.execute(
                    """SELECT a.*
                       FROM archived_memories_fts
                       JOIN archived_memories a ON a.rowid = archived_memories_fts.rowid
                       WHERE archived_memories_fts MATCH ?
                       ORDER BY rank LIMIT ?""",
                    (query, limit),
                ).fetchall()
            except sqlite3.OperationalError:
                # Fall back to per-word LIKE search (OR across all words)
                words = [w.strip() for w in query.split() if w.strip()]
                if not words:
                    rows = []
                else:
                    clauses = " OR ".join(
                        ["title LIKE ? OR content LIKE ?"] * len(words)
                    )
                    params = []
                    for w in words:
                        like = f"%{w}%"
                        params.extend([like, like])
                    params.append(limit)
                    rows = con.execute(
                        f"SELECT * FROM archived_memories WHERE {clauses} LIMIT ?",
                        params,
                    ).fetchall()

        return [_row_to_dict(r) for r in rows]

    def get_demotion_candidates(
        self, db_path: Optional[Path] = None, days_inactive: int = 90
    ) -> list[str]:
        """
        Return list of memory ids from main memories table where:
        last_accessed_at < now - days_inactive AND access_count == 0
        """
        db = Path(db_path) if db_path else self._db_path
        cutoff = (
            datetime.now(timezone.utc) - timedelta(days=days_inactive)
        ).isoformat()

        with _conn(db) as con:
            rows = con.execute(
                """SELECT id FROM memories
                   WHERE access_count = 0
                   AND (
                       last_accessed_at IS NULL
                       OR last_accessed_at < ?
                   )""",
                (cutoff,),
            ).fetchall()

        return [r["id"] for r in rows]

    def demote(self, db_path: Path, memory_id: str, lance_store) -> bool:
        """
        Move memory from memories → archived_memories, delete from LanceDB.
        Returns True if successful.
        """
        db = Path(db_path) if db_path else self._db_path
        now = _now_iso()

        with _conn(db) as con:
            row = con.execute(
                "SELECT * FROM memories WHERE id=?", (memory_id,)
            ).fetchone()
            if not row:
                return False

            # Insert into archived_memories
            d = dict(row)
            con.execute(
                """INSERT OR REPLACE INTO archived_memories
                   (id, tier, namespace, title, content, tags, priority, confidence,
                    source, access_count, created_at, updated_at, last_accessed_at,
                    expires_at, archived_at, archive_reason, metadata)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    d["id"], d.get("tier", "cold"), d.get("namespace", "workspace"),
                    d.get("title", ""), d.get("content", ""),
                    d.get("tags", "[]"), d.get("priority", 3),
                    d.get("confidence", 1.0), d.get("source", "api"),
                    d.get("access_count", 0), d.get("created_at", now),
                    d.get("updated_at", now), d.get("last_accessed_at"),
                    d.get("expires_at"), now, "demoted",
                    d.get("metadata", "{}"),
                ),
            )
            con.execute("DELETE FROM memories WHERE id=?", (memory_id,))

        # Remove from LanceDB warm store
        try:
            int_id = abs(hash(memory_id)) % (2**31)
            lance_store.delete(int_id)
        except Exception:
            pass

        return True

    def promote(
        self,
        db_path: Path,
        memory_id: str,
        lance_store,
        model,
    ) -> Optional[dict]:
        """
        Move from archived_memories → memories, recompute embedding,
        upsert to LanceDB, return dict.
        """
        db = Path(db_path) if db_path else self._db_path
        now = _now_iso()

        with _conn(db) as con:
            row = con.execute(
                "SELECT * FROM archived_memories WHERE id=?", (memory_id,)
            ).fetchone()
            if not row:
                return None

            d = dict(row)

            # Check if already in main memories
            existing = con.execute(
                "SELECT id FROM memories WHERE id=?", (memory_id,)
            ).fetchone()

            if not existing:
                con.execute(
                    """INSERT INTO memories
                       (id, tier, namespace, title, content, tags, priority,
                        confidence, source, access_count, created_at, updated_at,
                        last_accessed_at, expires_at, metadata)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        d["id"], "warm", d.get("namespace", "workspace"),
                        d.get("title", ""), d.get("content", ""),
                        d.get("tags", "[]"), d.get("priority", 3),
                        d.get("confidence", 1.0), d.get("source", "api"),
                        d.get("access_count", 0), d.get("created_at", now),
                        now, now, d.get("expires_at"),
                        d.get("metadata", "{}"),
                    ),
                )

            con.execute(
                "DELETE FROM archived_memories WHERE id=?", (memory_id,)
            )

        # Recompute embedding and upsert to LanceDB
        text = f"{d.get('title', '')} {d.get('content', '')}"
        emb = model.encode(text, convert_to_numpy=True)

        mem_dict = {
            "id": abs(hash(memory_id)) % (2**31),
            "namespace": d.get("namespace", "workspace"),
            "title": d.get("title", ""),
            "content": d.get("content", ""),
            "tags": d.get("tags", "[]") if isinstance(d.get("tags"), str) else "[]",
            "priority": float(d.get("priority", 3)),
            "tier": "warm",
            "access_count": int(d.get("access_count", 0)),
            "last_accessed_at": str(d.get("last_accessed_at", "") or ""),
        }
        lance_store.upsert(mem_dict, emb)

        result = _row_to_dict(row)
        result["tier"] = "warm"
        return result

    def count(self) -> int:
        """Count of archived memories."""
        with _conn(self._db_path) as con:
            return con.execute(
                "SELECT COUNT(*) FROM archived_memories"
            ).fetchone()[0]


if __name__ == "__main__":
    # Smoke test with real DB
    store = ColdStore()
    count = store.count()
    print(f"Cold store has {count} archived memories")
    candidates = store.get_demotion_candidates(days_inactive=90)
    print(f"Demotion candidates (90d inactive, 0 access): {len(candidates)}")
    fts = store.search_fts("test", limit=3)
    print(f"FTS search 'test': {len(fts)} results")
    print("ColdStore smoke test PASSED")
