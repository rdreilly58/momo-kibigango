# AWS Mac Instance Quota Request Guide

**Date:** March 17, 2026, 12:41 PM EDT  
**Goal:** Request Mac instance access for your AWS account  
**Timeline:** 24-48 hours for AWS approval  
**Status:** Instructions provided below

---

## 📋 Step-by-Step: Request Mac Instance Quota

### Step 1: Open AWS Service Quotas Console
```
URL: https://console.aws.amazon.com/servicequotas/home
Region: us-east-1 (or your preferred region)
```

### Step 2: Search for Mac Instances

1. In the **Service Quotas** console, click **AWS services** (left sidebar)
2. Search for **"EC2"** → Click **Elastic Compute Cloud (EC2)**
3. In the quota list, search for **"mac"**

You should see quota entries like:
```
- Running On-Demand mac instances
- Running On-Demand mac1.metal instances
- Running On-Demand mac2.metal instances
- Running On-Demand mac3.metal instances
```

### Step 3: Request Quota for M3 Max

Look for: **"Running On-Demand mac3-max.metal instances"** (or similar)

1. Click on the quota row
2. Click **"Request quota increase"** button
3. Set **Desired quota value:** `1` (or higher if you want multiple)
4. Add optional note:
   ```
   GPU offload testing for open source project.
   Single mac3-max.metal instance needed.
   ```
5. Click **"Request quota increase"**

### Step 4: Confirm Request

You should see:
```
✅ Request submitted successfully
Request ID: [request-id]
Status: Pending
```

**Save the Request ID** — you can track it in the console.

---

## 🔔 What Happens Next

### Timeline
```
Now (12:41 PM EDT):     Request submitted
24 hours later:         Usually approved (can be faster)
48 hours later:         Definitely approved (if not, AWS will contact)
```

### How You'll Know
- ✅ Email from AWS (to account email)
- ✅ Console shows "Approved" status
- ✅ You can immediately launch mac3-max.metal instances

### If Denied
- Rare, but possible if account is new or unusual
- AWS will email explanation
- Can resubmit with more details
- Alternative: Contact AWS Support (paid)

---

## 🚀 Once Approved (24-48 Hours)

Once AWS approves, I'll:
1. Allocate Dedicated Host for Mac in us-east-1a
2. Launch mac3-max.metal instance
3. Configure:
   - Security group (SSH + ARD ports)
   - SSH key pair (already created)
   - macOS setup
   - Apple Remote Desktop (port 5900)

Then you can:
- **SSH:** `ssh -i ~/.ssh/vlm-deploy-key.pem ec2-user@[public-ip]`
- **ARD:** Open "Remote Desktop" app on your Mac → connect to IP

---

## 📊 What You're Requesting

### Requested Resource
```
Instance Type:   mac3-max.metal
Memory:          48GB unified
CPU:             12-core (6P + 6E)
GPU:             20-core integrated
Storage:         1TB SSD
Deployment:      EC2 Dedicated Host
Region:          us-east-1 (us-east-1a)
Commitment:      24+ hours minimum
```

### Cost
```
Dedicated Host: $40.33/day = $1,210/month
On-Demand:      $2.162/hour = $1,557/month (continuous)
```

### Why This Instance
- ✅ Large unified memory (48GB) for multi-model inference
- ✅ Apple Silicon (M3) for macOS/iOS development
- ✅ No PCIe bottleneck (unlike separate GPU)
- ✅ Can run Mistral-7B + Qwen-14B concurrently
- ✅ Desktop experience (macOS native)

---

## 📝 Request Details (For Reference)

**Service:** Elastic Compute Cloud (EC2)  
**Quota Name:** Running On-Demand mac3-max.metal instances  
**Current Value:** 0  
**Requested Value:** 1 (or more)  
**Reason:** GPU offload testing and open source development  
**Request Time:** Tue 2026-03-17 12:41 PM EDT  

---

## ✅ Checklist

- [ ] Open AWS Service Quotas console
- [ ] Navigate to EC2 service
- [ ] Find "mac3-max.metal" quota
- [ ] Click "Request quota increase"
- [ ] Set desired value to 1
- [ ] Add note about GPU offload project
- [ ] Submit request
- [ ] Note Request ID
- [ ] Check email for confirmation

---

## 🔗 Direct Links

**AWS Service Quotas (us-east-1):**
```
https://console.aws.amazon.com/servicequotas/home?region=us-east-1#!/services/ec2/quotas
```

**AWS Support (if needed):**
```
https://console.aws.amazon.com/support/home
```

---

## 📞 If Issues Arise

**Problem:** Quota request doesn't appear or won't increase  
**Solution:** Contact AWS Support (free tier available)
```
1. Go to AWS Support
2. Create "Service Quota" case
3. Explain: "Want to launch mac3-max.metal for development"
4. Usual resolution: Same day
```

**Problem:** Request denied  
**Solution:** Not typical for mac instances, but:
```
1. AWS will email explanation
2. Address any issues mentioned
3. Resubmit request
4. Contact support if persists
```

---

## 🎯 After Approval: What I'll Do

**Step 1 (Immediate)**
- ✅ Allocate Dedicated Host for mac3-max.metal
- ✅ Launch instance on that host
- ✅ Configure security group (SSH + ARD)
- ✅ Get public IP address

**Step 2 (Instance Setup)**
- ✅ Install ARD (macOS native, usually pre-enabled)
- ✅ Set ARD password
- ✅ Configure for desktop access from your Mac
- ✅ Test SSH access for OpenClaw

**Step 3 (Your Access)**
- ✅ Provide connection details:
  - SSH: `ssh -i ~/.ssh/vlm-deploy-key.pem ec2-user@[IP]`
  - ARD: Open "Remote Desktop" app, connect to IP:5900
  - Username/password for ARD (via email or secure channel)

---

## 💡 Timeline Summary

```
Now (12:41 PM EDT):         You request quota
24-48 hours:                AWS approves (email confirmation)
Approval:                   I launch instance immediately
5 min after approval:       Instance running, IPs assigned
10 min after approval:      ARD configured and ready
11 min after approval:      You connect via Remote Desktop

Total time: < 12 hours
(If approved fast)
```

---

## 🔐 Security Notes

**Your MAC Instance Will Have:**
- ✅ SSH key pair (for OpenClaw)
- ✅ Security group (whitelist ports 22 + 5900)
- ✅ Private IP (internal AWS network)
- ✅ Public IP (for external access)
- ✅ ARD password (shared securely)

**Best Practice:**
- Restrict security group to your home IP (or VPN)
- Don't leave instance running 24/7 if not needed
- Terminate when testing complete (or keep for production)

---

## 📋 Once Approved

I'll create:
1. `mac-instance.json` — Configuration file with all details
2. Connection guide — How to SSH and use ARD
3. Setup script — Automate instance configuration
4. Security documentation — Keys and access methods

---

## 🎬 Ready to Request?

**Here's what you need to do (takes ~2 minutes):**

1. Go to: https://console.aws.amazon.com/servicequotas/home?region=us-east-1
2. Search "mac instances"
3. Find "Running On-Demand mac3-max.metal instances"
4. Click "Request quota increase"
5. Set value to `1`
6. Submit

**Expected:** Approved within 24 hours, usually much faster.

Once approved, I'll launch and configure everything for you.

---

**Next Update:** Will ping when I see AWS approval notification (or hourly check after ~20 min)

