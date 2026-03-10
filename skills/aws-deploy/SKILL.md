---
name: aws-deploy
description: Build and deploy Next.js/React applications to AWS Amplify. Use when deploying ReillyDesignStudio or other Amplify-configured projects, checking deployment status, or viewing build logs.
---

# AWS Amplify Deploy

Build and deploy applications to AWS Amplify.

**Prerequisites:**
- AWS CLI configured (✓ already set up)
- AWS Amplify CLI installed (✓ installed)
- Amplify project initialized (`amplify init`)
- IAM permissions for Amplify, S3, CloudFront

## Quick Deploy

```bash
# Deploy ReillyDesignStudio
bash {baseDir}/scripts/amplify-deploy.sh ~/reillydesignstudio

# Build only (no deploy)
bash {baseDir}/scripts/amplify-deploy.sh ~/reillydesignstudio --build-only

# Check deployment status
bash {baseDir}/scripts/amplify-deploy.sh ~/reillydesignstudio --status

# View deployment logs
bash {baseDir}/scripts/amplify-deploy.sh ~/reillydesignstudio --logs 100
```

## What It Does

1. **Validates** package.json exists
2. **Installs** dependencies (`npm ci`)
3. **Generates** Prisma client (if needed)
4. **Builds** Next.js application
5. **Publishes** to AWS Amplify via `amplify publish`

## Environment Variables

The `amplify.yml` file defines these build-time secrets (set in Amplify Console):

```
DATABASE_URL          # Prisma database connection
NEXTAUTH_SECRET       # NextAuth.js secret
NEXTAUTH_URL          # NextAuth.js callback URL
NEXT_PUBLIC_SITE_URL  # Public site URL
STRIPE_SECRET_KEY     # Stripe API key
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY
STRIPE_WEBHOOK_SECRET # Stripe webhook secret
GOOGLE_CLIENT_ID      # Google OAuth
GOOGLE_CLIENT_SECRET
SMTP_PASS             # Email SMTP password
NEXT_PUBLIC_GA_MEASUREMENT_ID  # Google Analytics
NEXT_PUBLIC_CF_BEACON_TOKEN    # Cloudflare
```

## Setup (First Time)

If `amplify init` hasn't been run:

```bash
cd ~/reillydesignstudio
amplify init
# Select AWS region, environment name, etc.

# Then deploy:
bash {baseDir}/scripts/amplify-deploy.sh ~/reillydesignstudio
```

## Manual Amplify Commands

```bash
# Initialize a new Amplify project
cd ~/reillydesignstudio
amplify init

# Add authentication, API, hosting, etc.
amplify add auth
amplify add api
amplify add hosting

# Push local configuration to AWS
amplify push

# Deploy (frontend only)
amplify publish

# View project status
amplify status

# View console
amplify console
```

## AWS Account

- **Account ID:** 053677584823
- **Region:** (check with `aws configure get region`)
- **CLI Version:** $(amplify --version)

## Troubleshooting

```bash
# Check AWS credentials
aws sts get-caller-identity

# Verify Amplify setup
amplify status

# View detailed logs
amplify logs --follow

# Rebuild from scratch
rm -rf node_modules .next
npm ci
npm run build
```
