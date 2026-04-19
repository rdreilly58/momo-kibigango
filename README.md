# 🍑 Momotaro — AI Agent Workspace

Personal AI agent workspace powered by [OpenClaw](https://openclaw.ai), running on an M4 Mac Mini (24GB RAM, macOS 25.x). Momotaro is a persistent autonomous assistant with memory, tools, and multi-channel communication (Telegram, Rocket.Chat, Discord).

## Overview

This workspace is the operational home for Momotaro — an AI agent that manages daily tasks, coding projects, system automation, and communication across multiple platforms. It includes custom skills, automation scripts, memory systems, and several active R&D projects.

## Architecture

```
┌───────────────────────────────────────────────────────────┐
│                   COMMUNICATION LAYER                      │
│   Telegram (primary) │ Rocket.Chat (work) │ Discord (soon) │
└─────────────────────────┬─────────────────────────────────┘
                          │
┌─────────────────────────▼─────────────────────────────────┐
│              OPENCLAW GATEWAY (:18789, loopback)           │
│    Session Mgmt  │  Model Routing  │  Skill Dispatch       │
└──────┬───────────┴─────────────────┴────────┬─────────────┘
       │                                      │
┌──────▼──────────────┐           ┌───────────▼────────────┐
│   TASK CLASSIFIER   │           │    MEMORY SYSTEM       │
│  Simple → Haiku     │           │  Total Recall (5-layer) │
│  Medium → Sonnet    │           │  observations.md       │
│  Complex → Opus     │           │  MEMORY.md (curated)   │
└──────┬──────────────┘           └────────────────────────┘
       │
┌──────▼───────────────────────────────────────────────────┐
│             SKILLS (30+) & SCRIPTS (40+)                  │
│  roblox-loader  │  ga4-analytics  │  daily-briefing       │
│  s3  │  aws-deploy  │  gmail-send  │  slack  │  ios-dev   │
└──────────────────────────────────────────────────────────┘
```

## Theory of Operations

### Task Routing (3 Tiers)

Every incoming message is classified before a model is invoked, keeping costs low and speed high.

| Tier | Model | Trigger | Context Loaded |
|------|-------|---------|----------------|
| Simple | `claude-haiku-4-5` | ≤50 words, status/weather queries | SOUL.md, USER.md |
| Medium | `claude-sonnet-4-6` | Conversation, writing, analysis | + MEMORY.md |
| Complex | `claude-opus-4-6` | Code, architecture, multi-step | + TOOLS.md, project files |

Classification is keyword-driven (`config/classifier-config.json`). Complex keywords: `build`, `refactor`, `implement`, `debug`, `architecture`. Simple keywords: `weather`, `status`, `check`, `today`. Default tier is Medium.

### Memory System

Memory is file-based and manually curated. No autonomous LLM compression — high signal, low noise.

| File | Purpose | When Loaded |
|------|---------|-------------|
| `SESSION_CONTEXT.md` | Single-paragraph session snapshot | First, every session (fast path) |
| `SOUL.md` | Personality, rules, behavior | Always (full path only) |
| `USER.md` | Who Bob is, preferences | Always (full path only) |
| `MEMORY.md` | Curated long-term facts | Medium/complex tasks |
| `TOOLS.md` | APIs, credentials guide, compute | Complex tasks only |
| `memory/YYYY-MM-DD.md` | Raw daily event logs | Today's file on demand |

### Session Context Fast Path

On session start, `SESSION_CONTEXT.md` is checked first. If recent, it bypasses full memory load — saving time and tokens. Auto-flush runs nightly at 00:50 before the 01:00 context reset.

### Memory Maintenance

During heartbeats (every few days): read recent `memory/YYYY-MM-DD.md` files, distill significant events into `MEMORY.md`, remove outdated entries. Daily files are raw notes; `MEMORY.md` is curated wisdom.

### Roblox Automation Pipeline

```
GitHub repo URL
    → git clone to ~/.games/
    → roblox-create-blank-place.sh   (creates game.rbxl XML)
    → plugin injection (MomotaroAutoTest.lua → ~/Library/...Plugins)
    → RobloxStudio launched with game file
    → 15s wait for initialization
    → log capture from ~/Library/Logs/Roblox/
    → error/warning parse (FLog/DFLog infrastructure noise filtered)
    → test result report (.test_results.txt)
```

## Testing

### Run the Workspace Test Suite

```bash
cd ~/.openclaw/workspace
bash Tests/workspace-test-suite.sh
```

Results are saved to `Tests/workspace-test-results.log`. The suite covers 15 sections across 77 tests:

| Section | What It Checks |
|---------|---------------|
| 1. Core Files | SOUL, USER, AGENTS, MEMORY, TOOLS, TASK_ROUTING, HEARTBEAT |
| 2. Directory Structure | scripts/, config/, skills/, memory/, logs/, Tests/ |
| 3. Config Validation | JSON validity, required keys, all 3 model IDs present |
| 4. OpenClaw Config | openclaw.json valid, models configured, no raw keys |
| 5. Script Syntax | bash -n / py_compile on all key scripts |
| 6. Script Executability | chmod +x on all runnable scripts |
| 7. Memory Integrity | observations.md non-empty, daily logs present, search script valid |
| 8. SOUL.md Content | Routing, memory, alerting, date rules, group chat behavior |
| 9. Task Routing | Haiku/Sonnet/Opus tiers and token budget documented |
| 10. Security | File permissions (700/600), no secrets in logs |
| 11. Skills | Required skills present, total skill count ≥ 4 |
| 12. Roblox Prerequisites | Studio installed, scripts present, Plugins dir exists |
| 13. Gateway Health | openclaw gateway running on port 18789 |
| 14. Python Dependencies | python3 available, json/pathlib/requests importable |
| 15. Git Health | Is a repo, no sensitive files tracked, git email configured |

### Other Test Suites

| Suite | Purpose |
|-------|---------|
| `Tests/tier-integration-test-suite.sh` | Verify classify-coding-task.sh routes correctly (Haiku/Opus/GPT-4) |
| `Tests/model-routing-test-suite.sh` | OpenRouter config, credentials, gateway, cron, security |
| `scripts/test/test_total_recall_file_indexing.sh` | Total Recall file indexing behavior |

### Known Test Findings (2026-04-19)

- `config/briefing.env`, `config/ga4.env`, `memory/api-keys-and-secrets.md` are tracked by git — these should be added to `.gitignore` and removed from history with `git filter-repo`

---

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

## Current Status (April 19, 2026)

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
