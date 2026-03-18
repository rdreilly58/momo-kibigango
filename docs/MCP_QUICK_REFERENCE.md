# MCP Quick Reference Guide

## Common Commands

### List Available Services

```bash
# List all configured MCP servers
mcporter list

# List with details
mcporter list --verbose

# Show available tools for a service
mcporter list gmail --schema
mcporter list github --schema
```

### Test Service Connectivity

```bash
# Quick test of Gmail
mcporter call gmail.search --args '{"query":"from:me","limit":1}'

# Quick test of GitHub
mcporter call github.list_repos --limit 1

# Quick test of BigQuery
mcporter call bigquery.list_datasets

# Quick test of Slack
mcporter call slack.list_channels
```

### Configuration Management

```bash
# List current config
mcporter config list

# Add a new server
mcporter config add myserver \
  --command "npx @org/mcp-server" \
  --env API_KEY="value"

# Remove a server
mcporter config remove myserver

# Get config for specific server
mcporter config get gmail
```

### Authentication

```bash
# Authenticate with a service
mcporter auth gmail
mcporter auth github

# Test authentication
mcporter auth github --test

# Reset authentication
mcporter auth gmail --reset
```

## Calling MCP Tools

### Basic Syntax

```bash
# With positional args
mcporter call gmail.search query="test" limit:5

# With JSON args
mcporter call gmail.search --args '{"query":"test","limit":5}'

# Full server.tool syntax
mcporter call gmail.search query="from:test@example.com"

# Direct URL (HTTP servers)
mcporter call https://api.linear.app/mcp list_issues team=ENG
```

### Common Tool Patterns

**Gmail:**
```bash
# Search emails
mcporter call gmail.search query="subject:invoice" limit:10

# Read message
mcporter call gmail.get_message message_id="ABC123"

# Send email
mcporter call gmail.send --args '{
  "to":"recipient@example.com",
  "subject":"Test",
  "body":"Hello world"
}'
```

**GitHub:**
```bash
# List repositories
mcporter call github.list_repos --limit 10

# List issues
mcporter call github.list_issues repo=owner/name state=open

# Create issue
mcporter call github.create_issue repo=owner/name \
  title="Bug report" \
  body="Description here"
```

**BigQuery:**
```bash
# List datasets
mcporter call bigquery.list_datasets

# Run query
mcporter call bigquery.query --args '{
  "sql":"SELECT COUNT(*) FROM dataset.table"
}'

# Get query results
mcporter call bigquery.get_query_results job_id="ABC123"
```

**Slack:**
```bash
# List channels
mcporter call slack.list_channels

# Send message
mcporter call slack.post_message --args '{
  "channel":"C123456",
  "text":"Hello channel"
}'

# List users
mcporter call slack.list_users
```

## Configuration Files

### Main Config Location

```bash
~/.mcporter/mcporter.json
```

### Config Structure

```json
{
  "mcpServers": {
    "servicename": {
      "description": "Service description",
      "command": "executable or npx command",
      "args": ["arg1", "arg2"],
      "env": {
        "KEY": "${HOME}/path/or/value"
      }
    }
  },
  "imports": []
}
```

### Example: Adding New Server

```bash
# Edit config directly
cat ~/.mcporter/mcporter.json | jq '.mcpServers.myserver = {
  "description": "My service",
  "command": "npx",
  "args": ["-y", "@org/mcp-server"],
  "env": {"API_KEY": "${API_KEY}"}
}' > ~/.mcporter/mcporter.json.tmp && \
mv ~/.mcporter/mcporter.json.tmp ~/.mcporter/mcporter.json
```

## Environment Variables

### Common MCP Server Environment Variables

```bash
# Gmail
export GMAIL_OAUTH_PATH=~/.mcporter/oauth/gmail.json

# GitHub
export GITHUB_PERSONAL_ACCESS_TOKEN="gho_..."

# AWS
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_REGION="us-east-1"

# BigQuery
export GOOGLE_APPLICATION_CREDENTIALS=~/.mcporter/oauth/bigquery-sa.json
export GCP_PROJECT_ID="127601657025"

# Slack
export SLACK_BOT_TOKEN="xoxb-..."
export SLACK_APP_TOKEN="xapp-..."
```

## Daemon Operations

```bash
# Start mcporter daemon (persistent background service)
mcporter daemon start

# Check daemon status
mcporter daemon status

# Stop daemon
mcporter daemon stop

# Restart daemon
mcporter daemon restart

# View daemon logs
tail -f ~/.mcporter/daemon.log
```

## Performance Tips

### Use --output json for Better Parsing

```bash
# Get JSON output
mcporter call github.list_repos --output json | jq '.[]'

# Parse specific fields
mcporter call github.list_repos --output json | jq '.[].name'
```

