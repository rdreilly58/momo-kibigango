#!/usr/bin/env python3
"""
total_recall_search.py — Comprehensive search across memory and local disk.

Intelligently routes queries to:
  - Semantic memory search (Sentence Transformers over memory/*.md, MEMORY.md)
  - Keyword file search (momo-kioku-search via mdfind/Spotlight)
  - Or both, interleaved by Borda-count relevance voting.

Usage:
  python3 total_recall_search.py <query> [--type auto|semantic|keyword]
                                          [--limit N] [--path /some/dir]
                                          [--json]
                                          [--min-score 0.35]
                                          [--force-fs-search]
                                          [--quick]
                                          [--verbose]
                                          [--explain]
                                          [--index-dir /path]
                                          [--prune-old]
                                          [--no-cache]

Exit codes:
  0  Success (even if zero results)
  1  Unrecoverable error (both backends failed)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Literal, Optional, Tuple

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

WORKSPACE = Path.home() / ".openclaw" / "workspace"
VENV_PYTHON = WORKSPACE / "venv" / "bin" / "python3"

# Keyword search backend paths
KEYWORD_SEARCH_BIN = str(Path.home() / "bin" / "momo-kioku-search")
KEYWORD_FALLBACK_BIN = str(Path.home() / "bin" / "fast-find-improved.sh")

# Caching
CACHE_DIR = WORKSPACE / ".cache" / "total_recall_search"
CACHE_TTL_SECONDS = 300  # 5-minute TTL
MTIME_INDEX_FILE = CACHE_DIR / "mtime_index.json"

# Semantic defaults
DEFAULT_MIN_SCORE = 0.4
PRUNE_DAYS = 90  # Skip memory files older than this when --prune-old is used

# ---------------------------------------------------------------------------
# Regex heuristics (Pass 1 of two-pass classification)
# ---------------------------------------------------------------------------

# Patterns strongly suggesting file/path queries
_FILENAME_RE = re.compile(
    r"""
    /                                    # path separator
    | \.[a-zA-Z]{1,6}\b                 # file extension (.md, .py, .sh, .swift …)
    | \b(sh|py|js|ts|swift|md|json|yml|yaml|txt|log|toml|cfg|conf)\b
    | ^~                                 # tilde path
    | ^run_                              # script prefix
    | README | CHANGELOG | LICENSE | Makefile | Dockerfile | Gemfile | Rakefile
    | (total_recall_search\.py|run_total_recall_benchmarks\.sh|total-recall-search)
    """,
    re.VERBOSE | re.IGNORECASE,
)

# Patterns strongly suggesting semantic/conceptual queries
_SEMANTIC_RE = re.compile(
    r"""
    \b(why|how|when|what|who|explain|describe|tell\s+me|find\s+out
      |summarize|recall|remember|decision|reason|context|history
      |latest|update|status|progress|plan|strategy|goal|note)\b
    """,
    re.VERBOSE | re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Global state for verbose / explain modes (set by CLI)
# ---------------------------------------------------------------------------

_verbose: bool = False
_explain: bool = False


def _vlog(msg: str) -> None:
    if _verbose:
        print(f"[VERBOSE] {msg}", file=sys.stderr)


def _vlog_backend(backend: str, reason: str) -> None:
    if _verbose:
        print(f"[BACKEND] Using {backend}: {reason}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Caching (improvement 5)
# ---------------------------------------------------------------------------

def _cache_key(query: str, search_type: str, limit: int, path: Optional[str]) -> str:
    raw = f"{query}|{search_type}|{limit}|{path}"
    return hashlib.sha256(raw.encode()).hexdigest()[:20]


def _read_cache(key: str) -> Optional[List[Dict]]:
    f = CACHE_DIR / f"{key}.json"
    if not f.exists():
        return None
    try:
        age = time.time() - f.stat().st_mtime
        if age > CACHE_TTL_SECONDS:
            _vlog(f"Cache expired (age={age:.0f}s)")
            return None
        data = json.loads(f.read_text())
        _vlog(f"Cache HIT key={key} age={age:.0f}s")
        return data
    except Exception as e:
        _vlog(f"Cache read error: {e}")
        return None


def _write_cache(key: str, results: List[Dict]) -> None:
    # Don't cache error-only result sets
    if results and all(r.get("error") for r in results):
        return
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        (CACHE_DIR / f"{key}.json").write_text(json.dumps(results, ensure_ascii=False))
        _vlog(f"Cache WRITE key={key} ({len(results)} results)")
    except Exception as e:
        _vlog(f"Cache write error: {e}")


# ---------------------------------------------------------------------------
# Query classification — two-pass heuristic (improvement 2)
# ---------------------------------------------------------------------------

def classify_query(query: str) -> Tuple[str, str]:
    """
    Two-pass heuristic classification.

    Pass 1: Regex patterns (instant).
    Pass 2: Quick Spotlight probe for ambiguous 3–4 word queries (≤2s).

    Returns (classification, reason_string).
    """
    words = query.split()
    nw = len(words)

    has_file = bool(_FILENAME_RE.search(query))
    has_sem = bool(_SEMANTIC_RE.search(query))

    # Clear file pattern with no semantic override → keyword
    if has_file and not has_sem:
        return "keyword", "pass1-regex: filename/path pattern"

    # Clear semantic pattern with no file override → semantic
    if has_sem and not has_file:
        return "semantic", "pass1-regex: conceptual/prose pattern"

    # Short query (1–2 words, no strong signal) → keyword for discovery
    if nw <= 2:
        return "keyword", f"pass1-length: short query ({nw} words)"

    # Long query (6+ words, no strong file signal) → semantic
    if nw >= 6:
        return "semantic", f"pass1-length: long query ({nw} words)"

    # Ambiguous 3–5 word queries: Pass 2 — quick Spotlight probe
    if 3 <= nw <= 5:
        try:
            proc = subprocess.run(
                [KEYWORD_SEARCH_BIN, query, "3"],
                capture_output=True, text=True, timeout=2, stdin=subprocess.DEVNULL,
            )
            if any(l.strip().startswith("/") for l in proc.stdout.splitlines()):
                return "keyword", "pass2-spotlight: found file matches"
        except Exception:
            pass  # Probe failed — fall through to default

    return "semantic", f"pass1-default: medium query ({nw} words)"


# ---------------------------------------------------------------------------
# Keyword search — three-tier fallback (improvement 1)
# ---------------------------------------------------------------------------

def _keyword_search(
    query: str,
    limit: int,
    path: Optional[str],
    force_fs: bool = False,
    quick: bool = False,
) -> List[Dict]:
    """
    Keyword search with fallback chain:
      1. momo-kioku-search (Spotlight/mdfind) — unless --force-fs-search
      2. fast-find-improved.sh (non-interactive) — unless --force-fs-search
      3. Filesystem grep/find (always available)

    --force-fs-search skips tiers 1 & 2.
    --quick sets a 2-second timeout on all tiers.
    """
    timeout = 2 if quick else 30
    t_start = time.time()

    if not force_fs:
        # Tier 1: momo-kioku-search
        r1 = _tier1_momo_kioku(query, limit, path, timeout)
        if r1 is not None:
            _vlog_backend("momo-kioku-search", f"tier1 OK ({len(r1)} results, {time.time()-t_start:.2f}s)")
            return r1

        # Tier 2: fast-find-improved.sh
        _vlog("Tier1 failed; trying fast-find-improved.sh")
        r2 = _tier2_fast_find(query, limit, path, timeout)
        if r2 is not None:
            _vlog_backend("fast-find-improved.sh", f"tier2 OK ({len(r2)} results, {time.time()-t_start:.2f}s)")
            return r2

        _vlog("Tier2 failed; falling back to filesystem search")
    else:
        _vlog_backend("filesystem", "--force-fs-search: skipping Spotlight backends")

    # Tier 3: filesystem grep/find
    return _tier3_fs_search(query, limit, path, timeout)


def _tier1_momo_kioku(
    query: str, limit: int, path: Optional[str], timeout: int
) -> Optional[List[Dict]]:
    cmd = [KEYWORD_SEARCH_BIN, query, str(limit)]
    if path:
        cmd.append(path)
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
        return _parse_paths(p.stdout, backend="momo-kioku")
    except FileNotFoundError:
        _vlog("momo-kioku-search not found")
        return None
    except subprocess.TimeoutExpired:
        _vlog(f"momo-kioku-search timed out ({timeout}s)")
        return None
    except Exception as e:
        _vlog(f"momo-kioku-search error: {e}")
        return None


def _tier2_fast_find(
    query: str, limit: int, path: Optional[str], timeout: int
) -> Optional[List[Dict]]:
    try:
        cmd = ["bash", KEYWORD_FALLBACK_BIN, query, str(limit)]
        if path:
            cmd.append(path)
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
        return _parse_paths(p.stdout, backend="fast-find")
    except FileNotFoundError:
        _vlog("fast-find-improved.sh not found")
        return None
    except subprocess.TimeoutExpired:
        _vlog(f"fast-find-improved.sh timed out ({timeout}s)")
        return None
    except Exception as e:
        _vlog(f"fast-find-improved.sh error: {e}")
        return None


def _tier3_fs_search(
    query: str, limit: int, path: Optional[str], timeout: int
) -> List[Dict]:
    """Filesystem find + grep fallback. Always available."""
    search_root = path or str(Path.home())
    results: List[Dict] = []

    # Strategy A: find by filename
    try:
        terms = query.split()
        name_args: List[str] = []
        for i, term in enumerate(terms):
            if i > 0:
                name_args.append("-o")
            name_args.extend(["-iname", f"*{term}*"])

        cmd = (
            ["find", search_root, "("]
            + name_args
            + [")", "-type", "f",
               "!", "-path", "*/.git/*",
               "!", "-path", "*/.cache/*",
               "!", "-path", "*/node_modules/*",
               "!", "-path", "*/__pycache__/*"]
        )
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
        for line in p.stdout.splitlines():
            line = line.strip()
            if line.startswith("/"):
                results.append({
                    "type": "keyword",
                    "path": line,
                    "snippet": _file_snippet(line),
                    "score": 0.9,
                    "_backend": "fs-find",
                })
            if len(results) >= limit:
                break
    except Exception as e:
        _vlog(f"fs-find error: {e}")

    if results:
        _vlog_backend("filesystem-find", f"tier3 OK ({len(results)} results)")
        return results[:limit]

    # Strategy B: grep content in memory/workspace dirs
    grep_dirs = ([path] if path else [
        str(WORKSPACE / "memory"),
        str(WORKSPACE),
    ])
    try:
        for d in grep_dirs:
            if not Path(d).exists():
                continue
            cmd = [
                "grep", "-rl", "-i", "--include=*.md", "--include=*.txt",
                "--include=*.py", "--include=*.sh", query, d,
            ]
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
            for line in p.stdout.splitlines():
                line = line.strip()
                if line:
                    results.append({
                        "type": "keyword",
                        "path": line,
                        "snippet": _file_snippet(line),
                        "score": 0.7,
                        "_backend": "fs-grep",
                    })
                if len(results) >= limit:
                    break
            if len(results) >= limit:
                break
    except Exception as e:
        _vlog(f"fs-grep error: {e}")

    if results:
        _vlog_backend("filesystem-grep", f"tier3 OK ({len(results)} results)")
        return results[:limit]

    _vlog("All keyword backends exhausted — returning error")
    return [_error_result("keyword", f"All keyword backends failed for: {query!r}")]


def _parse_paths(stdout: str, backend: str = "keyword") -> List[Dict]:
    """Parse line-by-line path output from keyword backends."""
    results: List[Dict] = []
    for line in stdout.splitlines():
        line = line.strip()
        if not line or not line.startswith("/"):
            continue
        results.append({
            "type": "keyword",
            "path": line,
            "snippet": _file_snippet(line),
            "score": 1.0,
            "_backend": backend,
        })
    return results  # empty list is fine (not None)


def _file_snippet(path: str, nlines: int = 2) -> str:
    """Return the first N non-empty lines of a file as a snippet."""
    try:
        with open(path, "r", errors="replace") as fh:
            collected: List[str] = []
            for line in fh:
                s = line.rstrip()
                if s:
                    collected.append(s)
                if len(collected) >= nlines:
                    break
        return "\n".join(collected) if collected else "(empty file)"
    except Exception as e:
        return f"(could not read: {e})"


# ---------------------------------------------------------------------------
# Semantic search — lazy-loaded model, dynamic threshold (improvements 3, 5, 6)
# ---------------------------------------------------------------------------

_loaded_model = None  # Lazy-loaded Sentence Transformers model


def _get_model():
    """Lazy-load the SentenceTransformer model (cached globally)."""
    global _loaded_model
    if _loaded_model is None:
        _vlog("Loading sentence-transformers model (all-MiniLM-L6-v2)…")
        t0 = time.time()
        from sentence_transformers import SentenceTransformer  # type: ignore
        _loaded_model = SentenceTransformer("all-MiniLM-L6-v2")
        _vlog(f"Model loaded in {time.time() - t0:.1f}s")
    return _loaded_model


def _semantic_search(
    query: str,
    limit: int,
    min_score: float = DEFAULT_MIN_SCORE,
    index_dirs: Optional[List[str]] = None,
    prune_old: bool = False,
    dynamic_threshold: bool = True,
) -> List[Dict]:
    """
    Semantic search via subprocess (memory_search_local.py) with inline fallback.

    Features:
      - Configurable min_score (--min-score)
      - Dynamic threshold: if 0 results, retry at 70% of threshold
      - Extra index dirs (--index-dir)
      - Pruning of old memory files (--prune-old)
    """
    script = WORKSPACE / "scripts" / "memory_search_local.py"
    python = str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable

    results: List[Dict] = []

    if script.exists():
        try:
            proc = subprocess.run(
                [python, str(script), "--json", "--limit", str(limit * 2), query],
                capture_output=True, text=True, timeout=120,
            )
            raw = proc.stdout.strip()
            if raw:
                data = json.loads(raw)
                results = [_normalise_semantic(r) for r in data]
        except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
            _vlog(f"Subprocess semantic failed ({e}), falling back to inline")
            results = []

    if not results:
        _vlog("Subprocess semantic empty/failed — running inline")
        results = _semantic_inline(query, limit * 2, index_dirs=index_dirs, prune_old=prune_old)

    # Apply threshold
    filtered = [r for r in results if r.get("score", 0.0) >= min_score and not r.get("error")]
    errors = [r for r in results if r.get("error")]

    _vlog(f"Semantic: {len(results)} raw → {len(filtered)} ≥ {min_score}")

    # Dynamic threshold: lower if zero non-error results
    if dynamic_threshold and not filtered and results and not errors:
        lowered = round(min_score * 0.7, 3)
        filtered = [r for r in results if r.get("score", 0.0) >= lowered]
        if filtered:
            _vlog(f"Dynamic threshold {min_score} → {lowered}: {len(filtered)} results")
            for r in filtered:
                r["_dynamic_threshold"] = lowered

    return (filtered[:limit] + errors) if filtered else (errors or [])


def _semantic_inline(
    query: str,
    limit: int,
    index_dirs: Optional[List[str]] = None,
    prune_old: bool = False,
) -> List[Dict]:
    """Inline Sentence Transformers search (lazy model load)."""
    try:
        # Extend sys.path with workspace venv
        venv_site = WORKSPACE / "venv" / "lib"
        if venv_site.exists():
            for sp in venv_site.glob("python*/site-packages"):
                if str(sp) not in sys.path:
                    sys.path.insert(0, str(sp))

        model = _get_model()
        mem_files = _load_memory_files(extra_dirs=index_dirs, prune_old=prune_old)
        chunks = _build_chunks(mem_files)

        if not chunks:
            return []

        q_emb = model.encode(query)
        texts = [c["text"] for c in chunks]
        embs = model.encode(texts)

        scored: List[Dict] = []
        for i, chunk in enumerate(chunks):
            sc = _cosine(q_emb, embs[i])
            scored.append({
                "type": "semantic",
                "path": _resolve_mem_path(chunk["source"]),
                "snippet": chunk["text"][:200].strip(),
                "score": round(float(sc), 4),
                "source_line": chunk.get("index", 0) * 10,
            })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:limit]

    except ImportError:
        return [_error_result(
            "semantic",
            "sentence-transformers not installed. "
            "Run: cd ~/.openclaw/workspace && source venv/bin/activate && "
            "pip install sentence-transformers",
        )]
    except Exception as e:
        return [_error_result("semantic", f"Inline semantic failed: {e}")]


def _normalise_semantic(raw: Dict) -> Dict:
    source = raw.get("source", "unknown")
    return {
        "type": "semantic",
        "path": _resolve_mem_path(source),
        "snippet": raw.get("text", "")[:200].strip(),
        "score": round(float(raw.get("score", 0.0)), 4),
        "source_line": raw.get("index", 0),
    }


# ---------------------------------------------------------------------------
# Memory file loading — incremental mtime tracking + pruning (improvement 6)
# ---------------------------------------------------------------------------

def _load_memory_files(
    extra_dirs: Optional[List[str]] = None,
    prune_old: bool = False,
) -> Dict[str, str]:
    """
    Load memory files for indexing.

    - extra_dirs: additional directories to scan for *.md
    - prune_old: skip files with mtime > PRUNE_DAYS days old
    """
    files: Dict[str, str] = {}

    # Core memory files (always included)
    for cand in [
        WORKSPACE / "MEMORY.md",
        WORKSPACE / "MEMORY.CORE.md",
        WORKSPACE / "memory" / "observations.md",
    ]:
        if cand.exists():
            try:
                files[cand.name] = cand.read_text(errors="replace")
            except Exception:
                pass

    # Daily memory dir
    mem_dir = WORKSPACE / "memory"
    if mem_dir.exists():
        for p in sorted(mem_dir.glob("*.md")):
            if p.name in files:
                continue
            if prune_old:
                try:
                    age_days = (time.time() - p.stat().st_mtime) / 86400
                    if age_days > PRUNE_DAYS:
                        _vlog(f"Pruning {p.name} (age={age_days:.0f}d > {PRUNE_DAYS}d)")
                        continue
                except Exception:
                    pass
            try:
                files[p.name] = p.read_text(errors="replace")
            except Exception:
                pass

    # Extra user-specified directories
    if extra_dirs:
        for d in extra_dirs:
            dp = Path(d)
            if not dp.exists():
                _vlog(f"--index-dir not found: {d}")
                continue
            for p in sorted(dp.rglob("*.md")):
                key = str(p)
                if key not in files:
                    if prune_old:
                        try:
                            age_days = (time.time() - p.stat().st_mtime) / 86400
                            if age_days > PRUNE_DAYS:
                                _vlog(f"Pruning {p.name} (age={age_days:.0f}d > {PRUNE_DAYS}d)")
                                continue
                        except Exception:
                            pass
                    try:
                        files[key] = p.read_text(errors="replace")
                        _vlog(f"Indexed extra: {p}")
                    except Exception:
                        pass

    _vlog(f"Loaded {len(files)} memory files")
    return files


def _get_changed_files(mem_dir: Path) -> List[Path]:
    """
    Incremental indexing: return files changed since last index run.
    Uses mtime_index.json to track previous mtimes.
    """
    mtime_idx = {}
    if MTIME_INDEX_FILE.exists():
        try:
            mtime_idx = json.loads(MTIME_INDEX_FILE.read_text())
        except Exception:
            pass

    changed: List[Path] = []
    new_idx: Dict[str, float] = {}

    for p in mem_dir.glob("*.md"):
        try:
            mt = p.stat().st_mtime
            new_idx[str(p)] = mt
            if mtime_idx.get(str(p)) != mt:
                changed.append(p)
        except Exception:
            pass

    # Save updated index
    try:
        MTIME_INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
        MTIME_INDEX_FILE.write_text(json.dumps(new_idx))
    except Exception:
        pass

    _vlog(f"Incremental: {len(changed)}/{len(new_idx)} files changed")
    return changed


def _build_chunks(memory_files: Dict[str, str], chunk_size: int = 500) -> List[Dict]:
    chunks: List[Dict] = []
    for source, text in memory_files.items():
        lines = text.split("\n")
        buf: List[str] = []
        size = 0
        idx = 0
        for line in lines:
            buf.append(line)
            size += len(line)
            if size >= chunk_size:
                chunks.append({"text": "\n".join(buf), "source": source, "index": idx})
                buf = buf[-5:]
                size = sum(len(l) for l in buf)
                idx += 1
        if buf:
            chunks.append({"text": "\n".join(buf), "source": source, "index": idx})
    return chunks


def _resolve_mem_path(source: str) -> str:
    p = Path(source)
    if p.is_absolute():
        return str(p)
    for base in [WORKSPACE, WORKSPACE / "memory"]:
        cand = base / source
        if cand.exists():
            return str(cand)
    return str(WORKSPACE / source)


# ---------------------------------------------------------------------------
# Math helpers
# ---------------------------------------------------------------------------

def _cosine(a, b) -> float:
    dot = sum(float(x) * float(y) for x, y in zip(a, b))
    ma = math.sqrt(sum(float(x) ** 2 for x in a))
    mb = math.sqrt(sum(float(x) ** 2 for x in b))
    return (dot / (ma * mb)) if ma and mb else 0.0


# ---------------------------------------------------------------------------
# Error result
# ---------------------------------------------------------------------------

def _db_fts_search(query: str, limit: int = 10) -> List[Dict]:
    """Search ai-memory.db via FTS5. Returns results in total_recall format."""
    try:
        import sqlite3 as _sqlite3, json as _json
        _db_path = Path.home() / ".openclaw" / "workspace" / "ai-memory.db"
        if not _db_path.exists():
            return []
        con = _sqlite3.connect(_db_path)
        con.row_factory = _sqlite3.Row
        rows = con.execute(
            """SELECT m.id, m.tier, m.namespace, m.title, m.content,
                      snippet(memories_fts, 1, '[', ']', '...', 20) AS snippet
               FROM memories_fts
               JOIN memories m ON m.id = memories_fts.rowid
               WHERE memories_fts MATCH ?
               ORDER BY rank LIMIT ?""",
            (query, limit),
        ).fetchall()
        con.close()
        results = []
        for row in rows:
            results.append({
                "source": "ai-memory.db",
                "path": f"ai-memory.db::{row['namespace']}::{row['id'][:8]}",
                "score": 0.7,  # FTS rank not numeric; assign a solid default
                "snippet": row["snippet"] or row["content"][:200],
                "title": row["title"],
                "tier": row["tier"],
                "namespace": row["namespace"],
                "backend": "db-fts",
            })
        _vlog(f"DB FTS: {len(results)} results for '{query}'")
        return results
    except Exception as e:
        _vlog(f"DB FTS error: {e}")
        return []


def _error_result(backend: str, msg: str) -> Dict:
    return {
        "type": backend,
        "path": "(error)",
        "snippet": f"ERROR: {msg}",
        "score": 0.0,
        "error": True,
    }


# ---------------------------------------------------------------------------
# Result merging — Borda count with file diversity (improvement 4)
# ---------------------------------------------------------------------------

def _borda_merge(
    keyword_results: List[Dict],
    semantic_results: List[Dict],
    limit: int,
) -> List[Dict]:
    """
    Relevance-weighted Borda count interleaving with file diversity.

    Each list contributes Borda points = (N - rank) * actual_score.
    Results from the same file get a diversity penalty after first appearance.
    """
    kw_ok  = [r for r in keyword_results  if not r.get("error")]
    kw_err = [r for r in keyword_results  if r.get("error")]
    se_ok  = [r for r in semantic_results if not r.get("error")]
    se_err = [r for r in semantic_results if r.get("error")]

    if not kw_ok and not se_ok:
        return kw_err + se_err

    # Accumulate Borda scores keyed by path
    borda: Dict[str, float] = {}
    rep: Dict[str, Dict] = {}   # path → best result dict

    for rank, r in enumerate(kw_ok):
        path = r["path"]
        pts = (len(kw_ok) - rank) * r.get("score", 1.0)
        borda[path] = borda.get(path, 0.0) + pts
        rep.setdefault(path, r)

    for rank, r in enumerate(se_ok):
        path = r["path"]
        pts = (len(se_ok) - rank) * r.get("score", 0.5)
        borda[path] = borda.get(path, 0.0) + pts
        rep.setdefault(path, r)

    # Sort by Borda score
    ranked = sorted(borda.keys(), key=lambda p: borda[p], reverse=True)

    # File-diversity pass: penalise same-file duplicates
    seen_files: Dict[str, int] = {}  # basename → count
    out: List[Dict] = []
    for path in ranked:
        base = Path(path).name
        count = seen_files.get(base, 0)
        if count > 0:
            borda[path] *= max(0.1, 1.0 - 0.3 * count)  # 30% penalty per repeat file
        seen_files[base] = count + 1

        result = dict(rep[path])  # copy
        result["_borda_score"] = round(borda[path], 4)

        if _explain:
            result["_explain"] = {
                "borda_score": result["_borda_score"],
                "original_score": result.get("score", 0),
                "result_type": result.get("type"),
                "diversity_penalty": count > 0,
            }

        out.append(result)
        if len(out) >= limit:
            break

    return out + kw_err + se_err


# ---------------------------------------------------------------------------
# Result metadata (improvement 7)
# ---------------------------------------------------------------------------

def _attach_meta(results: List[Dict], backend: str, latency_s: float) -> List[Dict]:
    """Attach _meta dict with backend, confidence, latency_ms to every result."""
    latency_ms = round(latency_s * 1000, 1)
    for r in results:
        score = r.get("score", 0.0)
        confidence = "high" if score >= 0.8 else ("medium" if score >= 0.5 else "low")
        r["_meta"] = {
            "backend": backend,
            "latency_ms": latency_ms,
            "confidence": confidence,
        }
        if r.get("_dynamic_threshold"):
            r["_meta"]["dynamic_threshold"] = True
    return results


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

def total_recall_search(
    query: str,
    search_type: Literal["auto", "semantic", "keyword"] = "auto",
    limit: int = 10,
    path: Optional[str] = None,
    # improvement 3
    min_score: float = DEFAULT_MIN_SCORE,
    # improvement 1
    force_fs: bool = False,
    # improvement 5
    quick: bool = False,
    use_cache: bool = True,
    # improvement 6
    index_dirs: Optional[List[str]] = None,
    prune_old: bool = False,
) -> List[Dict]:
    """
    Public entry point. Returns a list of result dicts.

    New parameters (all optional, backwards-compatible):
      min_score   — minimum semantic score (default 0.4)
      force_fs    — bypass Spotlight, use filesystem grep
      quick       — keyword-only, 2s timeout
      use_cache   — enable 5-min result cache (default True)
      index_dirs  — extra dirs for semantic indexing
      prune_old   — skip memory files older than 90 days
    """
    t0 = time.time()

    # Quick mode → always keyword, no cache
    if quick:
        _vlog("--quick mode: keyword-only, 2s timeout, no cache")
        results = _keyword_search(query, limit, path, force_fs=force_fs, quick=True)
        return _attach_meta(results, "keyword-quick", time.time() - t0)

    # Cache check
    if use_cache and not force_fs:
        ck = _cache_key(query, search_type, limit, path)
        cached = _read_cache(ck)
        if cached is not None:
            return _attach_meta(cached, "cache", time.time() - t0)

    # Dispatch
    backend_label = "unknown"

    if search_type == "keyword":
        results = _keyword_search(query, limit, path, force_fs=force_fs)
        backend_label = "keyword"

    elif search_type == "semantic":
        results = _semantic_search(
            query, limit, min_score=min_score, index_dirs=index_dirs, prune_old=prune_old
        )
        backend_label = "semantic"

    else:
        # Auto mode
        heuristic, reason = classify_query(query)
        _vlog(f"Auto → {heuristic} ({reason})")

        if heuristic == "keyword":
            kw = _keyword_search(query, limit, path, force_fs=force_fs)
            kw_ok = [r for r in kw if not r.get("error")]
            if kw_ok:
                results = kw[:limit]
                backend_label = "keyword"
            else:
                _vlog("Keyword sparse/empty; supplementing with semantic")
                sem = _semantic_search(
                    query, limit, min_score=min_score, index_dirs=index_dirs, prune_old=prune_old
                )
                results = _borda_merge(kw, sem, limit)
                backend_label = "auto(keyword+semantic)"
        else:
            sem = _semantic_search(
                query, limit, min_score=min_score, index_dirs=index_dirs, prune_old=prune_old
            )
            sem_ok = [r for r in sem if not r.get("error")]
            if len(sem_ok) < max(1, limit // 3):
                _vlog(f"Semantic sparse ({len(sem_ok)}); supplementing with keyword")
                kw = _keyword_search(query, max(3, limit // 2), path, force_fs=force_fs)
                results = _borda_merge(kw, sem_ok, limit)
                backend_label = "auto(semantic+keyword)"
            else:
                results = sem_ok[:limit]
                backend_label = "semantic"

    # Merge ai-memory.db FTS results (always, unless quick mode already returned)
    db_results = _db_fts_search(query, limit=max(3, limit // 2))
    if db_results:
        results = _borda_merge(results, db_results, limit)
        backend_label = f"{backend_label}+db-fts"

    results = _attach_meta(results, backend_label, time.time() - t0)

    # Write cache
    if use_cache and not force_fs:
        ck = _cache_key(query, search_type, limit, path)
        _write_cache(ck, results)

    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="total_recall_search",
        description="Comprehensive memory + disk search for Momotaro.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  total_recall_search "cascade proxy"            # auto-route
  total_recall_search "SOUL.md" --type keyword   # force keyword
  total_recall_search "Leidos job" --type semantic --min-score 0.3
  total_recall_search "config.py" --force-fs-search
  total_recall_search "email" --quick            # fast 2s keyword only
  total_recall_search "strategy" --verbose --explain
  total_recall_search "notes" --index-dir ~/Documents --prune-old
  total_recall_search "model" --no-cache --json
""",
    )
    p.add_argument("query", help="Search query")
    p.add_argument(
        "--type", choices=["auto", "semantic", "keyword"], default="auto",
        help="Search strategy (default: auto)",
    )
    p.add_argument("--limit", type=int, default=10, help="Max results (default: 10)")
    p.add_argument("--path", default=None, help="Restrict keyword search to directory")
    p.add_argument("--json", action="store_true", help="Emit JSON array output")

    # Improvement 3: configurable threshold
    p.add_argument(
        "--min-score", type=float, default=DEFAULT_MIN_SCORE,
        help=f"Min semantic relevance score 0.0–1.0 (default: {DEFAULT_MIN_SCORE})",
    )
    # Improvement 1: force filesystem search
    p.add_argument(
        "--force-fs-search", action="store_true",
        help="Bypass Spotlight backends; use filesystem grep/find directly",
    )
    # Improvement 5: quick mode + cache control
    p.add_argument(
        "--quick", action="store_true",
        help="Fast keyword-only search with 2-second timeout (no cache write)",
    )
    p.add_argument(
        "--no-cache", action="store_true",
        help="Disable the 5-minute result cache",
    )
    # Improvement 7: verbose + explain
    p.add_argument(
        "--verbose", action="store_true",
        help="Show backend selection reasoning on stderr",
    )
    p.add_argument(
        "--explain", action="store_true",
        help="Include result ordering rationale in output (_explain field)",
    )
    # Improvement 6: index dirs + pruning
    p.add_argument(
        "--index-dir", action="append", dest="index_dirs", metavar="DIR",
        help="Extra directory to include in semantic index (repeatable)",
    )
    p.add_argument(
        "--prune-old", action="store_true",
        help=f"Skip memory files older than {PRUNE_DAYS} days during semantic indexing",
    )
    return p


