# MCP (Model Context Protocol) Integration Plan for OpenClaw

## Executive Summary

This document outlines a comprehensive strategy for integrating MCP servers with OpenClaw to provide seamless access to external services. MCP enables structured communication between AI agents and external tools, making it ideal for expanding OpenClaw's capabilities without modifying core code.

## Current State Analysis

### Existing MCP Setup
- **mcporter** is already installed and configured at `/opt/homebrew/bin/mcporter`
- Configuration stored in `~/.mcporter/mcporter.json`
- Currently configured servers:
  - ✅ GitHub (with PAT authentication)
  - ✅ Filesystem (Projects & Documents access)
  - ✅ Notion (needs token)
  - ⚠️ Linear (auth required)
  - ⚠️ SQLite (offline - database missing)
  - ✅ Google Drive (partially configured)

### OpenClaw Configuration
- No native MCP configuration found in `openclaw.json`
- mcporter skill available at `/opt/homebrew/lib/node_modules/openclaw/skills/mcporter/`
- OpenClaw uses mcporter as a bridge to MCP servers

## Priority Services for Integration

### Tier 1 - Immediate Priority (Already in use)
1. **Gmail** - Bob uses `gog gmail` heavily for email operations
2. **Google Calendar** - Daily briefings require calendar access
3. **Google Analytics (BigQuery)** - GA4 data for ReillyDesignStudio
4. **GitHub** - Already configured, enhance with better error handling
5. **Slack** - Direct integration for Clawdbot operations

### Tier 2 - High Value (Next 30 days)
1. **AWS** - EC2 management, S3 operations, CloudWatch monitoring
2. **WhatsApp** - Replace wacli with MCP server
3. **Apple Keychain** - Centralized credential management
4. **Uptime Kuma** - Service monitoring integration
5. **Notion** - Complete the existing setup

### Tier 3 - Future Expansion
1. **Linear** - Project management (auth pending)
2. **Airtable** - Data management
3. **Stripe** - Payment processing
4. **Docker** - Container management
5. **Kubernetes** - Cluster operations

## Implementation Strategy

### 1. Pre-built vs Custom Servers

**Use Pre-built MCP Servers When:**
- Official server exists (@modelcontextprotocol/server-*)
- Community server is well-maintained (100+ stars on GitHub)
- Service has simple REST/GraphQL API

**Build Custom Wrappers When:**
- No existing MCP server available
- Complex authentication requirements
- Need to aggregate multiple APIs
- Custom business logic required

### 2. Authentication Strategy

```json
// Centralized credential storage in ~/.mcporter/mcporter.json
{
  "mcpServers": {
    "gmail": {
      "env": {
        "GOOGLE_OAUTH_PATH": "/path/to/oauth.json",
        "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/service-account.json"
      }
    },
    "aws": {
      "env": {
        "AWS_ACCESS_KEY_ID": "${AWS_ACCESS_KEY_ID}",
        "AWS_SECRET_ACCESS_KEY": "${AWS_SECRET_ACCESS_KEY}",
        "AWS_REGION": "us-east-1"
      }
    }
  }
}
```

**Best Practices:**
- Use environment variable references for sensitive data
- Store OAuth tokens in ~/.mcporter/oauth/
- Implement token refresh mechanisms
- Use Apple Keychain CLI for credential retrieval

### 3. Error Handling & Fallbacks

```typescript
// Fallback pattern for MCP operations
async function callMCPWithFallback(server: string, tool: string, args: any) {
  try {
    // Primary: Try MCP server
    return await mcporter.call(`${server}.${tool}`, args);
  } catch (error) {
    // Secondary: Try direct API call
    if (fallbackAPIs[server]) {
      return await fallbackAPIs[server][tool](args);
    }
    // Tertiary: Use CLI tool if available
    if (cliTools[server]) {
      return await exec(`${cliTools[server]} ${tool} ${args}`);
    }
    throw new Error(`All methods failed for ${server}.${tool}`);
  }
}
```

## Configuration Templates

### 1. Gmail MCP Server

```bash
# Install Gmail MCP server
npm install -g @modelcontextprotocol/server-gmail

# Configure in mcporter
mcporter config add gmail \
  --command "mcp-server-gmail" \
  --env GOOGLE_OAUTH_PATH=/Users/rreilly/.mcporter/oauth/gmail.json \
  --description "Gmail: read, search, send emails"
```

### 2. BigQuery MCP Server

