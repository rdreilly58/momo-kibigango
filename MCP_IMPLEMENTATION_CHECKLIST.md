# MCP Implementation Checklist

**Project**: OpenClaw MCP Integration  
**Phase**: 1 (Core Services)  
**Timeline**: 3-4 days  
**Status**: Ready to Start  

---

## Pre-Implementation (Before Day 1)

### Environment Setup
- [ ] Read MCP_SUMMARY.md (executive overview)
- [ ] Read MCP_INTEGRATION_PLAN.md (main strategy)
- [ ] Review MCP_PHASE1_SETUP.md (installation steps)
- [ ] Get approval from Bob to proceed

### System Verification
- [ ] Verify Node.js 18+ installed: `node --version`
- [ ] Verify mcporter installed: `which mcporter`
- [ ] Check mcporter version: `mcporter --version`
- [ ] Verify OpenClaw running: `openclaw status`
- [ ] Create backup directory: `mkdir -p ~/.openclaw/backups`

### Credential Preparation
- [ ] Have Google account credentials ready (rdreilly2010@gmail.com)
- [ ] Locate GitHub PAT or create new one
- [ ] Prepare AWS credentials or create new user
- [ ] Prepare Slack workspace (must be admin)
- [ ] Have 1Password CLI ready: `which op`

### Workspace Setup
- [ ] Create OAuth directory: `mkdir -p ~/.mcporter/oauth`
- [ ] Backup mcporter.json: `cp ~/.mcporter/mcporter.json ~/.mcporter/mcporter.json.bak-$(date +%Y%m%d)`
- [ ] Create logs directory: `mkdir -p ~/.openclaw/logs`
- [ ] Set permissions: `chmod 700 ~/.mcporter/oauth`

---

## Day 1: Gmail MCP Setup

### Morning - Preparation (1 hour)
- [ ] Review MCP_PHASE1_SETUP.md "Gmail MCP Setup" section
- [ ] Have MCP_AUTHENTICATION_GUIDE.md open for reference
- [ ] Verify Google account access
- [ ] Create clean workspace

### Gmail Configuration (2-3 hours)

#### Step 1: Verify Google Authentication
- [ ] Check gog authentication: `gog auth status`
- [ ] If not authenticated, login: `gog login rdreilly2010@gmail.com`
- [ ] Verify access: `gog gmail search 'from:rdreilly2010@gmail.com' --limit 1`
- [ ] Document result: ___________________________

#### Step 2: Export OAuth Token
- [ ] Verify token location: `ls -la ~/.config/gog/oauth-token.json`
- [ ] Copy token: `cp ~/.config/gog/oauth-token.json ~/.mcporter/oauth/gmail.json`
- [ ] Verify copy: `ls -la ~/.mcporter/oauth/gmail.json`
- [ ] Set permissions: `chmod 600 ~/.mcporter/oauth/gmail.json`

#### Step 3: Install Gmail MCP Server
- [ ] Try first option: `npm install -g mcp-server-gmail`
  - [ ] If successful, note version: _______________
  - [ ] If fails, try fallback: `npm install -g @modelcontextprotocol/server-gmail`
- [ ] Verify install: `which mcp-server-gmail` or `which @modelcontextprotocol/server-gmail`

#### Step 4: Update mcporter Configuration
- [ ] Open current config: `cat ~/.mcporter/mcporter.json | jq . | less`
- [ ] Add Gmail to mcporter.json (see template in MCP_PHASE1_SETUP.md)
- [ ] Verify JSON syntax: `jq . ~/.mcporter/mcporter.json`
- [ ] Test list: `mcporter list gmail`

#### Step 5: Test Gmail MCP
- [ ] List tools: `mcporter list gmail --schema`
- [ ] Search test: `mcporter call gmail.search --args '{"query":"from:rdreilly2010@gmail.com","limit":5}'`
- [ ] Expected: < 2 seconds response
- [ ] Actual response time: _______________ seconds
- [ ] Result: ✅ PASS / ❌ FAIL

### Evening - Documentation (1 hour)
- [ ] Document any issues encountered
- [ ] Note response times
- [ ] Save test output to file
- [ ] Update implementation log

**Day 1 Status**: ✅ Complete / ⏳ In Progress / ❌ Blocked

---

## Day 2: BigQuery MCP Setup

