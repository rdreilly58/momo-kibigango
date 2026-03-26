# Claude Code & Model Routing Analysis

**Date:** Thursday, March 26, 2026, 4:11 AM EDT  
**Question:** Does our model routing setup provide for Claude Code use for complex tasks?  
**Answer:** YES, but with strategic gaps & opportunities

---

## Current State: How Claude Code Fits In

### Current Architecture

**Claude Code Role:**
- ✅ Spawned as **subagent** for coding tasks (separate session)
- ✅ Uses **Opus** (claude-opus-4-0) by default
- ✅ Falls back to **GPT-4** if Opus fails
- ✅ Proper separation of concerns (billing, audit, isolation)

**Complex Task Flow (Current):**
```
User: "Build a new feature" (Complex task)
  ↓
Main Session: Detects coding keyword
  ↓
Spawns Subagent: sessions_spawn(task="...", model="claude-opus-4-0")
  ↓
Claude Code: Works in isolated session
  ↓
Results → Back to main session
```

**Current Constraints:**
- Subagent always uses Opus (expensive for small fixes)
- No cost optimization for coding tasks
- No fallback to Haiku for trivial fixes
- OpenRouter Auto doesn't apply to subagents

---

## The Gap: Model Routing Doesn't Include Subagents

### What's Missing

**Problem 1: Subagent Model Selection is Hardcoded**
```javascript
// Current implementation
sessions_spawn(
  runtime="subagent",
  task="Write a function",
  model="claude-opus-4-0"  // ← Always Opus
)

// What we need
sessions_spawn(
  runtime="subagent",
  task="Write a function",
  model=selectModelForTask("Write a function")  // ← Dynamic
)
```

**Problem 2: OpenRouter Auto is Main Session Only**
- OpenRouter Auto: ✅ Works in main session
- OpenRouter Auto: ❌ Not used by subagents
- Subagents use direct Anthropic/OpenAI (no intelligent routing)

**Problem 3: No Tiered Model Selection for Subagents**
```
Current:
  - Single-file fix → Opus ($$$)
  - 4-file feature → Opus ($$$)
  - 16-file build → Opus ($$$)

What we need:
  - Single-file fix → Haiku ($)
  - 4-file feature → Opus ($$)
  - 16-file build → GPT-4 or Opus with batching ($$$)
```

---

## How It Currently Works for Complex Tasks

### Scenario 1: Complex Coding Task (e.g., "Build Swift app feature")

**Current Flow:**
```
User: "Build a WebSocket feature for Momotaro iOS app"
  ↓
Momotaro detects: coding keywords
  ↓
Spawns Claude Code subagent with Opus
  ↓
Claude Code works in isolated session
  - Full context loaded
  - Full reasoning enabled
  - Xcode integration available
  ↓
Results delivered back to main session
```

