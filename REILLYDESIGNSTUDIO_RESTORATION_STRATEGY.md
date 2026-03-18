# ReillyDesignStudio Website Restoration Strategy

**Created:** March 15, 2026 @ 3:36 AM EDT  
**Status:** Ready to Execute  
**Scope:** Major Migration + Restoration

---

## Executive Summary

**Goal:** Restore website to March 12, 2026 version and migrate hosting to AWS Amplify while preserving all integrations.

**Timeline:** [TBD - awaiting approval]  
**Risk Level:** Medium (data preservation critical)  
**Rollback Plan:** Keep old infrastructure alive for 48-72 hours post-cutover

---

## Strategic Goals (Prioritized)

1. **PRIMARY:** Restore website to working March 12th state
2. **SECONDARY:** Migrate hosting to AWS Amplify (from current)
3. **TERTIARY:** Preserve all data, integrations, and functionality
4. **CLEANUP:** Remove previous AWS implementations

---

## Critical Infrastructure to Preserve

### Database Layer
```
✅ Neon PostgreSQL
   - Keep existing instance
   - Preserve all data
   - Connection string stays same
   - Schema matches March 12th version
   
✅ Prisma ORM
   - Update schema if needed
   - Migration scripts ready
   - Connection pooling configured
```

### Analytics & Monitoring
```
✅ Google Analytics 4 (GA4)
   - Property ID: [to be confirmed]
   - Measurement ID: [to be confirmed]
   - Tracking code maintained
   - Historical data preserved
   
✅ Sentry Error Tracking
   - DSN: https://a6b9e648a246ad893c1a40399d39993b@o4511047232061440.ingest.us.sentry.io/4511047233961984
   - Organization: reilly-design-studio
   - Project: reillydesignstudio
   - Auth Token: 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
```

### Authentication & Session Management
```
✅ NextAuth Configuration
   - Session strategy (database-based)
   - NEXTAUTH_URL: https://reillydesignstudio.com
   - NEXTAUTH_SECRET: [preserved from current]
   - Session table in Neon
```

### DNS & Domain
```
✅ Cloudflare DNS
   - DNS provider (continue using)
   - Root domain: reillydesignstudio.com
   - Current A/AAAA records backup
   - All subdomains preserved
   - SSL/TLS settings maintained
```

### AWS Resources
```
✅ S3 Buckets
   - For file uploads (invoices, documents)
   - Bucket: [TBD]
   - Access keys preserved
   - Bucket policies migrated
   
✅ AWS Amplify
   - New app for hosting
   - GitHub integration
   - Build & deployment settings
   - Custom domain configuration
```

---

## Environment Variables (Complete List)

All of these must be configured in Amplify console:

```bash
# Authentication
NEXTAUTH_URL=https://reillydesignstudio.com
NEXTAUTH_SECRET=[FROM CURRENT .env.local]

# Database (CRITICAL - DO NOT CHANGE)
DATABASE_URL=[Neon connection string - PRESERVE EXACTLY]

# Error Tracking (Sentry)
SENTRY_DSN=https://a6b9e648a246ad893c1a40399d39993b@o4511047232061440.ingest.us.sentry.io/4511047233961984
SENTRY_ORG=reilly-design-studio
SENTRY_PROJECT=reillydesignstudio
SENTRY_AUTH_TOKEN=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

# Analytics
GA4_MEASUREMENT_ID=[FROM GOOGLE ANALYTICS]
NEXT_PUBLIC_GA4_ID=[FROM GOOGLE ANALYTICS]

# AWS S3 (File Uploads)
AWS_ACCESS_KEY_ID=[FROM CURRENT CONFIG]
AWS_SECRET_ACCESS_KEY=[FROM CURRENT CONFIG]
AWS_REGION=us-east-1
AWS_S3_BUCKET=[BUCKET NAME]

# Application
NODE_ENV=production
LOG_LEVEL=info
```

