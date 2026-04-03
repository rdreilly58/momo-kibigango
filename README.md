# 🍑 Momotaro — AI Agent Workspace

Personal AI agent workspace powered by [OpenClaw](https://openclaw.ai), running on an M4 Mac Mini. Momotaro is a persistent AI assistant with memory, tools, and multi-channel communication (Telegram, Rocket.Chat, Discord).

## Overview

This workspace is the operational home for Momotaro — an AI agent that manages daily tasks, coding projects, system automation, and communication across multiple platforms. It includes custom skills, automation scripts, memory systems, and several active R&D projects.

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  OpenClaw Gateway                │
│         (Claude Opus 4.0 / Haiku 4.5)           │
├────────────┬──────────────┬─────────────────────┤
│  Telegram  │  Rocket.Chat │  Discord (planned)  │
├────────────┴──────────────┴─────────────────────┤
│              Momotaro Agent Core                 │
│  ┌──────────┬──────────┬──────────┬──────────┐  │
│  │ Memory   │ Skills   │ Scripts  │ Projects │  │
│  │ System   │ (30+)    │ (40+)    │ (6+)     │  │
│  └──────────┴──────────┴──────────┴──────────┘  │
├─────────────────────────────────────────────────┤
│          M4 Mac Mini (24GB RAM)                  │
│    macOS • Homebrew • Docker • Node.js v25       │
└─────────────────────────────────────────────────┘
```

## Key Projects

### [momo-kibidango](https://github.com/rdreilly58/momo-kibidango) — Cascade Proxy
API cost optimization proxy that routes LLM requests through a tiered cascade (Haiku → Sonnet → Opus). Scores response confidence and escalates only when needed.
- **Status:** Running on port 7780, in 3-day trial (April 2–5, 2026)
- **Results:** Threshold tuning complete (10/10 test suite), but surface-level confidence scoring can't detect "wrong but well-written" — core limitation identified

### [momo-akira](https://github.com/rdreilly58/momo-akira) — Token-Level Speculative Decoding
Correct implementation of PyramidSD (arxiv:2510.12966) for 2x faster local LLM inference. Uses nested draft→qualifier→target loop with logit divergence scoring.
- **Status:** v2 built (31 tests, 81% coverage), OOM issues with 3-model loading on 16GB — needs quantization or MLX backend
- **Branch:** `v2-token-level`

### [momo-kiji](https://github.com/rdreilly58/momo-kiji) — Apple Neural Engine Research
ANE-optimized inference engine based on the Orion paper (arxiv:2603.06728).
- **Status:** Research phase, featured on ReillyDesignStudio portfolio

### [ReillyDesignStudio](https://reillydesignstudio.com) — Portfolio Website
Next.js 16 site deployed on Vercel. Includes blog, project showcase, and Stripe integration.
- **Status:** Production, auto-deploys from `main` branch

### Momotaro iOS App
Native iOS app with WebSocket gateway connection to OpenClaw.
- **Status:** Build succeeds (zero errors), ready for TestFlight

### Roblox Game Automation
Automated pipeline: GitHub clone → Roblox Studio launch → 15s capture → error analysis.
- **Status:** Complete, fully automated via `scripts/roblox-full-automation.sh`

## Workspace Structure

```
├── SOUL.md              # Agent personality & behavior rules
├── USER.md              # Human profile (Bob / Robert Reilly)
├── AGENTS.md            # Workspace conventions & guidelines
├── MEMORY.md            # Long-term curated memory
├── MEMORY.CORE.md       # Lightweight startup context
├── HEARTBEAT.md         # Periodic task checklist
├── TOOLS.md             # Local tool configuration & notes
│
├── memory/              # Daily logs (YYYY-MM-DD.md)
├── scripts/             # 40+ automation scripts
├── skills/              # Custom OpenClaw skills
├── leidos/              # Work-related materials
├── docs/                # OpenClaw documentation mirror
│
├── momo-kibidango/      # Cascade proxy project
├── momo-kiji/           # ANE inference project
├── momotaro-ios/        # iOS app source
├── reillydesignstudio/  # Portfolio website
└── OnigashimaDashboard/ # macOS dashboard app
```

## Memory System

Momotaro wakes up fresh each session. Continuity is maintained through files:

- **`MEMORY.CORE.md`** — Lightweight startup context (loaded every session)
- **`MEMORY.md`** — Detailed curated memory (loaded on demand, ~22KB)
- **`memory/YYYY-MM-DD.md`** — Raw daily logs of events, decisions, and work
- **Local embeddings search** — Sentence Transformers (`all-MiniLM-L6-v2`) for semantic memory search, replacing broken OpenAI embeddings

## Automation & Scripts

Key scripts in `scripts/`:

| Script | Purpose |
|--------|---------|
| `start-gateway-with-brave.sh` | Start OpenClaw gateway with Brave Search API |
| `memory_search_local.py` | Local semantic memory search |
| `roblox-full-automation.sh` | GitHub → Roblox Studio → test pipeline |
| `gpu-health-check-full.sh` | GPU offload health monitoring |
| `telegraph_heartbeat.py` | Publish status reports to Telegraph |
| `classify-coding-task.sh` | Smart model selection for coding subagents |
| `api-quota-monitor.sh` | API quota monitoring |
| `auto-update-system.sh` | Automated Homebrew/npm/macOS updates |
| `pdf-from-markdown.sh` | Markdown → PDF conversion |

## Communication Channels

| Channel | Status | Notes |
|---------|--------|-------|
| Telegram | ✅ Active | Primary channel, fully operational |
| Rocket.Chat | ✅ Active | Work channel, custom plugin (fixed April 2) |
| Discord | 🔲 Planned | Setup pending |

## Cost Optimization

Three-tier model routing for subagent coding tasks:

- **Haiku** — Trivial fixes (typos, formatting): 150x cheaper than Opus
- **Opus** — Medium complexity (features, refactoring): baseline
- **GPT-4** — Complex architecture: fallback for hardest problems

Smart classifier (`scripts/classify-coding-task.sh`) analyzes task description and selects optimal model. Expected 64–78% cost reduction vs always using Opus.

---

## Lessons Learned

### 1. Speculative Decoding ≠ Model Routing (April 2026)
**The biggest lesson.** v1 of momo-akira implemented response-level cascade routing (generate full response → score quality → maybe regenerate with bigger model) and called it "speculative decoding." It wasn't. Speculative decoding is a specific token-level algorithm: a draft model proposes K tokens, a verifier checks them in a single parallel forward pass via logit divergence, and accepted tokens skip expensive autoregressive generation. The speedup comes from GPU parallelism (verifying K tokens costs the same as generating 1), not from choosing cheaper models. API models (Claude, GPT) **cannot** do this — they don't expose logits or support parallel verification. This requires local models with shared tokenizers. v2 implements the actual algorithm correctly.

### 2. Surface-Level Confidence Scoring Is Insufficient (April 2026)
The cascade proxy (momo-kibidango) scores response quality based on length, coherence, and complexity. In a 100-request load test, 100% of requests stayed at Haiku tier because Haiku produces well-structured, confident-sounding responses — even when they're wrong. Detecting "wrong but well-written" requires ground truth or domain-specific validation, not surface-level heuristics. The scorer needs fundamental rethinking.

### 3. Memory Is Only as Good as the Files (March 2026)
"Mental notes" don't survive session restarts. Every decision, lesson, and context that matters must be written to a file. The memory system (MEMORY.md + daily logs + local embeddings search) is the agent's only continuity mechanism. When we lost the OpenAI embeddings API (quota exceeded), we built local search with Sentence Transformers in 15 minutes — because the files themselves were intact. **Text > Brain. 📝**

### 4. Never Infer Dates or Times (March 2026)
Made a serious mistake updating a recurring calendar event by assuming Thursday instead of reading the Friday date from message metadata. This deleted all future instances of the event. **Always read timestamps from metadata. Never calculate or infer.** This is now an enforced rule.

### 5. Config File Rewrites Are Dangerous (April 2026)
A Python script that read `openclaw.json`, modified one field, and wrote it back silently dropped the entire `channels.rocketchat` section — breaking the Rocket.Chat channel completely. JSON5 → JSON conversion lost data. **Rule:** Never do full-file read-modify-write on config files. Use `openclaw config set` for single-field changes, and always backup first.

### 6. LaunchAgents Accumulate and Conflict (April 2026)
Found 6+ standalone Rocket.Chat LaunchAgent services running simultaneously, each intercepting messages differently. Legacy scripts from earlier experiments were still active, causing message duplication and routing failures. **Clean up old LaunchAgents aggressively.** Rename unused plists to `.disabled`, don't just unload them.

### 7. Docker Healthchecks Need Container-Aware Tooling (April 2026)
Rocket.Chat Docker container was perpetually "unhealthy" because the healthcheck used `curl` (not installed in the container) and `localhost` (doesn't resolve inside containers). Fixed by switching to `wget --spider -q http://127.0.0.1:3000/health`. **Always verify that healthcheck tools exist inside the container.**

### 8. Local Models on 16GB Need Quantization (April 2026)
Attempted to load 3 Qwen2.5 models (0.5B + 1.5B + 3B) in float16 for speculative decoding — OOM killed repeatedly. Even the smallest trio at float16 plus PyTorch overhead plus OS takes ~16GB. **Lesson:** On consumer hardware, always plan for int4/int8 quantization or use MLX backend (more memory efficient on Apple Silicon).

### 9. Sudo Access Is a Feature, Not a Risk (March 2026)
Passwordless sudo for whitelisted commands (`/etc/sudoers.d/momotaro`) dramatically improved productivity — system updates, Homebrew installs, service management all happen without interruption. The whitelist approach maintains security (only approved commands) with full audit trail. **Use it freely; that's why it exists.**

### 10. Environment Variables Must Be Set Where the Process Starts (March 2026)
Brave Search API key was in the config file but the Gateway couldn't find it. Root cause: the Gateway reads environment variables at startup, and the launchctl plist didn't pass them through. Created a startup script that explicitly sets `BRAVE_API_KEY` before launching the Gateway. **Config files ≠ environment variables.** Know which one your process expects.

---

## Current Status (April 3, 2026)

### ✅ Operational
- **OpenClaw Gateway** — Running, Claude Opus 4.0 default
- **Telegram channel** — Primary comms, fully functional
- **Rocket.Chat channel** — Work comms via custom plugin, fixed April 2
- **Memory system** — Local embeddings search + daily logs + curated memory
- **ReillyDesignStudio** — Production on Vercel, auto-deploying
- **Roblox automation** — Full pipeline operational
- **Momotaro iOS app** — Builds clean, ready for TestFlight
- **Cost optimization** — Smart model classifier active (Haiku/Opus/GPT-4 tiering)
- **System automation** — Auto-updates, API monitoring, Telegraph reports

### 🔬 In Progress
- **momo-kibidango cascade proxy** — 3-day trial (April 2–5), confidence scorer needs rework
- **momo-akira v2** — Token-level speculative decoding built, needs quantized model loading to fit in 16GB RAM
- **momo-kiji** — ANE inference research, early stage

### ⏳ Pending
- **AWS Mac instance** — Quota request submitted, awaiting approval
- **Discord channel** — Setup not yet started
- **robert@reillydesignstudio.com** — Needs Google Workspace app password for Himalaya
- **Google OAuth** — `rdreilly2010@gmail.com` token expired, needs `gog auth`

### 📊 Infrastructure
- **Hardware:** M4 Mac Mini, 24GB RAM, macOS 25.3.0
- **Runtime:** Node.js v25.9.0, Python 3.x, Docker
- **Models:** Claude Opus 4.0 (primary), Claude Haiku 4.5 (fast/fallback)
- **DNS:** Cloudflare (reillydesignstudio.com, momo-kibidango.org)
- **Hosting:** Vercel (websites), AWS Route 53 (DNS), Docker (Rocket.Chat)

---

## Setup

This workspace is designed for [OpenClaw](https://openclaw.ai). To run your own:

1. Install OpenClaw: `npm install -g openclaw`
2. Initialize workspace: `openclaw init`
3. Configure your `SOUL.md`, `USER.md`, and `AGENTS.md`
4. Connect channels (Telegram, Rocket.Chat, etc.)
5. Start the gateway: `openclaw gateway start`

See [OpenClaw docs](https://docs.openclaw.ai) for full setup guide.

## License

Personal workspace — not intended for redistribution. Individual projects (momo-kibidango, momo-akira, momo-kiji) have their own licenses in their respective repositories.
