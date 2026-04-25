# OpenClaw Multi-Host Failover

**Last updated:** 2026-04-25
**Status:** Single live host (M4 Max Mac mini). AWS Mac dedicated host allocation in progress.

---

## Host Inventory

| Handle | Machine | Status | Notes |
|--------|---------|--------|-------|
| `local` | M4 Max Mac mini (on-prem) | LIVE — primary | Only live host today |
| `mac-aws` | AWS dedicated Mac (momotaro-mac) | PENDING | Allocator running 3x daily |

EC2 Linux (54.81.20.218) was permanently decommissioned 2026-04-22. Do not reference it.

---

## What OpenClaw Automates

### 1. Dedicated-host allocation (`scripts/mac-allocator-cron.sh`)
- Runs Thu 8am / 2pm / 8pm via crontab.
- Calls `aws ec2 allocate-hosts` across all four US regions.
- Tries `mac-m4pro.metal` first, falls back to `mac-m4.metal`.
- On success: writes `aws-config/mac-instance-allocated.json` with `status=ALLOCATED_AND_READY`.
- Log: `~/.openclaw/logs/mac-allocator-cron.log`

### 2. Host health gating (`scripts/host-router.sh`)
- Reads `~/.openclaw/logs/health-check.log` (written every 2h by `system-health-check.sh`).
- Reads `aws-config/mac-instance-allocated.json` to know if AWS Mac is live.
- If selected host is unhealthy, falls through to next candidate.
- Outputs `local` | `mac-aws` | `skip`.

### 3. Task → host mapping (`scripts/agent-router.sh --host`)
- GPU/ML/iOS tasks prefer `mac-aws` when available; fall back to `local`.
- Ops/code/general tasks prefer `local`; use `mac-aws` as secondary.

---

## What Requires Manual AWS Console Action

The dedicated-host allocation via `aws ec2 allocate-hosts` is fully automated. However, **launching a macOS EC2 instance on the allocated host requires a manual console step** because:

> AWS macOS AMIs are not published to the public SSM parameter store and cannot be reliably queried with `aws ec2 describe-images` from a third-party account. The instance must be launched from the EC2 Console using the Marketplace macOS AMI picker.

### Precise Console Steps (once `mac-allocator-cron.sh` succeeds)

1. Verify allocation succeeded:
   ```bash
   cat ~/.openclaw/workspace/aws-config/mac-instance-allocated.json
   # Check: "status": "ALLOCATED_AND_READY"
   ```

2. Log in to AWS Console → EC2 → https://console.aws.amazon.com/ec2/

3. Click **Launch Instances**.

4. **Name:** `momotaro-mac`

5. **AMI:** Search "macOS Sonoma" → select the latest ARM64/Apple Silicon AMI.

6. **Instance type:** `mac-m4pro.metal` or `mac-m4.metal` (match what was allocated).

7. **Key pair:** `momotaro-mac` (already exists in `~/.ssh/momotaro-mac.pem`)

8. **Network settings:**
   - VPC: `vpc-0b90aef469eaa022e`
   - Subnet: `subnet-0fa346347ac41fd30` (us-east-1e)
   - Security group: `mac-os-dev-sg` (sg-0e75cb20af284e813)

9. **Placement:** Set **Host** to the dedicated host just allocated (filter by tag `Name=momotaro-mac`).

10. **Storage:** 300 GB.

11. **Tags:** `Name=momotaro-mac`, `Owner=bob`

12. Click **Launch Instance**. Wait 15–20 min for full boot.

13. **After launch:** Copy the instance's Public IP, then update the config:
    ```bash
    # Replace <PUBLIC_IP> with the actual IP from the console
    jq --arg ip "<PUBLIC_IP>" '.host_ip = $ip' \
      ~/.openclaw/workspace/aws-config/mac-instance-allocated.json \
      > /tmp/mac-cfg.json && mv /tmp/mac-cfg.json \
      ~/.openclaw/workspace/aws-config/mac-instance-allocated.json
    ```
    Once `host_ip` is set, `host-router.sh` will probe SSH port 22 and mark the host UP.

14. Verify routing:
    ```bash
    bash ~/.openclaw/workspace/scripts/host-router.sh general status
    bash ~/.openclaw/workspace/scripts/agent-router.sh --host --explain "train ML model"
    ```

---

## Failover Behaviour

```
Task arrives
    │
    ▼
host-router.sh resolves candidate list by task type
    │   gpu/ios/ml  → [mac-aws, local]
    │   ops/general → [local, mac-aws]
    │
    ▼
Try first candidate — is it healthy?
    ├── YES → route to it
    └── NO  → try next candidate
                ├── YES → route to it
                └── NO  → output "skip" (exit 1)
                          caller should queue or abort
```

**"Healthy" definition:**
- `local`: health-check.log does not show ERROR for Disk Space or Memory Files in last 50 lines.
- `mac-aws`: `mac-instance-allocated.json` has `status=ALLOCATED_AND_READY` AND SSH to `host_ip:22` succeeds within 3s.

---

## Cost Notes

- Dedicated host billing starts at allocation, not instance launch.
- `mac-m4pro.metal` ≈ $1.83/hr with 24-hour minimum.
- `mac-m4.metal` ≈ $1.29/hr with 24-hour minimum.
- Release host via: `aws ec2 release-hosts --host-ids <HOST_ID> --region <REGION>`
- Do **not** release automatically — always confirm with user first.
