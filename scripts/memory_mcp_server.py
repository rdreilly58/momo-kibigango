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
import subprocess
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

# Ensure venv packages are on path
_VENV = Path(__file__).parent.parent / "venv" / "lib" / "python3.14" / "site-packages"
if _VENV.exists():
    sys.path.insert(0, str(_VENV))

# Ensure Homebrew bin is on PATH (MCP servers launched by OpenClaw may have stripped PATH)
os.environ["PATH"] = "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:" + os.environ.get("PATH", "")

import numpy as np
from sentence_transformers import SentenceTransformer
from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

WORKSPACE = Path(os.environ.get("OPENCLAW_WORKSPACE", Path.home() / ".openclaw" / "workspace"))
MODEL_NAME = "all-MiniLM-L6-v2"

EMAIL_ACCOUNTS = [
    "rdreilly2010@gmail.com",
    "reillyrd58@gmail.com",
    "robert@reillydesignstudio.com",
]
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

import subprocess
import shutil
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

_TZ = ZoneInfo("America/New_York")

# Email accounts known to the system
_EMAIL_ACCOUNTS = [
    "rdreilly2010@gmail.com",
    "reillyrd58@gmail.com",
    "robert@reillydesignstudio.com",
]
_DEFAULT_CALENDAR_ACCOUNT = "rdreilly2010@gmail.com"


def _run(cmd: str, timeout: int = 15) -> tuple[int, str, str]:
    """Run a shell command, return (returncode, stdout, stderr)."""
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def _gog_available() -> bool:
    return shutil.which("gog") is not None


def _resolve_accounts(account: str) -> list[str]:
    """Return list of account email addresses to query."""
    if account == "all":
        return list(_EMAIL_ACCOUNTS)
    if account in _EMAIL_ACCOUNTS:
        return [account]
    # Allow short label match
    for a in _EMAIL_ACCOUNTS:
        if account in a:
            return [a]
    return [account]  # pass through unknown, let gog error


mcp = FastMCP(
    name="memory",
    instructions=(
        "Provides tiered semantic search over persistent memory (Hot LRU cache + "
        "LanceDB warm vector store + SQLite cold archive). Use memory_search for "
        "hybrid RRF search. Use memory_get to retrieve a specific file. "
        "Use memory_store to save new memories. Use memory_stats to see tier health. "
        "Also provides live email and calendar tools: email_list_unread, "
        "email_search, email_read, calendar_today, calendar_range."
    ),
)

# Lazy TierManager — only initialised when first memory tool is called
_tier_manager = None


def _get_tier_manager():
    global _tier_manager
    if _tier_manager is None:
        scripts_dir = Path(__file__).parent
        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))
        from memory_tier_manager import TierManager
        _tier_manager = TierManager()
    return _tier_manager


@mcp.tool()
def memory_search(query: str, top_k: int = DEFAULT_TOP_K, include_cold: bool = False) -> str:
    """
    Tiered hybrid semantic search across Hot cache, LanceDB warm store, and
    optionally SQLite cold archive.

    Uses Reciprocal Rank Fusion of vector similarity + BM25 full-text scores
    weighted by memory priority.

    Args:
        query:        Natural-language search query.
        top_k:        Maximum results (default 5, max 20).
        include_cold: Also search archived (cold) memories via FTS5 (default False).

    Returns:
        JSON array of results, each with: title, content, namespace, _score, _tier.
    """
    top_k = max(1, min(top_k, 20))
    try:
        mgr = _get_tier_manager()
        results = mgr.search(query, k=top_k, include_cold=include_cold)
        # Add preview field for backwards compatibility
        for r in results:
            if "preview" not in r:
                content = str(r.get("content", ""))
                r["preview"] = content[:200] + ("..." if len(content) > 200 else "")
        return json.dumps(results, ensure_ascii=False, indent=2)
    except Exception as exc:
        # Fall back to legacy flat-file search if tier manager fails
        results = semantic_search(query, top_k=top_k)
        return json.dumps({"results": results, "fallback": True, "error": str(exc)},
                          ensure_ascii=False, indent=2)


