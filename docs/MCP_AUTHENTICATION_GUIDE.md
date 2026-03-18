# MCP Authentication Guide

This guide covers how to set up and manage authentication for MCP servers in OpenClaw.

## Credential Storage Architecture

```
~/.mcporter/
├── mcporter.json          # Main config (references oauth/)
├── oauth/
│   ├── gmail.json         # Google OAuth token
│   ├── github.token       # GitHub PAT
│   ├── slack.token        # Slack app/bot tokens
│   ├── aws-creds.json     # AWS credentials
│   └── bigquery-sa.json   # BigQuery service account
└── secure/
    ├── 1password.sh       # 1Password credential retrieval script
    └── credential-sync.sh # Sync credentials from 1Password
```

## OAuth Flow Examples

### Gmail OAuth Setup

```bash
#!/bin/bash
# setup-gmail-oauth.sh

# 1. Create OAuth consent app in Google Cloud Console
# - App type: Desktop application
# - Scopes: gmail.modify, gmail.readonly, gmail.send

# 2. Download credentials JSON from console
GOOGLE_CLIENT_ID="YOUR_CLIENT_ID.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="YOUR_CLIENT_SECRET"

# 3. Authenticate
gog login rdreilly2010@gmail.com

# 4. Extract token for MCP
mkdir -p ~/.mcporter/oauth
cp ~/.config/gog/oauth-token.json ~/.mcporter/oauth/gmail.json

# 5. Verify
mcporter auth gmail --test
```

### GitHub Personal Access Token

```bash
#!/bin/bash
# setup-github-mcp.sh

# 1. Create PAT in GitHub Settings > Developer settings > Personal access tokens
# 2. Scopes needed:
#    - repo (full control)
#    - read:user
#    - read:org
#    - gist

# 3. Store securely
echo "gho_YOUR_PAT_HERE" > ~/.mcporter/oauth/github.token

# 4. Configure in mcporter
mcporter config add github \
  --command "npx -y @modelcontextprotocol/server-github" \
  --env GITHUB_PERSONAL_ACCESS_TOKEN="$(cat ~/.mcporter/oauth/github.token)"

# 5. Verify
mcporter call github.list_repos --json | head -5
```

### AWS Credentials

```bash
#!/bin/bash
# setup-aws-mcp.sh

# 1. Use existing AWS profile or create new one
aws configure --profile openclaw

# 2. Store credentials for MCP
cat ~/.aws/credentials | grep -A 2 "^\[openclaw\]" > ~/.mcporter/oauth/aws.ini

# 3. Configure MCP
mcporter config add aws \
  --command "npx -y @modelcontextprotocol/server-aws" \
  --env AWS_PROFILE=openclaw \
  --env AWS_CONFIG_FILE=~/.aws/config

# 4. Test
mcporter call aws.list_instances --json
```

### Slack App Integration

```bash
#!/bin/bash
# setup-slack-mcp.sh

# 1. Create Slack App in https://api.slack.com/apps
# 2. Enable required scopes:
#    - channels:read, channels:history
#    - chat:write, chat:read
#    - users:read, users:read.email
#    - files:read

# 3. Generate tokens
# Bot Token Scopes: Create bot user with above scopes
# App-level token: For socket mode (recommended)

# 4. Store tokens
mkdir -p ~/.mcporter/oauth/slack
echo "xoxb-YOUR_BOT_TOKEN" > ~/.mcporter/oauth/slack/bot.token
echo "xapp-YOUR_APP_TOKEN" > ~/.mcporter/oauth/slack/app.token

# 5. Configure
mcporter config add slack \
  --command "npx -y @modelcontextprotocol/server-slack" \
  --env SLACK_BOT_TOKEN="$(cat ~/.mcporter/oauth/slack/bot.token)" \
  --env SLACK_APP_TOKEN="$(cat ~/.mcporter/oauth/slack/app.token)"
```

## Token Refresh Strategies

### Automatic Refresh Script

