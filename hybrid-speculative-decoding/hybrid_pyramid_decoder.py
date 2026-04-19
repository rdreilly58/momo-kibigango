#!/usr/bin/env python3
"""
Hybrid 3-Tier Speculative Decoding
Local draft + qualifier with Claude Opus fallback for hard questions
"""

import torch
import time
import json
import os
import numpy as np
from typing import List, Tuple, Dict, Optional, Any
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch.nn.functional as F
from sentence_transformers import SentenceTransformer
import anthropic
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hybrid_decoder.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"


class HybridPyramidDecoder:
    """Hybrid 3-tier decoder with local draft/qualifier and Opus fallback"""
    
    def __init__(self,
                 draft_model_id: str = "Qwen/Qwen2.5-0.5B-Instruct",
                 qualifier_model_id: str = "microsoft/phi-2",
                 similarity_model_id: str = "sentence-transformers/all-MiniLM-L6-v2",
                 anthropic_api_key: Optional[str] = None,
                 device: Optional[str] = None):
        
        # Detect device
        if device:
            self.device = device
        elif torch.cuda.is_available():
            self.device = "cuda"
        elif torch.backends.mps.is_available():
            self.device = "mps"
        else:
            self.device = "cpu"
        
        logger.info(f"Using device: {self.device}")
        
        # Load models
        start_load = time.time()
        self._load_models(draft_model_id, qualifier_model_id, similarity_model_id)
        load_time = time.time() - start_load
        logger.info(f"All models loaded in {load_time:.2f} seconds")
        
        # Initialize Anthropic client
        if anthropic_api_key:
            self.anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
        else:
            # Try environment variable
            api_key = os.environ.get('ANTHROPIC_API_KEY')
            if api_key:
                self.anthropic_client = anthropic.Anthropic(api_key=api_key)
            else:
                logger.warning("No Anthropic API key provided. Opus fallback disabled.")
                self.anthropic_client = None
        
        # Quality thresholds by task type
        self.thresholds = {
            'math': 0.90,      # High threshold for math
            'code': 0.88,      # High for code
            'creative': 0.80,  # Lower for creative
            'general': 0.85    # Default
        }
        
        # Metrics tracking
        self.metrics = {
            'total_requests': 0,
            'local_accepts': 0,
            'opus_fallbacks': 0,
            'total_latency': 0,
            'total_cost': 0,
            'acceptance_by_type': {k: {'total': 0, 'accepted': 0} for k in self.thresholds}
        }
    
    def _load_models(self, draft_id: str, qualifier_id: str, similarity_id: str):
        """Load all models with optimizations"""
        
        # Load draft model (Qwen 0.5B)
        logger.info(f"Loading draft model: {draft_id}")
        self.draft_tokenizer = AutoTokenizer.from_pretrained(draft_id, trust_remote_code=True)
        if self.draft_tokenizer.pad_token is None:
            self.draft_tokenizer.pad_token = self.draft_tokenizer.eos_token
        
        self.draft_model = AutoModelForCausalLM.from_pretrained(
            draft_id,
            torch_dtype=torch.float16 if self.device != "cpu" else torch.float32,
            low_cpu_mem_usage=True,
            trust_remote_code=True
        )
        if self.device != "cpu":
            self.draft_model = self.draft_model.to(self.device)
        self.draft_model.eval()
        
        # Load qualifier model (Phi-2)
        logger.info(f"Loading qualifier model: {qualifier_id}")
        self.qualifier_tokenizer = AutoTokenizer.from_pretrained(qualifier_id, trust_remote_code=True)
        if self.qualifier_tokenizer.pad_token is None:
            self.qualifier_tokenizer.pad_token = self.qualifier_tokenizer.eos_token
        
        self.qualifier_model = AutoModelForCausalLM.from_pretrained(
            qualifier_id,
            torch_dtype=torch.float16 if self.device != "cpu" else torch.float32,
            low_cpu_mem_usage=True,
            trust_remote_code=True
        )
        if self.device != "cpu":
            self.qualifier_model = self.qualifier_model.to(self.device)
        self.qualifier_model.eval()
        
        # Load similarity model for quality scoring
        logger.info(f"Loading similarity model: {similarity_id}")
        self.similarity_model = SentenceTransformer(similarity_id, device=self.device)
        
        logger.info("All models loaded successfully!")
    
    def _classify_task_type(self, prompt: str) -> str:
        """Classify task type based on prompt content"""
        prompt_lower = prompt.lower()
        
        # Math indicators
        if any(word in prompt_lower for word in ['calculate', 'solve', 'equation', 'math', 'integral', 'derivative', 'prove']):
            return 'math'
        
        # Code indicators
        if any(word in prompt_lower for word in ['code', 'program', 'function', 'implement', 'debug', 'algorithm', 'class']):
            return 'code'
        
        # Creative indicators
        if any(word in prompt_lower for word in ['story', 'poem', 'creative', 'imagine', 'describe', 'narrative']):
            return 'creative'
        
        return 'general'
    
    def _calculate_confidence(self, prompt: str, generated_text: str, task_type: str) -> float:
        """Calculate confidence score using semantic similarity"""
        # Get embeddings
        prompt_embedding = self.similarity_model.encode(prompt, convert_to_tensor=True)
        generated_embedding = self.similarity_model.encode(generated_text, convert_to_tensor=True)
        
        # Calculate cosine similarity
        similarity = F.cosine_similarity(prompt_embedding.unsqueeze(0), generated_embedding.unsqueeze(0)).item()
        
        # Adjust based on task type and response characteristics
        confidence = similarity
        
        # Boost confidence for appropriate length responses
        response_length = len(generated_text.split())
        if 20 <= response_length <= 200:
            confidence += 0.05
        
        # Penalty for very short responses
        if response_length < 10:
            confidence -= 0.1
        
        # Clamp to [0, 1]
        confidence = max(0.0, min(1.0, confidence))
        
        return confidence
    
    @torch.no_grad()
    def _generate_with_draft(self, prompt: str, max_new_tokens: int = 100) -> Tuple[str, float]:
        """Generate using local draft model and calculate confidence"""
        # Tokenize
        inputs = self.draft_tokenizer(prompt, return_tensors="pt", padding=True).to(self.device)
        
        # Generate
        outputs = self.draft_model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            pad_token_id=self.draft_tokenizer.pad_token_id
        )
        
        # Decode
        generated_text = self.draft_tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Get just the generated part
        generated_only = generated_text[len(prompt):].strip()
        
        # Calculate confidence
        task_type = self._classify_task_type(prompt)
        confidence = self._calculate_confidence(prompt, generated_only, task_type)
        
        return generated_only, confidence
    
    def _generate_with_opus(self, prompt: str, max_tokens: int = 100) -> Tuple[str, float]:
        """Generate using Claude Opus API"""
        if not self.anthropic_client:
            logger.error("Anthropic client not initialized")
            return "Error: Anthropic API not available", 0.0
        
        try:
            message = self.anthropic_client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=max_tokens,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Extract text and calculate cost
            generated_text = message.content[0].text
            
            # Estimate tokens (rough approximation)
            input_tokens = len(prompt.split()) * 1.3
            output_tokens = len(generated_text.split()) * 1.3
            
            # Claude Opus pricing (as of 2024)
            # $15 per 1M input tokens, $75 per 1M output tokens
            cost = (input_tokens * 0.015 + output_tokens * 0.075) / 1000
            
            return generated_text, cost
            
        except Exception as e:
            logger.error(f"Opus API error: {e}")
            return f"Error: {str(e)}", 0.0
    
    def generate(self, prompt: str, max_tokens: int = 100) -> Dict[str, Any]:
        """Main generation method with hybrid approach"""
        start_time = time.time()
        task_type = self._classify_task_type(prompt)
        
        # Update metrics
        self.metrics['total_requests'] += 1
        self.metrics['acceptance_by_type'][task_type]['total'] += 1
        
        # Try local generation first
        logger.info(f"Generating with draft model for {task_type} task...")
        draft_text, confidence = self._generate_with_draft(prompt, max_tokens)
        
        logger.info(f"Draft confidence: {confidence:.3f}, threshold: {self.thresholds[task_type]}")
        
        # Decide whether to accept or fallback
        if confidence > self.thresholds[task_type]:
            # Accept local generation
            source = 'local'
            final_text = draft_text
            cost = 0.0
            self.metrics['local_accepts'] += 1
            self.metrics['acceptance_by_type'][task_type]['accepted'] += 1
            logger.info("Accepted local generation")
        else:
            # Fallback to Opus
            logger.info("Confidence too low, falling back to Opus...")
            if self.anthropic_client:
                opus_text, cost = self._generate_with_opus(prompt, max_tokens)
                source = 'opus'
                final_text = opus_text
                self.metrics['opus_fallbacks'] += 1
                self.metrics['total_cost'] += cost
            else:
                # No Opus available, use draft anyway
                source = 'local-forced'
                final_text = draft_text
                cost = 0.0
                logger.warning("Opus not available, using draft output")
        
        # Calculate final metrics
        latency = time.time() - start_time
        self.metrics['total_latency'] += latency
        
        # Log request
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'task_type': task_type,
            'confidence': confidence,
            'source': source,
            'latency': latency,
            'cost': cost,
            'prompt_preview': prompt[:50] + '...' if len(prompt) > 50 else prompt
        }
        logger.info(f"Request completed: {json.dumps(log_entry, indent=2)}")
        
        return {
            'text': final_text,
            'source': source,
            'confidence': confidence,
            'task_type': task_type,
            'latency': latency,
            'cost': cost,
            'metrics': self.get_metrics()
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        total_reqs = self.metrics['total_requests']
        if total_reqs == 0:
            return self.metrics
        
        return {
            **self.metrics,
            'acceptance_rate': self.metrics['local_accepts'] / total_reqs,
            'average_latency': self.metrics['total_latency'] / total_reqs,
            'average_cost': self.metrics['total_cost'] / total_reqs,
            'acceptance_rates_by_type': {
                k: v['accepted'] / v['total'] if v['total'] > 0 else 0
                for k, v in self.metrics['acceptance_by_type'].items()
            }
        }


def test_basic_functionality():
    """Test basic functionality"""
    print("="*80)
    print("HYBRID PYRAMID DECODER TEST")
    print("="*80)
    
    # Initialize decoder
    decoder = HybridPyramidDecoder()
    
    # Test prompts
    test_prompts = [
        ("What is the capital of France?", "general"),
        ("Calculate the integral of x^2 from 0 to 1", "math"),
        ("Write a function to reverse a string in Python", "code"),
        ("Write a short poem about the ocean", "creative"),
        ("Explain photosynthesis in simple terms", "general"),
    ]
    
    for prompt, expected_type in test_prompts:
        print(f"\n{'='*60}")
        print(f"Prompt: {prompt}")
        print(f"Expected type: {expected_type}")
        
        result = decoder.generate(prompt, max_tokens=100)
        
        print(f"\nResult:")
        print(f"- Source: {result['source']}")
        print(f"- Confidence: {result['confidence']:.3f}")
        print(f"- Task type: {result['task_type']}")
        print(f"- Latency: {result['latency']:.2f}s")
        print(f"- Cost: ${result['cost']:.4f}")
        print(f"- Text: {result['text'][:100]}...")
    
    # Print final metrics
    print(f"\n{'='*60}")
    print("FINAL METRICS:")
    metrics = decoder.get_metrics()
    print(f"- Total requests: {metrics['total_requests']}")
    print(f"- Acceptance rate: {metrics['acceptance_rate']:.2%}")
    print(f"- Average latency: {metrics['average_latency']:.2f}s")
    print(f"- Average cost: ${metrics['average_cost']:.4f}")
    print(f"- Total cost: ${metrics['total_cost']:.4f}")


if __name__ == "__main__":
    test_basic_functionality()