### Morning - Preparation (30 min)
- [ ] Review BigQuery section in MCP_PHASE1_SETUP.md
- [ ] Verify GCP project: `gcloud projects list | grep 127601657025`
- [ ] Locate service account key

### BigQuery Configuration (2-3 hours)

#### Step 1: Prepare Service Account
- [ ] Find service account file: `ls -la ~/.gcp/*service-account.json`
- [ ] Expected path: `~/.gcp/127601657025-service-account.json`
- [ ] Verify contents: `cat ~/.gcp/127601657025-service-account.json | jq '.project_id'`
- [ ] Should return: `127601657025`

#### Step 2: Copy to OAuth Directory
- [ ] Copy file: `cp ~/.gcp/127601657025-service-account.json ~/.mcporter/oauth/bigquery-sa.json`
- [ ] Verify: `ls -la ~/.mcporter/oauth/bigquery-sa.json`
- [ ] Set permissions: `chmod 600 ~/.mcporter/oauth/bigquery-sa.json`
- [ ] Verify key has required roles: `gcloud projects get-iam-policy 127601657025 --flatten="bindings[].members" --filter="members:serviceAccount*"`

#### Step 3: Install BigQuery MCP Server
- [ ] Install: `npm install -g mcp-server-bigquery`
- [ ] Verify: `which mcp-server-bigquery`
- [ ] Check version: `npm list -g mcp-server-bigquery`

#### Step 4: Update mcporter Configuration
- [ ] Add BigQuery server to mcporter.json
- [ ] Set env variables:
  - [ ] GOOGLE_APPLICATION_CREDENTIALS
  - [ ] GCP_PROJECT_ID
- [ ] Verify JSON syntax: `jq . ~/.mcporter/mcporter.json`
- [ ] Reload mcporter: `mcporter daemon restart` (if running)

#### Step 5: Test BigQuery MCP
- [ ] List datasets: `mcporter call bigquery.list_datasets`
- [ ] Expected: See `ga4_reillydesignstudio` in output
- [ ] Sample query: `mcporter call bigquery.query --args '{"sql":"SELECT COUNT(*) as event_count FROM \`127601657025.ga4_reillydesignstudio.events_*\` WHERE _TABLE_SUFFIX = FORMAT_DATE(\"%Y%m%d\", CURRENT_DATE()-1) LIMIT 1"}'`
- [ ] Expected: < 3 seconds, numeric result
- [ ] Actual response time: _______________ seconds
- [ ] Result: ✅ PASS / ❌ FAIL

### Evening - Verification (1 hour)
- [ ] Document BigQuery test results
- [ ] Compare GA4 data with web analytics dashboard
- [ ] Note any anomalies
- [ ] Save test queries for reference

**Day 2 Status**: ✅ Complete / ⏳ In Progress / ❌ Blocked

---

## Day 3: GitHub Enhancement & Slack Setup

### Morning - GitHub Enhancement (1 hour)

#### GitHub Verification
- [ ] Check current config: `mcporter list github`
- [ ] List GitHub tools: `mcporter list github --schema | head -20`
- [ ] Test list repos: `mcporter call github.list_repos --limit 1`
- [ ] Expected: Responds in < 1 second
- [ ] Actual response time: _______________ seconds

#### GitHub Enhancements
- [ ] Add retry settings to config
- [ ] Add timeout settings (30000ms)
- [ ] Add rate limit handling
- [ ] Add caching configuration
- [ ] Verify config syntax: `jq . ~/.mcporter/mcporter.json | grep -A 10 '"github"'`

#### GitHub Testing
- [ ] Test: `mcporter call github.get_user`
- [ ] Test: `mcporter call github.list_issues repo=openclaw/openclaw state=open limit:5`
- [ ] Results: ✅ PASS / ❌ FAIL

### Afternoon - Slack Setup (2-3 hours)

#### Step 1: Create Slack App
- [ ] Go to https://api.slack.com/apps
- [ ] Click "Create New App" → "From scratch"
- [ ] Name: "OpenClaw MCP"
- [ ] Select workspace
- [ ] Write down App ID: _______________

#### Step 2: Configure OAuth & Permissions
- [ ] Go to "OAuth & Permissions"
- [ ] Add these Bot Token Scopes:
  - [ ] channels:history
  - [ ] channels:read
  - [ ] chat:write
  - [ ] groups:read
  - [ ] im:history
  - [ ] im:read
  - [ ] users:read
  - [ ] files:read
