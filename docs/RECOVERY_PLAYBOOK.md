# OpenClaw Recovery Playbook — Emergency Procedures

**Date:** March 25, 2026  
**Status:** ✅ COMPLETE  
**Scope:** Common failures + how to recover

---

## When Things Break: Decision Tree

```
❌ Something is broken/not working
   │
   ├─→ Is it a SERVICE? (Gateway, GPU, etc.)
   │   └─→ Go to "SERVICE RECOVERY" (Section 2)
   │
   ├─→ Is it a SCRIPT or CRON JOB?
   │   └─→ Go to "SCRIPT FAILURES" (Section 3)
   │
   ├─→ Is it DISK/STORAGE related?
   │   └─→ Go to "DISK EMERGENCY" (Section 4)
   │
   ├─→ Is it API/AUTHENTICATION?
   │   └─→ Go to "API FAILURES" (Section 5)
   │
   └─→ Is it GIT/DATA related?
       └─→ Go to "DATA RECOVERY" (Section 6)
```

---

## 1. IMMEDIATE STEPS (ALL FAILURES)

**When something fails, do this FIRST:**

```bash
# Step 1: Check system health
bash ~/.openclaw/workspace/scripts/system-health-check.sh --verbose

# Step 2: Check recent logs
tail -50 ~/.openclaw/logs/gateway.log
tail -50 ~/.openclaw/logs/health-check.log

# Step 3: Check what broke (run classifier)
python3 ~/.openclaw/workspace/scripts/task-classifier.py "the error you see"

# Step 4: Document the issue
echo "[$(date)] Issue: [DESCRIBE PROBLEM]" >> ~/.openclaw/logs/incidents.log
```

**DO NOT:**
- ❌ Panic or shut down the system
- ❌ Delete files to "fix" the problem
- ❌ Change configuration files blindly
- ❌ Force-kill processes
- ❌ Reboot without backing up critical data

---

## 2. SERVICE RECOVERY

### 2A. OpenClaw Gateway Not Responding

**Symptom:** "Gateway not responding on port 8080"

**Recovery (in order):**

1. **Check if running:**
   ```bash
   openclaw status
   ps aux | grep gateway
   ```

2. **If not running, restart:**
   ```bash
   openclaw gateway stop
   sleep 2
   openclaw gateway start
   
   # Wait 10 seconds for startup
   sleep 10
   
   # Verify
   curl http://localhost:8080/health
   ```

3. **If still not running, check logs:**
   ```bash
   tail -100 ~/.openclaw/logs/gateway.log
   ```

4. **If logs show API key issues:**
   ```bash
   # Ensure BRAVE_API_KEY is set
   source ~/.openclaw/workspace/TOOLS.secrets.local
   echo $BRAVE_API_KEY  # Should print key, not empty
   
   # Restart with key
   openclaw gateway restart
   ```

5. **Last resort: Full reinstall**
   ```bash
   brew uninstall openclaw
   brew install openclaw
   openclaw gateway start
   ```

### 2B. GPU Offload Not Working

**Symptom:** "GPU offload setup failed" or slow inference

**Recovery:**

1. **Quick test:**
   ```bash
   bash ~/.openclaw/workspace/scripts/gpu-health-check-quick.sh
   ```

2. **If SSH fails:**
   ```bash
   # Test connectivity
   ssh -v ec2-user@54.81.20.218 echo "OK"
   
   # Check if instance is running
   aws ec2 describe-instances --instance-ids i-xxx
   ```

3. **If GPU driver issue:**
   ```bash
   # SSH to instance
   ssh ec2-user@54.81.20.218
   nvidia-smi  # Check if GPU shows up
   ```

4. **If CUDA missing:**
   ```bash
   # On GPU instance
   python3 -c "import torch; print(torch.cuda.is_available())"
   ```

5. **If unresponsive, restart instance:**
   ```bash
   aws ec2 reboot-instances --instance-ids i-xxx
   # Wait 5 minutes for restart
   ```

---

## 3. SCRIPT FAILURES

### 3A. Cron Job Not Running

**Symptom:** Expected task didn't run at scheduled time

**Recovery:**

1. **Check cron is working:**
   ```bash
   crontab -l  # List jobs
   log show --predicate 'process == "cron"' --last 1h  # Check system log
   ```

