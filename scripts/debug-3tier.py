#!/usr/bin/env python3
"""Debug 3-tier startup - check where it hangs"""

import sys
import os
import time

# Add paths
sys.path.insert(0, os.path.expanduser('~/.openclaw/workspace/momo-kibidango/src'))

print("Step 1: Importing speculative_3model...")
start = time.time()
from speculative_3model import PyramidSpeculativeDecoder, ModelConfig
print(f"  ✅ Imported ({time.time()-start:.1f}s)")

print("Step 2: Creating ModelConfig...")
start = time.time()
config = ModelConfig()
print(f"  ✅ Config created ({time.time()-start:.1f}s)")

print("Step 3: Instantiating PyramidSpeculativeDecoder...")
start = time.time()
decoder = PyramidSpeculativeDecoder(config)
print(f"  ✅ Decoder instantiated ({time.time()-start:.1f}s)")

print("Step 4: Testing generate method...")
start = time.time()
result = decoder.generate("Hello world", max_length=20)
print(f"  ✅ Generation worked ({time.time()-start:.1f}s)")
print(f"  Generated: {result.get('generated_text', '')[:50]}...")

print("\n✅ ALL STEPS SUCCESSFUL")
print("Ready for Flask server!")