@mcp.tool()
def memory_store(
    title: str,
    content: str,
    namespace: str = "workspace",
    tier: str = "short",
    tags: str = "",
    priority: int = 5,
) -> str:
    """
    Store a new memory in all tiers (SQLite + LanceDB warm vector index).

    Args:
        title:     Short descriptive title.
        content:   Full memory content.
        namespace: Logical namespace (workspace, personal, projects/name, etc.).
        tier:      Memory tier: working (7-day TTL), short, or long.
        tags:      Comma-separated tags.
        priority:  Priority 1-10 (default 5).

    Returns:
        JSON with {id, status}.
    """
    try:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        mgr = _get_tier_manager()
        mem_id = mgr.store(title, content, namespace=namespace, tier=tier,
                           tags=tag_list, priority=priority)
        return json.dumps({"id": mem_id, "status": "stored"}, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"error": str(exc)}, ensure_ascii=False)


@mcp.tool()
def memory_stats() -> str:
    """
    Return health metrics for all memory tiers.

    Returns:
        JSON with hot cache hit rate, warm store record count, cold archive count,
        SQLite tier breakdown, and session search count.
    """
    try:
        mgr = _get_tier_manager()
        return json.dumps(mgr.stats(), ensure_ascii=False, indent=2)
    except Exception as exc:
        return json.dumps({"error": str(exc)}, ensure_ascii=False)


@mcp.tool()
def memory_promote(memory_id: str) -> str:
    """
    Promote a cold (archived) memory back to the warm tier.
    Recomputes its embedding and re-indexes it in LanceDB.

    Args:
        memory_id: The UUID of the archived memory.

    Returns:
        JSON with the promoted memory dict or {error}.
    """
    try:
        mgr = _get_tier_manager()
        result = mgr.promote_to_warm(memory_id)
        if result is None:
            return json.dumps({"error": f"Memory {memory_id} not found in cold store"})
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as exc:
        return json.dumps({"error": str(exc)}, ensure_ascii=False)


@mcp.tool()
def memory_rebuild_index() -> str:
    """
    Rebuild the LanceDB warm vector index from scratch by re-reading all
    SQLite memories and recomputing their embeddings.

    Returns:
        JSON with {synced: N, status}.
    """
    try:
        mgr = _get_tier_manager()
        n = mgr.rebuild_warm_index()
        return json.dumps({"synced": n, "status": "ok"}, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"error": str(exc)}, ensure_ascii=False)


@mcp.tool()
def memory_graph_search(query: str, depth: int = 1) -> str:
    """
    Graph-augmented memory search: semantic search + BFS link expansion.

    First finds semantically similar memory chunks (seeds), then traverses
    their graph links up to `depth` hops to surface related entities and
    session nodes.

    Args:
        query:  Natural-language search query.
        depth:  BFS expansion depth after seed retrieval (default 1, max 2).

    Returns:
        JSON with {"seeds": [...], "graph": [...]} — seeds are ranked by
        semantic similarity; graph nodes are linked neighbours.
    """
    import sys
    from pathlib import Path

    depth = max(0, min(depth, 2))

    # Seed phase: semantic search
    seeds = semantic_search(query, top_k=5)

    if not seeds or depth == 0:
        return json.dumps({"seeds": seeds, "graph": []}, ensure_ascii=False, indent=2)

    # Graph expansion via memory_db
    scripts_dir = Path(__file__).parent
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))

    try:
        from memory_db import MemoryDB  # type: ignore

        db = MemoryDB()
        seen_ids: set = set()
        graph_nodes = []

        for seed in seeds:
            # Map chunk source file → try to find memory DB entries by title/content
            source = seed.get("source", "")
            fts_hits = db.search_fts(query, limit=3)
            for hit in fts_hits:
                hit_id = hit["id"]
                if hit_id in seen_ids:
                    continue
                seen_ids.add(hit_id)
                neighbors = db.traverse(hit_id, depth=depth)
                for n in neighbors:
                    nid = n["memory"]["id"]
                    if nid not in seen_ids:
                        seen_ids.add(nid)
                        graph_nodes.append({
                            "title": n["memory"]["title"],
                            "content": n["memory"]["content"][:200],
                            "depth": n["depth"],
                            "relation": n["relation"],
                            "direction": n["direction"],
                        })
    except Exception as exc:
        return json.dumps({"seeds": seeds, "graph": [], "error": str(exc)},
                          ensure_ascii=False, indent=2)

    return json.dumps({
        "seeds": [{"source": s["source"], "score": s["score"], "preview": s["preview"]}
                  for s in seeds],
        "graph": graph_nodes,
    }, ensure_ascii=False, indent=2)


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
# Email + Calendar MCP tools
# ---------------------------------------------------------------------------

