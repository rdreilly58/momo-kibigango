# Termius Connection - Final Steps

## ✅ Mac mini Status Check

**Tailscale:** ✅ Active
- IP: `100.114.47.70`
- Your iPhone: Connected (shows as `bobiphone`)
- Status: Ready

**SSH Keys:** ✅ Configured
- Private key: Generated and ready
- Public key: In authorized_keys
- Username: `rreilly`

**SSH Daemon:** ⚠️ Need to enable (one-time)

---

## 🔧 Step 1: Enable SSH on Mac mini (One-Time)

### Method A: System Settings (Easiest)
1. Open **System Settings** on your Mac mini
2. Go to **General → Sharing**
3. Find **"Remote Login"** 
4. Toggle the switch **ON**
5. It will show: "Remote Login: On"

### Method B: Terminal (If you can run as admin)
```bash
sudo systemsetup -setremotelogin on
# Enter your Mac password when prompted
```

**After enabling:** Remote login service will start automatically

---

## 📱 Step 2: Configure Termius on iPhone

Once SSH is enabled on your Mac:

1. **Open Termius** on iPhone
2. Tap **"Hosts"** (bottom tab)
3. **Edit** the "Mac mini" host you created earlier
4. **Settings:**
   - **Hostname:** `100.114.47.70`
   - **Username:** `rreilly`
   - **Port:** `22`
   - **Authentication:** `Password`
   - **Password:** `1Trust1nG0d`
5. Tap **Save**

---

## 🚀 Step 3: Test Connection

1. In Termius, tap the **"Mac mini"** host
2. Termius will connect (should take 2-3 seconds)
3. You should see the prompt:
   ```
   rreilly@bobs-m4-mac-mini ~ %
   ```

4. Try a command:
   ```bash
   whoami
   # Should print: rreilly
   
   pwd
   # Should print: /Users/rreilly
   ```

---

## 🎉 Success Indicators

✅ You've successfully connected when you see:
- The Mac mini terminal prompt
- You can type commands
- Commands execute and return output
- You can navigate the file system (`ls`, `cd`, etc.)

---

## 🆘 Troubleshooting

### "Connection refused" or "Connection timeout"
1. **Check SSH is enabled:** System Settings → Sharing → Remote Login (should be ON)
2. **Check Tailscale:** 
   - On Mac: `tailscale status` (should show active)
   - On iPhone: Open Tailscale app (should show "Connected")
3. **Check IP:** On Mac, run `tailscale ip -4` (should be 100.114.47.70)

### "Permission denied"
1. Check password is exactly: `1Trust1nG0d` (case-sensitive)
2. Make sure username is: `rreilly`
3. Try again - sometimes it takes a second attempt

### "Network is unreachable"
1. Make sure both Mac and iPhone are on same Tailscale network
2. Check Tailscale admin: https://login.tailscale.com/admin
3. Both devices should show as "active"

### Still not working?
- Restart Termius app
- Restart Tailscale on Mac: `brew services restart tailscale`
- Restart Tailscale on iPhone: Force close and reopen app

---

## ✅ Next Steps (After Connection Works)

1. **Mark task complete:** Update Google Tasks
2. **Optional: SSH Keys:** We can set up passwordless auth later
3. **Explore Termius features:** Snippets, port forwarding, SFTP

---

## 📋 Quick Reference

| Item | Value |
|------|-------|
| **Tailscale IP** | 100.114.47.70 |
| **Username** | rreilly |
| **Port** | 22 |
| **Password** | 1Trust1nG0d |
| **Auth Method** | Password |

---

## 🎯 You're Almost There!

SSH just needs to be enabled on your Mac. Once you flip that switch in System Settings → Sharing → Remote Login, you'll be able to connect from Termius on your iPhone immediately.

Let me know once you've enabled SSH and tried connecting! 🍑
