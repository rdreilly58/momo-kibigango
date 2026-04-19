#!/usr/bin/env python3
"""
Hugging Face Embedding Wrapper
Provides embeddings via Hugging Face Inference API
"""

import os
import json
import requests
from typing import List, Union

# Configuration
HF_API_TOKEN = "REDACTED_HF_API_TOKEN"
HF_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

def embed_text(text: str) -> List[float]:
    """
    Get embedding for a single text string via Hugging Face API
    
    Args:
        text: Text to embed
        
    Returns:
        List of floats representing the embedding vector
        
    Raises:
        Exception: If API call fails
    """
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    payload = {
        "inputs": text,
        "options": {"wait_for_model": True}
    }
    
    try:
        response = requests.post(
            HF_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        # Hugging Face returns a list of embeddings (one per input)
        embeddings = response.json()
        
        # Return first embedding if list, otherwise return as-is
        if isinstance(embeddings, list) and len(embeddings) > 0:
            if isinstance(embeddings[0], list):
                return embeddings[0]
            else:
                return embeddings
        
        return embeddings
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Hugging Face API error: {e}")

def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Get embeddings for multiple text strings
    
    Args:
        texts: List of texts to embed
        
    Returns:
        List of embedding vectors
    """
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    payload = {
        "inputs": texts,
        "options": {"wait_for_model": True}
    }
    
    try:
        response = requests.post(
            HF_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Hugging Face API error: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        print("Embedding text:", text)
        embedding = embed_text(text)
        print(f"Embedding (first 5 values): {embedding[:5]}")
        print(f"Dimension: {len(embedding)}")
    else:
        print("Usage: python hf_embedding_wrapper.py <text to embed>")
