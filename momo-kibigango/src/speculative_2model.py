#!/usr/bin/env python3
"""
Phase 2: 2-Model Speculative Decoding Implementation
Project: momo-kibigango
Created: March 19, 2026

This module implements a 2-model speculative decoding pipeline with:
- Draft model: Phi-2 (2.7B parameters)
- Target model: Qwen2-7B-4bit (existing)
"""

import os
import time
import json
import torch
import psutil
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers import BitsAndBytesConfig
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class SpeculativeConfig:
    """Configuration for 2-model speculative decoding"""
    draft_model_id: str = "microsoft/phi-2"  # Fast draft model
    target_model_id: str = "Qwen/Qwen2-7B"  # Target model
    draft_tokens: int = 5  # Number of tokens to generate speculatively
    max_tokens: int = 512  # Maximum generation length
    temperature: float = 0.7
    top_p: float = 0.9
    device: str = "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"
    load_in_4bit: bool = True  # Use 4-bit quantization
    max_memory_gb: float = 12.0  # Maximum VRAM usage


class MemoryMonitor:
    """Monitor VRAM/RAM usage during inference"""
    
    def __init__(self):
        self.process = psutil.Process()
        self.baseline_memory = self.get_memory_usage()
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage in GB"""
        memory_info = self.process.memory_info()
        return {
            "rss_gb": memory_info.rss / (1024 ** 3),
            "vms_gb": memory_info.vms / (1024 ** 3),
            "percent": self.process.memory_percent()
        }
    
    def get_delta(self) -> Dict[str, float]:
        """Get memory usage delta from baseline"""
        current = self.get_memory_usage()
        return {
            "rss_delta_gb": current["rss_gb"] - self.baseline_memory["rss_gb"],
            "current_rss_gb": current["rss_gb"],
            "percent": current["percent"]
        }


class Speculative2Model:
    """2-Model Speculative Decoding Pipeline"""
    
    def __init__(self, config: SpeculativeConfig):
        self.config = config
        self.memory_monitor = MemoryMonitor()
        self.draft_model = None
        self.target_model = None
        self.draft_tokenizer = None
        self.target_tokenizer = None
        self.stats = {
            "total_draft_tokens": 0,
            "accepted_tokens": 0,
            "rejection_points": [],
            "inference_times": []
        }
        
    def load_models(self):
        """Load both draft and target models"""
        logger.info("Loading models...")
        start_time = time.time()
        
        # Quantization config for 4-bit
        quantization_config = None
        if self.config.load_in_4bit:
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
            )
        
        # Load draft model (Phi-2)
        logger.info(f"Loading draft model: {self.config.draft_model_id}")
        self.draft_tokenizer = AutoTokenizer.from_pretrained(
            self.config.draft_model_id,
            trust_remote_code=True
        )
        self.draft_model = AutoModelForCausalLM.from_pretrained(
            self.config.draft_model_id,
            quantization_config=quantization_config if self.config.device == "cuda" else None,
            device_map="auto" if self.config.device == "cuda" else None,
            trust_remote_code=True,
            torch_dtype=torch.float16 if self.config.device in ["cuda", "mps"] else torch.float32,
        )
        
        if self.config.device == "mps":
            self.draft_model = self.draft_model.to(self.config.device)
            
        # Check memory after draft model
        draft_memory = self.memory_monitor.get_delta()
        logger.info(f"Memory after draft model: {draft_memory['current_rss_gb']:.2f}GB (delta: {draft_memory['rss_delta_gb']:.2f}GB)")
        
        # Load target model (Qwen2-7B)
        logger.info(f"Loading target model: {self.config.target_model_id}")
        
        # Check if we have the MLX model locally
        mlx_model_path = Path.home() / ".cache/huggingface/hub/models--mlx-community--Qwen2-7B-4bit"
        if mlx_model_path.exists():
            logger.info("Using cached Qwen2-7B-4bit model")
            model_id = "mlx-community/Qwen2-7B-4bit"
        else:
            model_id = self.config.target_model_id
            
        self.target_tokenizer = AutoTokenizer.from_pretrained(
            model_id,
            trust_remote_code=True
        )
        self.target_model = AutoModelForCausalLM.from_pretrained(
            model_id,
            quantization_config=quantization_config if self.config.device == "cuda" else None,
            device_map="auto" if self.config.device == "cuda" else None,
            trust_remote_code=True,
            torch_dtype=torch.float16 if self.config.device in ["cuda", "mps"] else torch.float32,
        )
        
        if self.config.device == "mps":
            self.target_model = self.target_model.to(self.config.device)
            
        # Final memory check
        final_memory = self.memory_monitor.get_delta()
        logger.info(f"Total memory usage: {final_memory['current_rss_gb']:.2f}GB (delta: {final_memory['rss_delta_gb']:.2f}GB)")
        
        load_time = time.time() - start_time
        logger.info(f"Models loaded in {load_time:.2f}s")
        
        # Check if we're within memory budget
        if final_memory['current_rss_gb'] > self.config.max_memory_gb:
            logger.warning(f"Memory usage ({final_memory['current_rss_gb']:.2f}GB) exceeds budget ({self.config.max_memory_gb}GB)")
    
    def speculative_generate(
        self, 
        prompt: str, 
        max_tokens: Optional[int] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """Generate text using 2-model speculative decoding"""
        if max_tokens is None:
            max_tokens = self.config.max_tokens
            
        start_time = time.time()
        
        # Tokenize input
        input_ids = self.target_tokenizer.encode(prompt, return_tensors="pt").to(self.config.device)
        
        generated_ids = input_ids.clone()
        total_generated = 0
        
        with torch.no_grad():
            while total_generated < max_tokens:
                # Step 1: Generate draft tokens
                draft_start = time.time()
                draft_output = self.draft_model.generate(
                    generated_ids,
                    max_new_tokens=self.config.draft_tokens,
                    temperature=self.config.temperature,
                    top_p=self.config.top_p,
                    do_sample=True,
                    pad_token_id=self.draft_tokenizer.pad_token_id or self.draft_tokenizer.eos_token_id,
                )
                draft_time = time.time() - draft_start
                
                # Extract draft tokens
                draft_tokens = draft_output[:, generated_ids.shape[1]:]
                self.stats["total_draft_tokens"] += draft_tokens.shape[1]
                
                # Step 2: Verify with target model
                verify_start = time.time()
                
                # Get target model's predictions for each position
                accepted_tokens = 0
                for i in range(draft_tokens.shape[1]):
                    # Create input with draft tokens up to position i
                    verify_input = torch.cat([generated_ids, draft_tokens[:, :i+1]], dim=1)
                    
                    # Get target model's next token distribution
                    target_logits = self.target_model(verify_input).logits[:, -1, :]
                    target_probs = torch.nn.functional.softmax(target_logits / self.config.temperature, dim=-1)
                    
                    # Check if draft token matches target's top choices
                    draft_token_id = draft_tokens[0, i].item()
                    draft_token_prob = target_probs[0, draft_token_id].item()
                    
                    # Accept if probability is high enough (adaptive threshold)
                    top_k_probs, _ = torch.topk(target_probs[0], k=5)
                    threshold = top_k_probs[-1].item()  # 5th highest probability
                    
                    if draft_token_prob >= threshold:
                        accepted_tokens += 1
                        self.stats["accepted_tokens"] += 1
                    else:
                        # Rejection point - stop accepting
                        self.stats["rejection_points"].append(i)
                        break
                
                verify_time = time.time() - verify_start
                
                # Step 3: Update generated sequence
                if accepted_tokens > 0:
                    generated_ids = torch.cat([generated_ids, draft_tokens[:, :accepted_tokens]], dim=1)
                    total_generated += accepted_tokens
                else:
                    # Fall back to target model for one token
                    fallback_start = time.time()
                    target_output = self.target_model.generate(
                        generated_ids,
                        max_new_tokens=1,
                        temperature=self.config.temperature,
                        top_p=self.config.top_p,
                        do_sample=True,
                        pad_token_id=self.target_tokenizer.pad_token_id or self.target_tokenizer.eos_token_id,
                    )
                    fallback_time = time.time() - fallback_start
                    
                    generated_ids = target_output
                    total_generated += 1
                
                # Check for EOS
                if self.target_tokenizer.eos_token_id in generated_ids[0, -5:]:
                    break
        
        # Decode final output
        generated_text = self.target_tokenizer.decode(
            generated_ids[0], 
            skip_special_tokens=True
        )
        
        inference_time = time.time() - start_time
        self.stats["inference_times"].append(inference_time)
        
        # Calculate metrics
        acceptance_rate = self.stats["accepted_tokens"] / max(self.stats["total_draft_tokens"], 1)
        tokens_per_second = total_generated / inference_time
        
        metrics = {
            "inference_time": inference_time,
            "total_tokens": total_generated,
            "tokens_per_second": tokens_per_second,
            "acceptance_rate": acceptance_rate,
            "memory_usage_gb": self.memory_monitor.get_delta()["current_rss_gb"],
            "draft_tokens_total": self.stats["total_draft_tokens"],
            "accepted_tokens": self.stats["accepted_tokens"],
        }
        
        return generated_text, metrics
    
    def generate_baseline(
        self, 
        prompt: str, 
        max_tokens: Optional[int] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """Generate text using only the target model (baseline)"""
        if max_tokens is None:
            max_tokens = self.config.max_tokens
            
        start_time = time.time()
        
        # Tokenize and generate
        input_ids = self.target_tokenizer.encode(prompt, return_tensors="pt").to(self.config.device)
        
        with torch.no_grad():
            output = self.target_model.generate(
                input_ids,
                max_new_tokens=max_tokens,
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                do_sample=True,
                pad_token_id=self.target_tokenizer.pad_token_id or self.target_tokenizer.eos_token_id,
            )
        
        generated_text = self.target_tokenizer.decode(output[0], skip_special_tokens=True)
        
        inference_time = time.time() - start_time
        total_tokens = output.shape[1] - input_ids.shape[1]
        
        metrics = {
            "inference_time": inference_time,
            "total_tokens": total_tokens,
            "tokens_per_second": total_tokens / inference_time,
            "memory_usage_gb": self.memory_monitor.get_delta()["current_rss_gb"],
            "method": "baseline"
        }
        
        return generated_text, metrics


def main():
    """Test the 2-model speculative decoding implementation"""
    config = SpeculativeConfig()
    
    # Initialize pipeline
    pipeline = Speculative2Model(config)
    
    # Load models
    logger.info("Initializing 2-model speculative decoding pipeline...")
    pipeline.load_models()
    
    # Test prompts
    test_prompts = [
        "What is the capital of France?",
        "Write a short Python function to calculate factorial:",
        "Explain quantum computing in simple terms:",
    ]
    
    results = []
    
    for prompt in test_prompts:
        logger.info(f"\nTesting prompt: {prompt[:50]}...")
        
        # Baseline generation
        logger.info("Running baseline (single model)...")
        baseline_text, baseline_metrics = pipeline.generate_baseline(prompt, max_tokens=100)
        
        # Speculative generation
        logger.info("Running speculative decoding...")
        spec_text, spec_metrics = pipeline.generate_speculative(prompt, max_tokens=100)
        
        # Calculate speedup
        speedup = spec_metrics["tokens_per_second"] / baseline_metrics["tokens_per_second"]
        
        result = {
            "prompt": prompt,
            "baseline": {
                "text": baseline_text,
                "metrics": baseline_metrics
            },
            "speculative": {
                "text": spec_text,
                "metrics": spec_metrics
            },
            "speedup": speedup
        }
        
        results.append(result)
        
        logger.info(f"Speedup: {speedup:.2f}x")
        logger.info(f"Acceptance rate: {spec_metrics.get('acceptance_rate', 0):.2%}")
    
    # Save results
    output_path = Path(__file__).parent.parent / "results" / "phase2_initial_test.json"
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"\nResults saved to: {output_path}")
    
    # Print summary
    avg_speedup = sum(r["speedup"] for r in results) / len(results)
    logger.info(f"\nAverage speedup: {avg_speedup:.2f}x")


if __name__ == "__main__":
    main()