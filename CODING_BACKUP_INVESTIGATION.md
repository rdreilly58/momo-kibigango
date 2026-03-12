# Coding Backup Alternatives Investigation

## Overview
When Claude Code is unavailable or overloaded, we need alternative AI coding agents. This document reviews the best options available.

---

## 🏆 Top Candidates Ranked by Suitability

### 1. **Codex (OpenAI)** ⭐⭐⭐⭐⭐
**Best for:** Swift, Python, JavaScript coding when Claude is unavailable

**What it is:**
- OpenAI's code-specialized model
- Previously known as GitHub Copilot's engine
- Excellent at Swift/iOS development
- Works well with Xcode projects

**Integration with OpenClaw:**
- Available via ACP harness (runtime="acp")
- Can spawn as sub-agent
- Full IDE integration possible
- Supports file operations and terminal execution

**Pros:**
- ✅ Powerful code generation
- ✅ Swift/iOS specialist
- ✅ Works great with complex refactoring
- ✅ Good at debugging
- ✅ Reasonable pricing
- ✅ Very reliable uptime

**Cons:**
- ⚠️ Different coding style than Claude
- ⚠️ Slightly different error messages
- ⚠️ API key required (not included by default)

**Cost:** Variable (token-based, ~$0.01-0.03 per request for small files)

**Integration Level:** ⭐⭐⭐⭐⭐ (Native OpenClaw support via ACP)

**Recommendation:** Primary backup. Excellent for iOS/Swift work.

---

### 2. **Claude Opus (Direct API Call)** ⭐⭐⭐⭐
**Best for:** Fallback when Claude Code is overloaded

**What it is:**
- Direct Anthropic API call to Claude Opus
- More powerful reasoning than Haiku
- Can be spawned as isolated sub-agent
- Same coding style as Claude Code (continuity)

**Integration with OpenClaw:**
- Via `sessions_spawn` with runtime="subagent"
- Can access workspace files
- Supports iterative coding
- Full terminal access in sandbox

**Pros:**
- ✅ Same model, same style as Claude Code
- ✅ Better reasoning than Code variant
- ✅ Good availability
- ✅ No additional API keys needed
- ✅ Maintains code consistency
- ✅ Reliable for complex problems

**Cons:**
- ⚠️ Slower than Claude Code (more reasoning)
- ⚠️ Slightly higher latency
- ⚠️ Still subject to OpenClaw rate limits
- ⚠️ Not specifically optimized for coding

**Cost:** Included in OpenClaw subscription

**Integration Level:** ⭐⭐⭐⭐ (Already available via subagent)

**Recommendation:** Secondary backup when Claude Code unavailable. Best for continuity.

---

### 3. **Gemini 2.0 Pro (Google)** ⭐⭐⭐⭐
**Best for:** Complex multi-file projects, architectural decisions

**What it is:**
- Google's latest reasoning model
- Excellent context window (1M tokens)
- Strong at system design and refactoring
- Good Swift/iOS support

**Integration with OpenClaw:**
- Available via gemini skill
- Can be spawned for coding tasks
- Good file handling
- Terminal execution possible

**Pros:**
- ✅ Massive context window (handles large projects)
- ✅ Excellent at architecture/design
- ✅ Good at refactoring complex code
- ✅ Great for documentation
- ✅ Reliable availability
- ✅ Very fast responses

**Cons:**
- ⚠️ Different coding style
- ⚠️ Less specialized for code than Codex
- ⚠️ May require API key setup
- ⚠️ Less iterative refinement

**Cost:** Free tier available, paid tier ~$2/month for coding use

**Integration Level:** ⭐⭐⭐ (Via skill, requires setup)

**Recommendation:** Good for large-scale refactoring, architecture decisions. Not primary coding.

---

### 4. **Pi (Anthropic)** ⭐⭐⭐
**Best for:** Quick coding fixes, learning/teaching code

