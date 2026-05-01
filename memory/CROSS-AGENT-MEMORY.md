# Cross-Agent Memory Protocol

How subagents read and write memory. Three phases — use the highest phase available.

---

## Phase 1 — Context Injection (Active ✅)

Relevant memories are injected into the subagent's task prompt at spawn time.
The subagent doesn't need any tools or plugins — it just reads the injected context.

**How to use (in the parent session):**
```python
# Import the helper (run via exec or use inline)
result = exec("python3 ~/.openclaw/workspace/scripts/spawn-with-memory.py 'task description' --json")
enriched_task = result["task"]
sessions_spawn(task=enriched_task, ...)
```

**Or build inline:**
```
## 🧠 Memory Context (injected at spawn)
[paste top-N memory excerpts here]

## Task
[actual task]
```

**Limitations:**
- One-way: subagent can't write memories back to parent in real-time
- Static snapshot at spawn time
- Token cost (memory is in prompt, not retrieved on demand)

---

## Phase 2 — QMD Shared Sidecar (Active ✅)

QMD runs as a persistent sidecar (60s update interval). Subagents can:
- **Search** memory via QMD CLI or fallback script
- **Write back** findings that auto-index within ~60 seconds

**Search inside a subagent:**
```bash
# QMD CLI (preferred):
qmd search "anthropic spend" --json -n 5 -c memory-root-main -c memory-dir-main

# Fallback:
python3 ~/.openclaw/workspace/scripts/total_recall_search.py "query" --json --limit 5
```

**Write back from a subagent:**
```bash
python3 ~/.openclaw/workspace/scripts/memory-writeback.py write \
  --title "Key decision made" \
  --content "Full details here..." \
  --tags "decision,config"

# Or directly to today's log:
echo "\n## [SUBAGENT FINDING — $(date)]\nYour finding here" \
  >> ~/.openclaw/workspace/memory/$(date +%Y-%m-%d).md
```

**Check status:**
```bash
python3 ~/.openclaw/workspace/scripts/memory-writeback.py status
```

**Latency:** ~60 seconds for QMD to index writes. Parent can recall after next QMD update cycle.

---

## Phase 3 — Honcho Plugin (Planned)

Honcho provides true automatic cross-agent memory with zero configuration per spawn.

**Install when ready:**
```bash
openclaw plugins install @honcho-ai/openclaw-honcho
openclaw honcho setup  # self-hosted option available
openclaw gateway restart
```

Once installed: parent context flows to children automatically, write-backs are immediate,
and a persistent user model improves over time.

---

## Quick Reference

| Need | Phase 1 | Phase 2 | Phase 3 |
|------|---------|---------|---------|
| Subagent recalls past decisions | ✅ via injection | ✅ via QMD search | ✅ automatic |
| Subagent writes back findings | ❌ | ✅ ~60s latency | ✅ immediate |
| Setup required per spawn | Manual inject | None (QMD runs) | None (auto) |
| Parent recalls subagent work | ❌ | ✅ after 60s | ✅ immediate |
| User modeling over time | ❌ | ❌ | ✅ |

---

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/spawn-with-memory.py` | Phase 1: build enriched task prompt |
| `scripts/memory-writeback.py` | Phase 2: subagent write-back + search |
| `memory/MEMORY-SEARCH-GUIDE.md` | Namespace + tag search reference |
