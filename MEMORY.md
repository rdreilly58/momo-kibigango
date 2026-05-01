
## 📅 Calendar

- **Primary:** `apple-calendar-cli` — native Apple Calendar via EventKit. Always use `--json`.
- **Secondary/fallback:** `memory__calendar_today` / `memory__calendar_range` (Google Calendar)
- **Skill:** `~/.openclaw/workspace/skills/apple-calendar-cli/SKILL.md`

---

## 📧 Email — Auth Status

- **`rdreilly2010@gmail.com`** → ✅ Active, full OAuth — primary account
- **`robert@reillydesignstudio.com`** → ✅ Active OAuth (gmail scope, added 2026-04-27)
- ~~`reillyrd58@gmail.com`~~ → 🗑️ Abandoned. Token removed 2026-04-27. Do NOT use.
- **Send to Bob:** `rdreilly2010@gmail.com`

---

## 🛠️ Memory System (Updated May 1, 2026)

Memory system fully overhauled. Key scripts:
- `scripts/total_recall_search.py` — canonical search (use `--rerank` for recency-weighted results)
- `scripts/memory_tier_manager.py` — hot/warm/cold tier management
- `scripts/memory-auto-promote.py` — promote memories by priority/tags
- `scripts/spawn-with-memory.py` — inject memory context into subagent spawns (Phase 1)
- `scripts/memory-writeback.py` — subagent write-back via QMD (Phase 2)
- `scripts/dreams-consolidation.py` — nightly consolidation (23:30 cron)
- `scripts/memory-decay.py` — TTL decay (weekly)
- `scripts/memory-rerank.py` — recency × relevance composite scoring
- `memory/CROSS-AGENT-MEMORY.md` — cross-agent memory protocol

Native OpenClaw dreaming enabled (3 AM daily). Entity graph: 217 entities, 2,732 links.

---

## 🔧 Known Issues / Active

### Cron Isolation (Partial — May 1, 2026)
10 monitoring crons still running in main session. `openclaw cron edit` requires `--message` re-supplied for agentTurn crons. Need per-cron re-add to complete migration.

---

## ✅ Decisions Made

### Model Routing (Updated May 1, 2026)
- Default: `claude-sonnet-4-6`
- Cron/heartbeat: `claude-haiku-4-5`
- Subagents: `claude-sonnet-4-6` (Opus guardrail — subagents locked to Sonnet)
- Complex/on-demand: `claude-opus-4-7`
- Fallback: `google/gemini-2.5-flash`
- See `TASK_ROUTING.md` for classifier logic

### Memory Backend (May 1, 2026)
- Backend: QMD with `searchMode: query`, Ollama nomic-embed-text
- QMD update interval: 60s (for subagent write-back latency)
- Dreaming: enabled natively (3 AM daily sweep)

---

## 📋 Lessons Learned

- **File:** `memory/lessons-learned.md` — running record of problems, root causes, fixes
- `fix:` commits should reference entry: `(see lessons-learned.md#anchor)`

---

## 📝 Pending Tasks

Tracked in Things 3. Use `things today` or `things inbox` — not this file.
