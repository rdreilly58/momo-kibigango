# OpenClaw Workspace — Agent Instructions

## Session Start (MANDATORY)

At the start of every new conversation, before responding:

1. **Read `SESSION_CONTEXT.md`** — it contains the last session summary, recent commits, and pre-retrieved memories. It is always located at `/Users/rreilly/.openclaw/workspace/SESSION_CONTEXT.md`.

2. **Call `mcp__openclaw__memory_search`** with the user's first message or task as the query — retrieve up to 5 relevant memories. For tasks involving specific tools, projects, or people, prefer **`mcp__openclaw__memory_graph_search`** instead — it combines semantic search with graph link traversal to surface related entities and decisions. Silently incorporate results; do not narrate the retrieval unless directly asked.

This is not optional. It ensures continuity across sessions and prevents repeating work.

## Identity

See `SOUL.md` for communication style, task routing, and system capabilities.