- [ ] Scroll to "OAuth Tokens for Your Workspace"
- [ ] Click "Install to Workspace"
- [ ] Authorize the app
- [ ] Copy Bot Token (starts with xoxb-): _______________
- [ ] Save to file: `echo "xoxb-..." > ~/.mcporter/oauth/slack/bot.token`

#### Step 3: Generate App Token
- [ ] Go back to app settings
- [ ] Click "Socket Mode"
- [ ] Enable Socket Mode
- [ ] Click "Generate" for app-level token
- [ ] Scopes needed:
  - [ ] connections:write
- [ ] Copy App Token (starts with xapp-): _______________
- [ ] Save to file: `echo "xapp-..." > ~/.mcporter/oauth/slack/app.token`

#### Step 4: Install Slack MCP Server
- [ ] Create slack directory: `mkdir -p ~/.mcporter/oauth/slack`
- [ ] Set permissions: `chmod 700 ~/.mcporter/oauth/slack`
- [ ] Install server: `npm install -g @modelcontextprotocol/server-slack`
- [ ] Verify: `which @modelcontextprotocol/server-slack` (or similar)

#### Step 5: Update mcporter Configuration
- [ ] Add Slack to mcporter.json
- [ ] Set env variables for bot and app tokens
- [ ] Verify config syntax: `jq . ~/.mcporter/mcporter.json`

#### Step 6: Test Slack MCP
- [ ] List channels: `mcporter call slack.list_channels`
- [ ] Expected: Shows channels in workspace
- [ ] List users: `mcporter call slack.list_users --limit 5`
- [ ] Expected: Shows users
- [ ] Send test message (use test channel):
  ```bash
  mcporter call slack.post_message --args '{
    "channel":"C_TEST_CHANNEL_ID",
    "text":"Test message from MCP"
  }'
  ```
- [ ] Verify message in Slack: ✅ PASS / ❌ FAIL

### Evening - Integration Verification (1 hour)
- [ ] Document all tests
- [ ] Note any issues
- [ ] Verify all services respond
- [ ] Check mcporter list output

**Day 3 Status**: ✅ Complete / ⏳ In Progress / ❌ Blocked

---

## Day 4: Comprehensive Testing & Monitoring

### Morning - Full Integration Testing (2 hours)

#### Create Test Script
- [ ] Copy test script from MCP_PHASE1_SETUP.md
- [ ] Save as: `~/.openclaw/workspace/scripts/test-mcp-phase1.sh`
- [ ] Make executable: `chmod +x ~/.openclaw/workspace/scripts/test-mcp-phase1.sh`
- [ ] Run tests: `~/.openclaw/workspace/scripts/test-mcp-phase1.sh`

#### Run Service Tests
- [ ] Gmail tests: 
  - [ ] Search (must return < 2s)
  - [ ] List labels
- [ ] BigQuery tests:
  - [ ] List datasets
  - [ ] Sample query
- [ ] GitHub tests:
  - [ ] List repos
  - [ ] Get user info
- [ ] Slack tests:
  - [ ] List channels
  - [ ] List users

#### Performance Benchmarking
Service | Command | Time (seconds) | Target | Pass?
--------|---------|---|---|---
Gmail | search | ___ | < 2 | [ ]
BigQuery | query | ___ | < 3 | [ ]
GitHub | list_repos | ___ | < 1 | [ ]
Slack | list_channels | ___ | < 1 | [ ]

### Afternoon - Monitoring Setup (2 hours)

#### Health Check Script
- [ ] Copy health check script: `cp ~/.openclaw/workspace/scripts/mcp-health-check.sh ~/.openclaw/workspace/scripts/`
- [ ] Make executable: `chmod +x ~/.openclaw/workspace/scripts/mcp-health-check.sh`
- [ ] Test manually: `~/.openclaw/workspace/scripts/mcp-health-check.sh`
- [ ] Verify log created: `ls -la ~/.openclaw/logs/mcp-health.log`

#### Cron Setup
- [ ] Open crontab: `crontab -e`
- [ ] Add hourly check: `0 * * * * ~/.openclaw/workspace/scripts/mcp-health-check.sh`
- [ ] Verify entry: `crontab -l | grep mcp-health`

#### Log Monitoring
- [ ] Create log directory: `mkdir -p ~/.openclaw/logs`
- [ ] Check logs exist:
  - [ ] `~/.openclaw/logs/mcp-phase1-test.log`
  - [ ] `~/.openclaw/logs/mcp-health.log`
