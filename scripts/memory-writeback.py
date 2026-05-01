#!/usr/bin/env python3
"""
memory-writeback.py — Phase 2 cross-agent memory: subagent write-back via QMD.

Provides two things:
  1. A structured write-back helper that subagents call to record findings
     into today's memory log (auto-indexed by QMD within 60 seconds).
  2. A QMD-backed search wrapper for live memory queries inside subagents.

Usage (write-back):
    python3 memory-writeback.py write --title "Key finding" --content "..." [--tags decision,config]

Usage (search inside subagent):
    python3 memory-writeback.py search "anthropic spend check" [--limit 5]

Usage (status):
    python3 memory-writeback.py status

Design notes:
    - QMD interval is set to 60s (Phase 2 config). Writes surface to parent in ~1 min.
    - Falls back to direct file append when QMD is unavailable.
    - Search uses `qmd search` CLI if QMD is running, otherwise total_recall_search.py.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, date
from pathlib import Path

WORKSPACE = Path(os.environ.get("OPENCLAW_WORKSPACE", Path.home() / ".openclaw" / "workspace"))
MEMORY_DIR = WORKSPACE / "memory"
TODAY_FILE = MEMORY_DIR / f"{date.today().isoformat()}.md"

# QMD collections (match openclaw config)
QMD_COLLECTIONS = ["memory-root-main", "memory-dir-main"]


# ---------------------------------------------------------------------------
# Write-back
# ---------------------------------------------------------------------------

def write_back(title: str, content: str, tags: list[str] = None, priority: int = 5) -> dict:
    """
    Write a finding back to today's memory log.
    QMD will auto-index within ~60 seconds.
    """
    MEMORY_DIR.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    tags_str = f" [{', '.join(tags)}]" if tags else ""

    entry = f"\n## [SUBAGENT FINDING — {ts}]{tags_str}\n**{title}**\n\n{content}\n"

    with open(TODAY_FILE, "a") as f:
        f.write(entry)

    return {
        "status": "written",
        "file": str(TODAY_FILE),
        "title": title,
        "chars": len(entry),
        "note": "QMD will auto-index within ~60 seconds",
    }


# ---------------------------------------------------------------------------
# Search (QMD-backed with fallback)
# ---------------------------------------------------------------------------

def search(query: str, limit: int = 5) -> list[dict]:
    """
    Search memory using QMD CLI if available, else fall back to total_recall_search.
    """
    # Try QMD first
    try:
        args = ["qmd", "search", query, "--json", f"-n{limit}"]
        for c in QMD_COLLECTIONS:
            args += ["-c", c]
        r = subprocess.run(args, capture_output=True, text=True, timeout=10)
        if r.returncode == 0:
            data = json.loads(r.stdout)
            results = data if isinstance(data, list) else data.get("results", [])
            return [{"source": "qmd", **item} for item in results[:limit]]
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError):
        pass

    # Fallback: total_recall_search
    try:
        r = subprocess.run(
            [sys.executable, str(WORKSPACE / "scripts" / "total_recall_search.py"),
             query, "--json", "--limit", str(limit)],
            capture_output=True, text=True, timeout=30
        )
        if r.returncode == 0:
            data = json.loads(r.stdout)
            return [{"source": "total_recall_search", **item} for item in data]
    except (subprocess.TimeoutExpired, json.JSONDecodeError):
        pass

    return []


# ---------------------------------------------------------------------------
# Status
# ---------------------------------------------------------------------------

def status() -> dict:
    """Report write-back and QMD status."""
    # QMD available?
    qmd_ok = subprocess.run(["which", "qmd"], capture_output=True).returncode == 0

    # Today's memory file
    today_exists = TODAY_FILE.exists()
    today_size = TODAY_FILE.stat().st_size if today_exists else 0

    # Count subagent entries in today's file
    subagent_entries = 0
    if today_exists:
        content = TODAY_FILE.read_text(errors="replace")
        subagent_entries = content.count("[SUBAGENT FINDING")

    return {
        "qmd_available": qmd_ok,
        "today_file": str(TODAY_FILE),
        "today_exists": today_exists,
        "today_size_bytes": today_size,
        "subagent_entries_today": subagent_entries,
        "qmd_update_interval": "60s (Phase 2 config)",
        "collections": QMD_COLLECTIONS,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Subagent memory write-back and search (Phase 2)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # write
    w = sub.add_parser("write", help="Write a finding back to memory")
    w.add_argument("--title", required=True, help="Short title for the finding")
    w.add_argument("--content", required=True, help="Full content of the finding")
    w.add_argument("--tags", default="", help="Comma-separated tags (e.g. decision,config)")
    w.add_argument("--priority", type=int, default=5, help="Priority 1-10 (default 5)")

    # search
    s = sub.add_parser("search", help="Search memory (QMD or fallback)")
    s.add_argument("query", help="Search query")
    s.add_argument("--limit", type=int, default=5, help="Max results (default 5)")
    s.add_argument("--json", action="store_true", dest="as_json", help="Output as JSON")

    # status
    sub.add_parser("status", help="Show write-back and QMD status")

    args = parser.parse_args()

    if args.cmd == "write":
        tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []
        result = write_back(args.title, args.content, tags=tags, priority=args.priority)
        print(json.dumps(result, indent=2))

    elif args.cmd == "search":
        results = search(args.query, limit=args.limit)
        if args.as_json:
            print(json.dumps(results, indent=2))
        else:
            print(f"Found {len(results)} results for: {args.query!r}")
            for i, r in enumerate(results, 1):
                title = r.get("title") or r.get("path") or "?"
                snippet = (r.get("snippet") or r.get("content") or "")[:120]
                print(f"  [{i}] {title}")
                print(f"       {snippet}")

    elif args.cmd == "status":
        s = status()
        print(json.dumps(s, indent=2))


if __name__ == "__main__":
    main()
