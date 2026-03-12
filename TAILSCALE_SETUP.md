# Tailscale Setup for Remote Terminal Access

## ✅ Step 1: Mac mini Setup (COMPLETED)

**Status:** ✅ Tailscale installed and running
- **Version:** 1.94.2
- **Tailscale IP:** `100.114.47.70`
- **Hostname:** `bobs-m4-mac-mini`
- **Tailscale Domain:** `https://bobs-m4-mac-mini.tail321872.ts.net`
- **Service:** Running via `brew services`

### Verify Mac mini is Ready:
```bash
tailscale status
# Should show your device as active
```

---

## 📱 Step 2: Install Tailscale on iPhone/iPad (YOU DO THIS)

### On Your iPhone/iPad:
1. Open **App Store**
2. Search: **"Tailscale"**
3. Install the official Tailscale app (by Tailscale Inc.)
4. Open app and tap **"Sign in"**
5. Use your Google/GitHub/Microsoft account (or email)
6. **Important:** Use the SAME account as your Mac mini

**Note:** You should see both devices appear in the Tailscale admin console once you sign in.

---

## 🖥️ Step 3: Enable SSH on Mac mini (ALREADY DONE)

SSH is enabled by default on macOS. Verify:

```bash
sudo systemsetup -getremotelogin
# Should show: Remote Login: On
```

If not enabled, run:
```bash
sudo systemsetup -setremotelogin on
```

---

## 📲 Step 4: SSH from Terminal on iPhone/iPad

Once Tailscale is installed and your iPhone/iPad shows in your Tailscale account:

### Using Built-in Terminal App (iPad):
1. Open **Terminal** app on iPad (included with iPadOS 15+)
2. Connect to your Mac mini:
   ```bash
   ssh your-username@100.114.47.70
   ```
3. Enter your Mac mini password
4. You're in! 🎉

### Using Built-in Terminal App (iPhone):
- Same process, but Terminal is smaller
- Consider using landscape mode for better visibility
- Or use SSH client apps (see alternatives below)

---

## 🔑 Step 5: Set Up SSH Keys (OPTIONAL but RECOMMENDED)

SSH keys allow passwordless login. Do this once on your Mac mini:

### Generate SSH Key:
```bash
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_mobile -C "iphone-ipad"
# Press Enter twice (no passphrase for convenience)
```

### Copy Key to Authorized Hosts:
```bash
cat ~/.ssh/id_ed25519_mobile.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### Export Private Key to iPhone/iPad:
```bash
cat ~/.ssh/id_ed25519_mobile
# Copy the output starting with "-----BEGIN OPENSSH PRIVATE KEY-----"
```

Then on iPhone/iPad Terminal:
```bash
# Create .ssh directory
mkdir -p ~/.ssh

# Paste the private key
nano ~/.ssh/id_ed25519_mobile
# Paste, save (Ctrl+X, Y, Enter)

# Set permissions
chmod 600 ~/.ssh/id_ed25519_mobile
```

### Connect with Key:
```bash
ssh -i ~/.ssh/id_ed25519_mobile your-username@100.114.47.70
# No password needed!
```

---

## ✅ Verification Checklist

- [ ] Tailscale installed on Mac mini
- [ ] Tailscale installed on iPhone/iPad
- [ ] Both devices signed in to same Tailscale account
- [ ] Mac mini appears in Tailscale admin console
- [ ] iPhone/iPad appears in Tailscale admin console
- [ ] SSH works: `ssh user@100.114.47.70`
- [ ] (Optional) SSH keys configured for passwordless login

---

## 🚀 Quick Reference

### Connect to Mac mini from iPhone/iPad:
```bash
ssh your-username@100.114.47.70
```

### Your Mac mini Details:
- **Tailscale IP:** 100.114.47.70
- **Hostname:** bobs-m4-mac-mini
- **Tailscale Domain:** bobs-m4-mac-mini.tail321872.ts.net

### Useful Commands:
```bash
# View files
ls -la

# Edit files
nano filename

# Check system
uname -a

# See disk usage
df -h

# Run OpenClaw commands
openclaw status

# Work with Git
git status
git log
```

---

## 🔒 Security Notes

1. **Firewall:** Your Mac mini is protected by Tailscale's zero-trust network
2. **No Port Forwarding:** You don't need to expose SSH to the internet
3. **Two-Factor Auth:** Enable 2FA on your Tailscale account for extra security
4. **SSH Keys:** Better than passwords - they can't be brute-forced

---

## ⚠️ Troubleshooting

### "Connection refused" error:
```bash
# Check SSH is running on Mac mini
sudo systemsetup -getremotelogin

# Check Tailscale is running
tailscale status
```

### Can't see iPhone/iPad in Tailscale:
- Make sure both devices are signed in to same Tailscale account
- Force close Tailscale app and reopen
- Check Tailscale admin console: https://login.tailscale.com/admin

### Slow connection:
- This is normal over cellular
- Tailscale optimizes for reliability, not speed
- Better over WiFi

### "Permission denied" on SSH:
- Check username is correct: `whoami` on Mac mini
- Check authorized_keys file: `cat ~/.ssh/authorized_keys`
- SSH key permissions: `ls -la ~/.ssh/`

---

## 📖 Next Steps

1. **Complete Steps 2-4 above** on your iPhone/iPad
2. **Test SSH connection** from Terminal
3. **(Optional) Set up SSH keys** for passwordless login
4. **Update your Google Tasks** - Mark "Create remote terminal access from my iPhone to Mac mini" as done! ✅

---

## 📞 Support

- **Tailscale Docs:** https://tailscale.com/kb/
- **SSH Troubleshooting:** https://support.apple.com/en-us/HT204587
- **Terminal App Help:** Hold Help key on iPad keyboard in Terminal app

Enjoy remote access to your Mac mini! 🍑
