#!/usr/bin/env python3
"""
MCP server for local memory search.

Replaces the broken ai-memory Rust binary that was hardcoded to OpenAI.
Uses local Sentence Transformers (all-MiniLM-L6-v2) — no API keys, no quota.

Tools exposed:
  memory_search(query, top_k=5)  — semantic search across MEMORY.md + memory/*.md
  memory_get(filename)           — return raw content of a specific memory file
"""

import os
import sys
import glob
import json
from pathlib import Path
from typing import Optional

# Ensure venv packages are on path
_VENV = Path(__file__).parent.parent / "venv" / "lib" / "python3.14" / "site-packages"
if _VENV.exists():
    sys.path.insert(0, str(_VENV))

import numpy as np
from sentence_transformers import SentenceTransformer
from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

WORKSPACE = Path(os.environ.get("OPENCLAW_WORKSPACE", Path.home() / ".openclaw" / "workspace"))
MODEL_NAME = "all-MiniLM-L6-v2"
DEFAULT_TOP_K = 5
CHUNK_SIZE = 500  # chars
CHUNK_OVERLAP = 2  # lines kept for overlap between chunks

# ---------------------------------------------------------------------------
# Embedding / search engine (module-level singleton, lazy-loaded)
# ---------------------------------------------------------------------------

_model: Optional[SentenceTransformer] = None
_index: list = []  # list of {"source": str, "chunk": str, "embedding": np.ndarray}
_index_mtime: dict = {}  # filename → mtime, used to detect stale index


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        # local_files_only=True skips HuggingFace network checks on every startup
        _model = SentenceTransformer(MODEL_NAME, local_files_only=True)
    return _model


def _memory_files() -> list[Path]:
    files: list[Path] = []
    top = WORKSPACE / "MEMORY.md"
    if top.exists():
        files.append(top)
    mem_dir = WORKSPACE / "memory"
    if mem_dir.exists():
        files.extend(sorted(mem_dir.glob("*.md")))
    return files


def _chunk_text(text: str) -> list[str]:
    """Split text into overlapping char-size chunks."""
    lines = text.split("\n")
    chunks: list[str] = []
    current: list[str] = []
    current_size = 0

    for line in lines:
        current.append(line)
        current_size += len(line)
        if current_size >= CHUNK_SIZE:
            chunks.append("\n".join(current))
            current = current[-CHUNK_OVERLAP:] if len(current) > CHUNK_OVERLAP else []
            current_size = sum(len(l) for l in current)

    if current:
        chunks.append("\n".join(current))

    return chunks or [text]  # always return at least one chunk


def _needs_reindex() -> bool:
    """Return True if any memory file is newer than the cached mtime."""
    for f in _memory_files():
        mtime = f.stat().st_mtime
        if _index_mtime.get(str(f)) != mtime:
            return True
    return len(_index) == 0


def _build_index() -> None:
    """(Re)build the in-memory embedding index from all memory files."""
    global _index, _index_mtime
    model = _get_model()
    files = _memory_files()

    new_chunks: list[dict] = []
    new_mtime: dict = {}

    for filepath in files:
        try:
            content = filepath.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        rel = str(filepath.relative_to(WORKSPACE))
        for chunk in _chunk_text(content):
            new_chunks.append({"source": rel, "chunk": chunk})
        new_mtime[str(filepath)] = filepath.stat().st_mtime

    if not new_chunks:
        _index = []
        _index_mtime = new_mtime
        return

    texts = [c["chunk"] for c in new_chunks]
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)

    for i, entry in enumerate(new_chunks):
        entry["embedding"] = embeddings[i]

    _index = new_chunks
    _index_mtime = new_mtime


def _cosine_scores(query_emb: np.ndarray) -> np.ndarray:
    """Return cosine similarity between query_emb and every indexed chunk."""
    if not _index:
        return np.array([])
    matrix = np.stack([e["embedding"] for e in _index])  # (N, D)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    query_norm = np.linalg.norm(query_emb)
    if query_norm == 0:
        return np.zeros(len(_index))
    safe_norms = np.where(norms == 0, 1, norms)
    return (matrix / safe_norms) @ query_emb / query_norm


def semantic_search(query: str, top_k: int = DEFAULT_TOP_K) -> list[dict]:
    """
    Core search function — build/refresh index then rank chunks by similarity.

    Returns list of dicts: {source, score, text, preview}
    """
    if _needs_reindex():
        _build_index()

    if not _index:
        return []

    model = _get_model()
    query_emb = model.encode(query, convert_to_numpy=True)
    scores = _cosine_scores(query_emb)

    top_indices = np.argsort(scores)[::-1][:top_k]
    results = []
    for idx in top_indices:
        entry = _index[int(idx)]
        results.append({
            "source": entry["source"],
            "score": round(float(scores[idx]), 4),
            "text": entry["chunk"],
            "preview": entry["chunk"][:200] + ("..." if len(entry["chunk"]) > 200 else ""),
        })

    return results


def get_memory_file(filename: str) -> Optional[str]:
    """
    Return the raw content of a memory file by relative filename.
    Accepts bare filename (e.g. 'feedback_testing.md') or relative path
    (e.g. 'memory/feedback_testing.md').
    Returns None if the file doesn't exist.
    """
    candidate = WORKSPACE / filename
    if candidate.exists() and candidate.is_file():
        return candidate.read_text(encoding="utf-8")

    # Try inside memory/ subdirectory as a convenience
    candidate2 = WORKSPACE / "memory" / filename
    if candidate2.exists() and candidate2.is_file():
        return candidate2.read_text(encoding="utf-8")

    return None


# ---------------------------------------------------------------------------
# MCP server definition
# ---------------------------------------------------------------------------

mcp = FastMCP(
    name="memory",
    instructions=(
        "Provides semantic search over the agent's persistent memory files "
        "(MEMORY.md and memory/*.md). Use memory_search to find relevant context "
        "by natural-language query. Use memory_get to retrieve a specific file."
    ),
)


@mcp.tool()
def memory_search(query: str, top_k: int = DEFAULT_TOP_K) -> str:
    """
    Semantically search the agent's persistent memory files.

    Args:
        query:  Natural-language search query.
        top_k:  Maximum number of results to return (default 5, max 20).

    Returns:
        JSON array of results, each with: source, score, preview, text.
        Returns an empty array JSON string if nothing is indexed.
    """
    top_k = max(1, min(top_k, 20))
    results = semantic_search(query, top_k=top_k)
    return json.dumps(results, ensure_ascii=False, indent=2)


@mcp.tool()
def memory_get(filename: str) -> str:
    """
    Retrieve the raw Markdown content of a specific memory file.

    Args:
        filename:  Relative path such as 'MEMORY.md', 'memory/user_role.md',
                   or just the bare filename 'user_role.md'.

    Returns:
        File contents as a string, or an error message if not found.
    """
    content = get_memory_file(filename)
    if content is None:
        available = [str(f.relative_to(WORKSPACE)) for f in _memory_files()]
        return json.dumps({
            "error": f"File not found: {filename}",
            "available_files": available,
        }, ensure_ascii=False, indent=2)
    return content


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="stdio")
