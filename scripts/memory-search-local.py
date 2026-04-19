#!/usr/bin/env python3
"""
Local Memory Search using Sentence Transformers
No API quota limits, works offline, instant results
Usage: python3 memory-search-local.py "search query" [--top-k 5]
"""

import os
import sys
import json
import re
from pathlib import Path
from sentence_transformers import SentenceTransformer
import numpy as np

MODEL_NAME = "all-MiniLM-L6-v2"
MEMORY_DIR = Path(os.path.expanduser("~/.openclaw/workspace/memory"))
MAIN_MEMORY = Path(os.path.expanduser("~/.openclaw/workspace/MEMORY.md"))
WORKSPACE_DIR = Path(os.path.expanduser("~/.openclaw/workspace"))

def load_model():
    """Load Sentence Transformers model"""
    print("📚 Loading embedding model...", file=sys.stderr)
    return SentenceTransformer(MODEL_NAME)

def chunk_text(text, chunk_size=300, overlap=50):
    """Split text into overlapping chunks"""
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunk = text[i:i + chunk_size]
        if chunk.strip():
            chunks.append(chunk)
    return chunks

def load_memory_files():
    """Load all searchable memory files"""
    documents = []
    
    # Load main MEMORY.md
    if MAIN_MEMORY.exists():
        with open(MAIN_MEMORY, 'r') as f:
            content = f.read()
            chunks = chunk_text(content)
            for chunk in chunks:
                documents.append({
                    'file': 'MEMORY.md',
                    'content': chunk
                })
    
    # Load daily memory files
    if MEMORY_DIR.exists():
        for md_file in sorted(MEMORY_DIR.glob("*.md"), reverse=True)[:30]:  # Last 30 files
            try:
                with open(md_file, 'r') as f:
                    content = f.read()
                    chunks = chunk_text(content)
                    for chunk in chunks:
                        documents.append({
                            'file': md_file.name,
                            'content': chunk
                        })
            except:
                pass
    
    # Load key docs from workspace
    key_docs = [
        WORKSPACE_DIR / "leidos/knowledge/LEADERSHIP_STRATEGY.md",
        WORKSPACE_DIR / "leidos/knowledge/FIRST_DAY_PLAN.md",
        WORKSPACE_DIR / "leidos/knowledge/FIRST_WEEK_PLAN.md",
        WORKSPACE_DIR / "docs/SESSION_SUMMARY_2026-03-26.md",
        WORKSPACE_DIR / "SOUL.md",
        WORKSPACE_DIR / "USER.md",
    ]
    
    for doc_path in key_docs:
        if doc_path.exists():
            try:
                with open(doc_path, 'r') as f:
                    content = f.read()
                    chunks = chunk_text(content)
                    for chunk in chunks:
                        documents.append({
                            'file': doc_path.name,
                            'content': chunk
                        })
            except:
                pass
    
    return documents

def search(query, documents, model, top_k=5):
    """Search memory files"""
    
    if not documents:
        print("❌ No memory files found", file=sys.stderr)
        return []
    
    print(f"🔍 Searching {len(documents)} chunks...", file=sys.stderr)
    
    # Embed query
    query_embedding = model.encode(query)
    
    # Embed all documents
    doc_contents = [doc['content'] for doc in documents]
    doc_embeddings = model.encode(doc_contents)
    
    # Calculate cosine similarities
    similarities = []
    for embedding in doc_embeddings:
        sim = np.dot(embedding, query_embedding) / (
            np.linalg.norm(embedding) * np.linalg.norm(query_embedding) + 1e-8
        )
        similarities.append(sim)
    
    similarities = np.array(similarities)
    
    # Get top results
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    
    results = []
    for idx in top_indices:
        if similarities[idx] > 0.2:  # Lower threshold for broader matches
            results.append({
                'file': documents[idx]['file'],
                'score': float(similarities[idx]),
                'content': documents[idx]['content']
            })
    
    return results

def format_results(results, query):
    """Format search results"""
    
    if not results:
        print(f"⚠️  No strong memory matches for: '{query}'")
        print("Try a different search term or check these files:")
        print("  - ~/.openclaw/workspace/MEMORY.md")
        print("  - ~/.openclaw/workspace/leidos/knowledge/LEADERSHIP_STRATEGY.md")
        return
    
    print(f"\n✅ Found {len(results)} relevant memory section(s):\n")
    print("=" * 80)
    
    for i, result in enumerate(results, 1):
        print(f"\n[{i}] {result['file']} (match: {result['score']:.0%})")
        print("-" * 80)
        
        # Clean up content
        content = result['content'].strip()
        if len(content) > 400:
            content = content[:400] + "..."
        
        print(content)
        print()

def main():
    """Main execution"""
    
    if len(sys.argv) < 2:
        print("Usage: python3 memory-search-local.py 'search query' [--top-k 5]")
        sys.exit(1)
    
    query = sys.argv[1]
    top_k = 5
    
    # Parse arguments
    for arg in sys.argv[2:]:
        if arg.startswith("--top-k"):
            top_k = int(arg.split("=")[1])
    
    try:
        # Load model and documents
        model = load_model()
        documents = load_memory_files()
        
        if not documents:
            print("❌ No memory documents found")
            sys.exit(1)
        
        print(f"Loaded {len(documents)} document chunks\n", file=sys.stderr)
        
        # Search
        results = search(query, documents, model, top_k)
        
        # Format and display
        format_results(results, query)
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
