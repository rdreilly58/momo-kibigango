#!/bin/bash
# Setup script for TPU v6e-1 VM (Trillium)
# Run this once after SSH-ing into the TPU VM

set -e

echo "=== Setting up TPU v6e environment ==="

# Install PyTorch + XLA for TPU v6 (Trillium)
# TPU v6e uses the same torch_xla as v5e but with newer libtpu
pip install torch==2.3.0 torchvision --extra-index-url https://download.pytorch.org/whl/cpu
pip install torch_xla[tpu] -f https://storage.googleapis.com/libtpu-releases/index.html

# HuggingFace stack
pip install transformers datasets accelerate sentencepiece protobuf

echo "=== Verifying TPU access ==="
python3 -c "
import torch_xla.core.xla_model as xm
device = xm.xla_device()
print(f'✅ TPU device: {device}')
x = torch.ones(2, 2).to(device)
print(f'✅ Tensor on TPU: {x}')
"

echo "=== Setup complete ==="
echo "Run: python train_drafter_tpu_v6e.py"
