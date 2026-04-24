# Discord Integration - Deployment Status

**Status:** 🟡 AWAITING USER INPUT  
**Last Updated:** March 21, 2026 01:15 EDT  
**Subagent:** Momotaro Discord Setup (depth 1/1)

---

## Current Phase: Phase 1 - User Actions Required

### What's Done ✅
- [x] Documentation created (DISCORD_SETUP.md)
- [x] Bot scaffold code written (discord_bot.py)
- [x] Config templates created (discord.json.example)
- [x] Validation script created (validate_discord_config.py)
- [x] Deployment tracking (this file)

### What's Pending from Bob (User)

**CRITICAL - Must be done by Bob first:**

- [ ] **Step 1.1:** Create Discord server
  - Go to https://discord.com/app
  - Click "+" and create "Momotaro & OpenClaw"
  - Save Server ID
  
- [ ] **Step 1.2:** Create 7 channels
  - #general, #subagents, #telegraph, #heartbeat, #archive, #dev-tools, #logs
  
- [ ] **Step 1.3:** Set channel permissions
  - Restrict #dev-tools and #logs to Bob only
  
- [ ] **Step 2.1:** Create Discord bot application
  - Go to https://discord.com/developers/applications
  - Create "Momotaro" application
  - Save Application ID
  
- [ ] **Step 2.2:** Get bot token
  - Add bot user to application
  - Copy bot token
  - Enable intents (Message Content, Server Members, Presence)
  
- [ ] **Step 2.3:** Authorize bot to server
  - Generate OAuth2 URL with permissions
  - Visit URL and authorize bot
  
- [ ] **Step 3.1:** Collect all IDs
  - Server ID
  - Application ID
  - 7 Channel IDs (right-click each channel)
  - Bot Token

- [ ] **Step 3.2:** Send IDs to Momotaro
  - Message on Telegram or email the data
  - Needed for config file creation

---

## Deployment Checklist

### Phase 1: Discord Server Setup (Bob)
- [ ] Server created
- [ ] 7 channels created
- [ ] Permissions set on #dev-tools and #logs
- [ ] Server ID saved

**Status:** 🔴 NOT STARTED  
**Expected Duration:** 15 minutes

---

### Phase 2: Discord Bot Setup (Bob)
- [ ] Discord Developer Portal application created
- [ ] Bot user added
- [ ] Intents enabled (Message Content, Server Members, Presence)
- [ ] Bot token copied
- [ ] OAuth2 permissions configured
- [ ] Bot authorized to server

**Status:** 🔴 NOT STARTED  
**Expected Duration:** 10 minutes

---

### Phase 3: OpenClaw Configuration (Momotaro)
- [ ] Discord config file created (~/.openclaw/config/discord.json)
- [ ] All IDs populated correctly
- [ ] Permissions set to 600 (chmod 600)
- [ ] Config validated with script
- [ ] Bot token stored in Apple Keychain (DiscordBotToken)

**Status:** ⏳ READY TO EXECUTE (awaiting IDs from Bob)  
**Expected Duration:** 10 minutes

---

### Phase 4: OpenClaw Gateway Integration (Momotaro)
- [ ] Gateway config updated (~/.openclaw/config.json)
- [ ] Discord channel added to gateway
- [ ] Gateway restarted
- [ ] Bot comes online in Discord
- [ ] No errors in gateway logs

**Status:** ⏳ READY TO EXECUTE (after Phase 3)  
**Expected Duration:** 5 minutes

---

### Phase 5: Feature Integration (Momotaro)
- [ ] Telegraph auto-post configured
- [ ] Subagent integration working
- [ ] HEARTBEAT integration working
- [ ] Message archive enabled
- [ ] Search functionality working

**Status:** ⏳ READY TO EXECUTE (after Phase 4)  
**Expected Duration:** 15 minutes

---

### Phase 6: Testing & Verification (Both)
- [ ] Manual test: Send message to @Momotaro
- [ ] Manual test: Telegraph article auto-posts
- [ ] Manual test: Reactions work
- [ ] Manual test: Threads work
- [ ] Permission test: #dev-tools restricted correctly
- [ ] Permission test: #general is public
- [ ] Integration test: Telegraph links render in Discord
- [ ] Integration test: Code blocks format correctly
- [ ] Error handling: Check #logs for errors
- [ ] Auto-reconnect: Stop and restart gateway

