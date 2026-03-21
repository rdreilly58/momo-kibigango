#!/usr/bin/env python3
"""
Local Memory Search using Sentence Transformers
Fast, free, no API keys needed
"""

import os
import glob
import math
from pathlib import Path
from typing import List, Dict
import sys

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sentence_transformers import SentenceTransformer

# Load model once
MODEL = SentenceTransformer('all-MiniLM-L6-v2')

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
        for md_file in sorted(glob.glob(str(memory_dir / "*.md"))):
            filename = os.path.basename(md_file)
            with open(md_file, 'r') as f:
                memory_files[filename] = f.read()
    
    return memory_files

def split_into_chunks(text: str, chunk_size: int = 500) -> List[Dict]:
    """Split text into overlapping chunks"""
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
            chunks.append({"text": chunk_text, "index": chunk_index})
            current_chunk = current_chunk[-5:]  # Overlap
            current_size = sum(len(l) for l in current_chunk)
            chunk_index += 1
    
    if current_chunk:
        chunks.append({"text": '\n'.join(current_chunk), "index": chunk_index})
    
    return chunks

def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    dot_product = sum(x * y for x, y in zip(a, b))
    magnitude_a = math.sqrt(sum(x * x for x in a))
    magnitude_b = math.sqrt(sum(x * x for x in b))
    if magnitude_a == 0 or magnitude_b == 0:
        return 0
    return dot_product / (magnitude_a * magnitude_b)

def memory_search(query: str, top_k: int = 5) -> List[Dict]:
    """
    Search memory files using local Sentence Transformers
    
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
        for chunk_data in chunks:
            all_chunks.append({
                "text": chunk_data["text"],
                "source": filename,
                "index": chunk_data["index"]
            })
    
    if not all_chunks:
        return []
    
    print(f"Processing {len(all_chunks)} chunks...", file=sys.stderr)
    
    # Get query embedding
    print(f"Embedding query: '{query}'", file=sys.stderr)
    query_embedding = MODEL.encode(query)
    
    # Get embeddings for all chunks
    print(f"Embedding {len(all_chunks)} chunks...", file=sys.stderr)
    chunk_texts = [c["text"] for c in all_chunks]
    chunk_embeddings = MODEL.encode(chunk_texts)
    
    # Score all chunks
    scores = []
    for i, chunk in enumerate(all_chunks):
        score = cosine_similarity(query_embedding, chunk_embeddings[i])
        scores.append({
            "score": score,
            "text": chunk["text"][:150] + "..." if len(chunk["text"]) > 150 else chunk["text"],
            "full_text": chunk["text"],
            "source": chunk["source"],
            "index": chunk["index"]
        })
    
    # Sort by score and return top k
    results = sorted(scores, key=lambda x: x["score"], reverse=True)[:top_k]
    
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: memory_search_local.py <query>")
        sys.exit(1)
    
    query = " ".join(sys.argv[1:])
    print(f"\nSearching for: '{query}'\n", file=sys.stderr)
    
    results = memory_search(query, top_k=5)
    
    if results:
        print(f"\n{'='*70}\n")
        for i, result in enumerate(results, 1):
            print(f"[{i}] Score: {result['score']:.3f} | {result['source']}")
            print(f"    {result['text']}")
            print()
    else:
        print("No results found\n")
