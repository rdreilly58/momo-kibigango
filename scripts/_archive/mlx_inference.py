#!/usr/bin/env python3
"""
mlx_inference.py — MLX-LM local inference helper for M4 Max.

Replaces Ollama (hangs on M4 Max, issue #41871) with the MLX backend,
which has native Apple Silicon support and no hang issues.

Usage (module):
    from mlx_inference import generate, MLXClient

    # Simple one-shot generation
    result = generate("Explain what MLX is", model="qwen2.5-7b")

    # Ollama-compatible client (drop-in for scripts that used requests to Ollama)
    client = MLXClient()
    result = client.generate(model="mistral", prompt="Hello")

Usage (CLI):
    python3 mlx_inference.py "your prompt here" [--model qwen2.5-7b] [--max-tokens 512]
    python3 mlx_inference.py --list-models

Model aliases (map Ollama names → MLX HF cache paths):
    mistral        → mlx-community/Qwen2.5-7B-Instruct-4bit  (closest capable replacement)
    qwen2.5        → mlx-community/Qwen2.5-7B-Instruct-4bit
    qwen2.5-7b     → mlx-community/Qwen2.5-7B-Instruct-4bit
    qwen2.5-3b     → mlx-community/Qwen2.5-3B-Instruct-4bit
    qwen2.5-small  → mlx-community/Qwen2.5-1.5B-Instruct-4bit
    qwen2.5-tiny   → mlx-community/Qwen2.5-0.5B-Instruct-4bit
    phi            → mlx-community/Qwen2.5-3B-Instruct-4bit   (phi not in MLX cache)
    default        → mlx-community/Qwen2.5-7B-Instruct-4bit
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Optional

# ── Bootstrap MLX from Homebrew Python 3.14 site-packages ──────────────────
_MLX_SITE = Path("/opt/homebrew/lib/python3.14/site-packages")
if _MLX_SITE.exists() and str(_MLX_SITE) not in sys.path:
    sys.path.insert(0, str(_MLX_SITE))

# ── Model registry ────────────────────────────────────────────────────────────

_HF_HUB = Path.home() / ".cache" / "huggingface" / "hub"

# Map alias → HF hub snapshot path (resolved at runtime)
_MODEL_ALIASES: dict[str, str] = {
    "mistral":        "mlx-community/Qwen2.5-7B-Instruct-4bit",
    "qwen2.5":        "mlx-community/Qwen2.5-7B-Instruct-4bit",
    "qwen2.5-7b":     "mlx-community/Qwen2.5-7B-Instruct-4bit",
    "qwen7b":         "mlx-community/Qwen2.5-7B-Instruct-4bit",
    "qwen2.5-coder":  "mlx-community/Qwen2.5-7B-Instruct-4bit",
    "qwen2.5-3b":     "mlx-community/Qwen2.5-3B-Instruct-4bit",
    "qwen2.5-small":  "mlx-community/Qwen2.5-1.5B-Instruct-4bit",
    "qwen2.5-1.5b":   "mlx-community/Qwen2.5-1.5B-Instruct-4bit",
    "qwen2.5-tiny":   "mlx-community/Qwen2.5-0.5B-Instruct-4bit",
    "qwen2.5-0.5b":   "mlx-community/Qwen2.5-0.5B-Instruct-4bit",
    "phi":            "mlx-community/Qwen2.5-3B-Instruct-4bit",
    "localqwen":      "mlx-community/Qwen2-7B-4bit",
    "default":        "mlx-community/Qwen2.5-7B-Instruct-4bit",
}


def _resolve_model_path(alias: str) -> str:
    """Resolve alias → HF repo ID or local snapshot path."""
    # Already a HF repo ID or absolute path
    if "/" in alias or alias.startswith("/"):
        return alias

    repo_id = _MODEL_ALIASES.get(alias.lower(), _MODEL_ALIASES["default"])

    # Try to find a local snapshot so we don't hit the network
    cache_name = "models--" + repo_id.replace("/", "--")
    snapshot_root = _HF_HUB / cache_name / "snapshots"
    if snapshot_root.exists():
        snapshots = sorted(snapshot_root.iterdir())
        if snapshots:
            return str(snapshots[-1])  # latest snapshot

    # Fall back to HF repo ID (will download on first use)
    return repo_id


def list_available_models() -> list[dict]:
    """Return locally cached MLX models."""
    models = []
    if not _HF_HUB.exists():
        return models
    for d in sorted(_HF_HUB.iterdir()):
        if d.name.startswith("models--mlx-community--"):
            name = d.name.replace("models--mlx-community--", "mlx-community/")
            snapshots = list((d / "snapshots").glob("*")) if (d / "snapshots").exists() else []
            models.append({
                "name": name,
                "cached": len(snapshots) > 0,
                "path": str(snapshots[-1]) if snapshots else None,
            })
    return models


# ── Model cache (avoid reloading the same model repeatedly) ──────────────────

_model_cache: dict[str, tuple] = {}  # path → (model, tokenizer)


def _load(model_path: str):
    """Load model+tokenizer, with in-process caching."""
    if model_path in _model_cache:
        return _model_cache[model_path]

    try:
        import mlx_lm  # type: ignore
    except ImportError as e:
        raise ImportError(
            "mlx_lm not found. Install via: pip install mlx-lm"
        ) from e

    model, tokenizer = mlx_lm.load(model_path)
    _model_cache[model_path] = (model, tokenizer)
    return model, tokenizer


# ── Core generate function ────────────────────────────────────────────────────

def generate(
    prompt: str,
    model: str = "default",
    max_tokens: int = 512,
    temperature: float = 0.7,
    system_prompt: Optional[str] = None,
    verbose: bool = False,
) -> str:
    """
    Generate text from a local MLX model.

    Args:
        prompt:        User prompt text.
        model:         Model alias (e.g. "mistral", "qwen2.5-7b") or HF repo ID.
        max_tokens:    Maximum tokens to generate.
        temperature:   Sampling temperature (0 = deterministic).
        system_prompt: Optional system message prepended via chat template.
        verbose:       Stream tokens to stderr while generating.

    Returns:
        Generated text as a string.
    """
    import mlx_lm  # type: ignore

    model_path = _resolve_model_path(model)
    mlx_model, tokenizer = _load(model_path)

    # Apply chat template if available
    if system_prompt or hasattr(tokenizer, "apply_chat_template"):
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        try:
            formatted = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
        except Exception:
            formatted = prompt
    else:
        formatted = prompt

    result = mlx_lm.generate(
        mlx_model,
        tokenizer,
        prompt=formatted,
        max_tokens=max_tokens,
        verbose=verbose,
        temp=temperature,
    )
    return result


# ── Ollama-compatible client (drop-in replacement) ───────────────────────────

class MLXClient:
    """
    Drop-in replacement for scripts that called the Ollama HTTP API.

    Old (Ollama):
        import requests
        r = requests.post("http://localhost:11434/api/generate",
                          json={"model": "mistral", "prompt": "...", "stream": False})
        text = r.json()["response"]

    New (MLX):
        from mlx_inference import MLXClient
        client = MLXClient()
        text = client.generate(model="mistral", prompt="...")["response"]
    """

    def generate(
        self,
        model: str = "default",
        prompt: str = "",
        system: str = "",
        max_tokens: int = 512,
        temperature: float = 0.7,
        stream: bool = False,
    ) -> dict:
        """Return dict matching Ollama /api/generate response shape."""
        t0 = time.time()
        text = generate(
            prompt=prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system_prompt=system or None,
        )
        elapsed = time.time() - t0
        return {
            "model": model,
            "response": text,
            "done": True,
            "total_duration": int(elapsed * 1e9),
            "backend": "mlx",
        }

    def chat(
        self,
        model: str = "default",
        messages: list[dict] | None = None,
        max_tokens: int = 512,
        temperature: float = 0.7,
    ) -> dict:
        """Return dict matching Ollama /api/chat response shape."""
        messages = messages or []
        system = next(
            (m["content"] for m in messages if m.get("role") == "system"), ""
        )
        user = next(
            (m["content"] for m in reversed(messages) if m.get("role") == "user"), ""
        )
        text = generate(
            prompt=user,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system_prompt=system or None,
        )
        return {
            "model": model,
            "message": {"role": "assistant", "content": text},
            "done": True,
            "backend": "mlx",
        }


# ── CLI ───────────────────────────────────────────────────────────────────────

def _cli():
    p = argparse.ArgumentParser(description="MLX local inference (M4 Max)")
    p.add_argument("prompt", nargs="?", default="", help="Prompt text")
    p.add_argument("--model", "-m", default="default", help="Model alias or HF repo ID")
    p.add_argument("--max-tokens", type=int, default=512)
    p.add_argument("--temperature", type=float, default=0.7)
    p.add_argument("--system", default="", help="System prompt")
    p.add_argument("--list-models", action="store_true", help="List cached MLX models")
    p.add_argument("--json", dest="as_json", action="store_true", help="Output JSON")
    args = p.parse_args()

    if args.list_models:
        models = list_available_models()
        if args.as_json:
            print(json.dumps(models, indent=2))
        else:
            print(f"{'Model':<45} {'Cached':<8}")
            print("-" * 55)
            for m in models:
                print(f"{m['name']:<45} {'✅' if m['cached'] else '❌':<8}")
            print(f"\nAliases: {', '.join(sorted(_MODEL_ALIASES.keys()))}")
        return

    if not args.prompt:
        p.print_help()
        return

    result = generate(
        prompt=args.prompt,
        model=args.model,
        max_tokens=args.max_tokens,
        temperature=args.temperature,
        system_prompt=args.system or None,
        verbose=not args.as_json,
    )

    if args.as_json:
        print(json.dumps({"response": result, "model": args.model, "backend": "mlx"}))
    else:
        print(result)


if __name__ == "__main__":
    _cli()
