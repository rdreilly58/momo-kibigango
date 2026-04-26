# Archive Log

Scripts moved here are NOT deleted — they are preserved for reference.
All moves performed 2026-04-25 as part of OpenClaw scripts directory consolidation.

## Batch: 2026-04-25 — Scripts directory audit + consolidation

### fast-find variants (keep fast-find-improved.sh)
- `fast-find.sh` — superseded by fast-find-improved.sh
- `fast-find-v2.sh` — intermediate version, superseded by fast-find-improved.sh

### 3-tier inference system (not in cron, not active)
- `debug-3tier.py` — debug tool for 3-tier inference, system not active
- `debug-3tier-with-flask.py` — Flask debug variant, system not active
- `simple-3tier-start.py` — simplified startup, superseded
- `start-3tier-daemon.sh` — daemon launcher, system not active
- `start-3tier-fixed.sh` — bugfix iteration, system not active
- `test-3tier-pyramid.py` — test suite for 3-tier system, not active
- `test-3tier-pyramid.sh` — shell wrapper for above, not active

### OpenRouter (not in active use)
- `spawn-with-openrouter.sh` — OpenRouter subagent spawning, not in cron
- `setup-subagent-openrouter.sh` — one-time setup, OpenRouter not active

### Memory tier system (replaced by memory-core plugin)
- `memory_hot_cache.py` — hot cache layer, replaced by memory-core plugin
- `memory_cold_store.py` — cold storage layer, replaced by memory-core plugin
- `memory_tier_manager.py` — tier orchestrator, replaced by memory-core plugin
- `memory_graph.py` — graph layer, replaced by memory-core plugin
- `memory_db.py` — DB layer, replaced by memory-core plugin

### Legacy memory search variants (active: memory_mcp_server.py, memory_search.py)
- `memory_search_hf.py` — HuggingFace embedding search, legacy variant
- `memory_search_wrapper.py` — wrapper around old search, legacy
- `memory_search_local` — legacy local search binary/script
- `memory_search_local.py` — local search Python variant, superseded

### ML training and inference (not in cron)
- `precompute_hidden_states.py` — precompute for speculative decoding, EC2 era
- `precompute_v2.py` — v2 precompute variant, EC2 era
- `train_drafter_cached.py` — drafter training with cache, EC2/TPU era
- `train_drafter_tpu_v6e.py` — TPU v6e training, EC2/TPU era (decommissioned)
- `mlx_inference.py` — MLX inference on Apple Silicon, not in cron
- `download_model.py` — model download helper, not active
- `benchmark-inference.py` — inference benchmark, not in cron
- `start-vlm-inference.sh` — VLM server start, not in cron
- `start-vlm-inference-fixed.sh` — bugfix iteration, not in cron
- `setup-vlm-mlx.sh` — VLM + MLX setup, one-time
- `poll_tpu_loss.sh` — TPU loss polling, EC2/TPU era (decommissioned)
- `provision_tpu_v6e.sh` — TPU provisioning, EC2/TPU era (decommissioned)
- `setup_tpu_v6e.sh` — TPU setup, EC2/TPU era (decommissioned)
- `ReDrafter_Training_Colab.ipynb` — Colab training notebook, not in cron

### RocketChat plugin test (not active)
- `rc-plugin-test.js` — RocketChat plugin integration test, not active

### Discord (not in cron)
- `discord_bot.py` — Discord bot, not in cron
- `discord_bot_simple.py` — simplified Discord bot, not in cron
- `run-discord-bot.sh` — Discord bot launcher, not in cron
- `validate_discord_config.py` — Discord config validator, one-time

### One-time setup scripts (already applied)
- `setup-staging-environment.sh` — staging env setup, already applied
- `setup-passwordless-sudo.sh` — sudo setup, already applied (via /etc/sudoers.d/momotaro)

### One-time cron migration scripts (already applied)
- `p1.1-add-timeouts-to-jobs.py` — cron timeout migration, already applied
- `apply-cron-update.sh` — cron update applier, already applied
- `cron-batch-add-timeouts.sh` — batch timeout addition, already applied

### Agent coordinator (replaced by OpenClaw native)
- `agent_coordinator.py` — multi-agent coordinator, replaced by OpenClaw native orchestration
- `agent_coordinator_test.py` — tests for above
