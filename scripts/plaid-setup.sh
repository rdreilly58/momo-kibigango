#!/usr/bin/env bash
# plaid-setup.sh — Scaffold for Plaid API integration (NOT ACTIVE)
# Target: 2-4 weeks from now (May/June 2026)
#
# This script documents the setup steps and validates prerequisites.
# It does NOT connect to Plaid yet.

set -euo pipefail

FINANCE_DIR="$HOME/.openclaw/workspace/finances"
CONFIG_TEMPLATE="$FINANCE_DIR/plaid-config.json.template"
CONFIG_FILE="$FINANCE_DIR/plaid-config.json"

echo "============================================"
echo "  Plaid Integration Setup — SCAFFOLD ONLY"
echo "============================================"
echo ""

# --- Step 1: Plaid Account ---
echo "STEP 1: Create Plaid Account"
echo "  → Go to https://dashboard.plaid.com/signup"
echo "  → Sign up for a developer account (free tier)"
echo "  → Note your client_id and secret from the dashboard"
echo ""

# --- Step 2: API Keys ---
echo "STEP 2: Store API Keys"
echo "  → After signup, store keys in macOS Keychain:"
echo "    security add-generic-password -s 'Openclaw-PLAID_CLIENT_ID' -a 'openclaw' -w 'YOUR_CLIENT_ID'"
echo "    security add-generic-password -s 'Openclaw-PLAID_SECRET' -a 'openclaw' -w 'YOUR_SECRET'"
echo ""

# --- Step 3: Config ---
echo "STEP 3: Configure"
if [[ -f "$CONFIG_FILE" ]]; then
    echo "  ✅ plaid-config.json exists"
else
    echo "  → Copy template to config:"
    echo "    cp $CONFIG_TEMPLATE $CONFIG_FILE"
    echo "  → Edit $CONFIG_FILE with your client_id and secret"
fi
echo ""

# --- Step 4: Link Accounts ---
echo "STEP 4: Link Bank Accounts"
echo "  → Use Plaid Link (web component) to connect each bank"
echo "  → Institution IDs pre-configured in template:"
echo "    • Bank of America:    ins_127989"
echo "    • Capital One:        ins_128026"
echo "    • Fidelity:           ins_12"
echo "  → Each linked account generates an access_token and item_id"
echo "  → Store these in plaid-config.json"
echo ""

# --- Step 5: MCP Integration ---
echo "STEP 5: MCP Integration (Future)"
echo "  Option A: Build a BankSync MCP server"
echo "    → Python FastMCP server wrapping plaid-python SDK"
echo "    → Tools: sync_transactions, get_balances, list_accounts"
echo "    → Register in ~/.claude/settings.json under mcpServers"
echo ""
echo "  Option B: Direct Plaid MCP"
echo "    → Use community plaid-mcp package if available"
echo "    → Configure with access tokens from Step 4"
echo ""

# --- Prerequisites Check ---
echo "============================================"
echo "  Prerequisites Check"
echo "============================================"

# Python
if command -v python3 &>/dev/null; then
    echo "  ✅ python3: $(python3 --version 2>&1)"
else
    echo "  ❌ python3: not found"
fi

# pip/plaid-python
if python3 -c "import plaid" 2>/dev/null; then
    echo "  ✅ plaid-python: installed"
else
    echo "  ⏳ plaid-python: not installed (pip install plaid-python)"
fi

# Keychain keys
for key in PLAID_CLIENT_ID PLAID_SECRET; do
    if security find-generic-password -s "Openclaw-$key" -a "openclaw" &>/dev/null 2>&1; then
        echo "  ✅ Keychain: $key found"
    else
        echo "  ⏳ Keychain: $key not set yet"
    fi
done

# Config file
if [[ -f "$CONFIG_FILE" ]]; then
    echo "  ✅ Config: plaid-config.json exists"
else
    echo "  ⏳ Config: template only (not copied yet)"
fi

echo ""
echo "STATUS: Scaffold ready. Not active until Plaid account is created."
echo "TARGET: May-June 2026"
