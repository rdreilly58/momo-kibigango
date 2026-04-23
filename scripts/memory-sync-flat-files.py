#!/usr/bin/env python3
"""
memory-sync-flat-files.py — Bulk-import flat memory/*.md files into tiered system.

Reads all .md files from memory/ and MEMORY.md, chunks them, and stores
each chunk in SQLite + LanceDB warm tier via TierManager.

Skips files already indexed (by checking title hash in SQLite).
Safe to re-run — idempotent via upsert.

Usage:
    python3 memory-sync-flat-files.py [--dry-run] [--force]
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

WORKSPACE = Path.home() / ".openclaw" / "workspace"
MEMORY_DIR = WORKSPACE / "memory"
SCRIPTS_DIR = WORKSPACE / "scripts"

sys.path.insert(0, str(SCRIPTS_DIR))

CHUNK_SIZE = 800  # chars per chunk
CHUNK_OVERLAP = 1  # lines of overlap between chunks


def chunk_text(text: str, source: str) -> list[dict]:
    """Split text into overlapping chunks, returning title + content pairs."""
    lines = text.split("\n")
    chunks: list[dict] = []
    current: list[str] = []
    current_size = 0
    chunk_idx = 0

    for line in lines:
        current.append(line)
        current_size += len(line)
        if current_size >= CHUNK_SIZE:
            chunk_text_val = "\n".join(current)
            chunks.append(
                {
                    "title": f"{source}#{chunk_idx}",
                    "content": chunk_text_val,
                    "source": source,
                }
            )
            current = current[-CHUNK_OVERLAP:] if len(current) > CHUNK_OVERLAP else []
            current_size = sum(len(l) for l in current)
            chunk_idx += 1

    if current:
        chunks.append(
            {
                "title": f"{source}#{chunk_idx}",
                "content": "\n".join(current),
                "source": source,
            }
        )

    return chunks or [{"title": source, "content": text, "source": source}]


def title_hash(title: str) -> str:
    return hashlib.md5(title.encode()).hexdigest()[:16]


def collect_files() -> list[Path]:
    files: list[Path] = []
    top = WORKSPACE / "MEMORY.md"
    if top.exists():
        files.append(top)
    if MEMORY_DIR.exists():
        files.extend(sorted(MEMORY_DIR.glob("*.md")))
    return files


def main() -> int:
    ap = argparse.ArgumentParser(description="Sync flat memory files into tiered store")
    ap.add_argument("--dry-run", action="store_true", help="Show what would be indexed")
    ap.add_argument(
        "--force", action="store_true", help="Re-index even if already present"
    )
    args = ap.parse_args()

    import sqlite3 as _sqlite3

    from memory_tier_manager import TierManager

    mgr = TierManager()
    db_path = WORKSPACE / "ai-memory.db"

    def title_exists(title: str) -> bool:
        with _sqlite3.connect(db_path) as con:
            row = con.execute(
                "SELECT 1 FROM memories WHERE title=? LIMIT 1", (title,)
            ).fetchone()
            return row is not None

    files = collect_files()
    print(f"Found {len(files)} memory files to sync")

    total_stored = 0
    total_skipped = 0
    total_chunks = 0

    for filepath in files:
        try:
            content = filepath.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            print(f"  SKIP (read error): {filepath.name} — {e}")
            continue

        rel = str(filepath.relative_to(WORKSPACE))
        chunks = chunk_text(content, rel)
        total_chunks += len(chunks)

        for chunk in chunks:
            title = chunk["title"]
            chunk_content = chunk["content"].strip()
            if not chunk_content:
                continue

            # Check if already indexed by exact title match
            if not args.force and title_exists(title):
                total_skipped += 1
                continue

            if args.dry_run:
                print(f"  WOULD store: {title} ({len(chunk_content)} chars)")
                total_stored += 1
                continue

            try:
                mgr.store(
                    title=title,
                    content=chunk_content,
                    namespace="memory-files",
                    tier="short",
                    tags=[rel.split("/")[-1].replace(".md", "")],
                    priority=6,
                )
                total_stored += 1
            except Exception as e:
                print(f"  ERROR storing {title}: {e}")

        print(f"  {rel}: {len(chunks)} chunks → {total_stored} stored so far")

    print(f"\nSync complete:")
    print(f"  Files processed: {len(files)}")
    print(f"  Total chunks:    {total_chunks}")
    print(f"  Stored:          {total_stored}")
    print(f"  Skipped (dup):   {total_skipped}")

    if not args.dry_run and total_stored > 0:
        print("\nRebuilding warm index...")
        n = mgr.rebuild_warm_index()
        print(f"  Warm index: {n} records synced")

    return 0


if __name__ == "__main__":
    sys.exit(main())
