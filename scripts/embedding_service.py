#!/usr/bin/env python3
"""
Local embedding service using Sentence Transformers.
Provides both CLI and Python API for generating embeddings.
"""

import os
import sys
import json
import time
import argparse
from typing import List, Union, Dict, Any
import hashlib

# Add venv to path
sys.path.insert(0, os.path.expanduser("~/.openclaw/workspace/venv/lib/python3.14/site-packages"))

from sentence_transformers import SentenceTransformer
import numpy as np


class EmbeddingService:
    """Local embedding service with caching and batch processing."""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model_name = model_name
        self.model = None
        self.cache = {}  # Simple in-memory cache
        self.stats = {
            'embeddings_generated': 0,
            'cache_hits': 0,
            'total_latency_ms': 0
        }
        
    def _load_model(self):
        """Lazy load the model on first use."""
        if self.model is None:
            print(f"Loading model {self.model_name}...", file=sys.stderr)
            self.model = SentenceTransformer(self.model_name)
            
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        return hashlib.md5(text.encode()).hexdigest()
        
    def embed(self, text: Union[str, List[str]], use_cache: bool = True) -> Union[List[float], List[List[float]]]:
        """
        Generate embeddings for text(s).
        
        Args:
            text: Single string or list of strings
            use_cache: Whether to use caching
            
        Returns:
            Single embedding vector or list of embedding vectors
        """
        self._load_model()
        
        # Handle single text
        if isinstance(text, str):
            texts = [text]
            single = True
        else:
            texts = text
            single = False
            
        results = []
        texts_to_embed = []
        text_indices = []
        
        # Check cache
        for i, t in enumerate(texts):
            if use_cache:
                cache_key = self._get_cache_key(t)
                if cache_key in self.cache:
                    results.append(self.cache[cache_key])
                    self.stats['cache_hits'] += 1
                else:
                    texts_to_embed.append(t)
                    text_indices.append(i)
                    results.append(None)
            else:
                texts_to_embed.append(t)
                text_indices.append(i)
                results.append(None)
                
        # Generate embeddings for uncached texts
        if texts_to_embed:
            start_time = time.time()
            embeddings = self.model.encode(texts_to_embed, convert_to_numpy=True)
            latency_ms = (time.time() - start_time) * 1000
            
            # Update stats
            self.stats['embeddings_generated'] += len(texts_to_embed)
            self.stats['total_latency_ms'] += latency_ms
            
            # Fill results and update cache
            for i, (idx, emb) in enumerate(zip(text_indices, embeddings)):
                results[idx] = emb.tolist()
                if use_cache:
                    cache_key = self._get_cache_key(texts_to_embed[i])
                    self.cache[cache_key] = results[idx]
                    
        return results[0] if single else results
        
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        avg_latency = (self.stats['total_latency_ms'] / self.stats['embeddings_generated'] 
                      if self.stats['embeddings_generated'] > 0 else 0)
        return {
            **self.stats,
            'avg_latency_ms': avg_latency,
            'cache_size': len(self.cache),
            'model': self.model_name
        }


def main():
    """CLI interface for the embedding service."""
    parser = argparse.ArgumentParser(description='Local embedding service')
    parser.add_argument('text', nargs='*', help='Text(s) to embed')
    parser.add_argument('--batch', action='store_true', help='Read batch input from stdin (JSON array)')
    parser.add_argument('--no-cache', action='store_true', help='Disable caching')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--model', default='all-MiniLM-L6-v2', help='Model name')
    
    args = parser.parse_args()
    
    service = EmbeddingService(model_name=args.model)
    
    if args.stats:
        print(json.dumps(service.get_stats(), indent=2))
        return
        
    # Get texts to embed
    if args.batch:
        texts = json.loads(sys.stdin.read())
    elif args.text:
        texts = args.text if len(args.text) > 1 else args.text[0]
    else:
        print("Error: Provide text as arguments or use --batch for JSON input", file=sys.stderr)
        sys.exit(1)
        
    # Generate embeddings
    embeddings = service.embed(texts, use_cache=not args.no_cache)
    
    # Output as JSON
    print(json.dumps(embeddings, indent=2))


if __name__ == '__main__':
    main()