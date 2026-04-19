#!/bin/bash

# Automated Mac instance allocation with retry logic
INSTANCE_TYPE="mac-m4pro.metal"
REGIONS=("us-east-1" "us-west-2")
MAX_RETRIES=5
RETRY_INTERVAL=60

for ATTEMPT in $(seq 1 $MAX_RETRIES); do
  echo "🔄 Attempt $ATTEMPT of $MAX_RETRIES ($(date '+%H:%M:%S'))"
  
  for REGION in "${REGIONS[@]}"; do
    # Get available AZs
    AZS=$(aws ec2 describe-availability-zones \
      --region $REGION \
      --query 'AvailabilityZones[?State==`available`].ZoneName' \
      --output text)
    
    for AZ in $AZS; do
      echo -n "  Trying $AZ... "
      
      RESULT=$(aws ec2 allocate-hosts \
        --instance-type $INSTANCE_TYPE \
        --availability-zone $AZ \
        --quantity 1 \
        --tag-specifications "ResourceType=dedicated-host,Tags=[{Key=Name,Value=momotaro-m4pro},{Key=Owner,Value=bob}]" \
        --region $REGION \
        --output json 2>&1)
      
      if echo "$RESULT" | jq -e '.HostIds[0]' > /dev/null 2>&1; then
        HOST_ID=$(echo "$RESULT" | jq -r '.HostIds[0]')
        echo "✅ SUCCESS!"
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "🎉 M4 PRO MAC INSTANCE ALLOCATED!"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "Host ID:    $HOST_ID"
        echo "AZ:         $AZ"
        echo "Type:       $INSTANCE_TYPE"
        echo "Region:     $REGION"
        echo ""
        
        # Save details
        cat > ~/.openclaw/workspace/aws-config/mac-instance-allocated.json << EOF
{
  "host_id": "$HOST_ID",
  "availability_zone": "$AZ",
  "region": "$REGION",
  "instance_type": "$INSTANCE_TYPE",
  "allocated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "status": "ALLOCATED"
}
EOF
        
        exit 0
      fi
    done
  done
  
  if [ $ATTEMPT -lt $MAX_RETRIES ]; then
    echo ""
    echo "⏳ No capacity available. Retrying in ${RETRY_INTERVAL}s..."
    echo ""
    sleep $RETRY_INTERVAL
  fi
done

echo ""
echo "❌ Failed to allocate after $MAX_RETRIES attempts"
exit 1
