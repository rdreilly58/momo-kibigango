#!/usr/bin/env python3
"""
OpenClaw Integration Layer for 2-Model Speculative Decoding
Project: momo-kibigango
Created: March 19, 2026

Provides HTTP API endpoint for OpenClaw to use local speculative decoding.
"""

import asyncio
import json
import logging
import time
from typing import Optional, Dict, Any
from pathlib import Path
from dataclasses import dataclass

from aiohttp import web
from pydantic import BaseModel, Field
import torch

from speculative_2model import Speculative2Model, SpeculativeConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class InferenceRequest(BaseModel):
    """Request model for inference API"""
    prompt: str
    max_tokens: int = Field(default=512, ge=1, le=2048)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=0.9, ge=0.0, le=1.0)
    use_speculative: bool = Field(default=True, description="Use speculative decoding")
    stream: bool = Field(default=False, description="Stream response tokens")


class InferenceResponse(BaseModel):
    """Response model for inference API"""
    generated_text: str
    tokens: int
    inference_time: float
    tokens_per_second: float
    method: str
    memory_usage_gb: float
    speedup: Optional[float] = None
    acceptance_rate: Optional[float] = None
    error: Optional[str] = None


class OpenClawIntegration:
    """HTTP server for OpenClaw integration"""
    
    def __init__(self, config: SpeculativeConfig):
        self.config = config
        self.pipeline: Optional[Speculative2Model] = None
        self.app = web.Application()
        self.setup_routes()
        self.is_initialized = False
        self.initialization_lock = asyncio.Lock()
        
    def setup_routes(self):
        """Setup HTTP routes"""
        self.app.router.add_post('/v1/inference', self.handle_inference)
        self.app.router.add_get('/v1/status', self.handle_status)
        self.app.router.add_get('/v1/health', self.handle_health)
        self.app.router.add_post('/v1/initialize', self.handle_initialize)
        
    async def initialize_pipeline(self):
        """Initialize the model pipeline (lazy loading)"""
        async with self.initialization_lock:
            if self.is_initialized:
                return
                
            logger.info("Initializing 2-model speculative decoding pipeline...")
            
            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            
            def _init():
                self.pipeline = Speculative2Model(self.config)
                self.pipeline.load_models()
                
            await loop.run_in_executor(None, _init)
            
            self.is_initialized = True
            logger.info("Pipeline initialized successfully")
    
    async def handle_health(self, request):
        """Health check endpoint"""
        return web.json_response({
            "status": "healthy",
            "initialized": self.is_initialized,
            "device": str(self.config.device),
            "timestamp": time.time()
        })
    
    async def handle_status(self, request):
        """Status endpoint with detailed information"""
        status = {
            "initialized": self.is_initialized,
            "config": {
                "draft_model": self.config.draft_model_id,
                "target_model": self.config.target_model_id,
                "draft_tokens": self.config.draft_tokens,
                "device": str(self.config.device),
                "max_memory_gb": self.config.max_memory_gb
            }
        }
        
        if self.is_initialized and self.pipeline:
            # Add runtime stats
            status["stats"] = {
                "total_inferences": len(self.pipeline.stats.get("inference_times", [])),
                "avg_acceptance_rate": (
                    self.pipeline.stats["accepted_tokens"] / max(self.pipeline.stats["total_draft_tokens"], 1)
                    if self.pipeline.stats["total_draft_tokens"] > 0 else 0
                ),
                "memory_usage_gb": self.pipeline.memory_monitor.get_delta()["current_rss_gb"]
            }
            
        return web.json_response(status)
    
    async def handle_initialize(self, request):
        """Explicit initialization endpoint"""
        if self.is_initialized:
            return web.json_response({
                "status": "already_initialized",
                "message": "Pipeline is already initialized"
            })
            
        try:
            await self.initialize_pipeline()
            return web.json_response({
                "status": "success",
                "message": "Pipeline initialized successfully"
            })
        except Exception as e:
            logger.error(f"Failed to initialize pipeline: {e}")
            return web.json_response({
                "status": "error",
                "error": str(e)
            }, status=500)
    
    async def handle_inference(self, request):
        """Main inference endpoint"""
        try:
            # Parse request
            data = await request.json()
            req = InferenceRequest(**data)
            
            # Initialize pipeline if needed
            if not self.is_initialized:
                await self.initialize_pipeline()
            
            # Update config with request parameters
            self.config.temperature = req.temperature
            self.config.top_p = req.top_p
            
            # Run inference in executor
            loop = asyncio.get_event_loop()
            
            if req.stream:
                # Streaming not implemented yet
                return web.json_response({
                    "error": "Streaming not yet implemented"
                }, status=501)
            
            # Non-streaming inference
            def _inference():
                if req.use_speculative:
                    return self.pipeline.speculative_generate(
                        req.prompt,
                        max_tokens=req.max_tokens
                    )
                else:
                    return self.pipeline.generate_baseline(
                        req.prompt,
                        max_tokens=req.max_tokens
                    )
            
            generated_text, metrics = await loop.run_in_executor(None, _inference)
            
            # Prepare response
            response = InferenceResponse(
                generated_text=generated_text,
                tokens=metrics["total_tokens"],
                inference_time=metrics["inference_time"],
                tokens_per_second=metrics["tokens_per_second"],
                method="speculative" if req.use_speculative else "baseline",
                memory_usage_gb=metrics.get("memory_usage_gb", 0),
                speedup=metrics.get("speedup"),
                acceptance_rate=metrics.get("acceptance_rate")
            )
            
            return web.json_response(response.dict())
            
        except Exception as e:
            logger.error(f"Inference error: {e}")
            return web.json_response({
                "error": str(e)
            }, status=500)
    
    def run(self, host: str = "127.0.0.1", port: int = 8080):
        """Run the HTTP server"""
        logger.info(f"Starting OpenClaw integration server on {host}:{port}")
        web.run_app(self.app, host=host, port=port)


