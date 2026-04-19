# Task Classifier — Auto-Routing Guide

**File:** `~/.openclaw/workspace/scripts/task-classifier.py`

## How It Works

The auto-classifier uses a decision tree to categorize tasks:

**Decision Flow:**
1. Token count check (≤10 tokens → likely simple)
2. Complex keyword scan (code, debug, refactor, analyze, etc.)
3. Simple keyword scan (weather, time, status, etc.)
4. Structure analysis (multi-line, chained, code blocks)
5. Default: When uncertain, pick COMPLEX (safer)

## Usage

**Direct CLI:**
```bash
python3 ~/.openclaw/workspace/scripts/task-classifier.py "your task here"
```

**Output:**
```
Task: what is the weather?
Complexity: SIMPLE
Reasoning: Multiple simple keywords detected (3)
Model: anthropic/claude-haiku-4-5
Thinking: off
Context: minimal
```

## Examples

### ✅ SIMPLE (Haiku, thinking=off, minimal context)
- "What's the weather?"
- "Delete this file"
- "Show me my calendar"
- "Is this site up?"
- "List my projects"

### ❌ COMPLEX (Opus, thinking=medium, full context)
- "Debug my Swift concurrency issue"
- "Write an article about distributed systems"
- "Analyze my email traffic and suggest improvements"
- "Build a new feature for momo-kiji"
- "Refactor my OpenClaw setup"

### 🤔 EDGE CASES
- "What are your thoughts on X?" → COMPLEX (asks for reasoning)
- "Remember this for later" → COMPLEX (context-dependent)
- "Check the status of the AWS quota" → SIMPLE (status check)

## Enforcement Rules

**I commit to:**
1. Run classifier on every user message (mental check, minimum)
2. Load minimal context for SIMPLE tasks (SOUL + USER only)
3. Load full context for COMPLEX tasks (all files + memory)
4. Use `thinking="off"` for SIMPLE, `thinking="medium"` for COMPLEX
5. Log classification decision in responses (optional, can be silent)

**When to override:**
- User explicitly asks for thinking/analysis → Use COMPLEX regardless
- Sensitive/private task → Use COMPLEX (safer defaults)
- Unclear classification → Default to COMPLEX

## Monitoring

Track accuracy quarterly:
- How often does simple classifier agree with actual complexity?
- Are any categories consistently misclassified?
- Should keyword lists be updated?
- Is context loading effective (measurable speedup)?

## Future Improvements

- ML-based classifier (train on historical tasks)
- Token budget optimization (adaptive thinking levels)
- Per-project context optimization
- Cost tracking by complexity level
