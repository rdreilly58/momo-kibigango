#!/usr/bin/env python3
"""
ReDrafter Training Script — TPU v6e-1
Trains a small RNN draft head for Qwen2.5-7B using Apple's ReDrafter approach.
Adapted from Apple arxiv:2403.09919 for TPU v6e via PyTorch/XLA.

Target: Google Cloud TPU v6e-1 (Trillium)
  - 1 chip, 16GB HBM2e
  - bfloat16 native
  - ~3x faster than A100 for this workload

Usage:
  # On TPU VM:
  pip install torch torch_xla[tpu] transformers datasets accelerate
  python train_drafter_tpu_v6e.py

  # Or via gcloud:
  gcloud compute tpus tpu-vm ssh <TPU_NAME> --zone=<ZONE> \
    --command="python train_drafter_tpu_v6e.py"
"""

import os
import gc
import time
import logging
import math
from dataclasses import dataclass, field
from typing import Optional, List

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim import AdamW
from torch.utils.data import DataLoader, Dataset

# TPU/XLA imports — gracefully fall back to CPU for local testing
try:
    import torch_xla.core.xla_model as xm
    import torch_xla.distributed.parallel_loader as pl
    import torch_xla.distributed.xla_backend  # noqa: F401
    TPU_AVAILABLE = True
    print("✅ TPU/XLA available")
except ImportError:
    TPU_AVAILABLE = False
    print("⚠️  torch_xla not found — running on CPU (testing mode)")

from transformers import AutoTokenizer, AutoModelForCausalLM
from datasets import load_dataset

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

@dataclass
class TrainingConfig:
    # Model
    base_model: str = "Qwen/Qwen2.5-7B-Instruct"
    drafter_hidden_size: int = 512
    drafter_num_layers: int = 2
    num_draft_tokens: int = 4          # How many tokens to draft at once

    # Data
    dataset_name: str = "anon8231489123/ShareGPT_Vicuna_unfiltered"
    dataset_split: str = "train"
    max_seq_len: int = 512             # Reduced from 2048 (OOM fix — proven on A100)
    max_samples: int = 5_000           # Small subset for quick validation

    # Training
    batch_size: int = 2                # Reduced for faster CPU base model inference
    grad_accumulation_steps: int = 4   # Effective batch = 32
    learning_rate: float = 2e-4
    weight_decay: float = 0.01
    warmup_steps: int = 200
    max_steps: int = 3000
    save_every: int = 500
    log_every: int = 10

    # Optimizer — 8-bit Adam not available on TPU; use standard AdamW with bfloat16
    dtype: torch.dtype = torch.bfloat16  # v6e native dtype

    # Paths
    output_dir: str = "./drafter_output_tpu"
    checkpoint_prefix: str = "redrafter_qwen25-7b_tpu"


CONFIG = TrainingConfig()


# ---------------------------------------------------------------------------
# Draft Head (ReDrafter architecture)
# Lightweight RNN that proposes K draft tokens given the last hidden state
# ---------------------------------------------------------------------------

