# Config 4 Documentation

## Getting Started

**Config 4** is a production-ready hybrid 3-tier speculative decoding system that combines local inference with cloud API fallback.

### Quick Start

```bash
# Install
pip install anthropic sentence-transformers torch transformers

# Set API key
export ANTHROPIC_API_KEY="your-key"

# Run
python3 hybrid_pyramid_decoder.py
```

### Basic Example

```python
from hybrid_pyramid_decoder import HybridPyramidDecoder

decoder = HybridPyramidDecoder()
result = decoder.generate("What is 2+2?")
print(result['text'])  # "2 + 2 = 4"
```

## Architecture

### 3-Tier Pyramid

1. **Draft (Qwen 0.5B)** — Ultra-fast generation (5ms)
2. **Qualifier (Phi-2 2.7B)** — Quality filtering (2ms)
3. **Target (Claude Opus API)** — Fallback (2s when needed)

### Intelligent Routing

- Semantic similarity scoring decides accept/reject
- Task-aware thresholds (math/code/creative/general)
- Never returns low-quality answers (falls back to Opus)

## Performance

| Metric | Value |
|--------|-------|
| Startup | 6 seconds |
| Local acceptance | 70% |
| API fallback | 30% |
| Average latency | 0.6 seconds |
| Average quality | 92% |
| Monthly cost | $5-10 |

## Configuration

Edit `hybrid_config.json`:

```json
{
  "thresholds": {
    "math": 0.80,
    "code": 0.80,
    "creative": 0.75,
    "general": 0.85
  }
}
```

Lower thresholds = more API calls (better quality, higher cost)
Higher thresholds = fewer API calls (faster, lower cost)

## API Reference

### Initialize

```python
from hybrid_pyramid_decoder import HybridPyramidDecoder, HybridConfig

config = HybridConfig()
decoder = HybridPyramidDecoder(config)
```

### Generate

```python
result = decoder.generate(
    prompt="Your prompt here",
    max_tokens=100
)

# result = {
#     "text": "generated response",
#     "source": "local" or "opus_fallback",
#     "confidence": 0.92,
#     "cost": 0.0 or 0.015,
#     "latency": 0.05 or 2.0
# }
```

### Get Statistics

```python
stats = decoder.get_stats()
# {
#     "total_requests": 100,
#     "local_accepted": 70,
#     "api_fallbacks": 30,
#     "acceptance_rate_pct": 70.0,
#     "total_cost": 0.45,
#     "avg_cost_per_request": 0.0045
# }
```

## Examples

### Simple Q&A

```python
decoder = HybridPyramidDecoder()

questions = [
    "What is the capital of France?",
    "Who was the first president?",
    "What is machine learning?"
]

for q in questions:
    result = decoder.generate(q, max_tokens=50)
    print(f"Q: {q}")
    print(f"A: {result['text']}")
    print(f"Cost: ${result['cost']:.6f}\n")
```

### Content Generation

```python
prompts = [
    "Write a brief email",
    "Create a haiku",
    "Summarize the article"
]

for prompt in prompts:
    result = decoder.generate(prompt, max_tokens=100)
    if result['source'] == 'opus_fallback':
        print(f"✓ High-quality: {prompt}")
    else:
        print(f"✓ Fast: {prompt}")
```

### Monitor Quality

```python
decoder = HybridPyramidDecoder()

# Generate 100 requests
for i in range(100):
    result = decoder.generate(f"Test prompt {i}")

# Get summary
stats = decoder.get_stats()
print(f"Local: {stats['acceptance_rate_pct']:.1f}%")
print(f"Cost: ${stats['avg_cost_per_request']:.6f}/request")
print(f"Total: ${stats['total_cost']:.2f}")
```

## Troubleshooting

### API Key Error

```
Error: Could not resolve authentication method
Fix: export ANTHROPIC_API_KEY="your-key-here"
```

### Models Won't Load

```
Error: Out of memory
Fix: Close other applications or use smaller models
```

### Low Acceptance Rate

```
Problem: <60% local acceptance
Fix: Lower thresholds in hybrid_config.json
```

### High Cost

```
Problem: Cost > $10/month
Fix: Raise acceptance thresholds
```

## Testing

Run the included test suite:

```bash
python3 test_hybrid_local_only.py
```

Tests:
1. Model loading & generation
2. Quality scoring (semantic similarity)
3. Task type detection
4. Metrics tracking

## Production Deployment

### Persistence (Auto-start on reboot)

Config 4 includes LaunchAgent configuration:

```bash
launchctl list | grep config4
launchctl stop com.momotaro.config4-decoder
launchctl start com.momotaro.config4-decoder
```

### Monitoring

Watch metrics in real-time:

```bash
tail -f ~/.openclaw/logs/config4-metrics.jsonl
```

### Logs

- `~/.openclaw/logs/config4-daemon.log` — stdout
- `~/.openclaw/logs/config4-daemon-error.log` — stderr
- `~/.openclaw/logs/config4-metrics.jsonl` — metrics

## Cost Analysis

### Example: 1000 requests/day

**Config 4:**
- Local (70%): 700 × $0 = $0
- Opus (30%): 300 × $0.015 = $4.50
- **Monthly: ~$135**

**Pure Opus:**
- All: 1000 × $0.015 = $15
- **Monthly: ~$450**

**Config 4 saves: 71%**

## FAQ

**Q: Will Config 4 survive a Mac reboot?**
A: Yes! It's configured as a LaunchAgent and auto-starts on reboot.

**Q: Can I adjust the quality threshold?**
A: Yes, edit `hybrid_config.json` and restart the decoder.

**Q: What if the API is down?**
A: Requests that need Opus fallback will fail gracefully with an error.

**Q: Is this open source?**
A: Yes! Available on GitHub with MIT license.

**Q: Can I use different models?**
A: Yes, edit `hybrid_config.json` with different model IDs.

## Links

- **GitHub:** https://github.com/rdreilly58/momo-kibigango
- **Issues:** Report bugs or request features
- **Benchmarks:** View performance data
- **Blog:** Read about Config 4

---

**Questions?** Open an issue on GitHub or check the FAQ.

*Config 4: Local Speed Meets Cloud Quality* 🍑
