# Hybrid Webhook + Telegram Setup Guide

## Goal
Implement real-time Rocket.Chat integration:
- Webhook detects messages instantly
- Telegram forwards notification
- I respond in Telegram
- Response auto-posts to Rocket.Chat

---

## Step 1: Get Telegram Bot Token

You need the bot token for @Momotaro_Bot. 

**Do you have it?**
- If yes: Save to `~/.openclaw/telegram-bot-token`
- If no: Create a new bot via @BotFather on Telegram

**To create bot:**
1. Message @BotFather
2. `/newbot`
3. Name it, get the token
4. Save token to: `~/.openclaw/telegram-bot-token`

**Command:**
```bash
echo "YOUR_BOT_TOKEN_HERE" > ~/.openclaw/telegram-bot-token
chmod 600 ~/.openclaw/telegram-bot-token
```

---

## Step 2: Start Webhook Server

```bash
python3 ~/.openclaw/workspace/scripts/rocketchat-webhook-forwarder.py
```

Will output:
```
🚀 Rocket.Chat Webhook Server Started
📍 Listening on 127.0.0.1:9998
📍 Endpoint: POST /rocket-chat
```

---

## Step 3: Configure Rocket.Chat Webhook

1. Open Rocket.Chat: `http://192.168.1.209:3000`
2. Go to **Admin** → **Integrations** → **Incoming Webhooks**
3. Click **Create New**
4. Fill in:
   - **Name:** Momotaro Real-Time
   - **Channel:** `general`
   - **Trigger Words:** (leave blank)
   - **URL:** `http://localhost:9998/rocket-chat`
   - **Post Data:**
     ```json
     {
       "text": "@message_text",
       "user_name": "@username",
       "channel_name": "@room_name"
     }
     ```
5. Click **Create**

---

## Step 4: Test the Webhook

From your work computer, send a message to #general:
```
"Hello from work computer"
```

**Expected:**
1. Message appears in #general
2. Webhook detects instantly
3. Telegram notification arrives here
4. Shows: `🚀 **Rocket.Chat #general** Hello from work computer`

---

## Step 5: Respond via Telegram

When you see the forwarded message here in Telegram:
1. Read the message
2. Respond in this Telegram chat
3. I'll use the posting script:
   ```bash
   ~/.openclaw/workspace/scripts/post-to-rocketchat.sh "My response"
   ```
4. Response appears in #general instantly

---

## Step 6: Auto-Start (LaunchAgent)

Create LaunchAgent to auto-start webhook server:

```bash
cat > ~/Library/LaunchAgents/com.momotaro.rocketchat-webhook.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.momotaro.rocketchat-webhook</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/rreilly/.openclaw/workspace/scripts/rocketchat-webhook-forwarder.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/rreilly/.openclaw/logs/webhook.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/rreilly/.openclaw/logs/webhook.log</string>
</dict>
</plist>
EOF

launchctl load ~/Library/LaunchAgents/com.momotaro.rocketchat-webhook.plist
```

---

## Final Workflow

```
Your Work Computer
    ↓ (Sends message to #general)
Rocket.Chat
    ↓ (Webhook detects instantly)
Webhook Server (localhost:9998)
    ↓ (Forwards to Telegram)
Telegram (THIS CHAT)
    ↓ (I see notification immediately)
My Response
    ↓ (I run posting script)
Response Posted to #general
    ↓ (Appears in Rocket.Chat instantly)
```

**Total latency: 1-3 seconds** ⚡

---

## Troubleshooting

**Webhook not firing?**
- Check Rocket.Chat webhook is enabled
- Verify URL: `http://localhost:9998/rocket-chat`
- Check webhook logs in Rocket.Chat Admin panel

**Telegram not receiving?**
- Verify bot token: `echo $TELEGRAM_BOT_TOKEN`
- Check file: `cat ~/.openclaw/telegram-bot-token`
- Restart webhook server

**Response not posting?**
- Run: `./post-to-rocketchat.sh "test message"`
- Check if message appears in #general

---

## Status

Ready to implement! Do you have the Telegram bot token? 🍑