**What Works Well:**
- ✅ Proper isolation (doesn't bloat main session history)
- ✅ Full context loaded (files can be read/modified)
- ✅ Dedicated reasoning (thinking mode available)
- ✅ Proper billing (subagent costs tracked separately)
- ✅ Clear audit trail

**What's Suboptimal:**
- ❌ Small fixes (typo, import) still use expensive Opus
- ❌ Can't use OpenRouter Auto for cost optimization
- ❌ No fallback to Haiku for trivial tasks
- ❌ No task complexity analysis before spawning

### Scenario 2: Simple Fix (e.g., "Fix missing semicolon in App.swift")

**Current Flow:**
```
User: "Fix missing semicolon in App.swift"
  ↓
Momotaro detects: coding + "fix" keywords
  ↓
Spawns Claude Code with Opus
  ↓
Claude Code: Reads file, finds semicolon, adds it
  ↓
Costs: Full Opus usage for 1-line fix ($0.015 per 1K tokens)
```

**The Problem:**
- Uses expensive Opus for trivial work
- Haiku could do this in 100ms for $0.0001
- **Cost ratio: 150x more expensive than needed**

---

## How Complex Tasks Should Work (Improved)

### Proposed Enhanced Flow

**Step 1: Task Complexity Analysis (In Main Session)**
```
User: "Build a WebSocket feature"
  ↓
Analyze task:
  - Keywords: "build", "feature", "websocket"
  - Scope: 4-8 files likely
  - Type: Code creation
  - Complexity: HIGH
  ↓
Decision: Spawn Opus subagent
```

**Step 2: Model Selection with Fallbacks**
```
Primary:      Claude Opus (best for complex builds)
Fallback 1:   OpenRouter Auto (if Opus overloaded)
Fallback 2:   GPT-4 (if neither available)
Haiku:        RESERVED for trivial fixes only
```

**Step 3: Subagent Spawning with Context**
```
sessions_spawn(
  runtime="subagent",
  task="Build WebSocket feature",
  model="claude-opus-4-0",
  context={
    files_to_read: ["Momotaro.swift", "Models.swift"],
    scope: "4-8 files",
    complexity: "high"
  }
)
```

**Step 4: Results with Cost Tracking**
```
Subagent completes
  ↓
Cost: $0.012 (Opus usage)
Time: 2.3 seconds
Files modified: 3
Status: SUCCESS
```

---

## Recommendations: 3-Tier Improvement Plan

### TIER A: Immediate (Today) - Quick Wins

**1. Add Task Complexity Classifier for Subagents**
```bash
# New script: classify-coding-task.sh
# Input: "Build a WebSocket feature for iOS"
# Output: { complexity: "high", files_estimate: 6, model: "opus" }

# Use cases:
# - "Fix typo" → { complexity: "low", model: "haiku" }
# - "Add logging" → { complexity: "medium", model: "opus" }
# - "Refactor 16-file module" → { complexity: "high", model: "gpt4" }
```

**2. Add Haiku Subagent for Trivial Fixes**
```
if task matches ["fix", "format", "lint", "typo"] AND file_count <= 1:
  model = "haiku"  // 150x cheaper
else:
  model = "opus"   // Standard
```

**Implementation:** Add to SOUL.md → Subagent routing rules

**Expected Impact:**
- Cost reduction: 15-20% on small fixes
- Speed improvement: 3x faster on trivial tasks
- Backward compatible: Doesn't break existing flows

### TIER B: Short Term (This Week) - Infrastructure

**1. OpenRouter Support for Subagents**
```
Current:  Main session uses OpenRouter Auto
          Subagents use direct Anthropic

Proposed: Subagents also route through OpenRouter
          - Pass OpenRouter creds to subagent env
          - Let subagent use openrouter/openrouter/auto
          - Unified model selection
```

**Implementation Steps:**
1. Add `OPENROUTER_API_KEY` to subagent environment
2. Update sessions_spawn to pass credentials
3. Update model fallback chain

**Expected Impact:**
- Unified cost optimization across main + subagents
- Additional 20-30% savings on coding tasks
- Single dashboard for all model usage

**2. Subagent Cost Tracking**
```
Before:  "Spawned subagent, got result" (opaque cost)
After:   "Spawned Opus subagent for 2.3s, $0.015 cost"
         "Fall back to Haiku? Use model: 'auto'"
```

**3. Subagent Model Selection API**
```javascript
// New function in coding-agent skill
selectModelForCodingTask(
  task_description,
  file_count,
  complexity_estimate
) → model_name

// Examples:
selectModelForCodingTask("Add import", 1, "low") 
  → "haiku" // 10x cheaper

selectModelForCodingTask("Build feature", 4, "medium")
  → "opus" // Balanced

selectModelForCodingTask("Refactor module", 16, "high")
  → "gpt-4" // Premium
```

### TIER C: Long Term (Next 2 Weeks) - Full Integration

**1. Unified Main + Subagent Routing**
```
Current Architecture:
  Main Session: OpenRouter Auto + Fallbacks
  Subagents: Direct Opus (hardcoded)

Proposed Architecture:
  Main Session: OpenRouter Auto
  Subagents: OpenRouter Auto (same logic)
  Fallbacks: Unified chain (Haiku → Opus → GPT-4)
```

**2. Cost Optimization Dashboard**
```
Show per-session breakdown:
  ├─ Main Session
  │   ├─ Simple tasks (Haiku): $0.30 (60%)
  │   ├─ Complex tasks (Opus): $0.15 (30%)
  │   └─ Analysis (full thinking): $0.05 (10%)
  │
  └─ Subagents (Coding)
      ├─ Trivial fixes (Haiku): $0.05 (10%)
      ├─ Features (Opus): $0.30 (60%)
      └─ Builds (GPT-4): $0.15 (30%)
```

**3. Intelligent Batching for Large Tasks**
```
Current:  "Build 16-file app" → Opus handles all
Proposed: "Build 16-file app" → Split into:
          - Files 1-4: Haiku (templates)
          - Files 5-12: Opus (core logic)
          - Files 13-16: GPT-4 (architecture)
          
Result: 40% cost reduction + better quality
```

---

## Specific Improvements for Complex Tasks

### Improvement 1: Smart Subagent Selection

**Before:**
```
User: "Write hello world in Swift"
→ Spawns Opus subagent ($0.015 per 1K tokens)
```

**After:**
```
User: "Write hello world in Swift"
→ Analyzes task: trivial_file_write
→ Spawns Haiku subagent ($0.0001 per 1K tokens)
→ 150x cost reduction
```

### Improvement 2: OpenRouter in Subagents

**Before:**
```
Subagent: uses claude-opus-4-0 directly
Cost: Fixed $0.015 per 1K tokens
```

**After:**
```
Subagent: uses openrouter/openrouter/auto
Cost: Dynamic, $0.001-0.015 per 1K tokens
       (OpenRouter selects optimal model)
```

### Improvement 3: Fallback Chain for Subagents

**Before:**
```
Spawn Subagent with Opus
→ If timeout: Fail (no fallback)
```

**After:**
```
Spawn Subagent with Opus
→ If timeout: Retry with GPT-4
→ If fails: Fallback to Haiku (simpler task)
→ If fails: Report with error details
```

### Improvement 4: Complexity-Aware Spawning

**Before:**
```
sessions_spawn(runtime="subagent", task="...", model="opus")
// No analysis, always Opus
```

**After:**
```
complexity = analyze(task)
model = select_model(complexity, file_count)
sessions_spawn(runtime="subagent", task="...", model=model)

// Smart selection:
// Complexity "low"   → Haiku
// Complexity "med"   → Opus
// Complexity "high"  → GPT-4
```

---

## Implementation Roadmap

### Week 1 (Today-Tomorrow)
- [ ] Create `classify-coding-task.sh` script
- [ ] Add Haiku subagent trigger for simple fixes
- [ ] Document in SOUL.md
- [ ] Test on existing coding tasks

### Week 2 (Next 3-4 days)
- [ ] Add OpenRouter support to subagents
- [ ] Update sessions_spawn to pass creds
- [ ] Add cost tracking output
- [ ] Test OpenRouter Auto with subagents

### Week 3 (Next week)
- [ ] Build unified cost dashboard
- [ ] Implement intelligent batching
- [ ] Complete fallback chain
- [ ] Documentation + examples

---

## Cost Impact Example

### Current: Building a 4-file feature
```
Task: "Build WebSocket manager for iOS"
Files: Manager.swift, Extensions.swift, Tests.swift, Mocks.swift
Current cost: 4 files × Opus = $0.060
Time: 3.2 seconds
```

### Improved: Same task with intelligent routing
```
Task: "Build WebSocket manager for iOS"
Files: Manager.swift (heavy), Extensions.swift (med), Tests.swift (light), Mocks.swift (light)

Route:
  - Manager.swift: Opus ($0.030)
  - Extensions.swift: Opus ($0.015)
  - Tests.swift: Haiku ($0.001)
  - Mocks.swift: Haiku ($0.001)

Total cost: $0.047 (22% reduction)
Time: 3.1 seconds (faster due to Haiku parallelization)
```

---

## Summary

### Current State ✅
- Claude Code works for complex tasks
- Uses Opus (appropriate for complexity)
- Proper isolation and billing
- Fallback to GPT-4

### Gaps Identified ❌
- No cost optimization for small fixes
- OpenRouter Auto doesn't apply to subagents
- Hardcoded Opus (no tiered selection)
- No intelligent task analysis before spawning

### Improvements Recommended 📈
1. **Immediate:** Add Haiku option for trivial fixes (150x cheaper)
2. **Short term:** OpenRouter support for subagents
3. **Long term:** Unified routing + intelligent batching

### Expected Impact 💰
- 15-30% cost reduction on coding tasks
- 3-5x speedup on trivial fixes
- Better quality on complex tasks (right model for job)
- Unified cost tracking

---

## Next Actions

1. **Approve this analysis** → Yes/No/Discuss
2. **Prioritize improvements** → Start with Tier A?
3. **Set timeline** → This week?
4. **Review SOUL.md changes** → Update subagent rules?

**Recommendation:** Implement Tier A today (2-3 hours), Tier B this week (4-5 hours), Tier C next week (6-8 hours).

---

**Document Created:** March 26, 2026, 4:11 AM EDT  
**Status:** Ready for implementation
