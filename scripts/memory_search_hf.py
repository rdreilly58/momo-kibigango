#!/usr/bin/env python3
"""
Memory Search via Hugging Face Embeddings
Searches MEMORY.md and memory/*.md files using HF embeddings
"""

import os
import glob
import json
from pathlib import Path
from typing import List, Dict, Tuple
import sys

# Import the HF wrapper
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hf_embedding_wrapper import embed_text, embed_texts

def load_memory_files() -> Dict[str, str]:
    """Load all memory files from memory/ directory"""
    workspace = Path.home() / ".openclaw" / "workspace"
    memory_files = {}
    
    # Load MEMORY.md
    memory_md = workspace / "MEMORY.md"
    if memory_md.exists():
        with open(memory_md, 'r') as f:
            memory_files["MEMORY.md"] = f.read()
    
    # Load memory/*.md files
    memory_dir = workspace / "memory"
    if memory_dir.exists():
        for md_file in glob.glob(str(memory_dir / "*.md")):
            filename = os.path.basename(md_file)
            with open(md_file, 'r') as f:
                memory_files[filename] = f.read()
    
    return memory_files

def split_into_chunks(text: str, chunk_size: int = 500) -> List[Tuple[str, int, str]]:
    """
    Split text into overlapping chunks
    Returns: List of (chunk_text, chunk_index, source_file)
    """
    lines = text.split('\n')
    chunks = []
    current_chunk = []
    current_size = 0
    chunk_index = 0
    
    for line in lines:
        current_chunk.append(line)
        current_size += len(line)
        
        if current_size >= chunk_size:
            chunk_text = '\n'.join(current_chunk)
            chunks.append((chunk_text, chunk_index, ""))
            current_chunk = current_chunk[-5:]  # Overlap
            current_size = sum(len(l) for l in current_chunk)
            chunk_index += 1
    
    if current_chunk:
        chunks.append(('\n'.join(current_chunk), chunk_index, ""))
    
    return chunks

def memory_search_hf(query: str, top_k: int = 5) -> List[Dict]:
    """
    Search memory files using Hugging Face embeddings
    
    Args:
        query: Search query string
        top_k: Number of results to return
        
    Returns:
        List of results with content, score, and source
    """
    print(f"Loading memory files...", file=sys.stderr)
    memory_files = load_memory_files()
    
    # Create chunks from all files
    all_chunks = []
    for filename, content in memory_files.items():
        chunks = split_into_chunks(content)
        for chunk_text, idx, _ in chunks:
            all_chunks.append({
                "text": chunk_text,
                "source": filename,
                "index": idx
            })
    
    if not all_chunks:
        return []
    
    print(f"Processing {len(all_chunks)} chunks...", file=sys.stderr)
    
    # Get query embedding
    print(f"Embedding query...", file=sys.stderr)
    query_embedding = embed_text(query)
    
    # Get embeddings for all chunks
    print(f"Embedding {len(all_chunks)} chunks...", file=sys.stderr)
    chunk_texts = [c["text"] for c in all_chunks]
    chunk_embeddings = embed_texts(chunk_texts)
    
    # Calculate similarity scores (cosine similarity)
    import math
    
    def cosine_similarity(a: List[float], b: List[float]) -> float:
        dot_product = sum(x * y for x, y in zip(a, b))
        magnitude_a = math.sqrt(sum(x * x for x in a))
        magnitude_b = math.sqrt(sum(x * x for x in b))
        if magnitude_a == 0 or magnitude_b == 0:
            return 0
        return dot_product / (magnitude_a * magnitude_b)
    
    # Score all chunks
    scores = []
    for i, chunk in enumerate(all_chunks):
        score = cosine_similarity(query_embedding, chunk_embeddings[i])
        scores.append({
            "score": score,
            "text": chunk["text"][:200] + "..." if len(chunk["text"]) > 200 else chunk["text"],
            "full_text": chunk["text"],
            "source": chunk["source"],
            "index": chunk["index"]
        })
    
    # Sort by score and return top k
    results = sorted(scores, key=lambda x: x["score"], reverse=True)[:top_k]
    
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: memory_search_hf.py <query>")
        sys.exit(1)
    
    query = " ".join(sys.argv[1:])
    print(f"\nSearching for: {query}\n", file=sys.stderr)
    
    results = memory_search_hf(query, top_k=5)
    
    if results:
        for i, result in enumerate(results, 1):
            print(f"\n[{i}] Score: {result['score']:.3f} | Source: {result['source']}")
            print(f"    {result['text']}")
    else:
        print("No results found")
