#!/bin/bash
# Monitor AWS Mac instance quota request status
# Run via cron to check periodically

REQUEST_ID="f385e0e9ebe248b1bbbc70b36755d34bU68btWJY"
CONFIG_FILE="$HOME/.openclaw/workspace/aws-config/mac-m4pro-quota-request.json"
LOG_FILE="$HOME/.openclaw/logs/mac-quota-monitor.log"

# Ensure log directory exists
mkdir -p "$HOME/.openclaw/logs"

# Check quota status via AWS CLI
echo "[$(date)] Checking Mac instance quota status..." >> "$LOG_FILE"

aws service-quotas get-service-quota \
  --service-code "ec2" \
  --quota-code "L-6919FC30" \
  --region us-east-1 > /tmp/quota_status.json 2>&1

if [ $? -eq 0 ]; then
  STATUS=$(jq -r '.Quota.QuotaAppliedAtLevel' /tmp/quota_status.json)
  VALUE=$(jq -r '.Quota.Value' /tmp/quota_status.json)
  
  echo "[$(date)] Quota Status: Value=$VALUE" >> "$LOG_FILE"
  
  # If value is now 1, approval is complete
  if [ "$VALUE" == "1" ]; then
    echo "[$(date)] ✅ MAC INSTANCE QUOTA APPROVED!" >> "$LOG_FILE"
    echo "Mac instance quota has been approved. Ready to launch mac-m4pro.metal instance." | \
      curl -X POST https://api.telegram.org/botYOUR_TOKEN/sendMessage \
      -d "chat_id=YOUR_CHAT_ID&text=Mac+quota+approved"
  else
    echo "[$(date)] ⏳ Still pending (value=$VALUE)" >> "$LOG_FILE"
  fi
else
  echo "[$(date)] ❌ Error checking quota status" >> "$LOG_FILE"
  cat /tmp/quota_status.json >> "$LOG_FILE"
fi

rm -f /tmp/quota_status.json