### Limit Results for Speed

```bash
# Always set limits on list operations
mcporter call github.list_repos limit:5

# Use pagination for large datasets
mcporter call github.list_repos limit:100 page:1
mcporter call github.list_repos limit:100 page:2
```

### Cache Results Locally

```bash
# Save results to file
mcporter call bigquery.list_datasets > ~/datasets.json

# Process offline
cat ~/datasets.json | jq '.[]'
```

## Troubleshooting

### Service Not Responding

```bash
# Check if service is healthy
mcporter list servicename

# View detailed logs
mcporter daemon status --verbose

# Test connection directly
mcporter call servicename.ping

# Restart daemon
mcporter daemon restart
```

### Authentication Errors

```bash
# Verify token exists
ls -la ~/.mcporter/oauth/

# Test auth
mcporter auth servicename --test

# Reset and re-authenticate
mcporter auth servicename --reset
mcporter auth servicename
```

### Timeout Issues

```bash
# Increase timeout in config
cat > ~/.mcporter/timeout.env << 'EOF'
MCPORTER_TIMEOUT=60000
MCPORTER_RETRY_ATTEMPTS=3
EOF

# Use with mcporter
source ~/.mcporter/timeout.env
mcporter call servicename.tool
```

## Monitoring

### Health Check Script

```bash
#!/bin/bash
# Quick health check

for service in gmail github bigquery slack; do
  echo -n "$service: "
  if mcporter list $service &>/dev/null; then
    echo "✓"
  else
    echo "✗"
  fi
done
```

### Performance Monitoring

```bash
# Time a MCP call
time mcporter call gmail.search query="test" limit:5

# Monitor system resources during call
watch -n 0.1 'ps aux | grep mcporter'
```

## Integration Examples

### Using in Bash Scripts

```bash
#!/bin/bash
# Send Slack alert on GitHub issue

ISSUE=$(mcporter call github.list_issues repo=owner/repo state=open limit:1 --output json)
ISSUE_TITLE=$(echo "$ISSUE" | jq -r '.[0].title')
ISSUE_URL=$(echo "$ISSUE" | jq -r '.[0].html_url')

mcporter call slack.post_message --args "{
  \"channel\":\"C123456\",
  \"text\":\"New issue: $ISSUE_TITLE\",
  \"blocks\":[{\"type\":\"section\",\"text\":{\"type\":\"mrkdwn\",\"text\":\"<$ISSUE_URL|View Issue>\"}}]
}"
```

### Using in Node.js

```javascript
const { exec } = require('child_process');
const { promisify } = require('util');
const execAsync = promisify(exec);

async function searchGmail(query) {
  const cmd = `mcporter call gmail.search --args '${JSON.stringify({
    query,
    limit: 10
  })}'`;
  
  const { stdout } = await execAsync(cmd);
  return JSON.parse(stdout);
}

async function getGitHubIssues() {
  const cmd = `mcporter call github.list_issues repo=owner/repo state=open --output json`;
  const { stdout } = await execAsync(cmd);
  return JSON.parse(stdout);
}
```

### Using with OpenClaw Skills

```bash
#!/bin/bash
# In an OpenClaw skill, use mcporter for external service access

# Get recent emails
EMAILS=$(mcporter call gmail.search query="after:2026-03-17" limit:5 --output json)

# Check GitHub PRs
PRS=$(mcporter call github.list_pull_requests repo=openclaw/openclaw state=open --output json)

# Query GA4 data
EVENTS=$(mcporter call bigquery.query --args '{
  "sql":"SELECT COUNT(*) FROM ga4_reillydesignstudio.events_*"
}')
```

## Useful Aliases

Add these to your shell profile (~/.zshrc or ~/.bash_profile):

```bash
# MCP shortcuts
alias mcp-list='mcporter list'
alias mcp-auth='mcporter auth'
alias mcp-call='mcporter call'

# Service-specific shortcuts
alias mcp-gmail='mcporter call gmail'
alias mcp-github='mcporter call github'
alias mcp-slack='mcporter call slack'
alias mcp-gcp='mcporter call bigquery'

# Common operations
alias mcp-health='for s in gmail github slack bigquery; do echo -n "$s: "; mcporter list $s &>/dev/null && echo "✓" || echo "✗"; done'

# Kill stuck processes
alias mcp-kill='pkill -f mcporter'
```

## Resources

- **MCP Spec**: https://modelcontextprotocol.io
- **mcporter Docs**: http://mcporter.dev
- **Server Repository**: https://github.com/modelcontextprotocol/servers
- **Community Servers**: https://github.com/wong2/awesome-mcp-servers

---

*Quick Reference v1.0 - March 18, 2026*