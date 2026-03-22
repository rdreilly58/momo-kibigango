# AWS Mac EC2 Decision Tree

**Current Status:** mac-m4pro quota request PENDING (March 20, expected approval within 24 hours)

**Decision Point:** Sunday, March 22, 2026, 6:54 AM EDT

---

## Decision Flowchart

```
┌─────────────────────────────────────────┐
│ AWS Mac Quota Approved?                 │
│ (Check by Mon 6/24)                     │
└─────────────────────────────────────────┘
         │
    ┌────┴────┐
    │         │
   YES       NO
    │         │
    │         └──────────────────────────────────┐
    │                                            │
    ▼                                            ▼
┌────────────────┐                    ┌──────────────────────┐
│ Provision      │                    │ Request mac-mini     │
│ mac-m4pro      │                    │ As interim option    │
│ (2-3h setup)   │                    │ (45% cheaper)        │
└────────────────┘                    └──────────────────────┘
    │                                            │
    ▼                                            ▼
┌────────────────────────────────────┐  ┌───────────────────┐
│ Use Cases:                         │  │ Use Cases:        │
│ • Roblox automation (macOS-only)   │  │ • Light CI/CD     │
│ • iOS/macOS builds                 │  │ • Development     │
│ • Production CI/CD                 │  │ • Testing         │
│ • Persistent storage               │  │ • Budget-focused  │
│ Cost: $7.3K-8.7K/mo               │  │ Cost: $4.2K/mo    │
└────────────────────────────────────┘  └───────────────────┘
    │                                            │
    │         ┌─────────────────────────────────┘
    │         │
    ▼         ▼
┌──────────────────────────────┐
│ For All Paths:               │
│ • Keep vLLM-MLX local ($0)   │
│ • Phase 2 PoC completion     │
│ • Add Lambda Labs for spikes │
│   ($0.50/hr as-needed)       │
└──────────────────────────────┘
```

---

## Decision Questions

### Q1: Do you need native macOS for builds?
**Answer:** Need iOS/Roblox/Xcode builds?
- **YES** → Must use AWS Mac (m4pro or mac-mini)
- **NO** → Skip to Q2

### Q2: Do you need GPU-accelerated ML training?
**Answer:** Large model training, fine-tuning?
- **YES** → Google Cloud A2 or Lambda Labs
- **NO** → Skip to Q3

### Q3: What's your tolerance for cost?
**Answer:** Monthly budget available?
- **$7K+** → **AWS mac-m4pro** (wait for approval)
- **$4-5K** → **AWS mac-mini** (immediate, 45% cheaper)
- **$500** → **vLLM-MLX locally** (free, adequate performance)
- **$0-100** → **Hetzner Cloud** (Linux only, budget)

### Q4: What's your time sensitivity?
**Answer:** How long can you wait?
- **Need now** → **Lambda Labs** (episodic spikes) + **Local vLLM-MLX** (daily work)
- **Can wait 3-5 days** → **AWS mac-m4pro** (wait for approval)
- **Flexible** → **All options available**

---

## Recommended Paths by Use Case

### Path A: Production-Grade CI/CD + Roblox Automation
```
aws mac-m4pro (PENDING approval)
├─ Roblox Studio automation (macOS-only)
├─ iOS app builds (Xcode)
├─ Persistent CI/CD infrastructure
└─ Cost: $7.3K-8.7K/month

Timeline:
├─ If approved this week → Start setup Monday
├─ If delayed → Request mac-mini as interim
└─ Expected: Live by end of week
```

### Path B: Cost-Optimized Development + AI
```
AWS mac-mini (immediate) + vLLM-MLX local (free)
├─ mac-mini: Light CI/CD, builds ($4.2K/month)
├─ Local vLLM: AI inference, development ($0)
├─ Lambda Labs: Heavy spikes as-needed ($0.50/hr)
└─ Cost: $4.2K-4.3K/month

Timeline:
├─ mac-mini → Request now, 1-2h setup
├─ Local vLLM → Phase 2 PoC (this week)
└─ Expected: Live by Tuesday
```

### Path C: Pure AI + Episodic Compute (Lowest Cost)
```
Local vLLM-MLX (free) + Lambda Labs (as-needed)
├─ vLLM: Daily AI inference locally ($0)
├─ Lambda Labs: Heavy spikes ($0.50/hr)
└─ Cost: $0-200/month (very variable)

Timeline:
├─ vLLM → Phase 2 PoC (this week)
├─ Lambda Labs → Setup account now
└─ Expected: Live immediately
```

### Path D: Maximum Flexibility (GPU + macOS)
```
AWS mac-m4pro (production) + Google Cloud A2 (GPU training)
├─ mac-m4pro: macOS, CI/CD, builds ($7.3K/month)
├─ A2: GPU training, large models ($2.5K/month)
├─ vLLM-MLX: Local development ($0)
└─ Cost: $9.8K+/month

Timeline:
├─ mac-m4pro → PENDING approval
├─ A2 → Available immediately
└─ Expected: All live by end of week
```

---

## Approval Status Check

**Current quota request:**
- **Request ID:** f385e0e9ebe248b1bbbc70b36755d34bU68btWJY
- **Type:** mac-m4pro.metal (1 host)
- **Status:** PENDING (since March 20)
- **Expected:** "Within 24 hours" (so by March 21, but let's assume by end of day Monday 3/24)

**Check status:**
```bash
# AWS CLI (if configured)
aws service-quotas get-service-quota \
  --service-code ec2 \
  --quota-code L-6919FC30 \
  --region us-east-1

# Or check AWS console
# → Service Quotas → EC2 → Search "mac-m4pro"
```

**If approved:** Provision within 2-3 hours
**If delayed:** Request mac-mini.metal (usually approved immediately)

---

## Decision Recommendation (Bob's Call)

**What I recommend (if you want my opinion):**

**Short term (this week):**
1. Complete Phase 2 vLLM-MLX locally (free, good baseline)
2. Monitor AWS quota approval (should come by Monday)
3. If approved → Provision mac-m4pro immediately
4. If delayed past Tuesday → Request mac-mini as interim

**Long term (next month):**
- Keep vLLM-MLX local for daily work ($0)
- Use AWS Mac for CI/CD + Roblox (if approved)
- Add Lambda Labs only for research spikes ($0.50/hr episodic)

**Cost optimization:**
- vLLM-MLX: Free, adequate for inference
- mac-mini: $4.2K/month if you need macOS
- mac-m4pro: $7.3K/month if you need production + Roblox automation
- Don't buy Google A2 yet (no GPU workloads yet)

---

## What You Decide

**I've created three documents for you:**

1. **AWS_MAC_ALTERNATIVES.md** (this workspace)
   - 7 options analyzed
   - Cost/performance comparison
   - Use cases for each
   - Annual cost projection

2. **AWS_MAC_DECISION_TREE.md** (this file)
   - Flowchart for your decision
   - Q&A to guide choice
   - Recommended paths by use case

3. **Your choice:**
   - **Approval status:** Check by Monday (expect answer)
   - **If approved:** I'll provision m4pro (2-3h setup)
   - **If delayed:** Which alternative appeals most?

**Ready to execute whichever path you choose.** 🍑
