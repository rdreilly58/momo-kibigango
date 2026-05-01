#!/usr/bin/env python3
"""
memory-decay.py — Importance-weighted TTL decay for ai-memory.db

Implements three decay rules:
  1. Archive (→ cold): age > 90d AND priority < 5 AND access_count == 0
  2. Delete:           age > 30d AND priority < 3 AND access_count == 0
  3. Downgrade tier:   age > 180d AND tier == 'short' AND access_count < 2

Runs in --dry-run mode by default. Use --apply to persist changes.
Skips entity nodes (tagged 'entity') and memories with tier='long'.

Usage:
    python3 memory-decay.py              # dry-run (default)
    python3 memory-decay.py --dry-run    # explicit dry-run
    python3 memory-decay.py --apply      # apply changes
    python3 memory-decay.py --apply --verbose

Weekly cron (Sunday 02:00):
    0 2 * * 0 cd ~/.openclaw/workspace && python3 scripts/memory-decay.py --apply >> ~/.openclaw/logs/memory-decay.log 2>&1
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

_SCRIPTS = Path(__file__).parent
sys.path.insert(0, str(_SCRIPTS))

DB_PATH = Path.home() / ".openclaw" / "workspace" / "ai-memory.db"

# Decay thresholds
ARCHIVE_AGE_DAYS   = 90
ARCHIVE_MAX_PRIORITY = 5  # exclusive: < 5
DELETE_AGE_DAYS    = 30
DELETE_MAX_PRIORITY = 3   # exclusive: < 3
DOWNGRADE_AGE_DAYS = 180
DOWNGRADE_MAX_ACCESS = 2  # exclusive: < 2


def _parse_date(s: str) -> datetime:
    """Parse ISO date string to UTC datetime."""
    try:
        # Handle 'Z' suffix and +00:00
        s = s.replace("Z", "+00:00")
        return datetime.fromisoformat(s)
    except Exception:
        # Fallback: assume UTC
        return datetime.now(timezone.utc)


def _age_days(created_at: str) -> float:
    """Return age in days from created_at ISO string to now."""
    now = datetime.now(timezone.utc)
    created = _parse_date(created_at)
    if created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)
    delta = now - created
    return delta.total_seconds() / 86400


def run_decay(
    db_path: Path = DB_PATH,
    dry_run: bool = True,
    verbose: bool = False,
) -> Dict:
    """
    Scan memories and apply (or simulate) decay rules.

    Returns stats dict with counts per action.
    """
    stats = {
        "scanned": 0,
        "archive": [],    # IDs to move to cold
        "delete": [],     # IDs to delete
        "downgrade": [],  # IDs to downgrade tier
        "skipped": 0,
        "applied": dry_run is False,
    }

    with sqlite3.connect(db_path) as con:
        con.row_factory = sqlite3.Row
        rows = con.execute(
            """SELECT id, title, tier, priority, namespace, tags,
                      created_at, access_count
               FROM memories
               ORDER BY created_at ASC"""
        ).fetchall()

    stats["scanned"] = len(rows)

    for row in rows:
        mem_id    = row["id"]
        title     = row["title"] or ""
        tier      = row["tier"] or "short"
        priority  = row["priority"] or 5
        tags_raw  = row["tags"] or "[]"
        created_at = row["created_at"] or ""
        access    = row["access_count"] or 0

        # Parse tags
        try:
            tags = json.loads(tags_raw)
        except Exception:
            tags = []

        # Skip: entity nodes never decay
        if "entity" in tags:
            stats["skipped"] += 1
            continue

        # Skip: long-tier memories survive forever (explicit intention)
        if tier == "long":
            stats["skipped"] += 1
            continue

        age = _age_days(created_at)

        # Rule 1: Delete (highest impact, check first)
        #   age > 30d AND priority < 3 AND access_count == 0
        if age > DELETE_AGE_DAYS and priority < DELETE_MAX_PRIORITY and access == 0:
            reason = f"age={age:.0f}d, priority={priority}, access={access}"
            stats["delete"].append({"id": mem_id, "title": title[:60], "reason": reason})
            if verbose:
                print(f"  [DELETE] {title[:60]} — {reason}")
            continue

        # Rule 2: Archive to cold
        #   age > 90d AND priority < 5 AND access_count == 0
        if age > ARCHIVE_AGE_DAYS and priority < ARCHIVE_MAX_PRIORITY and access == 0:
            reason = f"age={age:.0f}d, priority={priority}, access={access}"
            stats["archive"].append({"id": mem_id, "title": title[:60], "reason": reason})
            if verbose:
                print(f"  [ARCHIVE] {title[:60]} — {reason}")
            continue

        # Rule 3: Downgrade short → working (TTL reset)
        #   age > 180d AND tier == 'short' AND access_count < 2
        if age > DOWNGRADE_AGE_DAYS and tier == "short" and access < DOWNGRADE_MAX_ACCESS:
            reason = f"age={age:.0f}d, tier={tier}, access={access}"
            stats["downgrade"].append({"id": mem_id, "title": title[:60], "reason": reason})
            if verbose:
                print(f"  [DOWNGRADE] {title[:60]} — {reason}")
            continue

    # Summary counts
    n_archive  = len(stats["archive"])
    n_delete   = len(stats["delete"])
    n_downgrade = len(stats["downgrade"])

    print(f"[memory-decay] Scanned {stats['scanned']} memories")
    print(f"  → DELETE  : {n_delete}  (age>{DELETE_AGE_DAYS}d, priority<{DELETE_MAX_PRIORITY}, access=0)")
    print(f"  → ARCHIVE : {n_archive} (age>{ARCHIVE_AGE_DAYS}d, priority<{ARCHIVE_MAX_PRIORITY}, access=0)")
    print(f"  → DOWNGRADE: {n_downgrade} (age>{DOWNGRADE_AGE_DAYS}d, tier=short, access<{DOWNGRADE_MAX_ACCESS})")
    print(f"  → SKIPPED : {stats['skipped']} (entities + long-tier)")

    if dry_run:
        print("[memory-decay] DRY RUN — no changes written. Use --apply to persist.")
        return stats

    # Apply changes
    now_iso = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(db_path) as con:
        # Hard delete low-value memories
        for item in stats["delete"]:
            con.execute("DELETE FROM memories WHERE id=?", (item["id"],))
            print(f"  [DELETED] {item['title'][:60]}")

        # Archive: move to cold store (update tier to 'cold' if supported, else downgrade)
        # ai-memory.db uses working/short/long; cold is handled by memory_cold_store.py
        # Strategy: mark as 'working' with very low priority so they TTL out naturally
        for item in stats["archive"]:
            con.execute(
                "UPDATE memories SET tier='working', priority=1, updated_at=? WHERE id=?",
                (now_iso, item["id"]),
            )
            print(f"  [ARCHIVED→working] {item['title'][:60]}")

        # Downgrade: short → working (shorter TTL)
        for item in stats["downgrade"]:
            con.execute(
                "UPDATE memories SET tier='working', updated_at=? WHERE id=?",
                (now_iso, item["id"]),
            )
            print(f"  [DOWNGRADED→working] {item['title'][:60]}")

        con.commit()

    print(f"[memory-decay] Applied: {n_delete} deleted, {n_archive} archived, {n_downgrade} downgraded")
    return stats


def main():
    ap = argparse.ArgumentParser(description="Importance-weighted memory decay and TTL management")
    ap.add_argument("--dry-run", action="store_true", default=False,
                    help="Show what would change (no writes)")
    ap.add_argument("--apply", action="store_true",
                    help="Actually apply changes to DB")
    ap.add_argument("--verbose", "-v", action="store_true",
                    help="Show each memory decision")
    ap.add_argument("--db", default=str(DB_PATH),
                    help=f"Path to SQLite DB (default: {DB_PATH})")
    args = ap.parse_args()

    dry_run = not args.apply
    if dry_run:
        print("[memory-decay] Mode: DRY RUN (use --apply to persist changes)")
    else:
        print("[memory-decay] Mode: APPLY")

    stats = run_decay(
        db_path=Path(args.db),
        dry_run=dry_run,
        verbose=args.verbose,
    )

    # Print compact summary
    print("\n[summary]")
    print(f"  scanned:   {stats['scanned']}")
    print(f"  delete:    {len(stats['delete'])}")
    print(f"  archive:   {len(stats['archive'])}")
    print(f"  downgrade: {len(stats['downgrade'])}")
    print(f"  skipped:   {stats['skipped']}")


if __name__ == "__main__":
    main()