class ReDrafterHead(nn.Module):
    """
    Apple ReDrafter draft head.
    Takes the last hidden state from the base model and autoregressively
    proposes `num_draft_tokens` candidate tokens.

    Input:  hidden_state [B, H]  (last token's hidden state from base model)
    Output: draft_logits [B, K, V]  (logits for K draft positions)
    """

    def __init__(
        self,
        vocab_size: int,
        hidden_size: int,         # base model hidden dim (e.g. 3584 for Qwen2.5-7B)
        drafter_hidden: int = 512,
        num_layers: int = 2,
        num_draft_tokens: int = 4,
    ):
        super().__init__()
        self.num_draft_tokens = num_draft_tokens
        self.drafter_hidden = drafter_hidden

        # Project base model hidden state → drafter hidden
        self.input_proj = nn.Linear(hidden_size, drafter_hidden)

        # GRU for autoregressive drafting
        self.gru = nn.GRU(
            input_size=drafter_hidden,
            hidden_size=drafter_hidden,
            num_layers=num_layers,
            batch_first=True,
        )

        # Token embedding for feeding predicted tokens back in
        self.token_embed = nn.Embedding(vocab_size, drafter_hidden)

        # Output projection to vocabulary
        self.output_proj = nn.Linear(drafter_hidden, vocab_size, bias=False)

        self._init_weights()

    def _init_weights(self):
        nn.init.xavier_uniform_(self.input_proj.weight)
        nn.init.zeros_(self.input_proj.bias)
        nn.init.xavier_uniform_(self.output_proj.weight)

    def forward(
        self,
        hidden_state: torch.Tensor,   # [B, H_base]
        target_ids: Optional[torch.Tensor] = None,  # [B, K] for teacher forcing
    ) -> torch.Tensor:
        """
        Returns draft logits [B, K, V].
        Uses teacher forcing during training (target_ids provided),
        greedy sampling during inference.
        """
        B = hidden_state.size(0)

        # Project base hidden → drafter hidden; use as initial GRU hidden state
        h0 = self.input_proj(hidden_state)  # [B, D]
        h0 = h0.unsqueeze(0).expand(self.gru.num_layers, -1, -1).contiguous()  # [L, B, D]

        all_logits = []

        # Start token = zero embedding (no BOS needed for draft head)
        x = torch.zeros(B, self.drafter_hidden, device=hidden_state.device, dtype=hidden_state.dtype)
        h = h0

        for step in range(self.num_draft_tokens):
            out, h = self.gru(x.unsqueeze(1), h)  # out: [B, 1, D]
            logits = self.output_proj(out.squeeze(1))  # [B, V]
            all_logits.append(logits)

            if target_ids is not None:
                # Teacher forcing: feed ground truth token embedding
                x = self.token_embed(target_ids[:, step])
            else:
                # Greedy inference
                x = self.token_embed(logits.argmax(dim=-1))

        return torch.stack(all_logits, dim=1)  # [B, K, V]


# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------

class ShareGPTDataset(Dataset):
    """
    Tokenizes ShareGPT conversations and returns input_ids for LM training.
    Each sample is a random window of max_seq_len tokens from a conversation.
    """

    def __init__(self, tokenizer, max_seq_len: int = 512, max_samples: int = 50_000):
        self.tokenizer = tokenizer
        self.max_seq_len = max_seq_len

        logger.info(f"Loading ShareGPT dataset (max {max_samples} samples)...")
        ds = load_dataset(
            "anon8231489123/ShareGPT_Vicuna_unfiltered",
            data_files="ShareGPT_V3_unfiltered_cleaned_split.json",
            split="train",
        )

        self.samples = []
        for row in ds.select(range(min(max_samples, len(ds)))):
            text = " ".join(
                turn.get("value", "") for turn in row.get("conversations", [])
            )
            if len(text) < 100:
                continue
            ids = tokenizer(
                text,
                truncation=True,
                max_length=max_seq_len + 1,
                return_tensors="pt",
            ).input_ids.squeeze(0)
            if len(ids) >= 8:
                self.samples.append(ids)

        logger.info(f"Dataset ready: {len(self.samples)} samples")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        return self.samples[idx]


def collate_fn(batch):
    """Pad batch to same length."""
    max_len = max(x.size(0) for x in batch)
    padded = torch.zeros(len(batch), max_len, dtype=torch.long)
    for i, x in enumerate(batch):
        padded[i, :x.size(0)] = x
    return padded


# ---------------------------------------------------------------------------
# Loss
# ---------------------------------------------------------------------------

