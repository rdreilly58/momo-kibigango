#!/bin/bash

# Install vLLM and dependencies for speculative decoding
# Uses a virtual environment to avoid system Python conflicts

set -e

# Get absolute paths
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SKILL_DIR="$( dirname "$SCRIPT_DIR" )"
VENV_DIR="$SKILL_DIR/venv"

echo "=========================================="
echo "📦 Installing vLLM Dependencies"
echo "=========================================="
echo ""
echo "Script dir: $SCRIPT_DIR"
echo "Skill dir: $SKILL_DIR"
echo "Venv dir: $VENV_DIR"
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1)
echo "Python version: $PYTHON_VERSION"

if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
  echo "❌ Error: Python 3.8+ required"
  exit 1
fi

echo "✅ Python 3.8+ detected"
echo ""

# Create virtual environment
echo "Creating virtual environment at $VENV_DIR..."
python3 -m venv "$VENV_DIR"
echo "✅ Virtual environment created"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"
echo "✅ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing core dependencies..."
echo ""

# Upgrade pip
python3 -m pip install --upgrade pip setuptools wheel

# Install vLLM
echo ""
echo "Installing vLLM..."
python3 -m pip install vllm

# Install supporting libraries
echo ""
echo "Installing supporting libraries..."
python3 -m pip install \
  torch \
  transformers \
  peft \
  accelerate \
  jinja2 \
  requests \
  pydantic

# Check GPU support
echo ""
if command -v nvidia-smi &> /dev/null; then
  echo "✅ NVIDIA GPU detected"
else
  echo "⚠️  No NVIDIA GPU detected (will run slower on CPU)"
fi

echo ""
echo "=========================================="
echo "✅ Installation complete!"
echo "=========================================="
echo ""
echo "Virtual environment created at:"
echo "  $VENV_DIR"
echo ""
echo "To use it, either:"
echo "  1. Run scripts from this directory (they auto-activate)"
echo "  2. Or manually: source $VENV_DIR/bin/activate"
echo ""
echo "Next steps:"
echo "  1. Accept Llama model terms at https://huggingface.co/meta-llama"
echo "  2. Login to HuggingFace: huggingface-cli login"
echo "  3. Start the server: ./scripts/start-vlm-server.sh"
echo ""

# Verify installation inside venv
echo "Verifying installation..."
python3 -c "import vllm; print(f'✅ vLLM {vllm.__version__} installed')"
python3 -c "import torch; print(f'✅ PyTorch {torch.__version__} installed')"
python3 -c "import transformers; print(f'✅ Transformers {transformers.__version__} installed')"

echo ""
echo "Ready to go! 🚀"
