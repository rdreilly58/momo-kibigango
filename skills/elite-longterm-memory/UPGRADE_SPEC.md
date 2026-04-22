# Elite Long-Term Memory — Tiered Upgrade Spec
_Version 2.0 | April 22 2026_

---

## Problem Statement

The current memory system has three parallel stores (flat Markdown files, SQLite + in-memory vectors, MCP server) that work but have critical scaling gaps:

| Problem | Impact |
|---------|--------|
| Vector index rebuilt in-memory every session | ~2-5s cold start, all embeddings lost on crash |
| No promotion/demotion between tiers | Hot memories treated identically to month-old logs |
| Graph links underutilized (1 link in DB) | No semantic-relationship traversal in practice |
| FTS5 and vector search run independently | No score fusion — whichever is called wins |
| No access-frequency tracking driving tier placement | TTL-only expiry, no LRU promotion |
| Embeddings stored as Python-pickled blobs in SQLite | Not queryable, not diffable, no ANN index |

---

## Target Architecture: Tiered Hot / Warm / Cold

```
┌─────────────────────────────────────────────────────────────┐
│  HOT TIER  (in-process Python dict, TTL=30min)              │
│  • Last 50 accessed memories                                │
│  • Pre-computed embeddings for current session queries      │
│  • Zero-latency reads (<1ms)                                │
└────────────────────┬────────────────────────────────────────┘
                     │ miss
┌────────────────────▼────────────────────────────────────────┐
│  WARM TIER  (LanceDB persistent vector store)               │
│  • All memories with access_count ≥ 1 in last 90 days       │
│  • 384-dim embeddings stored natively (Arrow columnar)      │
│  • ANN search: ~5ms for 100k vectors                        │
│  • Hybrid scorer: RRF(vector_score, fts5_score, priority)   │
└────────────────────┬────────────────────────────────────────┘
                     │ miss / age-out
┌────────────────────▼────────────────────────────────────────┐
│  COLD TIER  (SQLite archive + compressed Markdown)          │
│  • Memories older than 90 days or access_count = 0          │
│  • No embeddings stored (recomputed on promotion)           │
│  • Git-notes for decision audit trail                       │
│  • Full-text scan only (no ANN)                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Breakdown

### 1. `memory_hot_cache.py` — Hot Tier
- **Storage**: Python `OrderedDict` (LRU, max 50 entries) in-process singleton
- **TTL**: 30-minute expiry per entry (time.monotonic)
- **On hit**: Increment `access_count` async, bump `last_accessed_at`
- **On miss**: Promote from Warm tier, add to Hot
- **Eviction**: Oldest-accessed entry dropped silently
- **Persistence**: None — intentionally ephemeral per session

```python
class HotCache:
    def get(self, memory_id: int) -> Memory | None
    def put(self, memory: Memory) -> None
    def invalidate(self, memory_id: int) -> None
    def stats(self) -> dict  # hit_rate, size, oldest_entry
```

### 2. `memory_lance_store.py` — Warm Tier (LanceDB)
- **Library**: `lancedb` (local, no server required)
- **DB path**: `~/.openclaw/workspace/lance_memory/`
- **Schema**:
  ```
  id: int64 (primary key, matches SQLite memories.id)
  namespace: utf8
  title: utf8
  content: utf8
  tags: utf8
  priority: float32
  tier: utf8
  access_count: int32
  last_accessed_at: timestamp
  embedding: fixed_size_list<float32>[384]
  ```
- **Index**: IVF-PQ index on `embedding` column (nlist=256)
- **Search**: `table.search(query_vec).metric("cosine").limit(k)`
- **Hybrid re-rank**: Reciprocal Rank Fusion combining:
  1. Vector cosine similarity (weight 0.6)
  2. SQLite FTS5 BM25 score (weight 0.3)
  3. `priority` field (weight 0.1)

```python
class LanceWarmStore:
    def upsert(self, memory: Memory, embedding: np.ndarray) -> None
    def search(self, query: str, k: int = 10) -> list[ScoredMemory]
    def delete(self, memory_id: int) -> None
    def reindex(self) -> None  # rebuild IVF-PQ index
    def sync_from_sqlite(self, db: MemoryDB) -> int  # returns rows synced
