# Discord + Momotaro Quick Start

**TL;DR:** Create server → Create bot → Get token → Done

---

## Step 1: Create Discord Server (5 min)

1. Open Discord: https://discord.com/app
2. Click **"+"** on left sidebar
3. Click **"Create My Own"**
4. **Name:** "Momotaro & OpenClaw"
5. **Region:** US East
6. Click **Create**
7. **Right-click server → Server Settings → "About Server"**
8. **Copy "Server ID"** — save this! 📌

---

## Step 2: Create 7 Channels (10 min)

Right-click server name → "Create Channel" for each:

1. **#general** (public)
2. **#subagents** (public)
3. **#telegraph** (public)
4. **#heartbeat** (public)
5. **#archive** (public)
6. **#dev-tools** (Bob only)
7. **#logs** (Bob only)

**For #dev-tools and #logs:**
- Right-click channel → Edit Channel → Permissions
- Add override for @everyone: **Deny** view + send
- Add override for yourself: **Allow** view + send

---

## Step 3: Create Bot (5 min)

1. Open: https://discord.com/developers/applications
2. Click **"New Application"**
3. **Name:** "Momotaro"
4. Accept terms → **Create**
5. Click **"Bot"** in sidebar
6. Click **"Add Bot"**
7. Under **TOKEN**: **Copy** (this is your bot password 🔐)

**Enable Intents:**
- Find "Privileged Gateway Intents"
- Toggle **ON**:
  - ✓ Message Content Intent
  - ✓ Server Members Intent

---

## Step 4: Authorize Bot (2 min)

1. Click **"OAuth2"** in sidebar
2. Click **"URL Generator"**
3. Check: **bot**
4. Check permissions:
   - ✓ View Channels
   - ✓ Send Messages
   - ✓ Embed Links
   - ✓ Attach Files
   - ✓ Read Message History
   - ✓ Add Reactions
   - ✓ Use Slash Commands
5. **Copy** the URL at bottom
6. **Paste in browser**
7. **Select your server** from dropdown
8. **Authorize**

Bot should now appear in your server (grey/offline) 🤖

---

## Step 5: Collect All IDs (3 min)

**From Discord:**

```
Server ID:        [Settings → About Server]
Application ID:   [Developer Portal → Application]
Bot Token:        [Developer Portal → Bot → TOKEN]

Channel IDs (right-click each channel, Copy ID):
#general:         [PASTE_ID]
#subagents:       [PASTE_ID]
#telegraph:       [PASTE_ID]
#heartbeat:       [PASTE_ID]
#archive:         [PASTE_ID]
#dev-tools:       [PASTE_ID]
#logs:            [PASTE_ID]
```

---

## Step 6: Send to Momotaro

**Reply to Momotaro with:**

```
Server ID: XXX
Bot Token: XYZ...
Bot Application ID: ABC...

#general: CHANNEL_ID
#subagents: CHANNEL_ID
#telegraph: CHANNEL_ID
#heartbeat: CHANNEL_ID
#archive: CHANNEL_ID
#dev-tools: CHANNEL_ID
#logs: CHANNEL_ID
```

---

## Done! 🎉

Once you send the IDs, Momotaro will:
1. Create config file
2. Start bot
3. Connect gateway
4. Run tests
5. Send confirmation

---

## Troubleshooting

### Bot shows offline?
- Check bot token is correct
- Verify it was authorized

### Can't see bot in server?
- Check permissions were set correctly
- Re-invite bot using OAuth2 URL

### Discord says "Invalid Token"?
- Bot token has a space or typo
- Copy again, very carefully

---

## For Reference

**Full setup guide:** `docs/DISCORD_SETUP.md`  
**Status tracker:** `DISCORD_DEPLOYMENT_STATUS.md`  
**Questions?** Check DISCORD_SETUP.md troubleshooting section

---

**Estimated time:** ~25 minutes total  
**Difficulty:** Easy (just copying IDs)  
**You've got this! 🍑**
