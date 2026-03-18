#!/bin/bash
# gpu-health-check-quick.sh
# Quick GPU health check on Mac boot
# Sends status to Telegram on success/failure

GPU_HOST="54.81.20.218"
GPU_KEY="$HOME/.ssh/vlm-deploy-key.pem"
LOG_FILE="$HOME/.openclaw/logs/gpu-health.log"

mkdir -p "$(dirname "$LOG_FILE")"

log_msg() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log_msg "=== GPU Health Check Started ==="

# Test SSH connection
if ! ssh -o ConnectTimeout=10 -o LogLevel=ERROR -i "$GPU_KEY" ubuntu@$GPU_HOST "true" >/dev/null 2>&1; then
  log_msg "FAIL: SSH timeout or connection refused"
  MSG="❌ GPU offload setup failed: SSH unreachable (check instance/key)"
  echo "$MSG"
  exit 1
fi

log_msg "PASS: SSH connection"

# Run quick Python check on GPU instance
RESULT=$(ssh -o LogLevel=ERROR -i "$GPU_KEY" ubuntu@$GPU_HOST /mnt/data/venv/bin/python3 <<'PYEND' 2>&1
import torch
print(f"GPU_NAME:{torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NONE'}")
print(f"CUDA_OK:{torch.cuda.is_available()}")
PYEND
)

if echo "$RESULT" | grep -q "CUDA_OK:True"; then
  GPU_NAME=$(echo "$RESULT" | grep "GPU_NAME:" | cut -d':' -f2)
  log_msg "SUCCESS: GPU operational (GPU: $GPU_NAME, CUDA: OK)"
  
  MSG="✅ GPU offload startup OK

Instance: 54.81.20.218
GPU: $GPU_NAME  
Status: Ready for inference"
  
  echo "$MSG"
  exit 0
else
  log_msg "FAIL: CUDA check failed. Output: $RESULT"
  MSG="❌ GPU offload setup failed: CUDA not available"
  echo "$MSG"
  exit 1
fi
