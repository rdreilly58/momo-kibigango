# Codex Backup System - Test Plan

## Overview
Test the fallback routing system to ensure Claude Code → Codex → Opus chain works correctly.

---

## 🧪 Test Options

### Option A: Simple Swift Function Test
**Scope:** Small, focused test
**Time:** 5 minutes
**Cost:** ~$0.01

**What we test:**
1. Codex receives request
2. Codex generates Swift code
3. Code compiles in Xcode
4. Compare output to Claude Code version

**Test Task:**
```
"Create a Swift function that validates email addresses using regex. 
Include error handling and unit tests."
```

**Comparison:**
- Claude Code version
- Codex version
- Side-by-side quality review

**Pros:**
- ✅ Quick to execute
- ✅ Easy to validate (code compiles)
- ✅ Low cost
- ✅ Clear pass/fail

**Cons:**
- ⚠️ Not realistic (too simple)
- ⚠️ Doesn't test complex features

---

### Option B: Real Momotaro-iOS Feature
**Scope:** Medium, realistic task
**Time:** 30 minutes
**Cost:** ~$0.05-0.10

**What we test:**
1. Codex handles real codebase context
2. Integration with existing code
3. WebSocket/network functionality
4. Actual compilation and testing

**Test Task:**
```
"Add a struct called 'GatewayMessage' to Momotaro-iOS that represents
messages from the OpenClaw gateway. Include encoding/decoding,
error handling, and example usage in comments."
```

**Comparison:**
- Claude Code implementation
- Codex implementation
- Which is more idiomatic Swift?
- Which integrates better?

**Pros:**
- ✅ Realistic test
- ✅ Can actually use output
- ✅ Tests real integration
- ✅ Medium cost

**Cons:**
- ⚠️ Longer to evaluate
- ⚠️ Harder to compare

---

### Option C: Refactoring/Debugging Task
**Scope:** Complex, realistic
**Time:** 45 minutes
**Cost:** ~$0.10-0.20

**What we test:**
1. Codex handles complex logic
2. Problem-solving ability
3. Code quality for real refactoring
4. Understanding of existing patterns

**Test Task:**
```
"Review the Momotaro-iOS project structure and suggest improvements for:
1. Separating concerns (Model/View/ViewModel)
2. Improving state management
3. Better error handling for network requests
4. Provide refactoring steps with code examples"
```

**Comparison:**
- Claude Code architectural advice
- Codex architectural advice
- Which has better understanding of SwiftUI patterns?
- Which prioritizes best practices?

**Pros:**
- ✅ Very realistic
- ✅ Tests reasoning ability
- ✅ Can actually implement suggestions
- ✅ Shows real value

**Cons:**
- ⚠️ Takes longer to evaluate
- ⚠️ Higher cost (~$0.15)
- ⚠️ Subjective comparison

---

### Option D: Fallback Chain Test
**Scope:** Comprehensive system test
**Time:** 20 minutes
**Cost:** ~$0.05

**What we test:**
1. Routing script works correctly
2. Codex receives fallback requests properly
3. Error handling works
4. All three models accessible

**Test Task:**
Run 3 tasks with decreasing priority:
```
Task 1 (High):  "Create async/await wrapper for URLSession"
Task 2 (Medium): "Explain Swift Combine operators"
Task 3 (Low):    "What is a protocol in Swift?"
```

**Expected Results:**
- High → Claude Code (primary)
- Medium → Claude Code or Codex
- Low → Opus (free)

**Comparison:**
- Track which model handles each
- Response quality from each
- Cost tracking

**Pros:**
- ✅ Tests whole system
- ✅ Validates routing logic
- ✅ Quick to run
- ✅ Clear metrics

**Cons:**
- ⚠️ Less realistic individually
- ⚠️ Harder to compare quality

---

### Option E: All-In-One Test Suite
**Scope:** Comprehensive (all tests)
**Time:** 90 minutes
**Cost:** ~$0.30-0.50

**What we test:**
1. Option A (simple Swift)
2. Option B (real feature)
3. Option C (refactoring advice)
4. Option D (fallback chain)
5. Complete comparison matrix

**Pros:**
- ✅ Comprehensive
- ✅ Complete validation
- ✅ Full documentation
- ✅ Sets baseline for future

**Cons:**
- ⚠️ Takes 90 minutes
- ⚠️ Higher cost
- ⚠️ Lots of data to review

---

## 📊 Comparison Matrix

| Test | Time | Cost | Realism | Value | Recommendation |
|------|------|------|---------|-------|-----------------|
| **A: Simple** | 5 min | $0.01 | Low | Quick check | Start here |
| **B: Feature** | 30 min | $0.10 | High | Good output | Then this |
| **C: Refactor** | 45 min | $0.15 | High | Very useful | Optional |
| **D: Routing** | 20 min | $0.05 | Medium | System check | Include |
| **E: All** | 90 min | $0.50 | Very High | Complete | Advanced |

---

## 🎯 My Recommendations

### Minimum (Quick Validation) — ~30 minutes, $0.15
1. **Option A** (5 min) — Verify Codex works
2. **Option D** (20 min) — Verify routing chain
3. **Quick review** (5 min) — Quality assessment

**Outcome:** Know if system works

---

### Recommended (Good Confidence) — ~55 minutes, $0.25
1. **Option A** (5 min) — Simple function
2. **Option B** (30 min) — Real Momotaro feature
3. **Option D** (20 min) — Routing validation

**Outcome:** Know if system works AND produces usable code

---

### Complete (Full Assurance) — ~90 minutes, $0.50
1. **Option A** (5 min) — Simple test
2. **Option B** (30 min) — Real feature
3. **Option C** (45 min) — Architecture review
4. **Option D** (10 min) — Final routing check

**Outcome:** Complete validation, ready for production use

---

## 📋 My Suggestion: Two-Phase Approach

### Phase 1: Quick Validation (Today) — 30 min, $0.15
- Run Options A + D
- Verify Codex works
- Verify routing works
- Quick quality check

### Phase 2: Real-World Test (This Week) — 30 min, $0.10
- Run Option B with actual Momotaro feature
- See if output is production-ready
- Fine-tune routing based on results

---

## What Do You Prefer?

**Quick Check (5 tests, $0.15):**
- Just verify it works
- Fast, cheap validation
- Good for peace of mind

**Solid Validation (3 tests, $0.25):**
- Verify it works
- Get real usable code
- Build confidence
- **← My recommendation**

**Complete Assurance (4 tests, $0.50):**
- Verify everything
- Get architecture advice
- Full documentation
- Advanced setup

Which approach appeals to you? 🍑
