#!/usr/bin/env python3
"""
Minimal test to check if PyTorch and transformers are available
Run this before the full setup to verify basic dependencies.
"""

import sys

print("Python version:", sys.version)

try:
    import torch
    print(f"✅ PyTorch installed: {torch.__version__}")
    
    if torch.backends.mps.is_available():
        print("✅ Apple Silicon GPU (MPS) available")
    elif torch.cuda.is_available():
        print("✅ CUDA GPU available")
    else:
        print("⚠️  No GPU detected, will use CPU")
        
except ImportError:
    print("❌ PyTorch not installed")
    
try:
    import transformers
    print(f"✅ Transformers installed: {transformers.__version__}")
except ImportError:
    print("❌ Transformers not installed")

try:
    import psutil
    mem = psutil.virtual_memory()
    print(f"✅ System memory: {mem.total / (1024**3):.1f} GB total, {mem.available / (1024**3):.1f} GB available")
except ImportError:
    print("❌ psutil not installed")

print("\nTo install missing dependencies:")
print("  pip install torch transformers psutil")