@mcp.tool()
def email_list_unread(account: str = "all") -> str:
    """
    List unread and important emails from one or all Gmail accounts.

    Args:
        account: Email address, short label (e.g. 'rdreilly2010'), or 'all'
                 (default). Known accounts: rdreilly2010@gmail.com,
                 reillyrd58@gmail.com, robert@reillydesignstudio.com.

    Returns:
        JSON object keyed by account with lists of {from, subject, date, flags}.
    """
    if not _gog_available():
        return json.dumps({"error": "gog CLI not found on PATH"})

    accounts = _resolve_accounts(account)
    results: dict = {}

    for acct in accounts:
        code, out, err = _run(f"gog gmail search 'is:unread' -a {acct} --json", timeout=20)
        if code != 0:
            results[acct] = {"error": err[:200] or "gog returned non-zero"}
            continue
        try:
            data = json.loads(out)
            msgs = data.get("messages", data.get("threads", []))
            results[acct] = [
                {
                    "id": m.get("id", ""),
                    "from": m.get("from", ""),
                    "subject": m.get("subject", "(no subject)"),
                    "date": m.get("date", ""),
                    "flags": [l for l in m.get("labels", []) if l in ("IMPORTANT", "STARRED")],
                }
                for m in msgs[:15]
            ]
        except (json.JSONDecodeError, Exception) as exc:
            results[acct] = {"error": str(exc), "raw": out[:300]}

    return json.dumps(results, ensure_ascii=False, indent=2)


@mcp.tool()
def email_search(query: str, account: str = "all", max_results: int = 10) -> str:
    """
    Search email using a Gmail search query across one or all accounts.

    Args:
        query:       Gmail search string, e.g. 'from:boss subject:meeting'.
        account:     Account email, short label, or 'all' (default).
        max_results: Cap per account (default 10, max 25).

    Returns:
        JSON object keyed by account, each with a list of matching messages.
    """
    if not _gog_available():
        return json.dumps({"error": "gog CLI not found on PATH"})

    max_results = max(1, min(max_results, 25))
    accounts = _resolve_accounts(account)
    results: dict = {}

    for acct in accounts:
        safe_query = query.replace("'", "'\\''")
        code, out, err = _run(f"gog gmail search '{safe_query}' -a {acct} --json", timeout=20)
        if code != 0:
            results[acct] = {"error": err[:200] or "gog returned non-zero"}
            continue
        try:
            data = json.loads(out)
            msgs = data.get("messages", data.get("threads", []))
            results[acct] = [
                {
                    "id": m.get("id", ""),
                    "from": m.get("from", ""),
                    "subject": m.get("subject", "(no subject)"),
                    "date": m.get("date", ""),
                    "snippet": m.get("snippet", m.get("subject", ""))[:200],
                }
                for m in msgs[:max_results]
            ]
        except (json.JSONDecodeError, Exception) as exc:
            results[acct] = {"error": str(exc)}

    return json.dumps(results, ensure_ascii=False, indent=2)


@mcp.tool()
def email_read(message_id: str, account: str) -> str:
    """
    Fetch the full body of a specific email message.

    Args:
        message_id: The message ID returned by email_list_unread or email_search.
        account:    The account email address that owns this message.

    Returns:
        JSON with {from, to, subject, date, body} or {error}.
    """
    if not _gog_available():
        return json.dumps({"error": "gog CLI not found on PATH"})

    safe_id = message_id.replace("'", "").replace(";", "").replace("&", "").replace("$", "").replace("(", "").replace(")", "")
    safe_acct = account.replace("'", "")
    code, out, err = _run(f"gog gmail read '{safe_id}' -a {safe_acct} --json", timeout=20)

    if code != 0:
        return json.dumps({"error": err[:300] or "gog returned non-zero", "message_id": message_id})

    try:
        data = json.loads(out)
        return json.dumps({
            "from": data.get("from", ""),
            "to": data.get("to", ""),
            "subject": data.get("subject", "(no subject)"),
            "date": data.get("date", ""),
            "body": data.get("body", data.get("text", data.get("snippet", "")))[:4000],
        }, ensure_ascii=False, indent=2)
    except json.JSONDecodeError:
        # gog may return plain text for some messages
        return json.dumps({"body": out[:4000]})


