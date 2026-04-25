#!/usr/bin/env bash
# test_finance.sh — Validate the personal finance system
# Tier: 1
set -euo pipefail

PASS=0
FAIL=0
WORKSPACE="$HOME/.openclaw/workspace"

pass() { ((PASS++)); echo "  ✅ $1"; }
fail() { ((FAIL++)); echo "  ❌ $1"; }

echo "========================================"
echo "  Finance System Test Suite"
echo "========================================"
echo ""

# --- 1. Agent file ---
echo "1. Finance Agent"
if [[ -f "$HOME/.claude/agents/finance.md" ]]; then
    pass "finance.md exists"
    if head -5 "$HOME/.claude/agents/finance.md" | grep -q "^name: finance"; then
        pass "has name: finance in frontmatter"
    else
        fail "missing name in frontmatter"
    fi
    if head -5 "$HOME/.claude/agents/finance.md" | grep -q "model: sonnet"; then
        pass "model is sonnet"
    else
        fail "model is not sonnet"
    fi
    if grep -q "expense-tracker-pro" "$HOME/.claude/agents/finance.md"; then
        pass "references expense-tracker-pro skill"
    else
        fail "missing expense-tracker-pro skill reference"
    fi
    if grep -q "intelligent-budget-tracker" "$HOME/.claude/agents/finance.md"; then
        pass "references intelligent-budget-tracker skill"
    else
        fail "missing intelligent-budget-tracker skill reference"
    fi
    if grep -q "personal-finance" "$HOME/.claude/agents/finance.md"; then
        pass "references personal-finance skill"
    else
        fail "missing personal-finance skill reference"
    fi
else
    fail "finance.md not found"
fi
echo ""

# --- 2. Directory structure ---
echo "2. Directory Structure"
for dir in imports reports budgets credit-cards debts; do
    if [[ -d "$WORKSPACE/finances/$dir" ]]; then
        pass "finances/$dir/ exists"
    else
        fail "finances/$dir/ missing"
    fi
done

if [[ -f "$WORKSPACE/finances/.gitignore" ]]; then
    pass ".gitignore in finances/"
else
    fail ".gitignore missing"
fi

if [[ -f "$WORKSPACE/finances/README.md" ]]; then
    pass "README.md exists"
else
    fail "README.md missing"
fi
echo ""

# --- 3. Import script ---
echo "3. CSV Import Script"
if [[ -f "$WORKSPACE/scripts/import-bank-csv.sh" ]]; then
    pass "import-bank-csv.sh exists"
    if [[ -x "$WORKSPACE/scripts/import-bank-csv.sh" ]]; then
        pass "import-bank-csv.sh is executable"
    else
        fail "import-bank-csv.sh not executable"
    fi

    # Test usage message (script exits 1 on no args)
    USAGE_OUT=$(bash "$WORKSPACE/scripts/import-bank-csv.sh" 2>&1 || true)
    if echo "$USAGE_OUT" | grep -q "Usage"; then
        pass "shows usage on no args"
    else
        fail "no usage message"
    fi

    # Test with a fake CSV (BoA format)
    TMPCSV=$(mktemp /tmp/test-boa-XXXXXXXX).csv
    echo 'Date,Description,Amount,Running Bal.' > "$TMPCSV"
    echo '04/15/2026,WHOLE FOODS #123,-45.67,1234.56' >> "$TMPCSV"
    echo '04/16/2026,STARBUCKS,-4.75,1229.81' >> "$TMPCSV"

    TEST_OUTPUT=$(bash "$WORKSPACE/scripts/import-bank-csv.sh" "$TMPCSV" boa 2>&1)
    if echo "$TEST_OUTPUT" | grep -q "Imported 2 transactions"; then
        pass "BoA import: 2 transactions imported"
    else
        fail "BoA import: unexpected output: $TEST_OUTPUT"
    fi

    # Verify normalized output
    MONTH_FILE="$WORKSPACE/finances/imports/$(date +%Y-%m)-transactions.csv"
    if [[ -f "$MONTH_FILE" ]]; then
        if grep -q "WHOLE FOODS" "$MONTH_FILE"; then
            pass "BoA import: transaction in normalized file"
        else
            fail "BoA import: transaction not found in normalized file"
        fi
        if grep -q "food" "$MONTH_FILE"; then
            pass "BoA import: auto-categorized as food"
        else
            fail "BoA import: category not detected"
        fi
    else
        fail "monthly transaction file not created"
    fi

    # Test import log
    if [[ -f "$WORKSPACE/finances/imports/import-log.md" ]]; then
        pass "import-log.md created"
    else
        fail "import-log.md not created"
    fi

    rm -f "$TMPCSV"
else
    fail "import-bank-csv.sh not found"
fi
echo ""

