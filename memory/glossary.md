---
title: Workspace Glossary
type: concept
created: 2026-05-03
updated: 2026-05-03
tags: [glossary, canonical, terminology]
---

# Workspace Glossary

Canonical terms used across all memory files, scripts, and documentation.
Check here before writing a new memory — use the term on the left, avoid the aliases.

---

## People

| Canonical | Aliases (avoid) | Notes |
|-----------|-----------------|-------|
| **Bob** | Robert, rreilly, the user | Full name: Robert Reilly |
| **Momotaro / Momo** | the assistant, Claude, the AI | Named by Bob on first meeting |

---

## Systems

| Canonical | Aliases (avoid) | Notes |
|-----------|-----------------|-------|
| **OpenClaw** | openclaw-cli, the platform | The AI personal assistant platform |
| **Gateway** | openclaw gateway, server | OpenClaw's local service (port 18789) |
| **QMD** | memory sidecar | Persistent search sidecar (60s update interval) |
| **LanceDB** | warm store, vector db | Warm-tier semantic search |
| **SQLite cold archive** | cold store, sqlite | Cold-tier FTS5 fallback |
| **Things 3** | Things, task tracker | Primary task manager (since 2026-04-16) |
| **Apple Calendar CLI** | apple-calendar-cli | Primary calendar tool (`--json` always) |
| **total-recall-search** | TRS, search script | `scripts/total_recall_search.py` — canonical search |

---

## Memory System Tiers

| Canonical | Description |
|-----------|-------------|
| **Hot tier** | In-process LRU cache — recent/frequent memories |
| **Warm tier** | LanceDB vector store — semantic hybrid search |
| **Cold tier** | SQLite archive — FTS5 full-text fallback |
| **Working tier** | Short-lived inserts with 7-day TTL (auto-expire) |

---

## Email Accounts

| Canonical | Aliases (avoid) | Status |
|-----------|-----------------|--------|
| **rdreilly2010** | personal gmail | ✅ Active — primary personal + calendar |
| **robert@reillydesignstudio.com** | RDS email | ✅ Active — design studio send/receive |
| ~~reillyrd58~~ | ~~reillyrd25~~ | ❌ Abandoned 2026-04-27 — do not use |

---

## Projects

| Canonical | Aliases | Notes |
|-----------|---------|-------|
| **momo-kibidango** | workspace repo, this repo | `~/.openclaw/workspace` — Momo's brain |
| **reillydesignstudio** | RDS, design site | Vercel-deployed portfolio site |
| **ReDrafter** | redrafter, benchmark | LLM benchmarking (Qwen2.5-7B-Instruct) |

---

## Model Routing Shorthand

| Canonical | Model ID | Use |
|-----------|----------|-----|
| **Haiku** | `claude-haiku-4-5` | Simple tasks, crons, heartbeats |
| **Sonnet** | `claude-sonnet-4-6` | Default — most tasks |
| **Opus** | `claude-opus-4-7` | Complex only — costs 25× Haiku |
| **Gemini** | `google/gemini-2.5-flash` | Fallback (Anthropic timeout/quota) |

---

## Memory File Types (Entity Taxonomy)

| Type | Use for |
|------|---------|
| `user` | Facts about Bob — role, preferences, identity |
| `feedback` | Behavioral guidance — what to do / avoid |
| `project` | Active or completed work — goals, decisions, status |
| `reference` | External system pointers — where to look things up |
| `concept` | Domain knowledge — definitions, mental models |
| `tool` | Tool/service profiles — how to use, quirks |
| `decision` | Architectural decisions — what was chosen and why |
| `lesson` | Post-mortems — root cause + prevention |
| `analysis` | Synthesized outputs — comparisons, gap analyses |

---

_See also: [[overview]] · [[CROSS-AGENT-MEMORY]]_
