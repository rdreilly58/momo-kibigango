# MCP Phase 1 Setup Guide - Core Services

This guide covers the step-by-step setup for Phase 1 MCP integration (Gmail, BigQuery, GitHub, Slack).

## Prerequisites

- OpenClaw installed and running
- `mcporter` CLI installed at `/opt/homebrew/bin/mcporter`
- Node.js 18+ installed
- Google Cloud project with API keys configured
- GitHub personal access token
- Slack workspace with app created

## Setup Checklist

- [ ] Verify mcporter installation
- [ ] Update mcporter to latest version
- [ ] Create OAuth directory structure
- [ ] Set up Gmail MCP
- [ ] Set up BigQuery MCP
- [ ] Enhance GitHub MCP
- [ ] Set up Slack MCP
- [ ] Run integration tests
- [ ] Set up monitoring

## Step 1: Verify and Update mcporter

```bash
#!/bin/bash
# verify-mcporter.sh

echo "Checking mcporter installation..."
if ! command -v mcporter &> /dev/null; then
  echo "✗ mcporter not found. Installing..."
  npm install -g mcporter
else
  echo "✓ mcporter found at $(which mcporter)"
  mcporter --version
fi

# Update to latest
npm install -g mcporter@latest

# Verify configuration directory
mkdir -p ~/.mcporter/oauth
mkdir -p ~/.openclaw/workspace/config

echo "✓ mcporter ready for configuration"
```

## Step 2: Gmail MCP Setup

### 2.1 Create Google Cloud Project

```bash
# If you haven't already created a GCP project:
# 1. Go to https://console.cloud.google.com
# 2. Create new project: "OpenClaw"
# 3. Enable APIs:
#    - Gmail API
#    - Google Drive API
# 4. Create OAuth 2.0 credentials (Desktop app)
# 5. Download credentials JSON

export GOOGLE_CLIENT_ID="YOUR_CLIENT_ID.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="YOUR_CLIENT_SECRET"
```

### 2.2 Authenticate Gmail

```bash
#!/bin/bash
# setup-gmail.sh

echo "Setting up Gmail MCP..."

# 1. Use existing gog authentication
if ! gog auth status 2>/dev/null | grep -q "rdreilly2010@gmail.com"; then
  echo "Authenticating with Google..."
  gog login rdreilly2010@gmail.com
fi

# 2. Extract OAuth token for MCP
mkdir -p ~/.mcporter/oauth
if [ -f ~/.config/gog/oauth-token.json ]; then
  cp ~/.config/gog/oauth-token.json ~/.mcporter/oauth/gmail.json
  echo "✓ Gmail OAuth token exported"
else
  echo "✗ Could not find gog OAuth token"
  echo "Run: gog login rdreilly2010@gmail.com"
  exit 1
fi

# 3. Test Gmail access
echo "Testing Gmail access..."
if gog gmail search 'from:rdreilly2010@gmail.com' --limit 1 &>/dev/null; then
  echo "✓ Gmail access confirmed"
else
  echo "✗ Gmail access failed"
  exit 1
fi

# 4. Install Gmail MCP server
echo "Installing Gmail MCP server..."
npm install -g mcp-server-gmail || npm install -g @modelcontextprotocol/server-gmail

# 5. Add to mcporter config
echo "Configuring mcporter..."
cat >> ~/.mcporter/mcporter.json << 'EOF'
  "gmail": {
    "description": "Gmail: search, read, send emails",
    "command": "mcp-server-gmail",
    "env": {
      "GMAIL_OAUTH_PATH": "${HOME}/.mcporter/oauth/gmail.json"
    }
  }
EOF

# 6. Test MCP Gmail
echo "Testing MCP Gmail server..."
if mcporter call gmail.search --args '{"query":"from:rdreilly2010@gmail.com","limit":1}' &>/dev/null; then
  echo "✓ Gmail MCP server working"
else
  echo "⚠ Gmail MCP server test inconclusive"
  echo "Run: mcporter list to verify installation"
fi

echo "✓ Gmail setup complete"
```

### 2.3 Verify Gmail MCP

```bash
# List available Gmail tools
mcporter list gmail --schema

# Test search
mcporter call gmail.search --args '{"query":"subject:test","limit":5}'

# Test send (dry run)
mcporter call gmail.draft --args '{"to":"test@example.com","subject":"Test","body":"Test message"}'
```

## Step 3: BigQuery MCP Setup

### 3.1 Prepare Service Account

