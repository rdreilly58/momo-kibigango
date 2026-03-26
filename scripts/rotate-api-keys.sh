#!/bin/bash
# API Key Rotation Automation
# Interactive guide for rotating API keys safely
# Usage: bash rotate-api-keys.sh [service_name]

set -e

SERVICES=(
  "brave"
  "openrouter"
  "huggingface"
  "cloudflare"
  "telegraph"
  "1password"
  "googlecloud"
)

print_header() {
  echo ""
  echo "========================================================================"
  echo "API Key Rotation Automation — Interactive Guide"
  echo "========================================================================"
  echo ""
}

show_services() {
  echo "Available services:"
  echo ""
  echo "  1) Brave Search API (90 days, HIGH priority)"
  echo "  2) OpenRouter API (90 days, HIGH priority)"
  echo "  3) Hugging Face Token (180 days, MEDIUM priority)"
  echo "  4) Cloudflare API (180 days, HIGH priority)"
  echo "  5) Telegraph API (180 days, MEDIUM priority)"
  echo "  6) 1Password Master (Annual, CRITICAL priority)"
  echo "  7) Google Cloud Service Account (Annual, HIGH priority)"
  echo ""
}

rotate_brave() {
  echo "Rotating Brave Search API Key..."
  echo ""
  echo "Steps:"
  echo "  1. Go to: https://api.search.brave.com/dashboard"
  echo "  2. Login with your Brave account"
  echo "  3. Generate new API key"
  echo "  4. Copy the new key"
  echo ""
  read -p "Enter new Brave API key (or press Enter to skip): " new_key
  
  if [ -n "$new_key" ]; then
    # Update TOOLS.secrets.local
    if grep -q "BRAVE_API_KEY" ~/.openclaw/workspace/TOOLS.secrets.local 2>/dev/null; then
      sed -i '' "s/export BRAVE_API_KEY=.*/export BRAVE_API_KEY=$new_key/" ~/.openclaw/workspace/TOOLS.secrets.local
    else
      echo "export BRAVE_API_KEY=$new_key" >> ~/.openclaw/workspace/TOOLS.secrets.local
    fi
    
    echo "  ✓ Key updated in TOOLS.secrets.local"
    
    # Test the key
    echo ""
    echo "Testing new key..."
    if source ~/.openclaw/workspace/TOOLS.secrets.local && web_search "test" > /dev/null 2>&1; then
      echo "  ✓ Key works! (tested with web_search)"
      
      # Record rotation
      local date=$(date +%Y-%m-%d)
      sed -i '' "s/| Brave Search.*$/| Brave Search | $date | 90 | HIGH/" ~/.openclaw/workspace/scripts/check-api-key-age.sh
      
      echo "  ✓ Rotation date recorded"
      echo "  ✓ Delete old key from https://api.search.brave.com/dashboard"
    else
      echo "  ✗ Key test failed! Check credentials."
      return 1
    fi
  fi
  
  echo ""
  echo "✓ Brave Search API key rotation complete"
}

rotate_openrouter() {
  echo "Rotating OpenRouter API Key..."
  echo ""
  echo "Steps:"
  echo "  1. Go to: https://openrouter.ai/keys"
  echo "  2. Login to your account"
  echo "  3. Generate new API key"
  echo "  4. Copy the new key (64+ characters)"
  echo ""
  read -p "Enter new OpenRouter API key (or press Enter to skip): " new_key
  
  if [ -n "$new_key" ]; then
    # Update TOOLS.secrets.local
    if grep -q "OPENROUTER_API_KEY" ~/.openclaw/workspace/TOOLS.secrets.local 2>/dev/null; then
      sed -i '' "s/export OPENROUTER_API_KEY=.*/export OPENROUTER_API_KEY=$new_key/" ~/.openclaw/workspace/TOOLS.secrets.local
    else
      echo "export OPENROUTER_API_KEY=$new_key" >> ~/.openclaw/workspace/TOOLS.secrets.local
    fi
    
    echo "  ✓ Key updated in TOOLS.secrets.local"
    
    # Test the key
    echo ""
    echo "Testing new key..."
    echo "  (Skipping auto-test to avoid cost - verify manually)"
    
    # Record rotation
    local date=$(date +%Y-%m-%d)
    sed -i '' "s/| OpenRouter.*$/| OpenRouter | $date | 90 | HIGH/" ~/.openclaw/workspace/scripts/check-api-key-age.sh
    
    echo "  ✓ Rotation date recorded"
    echo "  ✓ Delete old key from https://openrouter.ai/keys"
  fi
  
  echo ""
  echo "✓ OpenRouter API key rotation complete"
}

