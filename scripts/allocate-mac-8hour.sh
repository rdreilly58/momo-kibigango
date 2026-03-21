#!/bin/bash

# 8-hour Mac instance allocation - comprehensive US-wide search
INSTANCE_TYPES=("mac-m4pro.metal" "mac-m4.metal")
MAX_RUNTIME_HOURS=8
MAX_RUNTIME_SECONDS=$((MAX_RUNTIME_HOURS * 3600))
RETRY_INTERVAL=120  # 2 minutes between full region scans
START_TIME=$(date +%s)
LOGFILE="$HOME/.openclaw/logs/mac-allocation-8hour.log"

# Ensure log directory exists
mkdir -p "$(dirname "$LOGFILE")"

echo "🚀 Starting 8-hour Mac instance allocation search" | tee -a "$LOGFILE"
echo "   Start time: $(date)" | tee -a "$LOGFILE"
echo "   Will try all US regions and AZs" | tee -a "$LOGFILE"
echo "   Instance types: m4pro.metal (48GB) → m4.metal (24GB)" | tee -a "$LOGFILE"
echo "" | tee -a "$LOGFILE"

# Function to try allocation
try_allocate() {
  local INSTANCE_TYPE=$1
  local AZ=$2
  local REGION=$3
  
  RESULT=$(aws ec2 allocate-hosts \
    --instance-type $INSTANCE_TYPE \
    --availability-zone $AZ \
    --quantity 1 \
    --tag-specifications "ResourceType=dedicated-host,Tags=[{Key=Name,Value=momotaro-mac},{Key=Owner,Value=bob},{Key=Type,Value=${INSTANCE_TYPE%.metal}}]" \
    --region $REGION \
    --output json 2>&1)
  
  if echo "$RESULT" | jq -e '.HostIds[0]' > /dev/null 2>&1; then
    return 0
  fi
  return 1
}

# Function to get instance specs
get_specs() {
  local INSTANCE_TYPE=$1
  if [ "$INSTANCE_TYPE" = "mac-m4pro.metal" ]; then
    echo "48GB RAM, 14-core CPU, \$1.97/hr"
  else
    echo "24GB RAM, 10-core CPU, \$1.23/hr"
  fi
}

# Main allocation loop
ATTEMPT=0
while true; do
  CURRENT_TIME=$(date +%s)
  ELAPSED=$((CURRENT_TIME - START_TIME))
  ELAPSED_MIN=$((ELAPSED / 60))
  REMAINING=$((MAX_RUNTIME_SECONDS - ELAPSED))
  REMAINING_MIN=$((REMAINING / 60))
  
  if [ $REMAINING -le 0 ]; then
    echo "" | tee -a "$LOGFILE"
    echo "❌ 8-hour timeout reached at $(date)" | tee -a "$LOGFILE"
    echo "Could not allocate Mac instance. All US regions remain at capacity." | tee -a "$LOGFILE"
    exit 1
  fi
  
  ATTEMPT=$((ATTEMPT + 1))
  echo "🔄 Attempt $ATTEMPT | Elapsed: ${ELAPSED_MIN}min | Remaining: ${REMAINING_MIN}min | $(date '+%H:%M:%S')" | tee -a "$LOGFILE"
  
  # Get all US regions
  US_REGIONS=("us-east-1" "us-east-2" "us-west-1" "us-west-2")
  
  for REGION in "${US_REGIONS[@]}"; do
    # Get all AZs in this region
    AZS=$(aws ec2 describe-availability-zones \
      --region $REGION \
      --query 'AvailabilityZones[?State==`available`].ZoneName' \
      --output text 2>/dev/null)
    
    if [ -z "$AZS" ]; then
      echo "  ⚠️  $REGION: No AZs available" | tee -a "$LOGFILE"
      continue
    fi
    
    for AZ in $AZS; do
      for INSTANCE_TYPE in "${INSTANCE_TYPES[@]}"; do
        if try_allocate "$INSTANCE_TYPE" "$AZ" "$REGION"; then
          HOST_ID=$(echo "$RESULT" | jq -r '.HostIds[0]')
          SPECS=$(get_specs "$INSTANCE_TYPE")
          
          echo "" | tee -a "$LOGFILE"
          echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOGFILE"
          echo "🎉 MAC INSTANCE ALLOCATED!" | tee -a "$LOGFILE"
          echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" | tee -a "$LOGFILE"
          echo "" | tee -a "$LOGFILE"
          echo "Instance Type:  $INSTANCE_TYPE" | tee -a "$LOGFILE"
          echo "Specs:          $SPECS" | tee -a "$LOGFILE"
          echo "Host ID:        $HOST_ID" | tee -a "$LOGFILE"
          echo "Location:       $AZ ($REGION)" | tee -a "$LOGFILE"
          echo "Allocated at:   $(date)" | tee -a "$LOGFILE"
          echo "Time to allocate: ${ELAPSED_MIN} minutes" | tee -a "$LOGFILE"
          echo "" | tee -a "$LOGFILE"
          
          # Save config
          cat > ~/.openclaw/workspace/aws-config/mac-instance-allocated.json << EOF
{
  "host_id": "$HOST_ID",
  "instance_type": "$INSTANCE_TYPE",
  "availability_zone": "$AZ",
  "region": "$REGION",
  "specs": {
    "cpu_cores": "$(echo $SPECS | cut -d, -f2)",
    "memory": "$(echo $SPECS | cut -d, -f1)",
    "pricing": "$(echo $SPECS | cut -d, -f3)"
  },
  "allocated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "time_to_allocate_minutes": $ELAPSED_MIN,
  "status": "ALLOCATED_AND_READY"
}
EOF
          
          # Send notification
          echo "📧 Sending notification..." | tee -a "$LOGFILE"
          
          exit 0
        fi
      done
    done
  done
  
  # Wait before next attempt
  if [ $REMAINING -gt $RETRY_INTERVAL ]; then
    echo "  ⏳ Retrying in ${RETRY_INTERVAL}s..." | tee -a "$LOGFILE"
    sleep $RETRY_INTERVAL
  else
    echo "  ⏳ Final check before timeout..." | tee -a "$LOGFILE"
    sleep 30
  fi
done

