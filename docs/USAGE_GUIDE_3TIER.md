# 3-Tier Speculative Decoding: Usage Guide

## Table of Contents
1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Running the Server](#running-the-server)
4. [API Reference](#api-reference)
5. [Code Examples](#code-examples)
6. [Monitoring & Metrics](#monitoring--metrics)
7. [Production Deployment](#production-deployment)

## Installation

### System Requirements

- **OS**: Linux (Ubuntu 20.04+) or macOS
- **Python**: 3.8 or higher
- **CUDA**: 11.7+ (for GPU support)
- **Memory**: 16GB RAM minimum
- **GPU**: 16GB+ VRAM (24GB recommended)

### Step-by-Step Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/speculative-decoding.git
cd speculative-decoding

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install PyTorch (CUDA 11.8 example)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 4. Install dependencies
pip install -r requirements.txt

# 5. Download models (automatic on first run, or pre-download)
python download_models.py --config hybrid_config.json

# 6. Verify installation
python test_installation.py
```

### Docker Installation

```dockerfile
# Dockerfile provided
FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y python3-pip git
COPY requirements.txt /app/
WORKDIR /app
RUN pip3 install -r requirements.txt
COPY . /app/
CMD ["python3", "hybrid_server.py"]
```

```bash
# Build and run
docker build -t speculative-decoding .
docker run --gpus all -p 7779:7779 speculative-decoding
```

## Configuration

### Configuration File Structure

Create `hybrid_config.json`:

```json
{
  "models": {
    "draft": {
      "name": "Qwen/Qwen2.5-0.5B",
      "device": "cuda:0",
      "dtype": "float16",
      "max_seq_len": 2048
    },
    "speculation": {
      "name": "Qwen/Qwen2.5-1.5B", 
      "device": "cuda:0",
      "dtype": "float16",
      "max_seq_len": 2048
    },
    "target": {
      "name": "Qwen/Qwen2.5-7B",
      "device": "cuda:0",
      "dtype": "float16",
      "max_seq_len": 2048
    }
  },
  "speculation": {
    "draft_k": 4,
    "spec_k": 3,
    "max_candidates": 8,
    "temperature_draft": 0.8,
    "temperature_spec": 0.7
  },
  "quality": {
    "threshold": 0.85,
    "fallback_threshold": 0.5,
    "adaptive": true,
    "history_window": 100
  },
  "performance": {
    "batch_size": 8,
    "cache_implementation": "flash_attention",
    "enable_cuda_graphs": true,
    "profile": false
  },
  "api": {
    "host": "0.0.0.0",
    "port": 7779,
    "max_concurrent_requests": 10,
    "timeout": 300
  }
}
```

### Environment Variables

```bash
# Model cache directory
export HF_HOME=/path/to/model/cache

# API keys (if using gated models)
export HF_TOKEN=your_huggingface_token

# Performance tuning
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
export CUDA_VISIBLE_DEVICES=0,1  # Multi-GPU

# Logging
export LOG_LEVEL=INFO
export LOG_FILE=/var/log/speculative.log
```

### Model Selection Guide

**For Speed Priority**:
```json
{
  "draft": "bigcode/tiny_starcoder_py",
  "speculation": "microsoft/phi-2",
  "target": "codellama/CodeLlama-7b-hf"
}
```

**For Quality Priority**:
```json
{
  "draft": "Qwen/Qwen2.5-0.5B",
  "speculation": "Qwen/Qwen2.5-3B",
  "target": "Qwen/Qwen2.5-14B"
}
```

**For Memory Efficiency**:
```json
{
  "draft": "TinyLlama/TinyLlama-1.1B",
  "speculation": "stabilityai/stablelm-2-1_6b",
  "target": "mistralai/Mistral-7B-v0.1"
}
```

## Running the Server

### Basic Server Start

```bash
# Default configuration
python hybrid_server.py

# Custom configuration
python hybrid_server.py --config my_config.json

# Debug mode
python hybrid_server.py --debug --log-level DEBUG

# Production mode
python hybrid_server.py --workers 4 --daemon
```

### Server Options

| Option | Description | Default |
|--------|-------------|---------|
| `--config` | Configuration file path | `hybrid_config.json` |
| `--host` | Server host | `0.0.0.0` |
| `--port` | Server port | `7779` |
| `--workers` | Number of worker processes | `1` |
| `--daemon` | Run as daemon | `False` |
| `--log-level` | Logging level | `INFO` |
| `--profile` | Enable profiling | `False` |

### Health Checks

```bash
# Check server health
curl http://localhost:7779/health

# Response
{
  "status": "healthy",
  "version": "1.0.0",
  "models_loaded": {
    "draft": true,
    "speculation": true,
    "target": true
  },
  "gpu_available": true,
  "memory_usage_gb": 17.2
}
```

## API Reference

### Generation Endpoint

**POST /generate**

Generate text using 3-tier speculative decoding.

```bash
curl -X POST http://localhost:7779/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "The key to happiness is",
    "max_tokens": 150,
    "temperature": 0.8,
    "top_p": 0.95,
    "stream": false
  }'
```

**Request Parameters**:
| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `prompt` | string | Input prompt | Required |
| `max_tokens` | int | Maximum tokens to generate | 100 |
| `temperature` | float | Sampling temperature | 0.7 |
| `top_p` | float | Nucleus sampling | 0.95 |
| `top_k` | int | Top-k sampling | 50 |
| `stream` | bool | Stream response | false |
| `quality_mode` | string | "fast", "balanced", "quality" | "balanced" |

**Response**:
```json
{
  "text": "The key to happiness is finding balance in life...",
  "tokens": 45,
  "time_taken": 1.2,
  "tokens_per_second": 37.5,
  "model_used": "3-tier",
  "quality_score": 0.94
}
```

### Streaming Endpoint

**POST /generate (with stream=true)**

```python
import requests
import json

response = requests.post(
    "http://localhost:7779/generate",
    json={"prompt": "Tell me a story", "max_tokens": 200, "stream": True},
    stream=True
)

for line in response.iter_lines():
    if line:
        data = json.loads(line.decode('utf-8').replace('data: ', ''))
        print(data['text'], end='', flush=True)
```

### Metrics Endpoint

**GET /metrics**

```bash
curl http://localhost:7779/metrics

# Response
{
  "performance": {
    "tokens_per_second": 42.3,
    "avg_latency_ms": 23.6,
    "throughput_requests_per_sec": 8.2
  },
  "quality": {
    "acceptance_rate": 0.92,
    "fallback_rate": 0.03,
    "avg_quality_score": 0.95
  },
  "resources": {
    "gpu_utilization": 0.78,
    "memory_usage_gb": 17.2,
    "cache_hit_rate": 0.84
  }
}
```

## Code Examples

### Python Client

```python
import requests
import json

class SpeculativeClient:
    def __init__(self, base_url="http://localhost:7779"):
        self.base_url = base_url
    
    def generate(self, prompt, **kwargs):
        """Generate text with 3-tier speculative decoding."""
        payload = {
            "prompt": prompt,
            "max_tokens": kwargs.get("max_tokens", 100),
            "temperature": kwargs.get("temperature", 0.7),
            "stream": kwargs.get("stream", False)
        }
        
        response = requests.post(
            f"{self.base_url}/generate",
            json=payload
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.text}")
    
    def get_metrics(self):
        """Get performance metrics."""
        response = requests.get(f"{self.base_url}/metrics")
        return response.json()

# Example usage
client = SpeculativeClient()

# Simple generation
result = client.generate(
    "Explain quantum computing in simple terms:",
    max_tokens=200,
    temperature=0.7
)
print(result['text'])

# Check performance
metrics = client.get_metrics()
print(f"Tokens/sec: {metrics['performance']['tokens_per_second']}")
```

### Async Python Client

```python
import aiohttp
import asyncio

async def generate_async(prompt, max_tokens=100):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:7779/generate",
            json={
                "prompt": prompt,
                "max_tokens": max_tokens,
                "stream": True
            }
        ) as response:
            async for line in response.content:
                if line:
                    data = json.loads(line.decode().replace('data: ', ''))
                    print(data['text'], end='', flush=True)

# Run async
asyncio.run(generate_async("Once upon a time", 200))
```

### cURL Examples

```bash
# Basic generation
curl -X POST http://localhost:7779/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello world", "max_tokens": 50}'

# Quality mode
curl -X POST http://localhost:7779/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a poem about AI",
    "max_tokens": 100,
    "quality_mode": "quality"
  }'

# Streaming with jq
curl -X POST http://localhost:7779/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Count to 10", "stream": true}' \
  | jq -r '.text'
```

### JavaScript/Node.js Client

```javascript
const axios = require('axios');

class SpeculativeClient {
    constructor(baseUrl = 'http://localhost:7779') {
        this.baseUrl = baseUrl;
    }
    
    async generate(prompt, options = {}) {
        const response = await axios.post(
            `${this.baseUrl}/generate`,
            {
                prompt,
                max_tokens: options.maxTokens || 100,
                temperature: options.temperature || 0.7,
                stream: options.stream || false
            }
        );
        return response.data;
    }
}

// Usage
const client = new SpeculativeClient();
const result = await client.generate(
    'What is the meaning of life?',
    { maxTokens: 200 }
);
console.log(result.text);
```

## Monitoring & Metrics

### Built-in Monitoring

```python
# Enable detailed metrics in config
{
  "monitoring": {
    "enable_prometheus": true,
    "prometheus_port": 9090,
    "log_interval_seconds": 60,
    "track_per_request": true
  }
}
```

### Prometheus Integration

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'speculative'
    static_configs:
      - targets: ['localhost:9090']
```

### Key Metrics to Monitor

1. **Performance Metrics**:
   - `tokens_per_second` - Generation speed
   - `time_to_first_token` - Initial latency
   - `batch_efficiency` - GPU utilization

2. **Quality Metrics**:
   - `acceptance_rate` - Draft quality
   - `fallback_rate` - Quality issues
   - `quality_score` - Overall quality

3. **Resource Metrics**:
   - `gpu_memory_used` - Memory usage
   - `gpu_utilization` - Compute usage
   - `cache_hit_rate` - Cache efficiency

### Custom Monitoring Script

```python
#!/usr/bin/env python3
import requests
import time
import matplotlib.pyplot as plt
from collections import deque

class MetricsMonitor:
    def __init__(self, url="http://localhost:7779"):
        self.url = url
        self.history = deque(maxlen=100)
    
    def collect_metrics(self):
        response = requests.get(f"{self.url}/metrics")
        metrics = response.json()
        self.history.append({
            'timestamp': time.time(),
            'tps': metrics['performance']['tokens_per_second'],
            'quality': metrics['quality']['acceptance_rate']
        })
    
    def plot_realtime(self):
        plt.ion()
        fig, (ax1, ax2) = plt.subplots(2, 1)
        
        while True:
            self.collect_metrics()
            
            timestamps = [m['timestamp'] for m in self.history]
            tps = [m['tps'] for m in self.history]
            quality = [m['quality'] for m in self.history]
            
            ax1.clear()
            ax1.plot(timestamps, tps)
            ax1.set_ylabel('Tokens/sec')
            
            ax2.clear()
            ax2.plot(timestamps, quality)
            ax2.set_ylabel('Acceptance Rate')
            
            plt.pause(1)

# Run monitor
monitor = MetricsMonitor()
monitor.plot_realtime()
```

### Logging Configuration

```python
# logging_config.yaml
version: 1
handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: simple
  file:
    class: logging.handlers.RotatingFileHandler
    filename: speculative.log
    maxBytes: 10485760  # 10MB
    backupCount: 5
    formatter: detailed
formatters:
  simple:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  detailed:
    format: '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
root:
  level: INFO
  handlers: [console, file]
```

## Production Deployment

### Systemd Service

```ini
# /etc/systemd/system/speculative.service
[Unit]
Description=3-Tier Speculative Decoding Server
After=network.target

[Service]
Type=simple
User=speculative
WorkingDirectory=/opt/speculative-decoding
Environment="PATH=/opt/speculative-decoding/venv/bin"
ExecStart=/opt/speculative-decoding/venv/bin/python hybrid_server.py --config production.json
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Load Balancing

```nginx
# nginx.conf
upstream speculative {
    server localhost:7779;
    server localhost:7780;
    server localhost:7781;
}

server {
    listen 80;
    server_name api.example.com;
    
    location / {
        proxy_pass http://speculative;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
    }
}
```

### Production Checklist

- [ ] Configure appropriate model paths
- [ ] Set up monitoring and alerting
- [ ] Enable HTTPS/TLS
- [ ] Configure rate limiting
- [ ] Set up log rotation
- [ ] Create backup strategy
- [ ] Test failover procedures
- [ ] Document API keys and secrets
- [ ] Set resource limits
- [ ] Enable health checks