# Fallback handler for OpenClaw
class FallbackHandler:
    """Handles fallback to cloud providers when local inference fails"""
    
    def __init__(self):
        self.local_endpoint = "http://127.0.0.1:8080/v1/inference"
        self.timeout = 30  # seconds
        
    async def inference_with_fallback(
        self, 
        prompt: str,
        max_tokens: int = 512,
        use_local_first: bool = True
    ) -> Dict[str, Any]:
        """
        Try local inference first, fall back to cloud if needed.
        This would integrate with OpenClaw's existing LLM routing.
        """
        if use_local_first:
            try:
                # Try local speculative decoding
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        self.local_endpoint,
                        json={
                            "prompt": prompt,
                            "max_tokens": max_tokens,
                            "use_speculative": True
                        },
                        timeout=aiohttp.ClientTimeout(total=self.timeout)
                    ) as resp:
                        if resp.status == 200:
                            return await resp.json()
            except Exception as e:
                logger.warning(f"Local inference failed: {e}, falling back to cloud")
        
        # Fallback logic would go here - integrate with OpenClaw's existing providers
        return {
            "error": "Fallback to cloud providers not implemented",
            "suggestion": "Integrate with OpenClaw's existing LLM routing"
        }


def create_openclaw_config():
    """Create configuration for OpenClaw integration"""
    return {
        "local_inference": {
            "enabled": True,
            "endpoint": "http://127.0.0.1:8080/v1/inference",
            "timeout": 30,
            "use_for_categories": ["qa", "simple", "conversational"],
            "fallback_to_cloud": True,
            "memory_limit_gb": 12.0
        }
    }


def main():
    """Run the OpenClaw integration server"""
    config = SpeculativeConfig(
        device="mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu",
        draft_tokens=5,
        max_memory_gb=12.0
    )
    
    server = OpenClawIntegration(config)
    
    # Save OpenClaw config suggestion
    openclaw_config = create_openclaw_config()
    config_path = Path(__file__).parent.parent / "openclaw_integration_config.json"
    
    with open(config_path, "w") as f:
        json.dump(openclaw_config, f, indent=2)
    
    logger.info(f"OpenClaw configuration saved to: {config_path}")
    logger.info("Add this configuration to your OpenClaw settings to enable local inference")
    
    # Run server
    server.run()


if __name__ == "__main__":
    main()