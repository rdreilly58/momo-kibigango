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

## Identity

See `SOUL.md` for communication style, task routing, and system capabilities.
