#!/usr/bin/env python3
"""
memory-graph-activate.py — Bulk-activate entity graph from existing memories.

Extracts entities (people, projects, tools, companies, decisions) from all
stored memories using pattern matching, creates entity nodes, and wires graph
edges between co-occurring entities.

Does NOT call the Haiku API — uses fast regex/keyword extraction for bulk runs.
Use memory_graph.py extract --memory-id <id> (Haiku-based) for richer new memories.

Usage:
    python3 memory-graph-activate.py [--dry-run] [--verbose] [--limit N]
    python3 memory-graph-activate.py --apply
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Set, Tuple

_SCRIPTS = Path(__file__).parent
sys.path.insert(0, str(_SCRIPTS))
from memory_db import MemoryDB  # noqa: E402

# ── Entity pattern registry ─────────────────────────────────────────────────

# People: "Bob", "Robert Reilly", "Claude", etc. — capitalized names
_RE_PEOPLE = re.compile(r"\b(Bob|Robert(?: Reilly)?|Claude|Anthropic|Momotaro|Haiku|Sonnet|Opus)\b")

# Tools / CLIs
_RE_TOOLS = re.compile(
    r"\b(OpenClaw|openclaw|Things|Obsidian|Bear|Telegram|Slack|Discord|Zoom|"
    r"Tailscale|tmux|git|GitHub|AWS|EC2|S3|Leidos|Peraton|"
    r"LanceDB|SQLite|FTS5|Haiku|Claude|Anthropic|Google|Colab|"
    r"apple-calendar-cli|gog|himalaya|total-recall-search|"
    r"memory_graph|memory_db|memory_mcp_server|"
    r"MLX|PyTorch|Python|Node\.js|JavaScript|Swift|Rust|TypeScript|"
    r"npm|pip|brew|Homebrew|macOS|iOS|Xcode|"
    r"Vercel|Cloudflare|Tailwind|Next\.js|React|"
    r"ElevenLabs|Whisper|MCP|1Password)\b",
    re.IGNORECASE,
)

# Projects (camelCase, dash-case identifiers)
_RE_PROJECTS = re.compile(
    r"\b(momo-kibigango|momo-kioku|momo-akira|OnigashimaDashboard|"
    r"reillydesignstudio|ai-memory|memory-palace|total-recall|"
    r"briefing-agent|daily-briefing|auto-flush|pre-reboot-quit)\b",
    re.IGNORECASE,
)

# Companies
_RE_COMPANIES = re.compile(
    r"\b(Leidos|Peraton|Anthropic|Google|Apple|OpenAI|OpenRouter|"
    r"Amazon|Microsoft|GitHub|Vercel|Cloudflare|ElevenLabs|Tailscale)\b"
)

# File paths → extract basename
_RE_FILES = re.compile(r"([\w\-]+\.(?:py|md|sh|json|yaml|yml|ts|js|swift))\b")

# Namespaced entity detection from title
_RE_ENTITY_TITLE = re.compile(r"^ENTITY:(.+)$")

ENTITY_TYPE_MAP = {
    "Bob": "person", "Robert Reilly": "person", "Momotaro": "person",
    "Claude": "tool", "Haiku": "tool", "Sonnet": "tool", "Opus": "tool",
    "Anthropic": "company",
    "OpenClaw": "tool", "Things": "tool", "Obsidian": "tool",
    "Bear": "tool", "Telegram": "tool", "Slack": "tool",
    "Discord": "tool", "Zoom": "tool", "Tailscale": "tool",
    "tmux": "tool", "git": "tool", "GitHub": "tool",
    "AWS": "tool", "EC2": "tool", "S3": "tool",
    "LanceDB": "tool", "SQLite": "tool", "FTS5": "tool",
    "Google": "company", "Apple": "company", "OpenAI": "company",
    "OpenRouter": "company", "Amazon": "company", "Microsoft": "company",
    "Vercel": "company", "Cloudflare": "company", "ElevenLabs": "company",
    "Leidos": "company", "Peraton": "company",
    "MLX": "tool", "Python": "tool", "Node.js": "tool",
    "MCP": "tool", "1Password": "tool",
    "momo-kibigango": "project", "momo-kioku": "project",
    "momo-akira": "project", "OnigashimaDashboard": "project",
    "reillydesignstudio": "project", "ai-memory": "project",
    "total-recall": "project", "daily-briefing": "project",
}


def extract_entities_from_text(title: str, content: str) -> Dict[str, str]:
    """Extract {entity_name: entity_type} from title+content."""
    text = f"{title} {content}"
    found: Dict[str, str] = {}

    # Skip if this IS an entity node itself
    if _RE_ENTITY_TITLE.match(title):
        return found

    for pat, default_type in [
        (_RE_PEOPLE, "person"),
        (_RE_TOOLS, "tool"),
        (_RE_PROJECTS, "project"),
        (_RE_COMPANIES, "company"),
    ]:
        for m in pat.finditer(text):
            name = m.group(0)
            # Normalize common variants
            norm = {"Robert Reilly": "Bob", "robert reilly": "Bob",
                    "openclaw": "OpenClaw", "github": "GitHub",
                    "node.js": "Node.js"}.get(name.lower(), name)
            etype = ENTITY_TYPE_MAP.get(norm, ENTITY_TYPE_MAP.get(name, default_type))
            found[norm] = etype

    # File entities from content (limit to .py, .md, .sh)
    for m in _RE_FILES.finditer(content):
        fname = m.group(1)
        if len(fname) > 3:  # skip tiny ones
            found[fname] = "file"

    return found


def bulk_activate_graph(
    db: MemoryDB,
    dry_run: bool = True,
    verbose: bool = False,
    limit: int = None,
) -> Dict:
    """Main bulk activation routine."""
    stats = {
        "memories_scanned": 0,
        "entities_found": 0,
        "entities_created": 0,
        "entities_updated": 0,
        "edges_created": 0,
        "edges_skipped": 0,
    }

    # Load all non-working memories
    with sqlite3.connect(db.db_path) as con:
        con.row_factory = sqlite3.Row
        query = "SELECT id, title, content, namespace, tags FROM memories WHERE tier IN ('short','long') ORDER BY updated_at DESC"
        if limit:
            query += f" LIMIT {limit}"
        memories = [dict(r) for r in con.execute(query).fetchall()]

    stats["memories_scanned"] = len(memories)
    print(f"[graph-activate] Scanning {len(memories)} memories...")

    # Per-memory entity extraction
    memory_entities: Dict[str, Dict[str, str]] = {}  # mem_id → {name: type}
    all_entities: Dict[str, str] = {}  # name → type (union)

    for mem in memories:
        entities = extract_entities_from_text(mem["title"], mem["content"])
        if entities:
            memory_entities[mem["id"]] = entities
            all_entities.update(entities)
            if verbose:
                print(f"  [{mem['id'][:8]}] {mem['title'][:50]} → {list(entities.keys())[:5]}")

    stats["entities_found"] = len(all_entities)
    print(f"[graph-activate] Found {len(all_entities)} unique entities across all memories")

    if dry_run:
        print("[graph-activate] DRY RUN — no changes written")
        # Count what edges would be created
        edge_count = 0
        entity_pairs: Set[Tuple[str, str]] = set()
        for mem_id, entities in memory_entities.items():
            names = list(entities.keys())
            for i in range(len(names)):
                for j in range(i + 1, len(names)):
                    a, b = sorted([names[i], names[j]])
                    if (a, b) not in entity_pairs:
                        entity_pairs.add((a, b))
                        edge_count += 1
        stats["edges_created"] = edge_count
        print(f"[graph-activate] Would create {len(all_entities)} entities, {edge_count} edges")
        return stats

    # Apply: upsert entity nodes
    name_to_id: Dict[str, str] = {}

    # Load existing entities first
    with sqlite3.connect(db.db_path) as con:
        con.row_factory = sqlite3.Row
        existing = con.execute(
            "SELECT id, title FROM memories WHERE tags LIKE '%\"entity\"%'"
        ).fetchall()
        for row in existing:
            title = row["title"]
            if title.startswith("ENTITY:"):
                name = title[7:]
                name_to_id[name] = row["id"]

    now = datetime.now(timezone.utc).isoformat()

    with sqlite3.connect(db.db_path) as con:
        for name, etype in all_entities.items():
            title = f"ENTITY:{name}"
            if name in name_to_id:
                stats["entities_updated"] += 1
                if verbose:
                    print(f"  [exists] {title}")
            else:
                # Create new entity node
                mem_id = str(uuid.uuid4())
                tags_json = json.dumps(["entity", etype])
                metadata_json = json.dumps({
                    "entity_type": etype,
                    "entity_name": name,
                    "is_entity": True,
                })
                con.execute(
                    """INSERT INTO memories
                       (id, title, content, tier, namespace, tags, priority, source, metadata, created_at, updated_at)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                    (mem_id, title, f"{etype}: {name}", "long", "workspace",
                     tags_json, 6, "graph-activate", metadata_json, now, now),
                )
                name_to_id[name] = mem_id
                stats["entities_created"] += 1
                if verbose:
                    print(f"  [created] {title} ({etype})")

        con.commit()

    # Create edges: entity-to-entity co-occurrence + entity-to-memory links
    entity_pairs_seen: Set[Tuple[str, str]] = set()

    with sqlite3.connect(db.db_path) as con:
        # Get existing links to avoid dupes
        existing_links = set(
            (row[0], row[1])
            for row in con.execute("SELECT source_id, target_id FROM memory_links").fetchall()
        )

        for mem_id, entities in memory_entities.items():
            names = list(entities.keys())

            # Entity ↔ Memory link (entity "related_to" the memory)
            for name in names:
                eid = name_to_id.get(name)
                if eid and (eid, mem_id) not in existing_links:
                    con.execute(
                        "INSERT OR IGNORE INTO memory_links (source_id, target_id, relation, created_at) VALUES (?,?,?,?)",
                        (eid, mem_id, "related_to", now),
                    )
                    existing_links.add((eid, mem_id))
                    stats["edges_created"] += 1

            # Entity ↔ Entity co-occurrence within same memory
            for i in range(len(names)):
                for j in range(i + 1, len(names)):
                    a_name, b_name = names[i], names[j]
                    a_id = name_to_id.get(a_name)
                    b_id = name_to_id.get(b_name)
                    if not a_id or not b_id:
                        continue
                    key = tuple(sorted([a_id, b_id]))
                    if key in entity_pairs_seen:
                        stats["edges_skipped"] += 1
                        continue
                    entity_pairs_seen.add(key)
                    if (a_id, b_id) not in existing_links:
                        con.execute(
                            "INSERT OR IGNORE INTO memory_links (source_id, target_id, relation, created_at) VALUES (?,?,?,?)",
                            (a_id, b_id, "related_to", now),
                        )
                        existing_links.add((a_id, b_id))
                        stats["edges_created"] += 1

        con.commit()

    print(f"[graph-activate] Done!")
    print(f"  Memories scanned:  {stats['memories_scanned']}")
    print(f"  Entities found:    {stats['entities_found']}")
    print(f"  Entities created:  {stats['entities_created']}")
    print(f"  Entities updated:  {stats['entities_updated']}")
    print(f"  Edges created:     {stats['edges_created']}")
    print(f"  Edges skipped:     {stats['edges_skipped']} (duplicates)")

    return stats


def main():
    ap = argparse.ArgumentParser(description="Bulk-activate entity graph from existing memories")
    ap.add_argument("--dry-run", action="store_true", default=False,
                    help="Simulate without writing (default: show counts)")
    ap.add_argument("--apply", action="store_true",
                    help="Actually write entities and edges to DB")
    ap.add_argument("--verbose", "-v", action="store_true",
                    help="Show per-memory details")
    ap.add_argument("--limit", type=int, default=None,
                    help="Limit to first N memories (for testing)")
    args = ap.parse_args()

    dry_run = not args.apply
    if dry_run and not args.apply:
        print("[graph-activate] Running in DRY RUN mode. Use --apply to persist.")

    db = MemoryDB()
    stats = bulk_activate_graph(db, dry_run=dry_run, verbose=args.verbose, limit=args.limit)
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
