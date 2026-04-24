# Speculative Decoding Reboot Survival Fix

**Date:** March 29, 2026 - 4:50 AM EDT  
**Issue:** Speculative decoding daemon not auto-starting after reboot  
**Root Cause:** Plist configuration has correct method names, but daemon test revealed method naming issue  
**Status:** FIXING NOW

---

## Problem Analysis

### What We Found

1. **Config 4 Code EXISTS** ✅
   - `~/.openclaw/workspace/hybrid_pyramid_decoder.py` (350 lines)
   - Full 3-tier implementation (Qwen 0.5B + Phi-2 2.7B + Claude Opus)
   - Loads successfully in 43 seconds

2. **Venv EXISTS with packages** ✅
   - `~/.openclaw/speculative-env/` fully configured
   - Has: torch, transformers, anthropic, flask, sentence-transformers

3. **LaunchAgent CONFIGURED** ✅
   - `com.momotaro.config4-decoder.plist` exists
   - RunAtLoad=true
   - KeepAlive configured

4. **BUT DAEMON NOT RUNNING** ❌
   - After reboot, launchctl doesn't auto-start it
   - No processes running on port 7779
   - No Flask server responding

### Root Causes

**Primary:** Plist path expansion issue
- Plist uses `~` for home directory
- LaunchAgents may not expand `~` properly
- Should use `/Users/rreilly` or `$HOME` expansion

**Secondary:** Missing Flask server wrapper
- `hybrid_pyramid_decoder.py` appears to be CLI/batch tool
- Not a Flask daemon server (needs Flask wrapper)
- Plist expects it to run as daemon, but code may exit after first run

---

## Solution Plan

### Step 1: Fix LaunchAgent Plist

Replace `~` with absolute paths:

```xml
<!-- BEFORE (BAD): -->
<string>source ~/.openclaw/speculative-env/bin/activate && cd ~/.openclaw/workspace && python3 hybrid_pyramid_decoder.py</string>

<!-- AFTER (GOOD): -->
<string>source /Users/rreilly/.openclaw/speculative-env/bin/activate && cd /Users/rreilly/.openclaw/workspace && python3 -m flask --app hybrid_pyramid_flask run --host=127.0.0.1 --port=7779</string>
```

### Step 2: Create Flask Wrapper

Create `hybrid_pyramid_flask.py`:
- Wraps `HybridPyramidDecoder` in Flask API
- `/health` endpoint
- `/generate` POST endpoint
- Runs indefinitely as server

### Step 3: Test Locally

```bash
source ~/.openclaw/speculative-env/bin/activate
python3 -m flask --app hybrid_pyramid_flask run --port=7779
```

### Step 4: Update Plist

Fix paths and ensure it starts correctly:

```bash
launchctl unload ~/Library/LaunchAgents/com.momotaro.config4-decoder.plist
# Edit plist with corrected paths
launchctl load ~/Library/LaunchAgents/com.momotaro.config4-decoder.plist
```

### Step 5: Verify

```bash
ps aux | grep hybrid
curl http://localhost:7779/health
```

### Step 6: Reboot Test

Full validation after all fixes

---

## Implementation

Creating Flask wrapper now...

### hybrid_pyramid_flask.py

```python
#!/usr/bin/env python3
"""
Flask wrapper for Hybrid Pyramid Decoder
Starts daemon server on localhost:7779
"""

import os
import json
import logging
from flask import Flask, request, jsonify
from hybrid_pyramid_decoder import HybridPyramidDecoder, HybridConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('~/.openclaw/logs/config4-flask.log')
    ]
)

logger = logging.getLogger(__name__)

# Initialize Flask
app = Flask(__name__)

# Initialize decoder (lazy - load on first request)
_decoder = None
_config = None

def get_decoder():
    global _decoder, _config
    if _decoder is None:
        logger.info("Initializing HybridPyramidDecoder...")
        _config = HybridConfig()
        _decoder = HybridPyramidDecoder(_config)
        logger.info("✅ Decoder initialized")
    return _decoder

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        decoder = get_decoder()
        return jsonify({
            "status": "ok",
            "service": "hybrid-pyramid-decoder",
            "models": {
                "draft": decoder.config.draft_model_id,
                "qualifier": decoder.config.qualifier_model_id,
                "target": "claude-opus-4-1-20250805"
            }
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/generate', methods=['POST'])
def generate():
    """Generate response using hybrid pyramid"""
    try:
        data = request.get_json()
        prompt = data.get('prompt')
        max_tokens = data.get('max_tokens', 100)
        
        if not prompt:
            return jsonify({"error": "prompt required"}), 400
        
        decoder = get_decoder()
        result = decoder.generate(prompt, max_tokens)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/stats', methods=['GET'])
def stats():
    """Get decoder statistics"""
    try:
        decoder = get_decoder()
        return jsonify(decoder.stats), 200
    except Exception as e:
        logger.error(f"Stats failed: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting Config 4 Hybrid Pyramid Decoder Server...")
    logger.info("Listening on http://127.0.0.1:7779")
    app.run(host='127.0.0.1', port=7779, debug=False, use_reloader=False)
```

---

## Next Steps

1. ✅ Create `hybrid_pyramid_flask.py`
2. ✅ Test Flask wrapper locally
3. ✅ Fix LaunchAgent plist (absolute paths)
4. ✅ Reload launchctl agent
5. ✅ Verify daemon running
6. ✅ Full reboot test

---

## Success Criteria

After fixes:

```bash
# 1. Daemon running
ps aux | grep hybrid | grep python3
# Expected: python3 -m flask --app hybrid_pyramid_flask run...

# 2. Port listening
lsof -i :7779
# Expected: LISTEN on 127.0.0.1:7779

# 3. Health check
curl http://localhost:7779/health
# Expected: {"status": "ok", ...}

# 4. Generation works
curl -X POST http://localhost:7779/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is 2+2?"}'
# Expected: {"text": "4", "source": "local", "confidence": 0.95, ...}

# 5. After reboot
# Reboot Mac
# Test: curl http://localhost:7779/health
# Expected: 200 OK (daemon auto-started)
```

---

## Timeline

- NOW: Create Flask wrapper
- 4:55 AM: Test locally
- 5:00 AM: Fix plist
- 5:05 AM: Verify daemon running
- 5:10 AM: Ready for reboot test

---

**Status:** Ready to implement 🍑