---

## Implementation Phases

### Phase 0: Inventory & Documentation (IMMEDIATE)

**Objective:** Document everything before making changes

**Tasks:**
- [ ] Export all environment variables from current setup
  ```bash
  # Create backup of current .env files
  cat ~/.openclaw/workspace/reillydesignstudio/.env.local > ~/Desktop/env-backup-2026-03-15.txt
  ```

- [ ] Document Neon database details
  - Connection string
  - Database name
  - User credentials
  - Any replication/backup settings

- [ ] Document current Amplify setup (if exists)
  - App ID
  - Build settings
  - Deployment history
  - Domain configuration

- [ ] Backup Cloudflare DNS records
  - Export all DNS records
  - Note TTL values
  - Document current A/AAAA records

- [ ] Identify Git commit for March 12th version
  ```bash
  cd ~/.openclaw/workspace/reillydesignstudio
  git log --oneline --grep="March 12" # or similar
  git log --before="2026-03-13" --after="2026-03-11" --oneline
  ```

- [ ] List all current AWS resources in use
  - Amplify apps
  - Lambda functions
  - RDS databases
  - S3 buckets
  - VPC configurations

**Deliverables:**
- Backup of all env vars
- Neon connection details document
- Cloudflare DNS record export
- AWS resource inventory
- Git commit reference for March 12th

---

### Phase 1: Amplify Setup & Testing (STAGING)

**Objective:** Prepare Amplify environment without affecting production

**Tasks:**

1. **Create/Configure Amplify App**
   ```bash
   # Option A: Create new app in AWS Amplify console
   # Option B: Reconfigure existing if available
   ```

2. **Connect to GitHub Repository**
   - Authorize GitHub
   - Select repo: reillydesignstudio
   - Select branch: main (or March 12th branch if separate)

3. **Configure Build Settings**
   ```
   Framework: Next.js
   Build command: npm run build
   Start command: npm start
   Base directory: (root)
   ```

4. **Set Environment Variables in Amplify**
   - Copy all from Phase 0 backup
   - Verify DATABASE_URL is exact same
   - Store NEXTAUTH_SECRET securely

5. **Deploy to Preview (Staging)**
   - Trigger initial build
   - Monitor build logs
   - Check for build errors
   - Verify preview URL works

**Success Criteria:**
- Build completes without errors
- Preview environment accessible
- No database connection errors in logs

---

### Phase 2: Integration Testing (STAGING)

**Objective:** Verify all integrations work before DNS cutover

**Tests:**

1. **Database Connectivity**
   ```bash
   curl https://[staging-url]/api/health
   # Should return: { "status": "ok", "checks": { "database": "ok" } }
   ```

2. **GA4 Tracking**
   - Visit staging URL
   - Check Google Analytics real-time
   - Verify events are recording

3. **Sentry Error Capture**
   - Trigger test error in API route
   - Verify appears in Sentry dashboard within 10 seconds
   - Check stack trace accuracy

4. **NextAuth Sessions**
   - Test login flow
   - Verify session creation
   - Check session persistence
   - Test logout

5. **File Uploads (S3)**
   - Test file upload functionality
   - Verify files appear in S3
   - Test download/access

6. **Email Functionality**
   - Test contact form
   - Verify email is sent
   - Check email content

7. **Health Check**
   - `curl https://[staging-url]/api/health`
   - All checks should pass

**Success Criteria:**
- All tests pass
- No errors in logs
- All integrations functional
- Performance acceptable

---

### Phase 3: DNS Cutover (GO LIVE)

**Objective:** Redirect traffic to Amplify

**Pre-Cutover Checklist:**
- [ ] Phase 2 testing complete & passed
- [ ] All team members notified
- [ ] Rollback plan documented
- [ ] Monitoring dashboards open
- [ ] Support team on standby

**Cutover Steps:**

