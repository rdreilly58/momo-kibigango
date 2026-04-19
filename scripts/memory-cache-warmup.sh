#!/bin/bash
# Memory Search Cache Warmup
# Pre-computes embeddings for common query patterns
# Run after reindex or on startup

export GEMINI_API_KEY=$(grep GEMINI_API_KEY ~/.openclaw/.env | cut -d= -f2)

echo "Warming up memory search cache..."

# Common queries Bob asks
QUERIES=(
    "AA meetings schedule Zoom"
    "Leidos work team lead"
    "email sending Gmail app password"
    "Rocket.Chat configuration"
    "calendar events today"
    "momo-kibidango speculative decoding"
    "printer Brother print document"
    "API keys credentials secrets"
    "never infer dates lesson"
    "password manager Apple"
    "Roblox game development"
    "morning briefing evening briefing"
    "sudo permissions whitelist"
    "PDF generation WeasyPrint"
    "ReillyDesignStudio Vercel deploy"
)

for q in "${QUERIES[@]}"; do
    openclaw memory search "$q" --limit 1 --json > /dev/null 2>&1
    echo "  ✓ $q"
done

echo "Cache warmup complete (${#QUERIES[@]} queries)"
