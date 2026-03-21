#!/bin/bash

# Cron-safe Mac instance allocator
# Runs every 5 minutes, ensures allocation happens when capacity available
# Safe to run multiple times (checks if already allocated)

LOGFILE="$HOME/.openclaw/logs/mac-allocator-cron.log"
CONFIG_FILE="$HOME/.openclaw/workspace/aws-config/mac-instance-allocated.json"
LOCK_FILE="/tmp/mac-allocator.lock"

# Ensure log directory exists
mkdir -p "$(dirname "$LOGFILE")"

# Check if already allocated
if [ -f "$CONFIG_FILE" ]; then
  STATUS=$(jq -r '.status' "$CONFIG_FILE" 2>/dev/null)
  if [ "$STATUS" = "ALLOCATED_AND_READY" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Instance already allocated. Exiting." >> "$LOGFILE"
    exit 0
  fi
fi

# Prevent concurrent runs
if [ -f "$LOCK_FILE" ]; then
  LOCK_TIME=$(stat -f %m "$LOCK_FILE" 2>/dev/null || echo 0)
  CURRENT_TIME=$(date +%s)
  LOCK_AGE=$((CURRENT_TIME - LOCK_TIME))
  
  # If lock is older than 5 minutes, allow new attempt
  if [ $LOCK_AGE -lt 300 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Allocation already in progress (lock age: ${LOCK_AGE}s). Exiting." >> "$LOGFILE"
    exit 0
  fi
fi

touch "$LOCK_FILE"

# Log attempt
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting allocation attempt..." >> "$LOGFILE"

# Try allocation
try_allocate() {
  local INSTANCE_TYPE=$1
  local REGION=$2
  
  AZS=$(aws ec2 describe-availability-zones \
    --region $REGION \
    --query 'AvailabilityZones[?State==`available`].ZoneName' \
    --output text 2>/dev/null | head -2)
  
  for AZ in $AZS; do
    RESULT=$(aws ec2 allocate-hosts \
      --instance-type $INSTANCE_TYPE \
      --availability-zone $AZ \
      --quantity 1 \
      --tag-specifications "ResourceType=dedicated-host,Tags=[{Key=Name,Value=momotaro-mac},{Key=Owner,Value=bob}]" \
      --region $REGION \
      --output json 2>&1)
    
    if echo "$RESULT" | jq -e '.HostIds[0]' > /dev/null 2>&1; then
      return 0
    fi
  done
  
  return 1
}

# Try m4pro first, then m4
for REGION in us-east-1 us-east-2 us-west-1 us-west-2; do
  for INSTANCE_TYPE in mac-m4pro.metal mac-m4.metal; do
    if try_allocate "$INSTANCE_TYPE" "$REGION"; then
      HOST_ID=$(echo "$RESULT" | jq -r '.HostIds[0]')
      AZ=$(echo "$RESULT" | jq -r '.HostIds[0]' | head -1)
      
      echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ SUCCESS! Allocated $INSTANCE_TYPE in $REGION" >> "$LOGFILE"
      
      cat > "$CONFIG_FILE" << EOF
{
  "host_id": "$HOST_ID",
  "instance_type": "$INSTANCE_TYPE",
  "region": "$REGION",
  "allocated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "status": "ALLOCATED_AND_READY"
}
EOF
      
      rm -f "$LOCK_FILE"
      exit 0
    fi
  done
done

echo "[$(date '+%Y-%m-%d %H:%M:%S')] No capacity found this cycle" >> "$LOGFILE"
rm -f "$LOCK_FILE"
exit 1
