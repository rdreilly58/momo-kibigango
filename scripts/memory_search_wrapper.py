#!/usr/bin/env python3
"""
Local Embeddings Wrapper for memory_search
Replaces OpenAI embeddings with local Sentence Transformers
Falls back to HF API if local fails
"""

import sys
import json
import os
from pathlib import Path

def search_local(query: str, top_k: int = 5):
    """Search using local Sentence Transformers"""
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent / 'venv' / 'lib' / 'python3.11' / 'site-packages'))
        
        from sentence_transformers import SentenceTransformer
        import numpy as np
        
        # Load model
        model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Embed query
        query_embedding = model.encode(query, convert_to_tensor=False)
        
        # Search memory files
        memory_dir = Path.home() / '.openclaw' / 'workspace' / 'memory'
        results = []
        
        for md_file in sorted(memory_dir.glob('*.md')):
            with open(md_file, 'r') as f:
                content = f.read()
                
            # Split into chunks (simple line-based)
            chunks = content.split('\n\n')
            
            for chunk_idx, chunk in enumerate(chunks):
                if len(chunk.strip()) < 10:  # Skip tiny chunks
                    continue
                    
                chunk_embedding = model.encode(chunk, convert_to_tensor=False)
                similarity = np.dot(query_embedding, chunk_embedding)
                
                results.append({
                    'score': float(similarity),
                    'file': md_file.name,
                    'chunk': chunk[:200],
                    'path': f"{md_file.name}#{chunk_idx}"
                })
        
        # Sort by score and return top-k
        results = sorted(results, key=lambda x: x['score'], reverse=True)[:top_k]
        
        return {
            'status': 'success',
            'provider': 'local_sentence_transformers',
            'results': results,
            'count': len(results)
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': f'Local search failed: {str(e)}',
            'provider': 'local_sentence_transformers'
        }

def search_hf_fallback(query: str, top_k: int = 5):
    """Fallback to Hugging Face API if local fails"""
    try:
        import requests
        
        hf_token = os.getenv('HF_API_TOKEN')
        if not hf_token:
            return {'status': 'error', 'error': 'HF_API_TOKEN not set'}
        
        # This is a placeholder - actual HF API fallback would be more complex
        return {
            'status': 'fallback',
            'message': 'HF fallback available but not configured',
            'provider': 'huggingface_api'
        }
        
    except Exception as e:
        return {'status': 'error', 'error': f'HF fallback failed: {str(e)}'}

def main():
    if len(sys.argv) < 2:
        print(json.dumps({'error': 'Query required'}))
        sys.exit(1)
    
    query = sys.argv[1]
    top_k = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    # Try local first
    result = search_local(query, top_k)
    
    # If local fails, try HF fallback
    if result['status'] == 'error':
        print(json.dumps({'warning': 'Local search failed, would try HF fallback', **result}), file=sys.stderr)
        result = search_hf_fallback(query, top_k)
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()
