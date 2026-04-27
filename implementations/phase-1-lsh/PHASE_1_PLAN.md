# Phase 1: LSH MVP Implementation Plan

**Timeline:** 1-2 weeks  
**Goal:** 10x speedup on OpenClaw memory recall  
**Target:** Deploy LSH hash-based lookup with brute-force fallback  

---

## Objectives

✅ Index 600 OpenClaw memory chunks with LSH  
✅ Integrate into memory_search() function  
✅ Add brute-force fallback if recall < 90%  
✅ Benchmark: latency, accuracy, memory  
✅ Deploy to OpenClaw with monitoring  

---

## Week 1: Setup & Prototyping

### Day 1-2: Environment Setup
- [ ] Install FAISS: `pip install faiss-cpu`
- [ ] Load existing memory embeddings (Sentence Transformers)
- [ ] Verify embedding dimensions (384D expected)
- [ ] Create test dataset (100 sample queries)

### Day 3-4: LSH Prototype
- [ ] Create LSH index with 16 hash functions
- [ ] Index all 600 memory chunks
- [ ] Test basic query (measure latency)
- [ ] Compare vs brute-force baseline
- [ ] Measure accuracy (Recall@5)

### Day 5: Integration
- [ ] Create memory_search_lsh() function
- [ ] Add fallback logic (recall threshold)
- [ ] Wire into OpenClaw memory module
- [ ] Add logging and metrics collection

---

## Week 2: Testing & Deployment

### Day 1-2: Comprehensive Testing
- [ ] Test on full 600-chunk dataset
- [ ] Measure P50, P95, P99 latencies
- [ ] Evaluate Recall@5 on 30+ real queries
- [ ] Test fallback triggers
- [ ] Monitor memory usage

### Day 3-4: Optimization
- [ ] Tune number of hash functions (8-32)
- [ ] Optimize bucket sizes
- [ ] Adjust recall threshold
- [ ] Profile hotspots
- [ ] Document tuning decisions

### Day 5: Deployment
- [ ] Deploy to OpenClaw
- [ ] Enable monitoring/alerting
- [ ] Document usage and fallback behavior
- [ ] Create rollback procedure

---

## Success Criteria

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Latency (P50) | <10ms | 100-200ms | 🎯 |
| Latency (P95) | <25ms | 100-200ms | 🎯 |
| Latency (P99) | <50ms | 100-200ms | 🎯 |
| Recall@5 | >95% | 100% | ✅ |
| Memory | <20MB | 1.5MB | ✅ |
| Fallback Rate | <5% | N/A | 🎯 |

---

## Deliverables

**Code:**
- `lsh_memory_search.py` — LSH implementation
- `lsh_config.json` — Configuration (hash functions, buckets, etc.)
- `test_lsh_integration.py` — Comprehensive test suite
- `benchmark_lsh.py` — Performance measurement script

**Documentation:**
- `PHASE_1_RESULTS.md` — Implementation results and metrics
- `LSH_TUNING_GUIDE.md` — How to adjust parameters
- `DEPLOYMENT_GUIDE.md` — How to deploy to OpenClaw
- `TROUBLESHOOTING.md` — Common issues and fixes

**Metrics:**
- Latency baseline vs LSH comparison
- Accuracy (Recall@5) on test queries
- Memory usage analysis
- Fallback rate tracking

---

## Dependencies

- Python 3.8+
- numpy
- faiss-cpu (or faiss-gpu if available)
- sentence-transformers (already in OpenClaw)

---

## Risk Mitigation

**Risk:** Recall drops below 95%  
→ **Mitigation:** Increase hash functions, fall back to brute-force

**Risk:** Performance not 10x  
→ **Mitigation:** Optimize hash functions, tune bucket sizes

**Risk:** Memory overhead too high  
→ **Mitigation:** Use quantization or compression

**Risk:** Fallback triggered too often  
→ **Mitigation:** Adjust recall threshold, retrain hash functions

---

## Next Phases (Defer to Later)

**Phase 2:** Add LRU caching (2-3 weeks)
- Cache recent queries (60-70% hit rate)
- Reduce average latency to 6-8ms

**Phase 3:** Scale to 100K+ vectors (3 months)
- Evaluate HNSW migration
- Consider vector database
- Target <10ms for any size

---

**Status:** Ready to start  
**Owner:** OpenClaw Team  
**Created:** March 29, 2026