```bash
# Install BigQuery MCP server
npm install -g mcp-server-bigquery

# Configure with service account
mcporter config add bigquery \
  --command "mcp-server-bigquery" \
  --env GOOGLE_APPLICATION_CREDENTIALS=/Users/rreilly/.gcp/ga4-service-account.json \
  --env PROJECT_ID=127601657025 \
  --description "BigQuery: GA4 analytics data"
```

### 3. AWS MCP Server

```bash
# Install AWS MCP server
npm install -g @modelcontextprotocol/server-aws

# Configure with credentials
mcporter config add aws \
  --command "npx -y @modelcontextprotocol/server-aws" \
  --env AWS_PROFILE=openclaw \
  --description "AWS: EC2, S3, CloudWatch"
```

### 4. Slack MCP Server

```bash
# Install Slack MCP server
npm install -g @modelcontextprotocol/server-slack

# Configure with app token
mcporter config add slack \
  --command "npx -y @modelcontextprotocol/server-slack" \
  --env SLACK_APP_TOKEN=xapp-... \
  --env SLACK_BOT_TOKEN=xoxb-... \
  --description "Slack: messages, channels, users"
```

## Installation Steps

### Phase 1: Core Services (Week 1)

1. **Gmail Integration**
   ```bash
   # Authenticate with Google
   gog login rdreilly2010@gmail.com
   
   # Export OAuth token for MCP
   cp ~/.config/gog/oauth-token.json ~/.mcporter/oauth/gmail.json
   
   # Install and configure Gmail MCP
   npm install -g @modelcontextprotocol/server-gmail
   mcporter config add gmail --command "mcp-server-gmail"
   mcporter auth gmail
   ```

2. **BigQuery Integration**
   ```bash
   # Use existing service account
   cp ~/.gcp/service-account.json ~/.mcporter/oauth/bigquery-sa.json
   
   # Configure BigQuery MCP
   mcporter config add bigquery \
     --command "mcp-server-bigquery" \
     --env GOOGLE_APPLICATION_CREDENTIALS=~/.mcporter/oauth/bigquery-sa.json
   ```

3. **Enhanced GitHub**
   ```bash
   # Update existing GitHub config with better error handling
   mcporter config add github \
     --command "npx -y @modelcontextprotocol/server-github" \
     --env GITHUB_PERSONAL_ACCESS_TOKEN="${GITHUB_PAT}" \
     --env GITHUB_RETRY_ATTEMPTS=3 \
     --env GITHUB_TIMEOUT=30000
   ```

### Phase 2: Extended Services (Week 2-3)

1. **AWS Services**
2. **Slack Integration** 
3. **WhatsApp via Rube**
4. **Apple Keychain Integration**

### Phase 3: Advanced Features (Week 4+)

1. **Custom MCP Servers**
2. **Monitoring & Observability**
3. **Performance Optimization**

## Testing Strategy

### 1. Unit Tests for Each Server

```bash
# Test Gmail server
mcporter call gmail.search query="from:rdreilly2010@gmail.com" limit:5

# Test BigQuery server  
mcporter call bigquery.query \
  sql="SELECT COUNT(*) FROM ga4_reillydesignstudio.events_*"

# Test GitHub server
mcporter call github.list_issues repo="openclaw/openclaw" state="open"
```

### 2. Integration Tests

```javascript
// Test script: test-mcp-integration.js
const tests = [
  {
    name: "Gmail search performance",
    server: "gmail",
    tool: "search",
    args: { query: "subject:test", limit: 10 },
    expectedTime: 3000 // 3 seconds max
  },
  {
    name: "BigQuery GA4 query",
    server: "bigquery", 
    tool: "query",
    args: { 
      sql: "SELECT COUNT(*) FROM `ga4_reillydesignstudio.events_*` WHERE _TABLE_SUFFIX = FORMAT_DATE('%Y%m%d', CURRENT_DATE()-1)"
    },
    expectedTime: 5000
  }
];

// Run tests and report
for (const test of tests) {
  const start = Date.now();
  try {
    const result = await mcporter.call(`${test.server}.${test.tool}`, test.args);
    const duration = Date.now() - start;
    console.log(`✓ ${test.name}: ${duration}ms`);
  } catch (error) {
    console.log(`✗ ${test.name}: ${error.message}`);
  }
}
```

### 3. Error Handling Tests

- Network failures
- Authentication expiration
- Rate limiting
- Timeout handling
- Partial failures

## Security Considerations

### 1. Credential Management