```

### 3. `memory_cold_store.py` — Cold Tier
- **Criteria for cold**: `last_accessed_at < now - 90d` OR `access_count == 0` AND `created_at < now - 30d`
- **Storage**: Existing SQLite `archived_memories` table + `memory/archive/*.md` files
- **Search**: FTS5 keyword search only (no vector)
- **Promotion path**: On cold hit → recompute embedding → upsert to LanceDB Warm → add to Hot Cache

```python
class ColdStore:
    def search_fts(self, query: str, limit: int = 5) -> list[Memory]
    def promote(self, memory_id: int, warm_store: LanceWarmStore) -> Memory
    def demote_candidates(self, warm_store: LanceWarmStore) -> int  # returns count demoted
```

### 4. `memory_tier_manager.py` — Orchestrator
Single entry point that all callers use. Handles routing, promotion, demotion, and stats.

```python
class TierManager:
    def search(self, query: str, k: int = 10, include_cold: bool = False) -> list[ScoredMemory]
    def get(self, memory_id: int) -> Memory | None
    def store(self, memory: Memory) -> int  # returns id
    def delete(self, memory_id: int) -> None
    def promote_to_warm(self, memory_id: int) -> None
    def demote_cold_candidates(self) -> int
    def stats(self) -> TierStats  # hit rates, sizes per tier
    def rebuild_warm_index(self) -> None
```

**Search flow**:
```
query →
  1. HotCache.get_by_similarity(query)  ← if embedding hits within cosine 0.92
  2. LanceWarmStore.search(query, k=10) ← primary results
  3. if include_cold: ColdStore.search_fts(query, limit=5) ← fallback
  4. RRF fusion of all results
  5. Promote top cold results to Warm if score > threshold
  6. Store top result in HotCache
  → return fused, ranked list
```

### 5. Updated `memory_mcp_server.py` — MCP Tool Layer
Replace direct `memory_search` function with `TierManager.search()`.

New MCP tools exposed:
- `memory_search(query, k=10, include_cold=False)` — tiered hybrid search
- `memory_get(id_or_filename)` — direct get with Hot cache hit
- `memory_store(title, content, namespace, tags, tier)` — store new memory
- `memory_graph_search(query, depth=1)` — unchanged, still BFS on graph links
- `memory_stats()` — NEW: returns tier hit rates, sizes, last sync time
- `memory_promote(memory_id)` — NEW: manually promote cold → warm
- `memory_rebuild_index()` — NEW: full LanceDB IVF-PQ rebuild

---

## Data Migration

### Step 1 — Sync SQLite → LanceDB
```python
# Run once at startup if lance_memory/ doesn't exist
store.sync_from_sqlite(db)
# Upserts all non-archived memories (embedding recomputed if null)
```

### Step 2 — Tier Assignment
```sql
-- Existing tier values: working, short, long
-- Map to hot/warm/cold based on last_accessed_at + access_count
UPDATE memories SET tier='warm' WHERE tier='long' OR (tier='short' AND access_count > 0);
UPDATE memories SET tier='cold' WHERE tier='working' AND last_accessed_at < datetime('now', '-7 days');
```

### Step 3 — Embedding Recomputation
Any memory with `embedding IS NULL` gets recomputed during sync. Estimated time: ~2s for 14 existing records.

---

## Test Plan

### `tests/test_elite_memory_v2.py`

| Test | Description | Pass Criteria |
|------|-------------|---------------|
| `test_hot_cache_lru_eviction` | Fill cache to 50+1, verify oldest evicted | LRU entry absent, new entry present |
| `test_hot_cache_ttl_expiry` | Insert entry, advance mock clock 31min | Entry returns None on get |
| `test_warm_store_upsert_search` | Upsert 3 memories, search similar query | Top result matches expected title |
| `test_warm_store_hybrid_rrf` | Mock FTS5 + vector scores, run RRF | Combined rank differs from either alone |
| `test_cold_promotion` | Demote memory, search cold, verify promotion | Memory promoted to warm + in hot cache |
| `test_cold_demotion` | Insert memory with stale access_date | demote_candidates() returns 1 |
| `test_tier_manager_search_routing` | Mock all 3 tiers, search, check call order | Hot → Warm → Cold called in sequence |
| `test_tier_manager_stats` | Store/search several memories | stats() returns non-zero hit rates |
| `test_mcp_memory_search_tool` | Call MCP tool via stdio protocol | Returns JSON with scored results |
| `test_mcp_memory_stats_tool` | Call new memory_stats MCP tool | Returns tier breakdown JSON |
| `test_migration_sqlite_to_lance` | Populate SQLite, run sync_from_sqlite | All rows present in LanceDB |
| `test_embedding_persistence` | Upsert, restart LanceStore, search | Results match without recomputation |
| `test_graph_search_still_works` | BFS traversal on existing graph links | Unchanged behavior post-upgrade |
| `test_namespace_isolation` | Store same title in two namespaces | Search returns namespace-correct result |
| `test_concurrent_writes` | Two threads upsert different memories | No corruption, both readable |

---

## File Plan

```
scripts/
  memory_hot_cache.py        NEW — LRU in-process hot tier
  memory_lance_store.py      NEW — LanceDB warm tier + hybrid RRF
  memory_cold_store.py       NEW — cold tier promotion/demotion logic
  memory_tier_manager.py     NEW — unified orchestrator
  memory_mcp_server.py       MODIFY — swap search backend to TierManager
  memory_db.py               MODIFY — add access_count increment helper
  memory_search_local.py     MODIFY — use TierManager.search() as backend

tests/
  test_elite_memory_v2.py    NEW — full test suite (15 tests)

lance_memory/                NEW dir — LanceDB persistent store
  (auto-created on first run)
```

---

## Dependencies

```
lancedb>=0.6.0          # Persistent vector store (local, no server)
pyarrow>=14.0           # Arrow columnar format (lancedb dep)
sentence-transformers   # Already installed
numpy                   # Already installed
```

Install: `pip install lancedb pyarrow`

---

## Performance Targets

| Operation | Current | Target |
|-----------|---------|--------|
| Cold-start embedding rebuild | ~2-5s | 0s (persistent LanceDB) |
| Vector search (100 records) | ~50ms | ~5ms |
| Hot cache hit | N/A | <1ms |
| Hybrid search (vector + FTS5) | N/A | <20ms |
| Memory store (write) | ~10ms | ~15ms (LanceDB upsert overhead) |

---

## Out of Scope (future work)
- SuperMemory cloud sync
- Mem0 auto-extraction from conversation turns
- Cross-device replication
- Embedding model upgrade (e.g., `nomic-embed-text`)
