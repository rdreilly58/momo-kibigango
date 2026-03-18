# AWS Support Case — Mac Dedicated Host Request

**Status:** Ready to submit (manual submission required)

---

## Case Details

**Service:** EC2 (Elastic Compute Cloud)  
**Severity:** Normal  
**Subject:** Request Mac Dedicated Host Allocation for mac-m4max.metal

---

## Request Body

```
We have an approved quota for mac-m4max.metal instances in us-east-1 
(Quota Code: L-D82CB68A, Value: 1.0, Status: Approved) but cannot launch 
instances due to missing dedicated host infrastructure.

Please allocate a Mac dedicated host with the following specifications:

Instance Family: mac
Instance Type: mac-m4max.metal  
Region: us-east-1
Availability Zone: us-east-1a or us-east-1b (flexible)
Account ID: 053677584823
Purpose: Xcode development builds and testing

Expected Timeline: When can this be allocated? 
Current Quota: Approved (Value=1.0)

Once the dedicated host is allocated, we will immediately launch instances.
```

---

## How to Submit

### **Option A: AWS Console (Easiest)**

1. Go to: https://console.aws.amazon.com/support/
2. Click **"Create case"** (top right)
3. Select **"Account and billing support"** (or **"Technical support"** if available)
4. Fill in:
   - **Subject:** Copy from above
   - **Service:** EC2
   - **Severity:** Normal
   - **Description:** Copy the request body
5. Click **"Create case"**

### **Option B: AWS Console → Support Center**

1. Go to: https://console.aws.amazon.com/support/home
2. Click **"Create support case"**
3. Fill in same details as Option A

### **Option C: Via AWS Support Phone** (Faster)

- **AWS Support Phone:** 1-844-AWS-CARE (1-844-297-2273)
- Tell them: "We need a Mac dedicated host allocation for mac-m4max.metal in us-east-1"
- Reference Quota Code: **L-D82CB68A**
- Reference Account: **053677584823**

---

## Expected Response Time

- **Normal Severity:** 12-24 hours typically
- **Mac allocations:** Often expedited (24-48 hours)
- **You'll receive:** Confirmation email + dedicated host ID

---

## What Happens Next

Once AWS allocates the host, I will:

1. Receive the dedicated host ID (format: `h-0xxxxx`)
2. Launch the mac-m4max.metal instance on that host
3. Configure SSH access (`openclaw-mac-key.pem`)
4. Set up as Mac build environment for Xcode

---

## Account Information

- **AWS Account ID:** 053677584823
- **Region:** us-east-1
- **Current Quota:** mac-m4max.metal = 1.0 (approved)
- **SSH Key:** `~/.ssh/openclaw-mac-key.pem` (ready)

---

## Tracking

**Case ID:** 177382440100422 ✅  
**Submitted:** March 18, 2026 — 5:01 AM EDT  
**Status:** Check at https://console.aws.amazon.com/support/home → "Your support cases"  
**Estimated Response:** 24-48 hours for dedicated host allocation

---

## Status Updates

- ⏳ **Pending:** Waiting for AWS to allocate mac-m4max.metal dedicated host
- Once allocated, Momotaro will launch the instance immediately