1. **Update Cloudflare DNS**
   - Go to Cloudflare dashboard
   - Update A/AAAA records to point to Amplify
   - Note TTL (suggest lowering to 5 min before cutover)
   - Wait for propagation (typically 1-5 minutes)

2. **Monitor Traffic**
   ```bash
   # Watch Amplify logs in real-time
   # Watch Sentry for errors
   # Monitor GA4 for traffic
   # Check database logs
   ```

3. **Verify User Access**
   - Test from multiple networks
   - Check on mobile devices
   - Verify HTTPS/SSL working
   - Check response times

4. **Rollback Plan (If Issues)**
   - Keep old infrastructure alive
   - Have DNS reversion ready (< 1 minute)
   - Monitor for 24-48 hours minimum

**Monitoring During Cutover:**
- Sentry dashboard (error rate)
- GA4 real-time (traffic)
- Amplify logs (application logs)
- Cloudflare analytics (DNS queries)
- Database logs (connection issues)

---

### Phase 4: Verification (48-72 Hours)

**Objective:** Confirm everything working, then cleanup

**Tasks:**
- [ ] Monitor error rates (should be zero or baseline)
- [ ] Verify GA4 data flowing normally
- [ ] Check database query times
- [ ] Confirm all email sends working
- [ ] Validate file uploads working
- [ ] Monitor uptime (should be 100%)

**If Issues Found:**
- [ ] Check Sentry for error details
- [ ] Review Amplify build logs
- [ ] Check database logs
- [ ] Verify environment variables
- [ ] Roll back if necessary

---

### Phase 5: Cleanup (After Verification)

**Objective:** Remove old infrastructure

**Tasks:**

1. **Old Amplify App (if exists)**
   - [ ] Delete from AWS Amplify console
   - [ ] Verify DNS no longer points to it

2. **Old AWS Resources**
   - [ ] Delete unused Lambda functions
   - [ ] Terminate unused RDS databases
   - [ ] Delete old S3 buckets (if unused)
   - [ ] Remove old IAM roles/policies
   - [ ] Delete unused VPC resources

3. **Archive Configurations**
   - [ ] Save old deployment configs
   - [ ] Document what was deleted
   - [ ] Note deletion timestamps

4. **Final Verification**
   - [ ] Confirm no old resources still in use
   - [ ] Verify all traffic on new Amplify
   - [ ] Check AWS billing (old resources gone)

---

## Git & Code Management

### Identifying March 12th Version

```bash
# Find commits around March 12th
git log --after="2026-03-11" --before="2026-03-13" --oneline

# If specific branch exists
git branch -a | grep "march\|12"

# Get commit hash and check it
git show [COMMIT_HASH] --stat
```

### Code Reset (If Needed)

```bash
# If reverting entire codebase
git checkout [MARCH_12_COMMIT_HASH]

# Or create new branch from that point
git checkout -b restore-march-12 [MARCH_12_COMMIT_HASH]
```

---

## Risk Management

### High Risk Items

1. **Database Data Loss**
   - Mitigation: Neon snapshot before starting
   - Rollback: Restore from snapshot
   - Timeline: Minutes

2. **Connection String Wrong**
   - Mitigation: Triple-verify DATABASE_URL
   - Rollback: Revert Amplify env var
   - Timeline: Seconds

3. **DNS Pointing Wrong**
   - Mitigation: Have old DNS values documented
   - Rollback: Revert Cloudflare records
   - Timeline: < 5 minutes

### Medium Risk Items

1. **Auth Tokens Invalid**
   - Mitigation: Test each before cutover
   - Rollback: Update to valid tokens
   - Timeline: Minutes

2. **Build Fails**
   - Mitigation: Test on staging first
   - Rollback: Use previous build
   - Timeline: Minutes

### Low Risk Items

1. **Performance Issues**
   - Mitigation: Monitor & optimize
   - Rollback: No rollback needed
   - Timeline: Hours

