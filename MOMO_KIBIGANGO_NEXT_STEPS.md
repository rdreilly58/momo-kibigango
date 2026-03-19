# momo-kibigango: Phase 2 Go-Ahead Checklist

**Project:** 3-Model Speculative Decoding for OpenClaw  
**Phase 1 Status:** ✅ COMPLETE (March 19, 2026, 7:45 PM EDT)  
**Ready for:** Phase 2 Approval

---

## What Was Delivered (Phase 1)

✅ **Research:**
- Comprehensive web search on 3-model speculative decoding
- GitHub ecosystem analysis (5+ implementations reviewed)
- Paper analysis: PyramidSD (Byun et al., 2025, NeurIPS accepted)
- Technical deep-dive documentation

✅ **Analysis:**
- 16KB comprehensive technical guide (3MODEL_SPECULATIVE_DECODING_ANALYSIS.md)
- 8KB plain-English explanation (SPECULATIVE_DECODING_EXPLAINED.md)
- 9KB performance comparison report (PERFORMANCE_COMPARISON_REPORT.md)
- Phase-by-phase roadmap with success criteria

✅ **GitHub Repository:**
- Public repo: https://github.com/rdreilly58/momo-kibigango
- Clean, no secrets, ready for collaboration
- Project structure with docs/src/models/scripts/tests directories
- README.md with project overview
- ROADMAP.md with detailed timeline

---

## Decision Point: Phase 2 Go-Ahead

**Question:** Should we proceed with Phase 2 (2-Model Baseline Pilot)?

### To Approve Phase 2, Answer These Questions:

1. **Performance Justifies Effort?**
   - Question: Is 2x speedup (5 sec → 2.5 sec per query) worth 10-15 days of development?
   - Your answer: _______________

2. **AWS Migration Timeline?**
   - Question: Can we defer AWS g4dn.2xlarge deployment to focus on this (April/May)?
   - Your answer: _______________

3. **Research Credibility?**
   - Question: Satisfied that PyramidSD is well-researched (NeurIPS 2025) and worth implementing?
   - Your answer: _______________

4. **Budget & Resources?**
   - Question: Can we allocate a subagent for Phase 2 (3-5 days in April)?
   - Your answer: _______________

### If Yes to All Above:

**Approval:** 🔓 PROCEED WITH PHASE 2

---

## Phase 2 Execution Plan

If approved, here's exactly what happens:

### Week 1: April 1-5, 2026

**Task 1: Environment Setup (Half day)**
- Install vLLM or lucidrains baseline
- Download models: Qwen2-7B-4bit (target) + Phi-2-2.7B (draft)
- Verify VRAM allocation (<12GB)

**Task 2: 2-Model Implementation (2 days)**
- Implement draft-then-verify pipeline
- Integration layer with OpenClaw
- Fallback to single-model if needed

**Task 3: Benchmark Suite (1 day)**
- 5-10 test scenarios (math, writing, code, analysis, etc.)
- Measure: throughput, latency, quality
- Compare vs single-model baseline

### Week 2: April 8-15, 2026

**Task 4: Testing & Validation (1-2 days)**
- Verify 1.8-2.2x speedup
- Check for quality degradation
- Memory pressure testing
- Document findings

**Task 5: Report (Half day)**
- Phase 2 results document
- Performance metrics
- Recommendation: proceed to Phase 3?

---

## Phase 2 Success Criteria

For Phase 2 to be considered successful, ALL must be true:

- [ ] **Throughput:** 1.8-2.2x speedup achieved (24-28 tok/sec vs 12.5 baseline)
- [ ] **Memory:** VRAM usage <12GB sustained
- [ ] **Quality:** No degradation vs single-model
- [ ] **Integration:** Works seamlessly with OpenClaw
- [ ] **Fallback:** Single-model path always available
- [ ] **Documentation:** Comprehensive results document

If ANY criterion fails, Phase 2 concludes with findings + lessons learned. No automatic Phase 3.

---

## Phase 2 → Phase 3 Decision Gate

**Timeline:** April 20, 2026

**Criteria to Proceed to Phase 3:**
- Speedup targets met (1.8-2.2x confirmed)
- No quality degradation
- VRAM budget manageable
- Team capacity available

**If Blocked:** 
- Analyze failure reason
- Adjust approach
- Re-test, or pivot

---

## Phase 3 (If Approved): 3-Model Upgrade

**Timeline:** May 1-15, 2026 (3-4 days)

**What Happens:**
- Add qualifier model (Phi-1.5-1.3B)
- Implement pyramid hierarchy
- Fuzzy acceptance logic
- Optimize for Apple Silicon

**Expected Outcome:**
- 1.5-1.9x speedup (similar to Phase 2, but VRAM-efficient)
- 11GB VRAM (better than 2-model's 15-20GB)
- Better efficiency overall

---

## Immediate Action Items (If Approved)

1. **Create GitHub Issue**
   - Title: "Phase 2: 2-Model Baseline Pilot"
   - Labels: enhancement, phase-2, in-progress
   - Assign to: Claude Code subagent

2. **Repository Setup**
   - Clone: https://github.com/rdreilly58/momo-kibigango
   - Create branch: `feature/phase2-baseline`
   - Set up project board for tracking

3. **Resource Allocation**
   - Designate subagent owner
   - Reserve 3-5 days (April 1-15)
   - Establish check-in schedule

4. **Documentation**
   - Create Phase 2 implementation notes
   - Track progress daily
   - Generate final report

---

## Questions for Bob

1. Should we proceed with Phase 2?
2. Can AWS deployment wait until May (after Phase 2-3)?
3. Preference: Complete implementation vs documented design?
4. Any constraints on VRAM/power usage?

---

## Support Resources

**If you need to understand the technical details:**
- Read: `docs/3MODEL_SPECULATIVE_DECODING_ANALYSIS.md` (comprehensive)
- Or: `docs/SPECULATIVE_DECODING_EXPLAINED.md` (accessible)

**If you want to review the research:**
- Paper: https://arxiv.org/abs/2510.12966
- Publisher: NeurIPS 2025 Workshop (SPIGM)
- Authors: Google Research team

**If you need implementation examples:**
- GitHub: https://github.com/lucidrains/speculative-decoding
- GitHub: https://github.com/bassrehab/speculative-decoding
- Docs: https://docs.vllm.ai/features/speculative_decoding/

---

## Summary

✅ **Phase 1:** Research complete, documented, GitHub repo ready  
📋 **Phase 2:** Awaiting approval, 3-5 days in April  
📋 **Phase 3:** Conditional on Phase 2 success, May  
📋 **Phase 4:** Production deployment, June  

**Status:** READY TO PROCEED WITH BOB'S APPROVAL

---

**Next step:** Bob reviews analysis and approves/declines Phase 2.

If approved: Phase 2 begins April 1, 2026. 🚀
