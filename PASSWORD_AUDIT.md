# Password Security Audit & Change Tracking

**Date Started:** March 16, 2026, 8:36 AM EDT  
**Status:** In Progress  
**Goal:** Replace reused/compromised passwords with unique, strong passwords

---

## 📋 SITE AUDIT LIST

| # | Site | Email/Username | New Password | Current Status | Password Changed? | 1Password Entry | Notes |
|---|------|---|---|---|---|---|---|
| 1 | **Gmail** | rdreilly2010@gmail.com | `IXdAS6KjHyGAR5bQqqZo` | ✅ DONE | ✅ YES | i7cysz4mdghgoarqqlomqzc3oy | 🔴 HIGH PRIORITY - email master account |
| 2 | **AWS - Root** | robert.reilly@alum.mit.edu | (manually changed) | ⏳ PENDING | ❓ Manual | — | 🔴 CRITICAL - do NOT use regularly |
| 2b | **AWS - bob-admin (IAM)** | bob-admin | `ASub6gAf3DXmj0COY151` | ✅ DONE | ✅ YES | 2oja55tjht4rj65fdqfwzf3hoq | 🟡 USE THIS for daily work (admin access) |
| 3 | **Cloudflare** | (support case pending) | ⏰ SCHEDULED | ❌ No | — | 🔴 CRITICAL - domain registrar (8 visits) — **REMINDER: Wed Mar 18, 9 AM** |
| 4 | **Amazon** | rdreilly2010@gmail.com | ✅ DONE | ✅ YES | — | Password changed ✅ |
| 5 | **GitHub** | (need to verify) | ⏳ PENDING | ❌ No | — | Code repository access (4 visits) |
| 6 | **CapitalOne** | rdreilly58 | ✅ DONE | ✅ YES | — | 🟠 Financial institution — Updated ✅ |
| 7 | **Mercury** | robert.reilly@reillydesignstudio.com | ✅ DONE | ✅ YES | aifngc45fsjrzbcxzenom5flxa | 🟠 Financial/banking app (13-15 visits) — Changed ✅ |
| 8 | **LinkedIn** | robert.reilly@alum.mit.edu | `8JIWESX1JzW5q5rAzN87` | ✅ DONE | ✅ YES | — | Professional network — Updated ✅ |
| 8b | **Facebook** | robert.reilly@alum.mit.edu | `8JIWESX1JzW5q5rAzN87` | ✅ DONE | ✅ YES | — | Social media — Updated ✅ (shares password with LinkedIn) |
| 9 | **Apple** | (need to verify) | ⏳ PENDING | ❌ No | — | Apple ID - critical |
| 10 | **Slack** | (need to verify) | ⏳ PENDING | ❌ No | — | Team communication |
| 11 | **Google Analytics** | (need to verify) | ⏳ PENDING | ❌ No | — | Website analytics (5+ visits) |
| 12 | **Google Cloud Console** | (need to verify) | ⏳ PENDING | ❌ No | — | GCP access (3 visits) |
| 13 | ~~**Peraton (SSO)**~~ | — | ❌ REMOVED | N/A | — | ~~Corporate SSO~~ — Bob no longer works there |
| 14 | ~~**Peraton Prod**~~ | — | ❌ REMOVED | N/A | — | ~~Work application~~ — Bob no longer works there |
| 15 | **Salesforce** | (need to verify) | ⏳ PENDING | ❌ No | — | CRM/internal tool (2+ visits) |
| 16 | **Zoom** | (need to verify) | ⏳ PENDING | ❌ No | — | Video conferencing (2 visits) |
| 17 | **Microsoft Outlook/Office 365** | (need to verify) | ⏳ PENDING | ❌ No | — | Email/Office access (2 visits) |
| 18 | **Plaid** | (need to verify) | ⏳ PENDING | ❌ No | — | Fintech/banking aggregator (2 visits) |
| 19 | **PayViam** | (need to verify) | ⏳ PENDING | ❌ No | — | Payment service (5 visits) |
| 20 | **OppLoans** | (need to verify) | ⏳ PENDING | ❌ No | — | Lending/financial (1 visit) |

---

## 🔄 PROCESS WORKFLOW

**For each site:**
1. ✅ Verify email/username
2. ✅ Generate new unique password (16+ chars, mixed)
3. ✅ Create/update entry in 1Password
4. ✅ Login and change password at site
5. ✅ Verify new password works
6. ✅ Mark as "Password Changed ✅"

---

## ⚠️ SECURITY NOTES

- **Current risk:** Reusing passwords across multiple sites
- **Compromise vector:** If one site is breached, attacker has access to all sites using that password
- **Remediation:** Unique password per site
- **Master credential:** Gmail (email account) - change this FIRST

---

## 📊 PROGRESS SUMMARY

**Total sites:** 18 (removed Peraton)  
**Changed:** 7 (Gmail, Mercury, AWS IAM, Amazon, CapitalOne, LinkedIn, Facebook)  
**In Progress:** 1 (Cloudflare-scheduled Wed)  
**Pending:** 10  
**Completion:** 39% (7/18)

**Priority Tiers:**
- 🔴 **CRITICAL** (4 sites): Gmail, AWS, Cloudflare, Mercury
- 🟠 **HIGH** (6 sites): CapitalOne, GitHub, Google (Analytics/Cloud), Peraton
- 🟡 **MEDIUM** (10 sites): Remaining sites

---

## 🛠️ NEXT STEPS

1. Bob provides email/username for each site
2. Momotaro generates unique passwords
3. Momotaro creates 1Password entries
4. Bob changes passwords on each site (in order of criticality)
5. Track completion

**Ready to start? Need emails/usernames for each site!** 🔐
