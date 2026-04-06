#!/usr/bin/env python3
"""
Step 2: Train ReDrafter head from pre-computed hidden states.
No base model needed — pure TPU training, blazing fast.

Requires: ~/hidden_states_cache/hidden_states.npz (from precompute_hidden_states.py)

Usage:
  python3 train_drafter_cached.py
"""

import os
import math
import time
import logging
import numpy as np
from dataclasses import dataclass

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW

try:
    import torch_xla.core.xla_model as xm
    import torch_xla.distributed.parallel_loader as pl
    TPU_AVAILABLE = True
    print("✅ TPU/XLA available")
except ImportError:
    TPU_AVAILABLE = False
    print("⚠️  No TPU — using CPU")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class Config:
    cache_path: str    = os.path.expanduser("~/hidden_states_cache/hidden_states.npz")
    output_dir: str    = os.path.expanduser("~/drafter_output_cached")

    # Draft head
    drafter_hidden: int = 512
    num_layers: int     = 2
    num_draft_tokens: int = 4

    # Training
    batch_size: int     = 64       # Large — no base model overhead!
    grad_accum: int     = 2        # Effective batch = 128
    lr: float           = 2e-4
    weight_decay: float = 0.01
    warmup_steps: int   = 100
    max_steps: int      = 3000
    save_every: int     = 500
    log_every: int      = 10
    dtype               = torch.bfloat16

CFG = Config()


# ---------------------------------------------------------------------------
# Cached dataset — loads pre-computed hidden states
# ---------------------------------------------------------------------------

class CachedHiddenDataset(Dataset):
    def __init__(self, path: str):
        logger.info(f"Loading cached hidden states from {path}...")
        data = np.load(path)
        self.hidden  = torch.from_numpy(data["hidden"]).to(torch.bfloat16)  # [N, H]
        self.targets = torch.from_numpy(data["targets"]).long()              # [N, K]
        self.hidden_size = self.hidden.shape[1]
        logger.info(f"Loaded {len(self.hidden)} samples, hidden_size={self.hidden_size}")

    def __len__(self):
        return len(self.hidden)

    def __getitem__(self, idx):
        return self.hidden[idx], self.targets[idx]


# ---------------------------------------------------------------------------
# Draft head (same architecture as before)
# ---------------------------------------------------------------------------

class ReDrafterHead(nn.Module):
    def __init__(self, vocab_size, hidden_size, drafter_hidden=512, num_layers=2, num_draft_tokens=4):
        super().__init__()
        self.num_draft_tokens = num_draft_tokens
        self.input_proj  = nn.Linear(hidden_size, drafter_hidden)
        self.gru = nn.GRU(drafter_hidden, drafter_hidden, num_layers=num_layers, batch_first=True)
        self.token_embed = nn.Embedding(vocab_size, drafter_hidden)
        self.output_proj = nn.Linear(drafter_hidden, vocab_size, bias=False)
        nn.init.xavier_uniform_(self.input_proj.weight)
        nn.init.zeros_(self.input_proj.bias)
        nn.init.xavier_uniform_(self.output_proj.weight)

    def forward(self, hidden_state, target_ids=None):
        B = hidden_state.size(0)
        h0 = self.input_proj(hidden_state).unsqueeze(0).expand(
            self.gru.num_layers, -1, -1).contiguous()
        x = torch.zeros(B, h0.shape[-1], device=hidden_state.device, dtype=hidden_state.dtype)
        h = h0
        logits_list = []
        for step in range(self.num_draft_tokens):
            out, h = self.gru(x.unsqueeze(1), h)
            logits = self.output_proj(out.squeeze(1))
            logits_list.append(logits)
            if target_ids is not None:
                x = self.token_embed(target_ids[:, step])
            else:
                x = self.token_embed(logits.argmax(dim=-1))
        return torch.stack(logits_list, dim=1)  # [B, K, V]


def compute_loss(draft_logits, target_ids):
    K = draft_logits.size(1)
    loss = torch.tensor(0.0, device=draft_logits.device, dtype=draft_logits.dtype)
    for k in range(K):
        loss = loss + F.cross_entropy(draft_logits[:, k, :].float(), target_ids[:, k], ignore_index=0)
    return loss / K


