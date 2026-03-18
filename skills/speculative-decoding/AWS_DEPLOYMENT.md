# AWS Phase 2 Deployment Guide

**Goal:** Launch vLLM speculative decoding on AWS GPU instance  
**Time:** ~20 minutes setup + 10 minutes vLLM startup  
**Cost:** ~$3 for testing, ~$24 for 8 hours

---

## Prerequisites

1. **AWS Account** with billing enabled
2. **AWS CLI** installed + configured
   - Already installed ✅
   - Configure credentials: `aws configure`
3. **EC2 Key Pair** (for SSH access)

---

## Quick Start (4 Steps)

### Step 1: Create EC2 Key Pair (5 minutes)

```bash
# Create key pair
aws ec2 create-key-pair \
  --key-name vlm-key-pair \
  --region us-east-1 \
  --query 'KeyMaterial' \
  --output text > ~/vlm-key-pair.pem

# Make it secure
chmod 400 ~/vlm-key-pair.pem

# Verify it works
ls -la ~/vlm-key-pair.pem
# Output: -r--------  vlm-key-pair.pem
```

### Step 2: Launch AWS Instance (5 minutes)

```bash
cd ~/.openclaw/workspace/skills/speculative-decoding

chmod +x scripts/launch-aws-instance.sh

./scripts/launch-aws-instance.sh vlm-key-pair
```

**What happens:**
- Creates security group (allows SSH + port 8000)
- Launches p3.2xlarge instance (V100 GPU, 8 vCPU, 16GB RAM)
- Waits for instance to be ready
- Outputs IP address + SSH instructions

**Output will look like:**
```
✅ Instance Ready!

Instance Details:
  ID: i-0123456789abcdef0
  Type: p3.2xlarge
  IP: 54.123.456.789
  Region: us-east-1

Next steps:
  1. ssh -i ~/vlm-key-pair.pem ubuntu@54.123.456.789
  ...
```

### Step 3: SSH Into Instance (1 minute)

```bash
# Copy the IP from previous output
ssh -i ~/vlm-key-pair.pem ubuntu@54.123.456.789

# You'll see something like:
# ubuntu@ip-172-31-0-123:~$
```

### Step 4: Deploy vLLM (10 minutes)

**On the remote instance:**

```bash
# Update system
sudo apt update && sudo apt install -y git curl

# Clone the skill (or upload it)
# Option A: From git repo
git clone <your-openclaw-repo-url> openclaw
cd openclaw/workspace/skills/speculative-decoding

# Option B: Copy from local machine
# (Exit SSH, then from local machine):
# scp -i ~/vlm-key-pair.pem -r ~/.openclaw/workspace/skills/speculative-decoding ubuntu@54.123.456.789:~/

# Install vLLM + dependencies
./scripts/install-dependencies.sh

# Start vLLM server
./scripts/start-vlm-server.sh
```

**You'll see:**
```
✅ Virtual environment created
✅ Virtual environment activated
Installing vLLM...
[... lots of installation ...]
✅ vLLM installed
```

**Takes ~8-10 minutes first time** (downloading Llama models = 39GB)

---

## Testing

### From Remote Instance

```bash
# In the SSH session, test locally
./scripts/test-speculative.sh
```

### From Your Local Machine

```bash
# In a new terminal on your Mac
curl http://54.123.456.789:8000/health

# Should respond with:
# {"status":"ready"}
```

---

## Expected Performance

Once running, you should see:

| Metric | Expected |
|--------|----------|
| Simple query latency | 0.3-0.5s |
| Quality (simple) | 85% of Claude |
| Throughput | 10-20 req/sec |
| Availability | 99.9% uptime |

---

## Monitoring

### View Server Logs

**From SSH session:**
```bash
tail -f logs/vlm-server.log
```

### Monitor GPU Usage

**From SSH session:**
```bash
# Watch real-time GPU stats
nvidia-smi

# Should show:
# | GPU | Name | Memory-Usage | GPU-Util |
# |  0  | Tesla V100 | 15000MiB | 95% |
```

### Check Disk Space

```bash
df -h

# vLLM models will be ~39GB total
```

---

## Cost Management

### Check Running Time

```bash
# From local machine
aws ec2 describe-instances \
  --instance-ids i-0123456789abcdef0 \
  --query 'Reservations[0].Instances[0].[LaunchTime,State.Name]'
```

### Stop Instance (Pauses Billing)

```bash
# From local machine
aws ec2 stop-instances \
  --instance-ids i-0123456789abcdef0 \
  --region us-east-1

# Cost when stopped: ~$0.05/month (storage only)
# To resume: aws ec2 start-instances ...
```

### Terminate Instance (Stops Billing)

```bash
# FROM LOCAL MACHINE - WARNING: Deletes instance!
aws ec2 terminate-instances \
  --instance-ids i-0123456789abcdef0 \
  --region us-east-1

# Cost: $0 (fully stopped)
# Models will be deleted
# Cannot resume
```

---

## Troubleshooting

### "Permission denied" when SSHing

```bash
# Fix permissions
chmod 400 ~/vlm-key-pair.pem

# Try again
ssh -i ~/vlm-key-pair.pem ubuntu@54.123.456.789
```

### "vLLM installation takes too long"

- This is normal! First time downloads 39GB of Llama models
- Takes ~10 minutes on p3.2xlarge (fast GPU internet)
- Check progress: `nvidia-smi` (should show GPU at 100%)

### "Out of memory" error

- p3.2xlarge has 61GB RAM + 16GB VRAM
- Should be enough for Llama 7B + 13B
- If error, try: Llama 7B only (no verifier model)

### "CUDA error"

- Check: `nvidia-smi` (should show Tesla V100)
- Check vLLM logs: `tail -f logs/vlm-server.log`
- Make sure both models finished downloading

---

## Next Steps After Testing

### Option 1: Keep Running (Production)
- Monitor performance metrics
- Document actual speedup vs. Claude API
- Adjust batch sizes if needed
- Plan scaling

### Option 2: Stop for Now (Save Money)
```bash
# Stop instance (pause billing)
aws ec2 stop-instances --instance-ids i-xxx

# Can restart later
aws ec2 start-instances --instance-ids i-xxx
```

### Option 3: Terminate (Clean Up)
```bash
# Delete everything
aws ec2 terminate-instances --instance-ids i-xxx
```

---

## Cost Breakdown

| Item | Price | Notes |
|------|-------|-------|
| p3.2xlarge instance | $3.06/hr | Running time |
| Storage (EBS) | $10.80/month | 100GB gp3 |
| Data transfer | $0.02/GB | Outbound |
| Key pair | Free | Reusable |

**Example costs:**
- 1 hour testing: ~$3
- 1 day 24hr: ~$73
- 1 month (if left on): ~$2,200

**Recommendation:** Stop when not actively testing

---

## Success Criteria

You'll know it's working when:

✅ SSH into instance succeeds  
✅ vLLM installation completes  
✅ `nvidia-smi` shows V100 GPU  
✅ `./scripts/test-speculative.sh` passes all 4 tests  
✅ `curl http://IP:8000/health` returns `{"status":"ready"}`  
✅ Latency is 0.3-0.5s for simple queries  

---

## Questions?

Check:
- AWS docs: https://aws.amazon.com/ec2/
- vLLM docs: https://docs.vllm.ai
- Troubleshooting section above

Ready to deploy! 🚀
