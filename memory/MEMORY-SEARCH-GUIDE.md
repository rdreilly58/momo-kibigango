# MEMORY-SEARCH-GUIDE.md — How to Search Memory Effectively

_Last updated: 2026-05-01_

---

## Overview

OpenClaw uses a three-tier memory system:
1. **Hot** — in-process query cache (5-min TTL, reused within same session)
2. **Warm** — LanceDB vector store (hybrid semantic + FTS5, ~5-20ms)
3. **Cold** — SQLite archive (FTS5 fallback, time-decayed scoring)

The `memory__memory_search` tool searches warm + optionally cold tiers.

---

## Namespaces

All memories belong to a namespace. Use namespace filters to scope results:

| Namespace | What's stored there |
|-----------|---------------------|
| `workspace` | Agent decisions, configurations, observer notes, session contexts |
| `memory-files` | Chunked daily session logs (memory/YYYY-MM-DD.md → indexed chunks) |
| `personal` | Personal notes (rarely used currently) |
| `leidos` | Work-specific memories (currently sparse — most in workspace) |
| `projects/<name>` | Project-specific (e.g. `projects/reillydesignstudio`) |

**Note:** 372 of 417 total memories are `memory-files` (session chunks). Filtering to `workspace` gives 44 curated memories.

---

## Search Methods

### 1. MCP Tool (in-session, preferred)

```
memory__memory_search(query="your query", top_k=5)
memory__memory_search(query="Leidos configuration", top_k=10, include_cold=False)
```

**With namespace filter (memory_search tool doesn't expose namespace directly, but tier_manager does):**
```python
# Via tier manager CLI:
python3 ~/.openclaw/workspace/scripts/memory_tier_manager.py search "query" --ns workspace
python3 ~/.openclaw/workspace/scripts/memory_tier_manager.py search "query" --ns memory-files
```

### 2. Total Recall Search (unified semantic + disk)

```bash
total-recall-search "cascade proxy savings"       # auto-route
total-recall-search "Leidos job" --type semantic  # memory only
total-recall-search "SOUL.md" --type keyword      # file search
total-recall-search "config" --json --limit 5     # JSON output
```

### 3. Tier Manager CLI

```bash
cd ~/.openclaw/workspace
venv/bin/python3 scripts/memory_tier_manager.py search "query" --k 5
venv/bin/python3 scripts/memory_tier_manager.py search "query" --ns workspace --k 10
venv/bin/python3 scripts/memory_tier_manager.py search "query" --cold   # include archived
venv/bin/python3 scripts/memory_tier_manager.py stats
```

---

## Common Search Patterns

### Find Leidos work decisions
```
memory__memory_search(query="Leidos team principal engineer decisions")
# Or scoped:
python3 scripts/memory_tier_manager.py search "Leidos AMS airborne" --ns workspace
```

### Find config or tool decisions
```
memory__memory_search(query="OpenClaw configuration cascade proxy")
memory__memory_search(query="email OAuth token authentication")
```

### Find personal facts / user preferences
```
memory__memory_search(query="Bob communication style preferences")
# Or read directly:
cat ~/.openclaw/workspace/memory/USER_PROFILE.md
```

### Find script or tool setups
```
total-recall-search "total-recall-search setup" --type keyword
memory__memory_search(query="memory tier manager LanceDB warm store")
```

### Find session history
```
memory__memory_search(query="what happened on April 26")
# Memory-files namespace is chunked daily logs:
python3 scripts/memory_tier_manager.py search "April 26 session" --ns memory-files
```

### Find lessons learned
```
memory__memory_search(query="lesson learned fix error")
# Or read directly:
cat ~/.openclaw/workspace/memory/lessons-learned.md
```

---

## Understanding Scores

Results come back with `_score` (higher = better match) and `_tier`:
- `warm` — from LanceDB hybrid search (typical range 0.05–0.95)
- `cold` — archived memories (max 0.04, time-decayed)

**Hybrid RRF** combines vector similarity (semantic meaning) with BM25 full-text scoring.

---

## Tips

1. **Curated memories** → use `namespace=workspace` to avoid noise from session chunks
2. **Recent context** → daily logs in `memory-files` namespace, or read `memory/YYYY-MM-DD.md` directly
3. **Decisions/lessons** → tagged with `decision`, `lesson`, `config` → can filter by tag in tier manager
4. **Rebuilding index** → `python3 scripts/memory_tier_manager.py rebuild` (full resync)
5. **Incremental sync** → `python3 scripts/memory_tier_manager.py sync` (only new changes)

---

## Test Results (2026-05-01)

Three namespace-scoped searches were run to verify scoping works:

**Test 1 — namespace=workspace:**
```bash
venv/bin/python3 scripts/memory_tier_manager.py search "session context observer" --ns workspace --k 3
# → [warm:0.0717] ENTITY:SESSION_CONTEXT.md — workspace
# → [warm:0.0715] ENTITY:SESSION-STATE.md — workspace
# → [warm:0.0712] ENTITY:session-start.json — workspace
```
Result: Returns `workspace` entities only ✅

**Test 2 — namespace=memory-files:**
```bash
venv/bin/python3 scripts/memory_tier_manager.py search "Tailscale remote access SSH" --ns memory-files --k 3
# → [warm:0.0714] MEMORY.md#1 — memory-files
# → [warm:0.0710] memory/2026-04-26.md#23 — memory-files
```
Result: Returns `memory-files` chunks only (daily log excerpts) ✅

**Test 3 — no namespace filter:**
```bash
venv/bin/python3 scripts/memory_tier_manager.py search "apple calendar CLI events" --k 3
# → [warm:0.0743] memory/2026-04-26.md#26 — memory-files
# → [warm:0.0717] ENTITY:apple-calendar-cli — workspace
# → [warm:0.0712] MEMORY.md#0 — memory-files
```
Result: Mixed results from both namespaces, ranked by hybrid score ✅

Namespace filtering confirmed working.