def get_lr(step, warmup, max_steps, base_lr):
    if step < warmup:
        return base_lr * step / max(warmup, 1)
    progress = (step - warmup) / max(max_steps - warmup, 1)
    return base_lr * 0.5 * (1 + math.cos(math.pi * progress))


# ---------------------------------------------------------------------------
# Train
# ---------------------------------------------------------------------------

def train():
    cfg = CFG
    os.makedirs(cfg.output_dir, exist_ok=True)

    device = xm.xla_device() if TPU_AVAILABLE else torch.device("cpu")
    logger.info(f"Device: {device}")

    dataset = CachedHiddenDataset(cfg.cache_path)
    hidden_size = dataset.hidden_size

    # Need vocab size — load tokenizer only (tiny, fast)
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B-Instruct", trust_remote_code=True)
    vocab_size = len(tokenizer)
    logger.info(f"Vocab size: {vocab_size}")

    loader = DataLoader(dataset, batch_size=cfg.batch_size, shuffle=True,
                        drop_last=True, num_workers=0)
    if TPU_AVAILABLE:
        loader = pl.MpDeviceLoader(loader, device)

    draft_head = ReDrafterHead(
        vocab_size=vocab_size,
        hidden_size=hidden_size,
        drafter_hidden=cfg.drafter_hidden,
        num_layers=cfg.num_layers,
        num_draft_tokens=cfg.num_draft_tokens,
    ).to(device).to(cfg.dtype)

    n_params = sum(p.numel() for p in draft_head.parameters())
    logger.info(f"Draft head: {n_params:,} params ({n_params/1e6:.1f}M)")

    optimizer = AdamW(draft_head.parameters(), lr=cfg.lr,
                      weight_decay=cfg.weight_decay, betas=(0.9, 0.95))

    step = 0
    optimizer.zero_grad()
    start = time.time()
    new_lr = cfg.lr

    logger.info("Starting training...")

    while step < cfg.max_steps:
        for hidden, targets in loader:
            if step >= cfg.max_steps:
                break

            if not TPU_AVAILABLE:
                hidden  = hidden.to(device)
                targets = targets.to(device)

            logits = draft_head(hidden, target_ids=targets)
            loss   = compute_loss(logits, targets) / cfg.grad_accum
            loss.backward()

            if (step + 1) % cfg.grad_accum == 0:
                new_lr = get_lr(step, cfg.warmup_steps, cfg.max_steps, cfg.lr)
                for pg in optimizer.param_groups:
                    pg["lr"] = new_lr
                if TPU_AVAILABLE:
                    xm.optimizer_step(optimizer)
                else:
                    optimizer.step()
                optimizer.zero_grad()
                if TPU_AVAILABLE:
                    xm.mark_step()

            step += 1

            if step % cfg.log_every == 0:
                elapsed = time.time() - start
                loss_val = loss.item() * cfg.grad_accum
                logger.info(f"step={step}/{cfg.max_steps} | loss={loss_val:.4f} | lr={new_lr:.2e} | elapsed={elapsed:.0f}s")

            if step % cfg.save_every == 0:
                ckpt = os.path.join(cfg.output_dir, f"redrafter_qwen25-7b_step{step}.pt")
                if TPU_AVAILABLE:
                    xm.rendezvous("save")
                    xm.save({k: v.cpu() for k, v in draft_head.state_dict().items()}, ckpt)
                else:
                    torch.save(draft_head.state_dict(), ckpt)
                logger.info(f"Saved: {ckpt}")

    final = os.path.join(cfg.output_dir, "redrafter_qwen25-7b_final.pt")
    if TPU_AVAILABLE:
        xm.rendezvous("final")
        xm.save({k: v.cpu() for k, v in draft_head.state_dict().items()}, final)
    else:
        torch.save(draft_head.state_dict(), final)

    logger.info(f"Done in {(time.time()-start)/60:.1f} min. Saved: {final}")


if __name__ == "__main__":
    train()
