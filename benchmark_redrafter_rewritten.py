
#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
import time
from dataclasses import dataclass, field

import torch
import torch.nn as nn
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    PreTrainedTokenizerBase,
)

# --- Inlined content from src/momo_akira/models/redrafter.py ---
@dataclass
class DrafterConfig:
    vocab_size: int = 151665
    llm_hidden_size: int = 3584
    drafter_hidden_size: int = 1024
    num_gru_layers: int = 4

    @classmethod
    def from_state_dict(cls, sd: dict[str, torch.Tensor]) -> "DrafterConfig":
        vocab_size = int(sd["token_embed.weight"].shape[0])
        drafter_hidden = int(sd["token_embed.weight"].shape[1])
        llm_hidden = int(sd["input_proj.weight"].shape[1])
        num_layers = sum(1 for k in sd if k.startswith("gru.weight_ih_l"))
        return cls(
            vocab_size=vocab_size,
            llm_hidden_size=llm_hidden,
            drafter_hidden_size=drafter_hidden,
            num_gru_layers=num_layers,
        )


class DrafterHead(nn.Module):
    def __init__(self, cfg: DrafterConfig) -> None:
        super().__init__()
        self.cfg = cfg
        self.input_proj = nn.Linear(cfg.llm_hidden_size, cfg.drafter_hidden_size, bias=True)
        self.layer_norm = nn.LayerNorm(cfg.drafter_hidden_size)
        self.token_embed = nn.Embedding(cfg.vocab_size, cfg.drafter_hidden_size)
        self.gru = nn.GRU(
            input_size=cfg.drafter_hidden_size,
            hidden_size=cfg.drafter_hidden_size,
            num_layers=cfg.num_gru_layers,
            batch_first=True,
        )
        self.output_proj = nn.Linear(cfg.drafter_hidden_size, cfg.vocab_size, bias=False)

    @torch.no_grad()
    def init_state(self, llm_hidden: torch.Tensor) -> torch.Tensor:
        if llm_hidden.dim() == 1:
            llm_hidden = llm_hidden.unsqueeze(0)
        h0 = self.layer_norm(self.input_proj(llm_hidden))
        state = torch.zeros(
            self.cfg.num_gru_layers, 1, self.cfg.drafter_hidden_size,
            dtype=h0.dtype, device=h0.device,
        )
        state[0] = h0
        return state

    @torch.no_grad()
    def draft(
        self,
        llm_hidden: torch.Tensor,
        last_token_id: int,
        n_draft: int,
    ) -> list[int]:
        device = llm_hidden.device
        gru_h = self.init_state(llm_hidden)
        prev = torch.tensor([[last_token_id]], device=device, dtype=torch.long)
        out_ids: list[int] = []
        for _ in range(n_draft):
            x = self.token_embed(prev)
            out, gru_h = self.gru(x, gru_h)
            logits = self.output_proj(out[:, -1, :])
            nxt = int(logits.argmax(dim=-1).item())
            out_ids.append(nxt)
            prev = torch.tensor([[nxt]], device=device, dtype=torch.long)
        return out_ids


@dataclass
class ReDrafterMetrics:
    prompt_tokens: int = 0
    generated_tokens: int = 0
    drafter_proposed: int = 0
    drafter_accepted: int = 0
    verifier_calls: int = 0
    elapsed_s: float = 0.0
    per_step_accepts: list[int] = field(default_factory=list)

    @property
    def acceptance_rate(self) -> float:
        return (
            self.drafter_accepted / self.drafter_proposed
            if self.drafter_proposed
            else 0.0
        )

    @property
    def tokens_per_sec(self) -> float:
        return self.generated_tokens / self.elapsed_s if self.elapsed_s else 0.0

    @property
    def avg_accepted_per_step(self) -> float:
        return (
            sum(self.per_step_accepts) / len(self.per_step_accepts)
            if self.per_step_accepts
            else 0.0
        )

    def as_dict(self) -> dict[str, float | int]:
        return {
            "prompt_tokens": self.prompt_tokens,
            "generated_tokens": self.generated_tokens,
            "drafter_proposed": self.drafter_proposed,
            "drafter_accepted": self.drafter_accepted,
            "acceptance_rate": round(self.acceptance_rate, 4),
            "verifier_calls": self.verifier_calls,
            "avg_accepted_per_step": round(self.avg_accepted_per_step, 3),
            "elapsed_s": round(self.elapsed_s, 3),
            "tokens_per_sec": round(self.tokens_per_sec, 2),
        }


