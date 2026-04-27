#!/usr/bin/env python3
"""
memory-palace-builder.py — Organize memories into spatial "palace" structure.

Creates a virtual palace where related memories are proximate:
- Top-level "wings": major topics (projects, feedback, lessons, etc)
- Rooms within wings: semantic clusters
- Locations in rooms: individual memories

Uses embedding similarity for spatial layout.
Builds hierarchical structure: Palace → Wings → Rooms → Memories
"""

import json
import sys
import os
from typing import Dict, List, Tuple
from datetime import datetime, timezone
from collections import defaultdict

sys.path.insert(0, os.path.expanduser("~/.openclaw/workspace/scripts"))

from memory_db import MemoryDB
from memory_tier_manager import TierManager

# Palace configuration
PALACE_CONFIG = {
    "wings": {
        "feedback": {
            "color": "#FF6B6B",
            "icon": "💭",
            "description": "Behavior & Guidance",
        },
        "projects": {
            "color": "#4ECDC4",
            "icon": "🎯",
            "description": "Active Initiatives",
        },
        "lessons": {
            "color": "#95E1D3",
            "icon": "📚",
            "description": "Root Causes & Prevention",
        },
        "references": {
            "color": "#FFE66D",
            "icon": "🔗",
            "description": "External Resources",
        },
        "observations": {
            "color": "#A8E6CF",
            "icon": "👀",
            "description": "Activity Logs",
        },
    }
}


def get_memory_wing(namespace: str, tags: List[str]) -> str:
    """Determine which wing a memory belongs to based on namespace/tags."""
    if "feedback" in tags or namespace == "feedback":
        return "feedback"
    elif "project" in tags or "initiative" in tags:
        return "projects"
    elif "lesson" in tags or "root-cause" in tags:
        return "lessons"
    elif "reference" in tags or namespace == "reference":
        return "references"
    else:
        return "observations"


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Compute cosine similarity between embeddings."""
    if not vec1 or not vec2:
        return 0.0
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    mag1 = sum(a * a for a in vec1) ** 0.5
    mag2 = sum(b * b for b in vec2) ** 0.5
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return dot_product / (mag1 * mag2)


def cluster_memories(
    memories: List[Dict], num_clusters: int = 5
) -> Dict[int, List[Dict]]:
    """
    Simple k-means-like clustering of memories.
    Groups similar memories into "rooms".
    """
    if not memories:
        return {}

    # Simplified: group by title similarity
    clusters = defaultdict(list)

    # Group by first word of title (very simple heuristic)
    for mem in memories:
        title = mem.get("title", "")
        first_word = title.split()[0].lower() if title else "other"
        # Use first word as cluster key
        cluster_id = hash(first_word) % num_clusters
        clusters[cluster_id].append(mem)

    return dict(clusters)


def build_palace(db: MemoryDB, tm: TierManager) -> Dict:
    """
    Build a complete palace structure from all memories.

    Returns:
        Palace structure: {wings: {wing_name: {rooms: {room_id: [memories]}}}}
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

    palace = {
        "name": "Memory Palace",
        "built_at": datetime.now(timezone.utc).isoformat(),
        "stats": {
            "total_memories": 0,
            "total_wings": 0,
            "total_rooms": 0,
        },
        "wings": {},
    }

    try:
        with get_conn(db_path) as con:
            memories = con.execute(
                "SELECT id, title, content, namespace, tags, priority, tier FROM memories WHERE tier IN ('short', 'long')"
            ).fetchall()

        memories_list = [dict(m) for m in memories]
        palace["stats"]["total_memories"] = len(memories_list)

        # Organize by wing
        for wing_name in PALACE_CONFIG["wings"].keys():
            wing_memories = [
                m
                for m in memories_list
                if get_memory_wing(
                    m.get("namespace", ""), json.loads(m.get("tags", "[]"))
                )
                == wing_name
            ]

            if not wing_memories:
                continue

            # Cluster memories into rooms
            rooms = cluster_memories(wing_memories, num_clusters=3)

            wing = {
                "name": wing_name,
                "description": PALACE_CONFIG["wings"][wing_name]["description"],
                "color": PALACE_CONFIG["wings"][wing_name]["color"],
                "icon": PALACE_CONFIG["wings"][wing_name]["icon"],
                "memory_count": len(wing_memories),
                "rooms": {},
            }

            for room_id, room_memories in rooms.items():
                room_name = f"Room {room_id}"

                # Try to derive room name from content
                if room_memories:
                    first_title = room_memories[0].get("title", "")
                    if first_title:
                        room_name = first_title.split()[0:2]
                        room_name = " ".join(room_name) + f" ({len(room_memories)})"

                wing["rooms"][str(room_id)] = {
                    "name": room_name,
                    "memory_count": len(room_memories),
                    "memories": [
                        {
                            "id": m.get("id"),
                            "title": m.get("title"),
                            "priority": m.get("priority", 5),
                            "tier": m.get("tier"),
                        }
                        for m in room_memories
                    ],
                }

            palace["wings"][wing_name] = wing
            palace["stats"]["total_wings"] += 1
            palace["stats"]["total_rooms"] += len(rooms)

    except Exception as e:
        print(f"[palace:error] {e}", file=sys.stderr)
        return palace

    return palace


