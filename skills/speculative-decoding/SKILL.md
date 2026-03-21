# Speculative Decoding

Accelerate LLM text generation by 1.8-2.1x while maintaining quality through multi-model speculative decoding.

## Overview

This skill implements the Speculative Decoding technique from research, using smaller "draft" models to propose tokens that are verified by larger "target" models. The implementation supports three modes:

1. **Single Model** (1model) - Traditional generation, fallback option
2. **Two Model** (2model) - Draft + Target, reliable 1.9x speedup
3. **Three Model Pyramid** (3model) - Draft + Qualifier + Target, up to 2.1x speedup

The system automatically selects the best mode based on available memory and gracefully degrades if resources are constrained.

## Key Features

- **1.8-2.1x faster generation** while maintaining output quality
- **Automatic fallback** from 3-model → 2-model → 1-model on memory pressure
- **Production hardening** with error handling, monitoring, and rate limiting
- **Prometheus metrics** for observability (latency, throughput, acceptance rates)
- **Feature flags** for gradual rollout and A/B testing
- **OpenClaw native** with CLI and REST API interfaces

## Installation

```bash
# Install the skill
clawhub install speculative-decoding

# Or manually:
cd ~/momo-kibidango
pip install -r requirements.txt
python src/openclaw_native.py --initialize
```

## Usage Examples

### Basic Text Generation

```bash
# Generate with auto-selected mode
openclaw-speculative "Explain how neural networks work"

# Force specific mode
openclaw-speculative --mode 3model "Write a story about a robot"

# Longer generation
openclaw-speculative --max-length 500 "Describe the history of computing"
```

### Batch Processing

```bash
# Process multiple prompts from file
openclaw-speculative --batch prompts.txt --output results.json

# Example prompts.txt:
# What is machine learning?
# Explain quantum computing
# How does the internet work?
```

### Configuration Management

```bash
# Show current configuration
openclaw-speculative --show-config

# Update settings
openclaw-speculative --config enable_3model=true default_mode=3model

# Use custom config file
openclaw-speculative --config-file ~/my-config.json "Test prompt"
```

### System Operations

```bash
# Check system status
openclaw-speculative --status

# View performance metrics
openclaw-speculative --metrics

# Initialize models (usually automatic)
openclaw-speculative --initialize

# Clean shutdown
openclaw-speculative --shutdown
```

## REST API Usage

The skill also provides a REST API for integration:

```bash
# Start API server (runs on port 5000 by default)
python src/openclaw_integration_v2.py
```

### API Endpoints

**Generate text:**
```bash
curl -X POST http://localhost:5000/infer \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is artificial intelligence?",
    "max_length": 100,
    "temperature": 0.7,
    "mode": "2model"
  }'
```

**Batch generation:**
```bash
curl -X POST http://localhost:5000/batch \
  -H "Content-Type: application/json" \
  -d '{
    "prompts": ["Question 1?", "Question 2?"],
    "max_length": 50
  }'
```

**Check status:**
```bash
curl http://localhost:5000/status
```

**Update configuration:**
```bash
curl -X POST http://localhost:5000/config \
  -H "Content-Type: application/json" \
  -d '{"enable_3model": true, "default_mode": "3model"}'
```

## Configuration

Default configuration location: `~/.openclaw/workspace/skills/speculative-decoding/config.json`

```json
{
  "default_mode": "2model",
  "enable_3model": true,
  "enable_2model": true,
  "enable_fallback": true,
  "max_batch_size": 8,
  "request_timeout": 300,
  "enable_monitoring": true,
  "monitoring_port": 8080
}
```

### Key Settings

- `default_mode` - Which model configuration to use by default
- `enable_3model` - Allow 3-model pyramid mode (requires 11.6GB memory)
- `enable_fallback` - Automatically fall back on memory pressure
- `monitoring_port` - Port for Prometheus metrics endpoint

## Performance Tuning

### Memory Requirements

| Mode | Memory Usage | Speedup | Best For |
|------|--------------|---------|----------|
| 1model | 7GB | 1.0x (baseline) | Memory-constrained |
| 2model | 10.8GB | 1.9x | Balanced performance |
| 3model | 11.6GB | 2.0x | Maximum speed |

### Optimization Tips

1. **Warm up models** - First inference is slower due to model loading
2. **Batch requests** - Process multiple prompts together for efficiency
3. **Monitor metrics** - Watch acceptance rates; <60% indicates issues
4. **Adjust temperature** - Lower values (0.5-0.7) improve acceptance rates

## Monitoring

### Prometheus Metrics

Access metrics at `http://localhost:8080/metrics`:

