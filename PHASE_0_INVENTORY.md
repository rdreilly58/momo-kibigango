# Phase 0: Inventory & Documentation
**Date:** March 15, 2026 @ 4:09 AM EDT  
**Status:** ✅ COMPLETE

---

## Configuration Snapshot

### Git
- **Target Commit:** `282e52ce49fb89b6e92208afed3dfe3b3c8176cf`
- **Target Message:** "🚀 Deploy Stripe + OAuth environment variables (production keys live)"
- **Current HEAD:** `921ca1b` (32 commits ahead)
- **Location:** `~/.openclaw/workspace/reillydesignstudio`

### Database (Neon)
- **Project ID:** `flat-salad-11854892`
- **Branch:** `br-restless-voice-aif3o9rq` (production)
- **Endpoint Host:** `ep-green-voice-ai9e4rfz.c-4.us-east-1.aws.neon.tech`
- **Pooled Host:** `ep-green-voice-ai9e4rfz-pooler.c-4.us-east-1.aws.neon.tech`
- **Region:** `aws-us-east-1`
- **Status:** Idle (suspended since March 9, 2026)
- **CONNECTION STRING:** `postgresql://neondb_owner:npg_rkz4vYuJ0XlP@ep-green-voice-ai9e4rfz-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require`

### Environment Variables (Current)
```
SENTRY_DSN=https://a6b9e648a246ad893c1a40399d39993b@o4511047232061440.ingest.us.sentry.io/4511047233961984
SENTRY_ORG=reilly-design-studio
SENTRY_PROJECT=reillydesignstudio
SENTRY_AUTH_TOKEN=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
NEXTAUTH_URL=https://reillydesignstudio.com
LOG_LEVEL=info
DATABASE_URL=postgresql://neondb_owner:npg_rkz4vYuJ0XlP@ep-green-voice-ai9e4rfz-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

### Application
- **Framework:** Next.js 16
- **Runtime:** Node.js 18+
- **Build:** `npm run build` (next build)
- **Start:** `npm start` (next start)
- **Dev:** `npm run dev` (next dev)

### Hosting
- **Current:** Vercel
- **Target:** AWS Amplify (new app)
- **Domain:** `reillydesignstudio.com` (via Cloudflare)
- **DNS:** Standard setup (@ A record + www CNAME → Vercel, will update to Amplify)

### AWS Account
- **Account ID:** `053677584823`
- **CLI:** Configured and verified ✅
- **Amplify:** Will create new app

### GitHub
- **Repo:** `reillydesignstudio`
- **Auth:** OAuth (to be configured)
- **Branch:** main (or March 12th branch as needed)

### Neon API
- **API Key:** `napi_zdo70hz778qyn3yl0iuukmmu8s27aqot4eacjl6emm0h4g9obah1dber24b07ocn`
- **Status:** Verified working

---

## Next Phase: Phase 1 - Amplify Setup

**Objective:** Create and configure AWS Amplify app

**Tasks:**
1. Create new Amplify app in AWS
2. Connect to GitHub repository
3. Configure build settings (Next.js)
4. Set all environment variables
5. Deploy to preview/staging
6. Verify build succeeds

**Estimated Time:** 1 hour

**Prerequisites Met:**
- ✅ Git commit identified
- ✅ Database connection string captured
- ✅ Environment variables documented
- ✅ AWS credentials verified
- ✅ GitHub OAuth pending (will be requested)

---

## Important Notes

⚠️ **Database Strategy:**
- Fresh schema from March 12th (Prisma migrations)
- Current data will be cleared
- Schema initialized from commit `282e52c`

⚠️ **Critical Credentials:**
- DATABASE_URL: MUST remain exactly the same (Amplify env var)
- SENTRY credentials: Will be re-added to Amplify console
- NEXTAUTH_URL: Will update to production URL after DNS cutover

⚠️ **Rollback Plan:**
- Keep Vercel deployment live during Amplify testing
- Only update DNS after Phase 2 (integration testing) passes
- Can revert DNS to Vercel if issues found

---

## Status

✅ **Inventory Complete**  
⏳ **Ready for Phase 1**  
📋 **All credentials & configs documented**

**Next: Proceed to Phase 1 - Amplify Setup**
