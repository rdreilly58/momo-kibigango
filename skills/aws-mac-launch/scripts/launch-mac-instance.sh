#!/bin/bash

#######################################
# AWS Mac Instance Launcher
# For iOS Development on Reilly Design Studio
#######################################

set -e

# Configuration
REGION="us-east-1"
INSTANCE_TYPE="mac1.metal"  # Intel Mac (currently supported, M4 coming soon)
KEY_NAME="${KEY_NAME:-momotaro-mac}"
INSTANCE_NAME="${INSTANCE_NAME:-Momotaro-iOS-Dev}"
SECURITY_GROUP_NAME="mac-os-dev-sg"
VPC_ID="vpc-0b90aef469eaa022e"
SUBNET_ID="subnet-0fa346347ac41fd30"
DEDICATED_HOST_ID="${DEDICATED_HOST_ID:-}"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== AWS Mac Instance Launcher ===${NC}"
echo "Region: $REGION"
echo "Instance Type: $INSTANCE_TYPE"
echo "Instance Name: $INSTANCE_NAME"
echo ""

# Step 1: Query available macOS AMIs
echo -e "${YELLOW}Step 1: Querying macOS AMIs...${NC}"
# Use the latest AWS-managed macOS Sonoma x86_64 AMI (intel mac1.metal)
AMI_ID=$(aws ec2 describe-images \
  --region $REGION \
  --owners 628277914472 \
  --filters "Name=name,Values=amzn-ec2-macos-1*" "Name=state,Values=available" \
  --query 'sort_by(Images, &CreationDate)[-1].ImageId' \
  --output text)

if [ -z "$AMI_ID" ] || [ "$AMI_ID" = "None" ]; then
  # Fallback to specific known good AMI (macOS Intel)
  AMI_ID="ami-003b683d4b1ab633b"  # amzn-ec2-macos-14.8.1
fi

if [ -z "$AMI_ID" ]; then
  echo -e "${RED}✗ Failed to find a macOS AMI${NC}"
  exit 1
fi

echo -e "${GREEN}✓ Using AMI: $AMI_ID${NC}"

# Step 2: Create/Reuse Security Group
echo -e "${YELLOW}Step 2: Setting up Security Group...${NC}"
SG_ID=$(aws ec2 describe-security-groups \
  --region $REGION \
  --filters "Name=group-name,Values=$SECURITY_GROUP_NAME" "Name=vpc-id,Values=$VPC_ID" \
  --query 'SecurityGroups[0].GroupId' \
  --output text 2>/dev/null || echo "")

if [ "$SG_ID" = "None" ] || [ -z "$SG_ID" ]; then
  echo "Creating new security group..."
  SG_ID=$(aws ec2 create-security-group \
    --region $REGION \
    --group-name $SECURITY_GROUP_NAME \
    --description "Security group for macOS development instances" \
    --vpc-id $VPC_ID \
    --query 'GroupId' \
    --output text)
  
  # Add SSH access
  aws ec2 authorize-security-group-ingress \
    --region $REGION \
    --group-id $SG_ID \
    --protocol tcp \
    --port 22 \
    --cidr 0.0.0.0/0 \
    > /dev/null
  
  echo -e "${GREEN}✓ Created security group: $SG_ID${NC}"
else
  echo -e "${GREEN}✓ Using existing security group: $SG_ID${NC}"
fi

# Step 3: Generate SSH Key Pair if needed
echo -e "${YELLOW}Step 3: Setting up SSH key...${NC}"
KEY_PATH="$HOME/.ssh/${KEY_NAME}.pem"

if [ ! -f "$KEY_PATH" ]; then
  echo "Generating new SSH key pair..."
  aws ec2 create-key-pair \
    --region $REGION \
    --key-name $KEY_NAME \
    --query 'KeyMaterial' \
    --output text > "$KEY_PATH"
  chmod 400 "$KEY_PATH"
  echo -e "${GREEN}✓ Created SSH key: $KEY_PATH${NC}"
else
  echo -e "${GREEN}✓ Using existing SSH key: $KEY_PATH${NC}"
