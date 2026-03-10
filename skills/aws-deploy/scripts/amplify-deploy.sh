#!/bin/bash
# amplify-deploy.sh — Build and deploy to AWS Amplify
#
# Usage:
#   amplify-deploy.sh [REPO_PATH]           # Deploy current/specified repo
#   amplify-deploy.sh --build-only          # Build without deploying
#   amplify-deploy.sh --status              # Check deployment status
#   amplify-deploy.sh --logs [NUM_LINES]    # Show deployment logs
#   amplify-deploy.sh --help                # Show this help

set -euo pipefail

REPO_PATH="${1:-.}"
BUILD_ONLY=false
SHOW_STATUS=false
SHOW_LOGS=false
LOG_LINES=50

while [[ $# -gt 0 ]]; do
  case $1 in
    --build-only)
      BUILD_ONLY=true
      shift
      ;;
    --status)
      SHOW_STATUS=true
      shift
      ;;
    --logs)
      SHOW_LOGS=true
      LOG_LINES="${2:-50}"
      shift 2
      ;;
    -h|--help)
      head -15 "$0" | tail -12
      exit 0
      ;;
    *)
      REPO_PATH="$1"
      shift
      ;;
  esac
done

# Verify repo exists
if [[ ! -f "$REPO_PATH/package.json" ]]; then
  echo "[amplify] Error: No package.json found in $REPO_PATH" >&2
  exit 1
fi

cd "$REPO_PATH"

if [[ "$SHOW_STATUS" = true ]]; then
  echo "[amplify] Checking deployment status..."
  amplify status 2>/dev/null || echo "[amplify] Not an Amplify project (run amplify init first)"
  exit 0
fi

if [[ "$SHOW_LOGS" = true ]]; then
  echo "[amplify] Fetching last $LOG_LINES deployment logs..."
  amplify logs --follow 2>/dev/null | head -n "$LOG_LINES"
  exit 0
fi

echo "[amplify] Starting build process..."
echo "[amplify] Repository: $(pwd)"
echo "[amplify] Node: $(node --version)"
echo "[amplify] npm: $(npm --version)"

# Install dependencies
echo "[amplify] Installing dependencies..."
npm ci

# Generate Prisma client (if needed)
if [[ -f "prisma/schema.prisma" ]]; then
  echo "[amplify] Generating Prisma client..."
  npx prisma generate
fi

# Build
echo "[amplify] Building Next.js application..."
npm run build

if [[ "$BUILD_ONLY" = true ]]; then
  echo "[amplify] ✓ Build complete (--build-only, not deploying)"
  ls -lh .next/
  exit 0
fi

# Deploy to Amplify
echo "[amplify] Deploying to AWS Amplify..."
if ! amplify --version > /dev/null 2>&1; then
  echo "[amplify] Error: AWS Amplify CLI not found" >&2
  echo "[amplify] Install: npm install -g @aws-amplify/cli" >&2
  exit 1
fi

# Check if project is initialized
if [[ ! -d "amplify" ]]; then
  echo "[amplify] Amplify not initialized. Run: amplify init" >&2
  exit 1
fi

amplify publish --yes

echo "[amplify] ✓ Deployment complete"
echo "[amplify] Check status: amplify-deploy.sh --status"