2. **Verify specific job:**
   ```bash
   # Look for recent execution
   log show --predicate 'eventMessage contains[cd] "auto-update"' --last 1h
   ```

3. **Run manually to test:**
   ```bash
   bash ~/.openclaw/workspace/scripts/auto-update.sh --dry-run
   ```

4. **If manual works but cron doesn't:**
   - Cron may have failed silently
   - Check logs: `tail -50 ~/.openclaw/logs/updates.log`
   - Restart: `sudo launchctl stop com.apple.LaunchScheduler && sudo launchctl start com.apple.LaunchScheduler`

5. **If job produces errors:**
   ```bash
   # Run with full output
   bash -x ~/.openclaw/workspace/scripts/auto-update.sh 2>&1 | head -100
   ```

### 3B. Script Produces Errors

**Recovery:**

1. **Run with verbose:**
   ```bash
   bash -x script-name.sh --verbose
   ```

2. **Check for missing dependencies:**
   ```bash
   which python3 jq curl brew
   ```

3. **Reinstall if missing:**
   ```bash
   brew install python3 jq  # etc.
   ```

4. **Check permissions:**
   ```bash
   ls -la ~/.openclaw/workspace/scripts/
   # Should be executable (rwx)
   chmod +x ~/.openclaw/workspace/scripts/*.sh
   ```

---

## 4. DISK EMERGENCY

### 4A. Disk 90%+ Full

**Symptom:** "Disk usage critical: 90% used"

**Recovery (IMMEDIATE):**

1. **Run cleanup (safe mode):**
   ```bash
   bash ~/.openclaw/workspace/scripts/disk-cleanup.sh --dry-run
   ```

2. **Execute cleanup:**
   ```bash
   bash ~/.openclaw/workspace/scripts/disk-cleanup.sh
   ```

3. **If still >85%, use aggressive:**
   ```bash
   bash ~/.openclaw/workspace/scripts/disk-cleanup.sh --aggressive
   ```

