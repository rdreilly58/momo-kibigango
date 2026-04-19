#!/usr/bin/env python3
"""
memory_db.py — Python API for ai-memory.db (SQLite, schema v7)

Usage (module):
    from memory_db import MemoryDB
    db = MemoryDB()
    id_ = db.add("Session reset", "Context pruned...", tier="short", namespace="workspace")
    results = db.search_fts("cascade proxy")

Usage (CLI):
    python3 memory_db.py add "Title" "Content" [--tier short] [--ns workspace] [--tags tag1,tag2]
    python3 memory_db.py search "query" [--ns workspace] [--limit 5]
    python3 memory_db.py get <id>
    python3 memory_db.py expire          # archive TTL-expired memories
    python3 memory_db.py clean-links     # remove orphaned links
    python3 memory_db.py stats

Tiers:    working (this session), short (days), long (persistent)
Namespaces: workspace, leidos, personal, projects/<name>
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_PATH = Path.home() / ".openclaw" / "workspace" / "ai-memory.db"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def _conn(db_path: Path = DB_PATH):
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA foreign_keys=ON")
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


class MemoryDB:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path

    # ── WRITE ────────────────────────────────────────────────────────────────

    def add(
        self,
        title: str,
        content: str,
        *,
        tier: str = "short",
        namespace: str = "workspace",
        tags: List[str] | None = None,
        priority: int = 5,
        confidence: float = 1.0,
        source: str = "api",
        expires_at: Optional[str] = None,
        metadata: Dict[str, Any] | None = None,
    ) -> str:
        """Insert or update a memory. Returns the memory ID."""
        tags = tags or []
        metadata = metadata or {}
        now = _now()
        mem_id = str(uuid.uuid4())
        with _conn(self.db_path) as con:
            # UPSERT on (title, namespace) — update content if already exists
            existing = con.execute(
                "SELECT id FROM memories WHERE title=? AND namespace=?",
                (title, namespace),
            ).fetchone()
            if existing:
                con.execute(
                    """UPDATE memories SET content=?, tier=?, tags=?, priority=?,
                       confidence=?, source=?, expires_at=?, metadata=?, updated_at=?
                       WHERE id=?""",
                    (
                        content, tier, json.dumps(tags), priority, confidence,
                        source, expires_at, json.dumps(metadata), now, existing["id"],
                    ),
                )
                return existing["id"]
            con.execute(
                """INSERT INTO memories
                   (id, tier, namespace, title, content, tags, priority,
                    confidence, source, created_at, updated_at, expires_at, metadata)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    mem_id, tier, namespace, title, content,
                    json.dumps(tags), priority, confidence, source,
                    now, now, expires_at, json.dumps(metadata),
                ),
            )
        return mem_id

    def update(self, mem_id: str, **fields) -> bool:
        """Update arbitrary fields on an existing memory."""
        allowed = {
            "title", "content", "tier", "namespace", "tags", "priority",
            "confidence", "source", "expires_at", "metadata",
        }
        updates = {k: v for k, v in fields.items() if k in allowed}
        if not updates:
            return False
        updates["updated_at"] = _now()
        # JSON-encode list/dict fields
        for k in ("tags", "metadata"):
            if k in updates and not isinstance(updates[k], str):
                updates[k] = json.dumps(updates[k])
        set_clause = ", ".join(f"{k}=?" for k in updates)
        values = list(updates.values()) + [mem_id]
        with _conn(self.db_path) as con:
            cur = con.execute(f"UPDATE memories SET {set_clause} WHERE id=?", values)
            return cur.rowcount > 0

    def delete(self, mem_id: str) -> bool:
        with _conn(self.db_path) as con:
            cur = con.execute("DELETE FROM memories WHERE id=?", (mem_id,))
            return cur.rowcount > 0

    def link(self, source_id: str, target_id: str, relation: str = "related_to") -> bool:
        """Link two memories."""
        now = _now()
        try:
            with _conn(self.db_path) as con:
                con.execute(
                    "INSERT OR IGNORE INTO memory_links (source_id, target_id, relation, created_at) VALUES (?,?,?,?)",
                    (source_id, target_id, relation, now),
                )
            return True
        except sqlite3.IntegrityError:
            return False

    def archive(self, mem_id: str, reason: str = "manual") -> bool:
        """Move a memory to archived_memories."""
        now = _now()
        with _conn(self.db_path) as con:
            row = con.execute("SELECT * FROM memories WHERE id=?", (mem_id,)).fetchone()
            if not row:
                return False
            con.execute(
                """INSERT OR REPLACE INTO archived_memories
                   (id, tier, namespace, title, content, tags, priority, confidence,
                    source, access_count, created_at, updated_at, last_accessed_at,
                    expires_at, metadata, archived_at, archive_reason)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (*[row[k] for k in (
                    "id","tier","namespace","title","content","tags","priority",
                    "confidence","source","access_count","created_at","updated_at",
                    "last_accessed_at","expires_at","metadata",
                )], now, reason),
            )
            con.execute("DELETE FROM memories WHERE id=?", (mem_id,))
        return True

    # ── READ ─────────────────────────────────────────────────────────────────

    def get(self, mem_id: str) -> Optional[Dict]:
        with _conn(self.db_path) as con:
            row = con.execute("SELECT * FROM memories WHERE id=?", (mem_id,)).fetchone()
            if not row:
                return None
            r = dict(row)
            r["tags"] = json.loads(r["tags"] or "[]")
            r["metadata"] = json.loads(r["metadata"] or "{}")
            # bump access_count
            con.execute(
                "UPDATE memories SET access_count=access_count+1, last_accessed_at=? WHERE id=?",
                (_now(), mem_id),
            )
        return r

    def search_fts(
        self,
        query: str,
        *,
        namespace: Optional[str] = None,
        tier: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict]:
        """Full-text search via FTS5."""
        with _conn(self.db_path) as con:
            if namespace:
                rows = con.execute(
                    """SELECT m.*, snippet(memories_fts, 1, '[', ']', '...', 20) AS snippet
                       FROM memories_fts
                       JOIN memories m ON m.rowid = memories_fts.rowid
                       WHERE memories_fts MATCH ? AND m.namespace=?
                       ORDER BY rank LIMIT ?""",
                    (query, namespace, limit),
                ).fetchall()
            else:
                rows = con.execute(
                    """SELECT m.*, snippet(memories_fts, 1, '[', ']', '...', 20) AS snippet
                       FROM memories_fts
                       JOIN memories m ON m.rowid = memories_fts.rowid
                       WHERE memories_fts MATCH ?
                       ORDER BY rank LIMIT ?""",
                    (query, limit),
                ).fetchall()
            results = []
            for row in rows:
                r = dict(row)
                r["tags"] = json.loads(r.get("tags") or "[]")
                r["metadata"] = json.loads(r.get("metadata") or "{}")
                results.append(r)
        return results

    def list(
        self,
        *,
        namespace: Optional[str] = None,
        tier: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Dict]:
        clauses, params = [], []
        if namespace:
            clauses.append("namespace=?")
            params.append(namespace)
        if tier:
            clauses.append("tier=?")
            params.append(tier)
        where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
        params += [limit, offset]
        with _conn(self.db_path) as con:
            rows = con.execute(
                f"SELECT * FROM memories {where} ORDER BY priority DESC, updated_at DESC LIMIT ? OFFSET ?",
                params,
            ).fetchall()
        results = []
        for row in rows:
            r = dict(row)
            r["tags"] = json.loads(r.get("tags") or "[]")
            r["metadata"] = json.loads(r.get("metadata") or "{}")
            results.append(r)
        return results

    # ── MAINTENANCE ──────────────────────────────────────────────────────────

    def expire_ttl(self) -> int:
        """Archive all memories where expires_at < now. Returns count archived."""
        now = _now()
        with _conn(self.db_path) as con:
            expired = con.execute(
                "SELECT id FROM memories WHERE expires_at IS NOT NULL AND expires_at < ?",
                (now,),
            ).fetchall()
        count = 0
        for row in expired:
            if self.archive(row["id"], reason="ttl_expired"):
                count += 1
        return count

    def clean_orphaned_links(self) -> int:
        """Remove memory_links whose source or target no longer exists."""
        with _conn(self.db_path) as con:
            cur = con.execute(
                """DELETE FROM memory_links WHERE
                   source_id NOT IN (SELECT id FROM memories)
                   OR target_id NOT IN (SELECT id FROM memories)"""
            )
            return cur.rowcount

    def stats(self) -> Dict:
        with _conn(self.db_path) as con:
            memories = con.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
            archived = con.execute("SELECT COUNT(*) FROM archived_memories").fetchone()[0]
            links = con.execute("SELECT COUNT(*) FROM memory_links").fetchone()[0]
            orphaned = con.execute(
                """SELECT COUNT(*) FROM memory_links WHERE
                   source_id NOT IN (SELECT id FROM memories)
                   OR target_id NOT IN (SELECT id FROM memories)"""
            ).fetchone()[0]
            by_tier = {
                r[0]: r[1]
                for r in con.execute(
                    "SELECT tier, COUNT(*) FROM memories GROUP BY tier"
                ).fetchall()
            }
            by_ns = {
                r[0]: r[1]
                for r in con.execute(
                    "SELECT namespace, COUNT(*) FROM memories GROUP BY namespace"
                ).fetchall()
            }
        return {
            "memories": memories,
            "archived": archived,
            "links": links,
            "orphaned_links": orphaned,
            "by_tier": by_tier,
            "by_namespace": by_ns,
        }


# ── CLI ───────────────────────────────────────────────────────────────────────

def _cli():
    p = argparse.ArgumentParser(description="ai-memory.db CLI")
    sub = p.add_subparsers(dest="cmd")

    a = sub.add_parser("add", help="Add a memory")
    a.add_argument("title")
    a.add_argument("content")
    a.add_argument("--tier", default="short", choices=["working", "short", "long"])
    a.add_argument("--ns", default="workspace")
    a.add_argument("--tags", default="")
    a.add_argument("--priority", type=int, default=5)

    s = sub.add_parser("search", help="FTS search")
    s.add_argument("query")
    s.add_argument("--ns")
    s.add_argument("--limit", type=int, default=10)
    s.add_argument("--json", dest="as_json", action="store_true")

    g = sub.add_parser("get", help="Get memory by ID")
    g.add_argument("id")

    sub.add_parser("expire", help="Archive TTL-expired memories")
    sub.add_parser("clean-links", help="Remove orphaned links")
    sub.add_parser("stats", help="Show database statistics")

    ls = sub.add_parser("list", help="List memories")
    ls.add_argument("--ns")
    ls.add_argument("--tier")
    ls.add_argument("--limit", type=int, default=20)

    args = p.parse_args()
    db = MemoryDB()

    if args.cmd == "add":
        tags = [t.strip() for t in args.tags.split(",") if t.strip()]
        mem_id = db.add(args.title, args.content, tier=args.tier, namespace=args.ns, tags=tags, priority=args.priority)
        print(f"ok id={mem_id}")

    elif args.cmd == "search":
        results = db.search_fts(args.query, namespace=args.ns, limit=args.limit)
        if args.as_json:
            print(json.dumps(results, indent=2))
        else:
            for r in results:
                print(f"[{r['tier']}:{r['namespace']}] {r['title']}")
                print(f"  {r.get('snippet', r['content'][:120])}")

    elif args.cmd == "get":
        r = db.get(args.id)
        print(json.dumps(r, indent=2) if r else "not found")

    elif args.cmd == "expire":
        n = db.expire_ttl()
        print(f"archived {n} expired memories")

    elif args.cmd == "clean-links":
        n = db.clean_orphaned_links()
        print(f"removed {n} orphaned links")

    elif args.cmd == "stats":
        print(json.dumps(db.stats(), indent=2))

    elif args.cmd == "list":
        results = db.list(namespace=args.ns, tier=args.tier, limit=args.limit)
        for r in results:
            print(f"[{r['tier']}:{r['namespace']}] {r['title']} (p={r['priority']})")

    else:
        p.print_help()


if __name__ == "__main__":
    _cli()
