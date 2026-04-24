# Memory Search Override — March 30, 2026

## Problem
OpenClaw's built-in `memory_search` tool is hardcoded to use OpenAI embeddings. OpenAI quota is exhausted and won't be replenished. The tool will ALWAYS fail with:
```
openai embeddings failed: 429 insufficient_quota
```

## Solution
Use local Sentence Transformers embeddings via the `mem-search` shell alias.

## How It's Implemented

### 1. **SOUL.md** (Behavioral Guidance)
- Added critical section on memory search override
- Explains the problem and solution
- Tells Momotaro to NEVER use built-in tool, ALWAYS use mem-search

### 2. **AGENTS.md** (Session Startup)
- Added safeguard section explaining the issue
- Documents the shell alias and local script paths
- Reminds Momotaro to log accidental tool usage

### 3. **Shell Alias** (Easy Access)
```bash
alias mem-search='cd ~/.openclaw/workspace && source venv/bin/activate && python3 scripts/memory_search_local.py'
```
Added to `~/.zshrc` — use it anywhere:
```bash
mem-search "speculative decoding Phase 2"
```

### 4. **Local Search Script** (The Real Implementation)
- Path: `~/.openclaw/workspace/scripts/memory_search_local.py`
- Uses Sentence Transformers model: `all-MiniLM-L6-v2`
- Searches MEMORY.md and memory/*.md files
- Returns results in <1 second
- Zero API calls, zero quota issues

### 5. **Virtual Environment** (Dependencies)
- Path: `~/.openclaw/workspace/venv/`
- Contains Sentence Transformers and all dependencies
- Already installed and tested on March 20

### 6. **Memory Search Interceptor** (Safety Catch)
- Path: `~/.openclaw/workspace/scripts/memory-search-interceptor.sh`
- Can be sourced to override memory_search() function
- Automatically redirects to mem-search
- Prevents accidental use of broken tool

## Usage

**Quick Start:**
```bash
mem-search "your query here"
```

**Examples:**
```bash
mem-search "momo-kibigango Phase 2"
mem-search "local embeddings sentence transformers"
mem-search "speculative decoding timeline"
```

## Files Modified/Created

| File | Change | Date |
|------|--------|------|
| `SOUL.md` | Added Memory Search section with critical rule | March 30 |
| `AGENTS.md` | Added startup safeguard for tool override | March 30 |
| `~/.zshrc` | Added `mem-search` alias | March 30 |
| `scripts/memory-search-interceptor.sh` | Created bash interceptor | March 30 |
| `scripts/start-gateway-with-brave.sh` | Added interceptor environment var | March 30 |
| `scripts/memory_search_local.py` | Local search implementation (existing) | March 20 |
| `~/.openclaw/workspace/venv/` | Sentence Transformers environment (existing) | March 20 |

## How Momotaro Will Use This

1. **On session startup:** Read SOUL.md → see "Memory Search (CRITICAL)" section
2. **When needing to search:** Use `mem-search "query"` (not the built-in tool)
3. **If accidentally calling tool:** Catch the 429 error, log it, retry with mem-search
4. **Going forward:** Always prefer mem-search for any memory recalls

## Testing

All components tested and verified:
- ✅ Local Sentence Transformers installed and working
- ✅ Memory search script returns results in <1 second
- ✅ Shell alias configured and accessible
- ✅ SOUL.md and AGENTS.md document the override
- ✅ No further OpenAI API calls needed

## Maintenance

If momotaro ever upgrades OpenClaw to a version with true local embedding support, the built-in tool can be re-enabled. Until then, use `mem-search`.

---

**Implemented by:** Momotaro  
**Date:** March 30, 2026 — 4:37 AM EDT  
**Status:** PRODUCTION READY ✅
