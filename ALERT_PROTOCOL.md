# Alert Protocol — System Failures & Degradation

When I detect ANY of these, I MUST alert Bob immediately:

## Critical Failures (Alert Immediately)
- ❌ API quota exceeded (OpenAI, Brave, HF, Cloudflare, etc.)
- ❌ Service unreachable (GitHub, Vercel, AWS, etc.)
- ❌ Authentication failures
- ❌ Data loss or corruption
- ❌ Security incidents
- ❌ Disk space critical
- ❌ Memory/CPU overload

## Degradation (Alert When Detected)
- 🟡 Slow response times (>5s for quick task)
- 🟡 Rate limiting (HTTP 429)
- 🟡 Partial failures (some features working, some not)
- 🟡 Quota approaching limit (>80% used)
- 🟡 Retry loops or repeated failures

## Alert Format
```
⚠️ ALERT: [Service Name]
Status: [Critical/Warning]
Error: [What happened]
Impact: [What's affected]
Action: [What I'm doing / What you should do]
```

## What NOT to Do
- ❌ Silently work around failures
- ❌ Assume Bob will notice
- ❌ Defer alerts until next session
- ❌ Continue operations if service is down
- ❌ Make important decisions without knowing failures

## Examples

### Example 1: API Quota Exceeded
```
⚠️ ALERT: OpenAI Embeddings API
Status: CRITICAL
Error: Quota exceeded (429)
Impact: memory_search() unavailable, cannot search memory files
Action: I can read files directly for now. 
        You should: Check OpenAI billing → increase quota or switch to local embeddings
```

### Example 2: Service Rate Limited
```
⚠️ ALERT: Brave Search API
Status: WARNING
Error: Rate limited (HTTP 429)
Impact: web_search() may be slower, results delayed
Action: Backing off requests. You should: Monitor usage, may need upgrade
```

### Example 3: GitHub Unreachable
```
⚠️ ALERT: GitHub API
Status: CRITICAL
Error: Connection timeout (all retries failed)
Impact: Cannot push commits, pull code, check status
Action: GitHub appears to be down or unreachable. 
        You should: Check https://www.githubstatus.com
```

## Response Expectations
- Bob should see alerts immediately (not buried in output)
- Alerts should be actionable (what to do)
- Critical alerts should suggest workarounds
- Bob may respond with "fix it" or "ignore it" or ask for details

## Implementation
- When I detect an issue: Stop, alert, then ask how to proceed
- Don't assume you want me to work around silently
- Don't assume the issue will resolve itself
- Be explicit about impact and options
