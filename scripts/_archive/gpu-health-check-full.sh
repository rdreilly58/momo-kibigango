#!/bin/bash
# gpu-health-check-full.sh
# Full health check on heartbeat: SSH + GPU + CUDA + inference latency test
# Runtime: ~60-90 seconds (includes model load if not cached)

set -e

GPU_USER="ubuntu"
GPU_HOST="54.81.20.218"
GPU_KEY="$HOME/.ssh/vlm-deploy-key.pem"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Log file
LOG_FILE="$HOME/.openclaw/logs/gpu-health.log"
mkdir -p "$(dirname "$LOG_FILE")"

log_status() {
  local status=$1
  local message=$2
  local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
  echo "[$timestamp] $status: $message" >> "$LOG_FILE"
}

echo "" >> "$LOG_FILE"
echo "🔬 GPU Health Check (Full)" >> "$LOG_FILE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━" >> "$LOG_FILE"

# Step 1-3: Quick checks (same as quick script)
if ! ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=accept-new -i "$GPU_KEY" "$GPU_USER@$GPU_HOST" "echo CONNECTED" > /dev/null 2>&1; then
  log_status "FAIL" "SSH connection failed"
  echo "❌ GPU offload setup failed: SSH unreachable"
  exit 1
fi

log_status "PASS" "SSH connection OK"

GPU_CHECK=$(ssh -i "$GPU_KEY" "$GPU_USER@$GPU_HOST" << 'EOFCHECK'
output=$(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null || echo "FAILED")
if [ "$output" = "FAILED" ]; then
  echo "GPU_DRIVER_MISSING"
  exit 1
fi

cuda_check=$(/mnt/data/venv/bin/python3 << 'EOFPYTHON'
import torch
if torch.cuda.is_available():
    print("CUDA_OK")
else:
    print("CUDA_UNAVAILABLE")
EOFPYTHON
)

echo "$output|$cuda_check"
EOFCHECK
)

GPU_NAME=$(echo "$GPU_CHECK" | cut -d'|' -f1)
CUDA_STATUS=$(echo "$GPU_CHECK" | cut -d'|' -f2)

if [ "$GPU_NAME" = "GPU_DRIVER_MISSING" ] || [ -z "$GPU_NAME" ]; then
  log_status "FAIL" "GPU driver not detected"
  echo "❌ GPU offload setup failed: GPU driver issue"
  exit 1
fi

log_status "PASS" "GPU: $GPU_NAME"

if [ "$CUDA_STATUS" != "CUDA_OK" ]; then
  log_status "FAIL" "CUDA not available"
  echo "❌ GPU offload setup failed: CUDA initialization failed"
  exit 1
fi

log_status "PASS" "CUDA: OK"

# Step 4: Full inference test
INFERENCE_RESULT=$(ssh -i "$GPU_KEY" "$GPU_USER@$GPU_HOST" << 'EOFINF'
cd /mnt/data && source venv/bin/activate

python3 << 'EOFPYTHONTEST'
import torch
import time
from transformers import AutoModelForCausalLM, AutoTokenizer

print("INFERENCE_TEST_START")

try:
    # Load model
    start = time.time()
    model = AutoModelForCausalLM.from_pretrained(
        "mistralai/Mistral-7B-Instruct-v0.1",
        device_map="auto",
        torch_dtype=torch.bfloat16
    )
    tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1")
    load_time = time.time() - start
    
    # Quick test prompt (3 tokens)
    prompt = "Hello, how are you?"
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    
    # Measure latency
    start = time.time()
    with torch.no_grad():
        output = model.generate(inputs["input_ids"], max_new_tokens=10, temperature=0.7)
    infer_time = time.time() - start
    
    response = tokenizer.decode(output[0], skip_special_tokens=True)
    tokens_generated = len(output[0]) - len(inputs["input_ids"][0])
    tok_per_sec = tokens_generated / infer_time if infer_time > 0 else 0
    
    print(f"LOAD_TIME:{load_time:.2f}")
    print(f"INFER_TIME:{infer_time:.2f}")
    print(f"TOKENS_GENERATED:{tokens_generated}")
    print(f"TOK_PER_SEC:{tok_per_sec:.2f}")
    print("INFERENCE_TEST_OK")
    
except Exception as e:
    print(f"INFERENCE_TEST_FAILED:{str(e)}")
    exit(1)

EOFPYTHONTEST
EOFINF
)

# Parse results
if echo "$INFERENCE_RESULT" | grep -q "INFERENCE_TEST_OK"; then
  LOAD_TIME=$(echo "$INFERENCE_RESULT" | grep "LOAD_TIME:" | cut -d':' -f2)
  INFER_TIME=$(echo "$INFERENCE_RESULT" | grep "INFER_TIME:" | cut -d':' -f2)
  TOK_PER_SEC=$(echo "$INFERENCE_RESULT" | grep "TOK_PER_SEC:" | cut -d':' -f2)
  
  log_status "PASS" "Inference test OK (Load: ${LOAD_TIME}s, Latency: ${INFER_TIME}s, Speed: ${TOK_PER_SEC} tok/s)"
  
  # Sanity checks
  SPEED_INT=$(echo "$TOK_PER_SEC" | cut -d'.' -f1)
  if [ "$SPEED_INT" -lt 20 ]; then
    log_status "WARN" "Speed degraded: ${TOK_PER_SEC} tok/s (expected >25)"
  fi
  
  SUCCESS_MESSAGE="✅ GPU offload startup OK

Instance: 54.81.20.218
GPU: $GPU_NAME
Status: Fully operational

Inference Test Results:
  Model load time: ${LOAD_TIME}s
  Response latency: ${INFER_TIME}s
  Speed: ${TOK_PER_SEC} tok/s
  
All systems nominal. Ready to accept complex tasks!"
  
  log_status "SUCCESS" "Full health check passed"
  echo "$SUCCESS_MESSAGE"
  exit 0
else
  ERROR=$(echo "$INFERENCE_RESULT" | grep "INFERENCE_TEST_FAILED:" | cut -d':' -f2-)
  log_status "FAIL" "Inference test failed: $ERROR"
  echo "❌ GPU offload setup failed: Inference test error"
  exit 1
fi
