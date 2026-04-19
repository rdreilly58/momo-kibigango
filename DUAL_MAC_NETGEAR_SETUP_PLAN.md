# Dual Mac Mini Setup Plan — Netgear Dumb Switch

**Decision:** Connect M4 Mac mini + Older Mac mini via existing Netgear dumb switch  
**Date:** Sunday, March 22, 2026, 7:07 AM EDT  
**Status:** Ready to execute

---

## Quick Summary

```
M4 Mac mini ──────┐
                  │ Cat5e/Cat6 cables
          Netgear │
          Dumb    │ (no configuration)
          Switch  │
                  │
Older Mac mini ───┘
```

**Timeline:** 1-2 hours total
**Cost:** ~$20-30 (cables only, switch already owned)
**Complexity:** Low (just plugging cables)

---

## Phase 1: Hardware & Cables (15 minutes)

### What You Need

**Already have:**
- ✅ Netgear dumb switch (already owned)
- ✅ M4 Mac mini (has Ethernet port)
- ✅ Older Mac mini (needs Ethernet port verification)

**Need to acquire:**
- [ ] Cat5e or Cat6 cables (2x, 3-10 feet)
  - Recommendation: Cat6 (future-proof, same price as Cat5e)
  - Buy: Amazon, Newegg, Best Buy
  - Cost: ~$10-15 per cable (~$20-30 total)
  - Alternative: Use existing Ethernet cables if you have them

**Optional but recommended:**
- [ ] Velcro cable ties (organize cables behind desk)
- [ ] Cable sleeves (protect from damage, looks neat)
- [ ] Switch power cable verification (dumb switches usually need power)

### Shopping List

```
REQUIRED:
□ Cat5e/Cat6 Ethernet cables (2x, 3-10 feet each)
  - Amazon: "Cat6 Ethernet Cable" (6 pack for ~$15)
  - Speed: 1 Gbps minimum (both work)
  - Length: Measure distance between Macs + 2 feet slack

OPTIONAL:
□ Velcro cable ties (small management kit, ~$10)
□ Cable sleeve (if cables visible, ~$5)
□ Switch power adapter (if Netgear switch needs it)
```

### Verification Checklist

```
M4 Mac mini:
□ Has Ethernet port? (Check back of machine)
□ Ethernet port functional? (plug in a cable to verify)

Older Mac mini:
□ Has Ethernet port? (Check back of machine)
□ Model/Year: _________________ (for reference)
□ Ethernet port functional?

Netgear Switch:
□ Has power (plug it in first)
□ All ports visible and accessible
□ Model number: _________________ (for reference)
□ Ports working? (LED lights when powered)
```

---

## Phase 2: Physical Setup (20 minutes)

### Step 1: Gather Components

```
Before you start:
□ Have all cables ready
□ Clear space behind/around both Macs
□ Have switch power adapter ready
□ Measure cable distances
```

### Step 2: Power Up the Switch

```bash
1. Plug Netgear switch into power outlet
2. Wait 10 seconds for lights to stabilize
3. Check: Green lights on ports (indicates power)
4. Switch is ready (no configuration needed for dumb switch)
```

### Step 3: Connect M4 Mac mini

```bash
1. Take Cat6 cable #1
2. Plug into Ethernet port on M4 Mac (back of machine)
3. Plug other end into Port 1 or 2 on Netgear switch
4. Wait 5 seconds
5. Check: Orange/Green light on port (indicates connection)
6. Verify on Mac: System Settings → Network → Ethernet
   Should show "Connected" or "Active"
```

### Step 4: Connect Older Mac mini

```bash
1. Take Cat6 cable #2
2. Plug into Ethernet port on older Mac
3. Plug other end into Port 3 or 4 on Netgear switch
4. Wait 5 seconds
5. Check: Orange/Green light on port
6. Verify on Mac: System Settings → Network → Ethernet
   Should show "Connected" or "Active"
```

### Step 5: Cable Management (Optional but recommended)

```bash
1. Route cables along desk edge
2. Use Velcro ties to bundle cables together
3. Label each cable end (optional):
   - "M4-Port1" and "Older-Port3"
4. Keep cables away from power cords
5. Secure switch to desk edge with rubber feet
```

