#!/usr/bin/env python3
"""
memory-index-filter.py — Remove junk/empty daily memory files from the LanceDB index.

Daily files under 500 bytes are bare templates with no real content.
They pollute the vector index with noise chunks.

Usage:
    python3 memory-index-filter.py           # Report mode (dry run)
    python3 memory-index-filter.py --clean   # Remove from LanceDB index (not files!)
    python3 memory-index-filter.py --threshold 500  # Custom byte threshold

The files are NOT deleted from disk — only de-indexed from LanceDB warm store.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

WORKSPACE = Path.home() / ".openclaw" / "workspace"
MEMORY_DIR = WORKSPACE / "memory"
SCRIPTS_DIR = WORKSPACE / "scripts"
DEFAULT_THRESHOLD = 500  # bytes


def find_tiny_files(threshold: int) -> list[Path]:
    """Return memory/YYYY-MM-DD*.md files smaller than threshold bytes."""
    tiny = []
    if not MEMORY_DIR.exists():
        return tiny
    for path in sorted(MEMORY_DIR.rglob("*.md")):
        try:
            size = path.stat().st_size
        except OSError:
            continue
        if size < threshold:
            tiny.append(path)
    return tiny


def remove_from_index(tiny_files: list[Path], memory_dir: Path) -> dict:
    """
    Remove entries for tiny files from the LanceDB warm store.

    Memory chunks are indexed with titles like 'memory/2026-04-19.md#0'.
    We delete all SQLite memories matching those paths, then remove them
    from LanceDB via _stable_int_id on their UUIDs.
    """
    if str(SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPTS_DIR))

    from memory_db import MemoryDB
    from memory_lance_store import LanceWarmStore, _stable_int_id

    db = MemoryDB(db_path=WORKSPACE / "ai-memory.db")
    warm = LanceWarmStore(db_path=WORKSPACE / "lance_memory")

    removed_from_sqlite = 0
    removed_from_lance = 0
    errors = []

    for path in tiny_files:
        # relative path from workspace (e.g. "memory/2026-04-19.md")
        try:
            rel = path.relative_to(WORKSPACE)
        except ValueError:
            rel = path.name

        rel_str = str(rel)

        # Find all SQLite memories whose title starts with this path prefix
        import sqlite3
        with sqlite3.connect(WORKSPACE / "ai-memory.db") as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute(
                "SELECT id FROM memories WHERE title LIKE ? AND namespace = 'memory-files'",
                (f"{rel_str}%",)
            )
            rows = cur.fetchall()

        for row in rows:
            mem_id = row["id"]
            int_id = _stable_int_id(mem_id)
            try:
                warm.delete(int_id)
                removed_from_lance += 1
            except Exception as e:
                errors.append(f"LanceDB delete {mem_id}: {e}")
            try:
                db.delete(mem_id)
                removed_from_sqlite += 1
            except Exception as e:
                errors.append(f"SQLite delete {mem_id}: {e}")

    return {
        "removed_from_sqlite": removed_from_sqlite,
        "removed_from_lance": removed_from_lance,
        "errors": errors,
    }


def main():
    p = argparse.ArgumentParser(description="Filter empty/junk memory files from LanceDB index")
    p.add_argument("--clean", action="store_true", help="Remove from index (default: report only)")
    p.add_argument("--threshold", type=int, default=DEFAULT_THRESHOLD,
                   help=f"Byte threshold (default {DEFAULT_THRESHOLD})")
    args = p.parse_args()

    tiny = find_tiny_files(args.threshold)

    print(f"Memory index filter — threshold: {args.threshold} bytes")
    print(f"Scanning: {MEMORY_DIR}")
    print()

    if not tiny:
        print("✅ No files below threshold found. Index is clean.")
        return

    total_bytes = sum(f.stat().st_size for f in tiny)
    print(f"Found {len(tiny)} file(s) below {args.threshold} bytes ({total_bytes} bytes total):")
    for f in tiny:
        size = f.stat().st_size
        print(f"  {size:5d}B  {f.relative_to(WORKSPACE)}")

    if not args.clean:
        print()
        print("ℹ️  Report mode — no changes made.")
        print("   Run with --clean to remove these from the LanceDB index (files kept on disk).")
        return

    print()
    print("🧹 Removing from LanceDB index...")
    result = remove_from_index(tiny, MEMORY_DIR)
    print(f"  SQLite records removed: {result['removed_from_sqlite']}")
    print(f"  LanceDB entries removed: {result['removed_from_lance']}")
    if result["errors"]:
        print(f"  ⚠️  Errors ({len(result['errors'])}):")
        for e in result["errors"]:
            print(f"    {e}")
    else:
        print("✅ Done — no errors.")


if __name__ == "__main__":
    main()
