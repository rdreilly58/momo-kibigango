#!/usr/bin/env -S /Users/rreilly/.openclaw/workspace/venv/bin/python3
"""
memory_retrieve.py — Semantic memory retrieval CLI for session-start injection.

Wraps the sentence-transformers search engine from memory_mcp_server.py.
No API keys required — fully local inference via all-MiniLM-L6-v2.

Usage:
    python3 memory_retrieve.py "query text" [--top-k 5] [--format markdown|json]

Output (markdown, default):
    - [source] score=0.72 — preview text...

Output (json):
    [{"source": "...", "score": 0.72, "preview": "...", "text": "..."}]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# ── Bootstrap venv path ──────────────────────────────────────────────────────
_WORKSPACE = Path(__file__).parent.parent
_VENV = _WORKSPACE / "venv" / "lib" / "python3.14" / "site-packages"
if _VENV.exists():
    sys.path.insert(0, str(_VENV))

_SCRIPTS = Path(__file__).parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))


def _semantic_search(query: str, top_k: int) -> list[dict]:
    """Use memory_mcp_server's local embedding engine."""
    try:
        import memory_mcp_server as mms  # type: ignore
        return mms.semantic_search(query, top_k=top_k)
    except Exception as e:
        return [{"source": "error", "score": 0.0, "text": str(e), "preview": str(e)}]


def _format_markdown(results: list[dict]) -> str:
    lines = []
    for r in results:
        source = r.get("source", "?")
        score = r.get("score", 0.0)
        preview = r.get("preview", r.get("text", ""))[:160].replace("\n", " ")
        lines.append(f"  - [{source}] score={score:.2f} — {preview}")
    return "\n".join(lines) if lines else "  (no relevant memories found)"


def main() -> int:
    p = argparse.ArgumentParser(description="Semantic memory retrieval")
    p.add_argument("query", help="Natural-language search query")
    p.add_argument("--top-k", type=int, default=5, help="Max results (default: 5)")
    p.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format (default: markdown)",
    )
    args = p.parse_args()

    results = _semantic_search(args.query, top_k=args.top_k)

    if args.format == "json":
        # Strip raw embeddings (numpy arrays not JSON-serialisable)
        clean = [
            {"source": r["source"], "score": r["score"], "preview": r["preview"]}
            for r in results
        ]
        print(json.dumps(clean, ensure_ascii=False, indent=2))
    else:
        print(_format_markdown(results))

    return 0


if __name__ == "__main__":
    sys.exit(main())
