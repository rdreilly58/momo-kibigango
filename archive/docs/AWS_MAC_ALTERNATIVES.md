# AWS Mac EC2 Alternatives Analysis

**Decision Date:** Sunday, March 22, 2026, 6:54 AM EDT  
**Current Status:** mac-m4pro quota request PENDING (since March 20, expected approval "within 24 hours")

---

## Quick Summary Table

| Option | Cost/Month | Performance | Setup Time | Best For | Risk |
|--------|-----------|-------------|-----------|----------|------|
| **AWS mac-m4pro** | $7,300-8,700 | ⭐⭐⭐⭐⭐ Excellent | 2-3 hours | Production builds, CI/CD | Waiting for approval |
| **AWS mac-mini M4** | $4,200-5,000 | ⭐⭐⭐⭐ Very good | 1-2 hours | Good balance | Smaller VRAM (24GB) |
| **Local vLLM-MLX** | $0 | ⭐⭐⭐ Good | 2-3 hours | AI inference, local work | Limited to home machine |
| **Google Cloud A2** | $2,500-3,500 | ⭐⭐⭐⭐ GPU-focused | 1 hour | GPU training/inference | Not ARM (x86 NVIDIA) |
| **Lambda Labs GPU** | $0.50/hr | ⭐⭐⭐⭐ Pay-as-you-go | 30 min | Episodic heavy compute | No persistence |
| **Hetzner Cloud (ARM)** | $200-400 | ⭐⭐⭐ Budget ARM | 30 min | Cost-sensitive, Linux | Linux only (no macOS) |
| **Runpod.io (Cloud) ** | $0.40/hr | ⭐⭐⭐⭐ GPU rental | 15 min | ML inference, serverless | Ephemeral, API-driven |

---

## Detailed Analysis

### 1. AWS mac-m4pro.metal ⭐ CURRENT CHOICE

**Cost:** $10-12/hr (~$7,300-8,700/month)

**Specs:**
- 14-core M4 Pro CPU
- 20-core GPU
- 48GB unified memory
- 500GB SSD storage
- macOS environment (native)

**Pros:**
- ✅ Native macOS (Xcode, native tools)
- ✅ Highest performance (M4 Pro > M4 Max for cost)
- ✅ Unified memory (perfect for AI)
- ✅ Full control (not ephemeral)
- ✅ Persistent storage
- ✅ Great for Roblox Studio automation (macOS-only)

**Cons:**
- ❌ Expensive ($7K+/month)
- ⏳ Quota approval pending (as of March 20)
- ⚠️ Overkill for pure AI inference
- ⚠️ Long-term financial commitment

**Use Cases:**
- Production CI/CD (Xcode builds, iOS/macOS)
- Roblox Studio automation (macOS-only)
- Full development environment
- Concurrent multi-user development

**Status:** PENDING approval (expected this week)

---

### 2. AWS mac-mini.metal (M4) ⭐ LOWER-COST MAC

**Cost:** $4-5/hr (~$4,200-5,000/month) — ~45% cheaper

**Specs:**
- 10-core M4 CPU (vs 14-core M4 Pro)
- 10-core GPU (vs 20-core M4 Pro)
- 24GB unified memory (vs 48GB)
- 256GB SSD storage
- macOS environment

**Pros:**
- ✅ 45% cheaper than m4pro
- ✅ Still runs macOS (Xcode, iOS builds)
- ✅ 24GB memory adequate for most workflows
- ✅ M4 still excellent performance
- ✅ Likely immediate quota availability

**Cons:**
- ⚠️ 50% less GPU performance
- ⚠️ 24GB memory (tight for large models + datasets)
- ❌ Still expensive for AI-only workloads

**Use Cases:**
- Cost-optimized CI/CD
- iOS app builds (less parallel)
- Light AI inference
- Development environment (not production)

**Recommendation:** If AWS approval is delayed, this is best alternative for macOS needs

**Status:** Likely available immediately (can request in parallel)

---

### 3. Local vLLM-MLX Setup 🏠 ALREADY HAVE THIS

**Cost:** $0/month (uses your M4 Max Mac mini)

**Specs:**
- Your M4 Max (8-core CPU, 10-core GPU, 32GB)
- vLLM-MLX (optimized for Apple Silicon)
- Qwen 3 14B model (~10GB VRAM)

**Pros:**
- ✅ $0 cost (already paid for)
- ✅ Fast local inference (100ms latencies)
- ✅ No latency variance
- ✅ Full privacy (data never leaves)
- ✅ Can run in background without affecting work

**Cons:**
- ⚠️ Slower than A100 GPUs (but adequate)
- ⚠️ Limited to 14B parameter models
- ❌ Can't do large-scale training
- ❌ Shared resources with daily work

**Performance:**
- Inference: 15-18 tok/sec (good for most tasks)
- Latency: <1s for simple queries
- Throughput: ~1 query per second

**Use Cases:**
- Local AI assistance (already doing this)
- Development/testing
- Quick inference (no API latency)
- Cost-free baseline

**Status:** READY NOW (Phase 1 PoC complete, Phase 2 pending)

---

### 4. Google Cloud A2 (GPU) ⭐ GPU-FOCUSED ALTERNATIVE

**Cost:** $2.5-3.5/hr (~$2,500-3,500/month)

**Specs:**
- 12 vCPU (x86 Intel)
- 1x A100 GPU (40GB VRAM)
- 300GB memory
- Linux only

**Pros:**
- ✅ A100 GPU (industry standard for AI)
- ✅ 40GB GPU VRAM (massive)
- ✅ Lower cost than AWS Mac
- ✅ Proven infrastructure
- ✅ Pay-as-you-go (can pause)

