# AWS Mac Instance Quota Check — All Regions

**Current Status:** Primary request (us-east-1) pending 4+ days  
**Action:** Check alternative regions for availability

## Available AWS Regions for Mac Instances

| Region | Code | Status | Notes |
|--------|------|--------|-------|
| **N. Virginia** | us-east-1 | ⏳ PENDING (4+ days) | Current request: f385e0e9ebe248b1bbbc70b36755d34bU68btWJY |
| **Ohio** | us-east-2 | ❓ Unknown | Alt option |
| **N. California** | us-west-1 | ❓ Unknown | Alt option |
| **Oregon** | us-west-2 | ✅ RECOMMENDED | Typically available, faster approval |
| **Ireland** | eu-west-1 | ✅ RECOMMENDED | EU alternative, typical 24-48h approval |
| **London** | eu-west-2 | ❓ Unknown | EU option |
| **Frankfurt** | eu-central-1 | ❓ Unknown | EU option |
| **Singapore** | ap-southeast-1 | ❓ Unknown | APAC option |
| **Sydney** | ap-southeast-2 | ❓ Unknown | APAC option |
| **Tokyo** | ap-northeast-1 | ❓ Unknown | APAC option |

## Recommended Strategy

### Option 1: Submit to us-west-2 (Fastest)
- Typically 24-48 hours approval
- Geographically close to primary
- Good latency for US operations

### Option 2: Submit to eu-west-1 (Backup)
- Good as secondary region
- EU/international support

### Option 3: Wait for us-east-1 (Current)
- Already submitted (4+ days)
- May be in processing queue
- Escalate to Premium Support if needed

## How to Check Status

**Via AWS Console:**
1. Log in to AWS Console
2. Navigate: **Service Quotas** (top search bar)
3. Select: **EC2**
4. Search: **mac-m4pro.metal** or **mac-m4max.metal**
5. View **Recent requests** section
6. Check status for each region

**Via AWS CLI:**
```bash
# Check quota status in us-west-2
aws service-quotas get-service-quota \
  --service-code ec2 \
  --quota-code mac-m4pro.metal \
  --region us-west-2

# List pending requests
aws service-quotas list-requested-service-quota-change-history \
  --service-code ec2 \
  --region us-west-2
```

## Escalation Paths

**If us-east-1 still pending after 5 days:**
1. Contact AWS Premium Support (if available)
2. Submit to us-west-2 in parallel
3. Reference original request ID: `f385e0e9ebe248b1bbbc70b36755d34bU68btWJY`

**Fast-track options:**
- AWS Premium Support: 1-hour response SLA
- AWS Account Team: Direct escalation
- Submit to multiple regions simultaneously

## Timeline

| Date | Event | Status |
|------|-------|--------|
| Mar 20, 6:58 PM | Original request submitted (us-east-1) | ⏳ PENDING |
| Mar 21-22 | Expected approval window | ❌ MISSED |
| Mar 23, 6:58 PM | 72-hour escalation window | ❌ MISSED |
| Mar 25, 1:05 AM | 4+ days, still pending | ❌ OVERDUE |
| **Mar 25, 1:05 AM** | **Consider alternative regions** | ⏳ ACTION NEEDED |

## Next Steps

1. **Check AWS Console** (Service Quotas → EC2 → mac-m4pro.metal)
   - Status of us-east-1 request
   - Available quota in other regions

2. **Submit to us-west-2** (if available)
   - Expected: 24-48 hour approval
   - Will have Mac instance faster

3. **Escalate us-east-1** (optional)
   - Contact AWS Support if quota is available but approval stuck
   - Request expedited review

4. **Monitor both** once submitted
   - Email notifications when approved
   - Auto-launch instance (script ready)

## Resources

- AWS Service Quotas: https://console.aws.amazon.com/servicequotas/
- AWS EC2 Mac pricing: https://aws.amazon.com/ec2/pricing/on-demand/#Mac_instances
- Request deadline info: https://docs.aws.amazon.com/general/latest/gr/ec2-service.html

---

**Last Updated:** March 25, 2026, 1:05 AM EDT  
**Action Required:** Check AWS Console → Service Quotas for current status

---

## Update: us-west-2 Request Submitted (March 25, 1:08 AM)

**Action Taken:** Submitted parallel Mac quota request to us-west-2

**New Status:**
| Region | Request Date | Status | Expected Approval |
|--------|--------------|--------|-------------------|
| us-east-1 | Mar 20, 6:58 PM | ⏳ PENDING (overdue) | 24-48h (missed) |
| us-west-2 | Mar 25, 1:08 AM | ✅ SUBMITTED | 24-48h from now |

**Strategy:** Monitor both regions. Whichever approves first will be used for instance launch.

**Next Steps:**
1. Check AWS Console for approval notifications (both regions)
2. Expect us-west-2 approval by March 26-27, 1:08 AM
3. Auto-launch script ready: `~/.openclaw/workspace/scripts/auto-launch-mac-instance.sh`
4. Optionally escalate us-east-1 if approval very delayed

**Monitor Script:**
```bash
# Check both regions hourly
watch -n 3600 'aws service-quotas list-requested-service-quota-change-history --service-code ec2 --region us-west-2 | jq ".RequestedQuotaChangeHistoryDetails[0]"'
```

---
