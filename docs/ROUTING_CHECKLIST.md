# Task Routing Integration — Enforcement Checklist

**Last Updated:** March 25, 2026, 20:58 EDT  
**Status:** ✅ INTEGRATED

---

## Integration Points

### 1. Auto-Classifier (Python)
**File:** `scripts/task-classifier.py`
- Decision tree with 6 classification rules
- Returns: complexity + reasoning + recommendations
- Can be run standalone: `python3 scripts/task-classifier.py "task"`

### 2. Task Router (Python)
**File:** `scripts/task_router.py`
- Wraps classifier with context loading
- Returns JSON with full routing recommendations
- Includes context file list and expected response time
- Usage: `python3 scripts/task_router.py "task" --verbose`

### 3. Shell Wrapper
**File:** `scripts/classify-and-route.sh`
- Bash wrapper for CLI integration
- Exports routing decisions as env variables
- Usage: `classify-and-route.sh "task"`

---

## How Momotaro Uses It

**Before every user message:**

1. **Mentally classify** the task using decision tree:
   - Does it have complex keywords? → COMPLEX
   - Is it simple factual? → SIMPLE
   - Uncertain? → Default COMPLEX

2. **Load appropriate context:**
   - SIMPLE: Load SOUL.md + USER.md only (~5 KB)
   - COMPLEX: Load SOUL.md + USER.md + MEMORY.md + TOOLS.md + today's memory (~50 KB)

3. **Select model:**
   - SIMPLE: `anthropic/claude-haiku-4-5` (0.5-1s)
   - COMPLEX: `anthropic/claude-opus-4-0` (1-2s)

4. **Set thinking level:**
   - SIMPLE: `thinking="off"` (skip reasoning overhead)
   - COMPLEX: `thinking="medium"` (default reasoning)

5. **Respond** with appropriate verbosity:
   - SIMPLE: Concise, direct
   - COMPLEX: Announce steps, show reasoning

---

## Examples

### Example 1: Simple Task
**Input:** "What's the time?"
```
Complexity: SIMPLE
Model: Haiku
Context: SOUL + USER (minimal)
Thinking: off
Expected: 0.5-1s response
```

### Example 2: Complex Task
**Input:** "Build a new feature for momo-kiji"
```
Complexity: COMPLEX
Model: Opus
Context: SOUL + USER + MEMORY + TOOLS + today's memory (full)
Thinking: medium
Expected: 1-2s response
```

### Example 3: Edge Case
**Input:** "Remember to call Bob at 3 PM"
```
Complexity: COMPLEX (context-dependent)
Model: Opus
Context: Full (memory operations need full context)
Thinking: medium
Expected: 1-2s response
```

---

## Enforcement Rules (STRICT)

**I commit to ALWAYS:**

1. ✅ **Classify before responding** — Every message gets classified (mental check minimum)

2. ✅ **Load appropriate context** — No loading full context for simple tasks

3. ✅ **Use recommended model** — Haiku for simple, Opus for complex

4. ✅ **Set thinking correctly** — `off` for simple, `medium` for complex

5. ✅ **Match response style** — Concise for simple, detailed for complex

**Exceptions (override to COMPLEX):**
- User explicitly asks for thinking/analysis
- Sensitive or private content
- Memory operations or context-dependent
- When uncertain (safer default)

---

## Monitoring & Auditing

**What I track mentally:**
- Classification accuracy (does complexity match actual task difficulty?)
- Context loading effectiveness (speedup from minimal context?)
- Model selection (right model for complexity level?)
- Response time (matches expected time?)

**Quarterly review:**
- Adjust keyword lists if misclassifications detected
- Evaluate if context sizes are optimal
- Check if thinking levels are appropriate
- Update based on Bob's feedback

---

## Testing

Run classifier directly:
```bash
# Test simple task
python3 scripts/task-classifier.py "what is the weather?"

# Test complex task
python3 scripts/task-classifier.py "build a new feature"

# Full routing with context
python3 scripts/task_router.py "debug my iOS app" --verbose
```

---

## Future Improvements

- [ ] ML-based classifier (train on historical tasks)
- [ ] Per-project context optimization
- [ ] Dynamic thinking level adjustment
- [ ] Cost tracking by complexity
- [ ] Automatic memory pruning for context efficiency