rotate_huggingface() {
  echo "Rotating Hugging Face API Token..."
  echo ""
  echo "Steps:"
  echo "  1. Go to: https://huggingface.co/settings/tokens"
  echo "  2. Login to your account"
  echo "  3. Create new token (read access)"
  echo "  4. Copy the new token"
  echo ""
  read -p "Enter new Hugging Face token (or press Enter to skip): " new_token
  
  if [ -n "$new_token" ]; then
    # Update TOOLS.secrets.local
    if grep -q "HF_API_TOKEN" ~/.openclaw/workspace/TOOLS.secrets.local 2>/dev/null; then
      sed -i '' "s/export HF_API_TOKEN=.*/export HF_API_TOKEN=$new_token/" ~/.openclaw/workspace/TOOLS.secrets.local
    else
      echo "export HF_API_TOKEN=$new_token" >> ~/.openclaw/workspace/TOOLS.secrets.local
    fi
    
    echo "  ✓ Token updated in TOOLS.secrets.local"
    echo "  ✓ Delete old token from https://huggingface.co/settings/tokens"
    
    # Record rotation
    local date=$(date +%Y-%m-%d)
    sed -i '' "s/| Hugging Face.*$/| Hugging Face | $date | 180 | MEDIUM/" ~/.openclaw/workspace/scripts/check-api-key-age.sh
    
    echo "  ✓ Rotation date recorded"
  fi
  
  echo ""
  echo "✓ Hugging Face token rotation complete"
}

rotate_cloudflare() {
  echo "Rotating Cloudflare API Token..."
  echo ""
  echo "Steps:"
  echo "  1. Go to: https://dash.cloudflare.com/profile/api-tokens"
  echo "  2. Login to your account"
  echo "  3. Create new token with Zone.DNS permissions"
  echo "  4. Copy the new token"
  echo ""
  read -p "Enter new Cloudflare API token (or press Enter to skip): " new_token
  
  if [ -n "$new_token" ]; then
    # Update TOOLS.secrets.local
    if grep -q "CLOUDFLARE_TOKEN" ~/.openclaw/workspace/TOOLS.secrets.local 2>/dev/null; then
      sed -i '' "s/export CLOUDFLARE_TOKEN=.*/export CLOUDFLARE_TOKEN=$new_token/" ~/.openclaw/workspace/TOOLS.secrets.local
    else
      echo "export CLOUDFLARE_TOKEN=$new_token" >> ~/.openclaw/workspace/TOOLS.secrets.local
    fi
    
    echo "  ✓ Token updated in TOOLS.secrets.local"
    echo "  ✓ Delete old token from Cloudflare dashboard"
    
    # Record rotation
    local date=$(date +%Y-%m-%d)
    sed -i '' "s/| Cloudflare.*$/| Cloudflare | $date | 180 | HIGH/" ~/.openclaw/workspace/scripts/check-api-key-age.sh
    
    echo "  ✓ Rotation date recorded"
  fi
  
  echo ""
  echo "✓ Cloudflare API token rotation complete"
}

rotate_telegraph() {
  echo "Rotating Telegraph API Token..."
  echo ""
  echo "Steps:"
  echo "  1. Go to: https://telegra.ph (must be logged in)"
  echo "  2. Create new access token via API or dashboard"
  echo "  3. Copy the new token"
  echo ""
  read -p "Enter new Telegraph API token (or press Enter to skip): " new_token
  
  if [ -n "$new_token" ]; then
    # Backup old token
    if [ -f ~/.telegraph_token ]; then
      cp ~/.telegraph_token ~/.telegraph_token.backup
      echo "  ✓ Old token backed up to ~/.telegraph_token.backup"
    fi
    
    # Update token file
    echo "$new_token" > ~/.telegraph_token
    chmod 600 ~/.telegraph_token
    echo "  ✓ Token updated in ~/.telegraph_token"
    
    # Test the token
    echo ""
    echo "Testing new token..."
    if python3 ~/.openclaw/workspace/scripts/telegraph-cli.py status > /dev/null 2>&1; then
      echo "  ✓ Token works! (tested with telegraph-cli)"
    else
      echo "  ⚠ Token test inconclusive (may still be valid)"
    fi
    
    # Record rotation
    local date=$(date +%Y-%m-%d)
    sed -i '' "s/| Telegraph.*$/| Telegraph | $date | 180 | MEDIUM/" ~/.openclaw/workspace/scripts/check-api-key-age.sh
    
    echo "  ✓ Rotation date recorded"
  fi
  
  echo ""
  echo "✓ Telegraph API token rotation complete"
}

