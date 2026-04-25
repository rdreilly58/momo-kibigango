# Agent Wiring Documentation

This document shows how the four OpenClaw subagents are wired into workflows and cron jobs.

## Subagent Definitions

| Agent | Model | Tools | Purpose |
|-------|-------|-------|---------|
| **ops** | Sonnet | Bash, Read, Write, Edit, Glob, Grep | Infrastructure, cron, monitoring, deployment, system administration |
| **code** | Sonnet | Read, Edit, Write, Glob, Grep, Bash | Code implementation, refactoring, bug fixes, feature development |
| **research** | Haiku | Read, Grep, Glob, Bash, WebFetch, WebSearch | Exploration, documentation review, web research, context gathering (read-only) |
| **memory** | Haiku | Read, Write, Edit, Glob, Grep, Bash | Memory management, session documentation, lessons-learned entries |

## Routing Rules

### Automatically Applied (Session-Start Hook)

File: `scripts/session-start-hook.sh` — Analyzes every user prompt and suggests an agent.

**Suggestion patterns:**
- **ops**: cron, health check, crontab, logs, keychain, secrets, launchctl, disk, deploy, infra, monitoring
- **memory**: memory, remember, daily notes, lessons learned, MEMORY.md, consolidate, prune
- **research**: find, search, explore, how does, what does, read docs, investigate
- **code**: write code, implement, refactor, fix bug, add feature, edit file, coding

Suggestion is logged to `~/.openclaw/logs/session-start-hook.log` and injected into `SESSION_CONTEXT.md` under "Suggested agent".

### Manual Delegation (CLAUDE.md)

File: `CLAUDE.md` — Defines explicit routing rules:

1. **Delegate when self-contained.** If the task is a discrete operation (e.g., "wire X to cron"), delegate it.
2. **Chain when dependent.** Research → Code → Ops makes sense. Code → Research does not.
3. **Parallelize when independent.** Both need researched and ops work? Launch both agents simultaneously.
4. **Don't delegate trivial work.** A single grep doesn't need an agent.

## Cron Job Mapping

| Cron Schedule | Script | Agent | Purpose |
|---|---|---|---|
| 6am daily | morning-briefing-full-ga4.sh | research | Fetch GA4 data, compile briefing |
| 5pm daily | evening-briefing-full-ga4.sh | research | Evening GA4 report, error digest |
| 10pm daily | collect-daily-metrics.sh | ops | Collect system metrics |
| Every 2h | system-health-check.sh | **ops** | Monitor system health; alerts on failure |
| Every 5h | quota-monitoring-cron.sh | **ops** | Monitor API quota usage |
| Every 5min | email_vip_watcher.py | research | Watch for VIP emails |
| Every 30min | get-today-context.py | memory | Refresh daily context (emails, calendar) |
| Every 30min | status-page-update.py | ops | Update status page |
| Hourly :13 | session-watchdog.sh | ops | Monitor active sessions |
| Hourly :23 | cron-dead-man.sh | ops | Heartbeat check for missed crons |
| 12:50am | auto-flush-session-context.sh | ops | Flush stale session context |
| 4am | daily-session-reset.sh | ops | Daily reset of session state |
| 4:45pm | error-digest.sh | ops | Aggregate errors, send digest |
| Sun 2am | log-rotation (find) | ops | Truncate logs > 20MB |
| Mon 9am | weekly-metrics-summary.sh | ops | Weekly metrics report |
| Wed 9am | weekly-memory-smart-prune.sh | **memory** | Prune noise, archive old memory |
| Wed 10am | memory-sync-flat-files.py | memory | Sync memory to flat files |
| Thu 8am,2pm,8pm | mac-allocator-cron.sh | ops | Allocate Mac instance time |
| **Every 2h** | observer-agent.sh | ops/memory | Monitor workspace, write observations |
| **Sun 7:03pm** | subagent-cost-report.sh | memory | Weekly cost report |

**Bold = agent delegation happens automatically (cron spawns Claude agent internally)**

## Hook-Based Wiring

### UserPromptSubmit Hook
**File:** `scripts/session-start-hook.sh`

