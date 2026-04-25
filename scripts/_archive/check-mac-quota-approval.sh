#!/bin/bash

# Monitor mac-m4pro quota approval status
REQUEST_ID="f385e0e9ebe248b1bbbc70b36755d34bU68btWJY"
QUOTA_CODE="L-6919FC30"
REGION="us-east-1"

echo "🔍 Checking mac-m4pro quota approval status..."
echo ""

# Get request status
STATUS=$(aws service-quotas get-requested-service-quota-change \
  --request-id "$REQUEST_ID" \
  --region "$REGION" \
  --query 'RequestedQuota.Status' \
  --output text 2>/dev/null)

case "$STATUS" in
  "APPROVED")
    echo "✅ QUOTA APPROVED! mac-m4pro hosts now available"
    echo ""
    echo "Ready to allocate host:"
    echo "  aws ec2 allocate-hosts \\"
    echo "    --instance-type mac-m4pro.metal \\"
    echo "    --availability-zone us-east-1a \\"
    echo "    --quantity 1 \\"
    echo "    --region $REGION"
    exit 0
    ;;
  "PENDING")
    echo "⏳ PENDING: Waiting for AWS approval (typically 24 hours)"
    ;;
  "DENIED")
    echo "❌ DENIED: Request was rejected. You can resubmit or contact AWS Support"
    ;;
  *)
    echo "ℹ️  Status: $STATUS"
    ;;
esac

# Check current quota limit
QUOTA=$(aws service-quotas get-service-quota \
  --service-code ec2 \
  --quota-code "$QUOTA_CODE" \
  --region "$REGION" \
  --query 'Quota.Value' \
  --output text 2>/dev/null)

echo "   Current quota limit: $QUOTA hosts"
