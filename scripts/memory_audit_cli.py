#!/usr/bin/env python3
"""
memory_audit_cli.py — Query and analyze memory audit logs.

Usage:
  memory_audit_cli.py --memory-id <id> [--since <ISO-8601>]
  memory_audit_cli.py --namespace <ns> [--since <ISO-8601>]
  memory_audit_cli.py --recent [--days <N>]
  memory_audit_cli.py --stats
"""

import json
import sys
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path
from collections import defaultdict

AUDIT_LOG_DIR = Path.home() / ".openclaw" / "logs" / "memory-audit"


def load_entries(days: int = 90) -> list:
    """Load audit entries from the last N days."""
    entries = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    for log_file in sorted(AUDIT_LOG_DIR.glob("memory-*.jsonl")):
        try:
            with open(log_file) as f:
                for line in f:
                    if not line.strip():
                        continue
                    entry = json.loads(line)
                    entry_dt = datetime.fromisoformat(entry.get("ts", ""))
                    if entry_dt >= cutoff:
                        entries.append(entry)
        except (json.JSONDecodeError, OSError):
            pass

    return sorted(entries, key=lambda e: e.get("ts", ""))


def query_memory_id(memory_id: str, since: str = None) -> list:
    """Get audit trail for a specific memory ID."""
    entries = load_entries()
    since_dt = None

    if since:
        try:
            since_dt = datetime.fromisoformat(since)
        except ValueError:
            pass

    result = []
    for entry in entries:
        if entry.get("memory_id") == memory_id:
            if since_dt:
                entry_dt = datetime.fromisoformat(entry.get("ts", ""))
                if entry_dt >= since_dt:
                    result.append(entry)
            else:
                result.append(entry)

    return result


def query_namespace(namespace: str, since: str = None) -> list:
    """Get all audit entries for a namespace."""
    entries = load_entries()
    since_dt = None

    if since:
        try:
            since_dt = datetime.fromisoformat(since)
        except ValueError:
            pass

    result = []
    for entry in entries:
        if entry.get("namespace") == namespace:
            if since_dt:
                entry_dt = datetime.fromisoformat(entry.get("ts", ""))
                if entry_dt >= since_dt:
                    result.append(entry)
            else:
                result.append(entry)

    return result


def get_recent(days: int = 1) -> list:
    """Get recent audit entries from the last N days."""
    return load_entries(days=days)


def get_stats() -> dict:
    """Get overall audit statistics."""
    entries = load_entries(days=90)

    stats = {
        "total_entries": len(entries),
        "by_operation": defaultdict(int),
        "by_source": defaultdict(int),
        "by_namespace": defaultdict(int),
        "date_range": {
            "earliest": min((e.get("ts") for e in entries), default=""),
            "latest": max((e.get("ts") for e in entries), default=""),
        },
    }

    for entry in entries:
        stats["by_operation"][entry.get("op", "unknown")] += 1
        stats["by_source"][entry.get("source", "unknown")] += 1
        stats["by_namespace"][entry.get("namespace", "unknown")] += 1

    # Convert defaultdicts to regular dicts for JSON serialization
    stats["by_operation"] = dict(stats["by_operation"])
    stats["by_source"] = dict(stats["by_source"])
    stats["by_namespace"] = dict(stats["by_namespace"])

    return stats


def format_entry(entry: dict, verbose: bool = False) -> str:
    """Format an audit entry for display."""
    ts = entry.get("ts", "")[:16]  # ISO timestamp, no microseconds
    op = entry.get("op", "?").ljust(6)
    source = entry.get("source", "?")
    title = entry.get("title", "?")[:40]

    if verbose:
        return f"{ts} | {op} | {source:20} | {title}\n  ID: {entry.get('memory_id')}\n  Hash: {entry.get('hash')}"
    else:
        return f"{ts} | {op} | {source:20} | {title}"


def main():
    parser = argparse.ArgumentParser(description="Query memory audit logs")
    parser.add_argument("--memory-id", help="Query by memory ID")
    parser.add_argument("--namespace", help="Query by namespace")
    parser.add_argument("--recent", action="store_true", help="Get recent entries")
    parser.add_argument(
        "--days", type=int, default=1, help="For --recent, how many days"
    )
    parser.add_argument("--since", help="ISO-8601 timestamp to filter from")
    parser.add_argument("--stats", action="store_true", help="Get audit statistics")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if not AUDIT_LOG_DIR.exists():
        print("No audit logs found.", file=sys.stderr)
        sys.exit(1)

    if args.memory_id:
        entries = query_memory_id(args.memory_id, since=args.since)
    elif args.namespace:
        entries = query_namespace(args.namespace, since=args.since)
    elif args.recent:
        entries = get_recent(days=args.days)
    elif args.stats:
        stats = get_stats()
        print(json.dumps(stats, indent=2))
        return
    else:
        parser.print_help()
        sys.exit(1)

    if not entries:
        print("No entries found.", file=sys.stderr)
        sys.exit(0)

    print(f"\n{'Time':<17} | {'Op':<6} | {'Source':<20} | Title")
    print("-" * 80)
    for entry in entries:
        print(format_entry(entry, verbose=args.verbose))

    print(f"\nTotal: {len(entries)} entries\n")


if __name__ == "__main__":
    main()