### Physical Setup Complete ✅

At this point:
- Both Macs connected via Netgear switch
- Lights on ports should indicate active connection
- Network shows "Connected" on both Macs
- Ready for network configuration

---

## Phase 3: Network Configuration (30 minutes)

### Step 3A: Verify Network Connectivity

**On M4 Mac:**
```bash
# Check Ethernet connection status
ifconfig en0 | grep inet

# Should show IP address like: 169.254.x.x or 192.168.x.x
# If you see something, it's working!

# Test ping to older Mac (get its IP first)
ping 169.254.x.x  # Replace with actual IP
```

**On Older Mac:**
```bash
# Same check
ifconfig en0 | grep inet
```

### Step 3B: Set Machine Names

**On M4 Mac (run these commands):**
```bash
# Set nice names for identification
sudo scutil --set ComputerName "M4-Mac-mini"
sudo scutil --set HostName "m4-mac-mini"
sudo scutil --set LocalHostName "m4-mac-mini"

# Verify
scutil --get ComputerName
# Should show: M4-Mac-mini
```

**On Older Mac (run these commands):**
```bash
# Replace "OldMac" with actual model (e.g., "Mac-mini-2018")
sudo scutil --set ComputerName "OldMac-mini"
sudo scutil --set HostName "oldmac-mini"
sudo scutil --set LocalHostName "oldmac-mini"

# Verify
scutil --get ComputerName
```

### Step 3C: Enable File Sharing (on both Macs)

**On M4 Mac:**
1. Open System Settings
2. Go to General → Sharing
3. Click "File Sharing"
4. Enable toggle: ☑ File Sharing
5. Note the IP address (should be something like `smb://192.168.x.x`)
6. Click "Options" → Configure folders to share
7. Add folders you want to share (Documents, Downloads, Desktop)

**On Older Mac:**
1. Repeat same steps
2. System Settings → General → Sharing
3. Enable File Sharing
4. Note IP address

### Step 3D: Enable SSH (for remote commands)

**On M4 Mac:**
1. System Settings → General → Sharing
2. Scroll down to "Remote Login"
3. Enable toggle: ☑ Remote Login
4. Add your user account to list
5. Note the access instruction (usually `ssh user@m4-mac-mini.local`)

**On Older Mac:**
1. Repeat same steps
2. Enable Remote Login

### Step 3E: Test SSH Connectivity

**From M4 Mac, test access to older Mac:**
```bash
# Test 1: Simple connectivity
ssh oldmac-mini.local

# If asks for password, type it
# If you see the command prompt, it worked! ✅
# Type: exit (to exit SSH)

# Test 2: From Older Mac back to M4
ssh m4-mac-mini.local
# Should also work ✅
```

---

## Phase 4: File Sharing Setup (15 minutes)

### Option A: Mount via File Sharing (Easy)

**On M4 Mac, mount Older Mac's folders:**
```bash
# Create mount point
mkdir -p ~/Mounts/OldMac

# Mount via SMB (File Sharing)
# Replace 'username' with actual user on older Mac
mount_smbfs smb://username:password@oldmac-mini.local/Users/username/Documents ~/Mounts/OldMac

# Verify
ls ~/Mounts/OldMac
# Should show files from older Mac's Documents folder
```

**Create auto-mount script (optional):**
```bash
# Create file: ~/mount-macs.sh
cat > ~/mount-macs.sh << 'EOF'
#!/bin/bash
# Auto-mount older Mac shared folders

mkdir -p ~/Mounts/OldMac
mount_smbfs smb://username:password@oldmac-mini.local/Users/username/Documents ~/Mounts/OldMac

echo "✅ OldMac mounted at ~/Mounts/OldMac"
EOF

chmod +x ~/mount-macs.sh

# Run it:
~/mount-macs.sh
```

### Option B: Use SSH (Advanced)

```bash
# Direct file copy over SSH
scp -r username@oldmac-mini.local:/Users/username/Documents/file.txt ~/Downloads/

# Or mount entire home directory
sshfs username@oldmac-mini.local:/Users/username ~/Mounts/OldMac-SSH
```

### Option C: Use rsync (Best for Backups)

