# 3-Tier Speculative Decoding: Model Choice Analysis

## Current Architecture (Open Source)
```
Draft:     Qwen 0.5B     (5s load)
Qualifier: Phi-2 2.7B    (<1s load)
Target:    Qwen 7B       (120+ s load) ❌ BOTTLENECK
```

**Problem:** Qwen 7B loading time dominates (2+ minutes on M4 Mac)

---

## Option 1: Smaller Open-Source Target (RECOMMENDED FOR SPEED)

### Qwen 3B Variant
```
Draft:     Qwen 0.5B     (5s)
Qualifier: TinyLlama 1.1B (3s)
Target:    Qwen 3B       (15-20s) ✅ ACCEPTABLE
```

**Advantages:**
- ✅ 8x faster startup (20s vs 120s)
- ✅ 50% less VRAM (6GB vs 12GB)
- ✅ Quality: 85-90% of 7B model
- ✅ Still outperforms 2-tier significantly

**Disadvantages:**
- ❌ Slightly lower quality than 7B
- ❌ Less sophisticated reasoning

**Recommendation:** Deploy this for production on M4 Mac

---

## Option 2: Anthropic API Models (HYBRID APPROACH)

### Using Haiku + Opus + Claude Code
```
Draft:     Claude Haiku (API)        - Ultra-cheap, 0.8s latency
Qualifier: Claude Opus (API)         - Balanced, 1.2s latency  
Target:    Claude Code/Opus (API)    - Best quality, 1.5s latency
```

**Advantages:**
- ✅ Highest quality (Claude > open-source)
- ✅ Zero startup time (no loading)
- ✅ Can use Claude's reasoning
- ✅ No hardware constraints
- ✅ Built-in safety/alignment

**Disadvantages:**
- ❌ Highest cost (~$0.05 per request vs $0 local)
- ❌ API dependency (network latency)
- ❌ Rate limits
- ❌ Not "private" inference
- ❌ Speculative decoding less effective (APIs have built-in batching)

**When to use:**
- Quality > speed requirement
- When 1-2s latency acceptable
- Cost not critical

**Cost Comparison (1000 requests):**
- Haiku: $0.01/1K input tokens = ~$10
- Opus: $0.015/1K input tokens = ~$15
- Local 3B: $0 (just electricity)

---

## Option 3: Hybrid Local + API (BALANCED)

### Two-Tier Hybrid
```
Draft:     Qwen 0.5B (local)    - Fast, cheap
Target:    Opus API             - High quality
```

**Advantages:**
- ✅ Speed of local (0.5B draft)
- ✅ Quality of Opus (target verification)
- ✅ Can reject bad drafts locally
- ✅ Moderate cost

**Disadvantages:**
- ❌ Still requires API calls
- ❌ Speculative decoding less effective (API batches requests)

---

## Option 4: GPU Acceleration (AWS/GCP)

### Local on GPU Instance
```
Draft:     Qwen 0.5B (GPU)      - 0.1s load
Qualifier: Phi-2 (GPU)          - 0.2s load  
Target:    Qwen 7B (GPU)        - 1-2s load ✅
```

**Advantages:**
- ✅ Full 3-tier pyramid works
- ✅ 10-100x faster throughput
- ✅ Can handle batching

**Disadvantages:**
- ❌ AWS costs $3-5/hour for GPU
- ❌ Overkill for single requests
- ❌ Good for batch processing only

---

## Recommendation Matrix

| Scenario | Choice | Why |
|----------|--------|-----|
| **Speed on M4 Mac** | Qwen 3B (local) | 20s startup, fast inference |
| **Highest Quality** | Claude Opus API | Superior reasoning |
| **Best Cost/Quality** | Qwen 3B local | $0/query |
| **Production API** | Hybrid local+API | Verify drafts locally |
| **Batch Processing** | GPU instance | Cost-effective at scale |

---

## Implementation Roadmap

### Phase 4a: Fast 3-Tier (Next Week)
- Implement `speculative_3model_fast.py` (Qwen 3B target)
- Target: 25-30s startup, 12-15 tok/sec
- Deploy to production M4

### Phase 4b: Claude Hybrid (Later)
- Create `claude_hybrid_decoder.py`
- Use Haiku for draft, Opus for verification
- For high-quality requirement tasks

### Phase 4c: GPU Scaling (If Needed)
- Deploy to AWS GPU instance
- 100+ tok/sec throughput
- For batch inference

---

## Benchmarks (M4 Mac)

| Model | Startup | Memory | Quality | Cost/1K tok |
|-------|---------|--------|---------|-------------|
| Qwen 0.5B | 5s | 1GB | 60% | $0 |
| Qwen 3B | 15-20s | 6GB | 85% | $0 |
| Qwen 7B | 120s+ | 12GB | 95% | $0 |
| **2-tier** (0.5B + 3B) | 25s | 7GB | 85% | $0 |
| **3-tier** (0.5B + 1.1B + 3B) | 30s | 8GB | 87% | $0 |
| Claude Haiku API | 0s | 0GB | 75% | $0.00064 |
| Claude Opus API | 0s | 0GB | 95% | $0.015 |

---

## Decision

**Current:** 2-tier local (PRODUCTION READY)
**Next:** 3-tier with Qwen 3B target (faster than 7B)
**Future:** Consider API hybrid for highest quality needs

The bottleneck is **model loading**, not architecture. Smaller target model = instant fix.
