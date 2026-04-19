# OpenClaw Configuration & Capability Improvements
**Generated:** April 2, 2026 — Based on our usage patterns, problems encountered, and community best practices

---

## 🔴 HIGH PRIORITY (Fix Now)

### 1. Gateway Log Rotation
**Problem:** Gateway logs grew to 3.2 GB before we manually truncated them today.
**Impact:** Disk space, slow grep, can't read logs when debugging.
**Fix:** Set up logrotate:
```bash
sudo cat > /etc/logrotate.d/openclaw << 'EOF'
/Users/rreilly/.openclaw/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    size 100M
    copytruncate
}
EOF
```
**Source:** [linux-server-admin.com/openclaw/monitoring-logging](https://wiki.linux-server-admin.com/web-apps/genai/openclaw/howto/monitoring-logging)

---

### 2. Security: Disable `allowInsecureAuth`
**Problem:** Our config has `gateway.controlUi.allowInsecureAuth: true` — the gateway warns about this on every restart.
**Impact:** Allows token-only auth over HTTP without device identity verification. Known security issue ([GitHub #20683](https://github.com/openclaw/openclaw/issues/20683)).
**Fix:**
```bash
openclaw config set gateway.controlUi.allowInsecureAuth false
```
Then run `openclaw security audit` to check for other issues.
**Source:** [docs.openclaw.ai/gateway/security](https://docs.openclaw.ai/gateway/security)

---

### 3. Brave API Key — Proper Secrets Management
**Problem:** Brave API key was in keychain but gateway couldn't find it. We fixed it by putting it in `~/.openclaw/.env`, but this is a band-aid.
**Impact:** Web search breaks silently after updates/doctor runs.
**Fix:** Use OpenClaw's native secrets configuration:
```bash
openclaw configure --section web
```
Or use env var substitution in config:
```json5
{
  tools: {
    web: {
      search: {
        brave: { apiKey: "${BRAVE_API_KEY}" }
      }
    }
  }
}
```
**Source:** [docs.openclaw.ai/help/environment](https://docs.openclaw.ai/help/environment)

---

### 4. Workspace Bootstrap File Sizes
**Problem:** SOUL.md (20KB), TOOLS.md (41KB), MEMORY.md (23KB) are all being truncated during bootstrap injection. Each session starts with incomplete context.
**Impact:** Lost context every session, repeated mistakes, slower startup.
**Fix options:**
- **A) Trim files:** TOOLS.md has outdated sections (Discord setup, Telegraph, old printer docs). Archive old content to `docs/` and keep TOOLS.md under 15KB.
- **B) Increase limits:** `openclaw config set agents.defaults.bootstrapMaxChars 25000`
- **C) Both** (recommended): trim + modest limit increase.
**Source:** Bootstrap truncation warnings in every session.

---

## 🟡 MEDIUM PRIORITY (This Week)

### 5. Memory Search — Fix Built-in Tool
**Problem:** Built-in `memory_search` tool uses OpenAI embeddings (quota exceeded). We use a local Python workaround (`mem-search` alias) but it's fragile.
**Impact:** Memory search is unreliable, adds latency, shell alias breaks in some contexts.
**Fix:** Configure OpenClaw's native local embedding provider:
```json5
{
  agents: {
    defaults: {
      memorySearch: {
        enabled: true,
        provider: "local",
        local: {
          modelPath: "sentence-transformers/all-MiniLM-L6-v2"
        }
      }
    }
  }
}
```
**Source:** [docs.openclaw.ai/reference/memory-config](https://docs.openclaw.ai/reference/memory-config), [Reddit PSA](https://www.reddit.com/r/openclaw/comments/1r5mgmu/)

---

### 6. Prompt Caching Configuration
**Problem:** Large bootstrap files + full context = high token costs on every turn.
**Impact:** Unnecessary API spend, especially with Opus.
**Fix:** Enable cache-TTL pruning:
```json5
{
  agents: {
    defaults: {
      contextPruning: {
        mode: "cache-ttl",
        ttl: "5m"
      }
    }
  }
}
```
We already have this configured, but should verify it's working. Check with `openclaw status` for cache hit rates.
**Source:** [docs.openclaw.ai/reference/token-use](https://docs.openclaw.ai/reference/token-use), [Apiyi cost optimization guide](https://help.apiyi.com/en/openclaw-token-cost-optimization-guide-en.html)

---

### 7. Model Fallbacks
**Problem:** When Claude hits rate limits (HTTP 429), there's no automatic fallback.
**Impact:** Dead sessions during rate limiting (saw this tonight multiple times).
**Fix:**
```json5
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["anthropic/claude-sonnet-4-6", "anthropic/claude-haiku-4-5"]
      }
    }
  }
}
```
**Source:** [docs.openclaw.ai/concepts/model-failover](https://docs.openclaw.ai/concepts/model-failover)

---

### 8. Exec Approval — Telegram Inline Buttons
**Problem:** When exec approval was active, it was text-only `/approve <id>` commands — easy to miss, hard to use.
**Impact:** Debugging was nearly impossible (tonight's 2-hour ordeal).
**Current fix:** We set `tools.exec.security: full` + `ask: off` (YOLO mode).
**Better approach for the future:** Enable Telegram exec approvals with inline buttons:
```json5
{
  execApprovals: {
    telegram: {
      enabled: true,
      target: "dm"  // or "chat" for in-channel approval buttons
    }
  }
}
```
Note: GitHub [#3934](https://github.com/openclaw/openclaw/issues/3934) tracks inline button support. May already be implemented in v2026.4.1.
**Source:** [docs.openclaw.ai/tools/exec-approvals](https://docs.openclaw.ai/tools/exec-approvals)

---

## 🟢 LOW PRIORITY (Nice to Have)

### 9. ClawHub Skills to Evaluate
**Top skills by downloads** (from ClawHub registry, 13K+ skills):

| Skill | Downloads | Purpose | We Have? |
|-------|-----------|---------|----------|
| Capability Evolver | 35K | Auto-evolve agent capabilities | ❌ |
| ByteRover | 16K | Advanced web browsing | ❌ (we have agent-browser) |
| Self-Improving Agent | 15K | Self-optimization patterns | ❌ |
| ATXP | 14K | Automation toolkit | ❌ |
| Gog | 14K | Google Workspace CLI | ✅ |
| Agent Browser | 11K | Headless browser automation | ✅ |
| Summarize | 10K | URL/podcast summarization | ✅ |
| GitHub | 10K | GitHub operations | ✅ |

**Recommend evaluating:** Capability Evolver, ByteRover
**Source:** [ClawHub Top Skills 2026](https://clawoneclick.com/en/blog/clawhub-top-skills-2026)

---

### 10. Regular Maintenance Schedule
**Problem:** No automated maintenance — logs grow, tokens expire, configs drift.
**Recommended cadence:**

| Frequency | Task | How |
|-----------|------|-----|
| Daily | Log rotation | logrotate (see #1) |
| Weekly | `openclaw doctor` | Cron job |
| Weekly | `openclaw security audit` | Cron job |
| Monthly | API key rotation check | Manual or cron |
| Monthly | `openclaw update` | Manual with review |
| Monthly | Memory cleanup (archive old daily files) | During heartbeat |

**Source:** [OpenClaw Roadmap — Regular Maintenance](https://openclawroadmap.com/security-monitoring.php)

---

### 11. Environment Variable Best Practices
**Problem:** API keys scattered across keychain, .env, config.json, TOOLS.secrets.local.
**Fix:** Consolidate to `~/.openclaw/.env` (per OpenClaw docs, highest priority after process env):
```bash
# ~/.openclaw/.env
BRAVE_API_KEY=xxx
HF_API_TOKEN=xxx
CLOUDFLARE_TOKEN=xxx
```
Remove duplicates from other locations. Config references via `${VAR}` syntax.
**Source:** [docs.openclaw.ai/help/environment](https://docs.openclaw.ai/help/environment)

---

### 12. OpenClaw Version — Upgrade to 2026.4.1
**Current:** Was 2026.3.28, now appears to be 2026.4.1 (after `openclaw doctor`).
**Action:** Verify with `openclaw --version` and review changelog for breaking changes.
**Notable GitHub issues in latest:**
- [#51673](https://github.com/openclaw/openclaw/issues/51673): Fix totalTokens on zero usage reports (44 comments)
- [#52951](https://github.com/openclaw/openclaw/issues/52951): `tools.fs.roots` — per-agent filesystem roots (35 comments)
- [#39207](https://github.com/openclaw/openclaw/issues/39207): `before_response_emit` hook for output policies (47 comments)

---

## Summary — Quick Wins

| # | Action | Time | Impact |
|---|--------|------|--------|
| 1 | Set up logrotate | 5 min | Prevents 3 GB log bombs |
| 2 | Disable allowInsecureAuth | 1 min | Security fix |
| 3 | Consolidate API keys to .env | 10 min | No more key hunt |
| 4 | Trim TOOLS.md | 30 min | Better context per session |
| 5 | Configure native memory search | 15 min | Fix built-in memory_search |
| 6 | Add model fallbacks | 5 min | No more dead sessions on 429 |
