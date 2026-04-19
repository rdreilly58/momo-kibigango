# Vercel Configuration Fixes — Applied March 18, 2026

## Problems Found & Fixed

### 1. ✅ Missing `vercel.json`
**Problem:** No explicit Vercel configuration file  
**Impact:** Vercel uses defaults, which may not match Next.js app requirements  
**Fix:** Created `vercel.json` with:
- Build command: `next build`
- Output directory: `.next`
- Environment variables for production
- Cache-Control headers for API routes

### 2. ✅ Broken `.vercelignore`
**Problem:** `.vercelignore` contained only a timestamp comment, not file patterns  
**Impact:** Vercel uploaded unnecessary files (node_modules, docs, legal, etc.)  
**Fix:** Replaced with proper ignore patterns:
```
.git
.gitignore
README.md
docs
legal
.env.local
.env.*.local
*.log
node_modules
.next
.vercel
amplify
```

### 3. ⚠️ Environment Variables Needed in Vercel Dashboard
**Required (for full functionality):**
- `DATABASE_URL` — PostgreSQL connection string
- `STRIPE_SECRET_KEY` — Stripe API key
- `STRIPE_WEBHOOK_SECRET` — Stripe webhook signing secret
- `GOOGLE_CLIENT_ID` — OAuth for auth
- `GOOGLE_CLIENT_SECRET` — OAuth for auth
- `S3_REGION`, `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY`, `S3_BUCKET` — AWS S3
- `SMTP_HOST`, `SMTP_USER`, `SMTP_PASS` — Email

**Optional (for analytics):**
- `NEXT_PUBLIC_GA_MEASUREMENT_ID` — Google Analytics
- `NEXT_PUBLIC_CF_BEACON_TOKEN` — Cloudflare beacon

## Commits Applied

1. **96ff127** — 🔄 Test GitHub-to-Vercel webhook (manual test)
2. **bd5e667** — 🔧 Fix Vercel configuration (vercel.json + .vercelignore)

## Next Steps for Bob

1. **Go to Vercel Dashboard:**
   - https://vercel.com → ReillyDesignStudio project
   - Settings → Environment Variables

2. **Add missing environment variables:**
   - At minimum: `DATABASE_URL`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`
   - Check existing secrets from previous deployment if available

3. **Trigger a new deployment:**
   - Latest commit just pushed should trigger automatically
   - Check **Deployments** tab to monitor build

4. **Verify deployment:**
   - Once green checkmark appears, test: `reillydesignstudio.com/blog/speculative-decoding`
   - Should load the blog post without 404

## Summary

**What was broken:** Vercel config was incomplete and `.vercelignore` was corrupted  
**What's fixed:** Proper `vercel.json` created, `.vercelignore` cleaned  
**What still needs:** Environment variables in Vercel dashboard  

The build should now work correctly on Vercel once environment variables are set.