4. **Manual cleanup (if automated doesn't help):**
   ```bash
   # Remove node_modules (can reinstall)
   find ~/.openclaw/workspace -name node_modules -type d -exec rm -rf {} +
   
   # Remove old logs
   rm ~/.openclaw/logs/*.log.*
   
   # Clean git
   cd ~/.openclaw/workspace && git gc --aggressive
   ```

5. **Verify:**
   ```bash
   df -h ~
   # Should be <75%
   ```

---

## 5. API FAILURES

### 5A. Brave Search API Not Working

**Symptom:** Web searches fail or return errors

**Recovery:**

1. **Check API key is set:**
   ```bash
   echo $BRAVE_API_KEY
   # If empty, set it
   source ~/.openclaw/workspace/TOOLS.secrets.local
   ```

2. **Test API directly:**
   ```bash
   curl "https://api.search.brave.com/res/v1/web/search?q=test&count=1" \
     -H "X-Subscription-Token: $BRAVE_API_KEY"
   ```

3. **If 401 Unauthorized:**
   - API key is invalid or expired
   - Rotate key: See TOOLS.md for Brave token setup
   - Update TOOLS.secrets.local

4. **If 429 (rate limited):**
   - You've hit the quota (1000/month)
   - Wait for reset (monthly)
   - Or use fallback (local embeddings for search)

### 5B. OpenAI API Quota Exceeded

**Symptom:** "API quota exceeded" for embeddings

**Recovery:**

1. **Check current status:**
   ```bash
   bash ~/.openclaw/workspace/scripts/api-quota-monitor.sh --verbose
   ```

2. **Use local embeddings (fallback):**
   ```bash
   # This is already deployed
   python3 ~/.openclaw/workspace/scripts/memory_search_local.py "query"
   ```

3. **Wait for quota reset:**
   - Usage resets monthly
   - Check OpenAI account for reset date

4. **Contact OpenAI:**
   - If quota is 0 and should be higher
   - Request quota increase via OpenAI dashboard

---

## 6. DATA RECOVERY

### 6A. Accidental File Deletion

**Symptom:** "I deleted something important!"

**Recovery:**

1. **Check if it's in git:**
   ```bash
   cd ~/.openclaw/workspace
   git log --diff-filter=D --summary | grep "delete mode"
   git show <commit>:path/to/file > recovered-file
   ```

2. **If not committed, check Trash:**
   ```bash
   ls -la ~/.Trash/
   # Find and restore manually
   ```

3. **If critical file is gone:**
   - Memory files: Check daily backups in `memory/`
   - Scripts: Check git history
   - Docs: Check git history
   - Config: Check backups in `~/.openclaw/backups/`

### 6B. Git Corruption

**Symptom:** "Git fatal: loose object is corrupted"

**Recovery:**

1. **Check git integrity:**
   ```bash
   cd ~/.openclaw/workspace
   git fsck --full
   ```

2. **Repair if possible:**
   ```bash
   git gc --aggressive
   ```

3. **If unfixable, re-clone:**
   ```bash
   cd ~
   mv .openclaw/workspace .openclaw/workspace.bak
   git clone <remote> .openclaw/workspace
   ```

### 6C. Workspace Is Dirty (uncommitted changes)

**Symptom:** Can't pull/merge due to uncommitted changes

**Recovery (safe):**

1. **Stash changes:**
   ```bash
   cd ~/.openclaw/workspace
   git stash  # Saves changes temporarily
   ```

2. **Try operation again:**
   ```bash
   git pull
   ```

3. **Recover stashed changes (if needed):**
   ```bash
   git stash pop  # Restores saved changes
   ```

**Recovery (destructive):**

1. **Discard all local changes:**
   ```bash
   cd ~/.openclaw/workspace
   git checkout .
   git clean -fd  # Remove untracked files
   ```

---

## 7. ESCALATION GUIDE

**If recovery steps don't work, escalate to:**

1. **Check system health first:**
   ```bash
   bash ~/.openclaw/workspace/scripts/system-health-check.sh --verbose
   bash ~/.openclaw/workspace/scripts/api-quota-monitor.sh --verbose
   ```

2. **Collect diagnostics:**
   ```bash
   mkdir ~/openclaw-diagnostics
   cp ~/.openclaw/logs/* ~/openclaw-diagnostics/
   cp ~/.openclaw/workspace/SOUL.md ~/openclaw-diagnostics/
   cp ~/.openclaw/workspace/memory/2026-03-25.md ~/openclaw-diagnostics/
   # Share with Bob
   ```

3. **Document in incident log:**
   ```bash
   cat >> ~/.openclaw/logs/incidents.log << EOF
[$(date)] INCIDENT: [Title]
Error: [Full error message]
Steps taken: [What you tried]
Status: [Still broken / Fixed]
EOF
   ```

4. **Create recovery task in HEARTBEAT.md:**
   ```markdown
   ## RECOVERY IN PROGRESS
   - [x] Symptom identified
   - [ ] Root cause found
   - [ ] Fix applied
   - [ ] Verified working
   ```

---

## 8. PREVENTIVE MEASURES

**To avoid emergencies:**

- ✅ Run health checks daily (`system-health-check.sh`)
- ✅ Monitor disk space (alert at 75%)
- ✅ Commit changes regularly (`git add/commit`)
- ✅ Keep API quotas monitored (`api-quota-monitor.sh`)
- ✅ Test recovery procedures monthly
- ✅ Keep backups updated (git history)
- ✅ Review logs weekly

---

## 9. QUICK REFERENCE

| Issue | Command | Recovery Time |
|-------|---------|---|
| Gateway down | `openclaw gateway restart` | 30s |
| Disk full | `bash disk-cleanup.sh` | 1m |
| Cron not running | `bash script --dry-run` | 2m |
| API quota exceeded | Use local embeddings | 0s |
| Git corrupted | `git fsck --full` | 5m |
| File deleted | `git show <commit>:file` | 1m |
| Service unresponsive | `sudo launchctl restart` | 10s |

---

## 10. POST-INCIDENT

After recovering from an incident:

1. **Document what happened:**
   ```bash
   echo "Incident summary..." >> ~/.openclaw/logs/incidents.log
   ```

2. **Update memory:**
   ```bash
   # Add to memory/2026-03-25.md
   ## INCIDENT: [Title]
   - Root cause: [Why it happened]
   - Fix: [How we fixed it]
   - Prevention: [How to avoid next time]
   ```

3. **Commit changes:**
   ```bash
   git add -A && git commit -m "Recovery from [incident]: [summary]"
   ```

4. **Review preventive measures:**
   - Should health check have caught this?
   - Should we add a new monitoring check?
   - Should we add a test case?

---

**Key principle:** You can recover from almost anything except complete data loss. Always commit, always backup, always test recovery procedures.
