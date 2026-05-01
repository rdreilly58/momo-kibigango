#!/usr/bin/env python3
"""
memory-rerank.py — Recency × Relevance composite reranking for memory results.

Applies a weighted composite score over raw search results:
    score = (0.6 × vector_sim) + (0.25 × recency_boost) + (0.15 × access_boost)

Where:
    recency_boost = 1.0 / (1 + days_since_created / 30)
        → memories from the last 30 days score higher
    access_boost = min(access_count / 10, 1.0)
        → frequently accessed memories score higher

Input:  JSON array of memory search results (from memory_mcp_server, total_recall_search, etc.)
Output: Reranked JSON array with `_rerank_score` and `_rerank_details` fields.

Usage (CLI):
    # Rerank results from a JSON file:
    python3 memory-rerank.py results.json

    # Pipe from total_recall_search:
    python3 total_recall_search.py "anthropic spend check" --json | python3 memory-rerank.py -

    # Rerank a live query (auto-runs search and reranks):
    python3 memory-rerank.py --query "anthropic spend check"

Integration:
    total_recall_search.py supports --rerank flag (calls this module internally)
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

_SCRIPTS = Path(__file__).parent
sys.path.insert(0, str(_SCRIPTS))

DB_PATH = Path.home() / ".openclaw" / "workspace" / "ai-memory.db"

# Composite weights (must sum to 1.0)
W_VECTOR   = 0.60
W_RECENCY  = 0.25
W_ACCESS   = 0.15


def _age_days(created_at: str) -> float:
    """Return age in fractional days from created_at to now."""
    if not created_at:
        return 30.0  # default if unknown
    try:
        s = created_at.replace("Z", "+00:00")
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        delta = datetime.now(timezone.utc) - dt
        return max(0.0, delta.total_seconds() / 86400)
    except Exception:
        return 30.0


def _recency_boost(created_at: str) -> float:
    """
    Recency boost: 1.0 for brand-new, decays as memory ages.
    Half-life at 30 days: a 30-day-old memory scores 0.5.
    """
    age = _age_days(created_at)
    return 1.0 / (1.0 + age / 30.0)


def _access_boost(access_count) -> float:
    """Access boost: 0.0 for never accessed, 1.0 at 10+ accesses."""
    try:
        count = int(access_count or 0)
    except (TypeError, ValueError):
        count = 0
    return min(count / 10.0, 1.0)


def _load_db_metadata(result_ids: List[str], db_path: Path = DB_PATH) -> Dict[str, Dict]:
    """
    Load created_at and access_count from DB for known memory IDs.
    Returns {id: {created_at, access_count}}.
    """
    meta: Dict[str, Dict] = {}
    if not db_path.exists() or not result_ids:
        return meta

    placeholders = ",".join("?" * len(result_ids))
    try:
        with sqlite3.connect(db_path) as con:
            con.row_factory = sqlite3.Row
            rows = con.execute(
                f"SELECT id, created_at, access_count FROM memories WHERE id IN ({placeholders})",
                result_ids,
            ).fetchall()
        for row in rows:
            meta[row["id"]] = {
                "created_at": row["created_at"] or "",
                "access_count": row["access_count"] or 0,
            }
    except Exception as e:
        print(f"[rerank] DB lookup failed: {e}", file=sys.stderr)
    return meta


def rerank(
    results: List[Dict],
    db_path: Path = DB_PATH,
    w_vector: float = W_VECTOR,
    w_recency: float = W_RECENCY,
    w_access: float = W_ACCESS,
) -> List[Dict]:
    """
    Rerank a list of search results using composite scoring.

    Each result should have at least one of:
        - 'score' (float 0–1): raw vector/BM25 similarity
        - 'id' (str): memory ID for DB metadata lookup
        - 'created_at' (str): ISO timestamp (optional; will fetch from DB if id known)
        - 'access_count' (int): usage count (optional)

    Returns the same list sorted by _rerank_score descending.
    """
    if not results:
        return results

    # Collect IDs for DB lookup
    ids_to_fetch = [r["id"] for r in results if "id" in r and r["id"]]
    db_meta = _load_db_metadata(ids_to_fetch, db_path)

    scored = []
    for result in results:
        rid = result.get("id", "")

        # Raw similarity score (normalize to 0–1)
        raw_score = float(result.get("score", result.get("_score", 0.5)))
        raw_score = max(0.0, min(1.0, raw_score))

        # Get metadata from result or DB
        db_row = db_meta.get(rid, {})
        created_at = (
            result.get("created_at")
            or db_row.get("created_at")
            or ""
        )
        access_count = (
            result.get("access_count")
            or db_row.get("access_count")
            or 0
        )

        rec = _recency_boost(created_at)
        acc = _access_boost(access_count)

        composite = (w_vector * raw_score) + (w_recency * rec) + (w_access * acc)

        enriched = dict(result)
        enriched["_rerank_score"] = round(composite, 4)
        enriched["_rerank_details"] = {
            "vector_sim": round(raw_score, 4),
            "recency_boost": round(rec, 4),
            "access_boost": round(acc, 4),
            "age_days": round(_age_days(created_at), 1),
            "access_count": int(access_count),
            "weights": {"vector": w_vector, "recency": w_recency, "access": w_access},
        }
        scored.append(enriched)

    # Sort by composite score descending
    scored.sort(key=lambda x: x["_rerank_score"], reverse=True)
    return scored


def _run_query_and_rerank(query: str, verbose: bool = False) -> List[Dict]:
    """Run total_recall_search and rerank results."""
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, str(_SCRIPTS / "total_recall_search.py"),
             query, "--json", "--limit", "10"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0 and not result.stdout.strip():
            print(f"[rerank] Search failed: {result.stderr[:200]}", file=sys.stderr)
            return []
        raw = json.loads(result.stdout)
    except Exception as e:
        print(f"[rerank] Search error: {e}", file=sys.stderr)
        return []

    return rerank(raw)


def main():
    ap = argparse.ArgumentParser(description="Rerank memory search results by recency × relevance")
    grp = ap.add_mutually_exclusive_group(required=True)
    grp.add_argument("input", nargs="?", default=None,
                     help="Path to JSON results file, or '-' for stdin")
    grp.add_argument("--query", "-q",
                     help="Run search and rerank in one step")
    ap.add_argument("--verbose", "-v", action="store_true")
    ap.add_argument("--db", default=str(DB_PATH), help="SQLite DB path")
    args = ap.parse_args()

    if args.query:
        results = _run_query_and_rerank(args.query, verbose=args.verbose)
    else:
        # Read from file or stdin
        if args.input == "-":
            raw = sys.stdin.read()
        else:
            with open(args.input) as f:
                raw = f.read()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {e}", file=sys.stderr)
            sys.exit(1)
        results = rerank(data, db_path=Path(args.db))

    if args.verbose:
        for i, r in enumerate(results, 1):
            d = r.get("_rerank_details", {})
            title = r.get("title") or r.get("path") or r.get("id", "")[:40]
            print(
                f"  {i:2}. score={r['_rerank_score']:.4f} "
                f"(vec={d.get('vector_sim', 0):.3f} "
                f"rec={d.get('recency_boost', 0):.3f} "
                f"acc={d.get('access_boost', 0):.3f}) "
                f"age={d.get('age_days', '?')}d  {title[:60]}"
            )
    else:
        print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