def compute_drafter_loss(
    draft_logits: torch.Tensor,   # [B, K, V]
    target_ids: torch.Tensor,     # [B, K]
    vocab_size: int,
) -> torch.Tensor:
    """
    Cross-entropy loss between draft predictions and ground truth tokens.
    Memory-efficient: compute one position at a time to avoid [B*K, V] tensor.
    """
    total_loss = torch.tensor(0.0, device=draft_logits.device, dtype=draft_logits.dtype)
    K = draft_logits.size(1)

    for k in range(K):
        logits_k = draft_logits[:, k, :].float()  # [B, V] — upcast for numerical stability
        targets_k = target_ids[:, k]               # [B]
        loss_k = F.cross_entropy(logits_k, targets_k, ignore_index=0)
        total_loss = total_loss + loss_k

    return total_loss / K


# ---------------------------------------------------------------------------
# LR Schedule (linear warmup + cosine decay)
# ---------------------------------------------------------------------------

def get_lr(step: int, warmup_steps: int, max_steps: int, lr: float) -> float:
    if step < warmup_steps:
        return lr * step / max(warmup_steps, 1)
    progress = (step - warmup_steps) / max(max_steps - warmup_steps, 1)
    return lr * 0.5 * (1 + math.cos(math.pi * progress))


# ---------------------------------------------------------------------------
# Main training loop
# ---------------------------------------------------------------------------

