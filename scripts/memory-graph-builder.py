#!/usr/bin/env python3
"""
memory-graph-builder.py — Build and visualize memory relationship graph.

Creates a knowledge graph showing how memories relate:
- Nodes: memories with metadata (title, type, priority)
- Edges: relationships between memories
  - same_namespace: in same topic area
  - similar: high embedding similarity
  - referenced: mentioned in content
  - entity_linked: same named entity

Outputs:
- JSON graph for visualization (D3, Cytoscape, etc)
- ASCII network visualization
- Statistics on connectivity
"""

import json
import sys
import os
import re
from typing import Dict, List, Tuple, Set
from collections import defaultdict

sys.path.insert(0, os.path.expanduser("~/.openclaw/workspace/scripts"))

from memory_db import MemoryDB
from memory_tier_manager import TierManager
from memory_audit_logger import log_operation


def extract_entities(text: str) -> Set[str]:
    """Extract named entities and concepts from text."""
    entities = set()

    # Email addresses
    entities.update(re.findall(r"[\w\.-]+@[\w\.-]+", text))

    # URLs
    entities.update(re.findall(r"https?://[^\s]+", text))

    # UPPERCASE acronyms (3+ letters)
    entities.update(re.findall(r"\b[A-Z]{3,}\b", text))

    # Common patterns
    entities.update(re.findall(r"file://[^\s]+", text))

    return entities


def find_memory_links(memories: List[Dict]) -> List[Tuple[str, str, str]]:
    """
    Find relationships between memories.

    Returns:
        List of (source_id, target_id, relation_type) tuples
    """
    links = []
    memo_dict = {m["id"]: m for m in memories}

    for i, mem1 in enumerate(memories):
        for mem2 in memories[i + 1 :]:
            relation = None

            # Same namespace
            if mem1.get("namespace") == mem2.get("namespace"):
                relation = "same_namespace"

            # Shared entities
            entities1 = extract_entities(
                mem1.get("content", "") + mem1.get("title", "")
            )
            entities2 = extract_entities(
                mem2.get("content", "") + mem2.get("title", "")
            )

            shared = entities1 & entities2
            if shared and len(shared) >= 2:
                relation = "entity_linked"

            # Referenced in content
            if mem1.get("id") in mem2.get("content", ""):
                relation = "referenced"
            elif mem2.get("id") in mem1.get("content", ""):
                relation = "referenced"

            if relation:
                links.append((mem1["id"], mem2["id"], relation))

    return links


def build_graph(db: MemoryDB) -> Dict:
    """
    Build a complete memory relationship graph.

    Returns:
        Graph structure: {nodes: [...], edges: [...], stats: {...}}
    """
    import sqlite3
    from contextlib import contextmanager

    db_path = db.db_path

    @contextmanager
    def get_conn(path):
        con = sqlite3.connect(path)
        con.row_factory = sqlite3.Row
        try:
            yield con
        finally:
            con.close()

    graph = {
        "name": "Memory Relationship Graph",
        "built_at": __import__("datetime")
        .datetime.now(__import__("datetime").timezone.utc)
        .isoformat(),
        "nodes": [],
        "edges": [],
        "stats": {
            "total_nodes": 0,
            "total_edges": 0,
            "avg_connections": 0,
            "centrality": {},
        },
    }

    try:
        with get_conn(db_path) as con:
            memories = con.execute(
                "SELECT id, title, content, namespace, tags, priority, tier FROM memories WHERE tier IN ('short', 'long')"
            ).fetchall()

        memories_list = [dict(m) for m in memories]
        graph["stats"]["total_nodes"] = len(memories_list)

        # Create nodes
        for mem in memories_list:
            tags = json.loads(mem.get("tags", "[]"))
            node = {
                "id": mem["id"],
                "label": mem.get("title", "")[:40],
                "title": mem.get("title", ""),
                "namespace": mem.get("namespace", ""),
                "priority": mem.get("priority", 5),
                "tier": mem.get("tier", ""),
                "tags": tags,
                "size": 5 + mem.get("priority", 5),
            }
            graph["nodes"].append(node)

        # Find and create edges
        edges = find_memory_links(memories_list)
        edge_types = defaultdict(int)

        for src_id, tgt_id, relation in edges:
            edge = {
                "source": src_id,
                "target": tgt_id,
                "type": relation,
                "weight": {
                    "same_namespace": 1,
                    "entity_linked": 2,
                    "referenced": 3,
                }.get(relation, 1),
            }
            graph["edges"].append(edge)
            edge_types[relation] += 1

        graph["stats"]["total_edges"] = len(edges)
        graph["stats"]["edge_types"] = dict(edge_types)

        # Compute centrality (degree centrality)
        degrees = defaultdict(int)
        for edge in edges:
            degrees[edge["source"]] += 1
            degrees[edge["target"]] += 1

        if graph["stats"]["total_nodes"] > 0:
            graph["stats"]["avg_connections"] = 2 * len(edges) / len(memories_list)
            graph["stats"]["centrality"] = {
                node_id: degree
                for node_id, degree in sorted(degrees.items(), key=lambda x: -x[1])[:10]
            }

        # Log graph build
        log_operation(
            op="build",
            source="auto:graph",
            memory_id="batch",
            namespace="workspace",
            title="Built memory relationship graph",
            content=f"Graph with {len(memories_list)} nodes, {len(edges)} edges",
            tags=["graph", "visualization"],
        )

    except Exception as e:
        print(f"[graph:error] {e}", file=sys.stderr)

    return graph


