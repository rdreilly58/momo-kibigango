---
name: total-recall-search
description: "Performs a comprehensive search across your memory (semantic recall of observations) and local disk (fast keyword search of files), intelligently choosing the best search method for the query."
metadata:
  openclaw:
    emoji: "🔍"
    requires:
      bins: ["python3", "momo-kioku-search"]
    env: []
---

# Total Recall Search

Unified search over **semantic memory** (Sentence Transformers) and **local disk** (Spotlight/mdfind via `momo-kioku-search`). Intelligently routes by query type — or lets you force a mode.

## Quick Reference

```bash
# Auto-route (recommended)
total-recall-search "cascade proxy savings"

# Force keyword (file/path queries)
total-recall-search "SOUL.md" --type keyword

# Force semantic (memory/concept queries)
total-recall-search "Leidos start date" --type semantic

# Restrict keyword search to a directory
total-recall-search "config" --type keyword --path ~/.openclaw

# JSON output for programmatic use
total-recall-search "email credentials" --json

# More results
total-recall-search "model routing" --limit 20

# Faster keyword-only search (2s timeout)
total-recall-search "config.py" --quick

# Force filesystem grep/find (bypass Spotlight)
total-recall-search "config.py" --force-fs-search

# Lower semantic score threshold
total-recall-search "AI governance" --type semantic --min-score 0.3

# Include extra directory in semantic index
total-recall-search "notes" --type semantic --index-dir ~/Documents

# Show verbose backend debugging output
total-recall-search "strategy" --verbose

# Explain result ordering rationale
total-recall-search "latest updates" --explain
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | required | The search query |
| `--type` | auto \| semantic \| keyword | `auto` | Search strategy |
| `--limit` | int | `10` | Max results to return |
| `--path` | string | — | Restrict keyword search to this directory (Spotlight/filesystem) |
| `--json` | flag | off | Emit results as JSON array |
| `--min-score` | float | `0.4` | Minimum semantic relevance score (0.0–1.0) |
| `--force-fs-search` | flag | off | Bypass Spotlight/momo-kioku-search; use filesystem grep/find directly |
| `--quick` | flag | off | Fast keyword-only search with 2-second timeout (no cache write) |
| `--no-cache` | flag | off | Disable the 5-minute result cache |
| `--verbose` | flag | off | Show backend selection reasoning, pruning, and debug messages on stderr |
| `--explain` | flag | off | Include result ordering rationale in output (`_explain` field) |
| `--index-dir` | string | — | Extra directory to include in semantic index (repeatable) |
| `--prune-old` | flag | off | Skip memory files older than 90 days during semantic indexing |

## Auto-Routing Heuristic (Two-Pass Classification)

When `--type auto` (the default), the tool classifies the query using a two-pass heuristic:

1.  **Pass 1 (Regex Patterns):** Quickly identifies queries that strongly resemble file paths (`/`, `.ext`, `README`, etc.) or conceptual prose (`why`, `explain`, `motivation`).
2.  **Pass 2 (Quick Keyword Probe):** For ambiguous queries (3-5 words), it performs a fast, 2-second Spotlight search. If file matches are found, it routes to keyword search; otherwise, it defaults to semantic.

This system prioritizes speed for clear file-like queries and leverages semantic depth for conceptual questions.

## Keyword Search Backend Reliability (Three-Tier Fallback)

Keyword search now uses a robust three-tier fallback mechanism:

1.  **`momo-kioku-search` (Spotlight/mdfind):** Primary, fast backend (bypassed with `--force-fs-search`).
2.  **`fast-find-improved.sh`:** Secondary fallback if `momo-kioku-search` fails or is not found (bypassed with `--force-fs-search`).
3.  **Filesystem `grep`/`find`:** Ultimate fallback, always available, searches filenames and content (used directly with `--force-fs-search`).

## Semantic Search Enhancements

-   **Configurable Threshold:** `--min-score` allows setting the minimum relevance score (0.0-1.0) for results. Results below this are filtered.
-   **Dynamic Thresholding:** If initial semantic search yields no results above `--min-score`, the threshold is automatically lowered to 70% of the original and the search is re-attempted. Results from dynamic lowering are flagged with `_dynamic_threshold: true` in metadata.
-   **Custom Index Directories:** `--index-dir <PATH>` (repeatable) allows including additional directories in the semantic memory index.
-   **Memory Pruning:** `--prune-old` skips semantic indexing of `.md` files in memory directories that are older than 90 days, reducing load time and noise.
-   **Lazy Model Loading:** The Sentence Transformers model is loaded only when semantic search is first requested, improving startup performance for keyword-only queries.

## Result Interleaving & Merging (Borda Count with Diversity)

When `auto` mode combines keyword and semantic results, a **relevance-weighted Borda count voting** system is used. This method:

-   Assigns points to results based on their rank and score from each backend.
-   Prioritizes overall relevance.
-   Applies a **diversity penalty** to results from the same file after their first appearance, ensuring a wider variety of sources in the final output.

## Performance Optimizations

-   **Request Caching:** Results are cached for 5 minutes (`--no-cache` to disable), significantly speeding up repeated identical queries.
-   **Quick Mode (`--quick`):** Performs a fast, keyword-only search with a 2-second timeout, bypassing semantic search and cache writes for rapid file discovery.
-   **Lazy Semantic Model Loading:** As noted above, the embedding model only loads when truly needed.

## Output Schema (Enhanced)

Each result in the JSON array now includes additional metadata:

```json
{
  "type": "semantic" | "keyword",
  "path": "/absolute/path/to/file",
  "snippet": "First few lines or matching chunk",
  "score": 0.87,
  "source_line": 42,
  "error": true,                   // Only on backend failures
  "_meta": {                       // New: metadata about search execution
    "backend": "keyword" | "semantic" | "auto(keyword+semantic)" | "cache",
    "latency_ms": 123.4,           // Latency of the backend call
    "confidence": "high" | "medium" | "low",
    "dynamic_threshold": true      // Only if dynamic threshold was applied
  },
  "_borda_score": 1.23,            // Only if Borda merging was used
  "_explain": {                    // Only with --explain flag
    "borda_score": 1.23,
    "original_score": 0.87,
    "result_type": "semantic",
    "diversity_penalty": true
  }
}
```

## Better Error Handling & User Feedback

-   **Verbose Output (`--verbose`):** Prints detailed debugging information (backend selection, pruning actions, cache hits/misses) to `stderr`.
-   **Explain Mode (`--explain`):** Adds an `_explain` field to results in `auto` mode (when Borda merging is used), detailing the Borda score, original scores, result type, and any diversity penalties.
-   **Result Metadata (`_meta`):** Every non-error result includes an `_meta` dictionary with `backend`, `latency_ms`, and `confidence` (high, medium, low) to provide transparency on how the result was obtained.
-   **Improved Error Results:** Backend failures still surface as result entries with `"error": true` and a descriptive `snippet`, ensuring issues are never silently swallowed.

## Files

| Path | Purpose |
|------|---------|
| `~/.openclaw/workspace/scripts/total_recall_search.py` | Core implementation |
| `~/.openclaw/workspace/scripts/memory_search_local.py` | Semantic backend (updated with `--json`/`--limit` flags) |
| `~/bin/total-recall-search` | CLI launcher (activates venv automatically) |
| `~/bin/momo-kioku-search` | Keyword backend (mdfind wrapper) |
| `~/bin/fast-find-improved.sh` | Secondary keyword backend (filesystem find/grep fallback) |
| `~/.openclaw/workspace/.cache/total_recall_search/` | Local cache directory |
| `~/.openclaw/workspace/.cache/total_recall_search/mtime_index.json` | Incremental indexing mtime tracker |

## How to Use from Agent Context

The agent should call this tool via `exec` or rely on the `mem-search` alias for pure semantic queries. For unified search, use `total-recall-search`:

```bash
# From agent/skill code:
total-recall-search "cascade proxy" --json --limit 5 --verbose
```

Or in Python agent code, import and call directly:

```python
import subprocess, json