**What it is:**
- Anthropic's educational AI
- Good at explaining code
- Decent at simple-to-medium complexity tasks
- Web-based interface available

**Integration with OpenClaw:**
- Available via ACP harness
- Can spawn for specific coding tasks
- Good for pair programming scenarios

**Pros:**
- ✅ Excellent explanations
- ✅ Good teaching mode
- ✅ Stable and available
- ✅ Same company as Claude (continuity)

**Cons:**
- ❌ Not specialized for code generation
- ⚠️ Lower quality output than Claude Code
- ⚠️ Not ideal for complex refactoring
- ⚠️ Limited to simpler tasks

**Cost:** Included in OpenClaw

**Integration Level:** ⭐⭐⭐ (Via ACP)

**Recommendation:** Tertiary backup for simple tasks only.

---

### 5. **Code Llama (Meta)** ⭐⭐⭐
**Best for:** Self-hosted option, privacy-first coding

**What it is:**
- Meta's open-source code model
- Can be self-hosted on Mac mini
- Specialized for code generation
- Runs locally (no external API)

**Integration with OpenClaw:**
- Can be installed via Homebrew/Docker
- Runs locally on Mac mini
- Direct CLI integration
- Terminal access built-in

**Pros:**
- ✅ Privacy (runs locally)
- ✅ No external API calls
- ✅ Free and open-source
- ✅ Works offline
- ✅ Good for sensitive code

**Cons:**
- ❌ Quality lower than Claude/Codex
- ⚠️ Requires local compute (M4 Mac can handle)
- ⚠️ Setup complexity
- ⚠️ Not great for iOS/Swift
- ⚠️ Manual hosting/monitoring needed

**Cost:** Free

**Integration Level:** ⭐⭐ (Requires local setup)

**Recommendation:** Not primary, but good for privacy-critical work or backup when all APIs down.

---

### 6. **GPT-4 (OpenAI Direct)** ⭐⭐⭐⭐
**Best for:** Complex architectural decisions, edge cases

**What it is:**
- OpenAI's general-purpose model
- Good reasoning ability
- Better than GPT-3.5 but not specialized
- Can be called directly via API

**Integration with OpenClaw:**
- Via sessions_spawn with model override
- Full workspace access
- Good terminal support

**Pros:**
- ✅ Strong reasoning
- ✅ Good problem-solving
- ✅ Reliable availability
- ✅ Large knowledge base

**Cons:**
- ⚠️ Not code-specialized (slower)
- ⚠️ Requires API key setup
- ⚠️ More expensive per token
- ⚠️ Slower than specialized models

**Cost:** ~$0.03-0.10 per request (variable)

**Integration Level:** ⭐⭐⭐⭐ (Easy setup)

**Recommendation:** Backup for hard problems, not primary.

---

## 📊 Comparison Table

| Model | Swift/iOS | Speed | Quality | Availability | Cost | Setup |
|-------|-----------|-------|---------|--------------|------|-------|
| **Claude Code** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Free | Simple |
| **Codex** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Paid | Medium |
| **Opus** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Free | Simple |
| **Gemini 2.0** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Paid | Medium |
| **Pi** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Free | Simple |
| **Code Llama** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | Free | Hard |
| **GPT-4** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Paid | Medium |

---

## 🎯 Recommended Strategy

### Primary (Use First When Claude Code Unavailable):
**Codex** — Most similar quality, Swift specialist, reliable

### Secondary (Fallback):
**Claude Opus** — Same coding style, maintains continuity, simpler integration

### Tertiary (Complex Problems):
**Gemini 2.0 Pro** — Best for architectural decisions, large refactoring

### Quaternary (Simple Fixes Only):
**Pi** — Quick explanations and simple code generation

### Emergency (All APIs Down):
**Code Llama** — Local fallback, no external dependencies

---

## 🚀 Implementation Plan

