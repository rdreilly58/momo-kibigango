#!/usr/bin/env python3
"""
spawn-with-memory.py — Phase 1 cross-agent memory sharing via context injection.

Enriches subagent task prompts with relevant memory context before spawning,
so isolated subagents have working knowledge without needing the memory plugin.

Usage (as a library):
    from spawn_with_memory import build_enriched_task
    enriched = build_enriched_task(task="refactor the auth module", top_k=8)
    # Pass enriched["task"] to sessions_spawn(task=...)

Usage (CLI — generates enriched prompt for inspection):
    python3 spawn-with-memory.py "your task description" [--top-k 8] [--dry-run]

Design:
    Phase 1 (this file): static context injection at spawn time
    Phase 2: QMD CLI wrapper for live search inside subagent (see memory-writeback.py)
    Phase 3: Honcho plugin for automatic cross-agent memory (no code needed)
"""

import argparse
import json
import os
import sys
import time
from datetime import date
from pathlib import Path

WORKSPACE = Path(os.environ.get("OPENCLAW_WORKSPACE", Path.home() / ".openclaw" / "workspace"))
sys.path.insert(0, str(WORKSPACE / "scripts"))

# ---------------------------------------------------------------------------
# Core search (delegates to total_recall_search or tier_manager)
# ---------------------------------------------------------------------------

def search_memories(query: str, top_k: int = 8) -> list[dict]:
    """Return top_k memories relevant to query."""
    try:
        from memory_tier_manager import TierManager
        tm = TierManager()
        results = tm.search(query, k=top_k)
        return results
    except Exception as e:
        # Fallback: try total_recall_search subprocess
        import subprocess
        r = subprocess.run(
            [sys.executable, str(WORKSPACE / "scripts" / "total_recall_search.py"),
             query, "--json", "--limit", str(top_k)],
            capture_output=True, text=True
        )
        if r.returncode == 0:
            return json.loads(r.stdout)
        return []


def read_core_files() -> dict[str, str]:
    """Read MEMORY.md and USER_PROFILE.md (first 2KB each)."""
    cores = {}
    for fname in ["MEMORY.md", "memory/USER_PROFILE.md"]:
        fpath = WORKSPACE / fname
        if fpath.exists():
            content = fpath.read_text(errors="replace")
            cores[fname] = content[:2500]  # cap at 2.5KB per file
    return cores


def format_memories(memories: list[dict]) -> str:
    """Format memory search results as a readable context block."""
    if not memories:
        return "(no relevant memories found)"

    lines = []
    for i, m in enumerate(memories, 1):
        title = m.get("title") or m.get("path") or "untitled"
        content = m.get("content") or m.get("snippet") or ""
        score = m.get("_score") or m.get("_rerank_score") or 0
        tier = m.get("tier") or m.get("_tier") or ""
        tags = m.get("tags") or ""

        # Trim content to ~300 chars
        content_preview = content[:300].replace("\n", " ").strip()
        if len(content) > 300:
            content_preview += "…"

        lines.append(f"**[{i}] {title}**")
        if tier or tags:
            meta = " | ".join(filter(None, [tier, str(tags) if tags else ""]))
            lines.append(f"  *{meta}* (score: {score:.3f})")
        lines.append(f"  {content_preview}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main builder
# ---------------------------------------------------------------------------

def build_enriched_task(
    task: str,
    top_k: int = 8,
    include_core_files: bool = True,
    include_writeback_instructions: bool = True,
) -> dict:
    """
    Build an enriched task dict for sessions_spawn.

    Returns:
        {
          "task": str,               # enriched task string
          "memory_count": int,       # how many memories were injected
          "core_files": list[str],   # which core files were included
        }
    """
    # 1. Search for relevant memories
    memories = search_memories(task[:300], top_k=top_k)
    memory_block = format_memories(memories)

    # 2. Read core files
    core_files_content = ""
    core_files_loaded = []
    if include_core_files:
        cores = read_core_files()
        for fname, content in cores.items():
            core_files_content += f"\n### {fname}\n{content}\n"
            core_files_loaded.append(fname)

    # 3. Build write-back instructions
    writeback = ""
    if include_writeback_instructions:
        today = date.today().isoformat()
        writeback = f"""
## Memory Write-Back (Phase 2)
If you discover important facts, decisions, or learnings during this task,
write them back so the main session can recall them:

```bash
# Append findings to today's memory log:
cat >> ~/.openclaw/workspace/memory/{today}.md << 'EOF'
## [SUBAGENT FINDING — <timestamp>]
<your finding here>
EOF

# Or for important decisions, use total_recall_search to verify it's not already stored,
# then append to MEMORY.md directly.

# QMD will auto-index within 60 seconds (Phase 2 interval).
```
"""

    # 4. Assemble enriched prompt
    enriched = f"""## 🧠 Memory Context (injected at spawn — {len(memories)} memories, top_k={top_k})
*Query used: "{task[:100]}"*

{memory_block}
---
{core_files_content}
{writeback}
---

## Task
{task}
"""

    return {
        "task": enriched,
        "memory_count": len(memories),
        "core_files": core_files_loaded,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Build memory-enriched task prompt for subagent spawn")
    parser.add_argument("task", help="Task description for the subagent")
    parser.add_argument("--top-k", type=int, default=8, help="Number of memories to inject (default: 8)")
    parser.add_argument("--no-core-files", action="store_true", help="Skip MEMORY.md / USER_PROFILE.md injection")
    parser.add_argument("--dry-run", action="store_true", help="Print enriched prompt without saving")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    result = build_enriched_task(
        task=args.task,
        top_k=args.top_k,
        include_core_files=not args.no_core_files,
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"── Memory Context Injection Report ──")
        print(f"Memories injected : {result['memory_count']}")
        print(f"Core files        : {', '.join(result['core_files']) or 'none'}")
        print(f"Prompt length     : {len(result['task'])} chars")
        print()
        if args.dry_run:
            print("── Enriched Task Prompt ──")
            print(result["task"])


if __name__ == "__main__":
    main()