# --- 4. Debt tracker ---
echo "4. Debt Tracker"
if [[ -f "$WORKSPACE/finances/debts/debts.json" ]]; then
    pass "debts.json exists"
    if python3 -c "import json; json.load(open('$WORKSPACE/finances/debts/debts.json'))" 2>/dev/null; then
        pass "debts.json is valid JSON"
    else
        fail "debts.json is invalid JSON"
    fi
else
    fail "debts.json not found"
fi

if [[ -f "$WORKSPACE/scripts/debt-tracker.sh" ]]; then
    pass "debt-tracker.sh exists"
    if [[ -x "$WORKSPACE/scripts/debt-tracker.sh" ]]; then
        pass "debt-tracker.sh is executable"
    else
        fail "debt-tracker.sh not executable"
    fi

    # Test summary command
    if bash "$WORKSPACE/scripts/debt-tracker.sh" summary 2>&1 | grep -q "DEBT SUMMARY\|debt-free"; then
        pass "debt-tracker summary runs"
    else
        fail "debt-tracker summary failed"
    fi

    # Test payoff command
    if bash "$WORKSPACE/scripts/debt-tracker.sh" payoff avalanche 2>&1 | grep -q "PAYOFF PLAN\|No active"; then
        pass "debt-tracker payoff runs"
    else
        fail "debt-tracker payoff failed"
    fi

    # Test report command
    if bash "$WORKSPACE/scripts/debt-tracker.sh" report 2>&1 | grep -q "report written\|Debt Report\|Debt-free"; then
        pass "debt-tracker report runs"
    else
        fail "debt-tracker report failed"
    fi
else
    fail "debt-tracker.sh not found"
fi
echo ""

# --- 5. Finance report ---
echo "5. Monthly Report Generator"
if [[ -f "$WORKSPACE/scripts/finance-report.sh" ]]; then
    pass "finance-report.sh exists"
    if [[ -x "$WORKSPACE/scripts/finance-report.sh" ]]; then
        pass "finance-report.sh is executable"
    else
        fail "finance-report.sh not executable"
    fi

    # Run it (uses transactions from BoA test above)
    if bash "$WORKSPACE/scripts/finance-report.sh" 2>&1 | grep -q "Report written"; then
        pass "finance-report.sh generates report"
    else
        fail "finance-report.sh failed to generate"
    fi

    REPORT="$WORKSPACE/finances/reports/$(date +%Y-%m)-report.md"
    if [[ -f "$REPORT" ]]; then
        pass "report file created"
        if grep -q "Spending by Category" "$REPORT"; then
            pass "report contains spending breakdown"
        else
            fail "report missing spending breakdown"
        fi
    else
        fail "report file not created"
    fi
else
    fail "finance-report.sh not found"
fi
echo ""

# --- 6. Plaid scaffold ---
echo "6. Plaid Integration Scaffold"
if [[ -f "$WORKSPACE/finances/plaid-config.json.template" ]]; then
    pass "plaid-config.json.template exists"
    if python3 -c "import json; json.load(open('$WORKSPACE/finances/plaid-config.json.template'))" 2>/dev/null; then
        pass "template is valid JSON"
    else
        fail "template is invalid JSON"
    fi
    if grep -q "ins_127989" "$WORKSPACE/finances/plaid-config.json.template"; then
        pass "has BoA institution ID"
    else
        fail "missing BoA institution ID"
    fi
else
    fail "plaid-config.json.template not found"
fi

if [[ -f "$WORKSPACE/scripts/plaid-setup.sh" ]]; then
    pass "plaid-setup.sh exists"
    if [[ -x "$WORKSPACE/scripts/plaid-setup.sh" ]]; then
        pass "plaid-setup.sh is executable"
    else
        fail "plaid-setup.sh not executable"
    fi
else
    fail "plaid-setup.sh not found"
fi
echo ""

# --- 7. CLAUDE.md wiring ---
echo "7. CLAUDE.md & AGENT-WIRING.md"
if grep -q "finance" "$WORKSPACE/CLAUDE.md"; then
    pass "CLAUDE.md references finance agent"
else
    fail "CLAUDE.md missing finance agent"
fi

if grep -q "finance" "$WORKSPACE/AGENT-WIRING.md"; then
    pass "AGENT-WIRING.md references finance agent"
else
    fail "AGENT-WIRING.md missing finance agent"
fi

if grep -q "5 agents" "$WORKSPACE/AGENT-WIRING.md"; then
    pass "AGENT-WIRING.md updated to 5 agents"
else
    fail "AGENT-WIRING.md still says 4 agents"
fi
echo ""

# --- Summary ---
TOTAL=$((PASS + FAIL))
echo "========================================"
echo "  Results: $PASS/$TOTAL passed, $FAIL failed"
echo "========================================"

if [[ $FAIL -gt 0 ]]; then
    exit 1
fi
