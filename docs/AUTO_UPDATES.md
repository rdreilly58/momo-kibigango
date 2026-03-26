# OpenClaw Auto-Update Configuration

**Date:** March 25, 2026  
**Status:** ✅ IMPLEMENTED  
**Scope:** macOS, Homebrew, security patches, OpenClaw

---

## Overview

Automated update management ensures system security and stability without manual intervention. Three tiers:

1. **Dry-run checks** — Show what would update (no changes)
2. **Automatic minor updates** — Install non-disruptive packages
3. **Manual approval required** — Major OS updates, requires human review

---

## Components

### 1. Auto-Update Script
**File:** `scripts/auto-update.sh`

**Checks:**
- ✅ macOS OS updates (security + feature updates)
- ✅ Homebrew package updates (installed formulas)
- ✅ Security patches (critical only)
- ✅ OpenClaw CLI updates (auto via Homebrew)
- ✅ System health verification (post-update)

**Capabilities:**
```bash
# Check only (no changes)
bash auto-update.sh --dry-run

# Check with full approval (install all updates)
bash auto-update.sh --approve-all

# Interactive mode (check, then prompt for each category)
bash auto-update.sh
```

**Output:**
```
→ Checking macOS updates...
⚠️  2 macOS update(s) available

→ Checking Homebrew updates...
⚠️  8 Homebrew update(s) available:
  • python@3.14 (3.14.2 → 3.14.3)
  • node (20.10.0 → 20.11.1)
  ...

→ Checking security patches...
⚠️  1 security update(s) available

→ Checking OpenClaw updates...
OpenClaw version: 2026.3.24
(Will be updated with Homebrew packages)

→ Verifying system health...
✅ System Health: GOOD
```

---

## Cron Integration

### Recommended Schedule

```bash
# Add to crontab
crontab -e
```

```cron
# Daily dry-run check at 6 AM (notification only)
0 6 * * * bash /Users/rreilly/.openclaw/workspace/scripts/auto-update.sh --dry-run 2>&1 | mail -s "OpenClaw Updates Available" reillyrd58@gmail.com

# Weekly auto-update: Sunday at 2 AM (off-hours)
0 2 * * 0 bash /Users/rreilly/.openclaw/workspace/scripts/auto-update.sh --approve-all >> ~/.openclaw/logs/updates.log 2>&1

# Security patches: Run immediately when detected
# (Can use alerting system to trigger on-demand)
```

---

## Manual Updates

### Check for Updates
```bash
# See what would be updated (safe, no changes)
bash ~/.openclaw/workspace/scripts/auto-update.sh --dry-run

# Check only macOS
softwareupdate -l

# Check only Homebrew
brew outdated
```

### Install Updates

**Recommended approach (safe):**

1. **Check first:**
   ```bash
   bash scripts/auto-update.sh --dry-run
   ```

2. **Review available updates** — Read the list carefully

3. **Approve and install:**
   ```bash
   bash scripts/auto-update.sh --approve-all
   ```

4. **Verify system:**
   ```bash
   bash scripts/system-health-check.sh --verbose
   ```

---

## Safety Measures

### Pre-Update
- System health check (ensure no existing issues)
- Backup critical files (git commit all changes)
- Verify disk space (>5 GB free required)

### During Update
- Sequential execution (one update at a time)
- Logging all actions to `~/.openclaw/logs/updates.log`
- Error handling (stop on critical failures)

### Post-Update
- System health verification (all systems still working)
- Restart affected services (launchd agents)
- Test critical functions (Gateway, memory search, etc.)

---

## What Gets Updated

### Always Safe to Update
- ✅ Homebrew packages (non-formulae)
- ✅ Command-line tools (git, curl, etc.)
- ✅ Development tools (Xcode, compilers)
- ✅ Security patches (critical)

### Requires Review
- ⚠️ macOS major versions (e.g., 14.0 → 15.0)
- ⚠️ Breaking changes in dependencies
- ⚠️ Database schema migrations

### Do NOT Auto-Update
- ❌ Major version jumps without testing
- ❌ System files in /etc without verification
- ❌ Custom configurations

---

## Troubleshooting

**"Update failed with error..."**
1. Check logs: `tail -100 ~/.openclaw/logs/updates.log`
2. Run health check: `bash scripts/system-health-check.sh --verbose`
3. Rollback if needed: `git checkout HEAD~1` (restore from git)

**"macOS update took too long"**
- This is normal; updates can take 30+ minutes
- Don't interrupt (system will resume after restart)
- Monitor from another device if concerned

**"Homebrew update broke something"**
1. Identify problematic package: `brew list` vs `brew cask list`
2. Downgrade: `brew install package@oldversion` 
3. Lock version: Add to `Brewfile`

**"OpenClaw not working after update"**
1. Restart: `openclaw gateway restart`
2. Check logs: `tail -100 ~/.openclaw/logs/gateway.log`
3. Verify health: `bash scripts/system-health-check.sh --verbose`
4. Rollback if needed: `brew uninstall openclaw && brew install openclaw@oldversion`

---

## Integration with Notifications

Health monitoring system alerts on:
- ❌ Update failures (critical)
- ⚠️ Available security patches (warning)
- ✅ Successful updates (info, logged)

**Alert delivery:**
- Logs to `~/.openclaw/logs/updates.log`
- Email daily report (optional)
- Telegram notifications (optional via HEARTBEAT.md)

---

## Future Improvements

- [ ] Automatic rollback if health check fails post-update
- [ ] A/B testing updates on test instance first
- [ ] Automated backup before major updates
- [ ] Update dependency resolver (prevent conflicts)
- [ ] Performance regression detection post-update
- [ ] Staged rollout (update on schedule, not all at once)
