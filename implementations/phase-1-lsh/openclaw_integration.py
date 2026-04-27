"""
OpenClaw Integration Module for LSH Memory Search

This module replaces the standard memory_search() function with LSH-accelerated search.
Integrates seamlessly with OpenClaw's memory module.
"""

import os
import json
import numpy as np
import logging
from pathlib import Path
from typing import List, Dict, Optional
from lsh_memory_search import LSHMemorySearch, SearchResult

logger = logging.getLogger(__name__)


class OpenClawLSHIntegration:
    """
    Integration layer between OpenClaw memory module and LSH search.
    Handles initialization, fallback, and metrics collection.
    """
    
    def __init__(
        self,
        memory_file_path: str = "~/.openclaw/workspace/MEMORY.md",
        embeddings_cache_path: str = "~/.openclaw/workspace/.lsh_cache",
        num_hashes: int = 20,  # Tuned up from 16 for better recall
        recall_threshold: float = 0.90,
    ):
        """Initialize OpenClaw LSH integration."""
        self.memory_file_path = Path(memory_file_path).expanduser()
        self.embeddings_cache_path = Path(embeddings_cache_path).expanduser()
        self.num_hashes = num_hashes
        self.recall_threshold = recall_threshold
        
        self.lsh_search = None
        self.initialized = False
        self.initialization_error = None
        
        logger.info("OpenClaw LSH Integration initialized")
    
    def initialize(self) -> bool:
        """
        Initialize LSH search from OpenClaw memory files.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Load memory embeddings and metadata from cache
            embeddings_file = self.embeddings_cache_path / "embeddings.npy"
            ids_file = self.embeddings_cache_path / "chunk_ids.json"
            contents_file = self.embeddings_cache_path / "chunk_contents.json"
            
            if not all([embeddings_file.exists(), ids_file.exists(), contents_file.exists()]):
                logger.warning("LSH cache files not found. Run cache_memory_embeddings() first.")
                return False
            
            # Load data
            embeddings = np.load(embeddings_file)
            with open(ids_file) as f:
                chunk_ids = json.load(f)
            with open(contents_file) as f:
                chunk_contents = json.load(f)
            
            # Create LSH search
            self.lsh_search = LSHMemorySearch(
                embeddings=embeddings,
                chunk_ids=chunk_ids,
                chunk_contents=chunk_contents,
                num_hashes=self.num_hashes,
                recall_threshold=self.recall_threshold,
            )
            
            self.initialized = True
            logger.info(f"✅ LSH integration ready ({len(chunk_ids)} chunks indexed)")
            return True
            
        except Exception as e:
            self.initialization_error = str(e)
            logger.error(f"LSH initialization failed: {e}")
            return False
    
    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
    ) -> List[Dict]:
        """
        Search memory using LSH.
        
        Args:
            query_embedding: (384,) numpy array
            top_k: Number of results to return
        
        Returns:
            List of dicts with keys: chunk_id, similarity, content, source
        """
        if not self.initialized or self.lsh_search is None:
            logger.error("LSH not initialized")
            return []
        
        try:
            results = self.lsh_search.search(
                query_embedding,
                top_k=top_k,
                use_fallback=True,
            )
            
            # Convert to dict format for OpenClaw
            return [
                {
                    "chunk_id": r.chunk_id,
                    "similarity": r.similarity,
                    "content": r.content,
                    "source": r.source,
                }
                for r in results
            ]
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def get_metrics(self) -> Dict:
        """Get LSH performance metrics."""
        if not self.initialized or self.lsh_search is None:
            return {}
        
        return self.lsh_search.get_metrics()
    
    def health_check(self) -> Dict:
        """
        Health check for LSH integration.
        
        Returns:
            Dict with status, latency, fallback rate, etc.
        """
        metrics = self.get_metrics()
        
        if not self.initialized:
            return {
                "status": "FAILED",
                "error": self.initialization_error or "Not initialized",
            }
        
        if metrics.get("total_queries", 0) < 10:
            return {
                "status": "WARMING_UP",
                "queries_run": metrics.get("total_queries", 0),
            }
        
        avg_latency = metrics.get("avg_latency_ms", 0)
        fallback_rate = metrics.get("fallback_rate", 0)
        
        if avg_latency > 50 or fallback_rate > 0.10:
            return {
                "status": "WARNING",
                "avg_latency_ms": avg_latency,
                "fallback_rate": fallback_rate,
                "recommendation": "Tune num_hashes or check query volume",
            }
        
        return {
            "status": "HEALTHY",
            "avg_latency_ms": avg_latency,
            "fallback_rate": fallback_rate,
            "lsh_hit_rate": metrics.get("lsh_hit_rate", 0),
            "total_queries": metrics.get("total_queries", 0),
        }


def create_openclaw_lsh() -> OpenClawLSHIntegration:
    """Factory function to create and initialize OpenClaw LSH integration."""
    integration = OpenClawLSHIntegration(num_hashes=20)
    if integration.initialize():
        return integration
    return None


# Global instance (lazy-loaded)
_openclaw_lsh = None


def get_lsh_search() -> Optional[OpenClawLSHIntegration]:
    """Get or create the global LSH search instance."""
    global _openclaw_lsh
    if _openclaw_lsh is None:
        _openclaw_lsh = create_openclaw_lsh()
    return _openclaw_lsh


if __name__ == "__main__":
    print("OpenClaw LSH Integration Module")
    print("Usage: from openclaw_integration import get_lsh_search")
    print("       lsh = get_lsh_search()")
    print("       results = lsh.search(query_embedding)")
