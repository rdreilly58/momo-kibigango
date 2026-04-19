# Skills Audit — March 27, 2026

## ACTUAL INVENTORY (Corrected)
- **Active Skills:** 26 (in `~/.openclaw/workspace/skills/`)
- **Archived Skills:** 13 (in `~/.openclaw/workspace/skills-archived/`)
- **Total:** 39 skills

## Problem Statement
Claude kept generating analytical reports WITHOUT showing the actual commands/lists needed for execution. This made recommendations useless without additional back-and-forth.

## Solution: Always provide THREE things
1. **Analysis** (context for decision-making)
2. **Actual List** (copy-paste ready commands or file paths)
3. **Execution Steps** (exactly how to do it)

---

## HIGH PRIORITY DELETION (10 skills — 264 KB)

### Actual File Paths to Delete

```bash
# Delete these 10 skills immediately
rm -rf ~/.openclaw/workspace/skills/email-best-practices
rm -rf ~/.openclaw/workspace/skills/browser-automation
rm -rf ~/.openclaw/workspace/skills/porteden-email
rm -rf ~/.openclaw/workspace/skills/email-daily-summary
rm -rf ~/.openclaw/workspace/skills/google-tasks
rm -rf ~/.openclaw/workspace/skills/uptime-kuma
rm -rf ~/.openclaw/workspace/skills/email-management
rm -rf ~/.openclaw/workspace/skills/security-monitor
rm -rf ~/.openclaw/workspace/skills/website-monitor
rm -rf ~/.openclaw/workspace/skills/notion
```

### Why Delete
- **email-best-practices**: Reference docs only, never executed
- **browser-automation**: Superseded by agent-browser (use that instead)
- **porteden-email**: Deprecated legacy skill
- **email-daily-summary**: Replaced by daily-briefing
- **google-tasks**: Using gog cli instead
- **uptime-kuma**: Using healthchecks.io instead
- **email-management**: Using gmail-send instead
- **security-monitor**: No active deployment
- **website-monitor**: Not configured
- **notion**: No Notion workspace

---

## MEDIUM PRIORITY DELETION (10 skills — 2.3 MB)

### Actual File Paths to Delete

```bash
# Delete these 10 skills (optional, review first)
rm -rf ~/.openclaw/workspace/skills/linkedin-automation
rm -rf ~/.openclaw/workspace/skills/time-tracker
rm -rf ~/.openclaw/workspace/skills/uml-diagrams
rm -rf ~/.openclaw/workspace/skills/database-operations
rm -rf ~/.openclaw/workspace/skills/sovereign-aws-cost-optimizer
rm -rf ~/.openclaw/workspace/skills/aws-mac-launch
rm -rf ~/.openclaw/workspace/skills/gpu-health-check
rm -rf ~/.openclaw/workspace/skills/resiliant-connections
rm -rf ~/.openclaw/workspace/skills/speculative-decoding    # 22M!
rm -rf ~/.openclaw/workspace/skills/pdf-pro                 # 672K!
```

### Why Delete
- **linkedin-automation**: No LinkedIn posting workflow
- **time-tracker**: Not actively used
- **uml-diagrams**: No architecture work
- **database-operations**: No active DB projects
- **sovereign-aws-cost-optimizer**: One-time tool
- **aws-mac-launch**: One-time automation
- **gpu-health-check**: AWS quota pending (waiting game)
- **resiliant-connections**: Reference documentation only
- **speculative-decoding**: Phase 1 research (22 MB!) — delete unless Phase 2 is priority
- **pdf-pro**: Superseded by make-pdf + weasyprint (672 KB)

---

## KEEP (22 skills — Your actual toolkit)

### Essential Skills
```
~/.openclaw/workspace/skills/daily-briefing          (116K) — Morning/evening reports
~/.openclaw/workspace/skills/gmail-send               (48K) — Email delivery
~/.openclaw/workspace/skills/make-pdf                 (8K)  — PDF generation
~/.openclaw/workspace/skills/invoice-generator        (28K) — Invoice creation
~/.openclaw/workspace/skills/office-docs              (24K) — Word/Excel editing
```

### Development Skills
```
~/.openclaw/workspace/skills/ios-dev                  (12K) — Xcode builds
~/.openclaw/workspace/skills/swift-expert             (64K) — iOS development
~/.openclaw/workspace/skills/roblox-loader            (68K) — Game automation
~/.openclaw/workspace/skills/aws-deploy               (8K)  — Amplify deployment
~/.openclaw/workspace/skills/agent-browser            (24K) — Web automation
~/.openclaw/workspace/skills/web-perf                 (16K) — Performance testing
```

### Operations Skills
```
~/.openclaw/workspace/skills/printer-brother          (36K) — Printer control
~/.openclaw/workspace/skills/print-local              (8K)  — Local printing
~/.openclaw/workspace/skills/s3                       (12K) — Object storage
~/.openclaw/workspace/skills/ga4-analytics            (16K) — Analytics queries
~/.openclaw/workspace/skills/address-lookup           (4K)  — Location lookup
~/.openclaw/workspace/skills/slack                    (12K) — Slack messaging
```

### Utility Skills (Built-in/CLI-based)
```
Local embeddings (integrated)                               — Memory search
gog cli                                                     — Gmail, Calendar, Drive, Tasks
```

---

## Execution Steps

### Step 1: Backup (ALWAYS do this first)
```bash
cd ~/.openclaw/workspace/skills
tar -czf ~/skills-backup-2026-03-27.tar.gz .
echo "✅ Backup created: ~/skills-backup-2026-03-27.tar.gz"
```

### Step 2: Delete HIGH PRIORITY
```bash
# Copy/paste the HIGH PRIORITY deletion block above
# Then verify:
ls ~/.openclaw/workspace/skills | wc -l  # Should be 32 (42-10)
```

### Step 3: Test System
```bash
openclaw status
openclaw cron list
```

### Step 4: Git Commit
```bash
cd ~/.openclaw/workspace
git add -A
git commit -m "CLEANUP: Remove 10 unused skills (HIGH PRIORITY)"
git log --oneline | head -3
```

### Step 5: Optional — Delete MEDIUM PRIORITY
```bash
# Only after reviewing:
# - Is Phase 2 of speculative-decoding planned? (if YES, keep it)
# - Do you ever use time-tracker? (if YES, keep it)
# - Do you use pdf-pro features? (if NO, keep make-pdf)
```

---

## Important: Never Forget This
- **Always provide actual paths/commands**, not just analysis
- When recommending deletion, show the exact `rm` commands
- Include backup steps before destructive operations
- Show expected results (e.g., "should be 32 skills after")
- Provide git commit steps for audit trail

This SKILLS_AUDIT.md file IS the permanent record. Reference it in future audits.