```bash
#!/bin/bash
# scripts/mcp-token-refresh.sh

set -e

OAUTH_DIR=~/.mcporter/oauth
LOG_FILE=~/.openclaw/logs/mcp-token-refresh.log

log() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

refresh_gmail_token() {
  log "Refreshing Gmail token..."
  if gog auth refresh 2>/dev/null; then
    cp ~/.config/gog/oauth-token.json "$OAUTH_DIR/gmail.json"
    log "✓ Gmail token refreshed"
  else
    log "✗ Gmail token refresh failed"
    return 1
  fi
}

refresh_github_token() {
  log "Checking GitHub token validity..."
  if mcporter call github.list_user_repos limit:1 &>/dev/null; then
    log "✓ GitHub token valid"
  else
    log "⚠ GitHub token may have expired"
    echo "Please refresh GitHub PAT manually:"
    echo "1. Go to https://github.com/settings/tokens"
    echo "2. Generate new token"
    echo "3. Run: echo 'TOKEN' > ~/.mcporter/oauth/github.token"
  fi
}

refresh_aws_credentials() {
  log "Checking AWS credentials..."
  if aws sts get-caller-identity --profile openclaw &>/dev/null; then
    log "✓ AWS credentials valid"
  else
    log "⚠ AWS credentials expired or invalid"
  fi
}

# Run all refreshes
refresh_gmail_token || true
refresh_github_token || true
refresh_aws_credentials || true

log "Token refresh cycle complete"
```

### Cron Job Setup

```bash
# Install refresh script as cron job
# Runs daily at 2 AM to refresh tokens

# 1. Make script executable
chmod +x ~/.openclaw/workspace/scripts/mcp-token-refresh.sh

# 2. Create cron entry
crontab -e

# Add this line:
# 0 2 * * * /Users/rreilly/.openclaw/workspace/scripts/mcp-token-refresh.sh

# 3. Verify
crontab -l
```

## 1Password Integration

### Automated Credential Injection

```bash
#!/bin/bash
# scripts/mcp-inject-from-1password.sh

# This script retrieves credentials from 1Password and injects them
# into MCP server environment variables at startup

set -e

VAULT="OpenClaw"

# Gmail OAuth Token
export GMAIL_OAUTH=$(op read "op://$VAULT/MCP Gmail OAuth Token/password" 2>/dev/null || echo "")

# GitHub PAT
export GITHUB_PERSONAL_ACCESS_TOKEN=$(op read "op://$VAULT/MCP GitHub PAT/password" 2>/dev/null || echo "")

# AWS Credentials
export AWS_ACCESS_KEY_ID=$(op read "op://$VAULT/AWS OpenClaw/access_key_id" 2>/dev/null || echo "")
export AWS_SECRET_ACCESS_KEY=$(op read "op://$VAULT/AWS OpenClaw/secret_access_key" 2>/dev/null || echo "")

# Slack Tokens
export SLACK_BOT_TOKEN=$(op read "op://$VAULT/Slack MCP Bot/token" 2>/dev/null || echo "")
export SLACK_APP_TOKEN=$(op read "op://$VAULT/Slack MCP App/token" 2>/dev/null || echo "")

# Verify 1Password is authenticated
if ! op user get --me &>/dev/null; then
  echo "Error: 1Password CLI not authenticated"
  exit 1
fi

echo "✓ Credentials loaded from 1Password"
echo "Ready to start MCP servers with injected credentials"

# Start mcporter daemon with these credentials
exec mcporter daemon start
```

### 1Password Setup

