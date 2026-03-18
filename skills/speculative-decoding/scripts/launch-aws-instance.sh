#!/bin/bash

# Launch AWS p3.2xlarge GPU instance for vLLM speculative decoding
# Prerequisites:
#   - AWS CLI configured (aws configure)
#   - EC2 key pair created (--key-name parameter)
#   - VPC security group allows SSH + HTTP (ports 22, 8000)

set -e

# Configuration
INSTANCE_TYPE="p3.2xlarge"           # NVIDIA V100 GPU (16GB), 8 vCPU
AMI_ID="ami-04680790a315cd58d"      # Ubuntu 22.04 LTS (us-east-1, latest)
REGION="us-east-1"
AVAILABILITY_ZONE="us-east-1a"
VOLUME_SIZE=100                      # GB (for models)
KEY_NAME="${1:-}"
INSTANCE_NAME="vlm-speculative-decoding"

echo "=========================================="
echo "🚀 Launching AWS GPU Instance"
echo "=========================================="
echo ""
echo "Configuration:"
echo "  Instance type: $INSTANCE_TYPE"
echo "  Region: $REGION"
echo "  Availability Zone: $AVAILABILITY_ZONE"
echo "  Storage: ${VOLUME_SIZE}GB"
echo "  Name: $INSTANCE_NAME"
echo ""

# Check if key name provided
if [ -z "$KEY_NAME" ]; then
  echo "❌ Error: Key pair name required"
  echo ""
  echo "Usage: ./launch-aws-instance.sh YOUR_KEY_PAIR_NAME"
  echo ""
  echo "To create a key pair:"
  echo "  aws ec2 create-key-pair --key-name my-key-pair --region $REGION --query 'KeyMaterial' --output text > my-key-pair.pem"
  echo "  chmod 400 my-key-pair.pem"
  exit 1
fi

# Verify key pair exists
echo "Checking key pair '$KEY_NAME'..."
if ! aws ec2 describe-key-pairs --key-names "$KEY_NAME" --region "$REGION" > /dev/null 2>&1; then
  echo "❌ Error: Key pair '$KEY_NAME' not found in region $REGION"
  exit 1
fi

echo "✅ Key pair found"
echo ""

# Create security group (if needed)
echo "Setting up security group..."
SG_NAME="vlm-speculative-sg"

# Check if SG exists
if ! aws ec2 describe-security-groups --filters "Name=group-name,Values=$SG_NAME" --region "$REGION" > /dev/null 2>&1; then
  echo "Creating security group..."
  SG_ID=$(aws ec2 create-security-group \
    --group-name "$SG_NAME" \
    --description "Security group for vLLM speculative decoding" \
    --region "$REGION" \
    --query 'GroupId' \
    --output text)
  
  echo "✅ Security group created: $SG_ID"
  
  # Allow SSH
  aws ec2 authorize-security-group-ingress \
    --group-id "$SG_ID" \
    --protocol tcp \
    --port 22 \
    --cidr 0.0.0.0/0 \
    --region "$REGION"
  
  # Allow vLLM API
  aws ec2 authorize-security-group-ingress \
    --group-id "$SG_ID" \
    --protocol tcp \
    --port 8000 \
    --cidr 0.0.0.0/0 \
    --region "$REGION"
else
  SG_ID=$(aws ec2 describe-security-groups \
    --filters "Name=group-name,Values=$SG_NAME" \
    --region "$REGION" \
    --query 'SecurityGroups[0].GroupId' \
    --output text)
  echo "✅ Using existing security group: $SG_ID"
fi

echo ""
echo "Launching instance..."
echo "This will take 2-3 minutes..."
echo ""

# Launch instance
INSTANCE_ID=$(aws ec2 run-instances \
  --image-id "$AMI_ID" \
  --instance-type "$INSTANCE_TYPE" \
  --key-name "$KEY_NAME" \
  --security-group-ids "$SG_ID" \
  --block-device-mappings "DeviceName=/dev/sda1,Ebs={VolumeSize=$VOLUME_SIZE,VolumeType=gp3}" \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$INSTANCE_NAME}]" \
  --region "$REGION" \
  --query 'Instances[0].InstanceId' \
  --output text)

echo "✅ Instance launched: $INSTANCE_ID"
echo ""
echo "Waiting for instance to start..."

# Wait for instance to be running
aws ec2 wait instance-running \
  --instance-ids "$INSTANCE_ID" \
  --region "$REGION"

echo "✅ Instance is running"
echo ""

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
  --instance-ids "$INSTANCE_ID" \
  --region "$REGION" \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text)

echo "=========================================="
echo "✅ Instance Ready!"
echo "=========================================="
echo ""
echo "Instance Details:"
echo "  ID: $INSTANCE_ID"
echo "  Type: $INSTANCE_TYPE"
echo "  IP: $PUBLIC_IP"
echo "  Region: $REGION"
echo ""
echo "Next steps:"
echo ""
echo "1. SSH into instance:"
echo "   ssh -i /path/to/$KEY_NAME.pem ubuntu@$PUBLIC_IP"
echo ""
echo "2. Once connected, clone the skill:"
echo "   git clone <repo-url>"
echo "   cd openclaw/workspace/skills/speculative-decoding"
echo ""
echo "3. Install dependencies:"
echo "   ./scripts/install-dependencies.sh"
echo ""
echo "4. Start vLLM server:"
echo "   ./scripts/start-vlm-server.sh"
echo ""
echo "5. Test from your local machine:"
echo "   curl http://$PUBLIC_IP:8000/health"
echo ""
echo "Cost estimate:"
echo "  - p3.2xlarge: \$3.06/hour"
echo "  - 1 hour testing: ~\$3"
echo "  - 8 hours: ~\$24"
echo ""
echo "To terminate (stop paying):"
echo "  aws ec2 terminate-instances --instance-ids $INSTANCE_ID --region $REGION"
echo ""