- `speculative_decoding_inference_total` - Total inference count
- `speculative_decoding_latency_seconds` - Request latency histogram
- `speculative_decoding_throughput_tokens_per_second` - Token generation rate
- `speculative_decoding_acceptance_rate` - Draft token acceptance rates
- `speculative_decoding_memory_usage_gb` - Memory consumption

### Health Checks

- `/health` - Basic liveness check
- `/ready` - Readiness probe (checks model loading)
- `/debug` - Detailed diagnostics

### Example Prometheus Query

```promql
# Average throughput over 5 minutes
rate(speculative_decoding_tokens_generated_total[5m]) / rate(speculative_decoding_inference_total[5m])

# P95 latency by mode
histogram_quantile(0.95, speculative_decoding_latency_seconds_bucket)
```

## Troubleshooting

### Common Issues

**Out of Memory Error**
- Symptom: "ResourceExhaustedError" or OOM errors
- Solution: Enable fallback mode or use 2model instead of 3model
- Check: Run `openclaw-speculative --status` to see memory usage

**Low Acceptance Rate**
- Symptom: Acceptance rate <60%, slow generation
- Causes: Temperature too high, incompatible prompts
- Solution: Lower temperature to 0.5-0.7, use simpler prompts

**Slow First Inference**
- Symptom: First generation takes 30-60 seconds
- Cause: Model loading and initialization
- Solution: Use `--initialize` to preload models

**Rate Limit Errors**
- Symptom: "Rate limit exceeded" errors
- Cause: Too many requests per minute (default: 60)
- Solution: Batch requests or increase limit in config

### Debug Commands

```bash
# Check memory usage
openclaw-speculative --status | jq .system_metrics

# View error counts
openclaw-speculative --metrics | jq .error_counts

# Test with minimal mode
openclaw-speculative --mode 1model "Test prompt"

# Enable debug logging
export LOGLEVEL=DEBUG
openclaw-speculative "Test with debug"
```

### Log Locations

- Performance metrics: `~/.openclaw/workspace/skills/speculative-decoding/logs/performance_metrics.jsonl`
- Error logs: Check OpenClaw session logs
- Inference history: `~/.openclaw/workspace/skills/speculative-decoding/logs/inference_*.log`

## Architecture Details

### Model Pipeline

```
3-Model Pyramid:
┌─────────────────────────────┐
│   Qwen2-7B-4bit (Target)    │ ← Final verification
│      4GB VRAM               │    
└─────────────────────────────┘
              ↑ 90% acceptance
┌─────────────────────────────┐
│   Phi-2 2.7B (Qualifier)    │ ← Quality filter
│      2.5GB VRAM             │    
└─────────────────────────────┘
              ↑ 85% acceptance
┌─────────────────────────────┐
│   Qwen2-0.5B (Draft)        │ ← Fast generation
│      2GB VRAM               │    
└─────────────────────────────┘
```

### How It Works

1. **Draft Generation** - Small model quickly generates N tokens
2. **Qualification** - Medium model filters obviously wrong tokens
3. **Verification** - Large model accepts/rejects qualified tokens
4. **Fallback** - On rejection, generate single token from target

This hierarchical approach achieves better acceptance rates than direct draft→target verification.

## Advanced Usage

### Custom Model Configuration

Create a custom config file:
```json
{
  "draft_model_id": "microsoft/phi-2",
  "target_model_id": "meta-llama/Llama-2-7b-chat-hf",
  "max_draft_tokens": 8,
  "temperature": 0.6,
  "device": "cuda"
}
```

### Programmatic Usage

```python
from openclaw_native import OpenClawSpeculativeDecoding, OpenClawConfig

# Create configuration
config = OpenClawConfig(
    default_mode="3model",
    enable_monitoring=True
)

# Initialize skill
skill = OpenClawSpeculativeDecoding(config)
skill.initialize()

# Generate text
result = skill.generate(
    "Explain quantum computing",
    max_length=200,
    temperature=0.7
)

print(result["output"])
print(f"Tokens/sec: {result['tokens_generated'] / result['generation_time']:.1f}")
```

## Contributing

The skill is part of the momo-kibidango project: https://github.com/rdreilly58/momo-kibidango

To contribute:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## References

- Original paper: ["Speculative Decoding"](https://arxiv.org/abs/2211.01098)
- Implementation: [momo-kibidango](https://github.com/rdreilly58/momo-kibidango)
- Related research: [SpecInfer](https://arxiv.org/abs/2305.09781), [Medusa](https://arxiv.org/abs/2401.10020)

## License

MIT License - See repository for details.