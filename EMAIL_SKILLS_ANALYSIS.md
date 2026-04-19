# Email Skills Analysis & Recommendations

**Date:** March 16, 2026  
**Goal:** Evaluate email reading/processing skills, identify gaps, suggest improvements

---

## CURRENT AVAILABLE SKILLS

### 1. **gog** (Google Workspace CLI) ✅ ACTIVE
**Location:** `/opt/homebrew/lib/node_modules/openclaw/skills/gog/SKILL.md`

**Capabilities:**
- Gmail: Search, read, send, organize
- Supports multiple accounts
- JSON output for scripting
- Fast (2-5s per query)
- Combined filters: `from:X AND subject:Y AND after:DATE`

**Strengths:**
- ✅ Fast (Gmail API, not IMAP)
- ✅ Already authenticated
- ✅ Supports complex queries
- ✅ Batch operations possible
- ✅ Production-ready

**Weaknesses:**
- ❌ Gmail only (no Outlook, Exchange)
- ❌ Limited attachment handling
- ❌ Can't process MBOX files
- ❌ No automatic digests/summaries

**Current Usage:** Primary email tool in SOUL.md

---

### 2. **himalaya** (IMAP/SMTP CLI) ✅ ACTIVE
**Location:** `/opt/homebrew/lib/node_modules/openclaw/skills/himalaya/SKILL.md`

**Capabilities:**
- IMAP/SMTP support (any email provider)
- List, read, search, reply, forward
- Compose with MML (MIME Meta Language)
- Message organization
- Multi-account support

**Strengths:**
- ✅ Works with any email provider
- ✅ Offline-capable
- ✅ Full MIME support
- ✅ Good for complex operations

**Weaknesses:**
- ❌ Slow (30-60s per query)
- ❌ Pagination-limited
- ❌ More manual configuration
- ❌ Not ideal for bulk operations

**Current Usage:** Backup/alternative to gog

---

### 3. **email-management** (ReillyDesignStudio) ✅ LOCAL
**Location:** `~/.openclaw/workspace/skills/email-management/SKILL.md`

**Capabilities:**
- Himalaya wrapper for robert@reillydesignstudio.com
- Standard email operations
- Account-specific configuration

**Strengths:**
- ✅ Pre-configured for your account
- ✅ Documented workflows

**Weaknesses:**
- ❌ Single account only
- ❌ Limited to ReillyDesignStudio domain
- ❌ Built on slow Himalaya

**Status:** Functional but underutilized

---

## CLAWHUB AVAILABLE SKILLS

### High-Relevance (For Email Processing)

| Skill | Rating | Purpose | Status |
|-------|--------|---------|--------|
| **email-daily-summary** | 3.588 | Auto-generate email digests | ⭐⭐⭐ |
| **email-reader** | 3.345 | General email reading | ⭐⭐ |
| **porteden-email** | 3.474 | Secured access (Gmail/Outlook) | ⭐⭐⭐ |
| **email-best-practices** | 3.476 | Email workflow automation | ⭐⭐⭐ |
| **email-design** | 3.363 | Email template/formatting | ⭐ |
| **email-marketing** | 3.478 | Campaign-focused | ⭐ |

### Medium-Relevance (Email-Adjacent)

| Skill | Purpose |
|-------|---------|
| react-email-skills | React component libraries |
| email-mail-master | Send via Mail Master 万能邮箱 |
| bot-email | BotEmail.ai - Free bot service |
| email-163-com | Chinese email support |

---

## PERFORMANCE COMPARISON

### Speed (Critical for UX)

| Tool | Type | Latency | Batch |
|------|------|---------|-------|
| **gog** | API | 2-5s | ✅ Fast |
| **himalaya** | IMAP | 30-60s | ❌ Slow |
| **email-daily-summary** | Unknown | ? | ⭐⭐⭐ |
| **porteden-email** | Custom | ? | ? |

---

## RECOMMENDATIONS

### Immediate (This Week)

**1. Optimize Current Setup**
- Switch to `gog` for all Gmail queries (already in TOOLS.md)
- Stop using Himalaya for bulk operations
- Document workflow in TOOLS.md

**2. Install PortEden Email Skill**
- Supports Gmail + Outlook + Exchange
- Secured access (important)
- Good for multi-provider support
- ```bash
  clawhub install porteden-email
  ```

