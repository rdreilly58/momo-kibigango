#!/usr/bin/env python3
"""
memory_graph.py — Graph memory layer for ai-memory.db

Extracts entities and relationships from session summaries using Claude Haiku,
stores them as entity nodes (memories) + typed edges (memory_links), and
provides graph-augmented search that combines FTS with BFS link traversal.

Entity node convention:
  title    = "ENTITY:<name>"   — unique key in DB
  tier     = "long"            — entities persist indefinitely
  tags     = ["entity", <type>]
  metadata = {"entity_type": ..., "entity_name": ..., "is_entity": true}

Entity types:  person, project, tool, concept, system, file
Relation types: uses, depends_on, works_on, owns, resolves, blocks,
                related_to, part_of

Usage (CLI):
    python3 memory_graph.py extract --summary '{"one_liner":...}' [--dry-run]
    python3 memory_graph.py extract --memory-id <id>              [--dry-run]
    python3 memory_graph.py traverse "entity name"    [--depth 2]
    python3 memory_graph.py search   "query"          [--depth 1]
    python3 memory_graph.py list-entities             [--ns workspace]
    python3 memory_graph.py stats
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Path bootstrap — allow import from scripts/ directory
# ---------------------------------------------------------------------------

_SCRIPTS = Path(__file__).parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from memory_db import MemoryDB  # type: ignore  # noqa: E402

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DEFAULT_WORKSPACE = Path.home() / ".openclaw" / "workspace"
DB_PATH = DEFAULT_WORKSPACE / "ai-memory.db"
HAIKU_MODEL = "claude-haiku-4-5-20251001"
ENTITY_PREFIX = "ENTITY:"
DEFAULT_NAMESPACE = "workspace"

VALID_ENTITY_TYPES = {"person", "project", "tool", "concept", "system", "file"}
VALID_RELATIONS = {
    "uses", "depends_on", "works_on", "owns", "resolves",
    "blocks", "related_to", "part_of",
}

# ---------------------------------------------------------------------------
# Haiku extraction prompt
# ---------------------------------------------------------------------------

_GRAPH_EXTRACTION_PROMPT = """\
Extract named entities and relationships from a session summary.

Return ONLY valid JSON — no markdown fences, no commentary:
{
  "entities": [
    {"name": "ExactName", "type": "person|project|tool|concept|system|file", "description": "one sentence"}
  ],
  "relationships": [
    {"source": "EntityA", "target": "EntityB", "relation": "uses|depends_on|works_on|owns|resolves|blocks|related_to|part_of"}
  ]
}