```bash
#!/bin/bash
# setup-bigquery.sh

echo "Setting up BigQuery MCP..."

# 1. Check for existing service account
GCP_SA_FILE=~/.gcp/127601657025-service-account.json

if [ ! -f "$GCP_SA_FILE" ]; then
  echo "Service account file not found. Expected at: $GCP_SA_FILE"
  echo "Please create one:"
  echo "1. Go to https://console.cloud.google.com/iam-admin/serviceaccounts"
  echo "2. Select project: 127601657025"
  echo "3. Create service account for BigQuery"
  echo "4. Grant roles: roles/bigquery.user, roles/bigquery.dataEditor"
  echo "5. Create JSON key and save to: $GCP_SA_FILE"
  exit 1
fi

# 2. Copy to mcporter oauth directory
cp "$GCP_SA_FILE" ~/.mcporter/oauth/bigquery-sa.json
chmod 600 ~/.mcporter/oauth/bigquery-sa.json

echo "✓ Service account copied"

# 3. Verify service account
if gcloud auth activate-service-account --key-file="$GCP_SA_FILE" &>/dev/null; then
  echo "✓ Service account authenticated"
else
  echo "⚠ Service account authentication issue"
fi

# 4. Install BigQuery MCP server
echo "Installing BigQuery MCP server..."
npm install -g mcp-server-bigquery

# 5. Add to mcporter config
cat >> ~/.mcporter/mcporter.json << 'EOF'
  "bigquery": {
    "description": "BigQuery: GA4 analytics and data warehouse queries",
    "command": "mcp-server-bigquery",
    "env": {
      "GOOGLE_APPLICATION_CREDENTIALS": "${HOME}/.mcporter/oauth/bigquery-sa.json",
      "GCP_PROJECT_ID": "127601657025"
    }
  }
EOF

# 6. Test BigQuery MCP
echo "Testing BigQuery MCP..."
if mcporter call bigquery.list_datasets 2>&1 | grep -q "ga4"; then
  echo "✓ BigQuery MCP working"
else
  echo "⚠ BigQuery MCP test inconclusive"
fi

echo "✓ BigQuery setup complete"
```

### 3.2 Verify BigQuery MCP

```bash
# List datasets
mcporter call bigquery.list_datasets

# List tables in GA4 dataset
mcporter call bigquery.list_tables dataset_id=ga4_reillydesignstudio

# Run sample query
mcporter call bigquery.query --args '{
  "sql": "SELECT COUNT(*) as event_count FROM `127601657025.ga4_reillydesignstudio.events_*` WHERE _TABLE_SUFFIX = FORMAT_DATE(\"%Y%m%d\", CURRENT_DATE()-1) LIMIT 1"
}'
```

## Step 4: GitHub MCP Enhancement

### 4.1 Verify Existing GitHub Setup

```bash
#!/bin/bash
# verify-github.sh

echo "Verifying GitHub MCP setup..."

# Check if already configured
if mcporter list github &>/dev/null; then
  echo "✓ GitHub MCP already configured"
  echo "Listing GitHub repositories..."
  mcporter call github.list_repos --limit 5
else
  echo "✗ GitHub MCP not found, initializing..."
fi
```

### 4.2 Enhance GitHub Configuration

```bash
#!/bin/bash
# enhance-github.sh

echo "Enhancing GitHub MCP configuration..."

# 1. Verify PAT exists
if ! grep -q "GITHUB_PERSONAL_ACCESS_TOKEN" ~/.mcporter/mcporter.json; then
  echo "Adding GitHub PAT to config..."
  # PAT should already be configured from previous setup
  echo "PAT configuration needed. Set GITHUB_PERSONAL_ACCESS_TOKEN environment variable."
fi

# 2. Add retry and timeout settings
cat > ~/.mcporter/github-config.json << 'EOF'
{
  "retryAttempts": 3,
  "retryDelayMs": 1000,
  "timeoutMs": 30000,
  "rateLimitHandler": "wait",
  "cacheEnabled": true,
  "cacheTtlSeconds": 300
}
EOF

echo "✓ GitHub enhancement complete"
```

### 4.3 Test GitHub MCP

```bash
# List pull requests
mcporter call github.list_pull_requests repo=openclaw/openclaw state=open

# List issues
mcporter call github.list_issues repo=openclaw/openclaw labels="bug" limit=10

# Get repository info
mcporter call github.get_repository repo=openclaw/openclaw
```

## Step 5: Slack MCP Setup

