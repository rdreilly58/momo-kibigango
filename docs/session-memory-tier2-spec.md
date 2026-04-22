# Spec: Two-Tier Session Memory System

**Status:** Ready to build  
**Date:** 2026-04-22  
**Goal:** Automated session capture and structured recall — no relying on agent remembering to write notes.

---

## Problem

The session-memory internal hook regressed in OpenClaw v2026.4.15 and no longer writes conversation transcripts. The current workaround (SOUL.md instructs the agent to write notes manually) breaks whenever the agent forgets or a session ends abruptly. Session startup has full amnesia — SESSION_CONTEXT.md is written but never auto-read, and ai-memory.db (11 records) is never queried.

---

## Architecture: Two Tiers

### Tier 1 — Always-Loaded Briefing (`SESSION_CONTEXT.md`)
- Small (~150 lines max)
- LLM-compressed summary of recent sessions (Haiku, not raw transcript)
- Structured fields: `topics`, `completed`, `learned`, `issues`, `next_steps`, `one_liner`
- Auto-written at session end AND by cron safety net
- Already included in boot context (openclaw.json `boot-md` hook reads it)

### Tier 2 — Full Store (`memory/YYYY-MM-DD.md` + `ai-memory.db`)
- Full structured summaries appended to daily notes (Tasks/Learnings/Issues/Summary sections)
- SQLite records for FTS and semantic search
- Queried on demand via existing MCP server (`memory_search`)

---

## Components to Build

### 1. `scripts/session_summarizer.py` — Core Engine

**Purpose:** Accept conversation text, call Haiku to compress, write outputs.

**Input:** 
- `--text` (string): raw conversation text, OR
- `--file` (path): read from file  
- `--session-file` (path): read from session file in memory/ directory

**Processing:**
1. Strip system messages and metadata boilerplate
2. Skip if content is <200 chars (too short to summarize)
3. Call Claude Haiku via Anthropic SDK with prompt caching
4. Parse JSON response into structured summary
5. Deduplication check: compare against last entry in today's daily file using Jaccard similarity — if >60% overlap on significant words, skip write
6. Write outputs

**Haiku prompt (system):**
```
You are a session memory compressor. Given a conversation transcript, extract a structured summary in valid JSON only. No commentary, no markdown fences — raw JSON.

Schema:
{
  "one_liner": "1-sentence summary of what happened (max 120 chars)",
  "topics": ["list", "of", "topics", "discussed"],
  "completed": ["tasks or problems resolved"],
  "learned": ["facts, decisions, or insights discovered"],
  "issues": ["problems hit, errors, things that didn't work"],
  "next_steps": ["open items or follow-ups if any"]
}

Rules:
- Be factual and specific (include file names, script names, error messages)
- completed/learned/issues/next_steps: 0-5 items each, bullet-point style
- If nothing significant happened, return {"one_liner": "Routine session, nothing notable", "topics": [], "completed": [], "learned": [], "issues": [], "next_steps": []}
- Never hallucinate — only include what is explicitly in the transcript
```

**Outputs (all optional via flags, all default ON):**
1. **Daily notes** (`memory/YYYY-MM-DD.md`): Append to Tasks/Learnings/Issues/End of Day Summary sections. Append, never overwrite. Format each item as `- [HH:MM] item text`.
2. **SESSION_CONTEXT.md**: Prepend new summary entry (with timestamp) to top of history block. Keep last 5 summaries (older ones pruned). Max 150 lines total.
3. **ai-memory.db**: `memory_db.py add` with tier=short, ns=workspace, tags="session,summary,auto"

**Flags:**
```
--text TEXT          Conversation text to summarize
--file PATH          Read conversation from file  
--session-file PATH  Read from session file
--dry-run            Print output, don't write files
--no-daily           Skip daily notes write
--no-context         Skip SESSION_CONTEXT.md write  
--no-db              Skip ai-memory.db write
--workspace PATH     Override workspace (default: ~/.openclaw/workspace)
--min-chars INT      Skip if input < N chars (default: 200)
--dedup-threshold FLOAT  Jaccard threshold for skip (default: 0.60)
```

**Exit codes:** 0=success, 1=skipped (too short), 2=skipped (duplicate), 3=error

---

### 2. `scripts/session-stop-hook.sh` — Hook Wrapper

