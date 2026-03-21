#!/usr/bin/env python3
"""Download and verify the all-MiniLM-L6-v2 embedding model."""

import os
import sys
import time

# Add venv to path
sys.path.insert(0, os.path.expanduser("~/.openclaw/workspace/venv/lib/python3.14/site-packages"))

from sentence_transformers import SentenceTransformer

print("Downloading all-MiniLM-L6-v2 model...")
start_time = time.time()

# Download model (will cache automatically)
model = SentenceTransformer('all-MiniLM-L6-v2')

download_time = time.time() - start_time
print(f"✓ Model downloaded in {download_time:.2f} seconds")

# Test the model
print("\nTesting embedding generation...")
test_text = "This is a test sentence to verify the embedding model works."
start_time = time.time()
embedding = model.encode(test_text)
inference_time = (time.time() - start_time) * 1000  # Convert to ms

print(f"✓ Embedding generated successfully")
print(f"  - Dimension: {len(embedding)}")
print(f"  - Inference time: {inference_time:.1f}ms")
print(f"  - First 5 values: {embedding[:5].tolist()}")

# Get model info
print(f"\nModel info:")
print(f"  - Max sequence length: {model.max_seq_length}")
print(f"  - Embedding dimension: {model.get_sentence_embedding_dimension()}")

print("\n✅ Model ready for use!")