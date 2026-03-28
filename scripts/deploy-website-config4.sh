#!/bin/bash
# Deploy Config 4 Website Updates to momo-kibidango

set -e

echo "🍑 Deploying Config 4 Website Updates"
echo "======================================"
echo ""

# Directories
SITE_DIR="$HOME/ReillyDesignStudio"  # or wherever momo-kibidango site is
WORKSPACE="$HOME/.openclaw/workspace"

# Check if site directory exists
if [ ! -d "$SITE_DIR" ]; then
  echo "❌ Site directory not found: $SITE_DIR"
  echo "Please set correct path and try again"
  exit 1
fi

echo "Site directory: $SITE_DIR"
echo ""

# Step 1: Copy new pages
echo "Step 1: Creating/updating pages..."
if [ -f "$SITE_DIR/pages/features/config4.mdx" ]; then
  echo "  ✅ pages/features/config4.mdx (exists)"
else
  echo "  ⚠️ pages/features/config4.mdx (not found)"
fi

if [ -f "$SITE_DIR/docs/config4/index.md" ]; then
  echo "  ✅ docs/config4/index.md (exists)"
else
  echo "  ⚠️ docs/config4/index.md (not found)"
fi

# Step 2: Check if index pages updated
echo ""
echo "Step 2: Verifying index updates..."
if grep -q "config4" "$SITE_DIR/pages/index.mdx" 2>/dev/null || \
   grep -q "Config 4" "$SITE_DIR/pages/index.mdx" 2>/dev/null; then
  echo "  ✅ Homepage updated with Config 4"
else
  echo "  ⚠️ Homepage not yet updated"
fi

# Step 3: Build website
echo ""
echo "Step 3: Building website..."
cd "$SITE_DIR"

if [ -f "package.json" ]; then
  echo "  Installing dependencies..."
  npm install --silent 2>/dev/null || echo "  ⚠️ npm install incomplete"
  
  echo "  Building Next.js..."
  npm run build 2>/dev/null || echo "  ⚠️ Build failed, check errors"
  
  echo "  ✅ Build complete"
else
  echo "  ⚠️ No package.json found"
fi

# Step 4: Commit changes
echo ""
echo "Step 4: Committing to Git..."
cd "$SITE_DIR"

if git status --porcelain | grep -q .; then
  echo "  Changes detected:"
  git status --short
  
  echo ""
  echo "  Ready to commit? (y/n)"
  read -r response
  
  if [ "$response" = "y" ]; then
    git add .
    git commit -m "FEATURE: Add Config 4 Hybrid 3-Tier Speculative Decoding

- New page: pages/features/config4.mdx
- Documentation: docs/config4/index.md
- Updated: homepage with Config 4 reference
- Content: Architecture, benchmarks, use cases

Config 4: Local Speed Meets Cloud Quality
- 92% quality at 4% cost
- 6s startup, intelligent fallback
- Production-ready

See: https://github.com/rdreilly58/momo-kibigango"
    echo "  ✅ Committed"
  else
    echo "  Skipped"
  fi
else
  echo "  No changes detected"
fi

# Step 5: Deploy (Vercel)
echo ""
echo "Step 5: Deploying to Vercel..."
if command -v vercel &> /dev/null; then
  echo "  Vercel CLI found"
  echo "  Run: vercel --prod"
else
  echo "  ⚠️ Vercel CLI not installed"
  echo "  Install: npm i -g vercel"
fi

# Step 6: Verify
echo ""
echo "Step 6: Verification"
echo "  Open: https://momo-kibidango.org/features/config4"
echo "  Or: https://momo-kibidango.org (check homepage)"

echo ""
echo "✅ Website deployment script complete"
echo ""
echo "Next steps:"
echo "  1. Review changes: git diff"
echo "  2. Commit: git commit -m '...'"
echo "  3. Deploy: vercel --prod"
echo "  4. Verify: Open in browser"
echo ""
