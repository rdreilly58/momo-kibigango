#!/bin/bash
# setup-ga4.sh — Configure GA4 Analytics access
#
# Usage:
#   bash setup-ga4.sh [PROPERTY_ID] [SERVICE_ACCOUNT_JSON_PATH]

set -euo pipefail

PROPERTY_ID="${1:-}"
SERVICE_ACCOUNT_PATH="${2:-}"

if [[ -z "$PROPERTY_ID" ]]; then
  echo "Usage: setup-ga4.sh <PROPERTY_ID> [SERVICE_ACCOUNT_JSON_PATH]"
  echo ""
  echo "Get your GA4 Property ID:"
  echo "  1. Go to: https://analytics.google.com"
  echo "  2. Select your property (ReillyDesignStudio)"
  echo "  3. Admin → Property Settings"
  echo "  4. Copy the Property ID"
  echo ""
  exit 1
fi

# Default path for service account key
SERVICE_ACCOUNT_PATH="${SERVICE_ACCOUNT_PATH:-$HOME/.openclaw/workspace/secrets/ga4-service-account.json}"

if [[ ! -f "$SERVICE_ACCOUNT_PATH" ]]; then
  echo "[ga4] ⚠️  Service account key not found: $SERVICE_ACCOUNT_PATH"
  echo ""
  echo "Steps to create:"
  echo "  1. Go to: https://console.cloud.google.com/iam-admin/serviceaccounts"
  echo "  2. Create a service account"
  echo "  3. Grant role: Viewer"
  echo "  4. Create JSON key"
  echo "  5. Download and save to: $SERVICE_ACCOUNT_PATH"
  echo ""
  exit 1
fi

# Verify JSON is valid
if ! jq empty "$SERVICE_ACCOUNT_PATH" 2>/dev/null; then
  echo "[ga4] ✗ Invalid JSON in service account file" >&2
  exit 1
fi

# Test API access
echo "[ga4] Testing API access..."

export GOOGLE_APPLICATION_CREDENTIALS="$SERVICE_ACCOUNT_PATH"

# Try a simple query using gog
if command -v gog &> /dev/null; then
  echo "[ga4] Using gog CLI..."
  
  # Check if analytics commands are available
  if gog analytics --help &>/dev/null; then
    gog analytics report \
      --property-id="$PROPERTY_ID" \
      --date-ranges="today" \
      --dimensions="date" \
      --metrics="sessions" \
      --plain || {
        echo "[ga4] ✗ API call failed. Check Property ID and permissions."
        exit 1
      }
    echo "[ga4] ✓ API access verified!"
  else
    echo "[ga4] ⚠️  gog analytics not available. Install gog and enable analytics command."
  fi
else
  echo "[ga4] ⚠️  gog CLI not found. Install gog for easy analytics queries."
fi

# Save config
mkdir -p ~/.openclaw/workspace/config
cat > ~/.openclaw/workspace/config/ga4.env << EOF
# GA4 Analytics Configuration
export GA4_PROPERTY_ID="$PROPERTY_ID"
export GOOGLE_APPLICATION_CREDENTIALS="$SERVICE_ACCOUNT_PATH"
EOF

echo "[ga4] ✓ Configuration saved to: ~/.openclaw/workspace/config/ga4.env"
echo ""
echo "To use GA4 commands, run:"
echo "  source ~/.openclaw/workspace/config/ga4.env"
echo ""
echo "Then:"
echo "  gog analytics report --property-id=\$GA4_PROPERTY_ID ..."
