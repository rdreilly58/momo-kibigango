# AWS Account vCPU Limit Issue

**Status:** ⚠️ Cannot launch GPU instances (account limit exceeded)

**Error:** 
```
You have requested more vCPU capacity than your current vCPU limit of 0 allows 
for the instance bucket that the specified instance type belongs to.
```

## Why This Happens

New AWS accounts start with GPU vCPU limits at 0. You need to request increases.

## Solution: Request vCPU Limit Increase

### Automated (AWS CLI):
```bash
# Request limit increase for GPU instances
aws service-quotas request-service-quota-increase \
  --service-code ec2 \
  --quota-code L-DB2E81BA \
  --desired-value 8 \
  --region us-east-1
```

### Manual (AWS Console):
1. Go to: https://console.aws.amazon.com/servicequotas/
2. Search for "EC2"
3. Find "Running g4dn instances" (or p3 instances)
4. Click and request increase to 4-8 vCPUs
5. AWS approves within 24 hours (usually instantly)

## Temporary Workarounds

### Option 1: Use CPU-Only Instance (Slow but Free)
```bash
aws ec2 run-instances \
  --image-id ami-04680790a315cd58d \
  --instance-type t3.xlarge \
  --key-name vlm-key-pair \
  --region us-east-1
```

**Pros:** Instant launch, no vCPU limits  
**Cons:** Very slow (~10s per response), not for production

### Option 2: Use Google Cloud (Different Provider)
- Better GPU access for new accounts
- Similar pricing (~$0.35/hr for T4)

### Option 3: Use Lambda + S3 (Serverless)
- No EC2 limits to worry about
- Pay per inference only
- More expensive per request

## Quick Fix (Recommended)

**Do this now:**
1. Go to AWS Service Quotas: https://console.aws.amazon.com/servicequotas/
2. Search "EC2 Running g4dn"
3. Click it, request increase to 8 vCPUs
4. AWS usually approves in <1 hour
5. Come back and run the deployment script again

## After Limit Increase

Once approved, your account will support:
- g4dn.xlarge (NVIDIA T4, $0.526/hr)
- g4dn.12xlarge (NVIDIA T4, much bigger)
- p3.2xlarge (V100, $3.06/hr)
- a2.xlarge (Trainium)

Then rerun:
```bash
cd ~/.openclaw/workspace/skills/speculative-decoding
./scripts/launch-aws-instance.sh vlm-key-pair
```

## Alternative: Use GCP Instead

Google Cloud is often easier for GPU access:

```bash
# Install gcloud CLI
brew install google-cloud-sdk

# Create VM with GPU
gcloud compute instances create vlm-test \
  --zone=us-central1-a \
  --machine-type=n1-standard-4 \
  --accelerator=type=nvidia-tesla-t4,count=1 \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud
```

**Cost:** ~$0.35/hr (cheaper than AWS)  
**Setup:** ~15 minutes

## Cost Comparison

| Provider | Instance | Cost/hr | GPU | Notes |
|----------|----------|---------|-----|-------|
| AWS | g4dn.xlarge | $0.526 | T4 16GB | Need limit increase |
| AWS | p3.2xlarge | $3.06 | V100 16GB | Need limit increase |
| GCP | n1-std-4 + T4 | $0.35 | T4 16GB | Usually available |
| Lambda | Per inference | ~$0.50-1 | Shared | No GPU management |

## Recommended Next Steps

**Priority 1 (5 minutes):** Request AWS vCPU limit increase
- Usually approved instantly
- Then you can use cheaper g4dn.xlarge ($0.526/hr)

**Priority 2 (if AWS doesn't approve quickly):** Use GCP
- Typically available without requests
- Costs $0.15 less/hour
- Same vLLM setup

**Priority 3 (if you need GPU now):** Use CPU-only instance
- Works but very slow (~10-20s per response)
- Good for testing only

---

**Choose one and let me know!** 🍑
