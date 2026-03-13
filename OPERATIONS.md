# Momotaro iOS — User Operations Guide

![Version](https://img.shields.io/badge/Version-1.0.0-blue)
![Status](https://img.shields.io/badge/Status-Ready%20for%20Beta-brightgreen)
![iOS Support](https://img.shields.io/badge/iOS-17%2B-blue)

---

## 📋 Table of Contents

1. [Getting Started](#getting-started)
2. [Core Features](#core-features)
3. [Messaging & Sessions](#messaging--sessions)
4. [Subscription Plans](#subscription-plans)
5. [Settings & Preferences](#settings--preferences)
6. [Troubleshooting](#troubleshooting)
7. [FAQ](#faq)
8. [Privacy & Security](#privacy--security)

---

## 🚀 Getting Started

### First Launch

1. **Download & Install**
   - Search "Momotaro" in App Store (iOS 17+)
   - Or build from source following [INSTALLATION.md](INSTALLATION.md)

2. **Create Your First Session**
   - Tap **"New Session"** button
   - Give your session a name (e.g., "Chat with AI")
   - Press **"Start"**

3. **Send Your First Message**
   - Tap the message input box
   - Type your message
   - Press **Send** (arrow button)

4. **View Your Session History**
   - All messages are saved automatically
   - Scroll up to see earlier messages
   - Search across all sessions

---

## 💬 Core Features

### 1. Chat Sessions

**What is a Session?**
- A conversation thread between you and Momotaro
- Each session has its own message history
- You can manage up to 3 sessions on Free plan, unlimited on Pro

**Creating a Session**
```
Home → "+" or "New Session" → Enter name → Start
```

**Managing Sessions**
- Tap session name to rename
- Swipe left to delete (⚠️ irreversible)
- Tap session to switch between them

### 2. Real-Time Messaging

**Sending Messages**
1. Type in the message input field
2. Attach files or images (Pro plan)
3. Press **Send** arrow button
4. Message appears instantly

**Message Status**
- 🔵 **Sending** — Message in transit
- ✅ **Sent** — Delivered to server
- 👁️ **Read** — Momotaro read it

**Editing & Deleting**
- Long-press message for options menu
- Edit: Modify and resubmit
- Delete: Permanently remove (not reversible)

### 3. Message Search

**Search Your History**
- Tap **Search** icon in message list
- Type keywords to find messages
- Results show across all sessions (Pro plan only)

**Free Plan Search Limitations**
- Search limited to current session only
- Last 100 messages indexed

**Pro Plan Search**
- Search all sessions simultaneously
- Full message history available
- Advanced filters: date, sender, keywords

### 4. Session Features

**Session Info**
- Tap ⓘ (info icon) to see:
  - Total messages
  - Session created date
  - Last message timestamp

**Export Session** (Pro Plan Only)
- Tap **Export** → **Choose Format**
  - PDF (printable format)
  - JSON (raw data)
  - TXT (plain text)
- Save to Files app or share

### 5. Message History & Persistence

**Automatic Backup**
- All messages stored on device (Core Data)
- Automatic daily backup to device storage
- No cloud sync (privacy-first design)

**How Long Are Messages Kept?**
- **Free Plan:** Last 100 messages per session
- **Pro Plan:** Unlimited message history
- Deletion: Permanent once you confirm

---

## 💳 Subscription Plans

### Plan Comparison

| Feature | Free | Pro Monthly | Pro Annual |
|---------|------|-------------|-----------|
| **Price** | $0 | $9.99/mo | $79.99/yr |
| **Messages/Day** | 100 | Unlimited | Unlimited |
| **Active Sessions** | 3 | Unlimited | Unlimited |
| **Message History** | 100 last | Unlimited | Unlimited |
| **Search** | Current | All sessions | All sessions |
| **Export** | ❌ | ✅ | ✅ |
| **Analytics** | ❌ | ✅ | ✅ |
| **Priority Support** | ❌ | ✅ | ✅ |

### Upgrading to Pro

**Monthly Subscription ($9.99/month)**
1. Tap **Settings** → **Upgrade to Pro**
2. Select **"Pro Monthly"**
3. Confirm with Face ID / Touch ID
4. Subscription starts immediately

**Annual Subscription ($79.99/year)**
1. Tap **Settings** → **Upgrade to Pro**
2. Select **"Pro Annual"** (Save 33%!)
3. Confirm with Face ID / Touch ID
4. Subscription starts immediately

**What Happens After Purchase?**
- ✅ Unlock all Pro features instantly
- ✅ Existing sessions upgraded automatically
- ✅ Receipt sent to your Apple ID email
- ✅ Can restore on other devices with same Apple ID

### Managing Your Subscription

**View Subscription Status**
```
Settings → Account → Subscription Status
```

**Cancel Anytime**
1. Open **Settings** → **Account**
2. Tap **Manage Subscription**
3. Select **Cancel Subscription**
4. Access continues until renewal date
5. You'll get a cancellation confirmation

**Restore Purchases**
1. Tap **Settings** → **Account**
2. Tap **Restore Purchases**
3. Confirm with Face ID / Touch ID
4. Pro features restore instantly

**Renew After Cancellation**
- If you cancelled, you can resubscribe anytime
- Tap **Settings** → **Upgrade to Pro**
- Choose your plan again

---

## ⚙️ Settings & Preferences

### Account Settings

**View Your Account**
```
Settings → Account → Profile
```

**Account Information**
- User ID (device identifier)
- Account created date
- Current subscription tier
- Total sessions created
- Total messages sent

### Appearance

**Dark Mode**
- Automatically follows system settings
- Dark mode for low-light usage
- Light mode for bright environments

**Text Size**
```
Settings → Appearance → Text Size
Choose: Small, Normal, Large, Extra Large
```

### Notifications

**Message Notifications** (When Available)
```
Settings → Notifications → Message Alerts
```
- Enable/disable notifications
- Choose notification sound
- Set quiet hours (e.g., 11 PM - 8 AM)

### Privacy & Data

**Data Usage**
```
Settings → Privacy → Data Usage
```
- View your message count
- See storage used on device
- Clear cache (doesn't delete messages)

**Permissions**
```
Settings → Privacy → Permissions
```
Current permissions:
- 📱 **Access to Device:** Messages stored locally only
- 📷 **Camera/Photos:** Only if you opt-in to attachments
- 📍 **Location:** Never collected
- 🎤 **Microphone:** Never used

---

## 🔍 Troubleshooting

### Messages Not Sending

**Symptom:** Message stuck in "Sending" state

**Solutions:**
1. **Check Internet Connection**
   - WiFi or cellular must be active
   - Try airplane mode OFF/ON

2. **Restart App**
   - Swipe up from home to close app
   - Tap Momotaro to reopen

3. **Check Server Status**
   - Visit [status.momotaro.app](https://status.momotaro.app)
   - If server down, messages will retry automatically

4. **Force Delete Stuck Message**
   - Long-press the message
   - Tap **Delete** (will be permanently removed)
   - Retype and resend

### Can't Create New Session

**Symptom:** "+" button does nothing or shows error

**Reason:** You've reached session limit on Free plan
- Free plan: 3 sessions max
- To create more, delete an old session or upgrade to Pro

**Solution:**
- Delete a session you no longer need
- Or tap **"Upgrade to Pro"** for unlimited

### Search Not Working

**Symptom:** Search returns no results

**Possible Causes:**
1. **On Free Plan:** Search only works in current session
   - Switch to the session you want to search
   - Try again

2. **Message Too Old:** Free plan only indexes last 100 messages
   - Upgrade to Pro for full history search

3. **Search Term Too Vague:** Try specific keywords
   - Instead of "hello", search "hello world"

### Purchase Failed / Can't Upgrade

**Symptom:** "Upgrade" button grayed out or error message

**Solutions:**
1. **Check Payment Method**
   - Settings → [Your Apple ID] → Payment Method
   - Update or add valid payment method

2. **Restore Purchase**
   - If you purchased on another device:
   - Settings → Account → **Restore Purchases**
   - Confirm with Face ID/Touch ID

3. **Restart App**
   - Close app completely
   - Reopen and try again

4. **Contact Support**
   - Email: support@momotaro.app
   - Include: Device model, iOS version, screenshot of error

### App Crashes on Launch

**Symptom:** App closes immediately after opening

**Solutions:**
1. **Force Quit & Restart**
   ```
   Swipe up from home → Swipe up on Momotaro
   Wait 5 seconds, then tap to reopen
   ```

2. **Clear App Cache**
   ```
   Settings → Momotaro → Clear Cache
   ```

3. **Reinstall App**
   - Delete app (long-press → Remove)
   - Reinstall from App Store
   - Your messages are saved (will restore automatically)

### Low Storage Warning

**Symptom:** "Storage full" message

**Solutions:**
1. **Delete Old Sessions**
   - Sessions with 100+ messages take most space
   - Delete sessions you no longer need

2. **Export & Archive**
   - Export sessions to external storage
   - Delete the archived sessions in app

3. **Manage Device Storage**
   - Settings → General → iPhone Storage
   - Delete unused apps to free up space

---

## ❓ FAQ

### Q: Is my data private?
**A:** Yes. Messages are stored **only on your device**. No cloud backup by default. You control all your data.

### Q: Can you read my messages?
**A:** No. Messages are encrypted on device and never sent to our servers. See [Privacy & Security](#privacy--security).

### Q: What if I lose my phone?
**A:** Messages are stored locally only. If you need backup, export to Files/cloud storage first.

### Q: Can I use Momotaro on multiple devices?
**A:** **Free Plan:** Each device has separate sessions and history.
**Pro Plan:** Can restore purchases on other devices with same Apple ID (messages don't sync).

### Q: How long do messages stay?
**Free Plan:** Last 100 messages per session
**Pro Plan:** Unlimited - all messages kept until you delete

### Q: Can I use Momotaro offline?
**A:** View saved messages offline. New messages require internet connection. Messages queue and send when online.

### Q: Why am I getting "Session limit" error?
**A:** Free plan allows 3 active sessions max. Delete an old session or upgrade to Pro for unlimited.

### Q: How do I cancel my subscription?
**A:** Settings → Account → Manage Subscription → Cancel. You can resubscribe anytime.

### Q: Do you offer refunds?
**A:** Apple handles refunds through App Store. Request within 14 days of purchase through:
- **App Store** → Account → Purchase History → Report Problem

### Q: What iOS versions are supported?
**A:** iOS 17.0 and later. iPad supported (universal app).

### Q: Can I export my messages?
**A:** **Pro Plan:** Yes - PDF, JSON, or TXT formats via Session → Export menu
**Free Plan:** Manual copy/paste only

### Q: How often should I back up?
**A:** Recommended: Weekly export of important sessions to Files app or cloud storage (iCloud Drive, Google Drive, etc.)

---

## 🔒 Privacy & Security

### Data Collection Policy

**What We Collect:**
- ✅ Your messages (stored on device only)
- ✅ Session metadata (created date, message count)
- ✅ Subscription tier (for feature access)

**What We DON'T Collect:**
- ❌ Location data
- ❌ Device contacts
- ❌ Photos or files (unless you explicitly attach)
- ❌ Analytics or tracking cookies
- ❌ Personal identifiers

### Encryption

**In Transit:**
- All communication uses TLS 1.3
- Verified certificates only

**At Rest:**
- Messages encrypted with AES-256
- Keys stored securely in device keychain
- No access without device passcode

### Security Best Practices

**For Your Account:**
1. Use strong device passcode (not 1234)
2. Enable Face ID or Touch ID
3. Keep iOS updated
4. Don't share device with others

**For Your Messages:**
1. Regular backups (weekly recommended)
2. Export sensitive conversations to safe storage
3. Delete sessions you no longer need
4. Don't screenshot sensitive info for sharing

### Permissions Explanation

**Why Momotaro Requests Permissions:**

| Permission | Why? | Required? |
|-----------|------|-----------|
| Photos | Attach images to sessions | Optional |
| Camera | Record video messages (future) | No, not yet |
| Contacts | Not requested | Never |
| Location | Not requested | Never |
| Microphone | Not requested | Never |

**You Control Everything:**
- All permissions are optional
- Deny at any time in Settings
- App works without extra permissions

---

## 📞 Support

**Need Help?**
- 📧 **Email:** support@momotaro.app
- 🐛 **Bug Report:** [GitHub Issues](https://github.com/rdreilly58/momotaro-ios/issues)
- 📱 **In-App Help:** Settings → Help & Support

**Common Questions Already Answered?**
- Check this guide first
- Search FAQ section above
- Review [Troubleshooting](#troubleshooting)

---

## ✨ Tips & Tricks

### Pro Tips for Better Experience

1. **Organize with Session Names**
   - Use clear names: "Project Ideas", "Daily Log", "Learning Swift"
   - Tap session title to rename

2. **Export Regularly**
   - Weekly export important conversations
   - Creates backup + archivable format

3. **Use Search Effectively**
   - Specific keywords work best
   - Date filters available (Pro plan)

4. **Session Limits**
   - Free plan: Keep 3 active sessions
   - Archive old ones via export

5. **Storage Management**
   - Delete 100+ message sessions when not needed
   - Exported sessions free up device space

---

## 🎉 You're All Set!

You now have everything you need to use Momotaro effectively.

**Next Steps:**
- [ ] Create your first session
- [ ] Send a message
- [ ] Explore search and history
- [ ] Try upgrading for Pro features
- [ ] Export a session

**Questions? Issues?** → [Support Section](#-support)

---

**Last Updated:** March 10, 2026
**Version:** 1.0.0
**Status:** Production Ready ✅

🍑 **Enjoy Momotaro!**
