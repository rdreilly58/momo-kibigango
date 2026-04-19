# Tier C: Intelligent Batching Design Document

## Overview

**Tier C** implements intelligent task batching to achieve 10-20% additional cost savings by:
1. Analyzing large tasks for complexity distribution
2. Splitting complex work into Haiku/Opus/GPT-4 subtasks
3. Batching similar-complexity work together
4. Reducing redundant context switching
5. Optimizing token usage per model tier

**Expected additional savings:** 10-20% on top of Tier A + B (64-78%)  
**Total expected savings:** 75-85% overall cost reduction

---

## Problem Statement

Current Tier A + B approach:
- ✅ Routes each task to optimal model
- ✅ Saves 64-78% on single tasks
- ❌ Doesn't optimize large multi-file projects
- ❌ Doesn't batch similar work together
- ❌ May spawn multiple subagents inefficiently

### Example: Build New Feature (6 files)

**Without Tier C:**
```
Task: "Add caching layer to network module"
→ Classifies as: OPUS (medium complexity)
→ Spawns 1 subagent: Opus
→ Cost: $0.30 (6 files × $0.05 per file avg)
```

**With Tier C:**
```
Task: "Add caching layer to network module (6 files)"
→ Analyzes each file requirement:
   • NetworkCache.swift (implement) → OPUS tier
   • CacheDelegate.swift (implement) → OPUS tier
   • NetworkManager+Cache (modify) → HAIKU tier (small change)
   • Tests (3 files, add tests) → HAIKU tier (boilerplate)
   • Documentation (update) → HAIKU tier (minor)

→ Batching decision:
   • Batch 1: OPUS (2 complex files) - $0.10
   • Batch 2: HAIKU (4 simpler tasks) - $0.04
   
→ Total cost: $0.14 (53% savings vs $0.30)
```

---

## Architecture

### Three Components

**1. Task Analyzer (analyze-task-complexity.sh)**
- Parse task description + file list
- Determine per-file complexity
- Identify dependencies
- Create execution plan

**2. Task Splitter (split-complex-task.sh)**
- Break large tasks into subtasks
- Group by complexity tier (Haiku/Opus/GPT-4)
- Maintain dependency order
- Generate execution sequence

**3. Batch Executor (execute-batch.sh)**
- Spawn subagents for each batch
- Track costs per batch
- Monitor dependencies
- Report aggregated results

---

## Algorithm: Task Analysis

### Input
```
Task description + list of files (optional)
Example: "Add Redis caching to network layer (NetworkCache.swift, 
          CacheManager.swift, NetworkManager.swift, tests/)"
```

### Step 1: Parse Files & Identify Scope

```bash
# Extract file list
FILES=$(echo "$TASK" | grep -o '\([^ ]*\.swift\|[^ ]*\.ts\|[^ ]*\.py\)')
COUNT=$(echo "$FILES" | wc -l)

# Determine scope
if [ $COUNT -le 2 ]; then
  SCOPE="small"     # 1-2 files
elif [ $COUNT -le 5 ]; then
  SCOPE="medium"    # 3-5 files
else
  SCOPE="large"     # 6+ files
fi
```

### Step 2: Per-File Complexity Assessment

For each file, analyze keywords:

```bash
# NEW FILE (create) detection
if [[ "$FILE_DESC" =~ "create|new|add.*file" ]]; then
  COMPLEXITY="opus"  # Need to design from scratch
fi

# MODIFICATION detection (small)
if [[ "$FILE_DESC" =~ "fix|format|lint|add.*line|one.*change" ]]; then
  COMPLEXITY="haiku"  # Minor change
fi

# MODIFICATION detection (medium)
if [[ "$FILE_DESC" =~ "add feature|implement|refactor|optimize" ]]; then
  COMPLEXITY="opus"  # Medium modification
fi

# MODIFICATION detection (large)
if [[ "$FILE_DESC" =~ "redesign|rewrite|major refactor" ]]; then
  COMPLEXITY="gpt4"  # Complex redesign
fi

# TEST FILES
if [[ "$FILE" =~ "test|spec" ]]; then
  COMPLEXITY="haiku"  # Tests are boilerplate, use Haiku
fi

# DOCUMENTATION
if [[ "$FILE" =~ "\.md|README|CHANGELOG" ]]; then
  COMPLEXITY="haiku"  # Docs are simple
fi
```