**Purpose:** Called by Stop hook after each agent response. Guards against noise.

```bash
#!/bin/bash
# session-stop-hook.sh — Run session summarizer after agent stop
#
# Registered as a Stop hook in openclaw.json or .claude/settings.json
# Input: reads STDIN for conversation context (Claude Code hook protocol)
# Guard: only fires if session has been active for >5 minutes (avoid noise)
```

**Logic:**
1. Read stdin (Claude Code passes hook data as JSON via stdin)
2. Extract `session_id`, `transcript` (or path to transcript) from hook payload
3. Guard: check if last summary was written < 10 min ago — if so, exit 0 (already captured)
4. Guard: check if transcript < 200 chars — exit 0
5. Call `python3 session_summarizer.py --text "$transcript"`
6. Log result to `~/.openclaw/logs/session-summarizer.log`
7. Never block or fail loudly (agent stop should not be affected by hook errors)

**Hook payload format** (Claude Code Stop hook):
```json
{
  "session_id": "abc123",
  "stop_hook_active": true,
  "transcript": "...",  
  "hook_event_name": "Stop"
}
```

---

### 3. Hook Registration

**Primary:** Claude Code settings hook (`~/.claude/settings.json` or workspace `.claude/settings.json`):
```json
{
  "hooks": {
    "Stop": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "bash ~/.openclaw/workspace/scripts/session-stop-hook.sh"
      }]
    }]
  }
}
```

