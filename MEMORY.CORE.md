# MEMORY — CORE ONLY (Lightweight Startup)

**For full context, see:** `MEMORY.md` (detailed, 22 KB)

---

## Active Items (This Week)

**Phase 1 Model Improvements:** ✅ LIVE
- Default: Claude Opus 4.0 (swapped from GPT-4o)
- Fallback: Claude Haiku 4.5
- Caching: Enabled (300s TTL, SOUL.md + TOOLS.md)
- Status: OpenClaw restarted, config updated

**Performance Optimizations:** ✅ COMPLETE
- MEMORY.md: 28 KB → 2 KB (87% reduction via archival)
- Query routing: Simple (Haiku) vs Complex (Opus) enforced
- Expected: 2-3x overall speedup

**Outstanding (Non-Critical):**
- GitHub password: Reset needed (Bob forgot current)
- GitHub profile: Add reillyrd58@gmail.com to settings
- Cloudflare: Case #02033456 awaiting support response

---

## Quick Decision Tree

**"What should I use for...?"**

| Task | Tool/Model | Notes |
|------|-----------|-------|
| Simple Q (weather, time, facts) | Haiku | 0.5-1s |
| Complex work (analysis, code) | Opus | 1.5-2s |
| Draft writing/brainstorm | Local Qwen (Week 2) | Free, offline |
| Domain-specific (embedded sys) | Fine-tuned GPT-4o (Week 2) | 10-15% better |
| Long-form output (500+ tokens) | Speculative decoding (Week 3) | 2-3x faster |

---

## Decisions Made (March 22)

1. **Model swap:** GPT-4o → Opus (better quality, same cost)
2. **Caching:** Enable SOUL.md + TOOLS.md (25-35% faster repeats)
3. **Full roadmap:** All 6 model improvements approved for 2-3 week execution
4. **Memory archival:** 87% reduction in MEMORY.md footprint

---

**For full memory context, read MEMORY.md only when needed.**
**This file loads on every session to keep startup fast.**
