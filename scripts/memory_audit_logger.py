#!/usr/bin/env python3
"""
memory_audit_logger.py — Append-only audit trail for memory modifications.

Logs all memory operations (add, update, delete) with:
- Timestamp (ISO-8601 UTC)
- Operation type (add|update|delete|merge)
- Source (agent:observer|agent:consolidation|user:web|auto:dedup|etc)
- Memory ID + namespace + title
- Content hash (SHA256 of content)
- Diff (for updates)

Format: JSON-lines, one entry per line, rotated daily.
Retention: 90 days by default.
"""

import json
import sys
import os
import hashlib
from datetime import datetime, timezone, timedelta
from pathlib import Path

AUDIT_LOG_DIR = Path.home() / ".openclaw" / "logs" / "memory-audit"
AUDIT_LOG_DIR.mkdir(parents=True, exist_ok=True)

RETENTION_DAYS = 90


def get_audit_log_path():
    """Get today's audit log file path."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return AUDIT_LOG_DIR / f"memory-{today}.jsonl"


def content_hash(content: str) -> str:
    """Generate SHA256 hash of content."""
    return hashlib.sha256(content.encode()).hexdigest()[:12]


def log_operation(
    op: str,
    source: str,
    memory_id: str,
    namespace: str,
    title: str,
    content: str = "",
    old_content: str = "",
    tags: list = None,
    priority: int = 5,
):
    """
    Log a memory modification.

    Args:
        op: Operation type (add|update|delete|merge)
        source: Source identifier (e.g., agent:observer, user:web, auto:dedup)
        memory_id: UUID or identifier of the memory
        namespace: Memory namespace (workspace, personal, projects/*, etc)
        title: Memory title
        content: Current/new content (empty for delete)
        old_content: Previous content (for updates)
        tags: List of tags
        priority: Priority (1-10)
    """
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "op": op,
        "source": source,
        "memory_id": memory_id,
        "namespace": namespace,
        "title": title,
        "hash": content_hash(content) if content else "",
        "old_hash": content_hash(old_content) if old_content else "",
        "tags": tags or [],
        "priority": priority,
    }

    # Add diff for updates (simplified: just show content size change)
    if op == "update" and old_content and content:
        entry["diff"] = {
            "old_size": len(old_content),
            "new_size": len(content),
            "changed_lines": len(
                [
                    l
                    for l, o in zip(content.split("\n"), old_content.split("\n"))
                    if l != o
                ]
            ),
        }

    log_path = get_audit_log_path()
    try:
        with open(log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print(f"[audit-logger:error] Failed to write audit log: {e}", file=sys.stderr)

    # Clean up old logs
    cleanup_old_logs()


def cleanup_old_logs():
    """Remove audit logs older than RETENTION_DAYS."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)
    for log_file in AUDIT_LOG_DIR.glob("memory-*.jsonl"):
        try:
            file_date_str = log_file.stem.split("-", 1)[1]  # memory-YYYY-MM-DD
            file_date = datetime.strptime(file_date_str, "%Y-%m-%d").replace(
                tzinfo=timezone.utc
            )
            if file_date < cutoff:
                log_file.unlink()
        except (ValueError, OSError):
            pass


def get_audit_trail(memory_id: str, since: str = None) -> list:
    """
    Retrieve audit trail for a specific memory.

    Args:
        memory_id: Memory UUID to query
        since: Optional ISO-8601 timestamp to filter from

    Returns:
        List of audit entries for that memory, chronologically ordered
    """
    entries = []
    since_dt = None

    if since:
        try:
            since_dt = datetime.fromisoformat(since)
        except ValueError:
            pass

    for log_file in sorted(AUDIT_LOG_DIR.glob("memory-*.jsonl")):
        try:
            with open(log_file) as f:
                for line in f:
                    if not line.strip():
                        continue
                    entry = json.loads(line)
                    if entry.get("memory_id") == memory_id:
                        if since_dt:
                            entry_dt = datetime.fromisoformat(entry.get("ts", ""))
                            if entry_dt >= since_dt:
                                entries.append(entry)
                        else:
                            entries.append(entry)
        except (json.JSONDecodeError, OSError):
            pass

    return entries


if __name__ == "__main__":
    # Example usage for testing
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            log_operation(
                op="add",
                source="test",
                memory_id="test-uuid-123",
                namespace="workspace",
                title="Test Memory",
                content="Test content here",
                tags=["test"],
            )
            print("[audit-logger] Test entry written")
        elif sys.argv[1] == "--query" and len(sys.argv) > 2:
            entries = get_audit_trail(sys.argv[2])
            for entry in entries:
                print(json.dumps(entry))
