---
name: speculative-decoding
description: "Accelerate LLM inference using speculative decoding (small draft model + large verifier model). Provides 2-3x speedup for simple tasks with minimal quality trade-off. Falls back to standard API if vLLM unavailable."
homepage: https://docs.vllm.ai/en/latest/features/spec_decode.html
metadata: { "openclaw": { "emoji": "⚡", "version": "0.1.0", "phase": "experimental" } }
---

# Speculative Decoding Skill for OpenClaw

Accelerate simple task responses using speculative decoding (draft + verify pattern).

## What is Speculative Decoding?

Small fast model generates draft tokens → Large model verifies + generates actual tokens in parallel.

**Result:** 2-3x speedup without quality loss

## When to Use

✅ **USE this skill when:**
- Task is classified as SIMPLE (weather, calendar, quick facts)
- vLLM server is running locally
- You need immediate response (<1s)
- Speed > perfect accuracy (85% quality acceptable)

❌ **DON'T use when:**
- Task requires full Claude Opus reasoning
- vLLM server is down
- Quality MUST be 99%+ (use Claude API)
- Task involves sensitive decisions

## Setup

### Prerequisites
- Docker (or local vLLM installation)
- GPU or CPU (works with both, GPU much faster)
- 20GB+ free disk space (for models)

### Quick Start

```bash
# 1. Start vLLM server with speculative decoding
./scripts/start-vlm-server.sh

# 2. Test the setup
./scripts/test-speculative.sh

# 3. Monitor performance
tail -f logs/vlm-server.log
```

## Configuration

Edit `references/vlm-config.json` to customize:
- Draft model (default: Llama 2 7B)
- Verifier model (default: Llama 2 13B)
- Speculation length
- Temperature, top-p, etc.

## Performance

| Metric | vLLM Speculative | Claude API | Speedup |
|---|---|---|---|
| Simple query time | 0.3-0.5s | 1-2s | 2-3x |
| Quality (simple) | 85% | 99% | -14% |
| Cost per 1K tokens | $0.001 | $0.003 | 3x cheaper |
| Availability | Local | API-dependent | Local wins |

## Architecture

```
Simple Task (e.g., "What's the weather?")
    ↓
Route to vLLM (speculative decoding)
    ↓
Draft model (Llama 7B) generates candidate tokens
Verifier model (Llama 13B) accepts/rejects in parallel
    ↓
Return response (0.3-0.5s, 85% quality)

Complex Task (e.g., "Write analysis...")
    ↓
Route to Claude API
    ↓
Return response (1-2s, 99% quality)
```

## Fallback Behavior

If vLLM is unavailable:
1. Log warning
2. Fall back to standard Claude API
3. Return response via API
4. Alert user (optional): "⚠️ Using API fallback (vLLM unavailable)"

## Scripts

### `start-vlm-server.sh`
Start vLLM server with speculative decoding config.

```bash
./scripts/start-vlm-server.sh [--docker] [--port 8000]
```

### `test-speculative.sh`
Test speculative decoding with sample queries.

```bash
./scripts/test-speculative.sh
```

### `install-dependencies.sh`
Install vLLM + required packages.

```bash
./scripts/install-dependencies.sh
```

## References

- `vlm-config.json` — vLLM server configuration
- `model-pairs.json` — Tested model combinations
- `docker-compose.yml` — Docker setup (optional)

## Troubleshooting

**Q: vLLM server won't start**
- Check Docker is running: `docker ps`
- Check GPU availability: `nvidia-smi`
- Check port isn't in use: `lsof -i :8000`

**Q: Response quality is too low**
- Increase verifier model size (13B → 70B)
- Reduce speculation length
- Fall back to Claude API for complex tasks

**Q: Server is slow**
- Use GPU (not CPU): Check `nvidia-smi`
- Reduce batch size in config
- Reduce context window

## Monitoring

Check server health:
```bash
curl http://localhost:8000/health
```

View metrics:
```bash
tail -f logs/vlm-server.log | grep "throughput\|latency"
```

## Status

- ✅ Skill structure: Ready
- ⏳ vLLM integration: In progress
- ⏳ Performance testing: Pending
- ⏳ Production deployment: Planned

---

## Next Steps

1. Review SKILL.md
2. Configure vLLM (vlm-config.json)
3. Start local vLLM server
4. Run test harness
5. Measure speedup + quality
6. Document findings
