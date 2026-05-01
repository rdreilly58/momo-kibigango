# TASK ROUTING & OPTIMIZATION

**Purpose:** Route tasks to optimal models and context sizes for speed + quality.

---

## Task Classification Rules

### SIMPLE TASKS → Haiku (Fast Model)
**Characteristics:** Direct answer, minimal reasoning, <50 words, no analysis

**Examples:**
- Weather, time, calendar lookups
- Simple factual questions ("What is X?")
- Quick calculations or conversions
- Status checks ("Is this site up?")
- Direct yes/no questions
- File operations (view, list, delete)
- Single-step actions without analysis

**Context Loading:**
- ✅ SOUL.md (who you are)
- ✅ USER.md (who Bob is)
- ❌ MEMORY.md (not needed for facts)
- ❌ TOOLS.md (unless specifically about tools)

**Token Budgeting (Reasoning):**
- ✅ `thinking="off"` — skip reasoning overhead
- Saves 2-3 seconds per request

**Model:** `anthropic/claude-haiku-4-5`

**Hard rule:** If message word count > 50, minimum tier is Sonnet. No exceptions.

---

### MEDIUM TASKS → Sonnet (Default Model)
**Characteristics:** Conversational, analytical, writing, medium-complexity, or anything that doesn't clearly match Simple or Complex

**Examples:**
- General conversation and greetings with follow-up work
- Explaining concepts or summarizing things
- Writing emails, messages, short content
- Answering questions that need some context
- Memory lookups and cross-session continuity
- Most heartbeat tasks
- Anything ambiguous — when in doubt, Sonnet (not Haiku)

**Context Loading:**
- ✅ SOUL.md (who you are)
- ✅ USER.md (who Bob is)
- ✅ MEMORY.md (continuity)
- ❌ TOOLS.md (unless task needs it)

**Token Budgeting (Reasoning):**
- ✅ `thinking="off"` for conversational
- ✅ `thinking="medium"` for analysis

**Model:** `anthropic/claude-sonnet-4-6`

**This is the default tier.** Anything that doesn't match simple or complex keywords routes here. Gateway default is also Sonnet — Telegram, cron jobs, and all channels without overrides land here.

---

### COMPLEX TASKS → Opus (Capable Model)
**Characteristics:** Multi-step, deep reasoning, coding, architecture, strategy, >5 min work

**Examples:**
- Major refactors or architectural changes
- Security/compliance audits
- Data migrations
- Benchmark design and analysis
- Complex multi-system deployments
- Anything explicitly requiring `/opus`

**NOT Opus:** writing emails, explaining things, reviewing code, debugging, strategy discussion, planning — those are Sonnet.