```bash
# Use Apple Keychain for all credentials
op item create \
  --category="API Credential" \
  --title="MCP Gmail OAuth" \
  --vault="OpenClaw" \
  oauth_token[password]="$(cat ~/.mcporter/oauth/gmail.json | base64)"

# Retrieve at runtime
export GMAIL_OAUTH=$(op read "op://OpenClaw/MCP Gmail OAuth/oauth_token")
```

### 2. Access Control

```json
// Restrict MCP server access per agent
{
  "agents": {
    "main": {
      "mcp": {
        "allowedServers": ["gmail", "github", "bigquery", "notion"],
        "deniedTools": ["gmail.delete", "github.delete_repo"]
      }
    },
    "limited": {
      "mcp": {
        "allowedServers": ["filesystem"],
        "allowedPaths": ["/Users/rreilly/Documents/Public"]
      }
    }
  }
}
```

### 3. Audit Logging

```bash
# Enable MCP audit logging
export MCPORTER_AUDIT_LOG=/Users/rreilly/.openclaw/logs/mcp-audit.log
export MCPORTER_AUDIT_LEVEL=all

# Log format
# 2026-03-18T01:00:00Z|agent:main|gmail.search|{query:"test"}|success|125ms
```

## Monitoring & Observability

### 1. Health Checks

```bash
#!/bin/bash
# mcp-health-check.sh

servers=("gmail" "github" "bigquery" "slack" "aws")

for server in "${servers[@]}"; do
  if mcporter call "$server.ping" &>/dev/null; then
    echo "✓ $server: healthy"
  else
    echo "✗ $server: unhealthy"
    # Send alert to Healthchecks.io
    curl -fsS --retry 3 https://hc-ping.com/mcp-$server/fail
  fi
done
```

### 2. Performance Monitoring

```javascript
// Track MCP call performance
const metrics = {
  calls: {},
  
  track(server, tool, duration, success) {
    const key = `${server}.${tool}`;
    if (!this.calls[key]) {
      this.calls[key] = { count: 0, totalTime: 0, failures: 0 };
    }
    this.calls[key].count++;
    this.calls[key].totalTime += duration;
    if (!success) this.calls[key].failures++;
  },
  
  report() {
    for (const [key, stats] of Object.entries(this.calls)) {
      const avgTime = stats.totalTime / stats.count;
      const successRate = ((stats.count - stats.failures) / stats.count) * 100;
      console.log(`${key}: ${avgTime.toFixed(0)}ms avg, ${successRate.toFixed(1)}% success`);
    }
  }
};
```

## Migration Plan

### Week 1: Foundation
- [ ] Install core MCP servers (Gmail, BigQuery, Slack)
- [ ] Configure authentication for each service
- [ ] Update OpenClaw skills to use MCP where available
- [ ] Create fallback mechanisms

### Week 2: Integration
- [ ] Migrate email operations from `gog` to MCP
- [ ] Integrate BigQuery MCP for GA4 analytics
- [ ] Set up Slack MCP for Clawdbot
- [ ] Create unified error handling

### Week 3: Optimization
- [ ] Performance testing and tuning
- [ ] Implement caching layer
- [ ] Set up monitoring and alerts
- [ ] Document best practices

### Week 4: Advanced Features
- [ ] Build custom MCP servers for specialized needs
- [ ] Implement credential rotation
- [ ] Create MCP server health dashboard
- [ ] Train team on MCP usage

## Success Metrics

1. **Performance**
   - Gmail search: <2s (vs 5s with gog)
   - BigQuery queries: <3s
   - GitHub operations: <1s

2. **Reliability**
   - 99.9% uptime for critical services
   - Automatic failover within 5s
   - Zero credential exposure incidents

3. **Developer Experience**
   - Unified interface for all external services
   - Consistent error handling
   - Comprehensive documentation

## Conclusion

MCP integration will significantly enhance OpenClaw's capabilities by providing:

1. **Unified Interface**: Single protocol for all external services
2. **Better Performance**: Direct API access with optimized clients
3. **Enhanced Security**: Centralized credential management
4. **Improved Reliability**: Built-in retry logic and fallbacks
5. **Easier Maintenance**: Standardized configuration and updates

The phased approach ensures minimal disruption while gradually expanding capabilities. Starting with high-value services (Gmail, BigQuery, GitHub) provides immediate benefits while building foundation for future expansions.

## Next Steps

1. Review this plan with Bob
2. Prioritize Phase 1 services
3. Begin Gmail MCP integration
4. Set up monitoring infrastructure
5. Document lessons learned

---

*Created: March 18, 2026*
*Author: Momotaro (OpenClaw Agent)*
*Status: Draft - Pending Review*