### Step 3: Batching Strategy

```
Haiku Batch (Cost: $0.0001/task):
  • Simple modifications
  • Test files
  • Documentation
  • Lint/format fixes
  • Single-line changes

Opus Batch (Cost: $0.015/task):
  • New file creation
  • Medium modifications
  • Feature additions
  • Refactoring (not major)
  • Architecture (not redesign)

GPT-4 Batch (Cost: $0.030/task):
  • Major redesigns
  • Complex architecture changes
  • Multiple interdependent features
  • Performance-critical code
```

### Step 4: Dependency Resolution

```bash
# Build dependency graph
DEPENDS_ON=$(grep -l "import\|require\|from.*import" "$FILE" | \
  grep -E "($FILES_LIST)" || echo "")

# Determine execution order
if [ -n "$DEPENDS_ON" ]; then
  DEPENDS_ON_TIER=$(classify_file "$DEPENDS_ON")
  # Ensure dependency tier runs first
fi
```

---

## Implementation Plan

### Phase 1: Task Analyzer (2 hours)
- [ ] Create analyze-task-complexity.sh
- [ ] Parse task descriptions + file lists
- [ ] Per-file complexity assessment
- [ ] Output: JSON batch plan
- [ ] Test on 5 scenarios

### Phase 2: Task Splitter (1.5 hours)
- [ ] Create split-complex-task.sh
- [ ] Batch grouping logic
- [ ] Dependency ordering
- [ ] Cost calculation per batch
- [ ] Test on large tasks

### Phase 3: Batch Executor (2 hours)
- [ ] Create execute-batch.sh
- [ ] Sequential batch spawning
- [ ] Cross-batch dependency handling
- [ ] Progress tracking
- [ ] Cost aggregation
- [ ] Final report generation

### Phase 4: Integration (1 hour)
- [ ] Update SOUL.md with Tier C rules
- [ ] Add to cost tracking system
- [ ] Documentation & examples
- [ ] Testing (5+ scenarios)

### Phase 5: Testing (1 hour)
- [ ] Small task (1-2 files)
- [ ] Medium task (3-5 files)
- [ ] Large task (6+ files)
- [ ] Complex dependencies
- [ ] Verify cost savings

**Total estimated time: 7.5 hours** (or 4-6 hours if optimized)

---

## Example: Real Task Breakdown

### Scenario 1: Small Task (2 files)
```
Task: "Fix typo in error message and import"
Files: ErrorHandler.swift, Logger.swift

Analysis:
  • ErrorHandler.swift: "fix typo" → HAIKU
  • Logger.swift: "add import" → HAIKU

Batching:
  Batch 1 (HAIKU): Both files
  
Cost:
  • Expected: $0.015 (Opus, no batching)
  • Tier C: $0.0001 (Haiku batch)
  • Savings: 150x ✅
```

### Scenario 2: Medium Task (4 files)
```
Task: "Implement caching layer (4 files)"
Files: NetworkCache.swift (new), CacheManager.swift (new),
       NetworkManager.swift (modify), tests/CacheTests.swift

Analysis:
  • NetworkCache.swift: "create from scratch" → OPUS
  • CacheManager.swift: "create from scratch" → OPUS
  • NetworkManager.swift: "add cache support" → HAIKU
  • tests/CacheTests.swift: "write tests" → HAIKU

Batching:
  Batch 1 (OPUS): NetworkCache, CacheManager (2 files)
  Batch 2 (HAIKU): NetworkManager modification + tests (2 files)
  
Cost:
  • Expected: $0.06 (Opus all, no batching)
  • Tier C: $0.035 (Opus batch $0.03 + Haiku batch $0.0001)
  • Savings: 42% ✅
```

### Scenario 3: Large Task (8 files, complex)
```
Task: "Refactor auth system (8 files)"
Files: AuthManager.swift (major refactor), TokenCache.swift (new),
       LoginViewController.swift (modify), ProfileViewController.swift (modify),
       tests/ (4 test files), docs/ (README update)

Analysis:
  • AuthManager: "major refactor" → GPT-4
  • TokenCache: "create new" → OPUS
  • LoginViewController: "modify for new auth" → OPUS
  • ProfileViewController: "modify for new auth" → OPUS
  • tests/ (4 files): "write tests" → HAIKU
  • docs/README: "update" → HAIKU

Batching:
  Batch 1 (GPT-4): AuthManager (1 file) - $0.030
  Batch 2 (OPUS): TokenCache, ViewControllers (3 files) - $0.045
  Batch 3 (HAIKU): Tests, docs (5 files) - $0.0005
  
Cost:
  • Expected: $0.30 (GPT-4 all, no batching)
  • Tier C: $0.0755 (batched)
  • Savings: 75% ✅
```

