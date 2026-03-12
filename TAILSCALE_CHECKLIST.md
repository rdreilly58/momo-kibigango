# Tailscale + SSH Setup Checklist

## ✅ COMPLETED: Mac mini Side

**Status: READY**

### What's Done:
- ✅ Tailscale 1.94.2 installed via Homebrew
- ✅ Tailscale daemon running (started via brew services)
- ✅ Tailscale authenticated and active
- ✅ Mac mini IP on Tailscale: **100.114.47.70**
- ✅ Hostname: **bobs-m4-mac-mini**

### Verification Command (run on Mac mini):
```bash
tailscale status
# Should show:
# 100.114.47.70  bobs-m4-mac-mini  active
```

---

## 📋 YOUR TODO: iPhone/iPad Side (3 Steps, ~5 minutes)

### Step 1: Install Tailscale App on iPhone/iPad
1. Open **App Store**
2. Search: **"Tailscale"** (official app by Tailscale Inc.)
3. Tap **Install**
4. Wait for download

### Step 2: Sign In to Tailscale
1. Open the Tailscale app
2. Tap **"Sign in"**
3. Choose login method:
   - Google (recommended - uses your existing Google account)
   - GitHub
   - Microsoft
   - Email
4. **IMPORTANT:** Use the SAME account credentials as your Mac mini
5. Complete authentication in browser
6. Return to Tailscale app
7. Wait for device to appear (should show as "Connected")

### Step 3: Verify Both Devices Connected
1. Go to **https://login.tailscale.com/admin**
2. Sign in with same account
3. Look for:
   - ✅ **bobs-m4-mac-mini** (your Mac)
   - ✅ **Your iPhone/iPad** (whatever you named it)
4. Both should show as "Active" or "Connected"

---

## 🔌 Enable SSH on Mac mini (Already Enabled by Default)

SSH should already be enabled. To verify on your Mac:

**System Settings Method:**
1. Open **System Settings**
2. Go to **General → Sharing**
3. Look for **"Remote Login"**
4. Toggle **ON** if not already enabled
5. Note your username at the top

**Or via Terminal:**
```bash
# Check if SSH is enabled
defaults read /Library/Preferences/com.apple.RemoteDesktop.plist | grep vncEnabled
# If needed, enable it:
sudo systemsetup -setremotelogin on
```

---

## 🚀 First SSH Connection (After Steps 1-3 Above)

Once Tailscale is running on both devices:

### On iPhone/iPad Terminal:
```bash
# Replace 'username' with your actual Mac username
ssh username@100.114.47.70

# When prompted for password, enter your Mac password
# (You'll only see dots or nothing as you type)

# If successful, you'll see the Mac mini prompt!
```

### Your Mac Username:
To find it, run this on your Mac:
```bash
whoami
# Will print something like: rreilly
```

So your SSH command would be:
```bash
ssh rreilly@100.114.47.70
```

---

## 🔐 Optional: SSH Keys (Skip for Now)

Once you have basic SSH working, you can set up keys for passwordless login. See **TAILSCALE_SETUP.md** for full instructions.

---

## ✅ Success Indicators

You'll know it's working when you see:

```
rreilly@bobs-m4-mac-mini ~ %
```

This means you're logged into your Mac mini from your iPhone/iPad!

---

## 🆘 Troubleshooting

### "Connection refused":
- Make sure Tailscale is running on both devices
- Check: `tailscale status` on Mac mini
- Check Tailscale app on iPhone/iPad shows "Connected"

### "Permission denied":
- Check username is correct: run `whoami` on Mac
- Check password is correct (no caps lock!)
- Try: `ssh rreilly@100.114.47.70` (replace rreilly with your username)

### Can't find Tailscale in App Store:
- Make sure you're searching for **"Tailscale"** (official app)
- Developer: **Tailscale Inc.**
- Should be free

### Device not appearing in Tailscale admin:
- Make sure both signed in with SAME account
- Force close Tailscale app and reopen
- Check: https://login.tailscale.com/admin

---

## 📞 Questions?

See **TAILSCALE_SETUP.md** for detailed setup guide and security information.

---

## 🎉 When You're Done

Reply with:
- ✅ Tailscale installed on iPhone/iPad
- ✅ Both devices showing in Tailscale admin
- ✅ Successful SSH connection to Mac mini
- ✅ You can run commands from iPhone/iPad!

Then we can:
1. Set up SSH keys (optional but recommended)
2. Add Mosh for better mobile resilience (optional)
3. Mark your Google Task as complete! ✅

Good luck! 🍑