### 5.1 Create Slack App

```bash
# 1. Go to https://api.slack.com/apps
# 2. Click "Create New App" > "From scratch"
# 3. Name: "OpenClaw MCP"
# 4. Workspace: Select your workspace

# 5. Set up OAuth & Permissions:
#    - Scopes:
#      - channels:history
#      - channels:read
#      - chat:write
#      - groups:history (for DMs)
#      - groups:read
#      - im:history
#      - im:read
#      - users:read
#      - files:read

# 6. Generate tokens:
#    - Bot User OAuth Token: xoxb-...
#    - App-Level Token: xapp-... (required for socket mode)

# 7. Install app to workspace
```

### 5.2 Configure Slack MCP

```bash
#!/bin/bash
# setup-slack.sh

echo "Setting up Slack MCP..."

# 1. Store tokens securely
mkdir -p ~/.mcporter/oauth/slack

# Get tokens from https://api.slack.com/apps/YOUR_APP_ID/token-rotation
read -sp "Slack Bot Token (xoxb-): " BOT_TOKEN
echo "$BOT_TOKEN" > ~/.mcporter/oauth/slack/bot.token
chmod 600 ~/.mcporter/oauth/slack/bot.token

read -sp "Slack App Token (xapp-): " APP_TOKEN
echo "$APP_TOKEN" > ~/.mcporter/oauth/slack/app.token
chmod 600 ~/.mcporter/oauth/slack/app.token

echo "✓ Slack tokens stored"

# 2. Install Slack MCP server
echo "Installing Slack MCP server..."
npm install -g @modelcontextprotocol/server-slack

# 3. Add to mcporter config
cat >> ~/.mcporter/mcporter.json << 'EOF'
  "slack": {
    "description": "Slack: messages, channels, users, files",
    "command": "npx -y @modelcontextprotocol/server-slack",
    "env": {
      "SLACK_BOT_TOKEN": "${HOME}/.mcporter/oauth/slack/bot.token",
      "SLACK_APP_TOKEN": "${HOME}/.mcporter/oauth/slack/app.token"
    }
  }
EOF

# 4. Test Slack MCP
echo "Testing Slack MCP..."
if mcporter call slack.list_channels 2>&1 | head -5; then
  echo "✓ Slack MCP working"
else
  echo "⚠ Slack MCP test inconclusive"
fi

echo "✓ Slack setup complete"
```

### 5.3 Test Slack MCP

```bash
# List channels
mcporter call slack.list_channels

# Get channel info
mcporter call slack.get_channel channel_id=C01234567

# Send test message
mcporter call slack.post_message --args '{
  "channel": "C01234567",
  "text": "Test message from MCP"
}'
```

## Step 6: Integration Testing

### 6.1 Create Test Suite

```bash
#!/bin/bash
# test-mcp-phase1.sh

set -e

TEST_RESULTS=~/.openclaw/logs/mcp-phase1-test.log
mkdir -p $(dirname "$TEST_RESULTS")

echo "=== MCP Phase 1 Integration Tests ===" | tee "$TEST_RESULTS"
echo "Start time: $(date)" >> "$TEST_RESULTS"

test_count=0
pass_count=0
fail_count=0

run_test() {
  local name=$1
  local cmd=$2
  
  ((test_count++))
  echo -n "Test $test_count: $name... "
  
  if eval "$cmd" >> "$TEST_RESULTS" 2>&1; then
    echo "✓ PASS"
    ((pass_count++))
  else
    echo "✗ FAIL"
    ((fail_count++))
  fi
}

# Gmail tests
run_test "Gmail search" "mcporter call gmail.search --args '{\"query\":\"from:rdreilly2010@gmail.com\",\"limit\":1}'"
run_test "Gmail list labels" "mcporter call gmail.list_labels"

# BigQuery tests
run_test "BigQuery list datasets" "mcporter call bigquery.list_datasets"
run_test "BigQuery sample query" "mcporter call bigquery.query --args '{\"sql\":\"SELECT 1 as test\"}'"

# GitHub tests
run_test "GitHub list repos" "mcporter call github.list_repos --limit 1"
run_test "GitHub get user" "mcporter call github.get_user"

# Slack tests
run_test "Slack list channels" "mcporter call slack.list_channels"
run_test "Slack list users" "mcporter call slack.list_users"

# Summary
echo ""
echo "=== Test Summary ===" | tee -a "$TEST_RESULTS"
echo "Total: $test_count | Passed: $pass_count | Failed: $fail_count" | tee -a "$TEST_RESULTS"
echo "End time: $(date)" >> "$TEST_RESULTS"

if [ $fail_count -eq 0 ]; then
  echo "✓ All tests passed!"
  exit 0
else
  echo "✗ Some tests failed. Review log: $TEST_RESULTS"
  exit 1
fi
```

