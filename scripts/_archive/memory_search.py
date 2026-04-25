#!/usr/bin/env python3
"""
Local memory search using Sentence Transformers embeddings.
Searches MEMORY.md and memory/*.md files using semantic similarity.
"""

import os
import sys
import glob
import json
import argparse
from datetime import datetime
from pathlib import Path
import re

# Add venv to path
sys.path.insert(0, os.path.expanduser("~/.openclaw/workspace/venv/lib/python3.14/site-packages"))

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Tuple


class MemorySearcher:
    """Search memory files using local embeddings."""
    
    def __init__(self, workspace: str = "~/.openclaw/workspace"):
        self.workspace = os.path.expanduser(workspace)
        self.model = None
        self.memory_chunks = []  # List of (filename, chunk_text, embedding)
        
    def _load_model(self):
        """Lazy load the model."""
        if self.model is None:
            print(f"Loading embedding model...", file=sys.stderr)
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            
    def _chunk_text(self, text: str, chunk_size: int = 500) -> List[str]:
        """Split text into overlapping chunks."""
        lines = text.split('\n')
        chunks = []
        current_chunk = []
        current_size = 0
        
        for line in lines:
            line_size = len(line)
            if current_size + line_size > chunk_size and current_chunk:
                # Save current chunk
                chunks.append('\n'.join(current_chunk))
                # Start new chunk with overlap (keep last 2 lines)
                current_chunk = current_chunk[-2:] if len(current_chunk) > 2 else []
                current_size = sum(len(l) for l in current_chunk)
                
            current_chunk.append(line)
            current_size += line_size
            
        # Don't forget the last chunk
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
            
        return chunks
        
    def index_memory_files(self):
        """Index all memory files."""
        self._load_model()
        self.memory_chunks = []
        
        # Files to index
        memory_files = []
        
        # Add MEMORY.md if it exists
        memory_path = os.path.join(self.workspace, "MEMORY.md")
        if os.path.exists(memory_path):
            memory_files.append(memory_path)
            
        # Add all memory/*.md files
        memory_dir = os.path.join(self.workspace, "memory")
        if os.path.exists(memory_dir):
            memory_files.extend(glob.glob(os.path.join(memory_dir, "*.md")))
            
        # Process each file
        print(f"Indexing {len(memory_files)} memory files...", file=sys.stderr)
        
        for filepath in memory_files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Extract relative path for display
                rel_path = os.path.relpath(filepath, self.workspace)
                
                # Chunk the content
                chunks = self._chunk_text(content)
                
                # Generate embeddings for chunks
                if chunks:
                    embeddings = self.model.encode(chunks, convert_to_numpy=True)
                    for chunk, embedding in zip(chunks, embeddings):
                        self.memory_chunks.append((rel_path, chunk, embedding))
                        
            except Exception as e:
                print(f"Error indexing {filepath}: {e}", file=sys.stderr)
                
        print(f"Indexed {len(self.memory_chunks)} chunks from {len(memory_files)} files.", file=sys.stderr)
        
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search memory files for relevant content.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of results with filename, content, and score
        """
        if not self.memory_chunks:
            self.index_memory_files()
            
        # Generate query embedding
        self._load_model()
        query_embedding = self.model.encode(query, convert_to_numpy=True)
        
        # Calculate similarities
        results = []
        for filename, chunk, chunk_embedding in self.memory_chunks:
            # Cosine similarity
            similarity = np.dot(query_embedding, chunk_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(chunk_embedding)
            )
            results.append({
                'filename': filename,
                'content': chunk,
                'score': float(similarity),
                'preview': chunk[:200] + '...' if len(chunk) > 200 else chunk
            })
            
        # Sort by score and return top k
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
        
    def search_with_context(self, query: str, top_k: int = 5, context_lines: int = 3) -> List[Dict]:
        """Search and include surrounding context from the source file."""
        initial_results = self.search(query, top_k)
        
        # For each result, try to find it in the source file and get context
        enhanced_results = []
        for result in initial_results:
            filepath = os.path.join(self.workspace, result['filename'])
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                    
                # Find the chunk in the file
                chunk_start = file_content.find(result['content'][:100])  # Use first 100 chars to locate
                if chunk_start != -1:
                    # Get line numbers
                    lines_before = file_content[:chunk_start].count('\n')
                    
                    # Extract with context
                    all_lines = file_content.split('\n')
                    start_line = max(0, lines_before - context_lines)
                    end_line = min(len(all_lines), lines_before + result['content'].count('\n') + context_lines + 1)
                    
                    context_content = '\n'.join(all_lines[start_line:end_line])
                    result['content_with_context'] = context_content
                    result['line_number'] = lines_before + 1
                    
            except Exception as e:
                print(f"Error getting context for {result['filename']}: {e}", file=sys.stderr)
                
            enhanced_results.append(result)
            
        return enhanced_results


def main():
    """CLI interface for memory search."""
    parser = argparse.ArgumentParser(description='Search memory files using local embeddings')
    parser.add_argument('query', help='Search query')
    parser.add_argument('--top-k', type=int, default=5, help='Number of results to return')
    parser.add_argument('--context', type=int, default=3, help='Lines of context to include')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--workspace', default='~/.openclaw/workspace', help='Workspace directory')
    parser.add_argument('--reindex', action='store_true', help='Force reindex of memory files')
    
    args = parser.parse_args()
    
    searcher = MemorySearcher(workspace=args.workspace)
    
    if args.reindex:
        searcher.index_memory_files()
        
    # Perform search
    results = searcher.search_with_context(args.query, top_k=args.top_k, context_lines=args.context)
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        # Pretty print results
        print(f"\nSearch results for: '{args.query}'\n" + "="*60)
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['filename']} (score: {result['score']:.3f})")
            if 'line_number' in result:
                print(f"   Line {result['line_number']}")
            print("   " + "-"*40)
            content = result.get('content_with_context', result['content'])
            # Indent content
            for line in content.split('\n'):
                print(f"   {line}")
            print()


if __name__ == '__main__':
    main()