fi

# Step 4: Launch the macOS Instance
echo -e "${YELLOW}Step 4: Launching macOS instance...${NC}"

# Build launch command
# Note: Mac instances may require dedicated host for m4 types, but mac1.metal can use default
LAUNCH_CMD="aws ec2 run-instances \
  --region $REGION \
  --image-id $AMI_ID \
  --count 1 \
  --instance-type $INSTANCE_TYPE \
  --key-name $KEY_NAME \
  --security-group-ids $SG_ID \
  --subnet-id $SUBNET_ID \
  --tag-specifications ResourceType=instance,Tags=[{Key=Name,Value=$INSTANCE_NAME}] \
  --query 'Instances[0].InstanceId' \
  --output text"

# Only add dedicated host placement if explicitly provided
if [ ! -z "$DEDICATED_HOST_ID" ]; then
  LAUNCH_CMD="$LAUNCH_CMD --placement HostId=$DEDICATED_HOST_ID"
fi

INSTANCE_ID=$($LAUNCH_CMD)

if [ -z "$INSTANCE_ID" ]; then
  echo -e "${RED}✗ Failed to launch instance${NC}"
  exit 1
fi

echo -e "${GREEN}✓ Launched instance: $INSTANCE_ID${NC}"

# Step 5: Wait for instance to be running
echo -e "${YELLOW}Step 5: Waiting for instance to start (this may take 5-10 minutes)...${NC}"
aws ec2 wait instance-running \
  --region $REGION \
  --instance-ids $INSTANCE_ID

echo -e "${GREEN}✓ Instance is running${NC}"

# Step 6: Get connection details
echo -e "${YELLOW}Step 6: Retrieving connection details...${NC}"
INSTANCE_INFO=$(aws ec2 describe-instances \
  --region $REGION \
  --instance-ids $INSTANCE_ID \
  --query 'Reservations[0].Instances[0]' \
  --output json)

PUBLIC_IP=$(echo "$INSTANCE_INFO" | jq -r '.PublicIpAddress // "PENDING"')
PRIVATE_IP=$(echo "$INSTANCE_INFO" | jq -r '.PrivateIpAddress')

# Output summary
echo ""
echo -e "${GREEN}=== Instance Launched Successfully ===${NC}"
echo ""
echo "Instance ID:     $INSTANCE_ID"
echo "Instance Name:   $INSTANCE_NAME"
echo "Instance Type:   $INSTANCE_TYPE"
echo "Region:          $REGION"
echo "Private IP:      $PRIVATE_IP"
echo "Public IP:       $PUBLIC_IP"
echo ""
echo -e "${BLUE}Connection Command:${NC}"
if [ "$PUBLIC_IP" != "PENDING" ]; then
  echo "ssh -i $KEY_PATH ec2-user@$PUBLIC_IP"
else
  echo "Waiting for public IP assignment..."
  echo "ssh -i $KEY_PATH ec2-user@<public-ip>"
fi
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Wait for instance to fully initialize (5-10 minutes)"
echo "2. SSH into the instance and run: xcode-select --install"
echo "3. Set up development environment"
echo ""
echo "To terminate this instance later, run:"
echo "aws ec2 terminate-instances --region $REGION --instance-ids $INSTANCE_ID"
echo ""

# Save instance details
CONFIG_DIR="$HOME/.openclaw/workspace/config"
mkdir -p "$CONFIG_DIR"
cat > "$CONFIG_DIR/mac-instance.json" <<EOF
{
  "instance_id": "$INSTANCE_ID",
  "instance_name": "$INSTANCE_NAME",
  "instance_type": "$INSTANCE_TYPE",
  "region": "$REGION",
  "public_ip": "$PUBLIC_IP",
  "private_ip": "$PRIVATE_IP",
  "key_path": "$KEY_PATH",
  "security_group": "$SG_ID",
  "subnet_id": "$SUBNET_ID",
  "vpc_id": "$VPC_ID",
  "launch_time": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

echo -e "${GREEN}✓ Instance details saved to: $CONFIG_DIR/mac-instance.json${NC}"
