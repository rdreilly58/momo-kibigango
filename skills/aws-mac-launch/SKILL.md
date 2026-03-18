# aws-mac-launch — AWS Mac Instance for iOS Development

Launch a macOS EC2 instance on AWS for iOS development (Xcode, Swift, etc).

## Overview

Automates the full setup:
- Allocates (or uses existing) dedicated Mac host
- Queries latest macOS AMI
- Creates/reuses security group with SSH access
- Generates SSH key pair
- Launches instance with proper networking
- Outputs SSH connection details

## Usage

```bash
# Basic launch (uses defaults)
./scripts/launch-mac-instance.sh

# With custom instance name
INSTANCE_NAME="MyMacDev" ./scripts/launch-mac-instance.sh

# With specific host ID
DEDICATED_HOST_ID="host-0abc1def2ghi34567" ./scripts/launch-mac-instance.sh
```

## Prerequisites

- AWS CLI v2 configured with credentials
- `jq` for JSON parsing
- VPC and subnet in us-east-1 (auto-detected)
- Quota approved for `mac1.metal` (or similar)

## Configuration

Edit `scripts/launch-mac-instance.sh`:

```bash
REGION="us-east-1"
INSTANCE_TYPE="mac1.metal"
KEY_NAME="momotaro-mac"
INSTANCE_NAME="Momotaro-iOS-Dev"
```

## What Gets Created

| Resource | Details |
|----------|---------|
| Instance | macOS with Xcode pre-installed |
| Security Group | SSH access (port 22) from 0.0.0.0/0 |
| SSH Key Pair | Stored in `~/.ssh/momotaro-mac.pem` |
| Elastic IP | (Optional, enable in script) |

## Connection

After launch:
```bash
ssh -i ~/.ssh/momotaro-mac.pem ec2-user@<PUBLIC_IP>
```

## Cleanup

```bash
./scripts/terminate-instance.sh <INSTANCE_ID>
```

## Troubleshooting

| Error | Solution |
|-------|----------|
| `UnsupportedHostConfiguration` | Mac instance type not available in AZ, try different region |
| `No macOS AMI found` | Check AWS account has access to macOS AMIs |
| `Connection timeout` | Security group may need different CIDR range |

## References

- AWS Mac Instances: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-mac-instances.html
- macOS AMI: https://aws.amazon.com/marketplace/pp/prodview-wpp47khp4jkqq

## Status

✅ Customized for Reilly Design Studio
✅ Uses default VPC: vpc-0b90aef469eaa022e
✅ Subnet: us-east-1e (subnet-0fa346347ac41fd30)
✅ SSH Key: ~/.ssh/momotaro-mac.pem