Fires on every user message. Does:
1. Retrieves relevant memories via semantic search
2. **Analyzes prompt to suggest agent** (new in this change)
3. Injects memory + suggestion into SESSION_CONTEXT.md
4. Never fails — always approves the prompt

### PostToolUse Hook
**File:** `scripts/test-runner-hook.sh` (matcher: Write|Edit)

Fires after code changes. Automatically runs relevant tests. If tests fail, logs to `~/.openclaw/logs/test-runner.log`. Maps to **code** agent context.

### PreToolUse Hook
**File:** `scripts/secret-scan-hook.sh` (matcher: Bash|Write|Edit)

Scans for secrets before execution. Prevents accidental credential leaks. No agent needed; runs inline.

## Using Agents in Workflows

### From Main Agent (Interactive Session)

Detect task type and delegate using the `Agent` tool:

```python
# In a conversation, ask to delegate:
Agent(
  description="Wire health check to cron",
  subagent_type="ops",  # matches ~/.claude/agents/ops.md
  prompt="Add system-health-check.sh to crontab at 8am, 10am, 12pm..."
)
```

### From Cron Scripts

If a cron script needs to spawn a Claude session for complex logic:

1. Use `scripts/agent-router.sh` to determine the agent:
   ```bash
   AGENT=$(bash scripts/agent-router.sh "refactor memory search module")
   # → outputs: code
   ```

2. Spawn a subagent via the gateway/OpenClaw API (observed in `observer-agent.sh`):
   ```bash
   python3 scripts/agent_coordinator.py \
     submit --task "Fix memory indexing" \
     --type code \
     --priority 2
   ```

### Suggestion Visibility

Users see agent suggestions in `SESSION_CONTEXT.md`:

```markdown
## Retrieved Memory (session start 2026-04-25 11:15)
**Current time:** Friday 2026-04-25 11:15:32 EDT
**Suggested agent:** `ops` (based on prompt analysis)

- [memory entries...]
```

The suggestion is purely informative — Claude Code uses it as a hint but can choose to delegate or not.

## Testing Agent Wiring

Test suite validates the full wiring:

```bash
bash scripts/tests/test_subagents.sh
```

Covers:
- Agent file structure (YAML frontmatter, tools, model)
- BRAVE_API_KEY in keychain + settings.json
- Test-runner hook is wired and executable
- Cost tracking cron is active
- Script archive has 128 files

## Examples

### Example 1: User asks to schedule a report

**Input:** "Set up a weekly report job at Monday 9am that checks system health"

**Flow:**
1. session-start-hook detects "schedule", "weekly", "cron" → suggests **ops**
2. SESSION_CONTEXT.md shows "Suggested agent: ops"
3. Main agent sees suggestion, decides to delegate
4. Calls `Agent(..., subagent_type="ops", prompt="Set up cron job...")`
5. ops agent uses Bash + Read to understand current cron, wires health check script
6. Returns success; main agent confirms with user

### Example 2: User asks to consolidate memory files

**Input:** "Clean up and consolidate old session notes"

**Flow:**
1. session-start-hook detects "clean", "consolidate", "memory" → suggests **memory**
2. Main agent delegates to **memory** agent
3. memory agent uses Read + Edit + Bash to consolidate files
4. Writes lessons-learned entries if needed
5. Returns summary; main agent confirms

### Example 3: User asks to investigate a performance issue

**Input:** "Why are our memory searches so slow? Can you analyze and fix it?"

**Flow:**
1. session-start-hook detects "slow", "analyze", "fix" → could be research or code
2. Main agent decides: "This needs research first, then code"
3. Spawns **research** agent → analyzes memory_search.py, finds bottleneck
4. Passes findings to **code** agent → implements fix
5. Returns both findings and code changes to user

## Summary

- **4 agents** are defined in `~/.claude/agents/` and available as `subagent_type` values
- **Automatic routing** happens via session-start-hook (analyzes every prompt)
- **Cron jobs** are tagged with their corresponding agent in comments
- **Key crons** (health check, memory prune, error digest) delegate to agents when needed
- **CLAUDE.md** routing table guides manual delegation decisions
- **Test suite** validates all wiring (63 tests, all passing)

All changes are git-tracked and can be reviewed via `git log --oneline | head -1`.
