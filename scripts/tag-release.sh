#!/usr/bin/env bash
# tag-release.sh — Tag a release after test suite passes
# Usage: bash scripts/tag-release.sh [patch|minor|major] "description"
#
# Examples:
#   bash scripts/tag-release.sh patch "fix backup encryption key rotation"
#   bash scripts/tag-release.sh minor "add S3 off-site backups"
#   bash scripts/tag-release.sh major "complete backup hardening overhaul"

set -euo pipefail
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

BUMP="${1:-patch}"
DESCRIPTION="${2:-}"

if [[ -z "$DESCRIPTION" ]]; then
  echo "Usage: $0 [patch|minor|major] \"description\"" >&2
  exit 1
fi

case "$BUMP" in
  patch|minor|major) ;;
  *) echo "Error: bump must be patch, minor, or major" >&2; exit 1 ;;
esac

# ── Get current version ────────────────────────────────────────────────────────
CURRENT_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
echo "Current tag: $CURRENT_TAG"

# Strip leading 'v'
VERSION="${CURRENT_TAG#v}"
MAJOR=$(echo "$VERSION" | cut -d. -f1)
MINOR=$(echo "$VERSION" | cut -d. -f2)
PATCH=$(echo "$VERSION" | cut -d. -f3)

# ── Bump version ───────────────────────────────────────────────────────────────
case "$BUMP" in
  patch) PATCH=$((PATCH + 1)) ;;
  minor) MINOR=$((MINOR + 1)); PATCH=0 ;;
  major) MAJOR=$((MAJOR + 1)); MINOR=0; PATCH=0 ;;
esac

NEW_TAG="v${MAJOR}.${MINOR}.${PATCH}"
echo "New tag: $NEW_TAG"

# ── Confirm ────────────────────────────────────────────────────────────────────
echo ""
echo "Creating annotated tag: $NEW_TAG"
echo "  Message: $NEW_TAG: $DESCRIPTION"
read -r -p "Proceed? [y/N] " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
  echo "Aborted."
  exit 0
fi

# ── Create and push tag ────────────────────────────────────────────────────────
git tag -a "$NEW_TAG" -m "$NEW_TAG: $DESCRIPTION"
git push origin "$NEW_TAG"

echo ""
echo "✅ Tagged and pushed: $NEW_TAG"
echo "   Message: $NEW_TAG: $DESCRIPTION"