class ReDrafterModel:
    def __init__(
        self,
        base_model_name: str = "Qwen/Qwen2.5-7B-Instruct",
        drafter_path: str | Path = "redrafter_final.pt",
        device: str | None = None,
        dtype: torch.dtype = torch.float16,
    ) -> None:
        self.base_model_name = base_model_name
        self.drafter_path = Path(drafter_path)
        self.device = device or self._best_device()
        self.dtype = dtype if self.device != "cpu" else torch.float32

        self.tokenizer: PreTrainedTokenizerBase = AutoTokenizer.from_pretrained(
            base_model_name, trust_remote_code=True
        )
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        self.model = AutoModelForCausalLM.from_pretrained(
            base_model_name,
            torch_dtype=self.dtype,
            low_cpu_mem_usage=True,
            trust_remote_code=True,
        ).to(self.device)
        self.model.eval()

        sd = torch.load(self.drafter_path, map_location="cpu", weights_only=False)
        if hasattr(sd, "state_dict"):
            sd = sd.state_dict()
        self.drafter_cfg = DrafterConfig.from_state_dict(sd)
        base_hidden = int(self.model.config.hidden_size)
        if self.drafter_cfg.llm_hidden_size != base_hidden:
            raise RuntimeError(
                f"Drafter expects llm hidden_size={self.drafter_cfg.llm_hidden_size} "
                f"but base model has hidden_size={base_hidden}. "
                "Did you load the wrong base model?"
            )
        self.drafter = DrafterHead(self.drafter_cfg).to(self.device, dtype=self.dtype)
        missing, unexpected = self.drafter.load_state_dict(sd, strict=False)
        if missing:
            print(f"[redrafter] WARNING missing keys: {missing}")
        if unexpected:
            print(f"[redrafter] WARNING unexpected keys: {unexpected}")
        self.drafter.eval()

    @staticmethod
    def _best_device() -> str:
        if torch.backends.mps.is_available():
            return "mps"
        if torch.cuda.is_available():
            return "cuda"
        return "cpu"

    @torch.no_grad()
    def _verifier_forward(
        self, input_ids: torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor]:
        out = self.model(
            input_ids=input_ids,
            output_hidden_states=True,
            use_cache=False,
        )
        return out.logits, out.hidden_states[-1]

    @torch.no_grad()
    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 128,
        n_draft: int = 5,
        chat: bool = True,
    ) -> tuple[str, ReDrafterMetrics]:
        if chat and getattr(self.tokenizer, "chat_template", None):
            text = self.tokenizer.apply_chat_template(
                [{"role": "user", "content": prompt}],
                tokenize=False,
                add_generation_prompt=True,
            )
        else:
            text = prompt

        ids = self.tokenizer(text, return_tensors="pt").input_ids.to(self.device)
        prompt_len = int(ids.shape[1])
        eos_id = self.tokenizer.eos_token_id
        vocab_drafter = self.drafter_cfg.vocab_size

        metrics = ReDrafterMetrics(prompt_tokens=prompt_len)
        t0 = time.perf_counter()

        logits, hidden = self._verifier_forward(ids)
        metrics.verifier_calls += 1
        next_id = int(logits[0, -1].argmax().item())
        ids = torch.cat([ids, torch.tensor([[next_id]], device=self.device)], dim=1)
        metrics.generated_tokens += 1
        last_hidden = hidden[0, -1]

        while metrics.generated_tokens < max_new_tokens:
            if next_id == eos_id:
                break

            safe_prev = next_id if next_id < vocab_drafter else 0
            drafts = self.drafter.draft(last_hidden, safe_prev, n_draft)
            metrics.drafter_proposed += len(drafts)

            draft_tensor = torch.tensor([drafts], device=self.device, dtype=torch.long)
            verify_input = torch.cat([ids, draft_tensor], dim=1)
            logits, hidden = self._verifier_forward(verify_input)
            metrics.verifier_calls += 1

            base = ids.shape[1] - 1

            accepted = 0
            for i, d in enumerate(drafts):
                pred = int(logits[0, base + i].argmax().item())
                if pred == d:
                    accepted += 1
                    if metrics.generated_tokens + accepted >= max_new_tokens:
                        break
                    if d == eos_id:
                        break
                else:
                    break

            metrics.drafter_accepted += accepted
            metrics.per_step_accepts.append(accepted)

            bonus_pos = base + accepted
            bonus_id = int(logits[0, bonus_pos].argmax().item())

            new_tokens = drafts[:accepted] + [bonus_id]
            remaining = max_new_tokens - metrics.generated_tokens
            new_tokens = new_tokens[:remaining]
            ids = torch.cat(
                [ids, torch.tensor([new_tokens], device=self.device, dtype=torch.long)],
                dim=1,
            )
            metrics.generated_tokens += len(new_tokens)
            next_id = new_tokens[-1]

            last_hidden = hidden[0, bonus_pos]

            if eos_id in new_tokens:
                break

        metrics.elapsed_s = time.perf_counter() - t0

        gen_ids = ids[0, prompt_len:].tolist()
        text_out = self.tokenizer.decode(gen_ids, skip_special_tokens=True)
        return text_out, metrics

    @torch.no_grad()
    def generate_baseline(
        self,
        prompt: str,
        max_new_tokens: int = 128,
        chat: bool = True,
    ) -> tuple[str, ReDrafterMetrics]:
        if chat and getattr(self.tokenizer, "chat_template", None):
            text = self.tokenizer.apply_chat_template(
                [{"role": "user", "content": prompt}],
                tokenize=False,
                add_generation_prompt=True,
            )
        else:
            text = prompt

        ids = self.tokenizer(text, return_tensors="pt").input_ids.to(self.device)
        prompt_len = int(ids.shape[1])
        metrics = ReDrafterMetrics(prompt_tokens=prompt_len)
        t0 = time.perf_counter()

        out_ids = self.model.generate(
            ids,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=self.tokenizer.eos_token_id,
        )
        metrics.elapsed_s = time.perf_counter() - t0
        metrics.generated_tokens = int(out_ids.shape[1]) - prompt_len
        text_out = self.tokenizer.decode(
            out_ids[0, prompt_len:], skip_special_tokens=True
        )
        return text_out, metrics


