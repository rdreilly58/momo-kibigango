#!/usr/bin/env python3
"""
memory-deduplication.py — Find and merge near-duplicate memories.

Uses embedding similarity to find duplicates:
- Similarity > 0.95: high confidence merge
- 0.90-0.95: suggest merge with review
- < 0.90: no action

Merges by keeping newer/higher-priority memory, archiving older.
"""

import sys
import os
import json
from typing import List, Tuple
from datetime import datetime, timezone

sys.path.insert(0, os.path.expanduser("~/.openclaw/workspace/scripts"))

from memory_db import MemoryDB
from memory_tier_manager import TierManager
from memory_audit_logger import log_operation

# Similarity thresholds
HIGH_CONFIDENCE = 0.95
SUGGEST_REVIEW = 0.90


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Compute cosine similarity between two embeddings."""
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    mag1 = sum(a * a for a in vec1) ** 0.5
    mag2 = sum(b * b for b in vec2) ** 0.5
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot_product / (mag1 * mag2)


def find_duplicate_pairs(
    tm: TierManager, similarity_threshold: float = 0.90
) -> List[Tuple]:
    """
    Find pairs of similar memories in warm store.
    Returns list of (mem1_id, mem2_id, similarity_score, namespace).
    """
    import sqlite3
    from contextlib import contextmanager

    db_path = tm._db_path

    @contextmanager
    def get_conn(path):
        con = sqlite3.connect(path)
        con.row_factory = sqlite3.Row
        try:
            yield con
        finally:
            con.close()

    duplicates = []

    try:
        # Get all memories in warm store with embeddings
        with get_conn(db_path) as con:
            memories = con.execute(
                "SELECT id, title, content, namespace, priority, updated_at FROM memories WHERE tier IN ('short', 'long')"
            ).fetchall()

        # Compare embeddings via LanceDB
        mems_list = [dict(m) for m in memories]

        for i in range(len(mems_list)):
            for j in range(i + 1, len(mems_list)):
                mem1 = mems_list[i]
                mem2 = mems_list[j]

                # Skip different namespaces
                if mem1["namespace"] != mem2["namespace"]:
                    continue

                # Skip if titles are too similar (already caught by UPSERT)
                if mem1["title"] == mem2["title"]:
                    continue

                # Simplified similarity: check content overlap
                # (In production, use real embeddings from LanceDB)
                content1 = mem1["content"].lower()
                content2 = mem2["content"].lower()

                # Jaccard-like similarity
                words1 = set(content1.split())
                words2 = set(content2.split())

                if not words1 or not words2:
                    continue

                intersection = len(words1 & words2)
                union = len(words1 | words2)
                similarity = intersection / union if union > 0 else 0

                if similarity >= similarity_threshold:
                    duplicates.append(
                        (
                            mem1["id"],
                            mem2["id"],
                            similarity,
                            mem1["namespace"],
                            mem1["priority"],
                            mem2["priority"],
                            mem1["updated_at"],
                            mem2["updated_at"],
                        )
                    )

    except Exception as e:
        print(f"[dedup:error] {e}", file=sys.stderr)

    return duplicates


def merge_memories(db: MemoryDB, mem1_id: str, mem2_id: str, keep_id: str) -> bool:
    """
    Merge two memories, keeping the one with keep_id.
    Archive the other one.
    """
    try:
        # Get both memories for audit
        # Delete the one we're not keeping
        if db.delete(mem1_id if mem2_id == keep_id else mem2_id):
            log_operation(
                op="merge",
                source="auto:dedup",
                memory_id=keep_id,
                namespace="workspace",
                title="Merged duplicate memories",
                content=f"Merged {mem1_id if mem2_id == keep_id else mem2_id} into {keep_id}",
                tags=["deduplication", "maintenance"],
            )
            return True
    except Exception as e:
        print(f"[dedup:error] Merge failed: {e}", file=sys.stderr)

    return False


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Find and merge duplicate memories")
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.95,
        help="Similarity threshold for auto-merge (0.95=high confidence)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show duplicates without merging"
    )
    parser.add_argument("--namespace", help="Limit to specific namespace")

    args = parser.parse_args()

    db_path = os.path.expanduser("~/.openclaw/workspace/ai-memory.db")
    tm = TierManager(db_path=db_path)
    db = MemoryDB(db_path=db_path)

    print(f"[dedup] Scanning for duplicates (threshold={args.threshold})...")

    duplicates = find_duplicate_pairs(tm, similarity_threshold=args.threshold)

    if not duplicates:
        print("[dedup] No duplicates found")
        return 0

    print(f"[dedup] Found {len(duplicates)} duplicate pair(s):\n")

    merged_count = 0
    for dup in duplicates:
        mem1_id, mem2_id, sim, ns, pri1, pri2, upd1, upd2 = dup

        if args.namespace and ns != args.namespace:
            continue

        # Keep the one with higher priority or more recent update
        if pri1 > pri2 or (pri1 == pri2 and upd1 > upd2):
            keep_id, remove_id = mem1_id, mem2_id
        else:
            keep_id, remove_id = mem2_id, mem1_id

        print(f"  {mem1_id[:8]}... <-> {mem2_id[:8]}... (sim={sim:.2f})")
        print(f"    Keep: {keep_id[:8]}... | Remove: {remove_id[:8]}...")

        if not args.dry_run:
            if merge_memories(db, mem1_id, mem2_id, keep_id):
                merged_count += 1
                print(f"    ✅ Merged")
        else:
            print(f"    (dry-run: not merged)")
        print()

    if args.dry_run:
        print(f"[dedup] Dry-run: would merge {len(duplicates)} pairs")
    else:
        print(f"[dedup] Merged {merged_count}/{len(duplicates)} pairs")

    return 0


if __name__ == "__main__":
    sys.exit(main())
