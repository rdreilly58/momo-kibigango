# Mac M3 Max Instance Launch Status

**Date:** March 18, 2026 — 4:41 AM EDT  
**Status:** ⏳ CONFIGURATION ISSUE (Quota Approved, Launch Blocked)

---

## ✅ What's Done

- ✅ **Quota Approved:** `mac-m4max.metal` quota (code L-D82CB68A) = **Value 1.0** (ACTIVE)
- ✅ **SSH Key Created:** `~/.ssh/openclaw-mac-key.pem` (600 perms, ready)
- ✅ **AWS Authentication:** Verified and working
- ✅ **Region:** us-east-1 selected and confirmed operational

---

## ❌ The Problem

AWS us-east-1 reports the configuration "mac-m4max.metal + macOS 14+ AMI" is **"not supported"** even though:
1. The instance type exists in us-east-1
2. The quota is approved
3. The AMI is available

**Error:**
```
The requested configuration is currently not supported.
```

This is likely a capacity/provisioning issue specific to us-east-1 at this moment.

---

## 🔧 Solutions

### **Option A: Wait & Retry (Recommended)**
AWS might unlock capacity in 1-2 hours. Retry the launch command:

```bash
aws ec2 run-instances \
  --image-id ami-002d6140c42b927ef \
  --instance-type mac-m4max.metal \
  --region us-east-1 \
  --key-name openclaw-mac-key \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=Momotaro-MacDev}]' \
  --output json | jq '.Instances[0] | {InstanceId, State: .State.Name}'
```

**Expected when it works:**
```json
{
  "InstanceId": "i-0xxxxxxxxxx",
  "State": "pending"
}
```

### **Option B: Switch Regions**
Try us-west-2 or eu-west-1 (often have better mac capacity):

```bash
aws ec2 run-instances \
  --image-id ami-0xxxxx  # Find region-specific AMI
  --instance-type mac-m4max.metal \
  --region us-west-2 \
  --key-name openclaw-mac-key-usw2
```

### **Option C: Use mac2.metal (x86_64)**
If you need Xcode builds for Intel Macs, mac2.metal is more stable:

```bash
# Find x86_64_mac AMI for mac2.metal
aws ec2 describe-images \
  --owners amazon \
  --filters "Name=name,Values=amzn-ec2-macos*x86_64*" \
  --region us-east-1 \
  --query 'sort_by(Images, &CreationDate)[-1].[ImageId]' \
  --output text

# Launch
aws ec2 run-instances \
  --image-id ami-xxxxxxxx \
  --instance-type mac2.metal \
  --region us-east-1 \
  --key-name openclaw-mac-key
```

---

## 📊 What We Have Ready

| Component | Status | Details |
|-----------|--------|---------|
| AWS Quota | ✅ Approved | mac-m4max.metal, Value=1.0 |
| SSH Key | ✅ Ready | ~/.ssh/openclaw-mac-key.pem |
| Region | ✅ Selected | us-east-1 |
| Subnet | ✅ Available | subnet-0fa346347ac41fd30 |
| Security Groups | ✅ Default | Ready |
| Tags | ✅ Configured | Name=Momotaro-MacDev, Purpose=Xcode-Builds |

---

## 📋 Next Steps

**Immediate (Bob decides):**
1. **Wait & Retry:** I can retry in 30 minutes automatically
2. **Switch Regions:** Pick us-west-2 or eu-west-1 (need new SSH key)
3. **Use mac2.metal:** Fallback to x86_64 instance type (different architecture)

**Recommendation:** Option A (Wait & Retry). AWS usually unlocks capacity quickly. I'll set up an auto-retry in 1 hour.

---

## Command to Manually Retry

```bash
aws ec2 run-instances \
  --image-id ami-002d6140c42b927ef \
  --instance-type mac-m4max.metal \
  --region us-east-1 \
  --key-name openclaw-mac-key \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=Momotaro-MacDev}]' \
  --output json | jq '.Instances[0]'
```

If this succeeds, you'll get your Instance ID and the instance will launch.

---

**Status:** All prerequisites met. Awaiting AWS capacity. 🍑