**Context Loading:**
- ✅ SOUL.md (who you are)
- ✅ USER.md (who Bob is)
- ✅ MEMORY.md (for continuity and context)
- ✅ memory/YYYY-MM-DD.md (today's context)
- ✅ TOOLS.md (for setup/infrastructure)
- ✅ PROJECT-SPECIFIC files (as relevant)

**Token Budgeting (Reasoning):**
- ✅ `thinking="medium"` (balanced reasoning for most tasks)
- ✅ `thinking="full"` (extended reasoning for hard problems)
- ✅ `thinking="off"` (rare — skip if user asks for speed)

**Model:** `anthropic/claude-opus-4-7`

---

## Edge Cases & Overrides

**User explicitly asks for "thinking" or deep analysis:**
- Use Opus even if task looks simple
- User knows their need better than classifier

**Sensitive or privacy-critical:**
- Use Sonnet minimum (Opus if complex)

**When in doubt:**
- Default to Sonnet (not Haiku — Sonnet is the middle ground)
- Reserve Opus for truly hard problems only

---

## Context Size Impact

**Simple task with minimal context:**
- Haiku: ~200-400ms

**Medium task with Sonnet:**
- Sonnet: ~500ms-1s (covers ~80% of all requests)

**Complex task with full context:**
- Opus: ~1-2s (needed for quality)

**Savings vs old Haiku/Opus binary:**
- Old pattern: ~50% of tasks hit Opus unnecessarily
- New pattern: ~80% hit Sonnet, ~15% Haiku, ~5% Opus

---

## Implementation

**Classifier logic** (implemented in `scripts/task-classifier.py` + `config/classifier-config.json`):
1. **Code patterns** (```` ``` ````, `def `, `class `) → MEDIUM (Sonnet) minimum
2. **Opus keywords** (refactor, architecture, audit, migrate, benchmark, deploy) → COMPLEX
3. **Sonnet keywords** (write, email, explain, fix, code, review, design, analyze, plan, strategy, debug, optimize, improve, create, examine, recommend) → MEDIUM
4. **Multi-line / chained query** → MEDIUM minimum
5. **Simple keywords + short (≤10 tokens)** → SIMPLE (Haiku)
6. **Default** → MEDIUM (Sonnet — never default to Haiku or Opus)

**Gateway defaults (updated May 2026):**
- `model.default`: `anthropic/claude-sonnet-4-6` (was `claude-opus-4-0`)
- `model.complex`: `anthropic/claude-opus-4-7`
- `model.fallback`: `google/gemini-2.5-flash` → `anthropic/claude-haiku-4-5`
- Telegram channel: explicit `anthropic/claude-sonnet-4-6` override

**Context loader (load order matters — primacy/recency bias):**
```
FIRST:  SOUL.md (always — position 0 = highest attention)
SECOND: SESSION_CONTEXT.md (always)

if SIMPLE:
  load nothing else
elif MEDIUM:
  load(USER, MEMORY)
else:  # COMPLEX
  load(USER, MEMORY, TOOLS, relevant_projects, today's_memory)

LAST: retrieved memories via memory_search (position N = highest attention)
```

**Tool schema ceiling (active schemas in context):**

Research shows model reliability degrades sharply above ~19 active tool schemas.
Current always-loaded tools: ~10 (Read, Write, Edit, Bash, Grep, Glob, Agent, Skill, ToolSearch, ScheduleWakeup).
All other tools are deferred — only loaded via ToolSearch when explicitly needed.

Rules by tier:
- **SIMPLE (Haiku):** Do NOT call ToolSearch. Use only the 10 always-loaded tools. Fetching extra schemas wastes tokens and can degrade simple task performance.
- **MEDIUM (Sonnet):** Only call ToolSearch for the specific tool(s) the task requires. Never load schemas "just in case."
- **COMPLEX (Opus):** Load only what the task needs. Avoid loading unrelated MCP tools (e.g., don't load music_generate for a coding task).

---

## Token Budgeting Strategy

**Thinking/Reasoning Overhead:**
- Reasoning adds 2-3 seconds per request
- Haiku: Better off without reasoning (direct inference only)
- Sonnet: Optional — off for conversation, medium for analysis
- Opus: Usually needs reasoning (better decisions)

**Implementation:**
- **Simple tasks with Haiku:** Always `thinking="off"`
- **Medium tasks with Sonnet:** `thinking="off"` for chat, `thinking="medium"` for analysis
- **Complex tasks with Opus:** Default `thinking="medium"`
  - Upgrade to `thinking="full"` only for hard problems

**Speed Impact:**
- Simple + `thinking="off"`: ~0.5-1s response time
- Medium + `thinking="off"`: ~0.5-1s response time
- Medium + `thinking="medium"`: ~1-2s response time
- Complex + `thinking="medium"`: ~1-2s response time
- Complex + `thinking="full"`: ~3-5s response time

## Batch Processing (Tier 3 Optimization)

**When to batch:**
- Similar repetitive tasks (password generation, lookups)
- 3-5+ items needing processing
- Time-sensitive (user willing to wait for batch vs. 5 separate calls)

**Example:** Generate 5 passwords in 1 request instead of 5 separate requests
- Old: 5 calls × 1-2s = 5-10 seconds
- New: 1 batch call = 1-2 seconds
- Savings: 4-8 seconds

---


## Review & Adjust

Monitor accuracy of classification. Adjust rules if:
- Sonnet is routing tasks that need Haiku (over-investing on trivial tasks)
- Opus is being hit for tasks Sonnet handles fine
- Simple classification is wrong >10% of time
- User feedback suggests better thresholds

Quarterly review recommended.