---

## Rollback Procedure (If Needed)

**If things go wrong:**

1. **Revert DNS (< 5 min)**
   ```
   Cloudflare → Restore previous A/AAAA records
   Traffic redirects back to old host
   ```

2. **Check Old Infrastructure**
   ```
   Verify old system still running
   Test user access
   Monitor error rates
   ```

3. **Investigate Root Cause**
   ```
   Check Sentry logs
   Check Amplify build logs
   Check database connectivity
   Verify environment variables
   ```

4. **Fix & Retry**
   ```
   Correct configuration
   Test on staging
   Re-attempt cutover
   ```

---

## Success Metrics

After cutover, verify:

```
✓ Website accessible at reillydesignstudio.com
✓ All pages load without errors
✓ API endpoints responding
✓ Database queries working
✓ GA4 tracking events
✓ Sentry capturing errors (only real ones)
✓ Email functionality working
✓ File uploads to S3 working
✓ NextAuth sessions working
✓ Response times acceptable
✓ Zero 5xx errors
✓ HTTPS/SSL valid
```

---

## Questions for Bob (Awaiting Answers)

1. **Git Reference:**
   - What's the exact commit/tag for March 12th version?
   - Is this on main branch or separate branch?

2. **Current State:**
   - Where is website currently hosted?
   - What changed since March 12th that needs reverting?
   - Any data that needs to be lost?

3. **Data:**
   - Keep all existing database data?
   - Or start with clean database from March 12th?

4. **Testing:**
   - Full staging test before DNS cutover?
   - Or go straight to production?

5. **Timing:**
   - Urgent (today)?
   - This week?
   - When ready?

6. **Rollback:**
   - How long keep old infrastructure alive?
   - 24h? 48h? 72h?

7. **Notifications:**
   - Alert users during migration?
   - Maintenance window planned?

---

## Checklist Summary

### Before Starting
- [ ] All env vars exported & backed up
- [ ] Neon database snapshot taken
- [ ] Cloudflare DNS records exported
- [ ] Git commit identified
- [ ] All questions answered

### During Amplify Setup
- [ ] Amplify app created
- [ ] GitHub connected
- [ ] Build settings configured
- [ ] Environment variables set
- [ ] Preview deployment successful

### Before DNS Cutover
- [ ] All Phase 2 integration tests passed
- [ ] Staging environment fully tested
- [ ] Rollback plan documented
- [ ] Team notified
- [ ] Support team ready

### After DNS Cutover
- [ ] Traffic successfully routed
- [ ] Monitoring dashboards active
- [ ] Error rates normal
- [ ] GA4 tracking working
- [ ] Sentry operational

### After Verification Period
- [ ] 48-72 hours passed
- [ ] No issues found
- [ ] Old infrastructure deleted
- [ ] Billing verified (old resources gone)

---

## Timeline Estimate

**Phase 0 (Inventory):** 30 minutes  
**Phase 1 (Amplify Setup):** 1 hour  
**Phase 2 (Testing):** 1-2 hours  
**Phase 3 (DNS Cutover):** 15 minutes  
**Phase 4 (Verification):** 48-72 hours (monitoring, not active work)  
**Phase 5 (Cleanup):** 30 minutes  

**Total Active Time: 3-4 hours**  
**Total Calendar Time: 3-4 days (including verification period)**

---

## Important Notes

- ⚠️ **Never change DATABASE_URL except intentionally**
- ⚠️ **Always have rollback plan before DNS change**
- ⚠️ **Backup everything before making changes**
- ✅ **Test thoroughly on staging before production**
- ✅ **Monitor logs continuously during cutover**
- ✅ **Keep old infrastructure alive during verification**

---

## Status

✅ **Strategy Documented**  
⏳ **Awaiting Answers to Questions**  
📋 **Ready to Begin Phase 0**

**Next Step:** Confirm questions answered, then begin Inventory phase.
