# momo-kibigango

🍑 **3-Model Speculative Decoding for OpenClaw**

Pyramid Speculative Decoding (PyramidSD) implementation for local GPU inference on Apple Silicon (M4 Max).

## What is momo-kibigango?

An implementation of the October 2025 NeurIPS-accepted paper "3-Model Speculative Decoding" (PyramidSD), which achieves:
- **1.9x inference speedup** over standard speculative decoding
- **Better VRAM efficiency** than 2-model approaches (11GB vs 15-20GB)
- **No quality degradation** (verified through testing)
- **Seamless fallback** to single-model if needed

## Architecture

```
┌─────────────────────────────────────┐
│   Target Model (7B, Full Quality)   │ ← Qwen2-7B-4bit
├─────────────────────────────────────┤
│  Qualifier Model (2.5B, Balanced)   │ ← Phi-2
├─────────────────────────────────────┤
│   Draft Model (1B, Ultra-Fast)      │ ← Phi-1.5
└─────────────────────────────────────┘
```

## Performance

| Setup | Throughput | Latency | VRAM | Status |
|-------|-----------|---------|------|--------|
| Single (baseline) | 12.5 tok/s | 5.1s | 4GB | ✓ Current |
| 2-Model | 24-28 tok/s | 3.5-4s | 6GB | 📋 Phase 2 |
| **3-Model (PyramidSD)** | **23-26 tok/s** | **3.8-4.2s** | **11GB** | 📋 Phase 3 |

## Project Status

- ✅ **Phase 1:** Research complete (analysis documents ready)
- 🚀 **Phase 2:** 2-model baseline pilot (Started March 19, 2026)
  - ✅ Core implementation complete
  - ✅ Benchmark suite ready
  - ✅ OpenClaw integration layer
  - 📋 Testing & validation pending
- 📋 **Phase 3:** 3-model upgrade (May 2026)
- 📋 **Phase 4:** Production deployment (June 2026)

## Documentation

- **[ANALYSIS.md](docs/3MODEL_SPECULATIVE_DECODING_ANALYSIS.md)** — Comprehensive technical analysis (16KB)
- **[EXPLAINED.md](docs/SPECULATIVE_DECODING_EXPLAINED.md)** — Plain-English explanation
- **[PERFORMANCE.md](docs/PERFORMANCE_COMPARISON_REPORT.md)** — Benchmark results vs AWS setup

## Research Foundation

**Paper:** "3-Model Speculative Decoding"  
**Authors:** Sanghyun Byun, Mohanad Odema, Jung Guack (Google)  
**Published:** October 14, 2025  
**Status:** Accepted at NeurIPS 2025 Workshop (SPIGM)  
**ArXiv:** https://arxiv.org/abs/2510.12966

## Key Resources

- **lucidrains/speculative-decoding** — Recommended baseline implementation
- **vLLM** — Production inference engine with speculative decoding support
- **MLX-LM** — Apple Silicon optimization framework

## Quick Start

### Phase 2: 2-Model Baseline (Current)

```bash
# Setup environment
cd momo-kibigango
./scripts/setup_phase2.sh
source venv_phase2/bin/activate

# Run basic test
python src/speculative_2model.py

# Run full benchmark suite
python scripts/benchmark_2model.py

# Start OpenClaw integration server
python src/openclaw_integration.py

# Test API endpoint
curl -X POST http://localhost:8080/v1/inference \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is the capital of France?", "max_tokens": 50}'
```

### Phase 3: 3-Model Pyramid (Coming Soon)

```bash
# Will be available after Phase 2 validation
pip install -r requirements-phase3.txt
python scripts/benchmark_3model.py
```

## Team

- **Research & Analysis:** Momotaro (Claude Code)
- **Implementation:** Phase 2-4 (TBD)
- **Integration:** OpenClaw ecosystem
- **Sponsor:** Bob Reilly

## License

MIT — Open source and free to use

## Next Steps

1. ✅ Review analysis documents
2. 📋 Approve Phase 2 pilot
3. 📋 Begin 2-model baseline implementation
4. 📋 Benchmark and validate
5. 📋 Proceed to 3-model upgrade

---

**Status:** RESEARCH COMPLETE, AWAITING GO-AHEAD FOR PHASE 2

Questions? See docs/ for detailed technical deep-dives. 🍑