def train():
    cfg = CONFIG

    # Device setup
    if TPU_AVAILABLE:
        device = xm.xla_device()
        logger.info(f"Using TPU device: {device}")
    else:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {device}")

    os.makedirs(cfg.output_dir, exist_ok=True)

    # ---- Tokenizer ----
    logger.info(f"Loading tokenizer: {cfg.base_model}")
    tokenizer = AutoTokenizer.from_pretrained(cfg.base_model, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    vocab_size = len(tokenizer)
    logger.info(f"Vocab size: {vocab_size}")

    # ---- Base model (frozen, stays on CPU) ----
    # IMPORTANT: Keep base model on CPU. It's frozen and 14GB — putting it on
    # the 16GB TPU alongside the draft head would OOM. We run inference on CPU
    # and only transfer the last hidden state to TPU for the draft head.
    logger.info(f"Loading base model: {cfg.base_model} (frozen, CPU, bfloat16)")
    cpu_device = torch.device("cpu")
    base_model = AutoModelForCausalLM.from_pretrained(
        cfg.base_model,
        torch_dtype=cfg.dtype,
        device_map="cpu",
        trust_remote_code=True,
    )
    base_model.eval()
    for p in base_model.parameters():
        p.requires_grad_(False)
    logger.info("Base model loaded on CPU")

    # Get base model hidden size
    hidden_size = base_model.config.hidden_size
    logger.info(f"Base model hidden size: {hidden_size}")

    # ---- Draft head (trainable) ----
    logger.info("Initializing ReDrafter head...")
    draft_head = ReDrafterHead(
        vocab_size=vocab_size,
        hidden_size=hidden_size,
        drafter_hidden=cfg.drafter_hidden_size,
        num_layers=cfg.drafter_num_layers,
        num_draft_tokens=cfg.num_draft_tokens,
    ).to(device).to(cfg.dtype)

    num_params = sum(p.numel() for p in draft_head.parameters())
    logger.info(f"Draft head params: {num_params:,} ({num_params/1e6:.1f}M)")

    # ---- Dataset & DataLoader ----
    dataset = ShareGPTDataset(tokenizer, cfg.max_seq_len, cfg.max_samples)
    loader = DataLoader(
        dataset,
        batch_size=cfg.batch_size,
        shuffle=True,
        collate_fn=collate_fn,
        drop_last=True,
        num_workers=0,  # 0 required for TPU
    )

    if TPU_AVAILABLE:
        # Wrap loader for async TPU data prefetch
        loader = pl.MpDeviceLoader(loader, device)

    # ---- Optimizer ----
    # Note: BNB 8-bit Adam not available on TPU — use standard AdamW
    # bfloat16 training is stable on v6e without 8-bit optimizer
    optimizer = AdamW(
        draft_head.parameters(),
        lr=cfg.learning_rate,
        weight_decay=cfg.weight_decay,
        betas=(0.9, 0.95),
    )

    # ---- Training ----
    logger.info("Starting training...")
    step = 0
    optimizer.zero_grad()
    start_time = time.time()

    while step < cfg.max_steps:
        for batch in loader:
            if step >= cfg.max_steps:
                break

            # batch: [B, seq_len]
            if TPU_AVAILABLE:
                input_ids = batch
            else:
                input_ids = batch.to(device)

            # Build targets: shift by 1 per draft position
            # For position k, target is input_ids[:, k+1 : k+1+K]
            seq_len = input_ids.size(1)
            if seq_len < cfg.num_draft_tokens + 2:
                continue

            # Use a random start position for variety
            max_start = seq_len - cfg.num_draft_tokens - 1
            start = torch.randint(1, max(2, max_start), (1,)).item()

            context_ids = input_ids[:, :start]   # [B, start] — used on CPU
            target_ids  = input_ids[:, start:start + cfg.num_draft_tokens].to(device)  # [B, K] on TPU

            # Forward pass through frozen base model (on CPU) to get hidden state
            with torch.no_grad():
                cpu_context = context_ids.cpu()
                outputs = base_model(
                    input_ids=cpu_context,
                    output_hidden_states=True,
                    use_cache=False,
                )
                # Transfer only the small hidden state vector to TPU
                last_hidden = outputs.hidden_states[-1][:, -1, :].to(device)  # [B, H]

            # Forward pass through draft head
            draft_logits = draft_head(last_hidden, target_ids=target_ids)  # [B, K, V]

            # Loss
            loss = compute_drafter_loss(draft_logits, target_ids, vocab_size)
            loss = loss / cfg.grad_accumulation_steps
            loss.backward()

            if (step + 1) % cfg.grad_accumulation_steps == 0:
                # Update LR
                new_lr = get_lr(step, cfg.warmup_steps, cfg.max_steps, cfg.learning_rate)
                for pg in optimizer.param_groups:
                    pg["lr"] = new_lr

                if TPU_AVAILABLE:
                    xm.optimizer_step(optimizer)  # TPU: sync gradients across chips
                else:
                    optimizer.step()

                optimizer.zero_grad()

                if TPU_AVAILABLE:
                    xm.mark_step()  # Flush XLA graph

            step += 1

            # Logging
            if step % cfg.log_every == 0:
                elapsed = time.time() - start_time
                loss_val = loss.item() * cfg.grad_accumulation_steps
                logger.info(
                    f"step={step}/{cfg.max_steps} | loss={loss_val:.4f} | "
                    f"lr={new_lr:.2e} | elapsed={elapsed:.0f}s"
                )

            # Checkpoint
            if step % cfg.save_every == 0:
                ckpt_path = os.path.join(
                    cfg.output_dir, f"{cfg.checkpoint_prefix}_step{step}.pt"
                )
                if TPU_AVAILABLE:
                    # Ensure model is synced before saving
                    xm.rendezvous("checkpoint")
                    cpu_state = {k: v.cpu() for k, v in draft_head.state_dict().items()}
                    xm.save(cpu_state, ckpt_path)
                else:
                    torch.save(draft_head.state_dict(), ckpt_path)
                logger.info(f"Saved checkpoint: {ckpt_path}")

    # Final save
    final_path = os.path.join(cfg.output_dir, f"{cfg.checkpoint_prefix}_final.pt")
    if TPU_AVAILABLE:
        xm.rendezvous("final_save")
        xm.save({k: v.cpu() for k, v in draft_head.state_dict().items()}, final_path)
    else:
        torch.save(draft_head.state_dict(), final_path)

    total_time = time.time() - start_time
    logger.info(f"Training complete in {total_time/60:.1f} min. Saved: {final_path}")


if __name__ == "__main__":
    train()