def save_graph(graph: Dict, output_path: str = None):
    """Save graph to JSON for visualization."""
    if not output_path:
        output_path = os.path.expanduser("~/.openclaw/workspace/memory-graph.json")

    try:
        with open(output_path, "w") as f:
            json.dump(graph, f, indent=2)
        print(f"[graph] Saved to {output_path}")
    except Exception as e:
        print(f"[graph:error] Failed to save: {e}", file=sys.stderr)


def visualize_graph(graph: Dict) -> str:
    """Generate ASCII visualization of graph."""
    output = []
    output.append("🔗 MEMORY RELATIONSHIP GRAPH")
    output.append("=" * 60)
    output.append(f"Built: {graph.get('built_at')}")

    stats = graph.get("stats", {})
    output.append(
        f"Nodes: {stats.get('total_nodes')} | "
        f"Edges: {stats.get('total_edges')} | "
        f"Avg Connections: {stats.get('avg_connections', 0):.1f}"
    )
    output.append("")

    output.append("🏆 MOST CONNECTED MEMORIES (Centrality)")
    output.append("-" * 60)

    centrality = stats.get("centrality", {})
    node_dict = {n["id"]: n["label"] for n in graph.get("nodes", [])}

    for i, (node_id, degree) in enumerate(
        sorted(centrality.items(), key=lambda x: -x[1])[:10], 1
    ):
        label = node_dict.get(node_id, "Unknown")[:40]
        output.append(f"{i:2}. [{degree:2d} links] {label}")

    output.append("")
    output.append("📊 RELATIONSHIP TYPES")
    output.append("-" * 60)

    edge_types = stats.get("edge_types", {})
    for rel_type, count in sorted(edge_types.items(), key=lambda x: -x[1]):
        output.append(f"  {rel_type}: {count}")

    return "\n".join(output)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Build memory relationship graph")
    parser.add_argument(
        "--build", action="store_true", help="Build graph from memories"
    )
    parser.add_argument(
        "--visualize", action="store_true", help="Show ASCII visualization"
    )
    parser.add_argument("--output", help="Output file path for graph JSON")

    args = parser.parse_args()

    if not args.build and not args.visualize:
        parser.print_help()
        return

    db_path = os.path.expanduser("~/.openclaw/workspace/ai-memory.db")
    db = MemoryDB(db_path=db_path)

    if args.build:
        print("[graph] Building relationship graph...")
        graph = build_graph(db)
        save_graph(graph, output_path=args.output)

    if args.visualize:
        graph_path = args.output or os.path.expanduser(
            "~/.openclaw/workspace/memory-graph.json"
        )
        if os.path.exists(graph_path):
            with open(graph_path) as f:
                graph = json.load(f)
            print(visualize_graph(graph))
        else:
            print("[graph] Graph file not found. Run --build first.")


if __name__ == "__main__":
    main()
