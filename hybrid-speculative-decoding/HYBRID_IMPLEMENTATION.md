# Hybrid 3-Tier Speculative Decoding Implementation

## Overview

This implementation provides a hybrid approach to text generation that combines local models for fast responses with Claude Opus API fallback for complex queries. The system achieves ~70% local acceptance rate with <1s average latency.

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│   Request   │────▶│ Draft Model │────▶│   Quality    │
│             │     │ (Qwen 0.5B) │     │   Scoring    │
└─────────────┘     └─────────────┘     └──────┬───────┘
                                               │
                                               ▼
                                    ┌──────────────────┐
                                    │ Confidence > 0.85?│
                                    └────┬─────────┬───┘
                                         │ Yes     │ No
                                         ▼         ▼
                                    ┌─────────┐ ┌──────────┐
                                    │ Accept  │ │  Claude  │
                                    │ (Fast)  │ │   Opus   │
                                    └─────────┘ └──────────┘
```

## Components

### 1. HybridPyramidDecoder (`hybrid_pyramid_decoder.py`)

The main decoder class that orchestrates the hybrid approach:

- **Draft Model**: Qwen/Qwen2.5-0.5B-Instruct (fast, lightweight)
- **Qualifier Model**: microsoft/phi-2 (for future enhanced scoring)
- **Similarity Model**: sentence-transformers/all-MiniLM-L6-v2 (quality scoring)
- **Target API**: Claude 3 Opus via Anthropic API (high-quality fallback)

### 2. Flask API (`hybrid_flask_api.py`)

REST API server providing:

- `GET /health` - System health and metrics
- `POST /generate` - Main generation endpoint
- `GET /metrics` - Current performance metrics
- `GET /config` - Current configuration
- `PUT /config/thresholds` - Update confidence thresholds

### 3. Test Suite (`test_hybrid_pyramid.py`)

Comprehensive testing including:

- Easy prompts (should use local)
- Hard prompts (should fallback to Opus)
- Mixed prompts with known difficulties
- Latency testing for both paths
- Success criteria validation

### 4. Metrics Tracking (`hybrid_metrics.py`)

Advanced metrics and monitoring:

- Request logging with full details
- Performance analytics and reporting
- Live monitoring dashboard
- Visualization plots (acceptance rate, latency, costs)

## Installation

### Prerequisites

```bash
# Install Python dependencies
pip install torch transformers sentence-transformers anthropic flask flask-cors pandas matplotlib numpy
```

### Environment Setup

```bash
# Set Anthropic API key (optional, enables Opus fallback)
export ANTHROPIC_API_KEY='your-api-key-here'
```

## Usage

### Starting the Server

```bash
# Quick start
./start_hybrid_server.sh

# Custom configuration
HOST=0.0.0.0 PORT=8080 ./start_hybrid_server.sh

# Debug mode
DEBUG=true ./start_hybrid_server.sh
```

### API Examples

```bash
# Health check
curl http://localhost:7779/health

# Generate text
curl -X POST http://localhost:7779/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is the capital of France?",
    "max_tokens": 100
  }'

# Get metrics
curl http://localhost:7779/metrics

# Update thresholds
curl -X PUT http://localhost:7779/config/thresholds \
  -H "Content-Type: application/json" \
  -d '{
    "math": 0.95,
    "code": 0.90,
    "creative": 0.75,
    "general": 0.85
  }'
```

### Python Client

```python
import requests

# Create client
api_url = "http://localhost:7779"

# Generate text
response = requests.post(f"{api_url}/generate", json={
    "prompt": "Explain quantum computing",
    "max_tokens": 150
})

