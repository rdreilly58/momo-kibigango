#!/usr/bin/env python3
"""
memory_lance_store.py — LanceDB warm tier for the tiered memory system.

DB path: ~/.openclaw/workspace/lance_memory/
Schema: id, namespace, title, content, tags, priority, tier, access_count,
        last_accessed_at, embedding (384 floats)
"""

from __future__ import annotations

import hashlib
import sqlite3
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pyarrow as pa

_LANCE_DB_PATH = Path.home() / ".openclaw" / "workspace" / "lance_memory"
_TABLE_NAME = "memories"
_EMBEDDING_DIM = 384


def _stable_int_id(str_id: str) -> int:
    """
    Deterministic 63-bit integer derived from a stable string ID via SHA-256.

    Replaces Python's built-in hash() (which is randomised per-process and
    truncated to 31 bits, giving ~1/2B collision probability per pair).

    Returns a non-negative int that fits in pa.int64() (max 2**63 - 1).
    Collision probability for SHA-256 truncated to 63 bits is ~1/(2**63),
    i.e. effectively zero at any realistic scale.
    """
    digest = hashlib.sha256(str(str_id).encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") & ((1 << 63) - 1)


# Process-local mapping of LanceDB int IDs back to their original SQLite UUID
# strings, populated during sync_from_sqlite/upsert. Used by _row_to_dict to
# translate search results so the public `id` field is always the canonical
# UUID — keeps HotCache keys consistent with TierManager.get(uuid_string).
_INT_TO_UUID: Dict[int, str] = {}
_INT_TO_UUID_LOADED = False


def _ensure_int_to_uuid_loaded() -> None:
    """
    Lazy-populate the int_id -> uuid mapping from SQLite on first access.

    Necessary because the in-memory mapping is empty when a process starts
    fresh and queries existing LanceDB rows that were upserted by a previous
    process. Cost: one SQLite scan + N applications of _stable_int_id() per
    process lifetime, then the mapping is reused.
    """
    global _INT_TO_UUID_LOADED
    if _INT_TO_UUID_LOADED:
        return
    db_path = Path.home() / ".openclaw" / "workspace" / "ai-memory.db"
    if not db_path.exists():
        _INT_TO_UUID_LOADED = True
        return
    try:
        con = sqlite3.connect(str(db_path))
        rows = con.execute("SELECT id FROM memories").fetchall()
        con.close()
    except Exception:
        _INT_TO_UUID_LOADED = True
        return
    for (str_id,) in rows:
        if not str_id:
            continue
        try:
            int_id = int(str_id)
        except (ValueError, TypeError):
            int_id = _stable_int_id(str_id)
        _INT_TO_UUID.setdefault(int_id, str(str_id))
    _INT_TO_UUID_LOADED = True

# Lazy import lancedb to allow tests to mock it
def _get_lancedb():
    import lancedb
    return lancedb


def _make_schema() -> pa.Schema:
    return pa.schema([
        pa.field("id", pa.int64()),
        pa.field("namespace", pa.utf8()),
        pa.field("title", pa.utf8()),
        pa.field("content", pa.utf8()),
        pa.field("tags", pa.utf8()),
        pa.field("priority", pa.float32()),
        pa.field("tier", pa.utf8()),
        pa.field("access_count", pa.int32()),
        pa.field("last_accessed_at", pa.utf8()),
        pa.field("embedding", pa.list_(pa.float32(), _EMBEDDING_DIM)),
    ])


def _row_to_dict(row: dict) -> dict:
    """Convert a LanceDB result row to a plain dict, stripping Arrow artifacts.

    If the row's int `id` has a known mapping in _INT_TO_UUID, the public `id`
    field is replaced with the original UUID string and the int is preserved
    as `_int_id` for diagnostics. This keeps the cache layer keyed by UUID
    strings end-to-end so HotCache hits on TierManager.get(uuid_string).
    """
    result = {}
    for k, v in row.items():
        if k == "embedding":
            continue  # Don't expose raw embedding in search results
        if hasattr(v, "as_py"):
            result[k] = v.as_py()
        else:
            result[k] = v
    int_id = result.get("id")
    if isinstance(int_id, int):
        uuid = _INT_TO_UUID.get(int_id)
        if uuid is None:
            # Lazy-load on first miss so search results from existing LanceDB
            # rows (upserted by an earlier process) get translated.
            _ensure_int_to_uuid_loaded()
            uuid = _INT_TO_UUID.get(int_id)
        if uuid is not None:
            result["_int_id"] = int_id
            result["id"] = uuid
    return result


def _rrf_score(ranks: list[int], k: int = 60) -> float:
    """Reciprocal Rank Fusion score for a list of ranks."""
    return sum(1.0 / (k + r) for r in ranks)


class LanceWarmStore:
    """
    Persistent vector store backed by LanceDB.
    Handles upsert, ANN search, hybrid RRF search, delete, and SQLite sync.
    """

    def __init__(self, db_path: Optional[Path] = None):
        self._db_path = Path(db_path) if db_path else _LANCE_DB_PATH
        self._db_path.mkdir(parents=True, exist_ok=True)
        lancedb = _get_lancedb()
        self._db = lancedb.connect(str(self._db_path))
        self._table = self._get_or_create_table()

    def _get_or_create_table(self):
        lancedb = _get_lancedb()
        try:
            return self._db.open_table(_TABLE_NAME)
        except Exception:
            schema = _make_schema()
            return self._db.create_table(_TABLE_NAME, schema=schema)

    def _ensure_table(self):
        """Re-open table reference (useful after sync)."""
        self._table = self._get_or_create_table()

    def upsert(self, memory_dict: dict, embedding_array: np.ndarray) -> None:
        """
        Upsert a memory record keyed by id.
        memory_dict must contain at least 'id', other fields are optional.
        embedding_array: numpy array of shape (384,)

        If memory_dict has a `_uuid` field (the original SQLite UUID string),
        the int_id <-> uuid mapping is recorded so subsequent reads can
        translate the int back to its UUID.
        """
        emb = embedding_array.astype(np.float32).tolist()
        int_id = int(memory_dict.get("id", 0))
        record = {
            "id": int_id,
            "namespace": str(memory_dict.get("namespace", "workspace")),
            "title": str(memory_dict.get("title", "")),
            "content": str(memory_dict.get("content", "")),
            "tags": str(memory_dict.get("tags", "[]")),
            "priority": float(memory_dict.get("priority", 3)),
            "tier": str(memory_dict.get("tier", "warm")),
            "access_count": int(memory_dict.get("access_count", 0)),
            "last_accessed_at": str(memory_dict.get("last_accessed_at", "") or ""),
            "embedding": emb,
        }
        uuid = memory_dict.get("_uuid")
        if uuid is not None:
            _INT_TO_UUID[int_id] = str(uuid)
        self._table.merge_insert("id") \
            .when_matched_update_all() \
            .when_not_matched_insert_all() \
            .execute([record])

    def search(self, query_str: str, model, k: int = 10) -> list[dict]:
        """
        Encode query, run ANN search, return list of dicts with '_score' field.
        """
        query_emb = model.encode(query_str, convert_to_numpy=True).astype(np.float32)
        try:
            results = (
                self._table.search(query_emb)
                .metric("cosine")
                .limit(k)
                .to_list()
            )
        except Exception:
            return []

        output = []
        for row in results:
            d = _row_to_dict(row)
            # _distance is cosine distance (0=perfect), convert to similarity score
            dist = row.get("_distance", 1.0)
            d["_score"] = float(1.0 - dist)
            d["_tier"] = "warm"
            output.append(d)
        return output

    def hybrid_search(
        self,
        query_str: str,
        fts_results: list[dict],
        model,
        k: int = 10,
    ) -> list[dict]:
        """
        Reciprocal Rank Fusion of vector results + FTS5 results.
        Weights: vector=0.6, fts=0.3, priority=0.1
        Returns fused list of dicts with '_score' field.
        """
        vector_results = self.search(query_str, model, k=k * 2)

        # Build rank maps: {memory_id: rank_position}
        vec_ranks: dict[Any, int] = {}
        for rank, r in enumerate(vector_results):
            mid = r.get("id")
            if mid is not None:
                vec_ranks[mid] = rank + 1  # 1-indexed

        fts_ranks: dict[Any, int] = {}
        for rank, r in enumerate(fts_results):
            mid = r.get("id")
            if mid is not None:
                fts_ranks[mid] = rank + 1

        # All candidate ids
        all_ids = set(vec_ranks.keys()) | set(fts_ranks.keys())

        # Build lookup: id -> record
        id_to_record: dict[Any, dict] = {}
        for r in vector_results:
            id_to_record[r.get("id")] = r
        for r in fts_results:
            mid = r.get("id")
            if mid not in id_to_record:
                id_to_record[mid] = dict(r)

        # RRF with weights
        k_rrf = 60
        scored = []
        for mid in all_ids:
            vec_rank = vec_ranks.get(mid, len(vector_results) + 100)
            fts_rank = fts_ranks.get(mid, len(fts_results) + 100)
            vec_score = 0.6 / (k_rrf + vec_rank)
            fts_score = 0.3 / (k_rrf + fts_rank)
            rec = id_to_record.get(mid, {})
            priority_norm = float(rec.get("priority", 3)) / 10.0
            priority_score = 0.1 * priority_norm
            total = vec_score + fts_score + priority_score
            scored.append((mid, total))

        scored.sort(key=lambda x: x[1], reverse=True)

        results = []
        for mid, score in scored[:k]:
            rec = dict(id_to_record.get(mid, {"id": mid}))
            rec["_score"] = round(score, 6)
            rec["_tier"] = rec.get("_tier", "warm")
            results.append(rec)

        return results

    def delete(self, memory_id: int) -> None:
        """Remove a record by id."""
        try:
            self._table.delete(f"id = {int(memory_id)}")
        except Exception:
            pass

    def truncate(self) -> int:
        """
        Drop and recreate the LanceDB table. Returns rows removed.
        Used by sync_from_sqlite when a clean rebuild is requested
        (e.g. after an ID-scheme change so legacy rows do not coexist
        with fresh upserts under different int IDs).
        """
        try:
            previous = self._table.count_rows()
        except Exception:
            previous = 0
        try:
            self._db.drop_table(_TABLE_NAME)
        except Exception:
            pass  # table may not exist yet
        self._table = self._get_or_create_table()
        # Reset the in-memory mapping; sync_from_sqlite will repopulate.
        _INT_TO_UUID.clear()
        global _INT_TO_UUID_LOADED
        _INT_TO_UUID_LOADED = False
        return previous

    def sync_from_sqlite(self, db_path: Path, model, *, clean: bool = True) -> int:
        """
        Read all non-archived memories from SQLite, upsert each with
        freshly computed embedding. Returns count synced.

        clean: if True (default), the LanceDB table is truncated first so
               legacy rows under stale ID schemes are removed. Set False
               when calling from incremental sync paths.
        """
        import json

        if clean:
            removed = self.truncate()
            if removed:
                print(
                    f"[memory_lance_store] sync_from_sqlite: truncated {removed} "
                    f"existing rows before clean rebuild.",
                    file=sys.stderr,
                )

        con = sqlite3.connect(str(db_path))
        con.row_factory = sqlite3.Row
        rows = con.execute(
            "SELECT * FROM memories"
        ).fetchall()
        con.close()

        if not rows:
            return 0

        # Compute embeddings in batch
        texts = []
        records = []
        seen_int_ids: Dict[int, str] = {}  # int_id -> uuid; used for collision detection
        for i, row in enumerate(rows):
            d = dict(row)
            text = f"{d.get('title', '')} {d.get('content', '')}"
            texts.append(text)
            # Stable int id derived from SHA-256 of the SQLite UUID. Replaces
            # the prior abs(hash()) % 2**31 which used Python's randomised hash
            # (process-local) and only had 31 bits of namespace.
            str_id = str(d.get("id", ""))
            try:
                int_id = int(str_id)
            except (ValueError, TypeError):
                int_id = _stable_int_id(str_id)
            # Collision detection: if two different UUIDs produce the same int_id
            # in this batch, log a clear warning so it never goes silent.
            prior_uuid = seen_int_ids.get(int_id)
            if prior_uuid is not None and prior_uuid != str_id:
                print(
                    f"[memory_lance_store] WARNING: int_id collision in sync_from_sqlite: "
                    f"int_id={int_id} produced by both uuid={prior_uuid!r} and uuid={str_id!r}; "
                    f"second record will overwrite the first in LanceDB.",
                    file=sys.stderr,
                )
            seen_int_ids[int_id] = str_id
            d["_int_id"] = int_id
            records.append(d)

        embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)

        for d, emb in zip(records, embeddings):
            mem_dict = {
                "id": d["_int_id"],
                "_uuid": str(d.get("id", "")),  # populates _INT_TO_UUID via upsert()
                "namespace": d.get("namespace", "workspace"),
                "title": d.get("title", ""),
                "content": d.get("content", ""),
                "tags": d.get("tags", "[]") if isinstance(d.get("tags"), str) else "[]",
                "priority": float(d.get("priority", 3)),
                "tier": d.get("tier", "warm"),
                "access_count": int(d.get("access_count", 0)),
                "last_accessed_at": str(d.get("last_accessed_at", "") or ""),
            }
            self.upsert(mem_dict, emb)

        return len(records)

    def count(self) -> int:
        """Total records in the warm store."""
        try:
            return self._table.count_rows()
        except Exception:
            return 0


if __name__ == "__main__":
    # Smoke test
    import tempfile
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        store = LanceWarmStore(db_path=Path(tmpdir) / "lance")

        emb = model.encode("Test memory content", convert_to_numpy=True)
        store.upsert({"id": 1, "title": "Test", "content": "Test memory content",
                      "namespace": "workspace", "priority": 5, "tier": "warm",
                      "access_count": 0, "last_accessed_at": "", "tags": "[]"}, emb)

        results = store.search("test memory", model, k=5)
        print("Search results:", len(results), "top score:", results[0]["_score"] if results else None)
        assert len(results) == 1
        assert results[0]["title"] == "Test"

        print("count:", store.count())
        store.delete(1)
        print("after delete:", store.count())
        print("LanceWarmStore smoke test PASSED")
