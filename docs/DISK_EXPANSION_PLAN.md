# Disk Expansion Plan — External Storage Solution

**Date:** March 25, 2026  
**Status:** ✅ PLAN CREATED  
**Goal:** Add external storage to resolve 90% disk full crisis

---

## Current Situation

**Disk Status:**
- **Total capacity:** 894 GB
- **Used:** 779 GB (90%)
- **Available:** 91 GB (critical)

**Space breakdown (largest first):**
| Directory | Size | Type | Action |
|-----------|------|------|--------|
| `~/fpga-tools` | 159 GB | Development | Archive to external |
| `~/Library` | 115 GB | System/Apps | Keep (needed for system) |
| `~/VirtualMachines` | 37 GB | VMs/Docker | Archive to external |
| `~/Projects` | 7.6 GB | Development | Archive to external |
| `~/models` | 4.0 GB | ML models | Archive to external |
| `~/.openclaw/workspace` | 2.9 GB | OpenClaw | Keep (active work) |
| `~/oss-cad-suite` | 1.8 GB | CAD tools | Archive to external |
| `~/mlx-vllm-env` | 1.4 GB | Python env | Keep (active) |

**Total archivable: ~210 GB**

---

## Storage Options

### Option 1: External USB SSD (FASTEST, CHEAPEST)
- **Product:** Samsung T7 Shield 2TB USB 3.2
- **Cost:** ~$120-150
- **Speed:** 1050 MB/s read/write
- **Durability:** Shockproof, waterproof
- **Setup time:** 30 minutes (format + transfer)
- **Capacity:** 2 TB (plenty for 210 GB + future growth)
- **Recommendation:** ⭐⭐⭐⭐⭐ **Best for immediate relief**

### Option 2: Thunderbolt/USB-C External SSD (PORTABLE)
- **Product:** OWC Mercury Elite Pro Dual SSD 2TB
- **Cost:** ~$250-300
- **Speed:** 2800 MB/s Thunderbolt 4
- **Durability:** Professional grade
- **Setup time:** 30 minutes
- **Capacity:** 2 TB
- **Recommendation:** ⭐⭐⭐⭐ **Premium portable option**

### Option 3: Cloud Storage (SCALABLE, ALWAYS AVAILABLE)
- **Provider:** AWS S3 + AWS DataSync
- **Cost:** ~$0.023/GB/month (~$5/month for 210 GB)
- **Speed:** Network dependent (slower, but cloud-accessible)
- **Setup time:** 2-3 hours (AWS setup + migration)
- **Capacity:** Unlimited
- **Recommendation:** ⭐⭐⭐ **Long-term, pairs well with external SSD**

### Option 4: NAS (NETWORK ATTACHED STORAGE)
- **Product:** Synology DS923+ 4-bay NAS
- **Cost:** ~$400-500 + drives
- **Speed:** 1 Gbps network (slower than USB)
- **Setup time:** 1-2 hours
- **Capacity:** Scalable (4-16 TB depending on drives)
- **Recommendation:** ⭐⭐ **Overkill for home use, good for future backup strategy**

---

## Recommended Approach: HYBRID

**Best solution combines external SSD + cloud backup:**

1. **Immediate (Today):**
   - Order Samsung T7 Shield 2TB (~$150, arrives in 1-2 days)
   - Quick relief: Frees ~210 GB instantly when populated

2. **Setup (Tomorrow/Day 3):**
   - Format external SSD as MacOS Extended (journaled)
   - Create archive folders: `Archive/fpga-tools`, `Archive/VirtualMachines`, etc.
   - Move large directories to external storage (takes ~2 hours for 210 GB)
   - Disk frees up to ~75% usage (healthy)

3. **Long-term (Week 2):**
   - Set up AWS S3 bucket for archival copies
   - Configure automated sync: External SSD → S3 (daily)
   - Provides disaster recovery + cloud access

---

## Implementation Steps

### Step 1: Order External SSD
**Action:** Purchase Samsung T7 Shield 2TB
- **Where:** Amazon, B&H Photo, Best Buy
- **Expected cost:** $120-150
- **Delivery:** 1-2 days

### Step 2: Format and Mount
```bash
# Once arrived, format the drive
# 1. Connect via USB-C
# 2. Open Disk Utility
# 3. Select the drive
# 4. Click "Erase"
# 5. Format as "APFS" or "Mac OS Extended (Journaled)"
# 6. Name it "Archive"

# Verify mount
mount | grep -i archive
```

### Step 3: Create Archive Structure
```bash
mkdir -p /Volumes/Archive/{fpga-tools,virtualm machines,projects,models,cad-suite}
```