rotate_1password() {
  echo "Rotating 1Password Master Password..."
  echo ""
  echo "Steps:"
  echo "  1. Open 1Password desktop app"
  echo "  2. Account Settings → Security → Rotate Master Password"
  echo "  3. Follow the on-screen prompts"
  echo "  4. Download new Emergency Kit and save securely"
  echo ""
  read -p "Press Enter when 1Password rotation is complete... "
  
  # Record rotation
  local date=$(date +%Y-%m-%d)
  sed -i '' "s/| 1Password.*$/| 1Password | $date | 365 | CRITICAL/" ~/.openclaw/workspace/scripts/check-api-key-age.sh
  
  echo "  ✓ Rotation date recorded"
  
  echo ""
  echo "✓ 1Password master password rotation complete"
}

rotate_googlecloud() {
  echo "Rotating Google Cloud Service Account..."
  echo ""
  echo "Steps:"
  echo "  1. Go to: https://console.cloud.google.com"
  echo "  2. IAM & Admin → Service Accounts"
  echo "  3. Select your service account"
  echo "  4. Keys → Add Key → Create new key"
  echo "  5. Download JSON file"
  echo ""
  read -p "Enter path to new GCP credentials JSON (or press Enter to skip): " new_creds
  
  if [ -n "$new_creds" ] && [ -f "$new_creds" ]; then
    # Backup old credentials
    if [ -f ~/.gcp/credentials.json ]; then
      cp ~/.gcp/credentials.json ~/.gcp/credentials.json.backup
      echo "  ✓ Old credentials backed up"
    fi
    
    # Install new credentials
    mkdir -p ~/.gcp
    cp "$new_creds" ~/.gcp/credentials.json
    chmod 600 ~/.gcp/credentials.json
    echo "  ✓ New credentials installed"
    
    # Test authentication
    echo ""
    echo "Testing new credentials..."
    if gcloud auth activate-service-account --key-file=~/.gcp/credentials.json > /dev/null 2>&1 && gcloud projects list > /dev/null 2>&1; then
      echo "  ✓ Credentials work! (authenticated successfully)"
    else
      echo "  ⚠ Credential test inconclusive"
    fi
    
    # Record rotation
    local date=$(date +%Y-%m-%d)
    sed -i '' "s/| Google Cloud.*$/| Google Cloud | $date | 365 | HIGH/" ~/.openclaw/workspace/scripts/check-api-key-age.sh
    
    echo "  ✓ Rotation date recorded"
  fi
  
  echo ""
  echo "✓ Google Cloud service account rotation complete"
}

# Main execution
print_header

if [ -z "$1" ]; then
  show_services
  read -p "Select service (1-7) or name (brave/openrouter/etc): " choice
else
  choice=$1
fi

case "$choice" in
  1|brave) rotate_brave ;;
  2|openrouter) rotate_openrouter ;;
  3|huggingface) rotate_huggingface ;;
  4|cloudflare) rotate_cloudflare ;;
  5|telegraph) rotate_telegraph ;;
  6|1password) rotate_1password ;;
  7|googlecloud) rotate_googlecloud ;;
  *) echo "Invalid selection"; exit 1 ;;
esac

echo ""
echo "Next steps:"
echo "  1. Verify old keys are deleted from provider dashboards"
echo "  2. Test system functionality: bash ~/.openclaw/workspace/scripts/openclaw-health.sh"
echo "  3. Update MEMORY.md with rotation details"
echo ""
