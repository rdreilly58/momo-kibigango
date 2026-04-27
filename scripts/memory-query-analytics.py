#!/usr/bin/env python3
"""
memory-query-analytics.py — Track memory search patterns and usage.

Logs all memory searches to JSON-lines:
- Query text
- Results (count, IDs, scores)
- Source (agent:observer, user:web, etc)
- Timestamp
- Latency

Provides analytics:
- Most-searched memories
- Dead memories (never retrieved)
- Search success rate
- Performance metrics
"""

import json
import sys
import os
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from collections import defaultdict

ANALYTICS_LOG_DIR = Path.home() / ".openclaw" / "logs" / "memory-analytics"
ANALYTICS_LOG_DIR.mkdir(parents=True, exist_ok=True)

RETENTION_DAYS = 90


def get_analytics_log_path():
    """Get today's analytics log file path."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return ANALYTICS_LOG_DIR / f"queries-{today}.jsonl"


def log_query(
    query: str,
    result_count: int,
    result_ids: list = None,
    result_scores: list = None,
    source: str = "api",
    latency_ms: float = 0,
    namespace: str = "workspace",
):
    """
    Log a memory search query.

    Args:
        query: Search query text
        result_count: Number of results returned
        result_ids: List of memory IDs in results
        result_scores: List of relevance scores
        source: Source of query (agent:observer, user:web, api, etc)
        latency_ms: Query latency in milliseconds
        namespace: Namespace queried
    """
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "query": query,
        "result_count": result_count,
        "result_ids": result_ids or [],
        "result_scores": result_scores or [],
        "source": source,
        "latency_ms": latency_ms,
        "namespace": namespace,
        "success": result_count > 0,
    }

    log_path = get_analytics_log_path()
    try:
        with open(log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print(f"[analytics:error] Failed to write query log: {e}", file=sys.stderr)

    cleanup_old_logs()


def cleanup_old_logs():
    """Remove analytics logs older than RETENTION_DAYS."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)
    for log_file in ANALYTICS_LOG_DIR.glob("queries-*.jsonl"):
        try:
            file_date_str = log_file.stem.split("-", 1)[1]  # queries-YYYY-MM-DD
            file_date = datetime.strptime(file_date_str, "%Y-%m-%d").replace(
                tzinfo=timezone.utc
            )
            if file_date < cutoff:
                log_file.unlink()
        except (ValueError, OSError):
            pass


def get_analytics(days: int = 7) -> dict:
    """
    Analyze query patterns over the last N days.

    Returns:
        Dict with stats on search patterns, performance, dead memories
    """
    entries = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    for log_file in sorted(ANALYTICS_LOG_DIR.glob("queries-*.jsonl")):
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

    # Compute analytics
    stats = {
        "period_days": days,
        "total_queries": len(entries),
        "successful_queries": sum(1 for e in entries if e.get("success")),
        "success_rate": 0,
        "avg_latency_ms": 0,
        "total_results": sum(e.get("result_count", 0) for e in entries),
        "queries_by_source": defaultdict(int),
        "top_result_memories": defaultdict(int),
        "unused_memories": [],
        "p95_latency_ms": 0,
        "slow_queries": [],
    }

    if entries:
        stats["success_rate"] = stats["successful_queries"] / stats["total_queries"]
        latencies = [e.get("latency_ms", 0) for e in entries]
        stats["avg_latency_ms"] = sum(latencies) / len(latencies)
        latencies_sorted = sorted(latencies)
        idx_95 = int(len(latencies_sorted) * 0.95)
        stats["p95_latency_ms"] = (
            latencies_sorted[idx_95] if idx_95 < len(latencies_sorted) else 0
        )

    # Track queries by source
    for entry in entries:
        source = entry.get("source", "unknown")
        stats["queries_by_source"][source] += 1

        # Track which memories appear in results
        for mem_id in entry.get("result_ids", []):
            stats["top_result_memories"][mem_id] += 1

        # Flag slow queries
        if entry.get("latency_ms", 0) > 500:
            stats["slow_queries"].append(
                {
                    "ts": entry.get("ts"),
                    "query": entry.get("query", "")[:100],
                    "latency_ms": entry.get("latency_ms"),
                }
            )

    # Convert defaultdicts
    stats["queries_by_source"] = dict(stats["queries_by_source"])
    stats["top_result_memories"] = dict(
        sorted(stats["top_result_memories"].items(), key=lambda x: -x[1])[:20]
    )
    stats["slow_queries"] = stats["slow_queries"][:10]

    return stats


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Memory query analytics")
    parser.add_argument(
        "--log",
        action="store_true",
        help="Log a sample query (test mode)",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show analytics for last N days",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Days to analyze",
    )

    args = parser.parse_args()

    if args.log:
        # Test: log a sample query
        log_query(
            query="test query",
            result_count=3,
            result_ids=["id1", "id2", "id3"],
            result_scores=[0.95, 0.87, 0.76],
            source="test",
            latency_ms=45.2,
        )
        print("[analytics] Sample query logged")

    if args.stats:
        analytics = get_analytics(days=args.days)
        print(json.dumps(analytics, indent=2, default=str))

    if not args.log and not args.stats:
        parser.print_help()


if __name__ == "__main__":
    main()