Rules:
- Extract 2–8 entities; skip generic/filler terms like "session" or "code"
- Use canonical names: file names with extension, project names as-is, people by first name
- Only extract relationships explicitly present in the summary
- Both source and target MUST be entities you listed
- If nothing notable: {"entities": [], "relationships": []}
"""


# ---------------------------------------------------------------------------
# Haiku API call
# ---------------------------------------------------------------------------

def _get_api_key() -> str:
    """Return ANTHROPIC_API_KEY from env or briefing.env fallback."""
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if key:
        return key
    env_file = Path.home() / ".openclaw" / "workspace" / "config" / "briefing.env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line.startswith("ANTHROPIC_API_KEY="):
                return line.split("=", 1)[1].strip()
    raise RuntimeError(
        "ANTHROPIC_API_KEY not set — add to env or config/briefing.env"
    )


def _call_haiku_graph(summary: dict) -> dict:
    """Call Haiku to extract entities+relationships from a compact summary dict."""
    api_key = _get_api_key()

    import anthropic  # type: ignore

    client = anthropic.Anthropic(api_key=api_key)
    summary_text = json.dumps(summary, ensure_ascii=False, indent=2)

    message = client.messages.create(
        model=HAIKU_MODEL,
        max_tokens=512,
        system=[
            {
                "type": "text",
                "text": _GRAPH_EXTRACTION_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": f"Extract entities and relationships from this session summary:\n\n{summary_text}",
            }
        ],
    )

    raw = message.content[0].text.strip()
    return _parse_graph_json(raw)


def _parse_graph_json(raw: str) -> dict:
    """Parse and validate graph extraction JSON from Haiku."""
    import re

    # Strip markdown fences if model added them
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.MULTILINE)
    raw = re.sub(r"```\s*$", "", raw, flags=re.MULTILINE).strip()

    defaults = {"entities": [], "relationships": []}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return defaults

    # Validate + sanitize
    entities = []
    for e in parsed.get("entities", []):
        name = str(e.get("name", "")).strip()
        etype = str(e.get("type", "concept")).lower()
        desc = str(e.get("description", "")).strip()
        if name and etype in VALID_ENTITY_TYPES:
            entities.append({"name": name, "type": etype, "description": desc})

    entity_names = {e["name"] for e in entities}
    relationships = []
    for r in parsed.get("relationships", []):
        src = str(r.get("source", "")).strip()
        tgt = str(r.get("target", "")).strip()
        rel = str(r.get("relation", "related_to")).lower()
        if src in entity_names and tgt in entity_names and rel in VALID_RELATIONS:
            relationships.append({"source": src, "target": tgt, "relation": rel})

    return {"entities": entities, "relationships": relationships}


# ---------------------------------------------------------------------------
# Entity CRUD
# ---------------------------------------------------------------------------

def _entity_title(name: str) -> str:
    return f"{ENTITY_PREFIX}{name}"


def upsert_entity(
    name: str,
    entity_type: str,
    description: str,
    db: MemoryDB,
    namespace: str = DEFAULT_NAMESPACE,
) -> str:
    """
    Find or create an entity node. Returns the memory ID.
    If description is empty, keeps existing description on update.
    """
    title = _entity_title(name)
    # Try to find existing by exact title
    with __import__("sqlite3").connect(db.db_path) as con:
        row = con.execute(
            "SELECT id, content FROM memories WHERE title=? AND namespace=?",
            (title, namespace),
        ).fetchone()

    if row:
        mem_id, existing_content = row
        # Update description only if new one is richer
        if description and description != existing_content:
            db.update(mem_id, content=description)
        return mem_id

    return db.add(
        title=title,
        content=description or name,
        tier="long",
        namespace=namespace,
        tags=["entity", entity_type],
        priority=7,
        source="graph",
        metadata={"entity_type": entity_type, "entity_name": name, "is_entity": True},
    )


def find_entity(name: str, db: MemoryDB, namespace: str = DEFAULT_NAMESPACE) -> Optional[str]:
    """Return the memory ID of an entity by name, or None if not found."""
    title = _entity_title(name)
    with __import__("sqlite3").connect(db.db_path) as con:
        row = con.execute(
            "SELECT id FROM memories WHERE title=? AND namespace=?",
            (title, namespace),
        ).fetchone()
    return row[0] if row else None


def list_entities(db: MemoryDB, namespace: str = DEFAULT_NAMESPACE) -> List[Dict]:
    """Return all entity nodes."""
    with __import__("sqlite3").connect(db.db_path) as con:
        con.row_factory = __import__("sqlite3").Row
        rows = con.execute(
            """SELECT id, title, content, tags, metadata, updated_at
               FROM memories
               WHERE namespace=? AND tags LIKE '%\"entity\"%'
               ORDER BY updated_at DESC""",
            (namespace,),
        ).fetchall()

    results = []
    for r in rows:
        d = dict(r)
        d["tags"] = json.loads(d.get("tags") or "[]")
        d["metadata"] = json.loads(d.get("metadata") or "{}")
        if d["metadata"].get("is_entity"):
            d["name"] = d["metadata"].get("entity_name", d["title"].replace(ENTITY_PREFIX, ""))
            results.append(d)
    return results


# ---------------------------------------------------------------------------
# Graph population
# ---------------------------------------------------------------------------

def populate_graph(
    summary: dict,
    memory_id: str,
    db: MemoryDB,
    namespace: str = DEFAULT_NAMESPACE,
    dry_run: bool = False,
) -> dict:
    """
    Extract entities from a session summary and wire them into the graph.

    Also links each entity back to the session memory node (memory_id)
    with relation 'related_to'.

    Returns the extracted graph dict: {"entities": [...], "relationships": [...]}
    """
    graph = _call_haiku_graph(summary)

    entities = graph.get("entities", [])
    relationships = graph.get("relationships", [])

    if dry_run:
        return graph

    # Upsert entity nodes
    name_to_id: Dict[str, str] = {}
    for e in entities:
        eid = upsert_entity(e["name"], e["type"], e["description"], db, namespace)
        name_to_id[e["name"]] = eid
        # Link entity → session memory node
        if memory_id:
            db.link(eid, memory_id, relation="related_to")

    # Upsert relationships
    for r in relationships:
        src_id = name_to_id.get(r["source"])
        tgt_id = name_to_id.get(r["target"])
        if src_id and tgt_id:
            db.link(src_id, tgt_id, relation=r["relation"])

    return graph


# ---------------------------------------------------------------------------
# Graph traversal (BFS)
# ---------------------------------------------------------------------------

def traverse(
    entity_name: str,
    db: MemoryDB,
    depth: int = 2,
    namespace: str = DEFAULT_NAMESPACE,
) -> List[Dict]:
    """
    BFS from a named entity up to `depth` hops.

    Returns list of dicts: {memory, depth, relation, direction}
    """
    start_id = find_entity(entity_name, db, namespace)
    if not start_id:
        # Try FTS fallback
        hits = db.search_fts(_entity_title(entity_name), namespace=namespace, limit=1)
        if hits:
            start_id = hits[0]["id"]

    if not start_id:
        return []

    return _bfs(start_id, db, depth)


def _bfs(start_id: str, db: MemoryDB, max_depth: int) -> List[Dict]:
    """Generic BFS from start_id across memory_links."""
    import sqlite3

    visited = {start_id}
    queue = [(start_id, 0)]
    results = []

    with sqlite3.connect(db.db_path) as con:
        con.row_factory = sqlite3.Row

        while queue:
            current_id, current_depth = queue.pop(0)
            if current_depth >= max_depth:
                continue

            # Outgoing links
            out_links = con.execute(
                "SELECT target_id, relation FROM memory_links WHERE source_id=?",
                (current_id,),
            ).fetchall()
            # Incoming links
            in_links = con.execute(
                "SELECT source_id, relation FROM memory_links WHERE target_id=?",
                (current_id,),
            ).fetchall()

            for row in out_links:
                nid = row["target_id"]
                if nid not in visited:
                    visited.add(nid)
                    mem_row = con.execute(
                        "SELECT id, title, content, tags, metadata FROM memories WHERE id=?",
                        (nid,),
                    ).fetchone()
                    if mem_row:
                        m = dict(mem_row)
                        m["tags"] = json.loads(m.get("tags") or "[]")
                        m["metadata"] = json.loads(m.get("metadata") or "{}")
                        results.append({
                            "memory": m,
                            "depth": current_depth + 1,
                            "relation": row["relation"],
                            "direction": "out",
                        })
                        queue.append((nid, current_depth + 1))

            for row in in_links:
                nid = row["source_id"]
                if nid not in visited:
                    visited.add(nid)
                    mem_row = con.execute(
                        "SELECT id, title, content, tags, metadata FROM memories WHERE id=?",
                        (nid,),
                    ).fetchone()
                    if mem_row:
                        m = dict(mem_row)
                        m["tags"] = json.loads(m.get("tags") or "[]")
                        m["metadata"] = json.loads(m.get("metadata") or "{}")
                        results.append({
                            "memory": m,
                            "depth": current_depth + 1,
                            "relation": row["relation"],
                            "direction": "in",
                        })
                        queue.append((nid, current_depth + 1))

    return results


# ---------------------------------------------------------------------------
# Graph-augmented search
# ---------------------------------------------------------------------------

def graph_augmented_search(
    query: str,
    db: MemoryDB,
    depth: int = 1,
    fts_limit: int = 5,
    namespace: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Two-phase search:
      1. FTS to find seed nodes matching query
      2. BFS expansion to depth hops from each seed

    Returns {"seeds": [...fts results], "graph": [...traversal results]}
    """
    seeds = db.search_fts(query, namespace=namespace, limit=fts_limit)

    graph_nodes: Dict[str, Dict] = {}
    seen_ids = {s["id"] for s in seeds}

    for seed in seeds:
        neighbors = _bfs(seed["id"], db, depth)
        for n in neighbors:
            nid = n["memory"]["id"]
            if nid not in seen_ids:
                seen_ids.add(nid)
                graph_nodes[nid] = n

    return {
        "seeds": seeds,
        "graph": list(graph_nodes.values()),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cli():
    p = argparse.ArgumentParser(description="memory_graph.py — Graph memory layer")
    sub = p.add_subparsers(dest="cmd")

    # extract
    ex = sub.add_parser("extract", help="Extract entities from a summary")
    grp = ex.add_mutually_exclusive_group(required=True)
    grp.add_argument("--summary", help="JSON summary string")
    grp.add_argument("--memory-id", help="Pull summary from DB by memory ID")
    ex.add_argument("--ns", default=DEFAULT_NAMESPACE)
    ex.add_argument("--dry-run", action="store_true")

    # traverse
    tr = sub.add_parser("traverse", help="BFS from an entity")
    tr.add_argument("name", help="Entity name")
    tr.add_argument("--depth", type=int, default=2)
    tr.add_argument("--ns", default=DEFAULT_NAMESPACE)

    # search
    sr = sub.add_parser("search", help="Graph-augmented FTS search")
    sr.add_argument("query")
    sr.add_argument("--depth", type=int, default=1)
    sr.add_argument("--ns")

    # list-entities
    le = sub.add_parser("list-entities", help="List all entity nodes")
    le.add_argument("--ns", default=DEFAULT_NAMESPACE)

    # stats
    sub.add_parser("stats", help="Graph statistics")

    args = p.parse_args()
    db = MemoryDB()

    if args.cmd == "extract":
        if args.summary:
            try:
                summary = json.loads(args.summary)
            except json.JSONDecodeError as e:
                print(f"Invalid JSON: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            mem = db.get(args.memory_id)
            if not mem:
                print("Memory not found", file=sys.stderr)
                sys.exit(1)
            # Rebuild summary-like dict from content
            summary = {"one_liner": mem["title"], "content": mem["content"]}

        graph = populate_graph(
            summary,
            memory_id=getattr(args, "memory_id", "") or "",
            db=db,
            namespace=args.ns,
            dry_run=args.dry_run,
        )
        print(json.dumps(graph, indent=2))

    elif args.cmd == "traverse":
        results = traverse(args.name, db, depth=args.depth, namespace=args.ns)
        if not results:
            print(f"Entity '{args.name}' not found or has no links.")
        else:
            for r in results:
                m = r["memory"]
                title = m["title"].replace(ENTITY_PREFIX, "")
                print(f"  depth={r['depth']} [{r['direction']}:{r['relation']}] {title}")
                print(f"    {m['content'][:120]}")

    elif args.cmd == "search":
        results = graph_augmented_search(
            args.query, db, depth=args.depth, namespace=args.ns
        )
        print(f"Seeds ({len(results['seeds'])}):")
        for s in results["seeds"]:
            print(f"  [{s['tier']}] {s['title']}: {s['content'][:80]}")
        print(f"Graph neighbors ({len(results['graph'])}):")
        for n in results["graph"]:
            m = n["memory"]
            print(f"  depth={n['depth']} [{n['relation']}] {m['title']}: {m['content'][:80]}")

    elif args.cmd == "list-entities":
        entities = list_entities(db, namespace=args.ns)
        if not entities:
            print("No entities found.")
        else:
            for e in entities:
                etype = e["metadata"].get("entity_type", "?")
                print(f"  [{etype}] {e['name']}: {e['content'][:100]}")

    elif args.cmd == "stats":
        entities = list_entities(db)
        by_type: Dict[str, int] = {}
        for e in entities:
            t = e["metadata"].get("entity_type", "unknown")
            by_type[t] = by_type.get(t, 0) + 1
        import sqlite3
        with sqlite3.connect(db.db_path) as con:
            link_count = con.execute("SELECT COUNT(*) FROM memory_links").fetchone()[0]
        print(json.dumps({
            "total_entities": len(entities),
            "entities_by_type": by_type,
            "total_links": link_count,
        }, indent=2))

    else:
        p.print_help()


if __name__ == "__main__":
    _cli()
