# AWS Mac Instance Setup - Next Steps

## Status
✅ Quota approved for mac-m4max (Apple Silicon M3 Max equivalent)
✅ AWS Mac Launch Skill created and ready
⏳ Manual steps required for final launch

## Issue Discovered
macOS AMIs are not readily available via AWS CLI in the region/account. AWS provides pre-configured macOS instances through the Console or Marketplace.

## Solution: Manual Launch via AWS Console

1. **Log in to AWS Console:**
   - https://console.aws.amazon.com/ec2/

2. **Launch Instance:**
   - Click "Launch Instances"
   - Search for "macOS Ventura" or "macOS Sonoma"
   - Select the latest available AMI (Apple Silicon/ARM64)
   - Choose instance type: **mac-m4max.metal**
   - Network settings:
     - VPC: vpc-0b90aef469eaa022e
     - Subnet: subnet-0fa346347ac41fd30 (us-east-1e)
   - Security group: mac-os-dev-sg (already created)
   - Key pair: momotaro-mac (already created)
   - Storage: 300GB (default is fine)
   - Tags: Name=Momotaro-iOS-Dev

3. **Launch & Connect:**
   - Wait 15-20 minutes for instance to fully initialize
   - Copy the Public IP from the console
   - SSH: `ssh -i ~/.ssh/momotaro-mac.pem ec2-user@<PUBLIC_IP>`

4. **Post-Launch Setup:**
   ```bash
   # Update system
   sudo softwareupdate -a -i -R
   
   # Install Xcode Command Line Tools
   xcode-select --install
   
   # Install Homebrew (optional)
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

## Resources Created

| Resource | Details |
|----------|---------|
| **SSH Key** | ~/.ssh/momotaro-mac.pem (already created) |
| **Security Group** | sg-0e75cb20af284e813 (SSH access enabled) |
| **VPC** | vpc-0b90aef469eaa022e (default) |
| **Subnet** | subnet-0fa346347ac41fd30 (us-east-1e) |
| **Launch Script** | ~/.openclaw/workspace/skills/aws-mac-launch/ |

## Alternative: AWS CLI Direct Launch (Once AMI is available)

Once AWS provides public macOS AMIs, the skill script can be updated:

```bash
AWS_REGION=us-east-1 \
DEDICATED_HOST_ID="<your-host-id>" \
~/.openclaw/workspace/skills/aws-mac-launch/scripts/launch-mac-instance.sh
```

## Troubleshooting

**Q: Instance is stuck on "Initializing"?**
A: Mac instances take 15-20 minutes to fully boot. This is normal.

**Q: Can't SSH in?**
A: Check:
- Public IP is assigned (may need Elastic IP)
- Security group allows SSH (port 22)
- Key file permissions: `chmod 400 ~/.ssh/momotaro-mac.pem`

**Q: Xcode installation taking too long?**
A: Yes, it's large (~15GB). This is normal.

## Next Steps

1. Launch the instance via AWS Console (see "Solution" above)
2. SSH in once it's running
3. Install Xcode and dev tools
4. Test iOS build environment

Bob, do you want me to help with anything else while you launch via console? 🍑