### 6.2 Run Tests

```bash
chmod +x ~/.openclaw/workspace/scripts/test-mcp-phase1.sh
~/.openclaw/workspace/scripts/test-mcp-phase1.sh
```

## Step 7: Set Up Monitoring

```bash
#!/bin/bash
# setup-mcp-monitoring.sh

echo "Setting up MCP monitoring..."

# 1. Create health check script
cat > ~/.openclaw/workspace/scripts/mcp-health-check.sh << 'EOF'
#!/bin/bash
# MCP health check - runs hourly

SERVICES=("gmail" "github" "bigquery" "slack")
HEALTH_LOG=~/.openclaw/logs/mcp-health.log

for service in "${SERVICES[@]}"; do
  if mcporter list "$service" &>/dev/null; then
    echo "$(date): ✓ $service healthy" >> "$HEALTH_LOG"
  else
    echo "$(date): ✗ $service UNHEALTHY" >> "$HEALTH_LOG"
  fi
done
EOF

chmod +x ~/.openclaw/workspace/scripts/mcp-health-check.sh

# 2. Add to cron
(crontab -l 2>/dev/null || true; echo "0 * * * * ~/.openclaw/workspace/scripts/mcp-health-check.sh") | crontab -

echo "✓ Monitoring setup complete"
```

## Troubleshooting

### Gmail MCP Not Working

```bash
# 1. Verify OAuth token
ls -la ~/.mcporter/oauth/gmail.json

# 2. Check if gog is authenticated
gog auth status

# 3. Refresh token
gog auth refresh
cp ~/.config/gog/oauth-token.json ~/.mcporter/oauth/gmail.json

# 4. Test mcporter directly
mcporter list gmail --schema
```

### BigQuery MCP Issues

```bash
# 1. Verify service account
cat ~/.mcporter/oauth/bigquery-sa.json | jq '.project_id'

# 2. Test GCP authentication
gcloud auth activate-service-account --key-file=~/.mcporter/oauth/bigquery-sa.json
gcloud projects list

# 3. Check BigQuery access
bq ls --project_id=127601657025
```

### GitHub MCP Failures

```bash
# 1. Verify PAT token
echo $GITHUB_PERSONAL_ACCESS_TOKEN | wc -c  # Should be ~40 chars

# 2. Test GitHub API directly
curl -H "Authorization: token $GITHUB_PERSONAL_ACCESS_TOKEN" \
  https://api.github.com/user

# 3. Check rate limits
mcporter call github.get_rate_limit
```

### Slack MCP Connection Issues

```bash
# 1. Verify tokens
ls -la ~/.mcporter/oauth/slack/

# 2. Test token validity
curl -H "Authorization: Bearer $(cat ~/.mcporter/oauth/slack/bot.token)" \
  https://slack.com/api/auth.test

# 3. Check Slack workspace
mcporter call slack.get_workspace_info
```

## Rollback Plan

If you need to revert Phase 1 setup:

```bash
#!/bin/bash
# rollback-phase1.sh

echo "Rolling back Phase 1 MCP setup..."

# 1. Backup current config
cp ~/.mcporter/mcporter.json ~/.mcporter/mcporter.json.backup

# 2. Remove Phase 1 servers from config
jq 'del(.mcpServers.gmail, .mcpServers.bigquery, .mcpServers.slack)' \
  ~/.mcporter/mcporter.json > ~/.mcporter/mcporter.json.tmp
mv ~/.mcporter/mcporter.json.tmp ~/.mcporter/mcporter.json

# 3. Remove OAuth tokens
rm -f ~/.mcporter/oauth/gmail.json
rm -f ~/.mcporter/oauth/bigquery-sa.json
rm -rf ~/.mcporter/oauth/slack/

# 4. Uninstall MCP servers
npm uninstall -g mcp-server-gmail
npm uninstall -g mcp-server-bigquery
npm uninstall -g @modelcontextprotocol/server-slack

echo "✓ Rollback complete"
echo "Backup saved: ~/.mcporter/mcporter.json.backup"
```

---

*Created: March 18, 2026*
*Version: 1.0*