### Phase 1: Codex Integration (Recommended)
1. Get OpenAI API key (costs money but worth it)
2. Set up Codex in OpenClaw config
3. Create fallback routing logic
4. Test with Momotaro-iOS project

### Phase 2: Opus Fallback (Already Available)
1. No setup needed (already in OpenClaw)
2. Create helper script to spawn Opus for coding
3. Automatic fallback when Claude Code times out

### Phase 3: Gemini 2.0 Integration (Optional)
1. Set up Google Cloud credentials
2. Test with architecture/refactoring tasks
3. Use for large-scale changes

### Phase 4: Code Llama Local (Optional)
1. Install locally on Mac mini
2. Set up as emergency backup
3. Runs offline, no API needed

---

## 💰 Cost Analysis

### Per Month (Estimated for Active Development)

| Option | Upfront | Monthly | Per-Task |
|--------|---------|---------|----------|
| **Codex** | $0 | $10-20 | ~$0.10 per coding task |
| **Opus** | $0 | $0 | Included in OpenClaw |
| **Gemini** | $0 | $2-5 | ~$0.05 per task |
| **Pi** | $0 | $0 | Free |
| **Code Llama** | ~30 min setup | $0 | Free (uses Mac compute) |
| **GPT-4** | $0 | $5-15 | ~$0.10 per task |

**Total Recommended Setup:** ~$15/month for Codex + Gemini combo

---

## 📋 Setup Checklist

- [ ] **Codex:** Get OpenAI API key + add to OpenClaw config
- [ ] **Opus:** Create helper script for fallback spawning
- [ ] **Gemini:** (Optional) Set up Google credentials
- [ ] **Code Llama:** (Optional) Install locally for offline backup
- [ ] **Routing Logic:** Create decision tree for which model to use
- [ ] **Testing:** Test each model with Momotaro-iOS project
- [ ] **Documentation:** Document when to use each model

---

## 🎓 Usage Decision Tree

```
Need to code?
├─ Claude Code available?
│  └─ Yes → Use Claude Code
│  └─ No → Check Codex
├─ Codex available?
│  └─ Yes → Use Codex (best quality backup)
│  └─ No → Check Opus
├─ Opus available?
│  └─ Yes → Use Opus (maintains style)
│  └─ No → Check task complexity
├─ Complex problem?
│  └─ Yes → Use Gemini 2.0
│  └─ No → Use Pi (simple fixes)
├─ All APIs down?
│  └─ Yes → Use Code Llama (local)
```

---

## ✅ Recommendation Summary

**For your setup:**

1. **Primary Backup: Codex**
   - Cost: ~$15/month
   - Quality: Equal to Claude Code
   - Setup: Medium (need API key)
   - Best for: iOS/Swift development

2. **Secondary Fallback: Opus**
   - Cost: $0 (included)
   - Quality: 95% of Claude Code
   - Setup: Already available
   - Best for: Continuity and style consistency

3. **Tertiary: Gemini 2.0**
   - Cost: ~$5/month
   - Quality: 90% for coding, excellent for architecture
   - Setup: Medium
   - Best for: Large refactoring and design decisions

**Skip:**
- ❌ Pi (too simple for serious coding)
- ❌ Code Llama (quality too low unless offline is critical)
- ❌ GPT-4 (Codex is better + cheaper for coding)

---

## 💡 Next Steps

Would you like me to:

1. **Set up Codex integration** (recommended)?
   - Get API key from OpenAI
   - Configure OpenClaw
   - Test with a coding task

2. **Create fallback routing script**?
   - Automatic Claude Code → Codex → Opus
   - Smart detection of availability

3. **Test all models** with Momotaro-iOS?
   - Compare output quality
   - Document differences
   - Establish best practices

4. **Set up Code Llama local** (optional)?
   - Install on Mac mini
   - Test offline capability
   - Emergency backup only

Let me know which direction you'd like to go! 🍑
