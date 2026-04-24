# Mac Instance Launch — Platform Restrictions

**Status:** ❌ BLOCKED (Quota Approved, AWS Configuration Issue)  
**Date:** March 18, 2026 — 4:47 AM EDT

---

## What We Have

✅ **Quota Approved:** `mac-m4max.metal` (Value = 1.0, Active)  
✅ **SSH Keys Created:**
  - `~/.ssh/openclaw-mac-key.pem` (us-east-1)
  - `~/.ssh/openclaw-mac-key-usw2.pem` (us-west-2)  
✅ **AWS Authentication:** Working  
✅ **Credentials:** Valid and authenticated

---

## The Block

All Mac instance types fail with platform errors:

```
❌ mac-m4max.metal (us-east-1): "configuration not supported"
❌ mac-m4max.metal (us-west-2): "configuration not supported"
❌ mac2.metal (us-east-1): "tenancy not supported"
❌ mac2.metal (us-west-2): "tenancy not supported"
❌ mac1.metal (us-east-1): "tenancy not supported"
```

### Root Cause

AWS Mac instances require **dedicated host** infrastructure that:
1. Must be pre-allocated in your account (not on-demand)
2. Requires special AMI configurations
3. Has region/availability-zone restrictions
4. Quota approval alone doesn't guarantee launch capability

---

## Solutions

### **Option A: Use AWS Dedicated Hosts (Proper Path)**

Mac instances require you to allocate a dedicated host first:

```bash
# 1. Check available dedicated hosts in your region
aws ec2 describe-hosts \
  --filters "Name=instance-family,Values=mac" \
  --region us-east-1

# 2. If none exist, allocate one (this can take 24-48 hours)
aws ec2 allocate-hosts \
  --instance-family mac \
  --instance-type mac2.metal \
  --region us-east-1 \
  --availability-zone us-east-1a

# 3. Once allocated, launch instance on the host
aws ec2 run-instances \
  --image-id ami-xxxxx \
  --instance-type mac2.metal \
  --region us-east-1 \
  --host-id h-0xxxxx  # From allocate-hosts response
```

**Timeline:** 24-48 hours for AWS to allocate the host.

### **Option B: Use EC2 Mac Instance via AWS AppKit (Managed)**

AWS AppKit is AWS's managed macOS build environment:
- No dedicated host setup needed
- Available as managed service
- Better for CI/CD pipelines

**Route:** Contact AWS Support → Request AppKit for Xcode builds

### **Option C: Local Development Alternative**

Use your existing M4 Mac mini instead:
- Bob's laptop has M4 (similar to M3 Max)
- Can run Xcode locally
- No AWS infrastructure needed

---

## What Happened

1. **Quota Request:** ✅ Submitted and approved by AWS (this worked)
2. **Quota Activation:** ✅ Value shows 1.0 (this worked)
3. **Launch Attempt:** ❌ AWS blocks launch because no dedicated host exists

The quota doesn't automatically allocate infrastructure—it just removes the quota limit. The actual host allocation is a separate process.

---

## Recommendation

**For Momotaro's use case (Xcode builds):**

Since Bob already has an M4 Mac mini locally:
- **Faster:** Use local machine for development/testing
- **Cheaper:** Avoid $500+/month AWS Mac instance
- **Simpler:** No AWS infrastructure management

The AWS Mac instance makes sense if you need:
- CI/CD automation (automated builds)
- Multiple concurrent build agents
- Always-on build server

For occasional development work, the local M4 is better.

---

## If You Want to Proceed with AWS Mac

**Steps:**
1. Open AWS Support Case → Request Mac dedicated host allocation
2. Wait 24-48 hours for allocation
3. Once allocated, I can launch instance on that host

**Cost:** ~$500/month for the instance (plus $100/month for the dedicated host).

---

## Current Decision

Quota is approved and ready, but AWS infrastructure constraints prevent immediate launch. Options:

- [ ] Wait for AWS Support to allocate dedicated host (24-48 hours)
- [ ] Use AppKit managed service instead
- [ ] Use local M4 Mac mini for development
- [ ] Cancel and reallocate quota for different service

**What would Bob prefer?** 🍑