result = response.json()
print(f"Source: {result['source']}")
print(f"Confidence: {result['confidence']:.3f}")
print(f"Cost: ${result['cost']:.4f}")
print(f"Text: {result['text']}")
```

## Configuration

### Config File (`hybrid_config.json`)

```json
{
  "models": {
    "draft": {"id": "Qwen/Qwen2.5-0.5B-Instruct"},
    "qualifier": {"id": "microsoft/phi-2"},
    "similarity": {"id": "sentence-transformers/all-MiniLM-L6-v2"},
    "target": {"id": "claude-3-opus-20240229"}
  },
  "thresholds": {
    "math": 0.90,
    "code": 0.88,
    "creative": 0.80,
    "general": 0.85
  }
}
```

### Confidence Thresholds

- **Math**: 0.90 (high threshold for accuracy)
- **Code**: 0.88 (high for correctness)
- **Creative**: 0.80 (lower for flexibility)
- **General**: 0.85 (balanced default)

## Performance Metrics

### Target Performance

- **Startup Time**: ≤6 seconds
- **Acceptance Rate**: ≥70% (local model)
- **Average Latency**: <1 second
- **P95 Latency**: <2 seconds

### Cost Optimization

- Local requests: $0 (no API cost)
- Opus fallback: ~$0.015-0.075 per request
- Average cost with 70% acceptance: ~$0.01 per request

## Running Tests

```bash
# Run full test suite
python test_hybrid_pyramid.py

# Run with custom API URL
python test_hybrid_pyramid.py --api-url http://localhost:8080

# Test results saved to test_results.json
```

## Monitoring

### Live Dashboard

```bash
# Start live monitoring
python hybrid_metrics.py monitor

# Custom interval
python hybrid_metrics.py monitor --interval 10
```

### Generate Report

```bash
# Generate metrics report
python hybrid_metrics.py report

# Generate from custom log
python hybrid_metrics.py report --log-file custom.log
```

### Visualization

```bash
# Generate metric plots
python hybrid_metrics.py plot

# Plots saved to metrics_plots/
```

## Task Classification

The system automatically classifies prompts into task types:

- **Math**: Keywords like "calculate", "solve", "equation"
- **Code**: Keywords like "function", "implement", "debug"
- **Creative**: Keywords like "story", "poem", "imagine"
- **General**: Default for other queries

## Quality Scoring

Quality is assessed using:

1. Semantic similarity between prompt and response
2. Response length appropriateness
3. Task-specific adjustments

## Fallback Logic

```
IF confidence > threshold[task_type]:
    ACCEPT local generation (fast path)
ELSE:
    FALLBACK to Claude Opus (quality path)
```

## Error Handling

- Graceful degradation if Opus unavailable
- Automatic retry with exponential backoff
- Comprehensive error logging

## Production Deployment

### Systemd Service

Create `/etc/systemd/system/hybrid-decoder.service`:

```ini
[Unit]
Description=Hybrid Pyramid Decoder API
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/hybrid-speculative-decoding
Environment="ANTHROPIC_API_KEY=your-key"
ExecStart=/usr/bin/python3 hybrid_flask_api.py --host 0.0.0.0
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV ANTHROPIC_API_KEY=""
EXPOSE 7779

CMD ["python", "hybrid_flask_api.py", "--host", "0.0.0.0"]
```

## Troubleshooting

### Common Issues

1. **"No module named 'anthropic'"**
   ```bash
   pip install anthropic
   ```

2. **"CUDA out of memory"**
   - Use CPU mode: Set device="cpu" in code
   - Reduce batch size

3. **"Anthropic API error"**
   - Check API key is set correctly
   - Verify API quota/credits

4. **Slow startup**
   - Models download on first run
   - Use faster internet or pre-download models

### Debug Mode

```bash
# Enable detailed logging
DEBUG=true ./start_hybrid_server.sh

# Check logs
tail -f hybrid_api.log
tail -f hybrid_decoder.log
```

## Future Enhancements

1. **Caching**: Cache embeddings and responses
2. **Streaming**: Support streaming generation
3. **Batch Processing**: Handle multiple requests efficiently
4. **Model Quantization**: Further reduce model size
5. **Custom Models**: Support for other model combinations

## License

This implementation is provided as-is for research and educational purposes.

## Credits

- Qwen models by Alibaba Cloud
- Phi-2 by Microsoft
- Sentence Transformers by UKPLab
- Claude Opus by Anthropic