```bash
# Backup entire folder from older Mac to M4
rsync -av username@oldmac-mini.local:/Users/username/Documents/ ~/Backups/OldMac-Docs/

# Or with compression for large files
rsync -avz --compress username@oldmac-mini.local:/Users/username/Documents/ ~/Backups/
```

---

## Phase 5: Testing & Validation (20 minutes)

### Connectivity Tests

```bash
# Test 1: Ping between Macs
ping -c 5 oldmac-mini.local
# Should show: packets transmitted, no loss

# Test 2: SSH access
ssh username@oldmac-mini.local "echo 'Hello from M4!'"
# Should print: Hello from M4!

# Test 3: File transfer speed
# Create test file on older Mac:
ssh username@oldmac-mini.local "dd if=/dev/urandom of=/tmp/testfile bs=1M count=100"

# Copy it to M4 and measure speed:
time scp -r username@oldmac-mini.local:/tmp/testfile ~/testfile

# Should complete in ~1 second (100 MB in 1 sec = 800 Mbps = ✅ working)
```

### File Sharing Tests

```bash
# Test 1: List shared folders on older Mac
smbclient -L oldmac-mini.local

# Test 2: Mount and verify
ls ~/Mounts/OldMac
# Should show files from older Mac

# Test 3: Create test file
touch ~/Mounts/OldMac/test-from-m4.txt
# Go to older Mac, check if file appears in shared folder
```

### Performance Baseline

```bash
# Create benchmark script
cat > ~/test-mac-network.sh << 'EOF'
#!/bin/bash

echo "🧪 Dual Mac Network Performance Test"
echo "===================================="

# Test latency
echo ""
echo "Latency (should be <1ms):"
ping -c 5 oldmac-mini.local | tail -2

# Test SSH speed
echo ""
echo "SSH Response Time:"
time ssh oldmac-mini.local "echo 'OK'"

# Test file copy
echo ""
echo "File Copy Speed (should be ~100-125 MB/s):"
ssh oldmac-mini.local "dd if=/dev/urandom of=/tmp/speed-test bs=1M count=50 2>/dev/null"
time scp -r oldmac-mini.local:/tmp/speed-test ~/speed-test 2>/dev/null
rm ~/speed-test

echo ""
echo "✅ Network tests complete"
EOF

chmod +x ~/test-mac-network.sh
~/test-mac-network.sh
```

---

## Phase 6: Use Cases & Automation (Optional)

### Use Case 1: Backup Older Mac to M4

```bash
#!/bin/bash
# backup-oldmac.sh
# Backs up older Mac to M4 every day

BACKUP_DIR="$HOME/Backups/OldMac"
REMOTE_USER="username"
REMOTE_HOST="oldmac-mini.local"

mkdir -p "$BACKUP_DIR"

echo "📦 Backing up Older Mac..."

# Backup Documents
rsync -avz --delete \
  "$REMOTE_USER@$REMOTE_HOST:/Users/$REMOTE_USER/Documents/" \
  "$BACKUP_DIR/Documents/"

# Backup Downloads (optional)
rsync -avz --delete \
  "$REMOTE_USER@$REMOTE_HOST:/Users/$REMOTE_USER/Downloads/" \
  "$BACKUP_DIR/Downloads/"

echo "✅ Backup complete"
```

### Use Case 2: Distributed Compilation

```bash
#!/bin/bash
# compile-on-oldmac.sh
# Send build job to older Mac while M4 does other work

PROJECT="/Users/username/Projects/myapp"
REMOTE_HOST="oldmac-mini.local"

echo "📤 Sending build to older Mac..."

ssh "$REMOTE_HOST" "cd /Volumes/SharedBuilds && xcodebuild -scheme MyApp"

echo "✅ Build complete on older Mac"
```

### Use Case 3: Nightly Cleanup

```bash
#!/bin/bash
# nightly-cleanup.sh
# Clean temp files on both Macs

echo "🧹 Cleaning M4 Mac..."
rm -rf ~/Library/Caches/*
rm -rf /tmp/*

echo "🧹 Cleaning older Mac..."
ssh oldmac-mini.local "rm -rf ~/Library/Caches/* /tmp/*"

echo "✅ Cleanup complete"
```

---

## Troubleshooting Guide

