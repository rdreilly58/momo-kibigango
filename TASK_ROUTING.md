# TASK ROUTING & OPTIMIZATION

**Purpose:** Route tasks to optimal models and context sizes for speed + quality.

---

## Task Classification Rules

### SIMPLE TASKS → Haiku (Fast Model)
**Characteristics:** Direct answer, minimal reasoning, <5 min expected work

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
- ❌ memory/YYYY-MM-DD.md (not needed for facts)
- ❌ TOOLS.md (unless specifically about tools)

**Token Budgeting (Reasoning):**
- ✅ `thinking="off"` or `reasoning="off"` (skip reasoning overhead)
- Saves 2-3 seconds per request
- Haiku doesn't need reasoning for simple factual lookups
- Direct inference only

**Model:** `anthropic/claude-haiku-4-5`

---

### COMPLEX TASKS → Opus (Capable Model)
**Characteristics:** Multi-step, reasoning, analysis, coding, >5 min work

**Examples:**
- Coding tasks (design, refactor, build, debug)
- Strategic decisions, analysis
- Writing/editing (emails, documentation, content)
- Multi-step workflows (password audit, deployments)
- Problem-solving that needs deep reasoning
- Research and synthesis
- Context-aware responses (understanding ongoing projects)

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
- ✅ `thinking="off"` (skip if no analysis needed, rare for complex tasks)
- Complex work REQUIRES reasoning investment
- Better decision-making, deeper analysis, fewer mistakes

**Model:** `anthropic/claude-opus-4-0`

---

## Edge Cases & Overrides

**User explicitly asks for "thinking" or deep analysis:**
- Use Opus even if task looks simple
- User knows their need better than classifier

**Sensitive or privacy-critical:**
- Use Opus (safer defaults)
- Better at handling nuance and context

**When in doubt:**
- Default to Opus (better to over-invest than under-deliver)

---

## Context Size Impact

**Simple task with full context:**
- Haiku: ~1.5-2s (but using full 100+ KB context is wasteful)

**Simple task with minimal context:**
- Haiku: ~200-400ms (3-5x faster)

**Complex task with full context:**
- Opus: ~1-2s (needed for quality)

**Savings from context optimization:**
- Simple tasks: ~1-1.5s saved per request
- Complex tasks: No impact (use full context)

---

## Implementation

**Classifier logic:**
1. **Input length** — If <200 tokens + looks factual → Simple
2. **Keywords** — If contains code/build/analyze/research → Complex
3. **Scope** — If asks for single piece of info → Simple; if multi-step → Complex
4. **Default** — When unclear, pick Complex (safer)

**Context loader:**
```
if SIMPLE:
  load(SOUL, USER)
else:
  load(SOUL, USER, MEMORY, TOOLS, relevant_projects, today's_memory)
```

---

## Token Budgeting Strategy

**Thinking/Reasoning Overhead:**
- Reasoning adds 2-3 seconds per request
- Haiku: Better off without reasoning (direct inference only)
- Opus: Usually needs reasoning (better decisions)

**Implementation:**
- **Simple tasks with Haiku:** Always `thinking="off"` (no overhead)
- **Complex tasks with Opus:** Default `thinking="medium"`
  - Upgrade to `thinking="full"` only for hard problems
  - Can be `thinking="off"` if user asks for speed + accuracy < importance

**Speed Impact:**
- Simple + `thinking="off"`: ~0.5-1s response time
- Simple + reasoning enabled: ~2-3s response time
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

**Implementation:** See BATCH_PROCESSING.md for details

---

## Speculative Decoding (Tier 3 Future - TBD Q3/Q4 2026)

**Status:** Awaiting API provider support (Google/OpenAI)

**Expected benefits:**
- 2-3x speedup without quality loss
- Small fast model generates draft
- Large model verifies in parallel
- Combines speed + quality

**When available:**
- Will be activated automatically
- No code changes needed
- Monitor announcements from Claude/GPT-4 teams

---

## Review & Adjust

Monitor accuracy of classification. Adjust rules if:
- Haiku is rejecting tasks it should handle
- Simple classification is wrong >10% of time
- User feedback suggests better thresholds
- Reasoning level (thinking) needs adjustment
- Batch sizes need tuning (3-5 items optimal?)

Quarterly review recommended.
