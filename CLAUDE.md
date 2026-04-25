# OpenClaw Workspace — Agent Instructions

## Session Start (MANDATORY)

At the start of every new conversation, load context in this exact order — order matters for model attention:

1. **Read `SOUL.md` FIRST** — identity, routing rules, communication style. This is position 0 in context (primacy bias; highest model attention).

2. **Read `SESSION_CONTEXT.md` SECOND** — last session summary, recent commits, pre-retrieved memories.

3. **Call `mcp__openclaw__memory_search` LAST** — query with the user's first message, retrieve up to 5 relevant memories. Inject results just before responding (recency bias; highest model attention). Silently incorporate; do not narrate retrieval unless asked.

Loading order: SOUL → SESSION_CONTEXT → task-specific files (middle) → retrieved memories (last). Never bury critical context in the middle.

This is not optional. It ensures continuity across sessions and prevents repeating work.

## Context Size — Proactive Compaction

Compact early — do not wait for the auto-compact at 95%. When you estimate context is ~70-75% full (long conversation, many files read, multiple tool result blobs), proactively run `/compact`. A clean compact at 70% preserves more signal than a forced compact at 95%.

Signs you are approaching 70%:
- More than ~15 tool calls in the conversation
- More than ~5 large files read in one session
- Conversation has been running for 30+ turns

## KV-Cache Prefix — Do Not Re-Read These Files Mid-Session

`SOUL.md` and `USER.md` are the stable cache prefix. They are loaded once at session start (step 1 above) and must not be re-read later in the same session. Re-reading them changes their position in the context window and busts the prompt cache, costing tokens on every subsequent turn.

Rule: if you already loaded `SOUL.md` or `USER.md` at session start, treat their content as known for the rest of the session. Only re-read them if the user explicitly asks about or modifies them.

## Daily Session Notes — Template

File: `memory/YYYY-MM-DD.md` (today's date). Append, never overwrite.

```markdown
## Tasks
- Brief description of what was worked on

## Learnings
- Anything new discovered, debugged, or figured out

## Issues Encountered
- Problems hit, errors seen, things that didn't work

## End of Day Summary
- 1–3 sentence recap of the session
```

Rules: write at natural end points (goodbye, sign-off, wrap-up). Multiple sessions append to the same day file. Skip if nothing meaningful happened (quick one-off questions). This is how future-you knows what past-you did.

## Agent Delegation — When to Use Subagents

Five specialized subagents are defined in `~/.claude/agents/`. Use the `Agent` tool with the matching `subagent_type` to delegate work and protect main context from bloat.

### Routing Table

| Signal in user prompt | Delegate to | Why |
|---|---|---|
| cron, health check, crontab, logs, keychain, secrets, launchctl, disk, deploy, infra | **ops** | System administration, cron wiring, monitoring, keychain ops |
| write code, implement, refactor, fix bug, add feature, PR, edit file, coding | **code** | Code changes across any language/project in the workspace |
| find, search, explore, how does X work, what does X do, read docs, investigate | **research** | Read-only exploration and synthesis — never modifies files |
| memory, remember, daily notes, lessons learned, MEMORY.md, consolidate, prune | **memory** | Memory file management, session notes, lessons-learned entries |
| expense, spending, budget, debt, credit card, bank statement, import CSV, finance report, payoff | **finance** | Personal finance — expense tracking, bank imports, debt management, reports |

### Rules

1. **Delegate when the task is self-contained.** If the user asks "wire this to cron" — that's a clean ops delegation. If they ask "refactor and then wire to cron" — do the refactor in code, then delegate the cron wiring to ops.
2. **Don't delegate trivial lookups.** A single `grep` or `read` doesn't need an agent. Use agents when the task requires 3+ tool calls or domain expertise.
3. **Research first, code second.** When you're unsure how something works, delegate to research before delegating to code. Research returns findings; code acts on them.
4. **Memory agent for batch memory work.** Single memory writes are fine in main context. Delegate to memory for consolidation, pruning, or multi-file updates.
5. **Parallel where independent.** If you need both research and ops work that don't depend on each other, launch both agents simultaneously.

## Identity

See `SOUL.md` for communication style, task routing, and system capabilities.
