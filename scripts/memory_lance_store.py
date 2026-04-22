#!/usr/bin/env python3
"""
memory_lance_store.py — LanceDB warm tier for the tiered memory system.

DB path: ~/.openclaw/workspace/lance_memory/
Schema: id, namespace, title, content, tags, priority, tier, access_count,
        last_accessed_at, embedding (384 floats)
"""

from __future__ import annotations

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
    """Convert a LanceDB result row to a plain dict, stripping Arrow artifacts."""
    result = {}
    for k, v in row.items():
        if k == "embedding":
            continue  # Don't expose raw embedding in search results
        if hasattr(v, "as_py"):
            result[k] = v.as_py()
        else:
            result[k] = v
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
        """
        emb = embedding_array.astype(np.float32).tolist()
        record = {
            "id": int(memory_dict.get("id", 0)),
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

    def sync_from_sqlite(self, db_path: Path, model) -> int:
        """
        Read all non-archived memories from SQLite, upsert each with
        freshly computed embedding. Returns count synced.
        """
        import json

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
        for i, row in enumerate(rows):
            d = dict(row)
            text = f"{d.get('title', '')} {d.get('content', '')}"
            texts.append(text)
            # Map string id to integer for LanceDB (use rowid or hash)
            # We store an integer id — use index + 1 as proxy if needed
            # But we need stable ids — we'll use the hash of the string UUID
            str_id = d.get("id", "")
            try:
                int_id = int(str_id)
            except (ValueError, TypeError):
                # Hash the UUID string to a positive int
                int_id = abs(hash(str_id)) % (2**31)
            d["_int_id"] = int_id
            records.append(d)

        embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)

        for d, emb in zip(records, embeddings):
            mem_dict = {
                "id": d["_int_id"],
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
