# 🚀 AWS Quick Start — ReillyDesignStudio

**Current Date:** Saturday, March 14, 2026 at 5:22 PM EDT

---

## ✅ Current AWS Infrastructure

**Good news:** Your AWS account is already well-structured!

### **Existing Resources**

```
📦 S3 Buckets (3)
├── amplify-reillydesignstudio-dev-a7baa-deployment (Amplify builds)
├── lucianandgideon-coloring-pages (Legacy app)
└── reillydesignstudio-assets ⭐ (READY FOR USE)

🚀 Amplify Apps (2)
├── reillydesignstudio → d1az18myz2viu6.amplifyapp.com (ACTIVE)
└── lucianandgideon → d8trutozhfvsx.amplifyapp.com

👤 IAM Users (1)
└── reillydesignstudio-app ✅ (Service account for automation)

📊 Cost Tracking
└── Enabled (AWS Cost Explorer available)
```

---

## 🎯 Immediate Actions (This Week)

### **1. Verify S3 Bucket Configuration**
```bash
# Check reillydesignstudio-assets bucket
aws s3api get-bucket-versioning --bucket reillydesignstudio-assets

# Enable versioning (if not already)
aws s3api put-bucket-versioning --bucket reillydesignstudio-assets \
  --versioning-configuration Status=Enabled

# Check bucket size & contents
aws s3 ls s3://reillydesignstudio-assets --recursive --summarize
```

**Status:** ✅ Bucket exists, ready for invoice storage

---

### **2. Set Up Invoice Storage System**
```bash
# Create folder structure for invoices
aws s3api put-object --bucket reillydesignstudio-assets \
  --key "invoices/" \
  --content-type "application/x-directory"

# Verify it exists
aws s3 ls s3://reillydesignstudio-assets/invoices/

# Test by uploading a sample file
echo "Sample Invoice" > /tmp/test-invoice.txt
aws s3 cp /tmp/test-invoice.txt s3://reillydesignstudio-assets/invoices/test.txt
```

**Benefit:** Automated invoice backup + archival system

---

### **3. Enable CloudFront for reillydesignstudio-assets**
```bash
# Create CloudFront distribution (CLI)
aws cloudfront create-distribution-with-tags \
  --distribution-config-with-tags file:///tmp/cf-config.json

# OR use AWS Console for easier setup:
# https://console.aws.amazon.com/cloudfront/v3/
# Select: reillydesignstudio-assets S3 bucket
# This will:
# - Speed up asset delivery globally
# - Reduce bandwidth costs
# - Enable caching headers
```

**Benefit:** Portfolio images load 10x faster worldwide

---

### **4. Audit & Secure IAM User**
```bash
# Check current IAM user permissions
aws iam get-user-policy --user-name reillydesignstudio-app \
  --policy-name [policy-name]

# List attached policies
aws iam list-attached-user-policies --user-name reillydesignstudio-app

# Generate access key for automation
aws iam create-access-key --user-name reillydesignstudio-app
# SAVE THIS! You'll need it for automation scripts
```

**Security:** Create separate access keys for each integration (Slack, Lambda, etc.)

---

### **5. Set Up Cost Budget & Alerts**
```bash
# Create monthly budget alert ($50 limit)
cat > /tmp/budget-config.json << 'EOF'
{
  "BudgetName": "reillydesignstudio-monthly",
  "BudgetLimit": {
    "Amount": "50",
    "Unit": "USD"
  },
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST",
  "NotificationsWithSubscribers": [{
    "Notification": {
      "NotificationType": "FORECASTED",
      "ComparisonOperator": "GREATER_THAN",
      "Threshold": 80,
      "ThresholdType": "PERCENTAGE"
    },
    "Subscribers": [{
      "SubscriptionType": "EMAIL",
      "Address": "robert@reillydesignstudio.com"
    }]
  }]
}
EOF

aws budgets create-budget --account-id 053677584823 \
  --budget file:///tmp/budget-config.json
```

**Benefit:** Never surprised by AWS bills

---

## 🔧 Integration with ReillyDesignStudio

### **Invoice Generation Pipeline**

**Current Flow:**
```
Payment received (Stripe)
    ↓
Invoice generated (invoice-generator skill)
    ↓
PDF saved (???)  ← PROBLEM: Where does it go?
    ↓
Email to client (email-management skill)
```

**Improved Flow:**
```
Payment received (Stripe webhook)
    ↓
Lambda function triggered
    ↓
Generate PDF invoice
    ↓
Upload to S3 (reillydesignstudio-assets/invoices/)
    ↓
SNS notification sent
    ↓
Email to client with S3 link
    ↓
Backup complete ✅
```