### Problem: "Connection refused" when trying SSH

**Solution:**
```bash
# 1. Verify older Mac has Remote Login enabled
# System Settings → General → Sharing → Remote Login ☑

# 2. Check if you have SSH access
ssh username@oldmac-mini.local
# Should ask for password, not refuse connection

# 3. Test with IP directly
ssh username@192.168.x.x
# If this works, DNS resolution issue (not critical)
```

### Problem: Lights on Netgear switch ports not lighting up

**Solution:**
```bash
# 1. Check cable connection (reseat it)
# 2. Check cable quality (try different cable)
# 3. Try different port on switch
# 4. Verify Ethernet port on Mac
# 5. Restart both Macs
# 6. Check System Settings → Network → Ethernet
#    Should show "Connected"
```

### Problem: File copy very slow (<10 MB/s)

**Solution:**
```bash
# 1. Check connection speed:
iperf3 -c oldmac-mini.local
# Should show 100+ Mbps

# 2. Try different cable
# 3. Try different port on switch
# 4. Check for interference
# 5. Verify network configuration (see Phase 3)

# 6. If over SMB (file sharing), try SSH instead:
rsync -avz user@oldmac-mini.local:/path ~/local-path
```

### Problem: "Cannot resolve oldmac-mini.local"

**Solution:**
```bash
# 1. Use IP address directly:
ping 192.168.x.x
# (Get IP from System Settings → Network → Ethernet)

# 2. Check both Macs on same network:
ifconfig en0  # On M4
ifconfig en0  # On older Mac
# Both should start with 192.168 or 169.254

# 3. Restart both Macs
# 4. Reset network on both: System Settings → Network → Advanced
```

### Problem: SMB Mount "Permission denied"

**Solution:**
```bash
# 1. Verify username/password correct
# 2. Check File Sharing enabled on older Mac
# 3. Try mounting with explicit credentials:
mount_smbfs smb://correctusername:correctpassword@oldmac-mini.local/SharedFolder ~/mount

# 4. Check shared folders in System Settings
# 5. If still failing, use SSH method instead:
sshfs username@oldmac-mini.local:/Users/username ~/mounts/oldmac
```

---

## Checklist: Setup Complete

### Phase 1: Hardware ✅
- [ ] Cat5e/Cat6 cables purchased/located
- [ ] Netgear switch powered up
- [ ] M4 Mac connected to switch (Port 1)
- [ ] Older Mac connected to switch (Port 3)

### Phase 2: Network Configuration ✅
- [ ] Both Macs show "Ethernet Connected"
- [ ] Computer names set (M4-Mac-mini, OldMac-mini)
- [ ] File Sharing enabled on both
- [ ] Remote Login (SSH) enabled on both

### Phase 3: Testing ✅
- [ ] Ping test passes (latency <1ms)
- [ ] SSH access works (both directions)
- [ ] File copy speed >100 MB/s
- [ ] Mount test passes (access older Mac files)

### Phase 4: Automation (Optional) ✅
- [ ] Backup script created (if needed)
- [ ] Monitoring enabled (if needed)
- [ ] Performance baseline recorded

---

## Summary

**You now have:**
- ✅ Two Macs connected via dedicated Ethernet (1 Gbps)
- ✅ Low latency (<1ms) for real-time communication
- ✅ File sharing between machines
- ✅ SSH remote access
- ✅ Expandable (switch has more ports for future devices)

**Ready for:**
- Distributed builds and compilation
- Backup automation
- AI inference distribution
- Real-time data synchronization
- Future expansion (add more Macs/devices)

**Cost:** ~$20-30 (cables only, switch already owned)
**Setup time:** 1-2 hours
**Complexity:** Low (mostly configuration, not coding)

---

## Next Steps

**When ready to execute:**
1. Acquire Cat5e/Cat6 cables (2x)
2. Follow Phase 1-2 (physical setup, 35 min)
3. Follow Phase 3 (network config, 30 min)
4. Follow Phase 5 (testing, 20 min)
5. Optional: Implement Phase 4 (automation)

**I'm ready to:**
- Provide detailed commands when you get stuck
- Debug network issues
- Optimize for your specific use cases
- Create additional automation scripts

**Ready when you are.** 🍑