# --- Inlined content from src/momo_akira/decoding/redrafter_engine.py ---
@dataclass
class ReDrafterRunResult:
    prompt: str
    text: str
    metrics: ReDrafterMetrics
    baseline_metrics: ReDrafterMetrics | None = None

    @property
    def speedup(self) -> float | None:
        if self.baseline_metrics is None or self.baseline_metrics.tokens_per_sec == 0:
            return None
        return self.metrics.tokens_per_sec / self.baseline_metrics.tokens_per_sec


class ReDrafterEngine:
    def __init__(
        self,
        base_model_name: str = "Qwen/Qwen2.5-7B-Instruct",
        drafter_path: str | Path = "redrafter_final.pt",
        device: str | None = None,
        n_draft: int = 5,
    ) -> None:
        self.n_draft = n_draft
        self.model = ReDrafterModel(
            base_model_name=base_model_name,
            drafter_path=drafter_path,
            device=device,
        )

    @property
    def device(self) -> str:
        return self.model.device

    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 128,
        n_draft: int | None = None,
        compare_baseline: bool = False,
        chat: bool = True,
    ) -> ReDrafterRunResult:
        text, metrics = self.model.generate(
            prompt,
            max_new_tokens=max_new_tokens,
            n_draft=n_draft or self.n_draft,
            chat=chat,
        )
        baseline = None
        if compare_baseline:
            _, baseline = self.model.generate_baseline(
                prompt, max_new_tokens=max_new_tokens, chat=chat
            )
        return ReDrafterRunResult(
            prompt=prompt, text=text, metrics=metrics, baseline_metrics=baseline
        )

    def benchmark(
        self,
        prompts: list[str],
        max_new_tokens: int = 128,
        n_draft: int | None = None,
        compare_baseline: bool = True,
        chat: bool = True,
    ) -> list[ReDrafterRunResult]:
        return [
            self.generate(
                p,
                max_new_tokens=max_new_tokens,
                n_draft=n_draft,
                compare_baseline=compare_baseline,
                chat=chat,
            )
            for p in prompts
        ]


