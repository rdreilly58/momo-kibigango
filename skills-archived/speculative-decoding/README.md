# Speculative Decoding Skill - Phase 1 Complete

**Status:** Phase 1 (Setup & Testing) - READY TO LAUNCH  
**Date:** March 16, 2026  
**Goal:** Evaluate 2-3x speedup for simple tasks using vLLM speculative decoding

---

## 📦 What's Included

### Directory Structure
```
speculative-decoding/
├── SKILL.md                          # Skill documentation
├── README.md                         # This file
├── scripts/
│   ├── install-dependencies.sh       # Install vLLM + deps
│   ├── start-vlm-server.sh          # Start vLLM server
│   └── test-speculative.sh          # Test speculative decoding
├── references/
│   ├── vlm-config.json              # vLLM configuration
│   └── model-pairs.json             # Tested model pairs
└── logs/                            # Server logs (created on startup)
```

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd ~/.openclaw/workspace/skills/speculative-decoding
./scripts/install-dependencies.sh
```

**What it does:**
- Installs vLLM library
- Installs PyTorch, transformers, etc.
- Verifies NVIDIA GPU support (if available)
- Checks Python 3.8+ installed

**Time:** ~5-10 minutes

### 2. Start vLLM Server

**Option A: Docker (Recommended for isolation)**
```bash
./scripts/start-vlm-server.sh --docker --port 8000
```

**Option B: Local installation**
```bash
./scripts/start-vlm-server.sh --port 8000
```

**What happens:**
- Downloads Llama 2 7B (draft) model (~13GB)
- Downloads Llama 2 13B (verifier) model (~26GB)
- Starts speculative decoding server on port 8000
- Logs to `logs/vlm-server.log`

**Time:** ~10-20 minutes first run (model download)

### 3. Test the Server
```bash
./scripts/test-speculative.sh
```

**What it tests:**
- Server is running
- Can process simple requests
- Measures latency
- Reports token count

**Expected output:**
```
✅ Test 1: Simple greeting - PASS (Latency: 450ms, Tokens: 35)
✅ Test 2: Factual question - PASS (Latency: 520ms, Tokens: 40)
...
📊 Test Results: 4/4 passed
```

---

## 📊 Phase 1 Deliverables

| Item | Status | Location | Details |
|------|--------|----------|---------|
| Skill scaffold | ✅ Complete | SKILL.md | Full documentation |
| vLLM config | ✅ Complete | references/vlm-config.json | Ready to customize |
| Model pairs | ✅ Complete | references/model-pairs.json | Llama 2 7B + 13B |
| Startup script | ✅ Complete | scripts/start-vlm-server.sh | Docker + local options |
| Test harness | ✅ Complete | scripts/test-speculative.sh | 4 basic tests |
| Install script | ✅ Complete | scripts/install-dependencies.sh | One-command setup |
| Documentation | ✅ Complete | README.md + SKILL.md | Full guides |

---

## 🎯 Next Steps (Phase 2)

Once Phase 1 testing is complete:

1. **Measure actual speedup**
   - Compare vLLM latency vs. Claude API
   - Expected: 0.4-0.5s vs. 1-2s
   - That's ~2-3x faster ⚡

2. **Evaluate quality**
   - Compare responses (subjective)
   - Look for coherence, accuracy
   - Expected: 85% of Claude quality

3. **Test with real OpenClaw tasks**
   - Route simple tasks through vLLM
   - Route complex tasks through Claude API
   - Measure end-to-end speedup

4. **Document findings**
   - Speedup metrics
   - Quality assessment
   - Decision: Scale to production or stick with API?

---

## 🐛 Troubleshooting

### Problem: "vLLM not installed"
```bash
./scripts/install-dependencies.sh
```

### Problem: "CUDA out of memory"
- Check `nvidia-smi` (free GPU memory?)
- Reduce batch size in `vlm-config.json`
- Use smaller model pair (Llama 7B only)

### Problem: "Models not downloading"
- Check HuggingFace access: `huggingface-cli login`
- Make sure you've accepted Llama terms at https://huggingface.co/meta-llama

### Problem: "Server won't start"
```bash
# Check logs
tail -f logs/vlm-server.log

# Check GPU
nvidia-smi

# Check port
lsof -i :8000
```

---

## 📈 Expected Performance (Phase 1)

| Metric | Target | Notes |
|--------|--------|-------|
| Inference latency | 0.3-0.5s | For simple 50-token responses |
| Quality | 85% of Claude | Good enough for facts/weather/calendar |
| Throughput | 10-20 req/s | Depends on GPU |
| Memory | 40-50GB | Both models loaded |
| Cost | ~$0.50/day | AWS p3 instance |

---

## 🔗 Resources

**vLLM Documentation:**
- Main docs: https://docs.vllm.ai
- Speculative decoding: https://docs.vllm.ai/en/latest/features/spec_decode.html
- GitHub: https://github.com/vllm-project/vllm

**Llama Models:**
- HuggingFace: https://huggingface.co/meta-llama
- License: Commercial + research use allowed

**OpenClaw Skills:**
- Skill docs: https://docs.openclaw.ai/skills
- Examples: ~/.openclaw/workspace/skills/

---

## 📝 Decisions Made in Phase 1

1. **Model Pair:** Llama 2 7B + 13B (good balance of speed + quality)
2. **Framework:** vLLM (mature, well-maintained)
3. **Configuration:** Separate config files (easy to customize)
4. **Testing:** Simple automated test harness
5. **Documentation:** Full setup + troubleshooting guides

---

## 🎬 Ready to Start?

```bash
# 1. Install
cd ~/.openclaw/workspace/skills/speculative-decoding
./scripts/install-dependencies.sh

# 2. Start server
./scripts/start-vlm-server.sh --docker

# 3. Test
./scripts/test-speculative.sh

# 4. Proceed to Phase 2
```

**Estimated time:** 30-45 minutes (including model downloads)

---

## 📧 Contact

Questions or issues? Check:
- SKILL.md (full documentation)
- Troubleshooting section above
- vLLM docs (https://docs.vllm.ai)

---

**Status: Phase 1 ready for launch! 🚀**
