# Discord Setup Guide - Momotaro & OpenClaw

Complete Discord integration for Momotaro (OpenClaw bot) in your Discord server.

## Overview

This guide covers:
1. Creating a Discord server
2. Setting up the Momotaro bot
3. Configuring OpenClaw integration
4. Testing and verification
5. Troubleshooting

## Phase 1: Create Discord Server

### Step 1: New Server
1. Open Discord (https://discord.com/app)
2. Click **"+"** on the left sidebar
3. Select **"Create My Own"**
4. Server name: **"Momotaro & OpenClaw"**
5. Region: Select closest to your location (US recommended)
6. Click **Create**

### Step 2: Save Server ID
1. Go to **Server Settings** (gear icon)
2. Click **"About Server"** or **"Server Information"**
3. Copy **Server ID** (shown at top or under "Server ID")
4. Save this ID — you'll need it for OpenClaw config

### Step 3: Create Channels

Create these 7 channels in your server:

| Channel | Purpose | Permissions |
|---------|---------|------------|
| **#general** | Main chat with Momotaro | Public (everyone) |
| **#subagents** | Subagent task results | Public (everyone) |
| **#telegraph** | Published Telegraph articles | Public (everyone) |
| **#heartbeat** | Daily status reports | Public (everyone) |
| **#archive** | Searchable conversation archive | Public (everyone) |
| **#dev-tools** | Development commands | Bob only (restricted) |
| **#logs** | Error logs & system messages | Bob only (restricted) |

**To create channels:**
1. Right-click server name → **Create Channel**
2. Name: (use names above, with **#** prefix)
3. Channel Type: **Text**
4. Click **Create**

### Step 4: Set Channel Permissions

**For #dev-tools and #logs (Bob only):**
1. Right-click channel → **Edit Channel**
2. Click **Permissions**
3. Click **+ Add override** → Select **@everyone**
4. Set:
   - ✗ View Channel (deny)
   - ✗ Send Messages (deny)
5. Click **+ Add override** → Select your username (Bob)
6. Set:
   - ✓ View Channel (allow)
   - ✓ Send Messages (allow)
7. Click **Save Changes**

**All other channels:** Leave as default (public)

### Step 5: Enable Threads

1. Go to **Server Settings** → **Moderation**
2. Enable **"Auto Moderation"** (optional, but recommended)
3. Go back to **General** tab
4. Ensure **"Default notification level"** is appropriate for your needs

---

## Phase 2: Create Discord Bot

### Step 1: Create Application
1. Go to https://discord.com/developers/applications
2. Click **"New Application"**
3. Name: **"Momotaro"** (or "OpenClaw Assistant")
4. Accept Terms of Service
5. Click **Create**
6. **Copy Application ID** (shown on General info page) — save this

### Step 2: Create Bot User
1. Click **"Bot"** in left sidebar
2. Click **"Add Bot"**
3. Username will auto-fill as "Momotaro"

### Step 3: Configure Bot Intents & Token

**Copy Bot Token:**
1. Under **TOKEN**, click **Copy**
2. **SAVE THIS SECURELY** — treat it like a password
3. Store in 1Password vault (see Phase 3)
4. ⚠️ **Never commit to git or share publicly**

**Enable Required Intents:**
1. Scroll to **Privileged Gateway Intents**
2. Toggle **ON**:
   - ✓ Message Content Intent (read message content)
   - ✓ Server Members Intent (see who's online)
   - ✓ Presence Intent (optional, for status updates)
3. Click **Save Changes**

**Disable Public Bot:**
1. Scroll to **Public Bot** section
2. Toggle **OFF** (make bot private to Bob)
3. Click **Save Changes**

### Step 4: Set Bot Permissions

1. Click **OAuth2** in left sidebar
2. Click **URL Generator**
3. Select **Scopes**:
   - ✓ bot
4. Select **Permissions** (under Scopes):
   - ✓ View Channels
   - ✓ Send Messages
   - ✓ Embed Links
   - ✓ Attach Files
   - ✓ Read Message History
   - ✓ Mention @everyone, @here, and @[Role] (optional)
   - ✓ Add Reactions
   - ✓ Use Slash Commands
5. Copy the **Generated URL** at the bottom

### Step 5: Authorize Bot to Server

1. Paste the URL from Step 4 into your browser
2. Select your server **"Momotaro & OpenClaw"** from dropdown
3. Confirm permissions
4. Click **Authorize**
5. Complete CAPTCHA (if prompted)
6. Bot should now appear in your Discord server (offline, grey icon)

---

## Phase 3: Configure OpenClaw

### Step 1: Gather Required IDs

Before configuring OpenClaw, collect these from Discord:

```
Server ID:        [from Phase 1, Step 2]
Bot Token:        [from Phase 2, Step 3]
Application ID:   [from Phase 2, Step 1]

Channel IDs (right-click each channel → Copy Channel ID):
#general:         [CHANNEL_ID]
#subagents:       [CHANNEL_ID]
#telegraph:       [CHANNEL_ID]
#heartbeat:       [CHANNEL_ID]
#archive:         [CHANNEL_ID]
#dev-tools:       [CHANNEL_ID]
#logs:            [CHANNEL_ID]
```

### Step 2: Create Discord Config

Create file: `~/.openclaw/config/discord.json`

```json
{
  "bot": {
    "token": "YOUR_BOT_TOKEN_HERE",
    "command_prefix": "!",
    "status": "Playing with Momotaro"
  },
  "server": {
    "id": "YOUR_SERVER_ID_HERE",
    "channels": {
      "general": "GENERAL_CHANNEL_ID",
      "subagents": "SUBAGENTS_CHANNEL_ID",
      "telegraph": "TELEGRAPH_CHANNEL_ID",
      "heartbeat": "HEARTBEAT_CHANNEL_ID",
      "archive": "ARCHIVE_CHANNEL_ID",
      "dev_tools": "DEV_TOOLS_CHANNEL_ID",
      "logs": "LOGS_CHANNEL_ID"
    }
  },
  "features": {
    "auto_threading": true,
    "auto_embed_telegraph": true,
    "archive_messages": true,
    "telegraph_formatting": true,
    "mention_on_reply": false
  }
}
```

**Replace:**
- `YOUR_BOT_TOKEN_HERE` — Token from Phase 2
- `YOUR_SERVER_ID_HERE` — Server ID from Phase 1
- All `CHANNEL_ID` values — From your Discord channels

### Step 3: Secure Bot Token (1Password)

1. Open 1Password
2. Create new item:
   - Title: **"Discord Bot Token - Momotaro"**
   - Category: **Password**
   - Password: [paste bot token]
   - Vault: **"OpenClaw Secrets"**
3. Add notes with:
   - Server ID
   - Application ID
   - Creation date (today)
4. Save

### Step 4: Update .gitignore

Add to `~/.openclaw/workspace/.gitignore`:

```
# Discord configuration
config/discord.json
.discord_token
discord_token.txt
```

### Step 5: Test Configuration

```bash
# Validate Discord config syntax
python3 -m json.tool ~/.openclaw/config/discord.json

# Should output: valid JSON with no errors
```

---

## Phase 4: OpenClaw Gateway Integration

### Step 1: Update Gateway Config

Edit `~/.openclaw/config.json` and add/update:

```json
{
  "channels": ["telegram", "discord"],
  "discord": {
    "enabled": true,
    "config_path": "~/.openclaw/config/discord.json"
  }
}
```

### Step 2: Restart Gateway

```bash
# Restart OpenClaw gateway
openclaw gateway restart

# Check status
openclaw gateway status

# View logs (last 30 lines)
openclaw gateway logs --lines 30
```

**Expected output:**
- `Status: running`
- No errors in logs
- Bot should go **online** (green dot) in Discord within 30 seconds

### Step 3: Verify Bot Connection

In Discord:
1. Look at member list (right sidebar)
2. Find **"Momotaro"** 
3. Should show **green online status** ✓
4. Click profile to verify it's the bot

---

## Phase 5: Manual Testing

### Test 1: Send Message to Momotaro
1. Go to **#general** channel
2. Type: `@Momotaro Hello!`
3. Expected: Bot responds within 2-5 seconds
4. ✓ Pass: Bot responds
5. ✗ Fail: No response → Check logs

### Test 2: Telegraph Auto-Post
1. Publish an article via Telegraph CLI
2. Go to **#telegraph** channel
3. Expected: Article title + link posted automatically
4. ✓ Pass: Article appears
5. ✗ Fail: Check logs for errors

### Test 3: Reactions
1. Post a message in **#general**
2. Add emoji reaction (👍, ❤️, etc.)
3. Expected: Reaction appears
4. ✓ Pass: Reaction visible
5. ✗ Fail: Check bot permissions

### Test 4: Threads
1. Go to **#general**
2. Right-click a message → **Create Thread**
3. Name: "Test thread"
4. Post reply in thread
5. ✓ Pass: Thread created and usable
6. ✗ Fail: Channel permissions issue

---

## Troubleshooting

### Bot Won't Go Online
**Symptom:** Momotaro shows offline (grey icon)

**Solutions:**
1. Check bot token in config is correct
2. Verify gateway is running: `openclaw gateway status`
3. Check logs: `openclaw gateway logs --lines 50`
4. Restart gateway: `openclaw gateway restart`

### Can't Send Messages to Bot
**Symptom:** Messages to @Momotaro don't get responses

**Solutions:**
1. Verify bot has "Send Messages" permission
2. Check #logs channel for error messages
3. Try in #general (other channels might be restricted)
4. Verify bot token has Message Content Intent enabled

### Messages Spam/Double Post
**Symptom:** Bot responds multiple times to same message

**Solutions:**
1. Check gateway logs for duplicate handlers
2. Ensure only one gateway instance running
3. Restart gateway: `openclaw gateway restart`

### Telegraph Articles Don't Auto-Post
**Symptom:** Published articles not appearing in #telegraph

**Solutions:**
1. Check Telegraph API token in `config/telegraph.json`
2. Verify #telegraph channel ID is correct in discord.json
3. Check logs: `openclaw gateway logs --lines 100`
4. Test Telegraph manually: `python3 ~/.openclaw/workspace/scripts/telegraph-cli.py status`

### Permission Denied on #dev-tools or #logs
**Symptom:** Can't access Bob-only channels

**Solutions:**
1. Verify channel permissions are set correctly (see Phase 1, Step 4)
2. Make sure your Discord account is the server owner
3. Try removing and re-adding permission override
4. Restart Discord app

---

## Channel Guidelines

### #general
- Ask Momotaro questions
- Chat about projects
- Get responses and ideas
- Public channel — everyone can see

### #telegraph
- Published articles (auto-posted)
- Long-form content
- Research summaries
- Click links to read full articles

### #subagents
- Task results from subagents
- Progress updates
- Completion reports
- Technical output

### #heartbeat
- Daily status reports
- Calendar summaries
- Metrics and KPIs
- Auto-posted at scheduled times

### #archive
- Searchable message archive
- Historical conversations
- Reference material
- Use `/search [query]` to find content

### #dev-tools
- Development commands
- System utilities
- Admin functions
- **Bob only**

### #logs
- Error messages
- System alerts
- Debug output
- **Bob only**

---

## Commands Reference

### Basic Commands
```
@Momotaro [question]      Ask Momotaro a question
/search [query]           Search message archive
/config [setting] [value] Change settings (dev-tools only)
/status                   Check bot status
```

### Admin Commands (Bob only, #dev-tools)
```
/restart                  Restart Discord integration
/reload-config            Reload discord.json
/test-telegraph           Test Telegraph publishing
/archive-export           Export message archive to JSON
/purge-logs [days]        Delete logs older than N days
```

---

## Next Steps

1. ✅ Create Discord server
2. ✅ Create bot and get token
3. ✅ Configure OpenClaw
4. ✅ Run tests
5. Start chatting with Momotaro in #general!

---

## Support

If something isn't working:

1. Check **#logs** channel (Bob only)
2. Run: `openclaw gateway logs --lines 100`
3. Search docs: `~/.openclaw/workspace/docs/`
4. Check TOOLS.md for configuration details

Good luck! 🍑
