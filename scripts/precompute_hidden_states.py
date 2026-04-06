#!/usr/bin/env python3
"""
Step 1: Pre-compute hidden states from Qwen2.5-7B on CPU.
Saves (hidden_state, target_ids) pairs to disk so training
never needs to touch the base model again.

Run ONCE before training:
  python3 precompute_hidden_states.py

Output: ~/hidden_states_cache/ (numpy .npz files, ~1-2GB for 5K samples)
"""

import os
import gc
import time
import logging
import numpy as np
import torch
from torch.utils.data import Dataset
from transformers import AutoTokenizer, AutoModelForCausalLM
from datasets import load_dataset

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BASE_MODEL   = "Qwen/Qwen2.5-7B-Instruct"
MAX_SEQ_LEN  = 512
MAX_SAMPLES  = 5_000
NUM_DRAFT    = 4
OUTPUT_DIR   = os.path.expanduser("~/hidden_states_cache")
BATCH_SIZE   = 4   # CPU batch — small to avoid RAM spikes

os.makedirs(OUTPUT_DIR, exist_ok=True)

logger.info(f"Loading tokenizer: {BASE_MODEL}")
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

logger.info(f"Loading base model on CPU (bfloat16)...")
model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL, dtype=torch.bfloat16, device_map="cpu", trust_remote_code=True
)
model.eval()
for p in model.parameters():
    p.requires_grad_(False)
logger.info("Model loaded.")

logger.info("Loading ShareGPT dataset...")
ds = load_dataset(
    "anon8231489123/ShareGPT_Vicuna_unfiltered",
    data_files="ShareGPT_V3_unfiltered_cleaned_split.json",
    split="train",
)

samples = []
for row in ds.select(range(min(MAX_SAMPLES * 2, len(ds)))):
    text = " ".join(t.get("value", "") for t in row.get("conversations", []))
    if len(text) < 100:
        continue
    ids = tokenizer(text, truncation=True, max_length=MAX_SEQ_LEN + 1,
                    return_tensors="pt").input_ids.squeeze(0)
    if len(ids) >= NUM_DRAFT + 2:
        samples.append(ids)
    if len(samples) >= MAX_SAMPLES:
        break

logger.info(f"Tokenized {len(samples)} samples. Starting hidden state extraction...")

all_hidden = []
all_targets = []
start = time.time()

for i in range(0, len(samples), BATCH_SIZE):
    batch_ids = samples[i:i + BATCH_SIZE]
    max_len = max(x.size(0) for x in batch_ids)
    padded = torch.zeros(len(batch_ids), max_len, dtype=torch.long)
    for j, x in enumerate(batch_ids):
        padded[j, :x.size(0)] = x

    # Random context split
    seq_len = padded.size(1)
    ctx_end = max(2, seq_len - NUM_DRAFT - 1)
    split = torch.randint(1, ctx_end, (1,)).item()

    context  = padded[:, :split]
    targets  = padded[:, split:split + NUM_DRAFT]

    with torch.no_grad():
        out = model(input_ids=context, output_hidden_states=True, use_cache=False)
        hidden = out.hidden_states[-1][:, -1, :].to(torch.float32).numpy()

    all_hidden.append(hidden)
    all_targets.append(targets.numpy())

    if (i // BATCH_SIZE + 1) % 50 == 0:
        elapsed = time.time() - start
        pct = (i + len(batch_ids)) / len(samples) * 100
        logger.info(f"  {i + len(batch_ids)}/{len(samples)} ({pct:.0f}%) — {elapsed:.0f}s elapsed")

    gc.collect()

hidden_arr  = np.concatenate(all_hidden, axis=0).astype(np.float32)
targets_arr = np.concatenate(all_targets, axis=0).astype(np.int32)

out_path = os.path.join(OUTPUT_DIR, "hidden_states.npz")
np.savez_compressed(out_path, hidden=hidden_arr, targets=targets_arr)

elapsed = time.time() - start
size_mb = os.path.getsize(out_path) / 1e6
logger.info(f"Done! Saved {len(hidden_arr)} samples to {out_path} ({size_mb:.0f} MB) in {elapsed:.0f}s")
logger.info("Now run: python3 train_drafter_cached.py")
