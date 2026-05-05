---
title: Workspace Overview
type: analysis
created: 2026-05-03
updated: 2026-05-03
tags: [overview, synthesis, workspace]
---

# Workspace Overview

High-level synthesis of who Bob is, what's active, and what the open questions are.
This file should be updated after major project milestones or system changes.

_See [[glossary]] for canonical terms. See [[USER_PROFILE]] for Bob's full profile._

---

## Who Is Bob

Robert "Bob" Reilly — Team Lead / Principal Software Engineer at Leidos (Defense sector, Airborne & Mission Solutions). Started March 23, 2026. Eastern timezone. Heavy personal AI/ML investment: he built and maintains this memory system himself, iterates frequently.

Primary communication channel: Telegram (`8755120444`). Works weekdays, most active evenings/weekends on personal projects.

---

## The System: What This Is

A personal AI assistant workspace (`~/.openclaw/workspace`) running on:
- **OpenClaw** — the local AI platform (Gateway on port 18789)
- **Momotaro (Momo)** — Bob's named assistant persona
- **Three-tier memory** — hot LRU → LanceDB warm vector → SQLite cold FTS5
- **Subagent coordination** via `spawn-with-memory.py` + QMD write-back

The workspace repo is `momo-kibidango`. Bob treats this as a living system — improves it regularly.

---

## Active Projects (as of 2026-05-03)

| Project | Status | Notes |
|---------|--------|-------|
| Memory system improvements | 🟢 Active | Wiki-style taxonomy, lint, overview (this session) |
| reillydesignstudio | 🟡 Intermittent | Vercel-deployed; robert@reillydesignstudio.com live |
| ReDrafter | 🟡 Intermittent | LLM benchmarking (Qwen2.5-7B-Instruct) |
| iOS app(s) | 🟡 Intermittent | Swift; ios-dev skill available |
| MAC dedicated host | 🔵 Pending | Cron polling 3×/day; m4pro first, then m4 |

---

## Infrastructure State

| Component | Status | Notes |
|-----------|--------|-------|
| M4 Mac Mini | ✅ Primary | Local GPU (MLX), all primary inference |
| Google Colab H100 | ✅ Available | Manual launch — large batch only |
| EC2 54.81.20.218 | ❌ Decommissioned | April 22, 2026 — do not use |
| Tailscale | ❌ Removed | May 1, 2026 — direct SSH / Termius on LAN |
| OpenClaw Gateway | ✅ Running | Port 18789; LaunchAgent managed |
| Dreams consolidation | ✅ Running | 23:30 nightly cron |
| Observer cron | ✅ Running | Every 2 hours, isolated |
| Heartbeat | ✅ Running | Every 30 min, isolated, Haiku |

---

## Email Accounts

| Account | Status |
|---------|--------|
| rdreilly2010@gmail.com | ✅ Primary personal + calendar |
| robert@reillydesignstudio.com | ✅ Design studio (live on iCloud+ since 2026-05-02) |
| reillyrd58@gmail.com | ❌ Abandoned 2026-04-27 |

---

## Model Routing

Default: **Sonnet** for most tasks. Haiku for crons/heartbeats. Opus only for deep architecture tasks (costs 25× Haiku — justify every use). Gemini as fallback on Anthropic timeout/quota.

---

## Key Open Questions / Watch Items

- MAC dedicated host: still polling (allocated? launch?)
- Anthropic spend: hit 999/1000 req + 540K tokens/day April 23–26 — monitor if sustained
- 10 monitoring crons still running in main session (partial isolation migration)
- Memory lint coverage: new as of today — watch for false positives in first run

---

## Memory System Architecture

```
Hot (LRU in-process)
  └─ Warm (LanceDB — nomic-embed-text, hybrid semantic+FTS5)
       └─ Cold (SQLite — FTS5 full-text fallback)

Supporting scripts:
  total_recall_search.py     ← canonical query entrypoint
  memory_tier_manager.py     ← hot/warm/cold promotion/demotion
  memory-auto-promote.py     ← priority/tag-based promotion
  spawn-with-memory.py       ← inject context into subagents (Phase 1)
  memory-writeback.py        ← subagent write-back via QMD (Phase 2)
  dreams-consolidation.py    ← nightly consolidation (23:30 cron)
  memory-decay.py            ← TTL decay (weekly)
  memory-lint.py             ← consistency audit (weekly cron) ← NEW
```

Entity graph: 217 entities, 2,732 links (OpenClaw native dreaming).

---

_Cross-references: [[glossary]] · [[USER_PROFILE]] · [[CROSS-AGENT-MEMORY]] · [[lessons-learned]]_