# --- Original benchmark logic from scripts/benchmark_redrafter.py ---
PROMPTS = [
    "Write a short Python function that returns the nth Fibonacci number.",
    "Explain the difference between speculative decoding and beam search.",
    "Summarize the plot of Hamlet in three sentences.",
    "List five things to do in Reston, Virginia on a rainy Saturday.",
    "Translate the sentence 'The quick brown fox jumps over the lazy dog' into French.",
]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--base", default="Qwen/Qwen2.5-7B-Instruct",
                   help="Base LLM. Drafter head requires hidden_size=3584 (Qwen2.5-7B).")
    p.add_argument("--drafter", default=str(Path(__file__).parent / "redrafter_final.pt"))
    p.add_argument("--max-new-tokens", type=int, default=96)
    p.add_argument("--n-draft", type=int, default=5)
    p.add_argument("--no-baseline", action="store_true",
                   help="Skip vanilla baseline comparison (faster).")
    p.add_argument("--json", action="store_true", help="Emit JSON summary.")
    args = p.parse_args()

    # Note: the original script had ROOT / "redrafter_final.pt". Here we assume
    # redrafter_final.pt is in the same directory as this script, or explicitly
    # point to it if it's elsewhere.
    # For this self-contained script, we'll try to find it relative to the script.
    drafter_path_abs = Path(__file__).resolve().parent / Path(args.drafter).name
    if not drafter_path_abs.exists():
        print(f"[bench] WARNING: Drafter checkpoint not found at {drafter_path_abs}. "
              "Using a dummy drafter (will result in 0% acceptance rate). ", file=sys.stderr)
        # Fallback to creating a dummy for testing the pipeline, similar to test_redrafter.py
        with tempfile.NamedTemporaryFile(suffix=".pt", delete=False) as f:
            create_dummy_drafter_for_7b(Path(f.name))
            drafter_path_abs = Path(f.name)

    engine = ReDrafterEngine(
        base_model_name=args.base,
        drafter_path=drafter_path_abs,
        n_draft=args.n_draft,
    )
    print(f"[bench] base    : {args.base}")
    print(f"[bench] device  : {engine.device}")
    print(f"[bench] drafter : {engine.model.drafter_cfg}")
    print(f"[bench] n_draft : {args.n_draft}")
    print(f"[bench] max_new : {args.max_new_tokens}")
    print()

    results = engine.benchmark(
        PROMPTS,
        max_new_tokens=args.max_new_tokens,
        compare_baseline=not args.no_baseline,
    )

    summary: list[dict] = []
    total_redraft_tps = 0.0
    total_baseline_tps = 0.0
    total_accept_num = 0
    total_accept_den = 0

    for i, r in enumerate(results, 1):
        m = r.metrics
        total_accept_num += m.drafter_accepted
        total_accept_den += m.drafter_proposed
        total_redraft_tps += m.tokens_per_sec
        baseline_tps = r.baseline_metrics.tokens_per_sec if r.baseline_metrics else 0.0
        total_baseline_tps += baseline_tps
        speedup = r.speedup
        print(f"--- Prompt {i} ---")
        print(f"  prompt       : {r.prompt[:70]}{'...' if len(r.prompt) > 70 else ''}")
        print(f"  generated    : {r.text[:120]}{'...' if len(r.text) > 120 else ''}")
        print(f"  tokens       : {m.generated_tokens}")
        print(f"  redrafter t/s: {m.tokens_per_sec:.2f}")
        if r.baseline_metrics is not None:
            print(f"  baseline t/s : {baseline_tps:.2f}")
            if speedup is not None:
                print(f"  speedup      : {speedup:.2f}x")
        print(f"  accept rate  : {m.acceptance_rate:.2%} "
              f"({m.drafter_accepted}/{m.drafter_proposed})")
        print(f"  avg accepted : {m.avg_accepted_per_step:.2f} per step")
        print()
        summary.append({
            "prompt": r.prompt,
            "metrics": m.as_dict(),
            "baseline": r.baseline_metrics.as_dict() if r.baseline_metrics else None,
            "speedup": speedup,
        })

    n = len(results)
    overall_accept = (total_accept_num / total_accept_den) if total_accept_den else 0.0
    print("=== Overall ===")
    print(f"  prompts             : {n}")
    print(f"  avg redrafter t/s   : {total_redraft_tps / n:.2f}")
    if not args.no_baseline:
        print(f"  avg baseline t/s    : {total_baseline_tps / n:.2f}")
        if total_baseline_tps > 0:
            print(f"  avg speedup         : {(total_redraft_tps / total_baseline_tps):.2f}x")
    print(f"  overall accept rate : {overall_accept:.2%}")

    if args.json:
        print(json.dumps({"runs": summary, "overall_accept_rate": overall_accept}, indent=2))

    return 0


def create_dummy_drafter_for_7b(path: Path) -> None:
    """Create and save a dummy drafter head for Qwen2.5-7B-Instruct."""
    # Qwen-7B has hidden_size=3584, vocab_size=151665
    cfg = DrafterConfig(
        vocab_size=151665,
        llm_hidden_size=3584,  # This is the key change for 7B
        drafter_hidden_size=1024,
        num_gru_layers=4,
    )
    dummy_head = DrafterHead(cfg)
    torch.save(dummy_head.state_dict(), path)
    print(f"[bench] Created dummy drafter for 7B model at {path}", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