result = subprocess.run(
    ["total-recall-search", "your query", "--json", "--limit", "10", "--min-score", "0.2"],
    capture_output=True, text=True, timeout=60
)
results = json.loads(result.stdout)
```

## Semantic Backend Setup

Requires the workspace venv with `sentence-transformers`:

```bash
cd ~/.openclaw/workspace
python3 -m venv venv
source venv/bin/activate
pip install sentence-transformers
```

The backend model (`all-MiniLM-L6-v2`) is downloaded on first use (~80 MB).

## Keyword Backend

Uses `momo-kioku-search` (at `~/bin/momo-kioku-search`), which wraps `mdfind` (macOS Spotlight).

Falls back to `fast-find-improved.sh` if `momo-kioku-search` is unavailable. If both fail, it uses direct `grep`/`find` on the filesystem.

## Tips

-   **Memory search is slow (~5-15s)** on first run (model load). Subsequent calls are faster.
-   **Keyword search is instant** — prefer `--type keyword` or `--quick` for file discovery.
-   Use `--limit 20` when searching large memory archives.
-   Pipe `--json` output through `jq` for filtering: `... --json | jq '[.[] | select(.type=="semantic")]'`
-   Use `--verbose` to debug why certain backends are chosen or results are pruned.
-   Use `--explain` to understand the merging and ranking of results in `auto` mode.