def save_palace(palace: Dict, output_path: str = None):
    """Save palace structure to JSON file."""
    if not output_path:
        output_path = os.path.expanduser("~/.openclaw/workspace/memory-palace.json")

    try:
        with open(output_path, "w") as f:
            json.dump(palace, f, indent=2)
        print(f"[palace] Saved to {output_path}")
    except Exception as e:
        print(f"[palace:error] Failed to save: {e}", file=sys.stderr)


def visualize_palace(palace: Dict) -> str:
    """Generate ASCII visualization of palace."""
    output = []
    output.append("🏛️  MEMORY PALACE")
    output.append("=" * 60)
    output.append(f"Built: {palace.get('built_at')}")
    output.append(
        f"Memories: {palace['stats']['total_memories']} | "
        f"Wings: {palace['stats']['total_wings']} | "
        f"Rooms: {palace['stats']['total_rooms']}"
    )
    output.append("")

    for wing_name, wing in palace.get("wings", {}).items():
        icon = wing.get("icon", "")
        desc = wing.get("description", "")
        count = wing.get("memory_count", 0)

        output.append(f"{icon} {wing_name.upper()} ({count} memories)")
        output.append("-" * 60)

        for room_id, room in wing.get("rooms", {}).items():
            room_name = room.get("name", "Room")
            room_count = room.get("memory_count", 0)

            output.append(f"  └─ {room_name} ({room_count})")

            for mem in room.get("memories", [])[:3]:  # Show first 3
                title = mem.get("title", "")[:40]
                output.append(f"     • {title}")

            if room_count > 3:
                output.append(f"     • +{room_count - 3} more...")

        output.append("")

    return "\n".join(output)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Build memory palace structure")
    parser.add_argument(
        "--build", action="store_true", help="Build palace from memories"
    )
    parser.add_argument(
        "--visualize", action="store_true", help="Show ASCII visualization"
    )
    parser.add_argument("--output", help="Output file path for palace JSON")

    args = parser.parse_args()

    if not args.build and not args.visualize:
        parser.print_help()
        return

    db_path = os.path.expanduser("~/.openclaw/workspace/ai-memory.db")
    db = MemoryDB(db_path=db_path)
    tm = TierManager(db_path=db_path)

    if args.build:
        print("[palace] Building palace structure...")
        palace = build_palace(db, tm)
        save_palace(palace, output_path=args.output)

    if args.visualize:
        palace_path = args.output or os.path.expanduser(
            "~/.openclaw/workspace/memory-palace.json"
        )
        if os.path.exists(palace_path):
            with open(palace_path) as f:
                palace = json.load(f)
            print(visualize_palace(palace))
        else:
            print("[palace] Palace file not found. Run --build first.")


if __name__ == "__main__":
    main()