- [ ] Review test results: `cat ~/.openclaw/logs/mcp-phase1-test.log`

### Evening - Issue Resolution (1 hour)
- [ ] Review all test results
- [ ] Document any failures
- [ ] Troubleshoot issues (see MCP_PHASE1_SETUP.md)
- [ ] Re-test failed services
- [ ] Document solutions for future reference

**Day 4 Status**: ✅ Complete / ⏳ In Progress / ❌ Blocked

---

## Day 5: Documentation & Handoff

### Morning - Final Verification (1 hour)
- [ ] Run all services once more
- [ ] Verify credentials still working
- [ ] Check cron jobs active: `crontab -l`
- [ ] Verify all logs created and readable

### Documentation (2 hours)
- [ ] Summarize what was done
- [ ] Document any deviations from plan
- [ ] Note performance metrics
- [ ] Record lessons learned
- [ ] Update README_MCP.md with actual results
- [ ] Create FAQ based on issues encountered

### Knowledge Transfer (1-2 hours)
- [ ] Prepare brief overview for Bob
- [ ] Share MCP_QUICK_REFERENCE.md
- [ ] Demonstrate basic commands
- [ ] Explain fallback procedures
- [ ] Document password/token location
- [ ] Create emergency rollback guide

### Archive & Cleanup (30 min)
- [ ] Archive all logs: `tar -czf ~/.openclaw/logs/mcp-phase1-$(date +%Y%m%d).tar.gz ~/.openclaw/logs/`
- [ ] Backup configs: `cp -r ~/.mcporter ~/.openclaw/backups/mcporter-$(date +%Y%m%d)/`
- [ ] Clean temporary files
- [ ] Verify backups exist

**Day 5 Status**: ✅ Complete / ⏳ In Progress / ❌ Blocked

---

## Success Criteria

### Phase 1 Complete When:

#### Functionality
- [ ] Gmail MCP responding < 2 seconds
- [ ] BigQuery MCP responding < 3 seconds
- [ ] GitHub MCP responding < 1 second
- [ ] Slack MCP responding < 1 second
- [ ] All services pass integration tests

#### Reliability
- [ ] Each service tested 10+ times
- [ ] Zero authentication failures
- [ ] Fallback procedures verified
- [ ] Automatic recovery working

#### Monitoring
- [ ] Health check script running via cron
- [ ] Logs created and accessible
- [ ] Performance metrics recorded
- [ ] Alerts configured (if applicable)

#### Documentation
- [ ] Lessons learned documented
- [ ] Troubleshooting guide completed
- [ ] Team trained on basic operations
- [ ] Emergency procedures documented

#### Security
- [ ] All credentials in place
- [ ] File permissions correct (600 for oauth/)
- [ ] No tokens in logs or config
- [ ] Audit logging active

---

## Issue Tracking

### Issues Encountered

| # | Service | Issue | Solution | Status |
|---|---------|-------|----------|--------|
| 1 | | | | [ ] |
| 2 | | | | [ ] |
| 3 | | | | [ ] |
| 4 | | | | [ ] |
| 5 | | | | [ ] |

---

## Sign-Off

### Implementation Team
- Implemented by: _________________________ Date: _______
- Verified by: _____________________________ Date: _______

### Approval
- Reviewed by: Bob Reilly Date: _______
- Approved for Phase 2: [ ] YES [ ] NO

### Notes
_________________________________________________________________

_________________________________________________________________

_________________________________________________________________

---

## Next Steps (Phase 2)

After Phase 1 is complete:

- [ ] Review Phase 2 plan
- [ ] Identify additional services to integrate
- [ ] Schedule Phase 2 kickoff meeting
- [ ] Document lessons learned from Phase 1
- [ ] Plan performance optimizations

---

## Emergency Rollback

If critical issues arise:

1. Stop mcporter: `mcporter daemon stop`
2. Restore backup: `cp ~/.mcporter/mcporter.json.bak-YYYYMMDD ~/.mcporter/mcporter.json`
3. Restart: `mcporter daemon start`
4. Document issue in this checklist
5. Contact implementation lead

Full rollback script: See MCP_PHASE1_SETUP.md "Rollback Plan" section

---

*Created: March 18, 2026*  
*Version: 1.0*  
*Last updated: 2026-03-18*