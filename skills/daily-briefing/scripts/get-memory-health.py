#!/usr/bin/env python3
"""
get-memory-health.py — Memory system health metrics for daily briefings.

Outputs JSON with two shapes depending on --mode:
  morning:  snapshot (stats, observer status, integrity)
  evening:  activity summary (new today, observations, maintenance run)

Usage:
  python3 get-memory-health.py --mode morning
  python3 get-memory-health.py --mode evening   # also runs expire_ttl + clean_orphaned_links
"""

import argparse
import json
import os
import sqlite3
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

WORKSPACE   = Path.home() / ".openclaw" / "workspace"
DB_PATH     = WORKSPACE / "ai-memory.db"
OBS_FILE    = WORKSPACE / "memory" / "observations.md"
OBS_STAMP   = WORKSPACE / "memory" / ".observer-last-run"
SCRIPTS_DIR = WORKSPACE / "scripts"

sys.path.insert(0, str(SCRIPTS_DIR))


def _db_stats(conn):
    total   = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
    arch    = conn.execute("SELECT COUNT(*) FROM archived_memories").fetchone()[0]
    links   = conn.execute("SELECT COUNT(*) FROM memory_links").fetchone()[0]
    orphans = conn.execute(
        """SELECT COUNT(*) FROM memory_links WHERE
           source_id NOT IN (SELECT id FROM memories)
           OR target_id NOT IN (SELECT id FROM memories)"""
    ).fetchone()[0]
    by_tier = {r[0]: r[1] for r in conn.execute(
        "SELECT tier, COUNT(*) FROM memories GROUP BY tier"
    ).fetchall()}
    by_ns   = {r[0]: r[1] for r in conn.execute(
        "SELECT namespace, COUNT(*) FROM memories GROUP BY namespace"
    ).fetchall()}
    return dict(total=total, archived=arch, links=links,
                orphaned_links=orphans, by_tier=by_tier, by_namespace=by_ns)


def _observer_age_str(stamp_path: Path) -> tuple[str, bool]:
    """Returns (human-readable age string, is_ok bool)."""
    if not stamp_path.exists():
        return "never", False
    try:
        ts = int(stamp_path.read_text().strip())
        age_s = int(time.time()) - ts
        if age_s < 3600:
            return f"{age_s // 60}m ago", True
        if age_s < 86400:
            return f"{age_s // 3600}h ago", True
        return f"{age_s // 86400}d ago", False
    except Exception:
        return "unknown", False


def _obs_count_today(obs_path: Path) -> int:
    """Count observation bullet lines written today."""
    today = datetime.now().strftime("%Y-%m-%d")
    if not obs_path.exists():
        return 0
    count = 0
    in_today = False
    for line in obs_path.read_text().splitlines():
        if today in line:
            in_today = True
        if in_today and line.startswith("- "):
            count += 1
    return count


def _new_memories_today(conn) -> int:
    today = datetime.now(timezone.utc).date().isoformat()
    return conn.execute(
        "SELECT COUNT(*) FROM memories WHERE created_at >= ?", (today,)
    ).fetchone()[0]


def _db_size_kb() -> int:
    if DB_PATH.exists():
        return DB_PATH.stat().st_size // 1024
    return 0


def _status_icon(ok: bool) -> str:
    return "✅" if ok else "⚠️"


def morning_health(conn) -> dict:
    stats        = _db_stats(conn)
    obs_age, obs_ok = _observer_age_str(OBS_STAMP)
    db_kb        = _db_size_kb()
    orphans_ok   = stats["orphaned_links"] == 0

    tier_str = ", ".join(f"{t}: {n}" for t, n in sorted(stats["by_tier"].items()))
    ns_top   = sorted(stats["by_namespace"].items(), key=lambda x: -x[1])[:4]
    ns_str   = ", ".join(f"{n}: {c}" for n, c in ns_top)

    overall_ok = obs_ok and orphans_ok

    html = f"""<div class="section" style="border-left-color:#5cb85c;">
  <h2>🧠 Memory Health</h2>
  <div class="item"><strong>Records:</strong> {stats['total']} ({tier_str})</div>
  <div class="item"><strong>Namespaces:</strong> {ns_str}</div>
  <div class="item"><strong>Observer last run:</strong> {obs_age} {_status_icon(obs_ok)}</div>
  <div class="item"><strong>Orphaned links:</strong> {stats['orphaned_links']} {_status_icon(orphans_ok)}</div>
  <div class="item"><strong>Archived (TTL):</strong> {stats['archived']}</div>
  <div class="item"><strong>DB size:</strong> {db_kb} KB</div>
  <div class="item"><strong>Overall:</strong> {_status_icon(overall_ok)} {'Healthy' if overall_ok else 'Needs attention'}</div>
</div>"""

    return dict(html=html, total=stats["total"], observer_ok=obs_ok,
                observer_age=obs_age, orphaned_links=stats["orphaned_links"],
                db_kb=db_kb, overall_ok=overall_ok)


def evening_health(conn) -> dict:
    stats         = _db_stats(conn)
    new_today     = _new_memories_today(conn)
    obs_count     = _obs_count_today(OBS_FILE)
    obs_age, obs_ok = _observer_age_str(OBS_STAMP)
    db_kb         = _db_size_kb()

    # Run maintenance
    expired_count  = 0
    orphan_cleaned = 0
    try:
        from memory_db import MemoryDB
        db = MemoryDB()
        expired_count  = db.expire_ttl()
        orphan_cleaned = db.clean_orphaned_links()
    except Exception:
        pass

    exp_icon  = _status_icon(expired_count == 0)
    orph_icon = _status_icon(orphan_cleaned == 0)

    html = f"""<div class="section" style="border-left-color:#5cb85c;">
  <h2>🧠 Memory Activity Today</h2>
  <div class="item"><strong>New memories written:</strong> {new_today}</div>
  <div class="item"><strong>Observations logged:</strong> {obs_count}</div>
  <div class="item"><strong>Observer last run:</strong> {obs_age} {_status_icon(obs_ok)}</div>
  <div class="item"><strong>TTL-expired archived:</strong> {expired_count} {exp_icon}</div>
  <div class="item"><strong>Orphaned links cleaned:</strong> {orphan_cleaned} {orph_icon}</div>
  <div class="item"><strong>Total records:</strong> {stats['total']} &nbsp;|&nbsp; DB: {db_kb} KB</div>
</div>"""

    return dict(html=html, new_today=new_today, obs_count=obs_count,
                observer_ok=obs_ok, observer_age=obs_age,
                expired_archived=expired_count, orphans_cleaned=orphan_cleaned,
                total=stats["total"], db_kb=db_kb)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["morning", "evening"], default="morning")
    args = p.parse_args()

    if not DB_PATH.exists():
        print(json.dumps({"html": '<div class="item"><em>ai-memory.db not found</em></div>',
                          "error": "db_missing"}))
        return

    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        data = morning_health(conn) if args.mode == "morning" else evening_health(conn)
        conn.close()
    except Exception as e:
        data = {"html": f'<div class="item"><em>Memory health unavailable: {e}</em></div>',
                "error": str(e)}

    print(json.dumps(data))


if __name__ == "__main__":
    main()
