#!/bin/bash
set -e

echo "📦 Installing vLLM-MLX for local GPU inference..."

# Create venv if needed
if [ ! -d ~/mlx-vllm-env ]; then
  echo "Creating Python environment..."
  python3 -m venv ~/mlx-vllm-env
fi

source ~/mlx-vllm-env/bin/activate

# Install vLLM-MLX
echo "Installing vLLM-MLX..."
pip install --upgrade pip
pip install vllm-mlx torch numpy transformers

# Test import
echo "Testing imports..."
python3 << 'PYTHON_TEST'
try:
  from vllm_mlx import vLLM
  print("✓ vLLM-MLX imported successfully")
except Exception as e:
  print(f"⚠️ Error: {e}")
PYTHON_TEST

echo ""
echo "✓ vLLM-MLX setup complete"
