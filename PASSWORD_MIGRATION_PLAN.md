# Password Manager Migration Plan

**Decision Date:** March 19, 2026  
**Status:** Ready to Execute  
**Owner:** Bob Reilly

---

## Strategy: Hybrid Approach

### Distribution

| Category | Manager | Rationale |
|----------|---------|-----------|
| **Personal Passwords** | Apple Passwords | Native, convenient, frictionless |
| **System Secrets & API Keys** | 1Password | CLI access, audit logs, OpenClaw integration |
| **Dashlane** | Retire | Consolidate to avoid duplicate management |

---

## Migration Steps

### Phase 1: Export & Backup (Today - 15 min)

**Step 1a: Export Dashlane (Safety Net)**
```bash
# Open Dashlane app
# Settings → Export → Download encrypted backup
# Save to: ~/Desktop/dashlane-backup-2026-03-19.csv
# Keep in secure location (encrypted drive recommended)
```

**Step 1b: Export Chrome Passwords**
```bash
# Chrome → Settings → Passwords and autofill → Password Manager
# Click three dots (top right) → Export passwords
# Save to: ~/Desktop/chrome-passwords-2026-03-19.csv
```

### Phase 2: Import to Apple Passwords (Tomorrow - 10 min)

**Step 2a: Import Chrome CSV**
```bash
# On Mac:
# System Settings → Passwords (left sidebar)
# Click + button (top)
# Select "Import from file"
# Choose: chrome-passwords-2026-03-19.csv
# Apple Passwords auto-fills everything
```

**Step 2b: Verify on All Apple Devices**
- [ ] Mac (Settings → Passwords)
- [ ] iPhone (Settings → Passwords & Security)
- [ ] iPad (same as iPhone)
- [ ] Test a few logins in Safari

### Phase 3: Cleanup & Consolidate (Tomorrow afternoon - 10 min)

**Step 3a: Secure File Deletion**
```bash
# Delete temporary CSV files securely
rm ~/Desktop/chrome-passwords-2026-03-19.csv

# Keep Dashlane backup as safety net in secure location
# (Don't delete - keep for 2 weeks, then can discard)
```

**Step 3b: Disable Dashlane**
- [ ] Open Dashlane app
- [ ] Settings → Disable auto-fill
- [ ] Can uninstall completely (backup is saved)

### Phase 4: Clean 1Password (End of week - 15 min)

1Password will be **pure operational store** — secrets only

**Populate 1Password with:**
- [ ] Brave Search API key: `REDACTED_BRAVE_API_TOKEN`
- [ ] Cloudflare API Token: `REDACTED_CLOUDFLARE_TOKEN`
- [ ] GitHub tokens (if needed)
- [ ] GA4 service account (if needed)
- [ ] Any other API keys/operational secrets

---

## Current Status

### Chrome Passwords
- **Source:** Primary source (has more passwords than Dashlane)
- **Count:** To be determined on export
- **Action:** Export & import to Apple Passwords

### Dashlane
- **Status:** Will be retired
- **Safety:** Backup CSV saved before disabling
- **Timeline:** Can be uninstalled after 2-week verification period

### 1Password
- **Current State:** Empty (nothing of value)
- **Future State:** Secrets & API keys only (clean operational store)
- **Integration:** OpenClaw can access via `op` CLI

---

## Timeline

| Phase | Task | Duration | Date |
|-------|------|----------|------|
| 1 | Export Dashlane + Chrome | 15 min | Today (3/19) |
| 2 | Import to Apple Passwords | 10 min | Tomorrow (3/20) |
| 2 | Verify on all devices | 5 min | Tomorrow (3/20) |
| 3 | Secure cleanup & disable Dashlane | 10 min | Tomorrow (3/20) |
| 4 | Populate 1Password with secrets | 15 min | End of week (3/23) |

**Total effort:** ~55 minutes spread over 3 days

---

## Safety Checks

- ✅ Dashlane backup saved before any changes
- ✅ No shared/team accounts to worry about
- ✅ Verification on all Apple devices before cleanup
- ✅ CSV files securely deleted (not in trash)
- ✅ 2-week grace period before Dashlane uninstall

---

## Post-Migration

### Apple Passwords (Personal)
- Bank accounts
- Email accounts
- Social media
- Streaming services (Netflix, Spotify, etc.)
- Shopping sites (Amazon, etc.)
- Personal accounts

### 1Password (Operational)
- API keys (Brave, Cloudflare, GitHub, GA4)
- SSH keys
- Service account credentials
- Tokens (OpenClaw, ReadTheDocs)
- Sensitive environment variables
- Tool access credentials

### OpenClaw Integration
- ✅ No changes to current setup
- ✅ 1password skill works unchanged
- ✅ Password injection capability preserved
- ✅ Automation stays powerful

---

## Questions Answered

**Q: What about shared accounts?**  
A: None to migrate. Only personal accounts.

**Q: Keep Dashlane backup?**  
A: Yes. Save as safety net for 2 weeks, then can discard.

**Q: Will OpenClaw lose access?**  
A: No. 1Password stays operational, CLI access unchanged.

**Q: What about Chrome auto-fill?**  
A: Will still work (Apple Passwords integrates with Chrome extension).

---

## Sign-Off

**Decision:** Hybrid approach approved  
**Date:** March 19, 2026 @ 3:55 PM EDT  
**Ready to execute:** Yes  
**Start date:** March 19 evening (export) / March 20 morning (import)