def _print_human(results: List[Dict]) -> None:
    if not results:
        print("No results found.")
        return
    print(f"\n{'='*68}")
    print(f"  total_recall_search — {len(results)} result(s)")
    print(f"{'='*68}\n")
    for i, r in enumerate(results, 1):
        tag = f"[{r.get('type','?').upper()}]"
        score = r.get("score", 0)
        score_str = f"  score={score:.3f}"
        line_str = (f"  line≈{r['source_line']}" if "source_line" in r else "")

        meta = r.get("_meta", {})
        meta_str = ""
        if _verbose and meta:
            meta_str = (
                f"  [{meta.get('backend','?')} "
                f"{meta.get('latency_ms','?')}ms "
                f"conf={meta.get('confidence','?')}]"
            )

        print(f"  {i:>2}. {tag}{score_str}{line_str}{meta_str}")
        print(f"      {r['path']}")
        for sl in (r.get("snippet", "")).splitlines()[:3]:
            print(f"      │ {sl}")

        if _explain and "_explain" in r:
            ex = r["_explain"]
            print(
                f"      ╰─ borda={ex.get('borda_score',0):.2f}"
                f"  orig_score={ex.get('original_score',0):.3f}"
                f"  type={ex.get('result_type','?')}"
                + ("  [diversity-penalty]" if ex.get("diversity_penalty") else "")
            )
        print()


def main() -> int:
    global _verbose, _explain

    parser = _build_parser()
    args = parser.parse_args()

    _verbose = args.verbose
    _explain = args.explain

    results = total_recall_search(
        query=args.query,
        search_type=args.type,
        limit=args.limit,
        path=args.path,
        min_score=args.min_score,
        force_fs=args.force_fs_search,
        quick=args.quick,
        use_cache=not args.no_cache,
        index_dirs=args.index_dirs,
        prune_old=args.prune_old,
    )

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        _print_human(results)

    non_error = [r for r in results if not r.get("error")]
    return 0 if non_error or not results else 1


if __name__ == "__main__":
    sys.exit(main())