### Step 4: Move Data (Using `rsync` for safety)
```bash
# Move fpga-tools (159 GB - largest)
rsync -avh --progress ~/fpga-tools/ /Volumes/Archive/fpga-tools/

# Move VirtualMachines (37 GB)
rsync -avh --progress ~/VirtualMachines/ /Volumes/Archive/virtualm achines/

# Move Projects (7.6 GB)
rsync -avh --progress ~/Projects/ /Volumes/Archive/projects/

# Move models (4 GB)
rsync -avh --progress ~/models/ /Volumes/Archive/models/

# Move oss-cad-suite (1.8 GB)
rsync -avh --progress ~/oss-cad-suite/ /Volumes/Archive/cad-suite/

# Verify all transferred successfully
du -sh /Volumes/Archive/*
```

### Step 5: Remove Originals (After Verification)
```bash
# ONLY after confirming copies on external drive
rm -rf ~/fpga-tools ~/VirtualMachines ~/Projects ~/models ~/oss-cad-suite

# Verify disk space
df -h ~
# Should now show ~70-75% usage
```

### Step 6: Create Symlinks (Optional, for convenience)
```bash
# Link back to home for quick access without copying
ln -s /Volumes/Archive/fpga-tools ~/fpga-tools
ln -s /Volumes/Archive/projects ~/Projects
ln -s /Volumes/Archive/models ~/models
# etc.

# Now ~/fpga-tools behaves like original, but reads from external drive
```

---

## Safety Procedures

**CRITICAL: Verify Before Deleting**

1. **Always use `rsync` with `--progress`**
   - Shows transfer status in real-time
   - Can resume if interrupted
   - More reliable than `cp` or `mv`

2. **Verify transfer completed:**
   ```bash
   # Source and destination should have same size
   du -sh ~/fpga-tools
   du -sh /Volumes/Archive/fpga-tools
   # Should match exactly
   ```

3. **Test symlink works (if creating):**
   ```bash
   ls -la ~/fpga-tools  # Should list files from external drive
   ```

4. **Only then delete original:**
   ```bash
   rm -rf ~/fpga-tools  # Safe now that symlink handles it
   ```

---

## Post-Move Disk Status

**Expected result after moving 210 GB:**
- **Before:** 779 GB used / 894 GB = 90% (CRITICAL)
- **After:** 569 GB used / 894 GB = 64% (HEALTHY)
- **Free space:** 325 GB (plenty of headroom)

---

## Monitoring & Maintenance

### Weekly Check
```bash
# Check disk usage
df -h ~

# Check if external SSD is still mounted
mount | grep -i archive

# Check recent changes
find ~ -mtime -7 -type f | wc -l  # Files modified in last 7 days
```

### Monthly Backup
```bash
# Back up external SSD to cloud (future AWS setup)
# For now, keep original + external as 2-copy protection
```

---

## Cost Breakdown

| Component | Cost | Timeline | Notes |
|-----------|------|----------|-------|
| Samsung T7 Shield 2TB | $120-150 | Immediate | One-time purchase |
| AWS S3 storage | $5/month | Optional, week 2 | ~$60/year for 210 GB |
| **Total (one-time)** | **$120-150** | **Today** | **Solves disk crisis** |
| **Total (recurring)** | **$5/month** | **Optional** | **Long-term backup** |

---

## Next Actions

1. **Today (March 25):**
   - ✅ Approve plan (decision made: Option D)
   - [ ] Order Samsung T7 Shield 2TB

2. **Tomorrow (March 26):**
   - [ ] Drive arrives
   - [ ] Format and mount

3. **Day 3 (March 27):**
   - [ ] Create archive structure
   - [ ] Run rsync for all directories
   - [ ] Verify transfers
   - [ ] Delete originals
   - [ ] Verify disk space

4. **Week 2 (April 1):**
   - [ ] Optional: Set up AWS S3 for backup
   - [ ] Configure daily sync

---

## Troubleshooting

**"rsync is taking too long"**
- Normal: 210 GB at USB 3.2 speed (1050 MB/s) = ~3-4 hours
- Keep external drive plugged in, don't interrupt
- You can use the Mac normally while rsync runs in background

**"Transfer failed partway through"**
- rsync can resume: just run the same command again
- It will skip already-transferred files and continue

**"External drive unmounts randomly"**
- Check USB cable connection
- Try different USB port
- Update Samsung firmware if available

**"I deleted the original before verifying!"**
- If you have Time Machine backup: recover from there
- If not: external drive copy is still safe (that's the point!)

---

## Long-term Strategy

**This solution handles:**
- ✅ Immediate disk crisis (90% → 64%)
- ✅ Fast local access (USB 3.2, 1050 MB/s)
- ✅ Portable backup (take drive with you)
- ✅ Future scalability (2 TB, can upgrade later)

**Optional future improvements:**
- Add AWS S3 for disaster recovery
- Add NAS for whole-home backup
- Add Time Machine for automated backups
- Archive older projects to cloud-only storage
