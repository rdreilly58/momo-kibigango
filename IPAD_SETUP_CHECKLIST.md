# iPad Termius Setup Checklist - Today's Session

**Date:** Wednesday, March 11, 2026
**Goal:** Get remote terminal access working on iPad via Termius + Tailscale

---

## 📋 What's Already Done

✅ **Mac mini (Host)**
- Tailscale 1.94.2 installed and running
- Tailscale IP: `100.114.47.70`
- SSH enabled and working
- Username: `rreilly`
- Password: `1Trust1nG0d`

✅ **iPhone (Reference)**
- Tailscale installed and connected
- Termius installed and configured
- Successfully connecting to Mac mini
- Proving the setup works

---

## 🎯 iPad Setup Steps (Do These Now)

### Step 1: Tailscale on iPad
- [ ] Open App Store on iPad
- [ ] Search "Tailscale"
- [ ] Install (or verify already installed)
- [ ] Open Tailscale app
- [ ] Tap "Sign in"
- [ ] Use **same account** as iPhone (Google/GitHub/Microsoft/Email)
- [ ] Complete browser authentication
- [ ] Wait for "Connected" status
- [ ] Verify Mac mini appears in device list

**Expected result:** iPad shows "Connected" and can see Mac mini (100.114.47.70)

---

### Step 2: Termius on iPad
- [ ] Open App Store on iPad
- [ ] Search "Termius"
- [ ] Install (or verify already installed)
- [ ] Open Termius app
- [ ] Go to **"Hosts"** tab (bottom navigation)
- [ ] Tap **"+"** to add new host

---

### Step 3: Add Mac mini Host in Termius
Fill in these exact values:

```
Label:              Mac mini
Hostname:           100.114.47.70
Username:           rreilly
Port:               22
Authentication:     Password
Password:           1Trust1nG0d
```

- [ ] Enter all fields
- [ ] Tap **Save** (top right)

---

### Step 4: Test Connection
- [ ] In Termius, tap "Mac mini" host
- [ ] Should connect in 2-3 seconds
- [ ] Look for prompt: `rreilly@bobs-m4-mac-mini ~ %`
- [ ] Type: `uname -a` (test command)
- [ ] Should see macOS system info
- [ ] Type: `exit` (close connection)

---

## ✅ Success Criteria

You'll know it's working when:

1. ✅ Tailscale on iPad shows "Connected"
2. ✅ Termius can see Mac mini in the list
3. ✅ Tapping Mac mini connects successfully
4. ✅ You get the shell prompt
5. ✅ Commands execute and return results

---

## 🎯 What This Gets You

Once complete:

- 📱 Remote terminal access from iPad anytime, anywhere
- 🔐 Secure: WireGuard VPN + SSH encryption
- 🌍 Works on WiFi or cellular
- 💻 Full command-line access to Mac mini
- 📂 Can transfer files (SFTP in Termius)
- 🖥️ Split-screen compatible (iPad advantage)

---

## 💡 iPad-Specific Tips

### Landscape Mode
- Rotate iPad to landscape for wider terminal
- Much easier to read code and command output
- Better typing experience

### External Keyboard
- Pair a Bluetooth keyboard for better experience
- Trackpad support makes it like a remote desktop
- Much faster than on-screen keyboard

### Save Frequent Commands
Termius has snippet feature:
- Save `openclaw status`
- Save `git log --oneline -10`
- Save `df -h`
- Quick access with one tap

### File Transfer (SFTP)
Swipe left on connection in Termius:
- Download files from Mac
- Upload files to Mac
- Manage remote directories

---

## 🆘 If Something Goes Wrong

**Can't sign into Tailscale:**
- Use exact same account as iPhone (Google/GitHub/etc.)
- Check that device appears in https://login.tailscale.com/admin

**Connection refused in Termius:**
- Make sure Tailscale shows "Connected"
- Check password is exactly: `1Trust1nG0d`
- Try disconnecting/reconnecting Tailscale

**Can't see Mac mini:**
- Force close Tailscale app
- Reopen Tailscale
- Wait for device list to refresh
- Check admin console

**Slow/drops out:**
- Normal on cellular, faster on WiFi
- Tailscale prioritizes reliability over speed
- Try reconnecting

---

## 📊 Progress Tracking

| Step | Task | Status |
|------|------|--------|
| 1 | Tailscale on iPad | ⏳ Waiting |
| 2 | Termius on iPad | ⏳ Waiting |
| 3 | Add Mac mini host | ⏳ Waiting |
| 4 | Test connection | ⏳ Waiting |
| ✅ | Verify working | ⏳ Waiting |

---

## 📞 Ready to Go?

Let me know once you:
1. Have Tailscale signed in on iPad
2. Have Termius configured with Mac mini
3. Successfully connect and run a test command

Then we can explore iPad-specific features and optimizations! 🍑
