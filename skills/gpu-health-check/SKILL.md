# GPU Health Check Skill

Monitor GPU instance health and send status to Telegram.

## Description

Performs health checks on the GPU inference instance (54.81.20.218) and reports status:
- **Quick check** (@reboot): SSH + GPU + CUDA verification (~5 seconds)
- **Full check** (heartbeat): Includes inference latency test (~90 seconds)

On success: Sends "✅ GPU offload startup OK" to Telegram  
On failure: Sends "❌ GPU offload setup failed" with reason

## Usage

### Quick Check (at boot)
```bash
/Users/rreilly/.openclaw/workspace/scripts/gpu-health-check-quick.sh
```

Runs automatically via cron @reboot. Output piped to Telegram.

### Full Check (heartbeat)
```bash
/Users/rreilly/.openclaw/workspace/scripts/gpu-health-check-full.sh
```

Runs periodically via heartbeat. Includes inference latency test.

## Configuration

### SSH Key
- Location: `~/.ssh/vlm-deploy-key.pem`
- Must be readable by openclaw user
- Verify: `ssh -i ~/.ssh/vlm-deploy-key.pem ubuntu@54.81.20.218 echo OK`

### GPU Instance
- Host: `54.81.20.218`
- User: `ubuntu`
- Model: Mistral-7B-Instruct-v0.1 (cached at `/mnt/data/.cache/hf/models/`)
- venv: `/mnt/data/venv/`

### Log Files
- Quick check: `~/.openclaw/logs/gpu-health.log`
- Full check: `~/.openclaw/logs/gpu-health.log` (appended)
- Startup: `~/.openclaw/logs/gpu-startup.log` (cron output)

## Health Check Criteria

### Quick Check (Pass/Fail)
- ✅ SSH connection succeeds
- ✅ GPU driver detected (nvidia-smi available)
- ✅ CUDA available (torch.cuda.is_available() == True)

### Full Check (Pass/Fail + Metrics)
- ✅ All quick checks pass
- ✅ Model loads successfully
- ✅ Inference completes (10-token generation)
- ✅ Speed > 20 tok/s (sanity check)
- ⚠️ Latency < 90 seconds (warns if degraded)

## Success Message

```
✅ GPU offload startup OK

Instance: 54.81.20.218
GPU: NVIDIA A10G
Status: Ready for inference
Speed: 27.98 tok/s
Latency: 2.1s (3-token prompt)

Ready to accept complex tasks!
```

## Failure Messages

### SSH Unreachable
```
❌ GPU offload setup failed: SSH unreachable
```
- Check: Instance running? IP correct? Key valid?

### GPU Driver Missing
```
❌ GPU offload setup failed: GPU driver issue
```
- Check: nvidia-smi works? NVIDIA driver installed?

### CUDA Initialization Failed
```
❌ GPU offload setup failed: CUDA initialization failed
```
- Check: torch.cuda.is_available()? CUDA drivers loaded?

### Inference Error
```
❌ GPU offload setup failed: Inference test error
```
- Check: Model files at /mnt/data/.cache/hf/?
- Check: venv at /mnt/data/venv/ valid?
- Check: Disk space available?

## Integration with OpenClaw

### Cron @reboot
```bash
@reboot /Users/rreilly/.openclaw/workspace/scripts/gpu-health-check-quick.sh 2>&1 | tee -a ~/.openclaw/logs/gpu-startup.log
```

Runs once on Mac reboot. Output sent to Telegram via cron job callback.

### Heartbeat Monitoring
Edit `~/.openclaw/workspace/HEARTBEAT.md`:
```
## GPU Offload Health Check
Run full GPU health test every heartbeat
```

### Manual Test
```bash
bash ~/.openclaw/workspace/scripts/gpu-health-check-quick.sh
bash ~/.openclaw/workspace/scripts/gpu-health-check-full.sh
```

## Troubleshooting

### "SSH connection timeout"
- Check instance is running: `aws ec2 describe-instances --instance-ids i-046d1154c0f4a9b2e`
- Check security group allows port 22
- Verify key: `ssh-keygen -l -f ~/.ssh/vlm-deploy-key.pem`

### "CUDA not available"
- SSH in and check: `nvidia-smi`
- Check: `/mnt/data/venv/bin/python3 -c 'import torch; print(torch.cuda.is_available())'`
- If False: Restart instance or reinstall NVIDIA drivers

### "Inference test failed"
- Check model cache: `ls /mnt/data/.cache/hf/models/`
- Check venv: `/mnt/data/venv/bin/python3 --version`
- Check disk: `df -h /mnt/data/`

## Cost Impact

- Quick check: Negligible (5 seconds SSH, no GPU compute)
- Full check: ~60 seconds GPU time (~$0.02 per check)
- Daily full checks: ~$0.60/month
- Worth the insurance for $980/month instance

## References

- GPU Instance: i-046d1154c0f4a9b2e (g5.2xlarge, us-east-1)
- Instance IP: 54.81.20.218
- Instance Type: NVIDIA A10G (23GB VRAM)
- Monthly Cost: $980
- Performance Baseline: 27.98 tok/s (Mistral-7B-Instruct-v0.1)
