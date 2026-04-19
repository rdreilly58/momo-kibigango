# AWS Support Ticket Template — Mac Instance Launch

## Quick Steps

1. Go to: https://console.aws.amazon.com/support/home
2. Click **"Create case"** button (top right)
3. Copy-paste the content below into the form

---

## TICKET CONTENT (Copy & Paste)

**Category:** Service Limit (Quota)

**Subject:** Unable to Launch mac-m4max.metal Instances in us-east-1

**Priority:** Normal (but I can switch to High if needed)

**Description:**

```
Account ID: 053677584823
Region: us-east-1

ISSUE:
Our account has been approved for the "Running Dedicated mac-m4max Hosts" quota 
(Request ID: 09adbb0969524b309594ea609798ebf6SRpBCFI7). However, when attempting 
to launch a mac-m4max.metal instance, we receive the error:

"The requested configuration is currently not supported. 
Please check the documentation for supported configurations."

We also tried alternative Mac instance types (mac1.metal, mac2.metal) 
with the same error in us-east-1.

WHAT WE'VE TRIED:
- Launching via AWS CLI with correct VPC/subnet/security group configuration
- Attempting mac1.metal, mac2.metal, and mac-m4max.metal instance types
- Different availability zones (us-east-1a, us-east-1e)

WHAT WE NEED:
1. Confirmation that mac-m4max.metal is supported in us-east-1
2. If not available in us-east-1, recommendation for alternative region with availability
3. Any regional restrictions or prerequisites we need to know about

USE CASE:
iOS development with Xcode and Swift compilation. We're setting up a dedicated 
Mac instance to support our engineering team.

Thank you for your help!
```

---

## EXPECTED RESPONSE TIME

- **Standard Support:** 1-2 business days
- **Business Support:** 4-12 hours
- **Enterprise Support:** 1 hour (if applicable)

## AFTER TICKET IS CREATED

AWS will likely respond with one of these:

**Option A:** "Here's how to enable it in your account" → We proceed with launch script

**Option B:** "That's not available in us-east-1, try us-west-1 or us-west-2" → We update script to try us-west-2

**Option C:** "Here's an alternative approach..." → We follow their recommendation

**Once we hear back, let me know and we'll:**
1. Update the launch script if needed
2. Deploy the Mac instance
3. Install Xcode and dev tools
4. You're ready for iOS dev!

---

## DO YOU WANT ME TO:

1. ✅ Open the ticket for you programmatically? (need your AWS support preference)
2. ✅ Test us-west-2 region while we wait?
3. ✅ Set up your GPU instance (54.81.20.218) as a temporary workaround?
4. ✅ Something else?

Just say the word! 🍑