---

## Cost Savings Model

### Formula

```
Without Tier C (all tasks use highest model):
  Cost = NumFiles × CostOfHighestModel

With Tier C (intelligent batching):
  CostHaiku = NumHaikuTasks × 0.0001
  CostOpus = NumOpusTasks × 0.015
  CostGPT4 = NumGPT4Tasks × 0.030
  Cost = CostHaiku + CostOpus + CostGPT4
```

### Expected Savings by Task Size

| Task Size | Avg Savings | Example |
|-----------|------------|---------|
| 1-2 files | 150x (Haiku) | $0.015 → $0.0001 |
| 3-5 files | 40-50% | $0.06 → $0.03 |
| 6-10 files | 60-70% | $0.15 → $0.045 |
| 10+ files | 70-80% | $0.30 → $0.06 |

### Monthly Impact (Tier A + B + C)

Assuming monthly coding work:
- 50 small fixes: 50 × $0.0001 = $0.005
- 30 medium features: 30 × $0.02 = $0.60
- 5 large refactors: 5 × $0.10 = $0.50
- 2 complex builds: 2 × $0.20 = $0.40

**With Tier C:**
- Total: $1.55/month
- **Compared to Tier A + B: $0.85-1.00** (additional 15-20% savings)
- **Compared to baseline: $2.38** (76-79% total reduction)

---

## Success Criteria

### Phase 1: Analysis
- [ ] Parse task descriptions accurately
- [ ] Identify file lists (explicit or inferred)
- [ ] Classify per-file complexity correctly
- [ ] Output valid JSON plan

### Phase 2: Splitting
- [ ] Group files by complexity tier
- [ ] Respect dependency order
- [ ] Calculate accurate costs
- [ ] Handle edge cases (circular deps, etc)

### Phase 3: Execution
- [ ] Spawn batches in correct order
- [ ] Wait for dependencies
- [ ] Track costs per batch
- [ ] Aggregate results

### Phase 4: Testing
- [ ] 5/5 test scenarios pass
- [ ] Cost savings verified (10-20%)
- [ ] No loss of quality
- [ ] Documentation complete

---

## Risk Mitigation

### Risk 1: Over-batching (Loss of Quality)
**Mitigation:** Limit batch size to 2-3 related files. Larger batches spawn separately.

### Risk 2: Dependency Mishandling
**Mitigation:** Build dependency graph. Topological sort for execution order.

### Risk 3: Misclassification of Complexity
**Mitigation:** Conservative (err on side of higher model). Can always downgrade.

### Risk 4: Integration with Tier A + B
**Mitigation:** Tier C is optional wrapper around Tier A + B. No breaking changes.

---

## Open Questions

1. **Should Tier C be automatic or opt-in?**
   - Current design: Opt-in (user specifies file list)
   - Alternative: Auto-detect from context (more complex)

2. **How to handle file list inference?**
   - Option A: Require explicit file list
   - Option B: Parse from task description keywords
   - Option C: Ask Claude Code for file list

3. **When to spawn vs batch?**
   - Current: Batch if same tier + <3 files
   - Alternative: Always batch related work

4. **How to handle inter-batch communication?**
   - Option A: Run independently (no communication)
   - Option B: Share context via files
   - Option C: Full subagent context inheritance

---

## Next Steps

1. **Design review** with Bob (this document)
2. **Approval** to proceed with implementation
3. **Phase 1:** Task analyzer (2 hours)
4. **Phase 2:** Task splitter (1.5 hours)
5. **Phase 3:** Batch executor (2 hours)
6. **Phase 4:** Integration (1 hour)
7. **Phase 5:** Testing (1 hour)
8. **Deploy & monitor**

---

## References

- Tier A Design: Smart task classification
- Tier B Design: OpenRouter intelligent routing
- Cost tracking: Daily logs in ~/.openclaw/logs/subagent-costs/
- SOUL.md: Rules & decisions documentation

