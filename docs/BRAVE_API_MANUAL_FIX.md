# Brave API - Manual Fix Instructions

**Status:** Gateway needs `BRAVE_API_KEY` environment variable  
**Date:** March 17, 2026, 1:05 PM EDT  

---

## Problem Summary

- ✅ API key is valid (`REDACTED_BRAVE_API_TOKEN`)
- ✅ Config file has the key (in `~/.openclaw/config.json`)
- ❌ Gateway process doesn't have `BRAVE_API_KEY` in its environment
- ❌ web_search() fails with "missing_brave_api_key"

---

## Manual Fix (Recommended)

### Step 1: Open the plist file

```bash
open ~/Library/LaunchAgents/ai.openclaw.gateway.plist
```

This opens in your default editor (TextEdit or similar).

### Step 2: Find the EnvironmentVariables section

Look for:
```xml
<key>EnvironmentVariables</key>
<dict>
  ...existing variables...
</dict>
```

### Step 3: Add BRAVE_API_KEY

Inside the `<dict>` (between the existing environment variables), add:

```xml
<key>BRAVE_API_KEY</key>
<string>REDACTED_BRAVE_API_TOKEN</string>
```

**Example of what it should look like:**

```xml
<key>EnvironmentVariables</key>
<dict>
  <key>HOME</key>
  <string>/Users/rreilly</string>
  <key>TMPDIR</key>
  <string>/var/folders/q8/4n1j8yv17j5fdzc0c2wfbm4r0000gn/T/</string>
  <key>NODE_EXTRA_CA_CERTS</key>
  <string>/etc/ssl/cert.pem</string>
  
  <!-- ADD THIS LINE: -->
  <key>BRAVE_API_KEY</key>
  <string>REDACTED_BRAVE_API_TOKEN</string>
</dict>
```

### Step 4: Save the file

Command+S (or File → Save)

### Step 5: Restart Gateway

```bash
# Kill the running Gateway
pkill -f "openclaw.*gateway"

# Wait for launchd to restart it automatically
sleep 5
```

Or just close and reopen OpenClaw app.

### Step 6: Test web_search

Once Gateway is running, it should work:

```
web_search "test query"
```

---

## Why This Works

1. **plist file** defines the Gateway service for launchd
2. **EnvironmentVariables section** sets environment variables for the process
3. **BRAVE_API_KEY** tells web_search tool where to find the API key
4. **Gateway will restart** with the new environment variable

---

## Alternative: Command-line Fix

If you prefer command-line, use this (requires copy/paste):

```bash
# Backup first
cp ~/Library/LaunchAgents/ai.openclaw.gateway.plist ~/Library/LaunchAgents/ai.openclaw.gateway.plist.backup

# Add BRAVE_API_KEY using Python
python3 << 'EOF'
import plistlib
import os

plist_path = os.path.expanduser("~/Library/LaunchAgents/ai.openclaw.gateway.plist")

with open(plist_path, 'rb') as f:
    plist = plistlib.load(f)

if 'EnvironmentVariables' not in plist:
    plist['EnvironmentVariables'] = {}

plist['EnvironmentVariables']['BRAVE_API_KEY'] = 'REDACTED_BRAVE_API_TOKEN'

with open(plist_path, 'wb') as f:
    plistlib.dump(plist, f)

print("✅ BRAVE_API_KEY added to plist")
EOF

# Restart Gateway
pkill -f "openclaw.*gateway"
sleep 5
```

---

## Verification

After restarting, check that the variable is set:

```bash
# Should show BRAVE_API_KEY in the output
defaults read ~/Library/LaunchAgents/ai.openclaw.gateway.plist EnvironmentVariables | grep BRAVE
```

---

## If It Still Doesn't Work

Check:

1. **Is Gateway running?**
   ```bash
   pgrep -f "openclaw.*gateway"
   ```

2. **Is the plist valid?**
   ```bash
   plutil -lint ~/Library/LaunchAgents/ai.openclaw.gateway.plist
   ```

3. **Did you save the file?**
   - Check modification time: `ls -la ~/Library/LaunchAgents/ai.openclaw.gateway.plist`

4. **Did you restart Gateway?**
   ```bash
   pkill -f "openclaw.*gateway"
   sleep 5
   pgrep -f "openclaw.*gateway"  # Should show a new PID
   ```

---

## Key Info

- **API Key:** `REDACTED_BRAVE_API_TOKEN`
- **Plist location:** `~/Library/LaunchAgents/ai.openclaw.gateway.plist`
- **Config location:** `~/.openclaw/config.json`
- **Backup:** Made at `~/Library/LaunchAgents/ai.openclaw.gateway.plist.backup`

---

## Summary

The fix is simple:
1. Open the plist file
2. Add `BRAVE_API_KEY` to EnvironmentVariables
3. Save
4. Restart Gateway
5. web_search() will work

