#!/usr/bin/env python3
"""
Precompute hidden states using SYNTHETIC data — no HuggingFace dataset needed.
Generates random word sequences, runs Qwen2.5-7B on CPU, saves hidden states.
Fast, self-contained, no auth/download issues.
"""
import os, gc, time, logging, sys, random
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", stream=sys.stdout, force=True)
log = logging.getLogger()

BASE      = "Qwen/Qwen2.5-7B-Instruct"
OUT       = os.path.expanduser("~/hidden_states_cache/hidden_states.npz")
MAX_SEQ   = 128   # Short context — fast CPU inference
NUM_DRAFT = 4
N_SAMPLES = 2000
BATCH     = 2

os.makedirs(os.path.dirname(OUT), exist_ok=True)

log.info("Loading tokenizer...")
tok = AutoTokenizer.from_pretrained(BASE, trust_remote_code=True)
if tok.pad_token is None:
    tok.pad_token = tok.eos_token
log.info("Tokenizer loaded.")

log.info("Loading Qwen2.5-7B on CPU (bfloat16)...")
model = AutoModelForCausalLM.from_pretrained(
    BASE, torch_dtype=torch.bfloat16, device_map="cpu", trust_remote_code=True
)
model.eval()
for p in model.parameters():
    p.requires_grad_(False)
log.info(f"Model loaded. Hidden size: {model.config.hidden_size}")

# Synthetic vocab — no download needed
WORDS = [
    "the","quick","brown","fox","jumps","over","lazy","dog",
    "machine","learning","neural","network","transformer","attention",
    "model","training","inference","gradient","loss","optimize",
    "batch","epoch","weight","bias","layer","token","data","input",
    "output","hidden","state","sequence","context","generate","predict",
    "embedding","linear","softmax","activation","dropout","residual",
]

log.info(f"Generating {N_SAMPLES} synthetic samples (seq_len={MAX_SEQ})...")
samples = []
for _ in range(N_SAMPLES):
    n = random.randint(MAX_SEQ // 2, MAX_SEQ)
    text = " ".join(random.choices(WORDS, k=n))
    ids = tok(text, truncation=True, max_length=MAX_SEQ + NUM_DRAFT + 1,
              return_tensors="pt").input_ids.squeeze(0)
    if len(ids) >= NUM_DRAFT + 4:
        samples.append(ids)
log.info(f"Generated {len(samples)} valid samples.")

hidden_list, target_list = [], []
t0 = time.time()

for i in range(0, len(samples), BATCH):
    batch = samples[i:i + BATCH]
    max_l = max(x.size(0) for x in batch)
    pad = torch.zeros(len(batch), max_l, dtype=torch.long)
    for j, x in enumerate(batch):
        pad[j, :x.size(0)] = x

    split = max(2, pad.size(1) - NUM_DRAFT - 1)
    ctx = pad[:, :split]
    tgt = pad[:, split:split + NUM_DRAFT]

    with torch.no_grad():
        out = model(input_ids=ctx, output_hidden_states=True, use_cache=False)
        h = out.hidden_states[-1][:, -1, :].float().numpy()

    hidden_list.append(h)
    target_list.append(tgt.numpy())

    done = i + len(batch)
    if done % 200 == 0 or done == len(samples):
        elapsed = time.time() - t0
        pct = done / len(samples) * 100
        log.info(f"  {done}/{len(samples)} ({pct:.0f}%) | {elapsed:.0f}s elapsed")

    gc.collect()

hidden  = np.concatenate(hidden_list).astype(np.float32)
targets = np.concatenate(target_list).astype(np.int32)
np.savez_compressed(OUT, hidden=hidden, targets=targets)

elapsed = time.time() - t0
size_mb = os.path.getsize(OUT) / 1e6
log.info(f"✅ Done! Saved {len(hidden)} samples -> {OUT} ({size_mb:.1f}MB) in {elapsed:.0f}s")
log.info("Now run: python3 train_drafter_cached.py")