@mcp.tool()
def calendar_today(account: str = _DEFAULT_CALENDAR_ACCOUNT) -> str:
    """
    Fetch today's remaining calendar events plus tomorrow morning events.

    Args:
        account: Google Calendar account to query
                 (default rdreilly2010@gmail.com).

    Returns:
        JSON with {today: [...], tomorrow_morning: [...]} each event has
        {title, time, location}.
    """
    if not _gog_available():
        return json.dumps({"error": "gog CLI not found on PATH"})

    code, out, err = _run(f"gog calendar list -a {account} --json", timeout=20)
    if code != 0:
        return json.dumps({"error": err[:200] or "gog calendar unavailable"})

    try:
        data = json.loads(out)
        events = data.get("events", data.get("items", []))
    except json.JSONDecodeError:
        return json.dumps({"error": "JSON parse error", "raw": out[:300]})

    now = datetime.now(_TZ)
    today = now.date()
    tomorrow = today + timedelta(days=1)
    today_events, tomorrow_events = [], []

    for ev in events:
        start = ev.get("start", {})
        summary = ev.get("summary", "Untitled")
        location = ev.get("location", "")

        if "dateTime" in start:
            try:
                dt = datetime.fromisoformat(start["dateTime"]).astimezone(_TZ)
                ev_date = dt.date()
                if ev_date == today and dt < now:
                    continue  # already past
                time_str = dt.strftime("%-I:%M %p")
            except Exception:
                ev_date = None
                time_str = start["dateTime"][:16]
        elif "date" in start:
            try:
                from datetime import date as _date
                ev_date = _date.fromisoformat(start["date"])
                time_str = "All day"
            except Exception:
                ev_date = None
                time_str = ""
        else:
            continue

        if ev_date is None:
            continue

        entry = {"title": summary, "time": time_str, "location": location}

        if ev_date == today:
            today_events.append(entry)
        elif ev_date == tomorrow:
            # only morning (before noon)
            if time_str == "All day":
                tomorrow_events.append(entry)
            elif "dateTime" in start:
                try:
                    h = datetime.fromisoformat(start["dateTime"]).astimezone(_TZ).hour
                    if h < 12:
                        tomorrow_events.append(entry)
                except Exception:
                    pass

    return json.dumps({
        "today": today_events[:10],
        "tomorrow_morning": tomorrow_events[:5],
        "as_of": now.strftime("%Y-%m-%d %H:%M %Z"),
    }, ensure_ascii=False, indent=2)


@mcp.tool()
def calendar_range(start_date: str, end_date: str, account: str = _DEFAULT_CALENDAR_ACCOUNT) -> str:
    """
    Fetch calendar events between two dates (inclusive).

    Args:
        start_date: ISO date string, e.g. '2026-04-22'.
        end_date:   ISO date string, e.g. '2026-04-29'.
        account:    Google Calendar account (default rdreilly2010@gmail.com).

    Returns:
        JSON {events: [{title, date, time, location}, ...], count: N}.
    """
    if not _gog_available():
        return json.dumps({"error": "gog CLI not found on PATH"})

    # Validate dates
    try:
        from datetime import date as _date
        d_start = _date.fromisoformat(start_date)
        d_end = _date.fromisoformat(end_date)
        if d_end < d_start:
            return json.dumps({"error": "end_date must be >= start_date"})
    except ValueError as exc:
        return json.dumps({"error": f"Invalid date: {exc}"})

    code, out, err = _run(f"gog calendar list -a {account} --json", timeout=20)
    if code != 0:
        return json.dumps({"error": err[:200] or "gog calendar unavailable"})

    try:
        data = json.loads(out)
        events = data.get("events", data.get("items", []))
    except json.JSONDecodeError:
        return json.dumps({"error": "JSON parse error"})

    from datetime import date as _date
    matched = []

    for ev in events:
        start = ev.get("start", {})
        summary = ev.get("summary", "Untitled")
        location = ev.get("location", "")

        if "dateTime" in start:
            try:
                dt = datetime.fromisoformat(start["dateTime"]).astimezone(_TZ)
                ev_date = dt.date()
                time_str = dt.strftime("%-I:%M %p")
            except Exception:
                continue
        elif "date" in start:
            try:
                ev_date = _date.fromisoformat(start["date"])
                time_str = "All day"
            except Exception:
                continue
        else:
            continue

        if d_start <= ev_date <= d_end:
            matched.append({
                "title": summary,
                "date": ev_date.isoformat(),
                "time": time_str,
                "location": location,
            })

    matched.sort(key=lambda e: (e["date"], e["time"]))
    return json.dumps({"events": matched, "count": len(matched)}, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="stdio")