**Implementation:**
```bash
# Create Lambda execution role
aws iam create-role --role-name invoice-generator-lambda \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "lambda.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

# Attach S3 policy to role
aws iam attach-role-policy --role-name invoice-generator-lambda \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

# Now ready for Lambda function deployment
```

---

## 📊 AWS Cost Analysis

### **Current Spending (Estimate)**
```
S3 Storage (3 buckets):        ~$1.50/month
Amplify (builds + hosting):    ~$5.00/month
CloudFront (if enabled):       ~$0.50-2.00/month
───────────────────────────
TOTAL:                         ~$7-8/month
```

**Good news:** Very cost-effective for a production site!

---

## 🛠️ Useful Commands (Copy & Paste)

### **View Account Summary**
```bash
aws sts get-caller-identity
```

### **List All S3 Objects**
```bash
aws s3 ls s3://reillydesignstudio-assets --recursive
```

### **Upload Invoice PDF**
```bash
aws s3 cp invoice.pdf \
  s3://reillydesignstudio-assets/invoices/$(date +%Y-%m-%d-%H%M%S)-invoice.pdf
```

### **Download Invoice**
```bash
aws s3 cp s3://reillydesignstudio-assets/invoices/FILE.pdf ./downloaded.pdf
```

### **Get S3 URL (for sharing)**
```bash
# Public URL (if bucket is public)
echo "https://reillydesignstudio-assets.s3.amazonaws.com/invoices/FILE.pdf"

# Signed URL (temporary, 24 hours)
aws s3 presign s3://reillydesignstudio-assets/invoices/FILE.pdf \
  --expires-in 86400
```

### **Monitor Costs This Month**
```bash
aws ce get-cost-and-usage \
  --time-period Start=2026-03-01,End=2026-03-31 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE
```

### **Check S3 Bucket Size**
```bash
aws s3api get-bucket-location --bucket reillydesignstudio-assets
aws s3 ls s3://reillydesignstudio-assets --recursive --summarize
```

---

## 🔐 Security Checklist

- [ ] Enable MFA on AWS Console login
- [ ] Review IAM user permissions (reillydesignstudio-app)
- [ ] Rotate access keys every 90 days
- [ ] Enable CloudTrail for audit logs
- [ ] Set S3 bucket policies (who can access)
- [ ] Enable versioning on all buckets
- [ ] Test disaster recovery (restore from backup)

---

## 📈 Growth Roadmap

### **Phase 1: This Week**
- [x] Verify existing infrastructure
- [ ] Enable CloudFront for S3
- [ ] Set up cost alerts
- [ ] Test invoice storage

### **Phase 2: Next Week**
- [ ] Build Lambda for invoice automation
- [ ] Connect Stripe webhooks to Lambda
- [ ] Create SNS notifications
- [ ] Document deployment process

### **Phase 3: Month 2**
- [ ] Add CloudWatch monitoring
- [ ] Implement EventBridge workflows
- [ ] Create disaster recovery plan
- [ ] Add DynamoDB for analytics cache

### **Phase 4: Scale (Month 3+)**
- [ ] Implement multi-region deployment
- [ ] Add API Gateway for public endpoints
- [ ] Create CI/CD pipeline
- [ ] Full infrastructure-as-code setup

---

## 💡 Pro Tips

**Tip 1: Use AWS CLI Aliases**
```bash
# Add to ~/.zshrc or ~/.bashrc
alias aws-whoami='aws sts get-caller-identity'
alias aws-costs='aws ce get-cost-and-usage --time-period Start=2026-03-01,End=$(date +%Y-%m-%d) --granularity DAILY --metrics BlendedCost'
alias s3-list='aws s3 ls s3://reillydesignstudio-assets --recursive'
```

**Tip 2: CloudFormation Templates**
Save your infrastructure as code for easy replication:
```bash
aws cloudformation export-stack-template --stack-name my-stack > template.yaml
```

**Tip 3: Cost Optimization**
- Use S3 lifecycle policies (archive old invoices to Glacier)
- Enable S3 Intelligent Tiering (auto cost optimization)
- Use CloudFront caching headers
- Delete unused Amplify apps

---

## 📞 Next Steps

**Ready to implement?**

1. **Verify S3 bucket access** (test upload)
2. **Enable CloudFront** (global CDN)
3. **Set up cost alerts** (budget protection)
4. **Create Lambda for invoices** (automation)

**Want help with:**
- [ ] Terraform/CloudFormation templates?
- [ ] Lambda function code?
- [ ] Integration with Slack?
- [ ] Disaster recovery setup?

---

**Account ID:** 053677584823  
**Region:** us-east-1 (default)  
**Estimated Monthly Cost:** ~$7-10 (very affordable!)

🍑 Ready to dive into any of these AWS services?