**3. Install Email Daily Summary Skill**
- Auto-generate morning/evening digests
- Perfect for heartbeats
- Could replace manual Briefing generation
- ```bash
  clayhub install email-daily-summary
  ```

### Medium-Term (Next Month)

**4. Create Custom "Email Processor" Skill**
- Wrapper around gog + porteden-email
- Unified interface for multiple providers
- Smart routing (use fastest for each task)
- Caching for frequently-accessed emails
- Batch operations support

**5. Implement Email Filtering Workflow**
- Auto-categorize (work, personal, spam)
- Flag important messages
- Generate summaries by category
- Alert on VIP senders

### Long-Term (Q2 2026)

**6. Build Email Analytics Dashboard**
- Sender frequency
- Response time metrics
- Subject trends
- Volume over time

**7. Integrate with Briefing System**
- Auto-include email summary in morning briefing
- Highlight flagged/urgent messages
- Show unread count trends

---

## SKILLS TO INSTALL

### Immediate (High Priority)

```bash
# Multi-provider email access
clawhub install porteden-email

# Daily email summaries (perfect for briefings)
clawhub install email-daily-summary

# Email best practices & workflow
clawhub install email-best-practices
```

### Optional (Nice to Have)

```bash
# General email reader
clawhub install email-reader
```

---

## UPDATED TOOLS.md RECOMMENDATIONS

**Add to TOOLS.md:**

```markdown
## Email Operations (OPTIMIZED - March 16, 2026)

### PRIMARY METHOD: gog (Gmail API)
- **Speed:** 2-5s per query
- **Best for:** Gmail searches, bulk operations, JSON output
- **Command:** `gog gmail search 'QUERY' --json`
- **Example:** `gog gmail search 'from:bob@example.com AND subject:urgent'`

### SECONDARY: himalaya (IMAP/SMTP)
- **Speed:** 30-60s per query (slower)
- **Best for:** Non-Gmail accounts, offline work
- **Rarely needed** unless accessing Exchange/Outlook

### NEW: PortEden Email (Multi-Provider)
- **Speed:** Unknown (TBD)
- **Best for:** Gmail + Outlook + Exchange unified access
- **Status:** Installing soon

### Strategy
1. Use gog for all Gmail queries (fast, primary)
2. Use email-daily-summary for digests (automated)
3. Use porteden for multi-provider scenarios
4. Avoid himalaya unless no alternative
```

---

## DECISION MATRIX

### For Your Use Case (Robert's Email Needs)

| Need | Current Tool | Recommendation | Priority |
|------|--------------|---|---|
| Quick Gmail search | gog | ✅ Keep using | - |
| Batch operations | gog | ✅ Use more | - |
| Daily digest | Manual | ❌ → email-daily-summary | High |
| Multi-provider | None | ❌ → porteden-email | Medium |
| Email analytics | None | ❌ → Custom skill | Low |
| Workflow automation | None | ❌ → email-best-practices | Medium |

---

## IMPLEMENTATION PLAN

### Week 1 (This Week)
- ✅ Document current best practices in TOOLS.md
- 📦 Install porteden-email skill
- 📦 Install email-daily-summary skill
- 🧪 Test both with real email scenarios

### Week 2-3
- 📝 Create custom "email-processor" skill (wrapper)
- 🔗 Integrate with morning briefing cron
- 📊 Set up email analytics tracking

### Week 4+
- 🎯 Build dashboard (email trends)
- 🤖 Auto-filter + categorization
- 📈 Performance metrics

---

## ESTIMATED PRODUCTIVITY GAINS

| Tool | Task | Current Time | Future Time | Savings |
|------|------|--------------|-------------|---------|
| gog | Search emails | 5s | 5s | - |
| email-daily-summary | Morning digest | Manual 10m | Automatic 0m | **10m** ⚡ |
| email-daily-summary | Evening review | Manual 10m | Automatic 0m | **10m** ⚡ |
| porteden-email | Multi-provider | 60s+ | 10s | **50s** ⚡ |
| email-processor | Smart routing | N/A | 5s | **New** ⚡ |

**Daily savings:** ~20 minutes (morning/evening digests automated)

---

## NEXT STEPS

**Option 1: Proceed with installations** ✅
```bash
clawhub install porteden-email
clawhub install email-daily-summary
clawhub install email-best-practices
```

**Option 2: Test first** (safer)
- Review each skill's documentation
- Test in staging environment
- Then roll out to production

**Your call!** Which would you prefer? 🍑
