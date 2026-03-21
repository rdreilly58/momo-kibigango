#!/bin/bash

# Allocate Mac instance - tries both m4pro and m4 variants
INSTANCE_TYPES=("mac-m4pro.metal" "mac-m4.metal")
REGIONS=("us-east-1" "us-west-2")
MAX_RETRIES=5
RETRY_INTERVAL=30

echo "🚀 Starting flexible Mac instance allocation..."
echo "   Will try: m4pro.metal (48GB) → m4.metal (24GB)"
echo ""

for ATTEMPT in $(seq 1 $MAX_RETRIES); do
  echo "🔄 Attempt $ATTEMPT of $MAX_RETRIES ($(date '+%H:%M:%S'))"
  
  for INSTANCE_TYPE in "${INSTANCE_TYPES[@]}"; do
    for REGION in "${REGIONS[@]}"; do
      # Get available AZs
      AZS=$(aws ec2 describe-availability-zones \
        --region $REGION \
        --query 'AvailabilityZones[?State==`available`].ZoneName' \
        --output text 2>/dev/null)
      
      for AZ in $AZS; do
        echo -n "  $REGION/$AZ ($INSTANCE_TYPE)... "
        
        RESULT=$(aws ec2 allocate-hosts \
          --instance-type $INSTANCE_TYPE \
          --availability-zone $AZ \
          --quantity 1 \
          --tag-specifications "ResourceType=dedicated-host,Tags=[{Key=Name,Value=momotaro-mac},{Key=Owner,Value=bob},{Key=Type,Value=${INSTANCE_TYPE%.metal}}]" \
          --region $REGION \
          --output json 2>&1)
        
        if echo "$RESULT" | jq -e '.HostIds[0]' > /dev/null 2>&1; then
          HOST_ID=$(echo "$RESULT" | jq -r '.HostIds[0]')
          
          # Get pricing for this type
          if [ "$INSTANCE_TYPE" = "mac-m4pro.metal" ]; then
            PRICE="$1.97/hr"
            MEMORY="48GB"
            CORES="14-core"
          else
            PRICE="$1.23/hr"
            MEMORY="24GB"
            CORES="10-core"
          fi
          
          echo "✅ SUCCESS!"
          echo ""
          echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
          echo "🎉 MAC INSTANCE ALLOCATED!"
          echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
          echo ""
          echo "Instance Type:  $INSTANCE_TYPE"
          echo "Specs:          $CORES CPU, $MEMORY RAM"
          echo "Pricing:        $PRICE"
          echo "Host ID:        $HOST_ID"
          echo "Location:       $AZ ($REGION)"
          echo "Allocated:      $(date)"
          echo ""
          
          # Save details
          cat > ~/.openclaw/workspace/aws-config/mac-instance-allocated.json << EOF
{
  "host_id": "$HOST_ID",
  "instance_type": "$INSTANCE_TYPE",
  "availability_zone": "$AZ",
  "region": "$REGION",
  "specs": {
    "cpu_cores": "$CORES",
    "memory": "$MEMORY",
    "pricing": "$PRICE"
  },
  "allocated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "status": "ALLOCATED_AND_READY"
}
EOF
          
          exit 0
        fi
      done
    done
  done
  
  if [ $ATTEMPT -lt $MAX_RETRIES ]; then
    echo ""
    echo "⏳ No capacity found. Retrying in ${RETRY_INTERVAL}s..."
    sleep $RETRY_INTERVAL
  fi
done

echo ""
echo "❌ Could not allocate after $MAX_RETRIES attempts"
echo "All US regions at capacity. Consider:"
echo "  • Try again in 5-10 minutes (capacity fluctuates)"
echo "  • Check EU regions (eu-west-1, eu-central-1)"
exit 1
