# AWS Mac Instance Launch - Blockers & Solutions

## Problem Summary
Mac instance types (mac1.metal, mac2.metal) cannot be launched in us-east-1 despite:
- ✅ Quota approved for mac-m4max
- ✅ SSH key created
- ✅ Security group configured
- ✅ Subnet/VPC ready

## Errors Encountered
1. **mac-m4max.metal**: "The requested configuration is currently not supported"
2. **mac1.metal**: "The requested tenancy is not supported for this instance type"
3. **mac2.metal**: API call hangs (timeout after 2 min)

## Root Cause Analysis
- Mac instances require **dedicated hosts** in some regions
- us-east-1 availability may be limited or require pre-provisioned hosts
- m4 instances (Apple Silicon) likely not yet deployed to us-east-1

## Solutions (in order of preference)

### Option 1: AWS Support Ticket (Recommended)
**Action:** Create a support case with AWS directly

```bash
# Bob, you can open a ticket at:
https://console.aws.amazon.com/support/home

# Provide:
- Account ID: 053677584823
- Region: us-east-1
- Request: Launch mac-m4max.metal instance for iOS development
- Current quota: Approved
- Error: "configuration not supported"
```

**Expected Response:** 24-48 hours
AWS will either:
- Enable mac instances in your account/region
- Recommend alternative regions (us-west-1 or eu-west-1 often have availability)
- Provide alternative pricing/options

### Option 2: Try Alternative Region
AWS Mac instances may be available in other US regions:

```bash
# Check us-west-2 (often has good availability)
aws ec2 describe-images --region us-west-2 --owners 628277914472 \
  --filters "Name=name,Values=amzn-ec2-macos*" \
  --query 'Images[*].[ImageId,Name]' --output text

# If found, launch there instead:
export AWS_REGION=us-west-2
/Users/rreilly/.openclaw/workspace/skills/aws-mac-launch/scripts/launch-mac-instance.sh
```

### Option 3: Use AWS Directly (Manual)
If you can access AWS Console, try the dedicated host flow:
1. Go to EC2 Dashboard → Dedicated Hosts
2. Click "Allocate Host"
3. Select `mac-m4max` instance family
4. Let AWS assign availability
5. Launch instance on that host

### Option 4: Temporary Alternative
While waiting for Mac support, use the GPU instance for:
- Testing Swift code compilation (via SSH remote compiling)
- Running simulator tests with `simctl`
- Building via `xcodebuild` over SSH

Your GPU instance is ready: `54.81.20.218`

## Next Steps for Bob

**Immediate (5 min):**
1. Open AWS support ticket (Option 1)
2. Mention that Quota was approved but instances won't launch

**Fallback (if support takes time):**
- Try Option 2: us-west-2 region
- Or use GPU instance for remote Xcode work

**Timeline:**
- AWS response: 24-48 hours typically
- Instance launch: 15-20 min once approved
- Xcode install: 20-30 min

Would you like me to:
1. ✅ Create the support ticket content you can paste?
2. ✅ Test us-west-2 region automatically?
3. ✅ Set up remote Xcode on your GPU instance as a workaround?
