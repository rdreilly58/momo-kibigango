#!/usr/bin/env python3
"""
memory-auto-promote.py — Promote short-tier memories to long tier automatically.

Promotion criteria (any one triggers):
  1. priority >= 7
  2. access_count >= 3
  3. Tags contain any of: decision, config, lesson, important, long-term

Usage:
    python3 memory-auto-promote.py           # Dry run (show what would be promoted)
    python3 memory-auto-promote.py --commit  # Actually promote
    python3 memory-auto-promote.py --ns workspace  # Limit to one namespace
    python3 memory-auto-promote.py --priority-min 7  # Custom threshold

The script logs all promotions. Run periodically (weekly or via cron).
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path.home() / ".openclaw" / "workspace"
SCRIPTS_DIR = WORKSPACE / "scripts"
DB_PATH = WORKSPACE / "ai-memory.db"

# Tags that trigger promotion regardless of priority/access_count
PROMO_TAGS = {"decision", "config", "lesson", "important", "long-term", "longterm", "permanent"}

# Promotion criteria
DEFAULT_PRIORITY_MIN = 7
DEFAULT_ACCESS_MIN = 3


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def find_candidates(
    db_path: Path,
    priority_min: int = DEFAULT_PRIORITY_MIN,
    access_min: int = DEFAULT_ACCESS_MIN,
    namespace: str | None = None,
) -> list[dict]:
    """Query SQLite for short-tier memories meeting any promotion criterion."""
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        query = """
            SELECT id, title, namespace, tier, priority, tags, access_count
            FROM memories
            WHERE tier IN ('short', 'working')
        """
        params: list = []
        if namespace:
            query += " AND namespace = ?"
            params.append(namespace)
        query += " ORDER BY priority DESC, access_count DESC"
        rows = conn.execute(query, params).fetchall()

    candidates = []
    for row in rows:
        r = dict(row)
        reasons = []

        if r["priority"] >= priority_min:
            reasons.append(f"priority={r['priority']} >= {priority_min}")

        if r["access_count"] >= access_min:
            reasons.append(f"access_count={r['access_count']} >= {access_min}")

        # Parse tags — stored as JSON array string
        try:
            tags = set(json.loads(r["tags"] or "[]"))
        except (json.JSONDecodeError, TypeError):
            tags = set()

        matching_tags = tags & PROMO_TAGS
        if matching_tags:
            reasons.append(f"tags={matching_tags}")

        if reasons:
            r["_reasons"] = reasons
            r["_tags"] = list(tags)
            candidates.append(r)

    return candidates


def promote(db_path: Path, memory_id: str) -> bool:
    """Update tier to 'long' in SQLite."""
    with sqlite3.connect(db_path) as conn:
        updated_at = _now()
        cur = conn.execute(
            "UPDATE memories SET tier = 'long', updated_at = ? WHERE id = ?",
            (updated_at, memory_id),
        )
        return cur.rowcount > 0


def main():
    p = argparse.ArgumentParser(description="Auto-promote short memories to long tier")
    p.add_argument("--commit", action="store_true", help="Actually promote (default: dry run)")
    p.add_argument("--ns", "--namespace", help="Limit to namespace")
    p.add_argument("--priority-min", type=int, default=DEFAULT_PRIORITY_MIN)
    p.add_argument("--access-min", type=int, default=DEFAULT_ACCESS_MIN)
    args = p.parse_args()

    candidates = find_candidates(
        DB_PATH,
        priority_min=args.priority_min,
        access_min=args.access_min,
        namespace=args.ns,
    )

    if not candidates:
        print("✅ No memories meet promotion criteria.")
        return

    mode = "COMMIT" if args.commit else "DRY RUN"
    print(f"Memory auto-promote [{mode}] — {len(candidates)} candidate(s):\n")

    promoted = 0
    skipped = 0
    errors = []

    for c in candidates:
        reasons_str = "; ".join(c["_reasons"])
        title_short = c["title"][:60] + ("…" if len(c["title"]) > 60 else "")
        print(f"  [{c['namespace']}] {title_short}")
        print(f"    tier: {c['tier']} → long | {reasons_str}")

        if args.commit:
            try:
                ok = promote(DB_PATH, c["id"])
                if ok:
                    promoted += 1
                    print(f"    ✅ Promoted")
                else:
                    skipped += 1
                    print(f"    ⚠️  No rows updated (already gone?)")
            except Exception as e:
                errors.append(f"{c['id']}: {e}")
                print(f"    ❌ Error: {e}")
        else:
            print(f"    (dry run — no change)")

    print()
    if args.commit:
        print(f"Promoted: {promoted} | Skipped: {skipped} | Errors: {len(errors)}")
        if errors:
            print("Errors:", errors)
        if promoted > 0:
            print()
            print("ℹ️  LanceDB warm index still shows these as 'warm' tier (tier field in Lance")
            print("   is separate from SQLite tier). Run `memory_tier_manager.py rebuild` if")
            print("   you want Lance to reflect the updated tier metadata.")
            # Update entity graph for newly promoted memories
            print()
            print("🔗 Updating entity graph for promoted memories...")
            import subprocess
            graph_script = SCRIPTS_DIR / "memory-graph-activate.py"
            result = subprocess.run(
                [sys.executable, str(graph_script), "--apply"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                print(result.stdout.strip())
            else:
                print(f"⚠️  Graph update warning: {result.stderr[:200]}")
    else:
        print(f"[Dry run] Would promote {len(candidates)} memories.")
        print("Run with --commit to apply.")


if __name__ == "__main__":
    main()
