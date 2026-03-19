#!/bin/bash
set -e

echo "🚀 Starting local vLLM-MLX inference server..."
echo ""

source ~/mlx-vllm-env/bin/activate

MODEL_PATH=~/models/qwen35b-4bit

if [ ! -d "$MODEL_PATH" ]; then
  echo "❌ Model not found at $MODEL_PATH"
  exit 1
fi

echo "📂 Model: Qwen 3.5 35B (4-bit quantized)"
echo "🔌 Starting server on http://localhost:8000"
echo ""

# Start vLLM server
python3 -m vllm_mlx.api_server \
  --model $MODEL_PATH \
  --port 8000 \
  --max-num-seqs 4 \
  --max-model-len 4096

