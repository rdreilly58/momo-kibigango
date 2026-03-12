# Termius Setup for Remote Terminal Access (via Tailscale)

## ✅ Step 1: Mac mini Tailscale (COMPLETED)

**Status:** ✅ Tailscale installed and active
- **Tailscale IP:** 100.114.47.70
- **Hostname:** bobs-m4-mac-mini
- **Service:** Running

### Verify:
```bash
tailscale status
# Should show active connection
```

---

## ✅ Step 2: iPhone Tailscale (YOU HAVE THIS)

**Status:** ✅ Tailscale already installed on iPhone
- Sign in to same account as Mac mini
- Both devices should appear in Tailscale admin: https://login.tailscale.com/admin

### Quick Verify:
Open Tailscale app → Should show "Connected" status

---

## 📲 Step 3: Install Termius on iPhone (YOU DO THIS)

### On Your iPhone:
1. Open **App Store**
2. Search: **"Termius"**
3. Install (by Carlsberg Group)
4. Wait for download (app is ~50MB)

**Cost:** $4.99 (worth it for professional SSH client)

---

## 🔑 Step 4: Generate SSH Key on Mac mini

SSH keys allow secure, passwordless login. Generate one now:

```bash
# Generate key
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_termius -C "termius"

# When prompted for passphrase, press Enter twice (no passphrase)

# Verify it was created
ls -la ~/.ssh/id_ed25519_termius*
# Should show: id_ed25519_termius (private) and id_ed25519_termius.pub (public)
```

### Add Public Key to Authorized Keys:
```bash
cat ~/.ssh/id_ed25519_termius.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# Verify
cat ~/.ssh/authorized_keys
```

### Export Private Key (to copy to Termius):
```bash
cat ~/.ssh/id_ed25519_termius
```

**Copy the entire output starting with:**
```
-----BEGIN OPENSSH PRIVATE KEY-----
```

And ending with:
```
-----END OPENSSH PRIVATE KEY-----
```

---

## ⚙️ Step 5: Add Mac mini Host to Termius

### In Termius App (on iPhone):

1. **Open Termius**
2. Tap **"Hosts"** tab (bottom)
3. Tap **"+"** (add new host)
4. Fill in these fields:

   **Label:** `Mac mini` (or any name you like)
   
   **Hostname:** `100.114.47.70` (your Tailscale IP)
   
   **Username:** `rreilly` (or your actual Mac username - run `whoami` to check)
   
   **Port:** `22` (default SSH port)

5. **Authentication:**
   - Tap **"Key"** (not password)
   - Tap **"Create new key"**
   - Name: `termius`
   - **Paste the private key** you copied from Step 4
   - Tap **"Save"**

6. Back on host screen, select the key you just created

7. Tap **"Save"** (top right)

---

## 🚀 Step 6: Test Connection

### In Termius:

1. Tap the **"Mac mini"** host you just added
2. Termius should connect automatically (should take 2-3 seconds)
3. You'll see the Mac mini terminal prompt:

```
Last login: Wed Mar 11 06:52:00 2026
rreilly@bobs-m4-mac-mini ~ %
```

**Success!** 🎉

---

## 🎯 What You Can Do Now

Once connected, you have full terminal access to your Mac mini:

```bash
# Check system info
uname -a
hostname

# List files
ls -la ~/

# Check OpenClaw status
openclaw status

# View Git repos
cd ~/momotaro-ios && git status

# And anything else you normally do in Terminal!
```

---

## 💡 Termius Features to Explore

Once you're connected:

1. **Snippets** — Save frequently-used commands
   - Tap menu → Snippets
   - Create shortcuts for common tasks

2. **Port Forwarding** — Access services on Mac
   - Useful for web servers, databases, etc.

3. **File Transfer** — SFTP file browser
   - Built into Termius (swipe left on connection)

4. **Terminal Multiplexing** — Split screens
   - Command: `tmux` on Mac mini

5. **Password Manager** — Integration available
   - Optional, for future setup

---

## 🔒 Security Summary

**What's Secure:**
- ✅ SSH keys (can't be brute-forced)
- ✅ Tailscale VPN (zero-trust, WireGuard encryption)
- ✅ No port forwarding (Mac not exposed to internet)
- ✅ Private network access only

**Best Practices:**
- Don't share SSH private key
- Keep Tailscale signed in on both devices
- Use strong Mac password (for local security)
- (Optional) Enable 2FA on Tailscale account

---

## ✅ Verification Checklist

- [ ] Termius installed on iPhone
- [ ] SSH key generated on Mac mini
- [ ] Public key added to `~/.ssh/authorized_keys`
- [ ] Mac mini host added to Termius
- [ ] SSH key imported to Termius
- [ ] Successful connection test
- [ ] Can run commands on Mac mini from iPhone

---

## 🆘 Troubleshooting

### "Connection refused":
```bash
# On Mac mini, check SSH is running
ps aux | grep sshd

# Check Tailscale is active
tailscale status
```

### "Permission denied (publickey)":
- Verify key was copied correctly
- Check authorized_keys file:
  ```bash
  cat ~/.ssh/authorized_keys
  ```
- Make sure public key ends up in that file

### "Host not found":
- Check Tailscale IP is correct: `tailscale ip -4`
- Verify both devices in Tailscale admin console
- Check iPhone Tailscale app shows "Connected"

### Slow connection:
- This is normal over cellular
- Better over WiFi
- Tailscale prioritizes reliability over speed

---

## 📖 Next Steps

1. **Install Termius** on iPhone ($4.99)
2. **Generate SSH key** on Mac mini (copy command from Step 4)
3. **Export private key** and copy
4. **Add host to Termius** with SSH key
5. **Test connection** from Termius
6. **Explore features** (snippets, port forwarding, etc.)

---

## 🎉 Pro Tips

### Quickly Switch Between Hosts:
- Save multiple hosts in Termius
- Use Tab key to cycle between them (if using SFTP)

### Save Command Snippets:
```bash
# In Termius → Snippets
openclaw status         # Quick status check
git status              # Check Git repos
terraform plan          # If you use Terraform
```

### Create Aliases on Mac:
```bash
# Edit ~/.zshrc or ~/.bash_profile
alias ll='ls -la'
alias gc='git commit'

# Then use shortcuts in Termius!
```

---

## 📞 Support

- **Termius Docs:** https://support.termius.com/
- **SSH Key Help:** https://support.termius.com/hc/en-us/articles/6825156821267-Public-key-authentication
- **Tailscale Help:** https://tailscale.com/kb/

---

## Summary

**Total Setup Time:** ~10 minutes

1. Install Termius ($4.99)
2. Generate SSH key on Mac (2 min)
3. Add host to Termius (3 min)
4. Connect and test (1 min)

You'll have a professional SSH client on your iPhone with passwordless access to your Mac mini, secured by Tailscale and SSH keys. Way better than the free Terminal app!

Enjoy! 🍑