```bash
#!/bin/bash
# setup-1password-mcp.sh

VAULT="OpenClaw"

# Create vault if needed
op vault create "$VAULT" 2>/dev/null || true

# Create MCP credential items
op item create \
  --vault="$VAULT" \
  --category="API Credential" \
  --title="MCP Gmail OAuth Token" \
  --url="https://mail.google.com" \
  gmail_token[password]="PASTE_TOKEN_HERE"

op item create \
  --vault="$VAULT" \
  --category="API Credential" \
  --title="MCP GitHub PAT" \
  --url="https://github.com/settings/tokens" \
  pat[password]="gho_PASTE_TOKEN_HERE"

op item create \
  --vault="$VAULT" \
  --category="API Credential" \
  --title="Slack MCP Bot Token" \
  --url="https://api.slack.com/apps" \
  bot_token[password]="xoxb_PASTE_TOKEN_HERE" \
  app_token[password]="xapp_PASTE_TOKEN_HERE"

op item create \
  --vault="$VAULT" \
  --category="Login" \
  --title="AWS OpenClaw Profile" \
  --url="https://console.aws.amazon.com" \
  username="PROFILE_NAME" \
  access_key_id[password]="AKIAIOSFODNN7EXAMPLE" \
  secret_access_key[password]="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

echo "✓ MCP credentials stored in 1Password vault: $VAULT"
```

## Security Best Practices

### 1. Credential Isolation

```json
// mcporter.json - Never commit this file
{
  "mcpServers": {
    "gmail": {
      "env": {
        // Reference file, don't embed token
        "GMAIL_OAUTH_PATH": "${HOME}/.mcporter/oauth/gmail.json"
      }
    }
  }
}
```

### 2. File Permissions

```bash
#!/bin/bash
# Secure credential files with restrictive permissions

chmod 600 ~/.mcporter/oauth/*     # Owner read/write only
chmod 700 ~/.mcporter/oauth       # Owner access only
chmod 600 ~/.mcporter/mcporter.json

# Verify
ls -la ~/.mcporter/oauth/
# Should show: -rw------- (600)
```

### 3. Audit Logging

```bash
#!/bin/bash
# scripts/mcp-credential-audit.sh

AUDIT_LOG=~/.openclaw/logs/mcp-credential-audit.log

# Log all credential access
while true; do
  # Monitor file access
  fs_usage -w 1 ~/.mcporter/oauth 2>/dev/null | \
  grep -v "^CACHE" | \
  while read line; do
    echo "[$(date)] $line" >> "$AUDIT_LOG"
  done
  
  sleep 60
done
```

## Troubleshooting Authentication

### Testing Credentials

```bash
#!/bin/bash
# test-mcp-credentials.sh

test_service() {
  local service=$1
  local test_tool=$2
  
  echo "Testing $service..."
  if mcporter call "$service.$test_tool" 2>&1 | grep -q "error\|Error"; then
    echo "✗ $service: Authentication failed"
    return 1
  else
    echo "✓ $service: Authentication successful"
    return 0
  fi
}

# Test all services
test_service "gmail" "search" "--args '{\"query\":\"test\",\"limit\":1}'"
test_service "github" "list_repos"
test_service "slack" "list_channels"
test_service "aws" "list_instances"
test_service "bigquery" "list_datasets"
```

### Common Issues

**Issue**: "GITHUB_PERSONAL_ACCESS_TOKEN not found"
```bash
# Solution: Check file permissions and path
ls -la ~/.mcporter/oauth/github.token
cat ~/.mcporter/oauth/github.token  # Should show token
echo $GITHUB_PERSONAL_ACCESS_TOKEN  # Should output token if set
```

**Issue**: "Gmail token expired"
```bash
# Solution: Refresh token manually
gog auth refresh
cp ~/.config/gog/oauth-token.json ~/.mcporter/oauth/gmail.json
mcporter auth gmail --test
```

**Issue**: "AWS credentials not working"
```bash
# Solution: Verify AWS profile
aws sts get-caller-identity --profile openclaw
# Should return account info, not error
```

## Token Rotation Schedule

- **GitHub PAT**: Annual renewal (expires after 1 year)
- **Gmail OAuth**: Refresh on use (handled by gog automatically)
- **AWS Access Keys**: Every 90 days (set calendar reminder)
- **Slack Tokens**: Annual renewal
- **BigQuery Service Account**: Annual renewal

---

*Updated: March 18, 2026*