**Fallback cron** (safety net if hook doesn't fire — e.g., abrupt session end):
- Schedule: every 30 minutes during active hours (8 AM – 11 PM)
- Script: check if SESSION_CONTEXT.md was updated in last 30 min. If not, and if there are recent session files, run summarizer.
- Add to OpenClaw cron via `mcp__openclaw__cron` or direct JSON edit.

---

### 4. SESSION_CONTEXT.md Format (New)

Replace the current single-paragraph blob with a structured format the agent can scan in <5 seconds:

```markdown
# SESSION_CONTEXT.md

**Last updated:** 2026-04-22 09:15 EDT  
**Auto-generated — do not edit manually**

---

## Recent Sessions (last 5)

### 2026-04-22 07:00–07:35
**Summary:** Diagnosed session-memory hook regression; fixed with SOUL.md instructions and log_session_entry() helper; 25-test suite all passing.
**Completed:** fix(memory): agent-written summaries; test suite for daily-session-reset.sh  
**Learned:** OpenClaw v2026.4.15 hook writes only 171 bytes (session ID) not transcripts  
**Issues:** None  
**Next:** Two-tier memory system (in progress)

### 2026-04-22 06:50
**Summary:** Auto-flush before reset. Recent commits: 21e0ad7 test(memory); e634d5b fix(memory).

---

## System State (auto-refresh every 2h)
- Git: `main`, last commit: 21e0ad7 2026-04-22
- Things today: (items)
- Schedule: (today's events)
- Blocked: none known
```

---

### 5. Startup Bootstrap in SOUL.md

Update the Continuity section to explicitly instruct:
1. On session start, READ `SESSION_CONTEXT.md` first for orientation
2. The top section gives recent session context automatically
3. For deeper recall, use `memory_search` tool

---

## Testing Requirements

### Unit Tests (`Tests/test_session_summarizer.py`)

**Summarizer core:**
- `test_short_input_skipped` — input < 200 chars returns exit code 1
- `test_empty_input_skipped` — empty string skipped
- `test_haiku_called_with_correct_prompt` — mock Anthropic client, assert prompt structure
- `test_prompt_caching_headers_set` — assert cache_control on system prompt
- `test_json_parsing_valid` — valid JSON response parsed correctly
- `test_json_parsing_invalid` — malformed JSON handled gracefully (no crash)
- `test_json_missing_fields` — missing fields default to empty lists
- `test_dry_run_no_writes` — --dry-run flag produces no file writes

**Deduplication:**
- `test_dedup_identical_summary_skipped` — exact match → skip (exit 2)
- `test_dedup_high_similarity_skipped` — >60% Jaccard → skip
- `test_dedup_low_similarity_written` — <60% Jaccard → write
- `test_dedup_no_prior_entry_written` — empty daily file → always write

**File writes:**
- `test_daily_notes_tasks_appended` — tasks written under ## Tasks
- `test_daily_notes_learnings_appended` — learnings under ## Learnings
- `test_daily_notes_issues_appended` — issues under ## Issues Encountered
- `test_daily_notes_summary_appended` — one_liner under ## End of Day Summary
- `test_daily_notes_creates_file` — creates daily file if missing
- `test_daily_notes_timestamp_format` — entries have [HH:MM] prefix
- `test_session_context_prepends` — new summary prepended (not appended)
- `test_session_context_max_5` — older than 5th entry pruned
- `test_session_context_max_150_lines` — file never exceeds 150 lines
- `test_db_write_called` — memory_db.py add called with correct args
- `test_db_failure_doesnt_crash` — SQLite write failure is non-fatal
- `test_no_daily_flag` — --no-daily skips daily notes
- `test_no_context_flag` — --no-context skips SESSION_CONTEXT.md
- `test_no_db_flag` — --no-db skips database write

### Integration Tests (`Tests/test_session_stop_hook.sh`)

- `test_hook_reads_stdin` — script processes JSON from stdin
- `test_hook_short_transcript_skipped` — <200 chars → exits 0, no summarizer call
- `test_hook_recent_summary_guard` — summary written <10 min ago → skip
- `test_hook_calls_summarizer` — valid input → summarizer called
- `test_hook_never_fails_loudly` — summarizer crash → hook still exits 0
- `test_hook_logs_to_file` — result logged to session-summarizer.log

### End-to-end Test (`Tests/test_memory_e2e.sh`)

Simulate a full session cycle:
1. Create temp workspace
2. Run session_summarizer.py with sample conversation text
3. Assert daily notes written correctly
4. Assert SESSION_CONTEXT.md updated
5. Assert ai-memory.db has new record
6. Run again with similar text → assert deduplication skips
7. Run again with different text → assert appended (not replaced)
8. Assert SESSION_CONTEXT.md never exceeds 150 lines after 10 runs

---

## Existing Code to Reuse

| File | Purpose |
|------|---------|
| `scripts/memory_db.py` | SQLite API — use `MemoryDB.add()` directly (import as module) |
| `scripts/daily-session-reset.sh` | `log_session_entry()` helper — session_summarizer.py reimplements this in Python for reliability |
| `scripts/observer-agent.sh` | Pattern for isolated agentTurn scripts |
| `scripts/auto-flush-session-context.sh` | Context snapshot — will be updated to use new SESSION_CONTEXT.md format |
| `venv/` | Python 3.14 venv with `anthropic`, `sentence_transformers`, `mcp` already installed |
| `OPENCLAW_TEST_WORKSPACE` env var | Test isolation pattern (established today) |

---

## Implementation Notes

- Use `anthropic` SDK (already in venv) — NOT subprocess calls to claude CLI
- Enable prompt caching on the Haiku system prompt (it's static, >1024 tokens with examples added)
- Haiku model ID: `claude-haiku-4-5-20251001`
- API key: read from `ANTHROPIC_API_KEY` env var (available in briefing.env or system env)
- All file writes: atomic (write to `.tmp`, then `os.replace()`) — avoid half-written files
- All scripts: handle missing files, missing env vars, and API errors without crashing
- Log file: `~/.openclaw/logs/session-summarizer.log` (append-only, rotate at 1 MB)

---

## Out of Scope

- Cloud storage (all local)
- Changing the MCP server (already solid)
- Modifying memory_db.py schema
- Retroactively summarizing old sessions (can be done later as one-off)

---

## Files to Create/Modify

| Action | Path |
|--------|------|
| CREATE | `scripts/session_summarizer.py` |
| CREATE | `scripts/session-stop-hook.sh` |
| CREATE | `Tests/test_session_summarizer.py` |
| CREATE | `Tests/test_session_stop_hook.sh` |
| CREATE | `Tests/test_memory_e2e.sh` |
| MODIFY | `SOUL.md` — startup bootstrap instruction |
| MODIFY | `SESSION_CONTEXT.md` — migrate to new structured format |
| MODIFY | `scripts/auto-flush-session-context.sh` — use new format, defer to summarizer |
| CONFIGURE | `~/.claude/settings.json` or equivalent — register Stop hook |