**Status:** ⏳ READY TO EXECUTE (after Phase 5)  
**Expected Duration:** 20 minutes

---

### Phase 7: Documentation & Handoff (Momotaro)
- [ ] Discord setup guide completed (DISCORD_SETUP.md) ✅
- [ ] TOOLS.md updated with Discord config
- [ ] AGENTS.md updated with Discord routing
- [ ] Troubleshooting guide created
- [ ] Channel guidelines documented
- [ ] Commands reference created

**Status:** ⏳ READY TO EXECUTE (after Phase 6)  
**Expected Duration:** 15 minutes

---

## File Manifest

### Documentation
- ✅ `docs/DISCORD_SETUP.md` — Complete setup guide for Bob
- 📝 `DISCORD_DEPLOYMENT_STATUS.md` — This file

### Scripts
- ✅ `scripts/discord_bot.py` — Main bot implementation
- ✅ `scripts/validate_discord_config.py` — Config validator

### Configuration Templates
- ✅ `config/discord.json.example` — Template config file
- 📝 `config/discord.json` — Actual config (awaiting user data)

### Future Scripts (Pending)
- `scripts/discord_telegraph_integration.py`
- `scripts/discord_archive_manager.py`
- `scripts/discord_subagent_relay.py`

---

## How to Proceed

### For Bob (User):

1. **Read the setup guide:**
   ```bash
   cat docs/DISCORD_SETUP.md
   ```

2. **Follow Phases 1-2 manually:**
   - Create server
   - Create bot
   - Collect IDs

3. **Send IDs to Momotaro:**
   - Message on Telegram with IDs
   - Or reply in this session

### For Momotaro (When IDs Received):

1. **Create config file:**
   ```bash
   python3 scripts/validate_discord_config.py
   # (will show what's missing)
   ```

2. **Populate `~/.openclaw/config/discord.json`:**
   - Use the IDs Bob provided
   - Run validation script to verify

3. **Execute remaining phases:**
   - Phase 4: Gateway integration
   - Phase 5: Feature setup
   - Phase 6: Testing
   - Phase 7: Documentation

---

## Timeline

```
Phase 1-2 (Bob):     15-20 min  → Provide IDs
Phase 3 (Config):    10 min
Phase 4 (Gateway):   5 min      → Bot should go online
Phase 5 (Features):  15 min
Phase 6 (Testing):   20 min     → All tests pass
Phase 7 (Docs):      15 min
─────────────────────────────────────
TOTAL:               ~80 minutes
```

---

## Next Steps

**Immediate (next message to Bob):**
1. Share link to `docs/DISCORD_SETUP.md`
2. Ask Bob to complete Phases 1-2
3. Request Server ID, Bot Token, and Channel IDs

**When IDs Received:**
1. Populate config file
2. Execute Phase 3-7
3. Test in Discord
4. Report status back to Bob

---

## Support & Troubleshooting

### If Bot Won't Go Online
1. Check token in config is correct
2. Verify gateway is running
3. Check logs: `openclaw gateway logs --lines 50`
4. Restart gateway: `openclaw gateway restart`

### If Messages Don't Route to Momotaro
1. Verify bot has Message Content Intent enabled
2. Check gateway logs for routing errors
3. Ensure channel IDs are correct

### If Need to Reset
1. Delete config: `rm ~/.openclaw/config/discord.json`
2. Delete logs: `rm ~/.openclaw/logs/discord_bot.log`
3. Start over from Phase 3

---

## Success Criteria

When complete:
- ✅ Discord server created and configured
- ✅ Bot online and responsive
- ✅ Messages route to Momotaro
- ✅ Telegraph articles auto-post
- ✅ All tests passing
- ✅ Documentation complete
- ✅ Ready for daily use

---

**Ready to proceed once Bob provides Server ID, Application ID, Channel IDs, and Bot Token.**

Awaiting user input... 🍑
