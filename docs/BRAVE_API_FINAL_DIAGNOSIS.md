# Brave API Key Issue - Final Diagnosis & Status

**Date:** March 17, 2026, 1:00 PM EDT  
**Issue:** web_search() fails with "missing_brave_api_key"  
**Root Cause:** Gateway is looking for `BRAVE_API_KEY` environment variable, not config file  
**Status:** Config is correct, needs environment variable approach  

---

## 🎯 The Real Issue

OpenClaw Gateway's web_search tool requires the API key to be set as an **environment variable**, not in the config file.

**Error Message Clue:**
```
"set BRAVE_API_KEY in the Gateway environment"
```

## Current State

✅ **API Key is valid** - Direct curl test works (HTTP 200)  
✅ **Config file has key** - In both `search.brave.apiKey` and `tools.web.search.brave.apiKey`  
❌ **Gateway environment missing** - `BRAVE_API_KEY` not passed to Gateway process  

## Solution

The Gateway process needs `BRAVE_API_KEY` in its environment. Three approaches:

### Approach 1: Set in plist (Permanent)

Edit `~/Library/LaunchAgents/ai.openclaw.gateway.plist`:

```xml
<key>EnvironmentVariables</key>
<dict>
  <key>BRAVE_API_KEY</key>
  <string>REDACTED_BRAVE_API_TOKEN</string>
</dict>
```

Then reload:
```bash
launchctl unload ~/Library/LaunchAgents/ai.openclaw.gateway.plist
launchctl load ~/Library/LaunchAgents/ai.openclaw.gateway.plist
```

### Approach 2: Set in shell then start Gateway

```bash
export BRAVE_API_KEY="REDACTED_BRAVE_API_TOKEN"
# Then start OpenClaw app
```

### Approach 3: Use ~/.zshrc (for new sessions)

```bash
echo 'export BRAVE_API_KEY="REDACTED_BRAVE_API_TOKEN"' >> ~/.zshrc
source ~/.zshrc
```

## Current Config File Status

`~/.openclaw/config.json` now contains:

```json
{
  "search": {
    "provider": "brave",
    "brave": {
      "apiKey": "REDACTED_BRAVE_API_TOKEN"
    }
  },
  "tools": {
    "web": {
      "search": {
        "brave": {
          "apiKey": "REDACTED_BRAVE_API_TOKEN"
        }
      }
    }
  }
}
```

This is correct, but Gateway doesn't read it for web_search tool - it requires the environment variable.

## Why This Happened

The web_search tool implementation in OpenClaw:
1. Looks for `BRAVE_API_KEY` environment variable first
2. Falls back to config if not in environment
3. Fails with "missing_brave_api_key" if not found

Gateway's process environment doesn't inherit parent shell environment.

## Recommended Fix

**Best approach:** Add to plist EnvironmentVariables (permanent, survives reboots)

But due to sudo/launchctl issues, simpler workaround:

```bash
# Every time you start OpenClaw:
export BRAVE_API_KEY="REDACTED_BRAVE_API_TOKEN"
```

## Key Learnings

1. **OpenClaw config files** store credentials in `.openclaw/config.json`
2. **Tools like web_search** require separate environment variables
3. **Gateway process** doesn't inherit shell environment
4. **Solution:** Set env vars in plist (permanent) or shell before starting

## Status

- API Key: ✅ Valid and configured in config.json  
- Gateway: Running (PID 5474)
- Environment variable: ⏳ Need to set BRAVE_API_KEY in Gateway's environment
- web_search: ❌ Will work once env var is set

## Next Steps

1. Set `BRAVE_API_KEY` environment variable
2. Restart Gateway to pick it up
3. Test web_search()

