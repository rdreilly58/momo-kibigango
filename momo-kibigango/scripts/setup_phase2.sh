#!/bin/bash
# Phase 2 Setup Script for momo-kibigango
# Sets up environment and checks dependencies

set -e

echo "=== Phase 2: 2-Model Speculative Decoding Setup ==="
echo "Date: $(date)"
echo "Project: momo-kibigango"

# Check Python version
echo -e "\n1. Checking Python environment..."
python3 --version

# Create virtual environment if it doesn't exist
VENV_DIR="venv_phase2"
if [ ! -d "$VENV_DIR" ]; then
    echo -e "\n2. Creating virtual environment..."
    python3 -m venv $VENV_DIR
else
    echo -e "\n2. Virtual environment already exists"
fi

# Activate virtual environment
echo -e "\n3. Activating virtual environment..."
source $VENV_DIR/bin/activate

# Upgrade pip
echo -e "\n4. Upgrading pip..."
pip install --upgrade pip

# Install PyTorch for Apple Silicon (MPS)
echo -e "\n5. Installing PyTorch for Apple Silicon..."
if [[ $(uname -m) == "arm64" ]]; then
    # Apple Silicon Mac
    pip install torch torchvision torchaudio
else
    # Intel Mac or Linux
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
fi

# Install requirements
echo -e "\n6. Installing Phase 2 requirements..."
pip install -r requirements-phase2.txt

# Check GPU availability
echo -e "\n7. Checking compute device..."
python3 -c "
import torch
if torch.backends.mps.is_available():
    print('✅ Apple Silicon GPU (MPS) is available')
elif torch.cuda.is_available():
    print('✅ CUDA GPU is available')
else:
    print('⚠️  No GPU detected, will use CPU')
"

# Check memory
echo -e "\n8. System memory check..."
python3 -c "
import psutil
mem = psutil.virtual_memory()
print(f'Total RAM: {mem.total / (1024**3):.1f} GB')
print(f'Available RAM: {mem.available / (1024**3):.1f} GB')
print(f'Used RAM: {mem.percent:.1f}%')
"

# Create necessary directories
echo -e "\n9. Creating project directories..."
mkdir -p results
mkdir -p logs
mkdir -p models/cache

# Check for existing models
echo -e "\n10. Checking for cached models..."
if [ -d "$HOME/.cache/huggingface/hub/models--mlx-community--Qwen2-7B-4bit" ]; then
    echo "✅ Qwen2-7B-4bit model found in cache"
else
    echo "⚠️  Qwen2-7B-4bit model not found, will download on first run"
fi

# Check if Phi-2 is cached
if [ -d "$HOME/.cache/huggingface/hub/models--microsoft--phi-2" ]; then
    echo "✅ Phi-2 draft model found in cache"
else
    echo "⚠️  Phi-2 draft model not found, will download on first run (~2.7GB)"
fi

# Create a simple test script
echo -e "\n11. Creating test script..."
cat > test_setup.py << 'EOF'
#!/usr/bin/env python3
"""Quick test to verify setup"""

import torch
import transformers
import psutil

print("Setup verification:")
print(f"- PyTorch version: {torch.__version__}")
print(f"- Transformers version: {transformers.__version__}")
print(f"- Device: {'MPS' if torch.backends.mps.is_available() else 'CUDA' if torch.cuda.is_available() else 'CPU'}")
print(f"- Available memory: {psutil.virtual_memory().available / (1024**3):.1f} GB")
print("\n✅ Setup complete! Ready for Phase 2 implementation.")
EOF

chmod +x test_setup.py

echo -e "\n12. Running setup verification..."
python3 test_setup.py

echo -e "\n=== Setup Complete ==="
echo "To activate the environment in future sessions:"
echo "  source venv_phase2/bin/activate"
echo ""
echo "To run the speculative decoding implementation:"
echo "  python src/speculative_2model.py"
echo ""