**Cons:**
- ❌ Linux-only (no macOS)
- ❌ x86 architecture (not ARM)
- ❌ GPU-centric (CPU slower than M4)
- ❌ Not ideal for macOS app building

**Use Cases:**
- Large model fine-tuning
- GPU-accelerated ML training
- Batch inference jobs
- Research workloads

**Recommendation:** Only if you need GPU specifically (you don't yet)

**Status:** Available immediately, but requires Linux/Docker

---

### 5. Lambda Labs GPU Cloud ⚡ PAY-AS-YOU-GO GPU

**Cost:** $0.50/hr (~$360/month if always on, but pay only for usage)

**Specs:**
- A100 or A6000 GPUs (options available)
- Customizable CPU/RAM
- Linux environment
- Ephemeral (data lost on shutdown)

**Pros:**
- ✅ Extremely flexible (hour-by-hour billing)
- ✅ A100/A6000 GPU available
- ✅ Great for episodic heavy compute
- ✅ No long-term commitment
- ✅ Quick provisioning (5-10 min)

**Cons:**
- ❌ Ephemeral (data lost)
- ❌ Linux only
- ❌ No persistent storage
- ⚠️ Requires data staging every run

**Use Cases:**
- One-off training jobs
- Batch inference runs
- Temporary spike computing
- Research experiments

**Recommendation:** Perfect for episodic needs, not continuous

**Status:** Available immediately, no approval needed

---

### 6. Hetzner Cloud ARM Server 💰 BUDGET ARM

**Cost:** $200-400/month (~$0.01-0.015/hr)

**Specs:**
- ARM64 CPU (custom/AMPERE)
- 32-64GB RAM
- NVMe SSD
- Linux only (no macOS)

**Pros:**
- ✅ Extremely cheap ($200-400/month)
- ✅ ARM architecture (like M4 Mac)
- ✅ Persistent (not ephemeral)
- ✅ Good for background services

**Cons:**
- ❌ Linux only (not macOS)
- ❌ Slow compared to M4
- ⚠️ Unpredictable performance
- ❌ Customer service in German

**Use Cases:**
- Long-running Linux services
- Cron jobs & background tasks
- CI/CD runners
- Cost-sensitive deployments

**Recommendation:** Only if you need ARM + persistent + Linux

**Status:** Available immediately

---

### 7. RunPod.io (Serverless GPU) 🚀 MODERN ALTERNATIVE

**Cost:** $0.40/hr variable (~$288/month if always on)

**Specs:**
- A100/A6000 GPUs
- Customizable CPU/RAM
- Serverless/container model
- Ephemeral by default (persistent add-on)

**Pros:**
- ✅ Serverless model (pay only for use)
- ✅ Modern GPU infrastructure
- ✅ API-driven (easy automation)
- ✅ Container support
- ✅ Cheaper than Lambda Labs

**Cons:**
- ❌ Ephemeral by default
- ❌ API-first (not traditional SSH)
- ⚠️ Newer platform (less battle-tested)
- ⚠️ Cold start latencies

**Use Cases:**
- API-driven ML inference
- Automated pipelines
- Batch jobs
- Containerized workloads

**Status:** Available, growing adoption

---

## Decision Matrix

**What are your priorities?**

### I want native macOS builds (iOS, Xcode):
→ **AWS mac-m4pro** (wait for approval) or **AWS mac-mini** (immediate, cheaper)

### I want best cost/performance for AI:
→ **Local vLLM-MLX** ($0) + **Lambda Labs** for heavy spikes ($0.50/hr as-needed)

### I want GPU-accelerated ML:
→ **Google Cloud A2** ($2.5-3.5/hr always-on) or **Lambda Labs** (episodic)

### I want cheapest long-term compute:
→ **Hetzner Cloud** ($200-400/month) — Linux, ARM-based

### I want most flexibility:
→ **RunPod.io** serverless ($0.40/hr, pay-per-use)

---

## My Recommendation (March 22, 2026)

**Tiered approach:**

**Tier 1 (Now):** Keep local vLLM-MLX for daily work ($0/month)
- Phase 2 PoC completion
- Daily AI inference
- Development

**Tier 2 (If approved this week):** Spin up AWS mac-m4pro ($7.3K/month)
- CI/CD automation
- Roblox Studio automation
- Production builds
- Concurrent development

**Tier 3 (If Apple Silicon heavy computing needed):** Add Lambda Labs as needed ($0.50/hr)
- Research spikes
- Large batch jobs
- One-off training

**Tier 4 (NOT recommended right now):** Skip Google Cloud A2 (GPU-focused, you don't need it yet)

---

## Next Steps

1. **Today (by EOD):** Check AWS approval status for mac-m4pro
2. **If approved:** Provision immediately (2-3 hour setup)
3. **If delayed past Tuesday:** Request mac-mini.metal as interim (45% cheaper)
4. **Meanwhile:** Finish Phase 2 vLLM-MLX implementation (local is free)
5. **For future spikes:** Document Lambda Labs workflow for episodic needs

---

## Cost Projection (12 months)

| Scenario | Monthly | Annual |
|----------|---------|--------|
| **vLLM-MLX only** | $0 | $0 |
| **vLLM-MLX + Lambda spikes** | $50 | $600 |
| **mac-mini.metal** | $4,500 | $54,000 |
| **mac-m4pro** | $7,500 | $90,000 |
| **mac-m4pro + Lambda spikes** | $7,600 | $91,200 |

---

**Status:** Awaiting AWS approval. Will have a decision path by Monday. 🍑
