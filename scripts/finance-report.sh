#!/usr/bin/env bash
# finance-report.sh — Generate monthly finance report
# Usage:
#   bash scripts/finance-report.sh            # Current month
#   bash scripts/finance-report.sh 2026-04    # Specific month

set -euo pipefail

FINANCE_DIR="$HOME/.openclaw/workspace/finances"
IMPORT_DIR="$FINANCE_DIR/imports"
REPORT_DIR="$FINANCE_DIR/reports"
BUDGET_DIR="$FINANCE_DIR/budgets"
DEBTS_FILE="$FINANCE_DIR/debts/debts.json"
CARDS_FILE="$FINANCE_DIR/credit-cards/cards.json"

export MONTH="${1:-$(date +%Y-%m)}"
export TXN_FILE="$IMPORT_DIR/${MONTH}-transactions.csv"
export BUDGET_FILE="$BUDGET_DIR/${MONTH}-budget.json"
export REPORT_FILE="$REPORT_DIR/${MONTH}-report.md"
export DEBTS_FILE
export CARDS_FILE

mkdir -p "$REPORT_DIR"

if ! command -v python3 &>/dev/null; then
    echo "Error: python3 required"
    exit 1
fi

python3 << 'PYEOF'
import json, csv, os, sys
from collections import defaultdict
from datetime import datetime

month = os.environ.get("MONTH", "")
txn_file = os.environ.get("TXN_FILE", "")
budget_file = os.environ.get("BUDGET_FILE", "")
report_file = os.environ.get("REPORT_FILE", "")
debts_file = os.environ.get("DEBTS_FILE", "")
cards_file = os.environ.get("CARDS_FILE", "")

# Parse month for display
try:
    month_display = datetime.strptime(month, "%Y-%m").strftime("%B %Y")
except ValueError:
    month_display = month

lines = []
lines.append(f"# Financial Report — {month_display}")
lines.append(f"")
lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
lines.append(f"")

# --- Transactions ---
spending_by_cat = defaultdict(float)
income_by_cat = defaultdict(float)
transactions = []
total_expenses = 0
total_income = 0

if os.path.exists(txn_file):
    with open(txn_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                amount = float(row.get("amount", "0").replace("$", "").replace(",", ""))
            except ValueError:
                continue
            cat = row.get("category", "misc")
            desc = row.get("description", "").strip('"')
            date = row.get("date", "")
            account = row.get("account", "")

            transactions.append({"date": date, "desc": desc, "amount": amount, "category": cat, "account": account})

            if amount < 0:
                spending_by_cat[cat] += abs(amount)
                total_expenses += abs(amount)
            else:
                income_by_cat[cat] += amount
                total_income += amount

    lines.append(f"## Overview")
    lines.append(f"")
    lines.append(f"| Metric | Amount |")
    lines.append(f"|--------|--------|")
    lines.append(f"| Total Income | ${total_income:,.2f} |")
    lines.append(f"| Total Expenses | ${total_expenses:,.2f} |")
    lines.append(f"| Net | ${total_income - total_expenses:,.2f} |")
    lines.append(f"| Transactions | {len(transactions)} |")
    lines.append(f"")

    # --- Spending by Category ---
    lines.append(f"## Spending by Category")
    lines.append(f"")

    # Load budget if available
    budgets = {}
    if os.path.exists(budget_file):
        with open(budget_file) as f:
            budget_data = json.load(f)
            budgets = {b["category"]: b["limit"] for b in budget_data.get("budgets", [])}

    lines.append(f"| Category | Spent | Budget | Status |")
    lines.append(f"|----------|-------|--------|--------|")

    for cat in sorted(spending_by_cat, key=spending_by_cat.get, reverse=True):
        spent = spending_by_cat[cat]
        if cat in budgets:
            budget_limit = budgets[cat]
            pct = (spent / budget_limit) * 100
            status = f"{pct:.0f}%"
            if pct > 100:
                status += " ⚠️ OVER"
            elif pct > 80:
                status += " ⚡ close"
        else:
            budget_limit = "—"
            status = "no budget"
            budget_limit_str = "—"

        budget_str = f"${budget_limit:,.2f}" if isinstance(budget_limit, (int, float)) else "—"
        lines.append(f"| {cat} | ${spent:,.2f} | {budget_str} | {status} |")

    lines.append(f"")

    # --- Top Expenses ---
    expenses = [t for t in transactions if t["amount"] < 0]
    expenses.sort(key=lambda x: x["amount"])
    top = expenses[:10]

    if top:
        lines.append(f"## Top 10 Expenses")
        lines.append(f"")
        lines.append(f"| Date | Description | Amount | Category |")
        lines.append(f"|------|-------------|--------|----------|")
        for t in top:
            lines.append(f"| {t['date']} | {t['desc'][:40]} | ${abs(t['amount']):,.2f} | {t['category']} |")
        lines.append(f"")

else:
    lines.append(f"## Transactions")
    lines.append(f"")
    lines.append(f"No transaction file found for {month}.")
    lines.append(f"Import bank statements first: `bash scripts/import-bank-csv.sh <file> <bank>`")
    lines.append(f"")

# --- Credit Card Utilization ---
lines.append(f"## Credit Card Utilization")
lines.append(f"")

if os.path.exists(cards_file):
    with open(cards_file) as f:
        cards_data = json.load(f)

    cards = cards_data.get("cards", [])
    if cards:
        lines.append(f"| Card | Balance | Limit | Utilization | Due |")
        lines.append(f"|------|---------|-------|-------------|-----|")
        for c in cards:
            bal = c.get("balance", 0)
            limit = c.get("limit", c.get("credit_limit", 1))
            util = (bal / limit * 100) if limit > 0 else 0
            flag = " ⚠️" if util > 30 else ""
            lines.append(f"| {c['name']} | ${bal:,.2f} | ${limit:,.0f} | {util:.1f}%{flag} | {c.get('due_date', '—')}th |")
        lines.append(f"")
    else:
        lines.append(f"No credit cards configured. Add them to `finances/credit-cards/cards.json`.")
        lines.append(f"")
else:
    lines.append(f"No credit card data found. Create `finances/credit-cards/cards.json` to track cards.")
    lines.append(f"")

# --- Debt Progress ---
lines.append(f"## Debt Progress")
lines.append(f"")

if os.path.exists(debts_file):
    with open(debts_file) as f:
        debts_data = json.load(f)

    active_debts = [d for d in debts_data.get("debts", []) if d.get("balance", 0) > 0]
    if active_debts:
        total_debt = sum(d["balance"] for d in active_debts)
        total_min = sum(d["minimum_payment"] for d in active_debts)
        monthly_int = sum(d["balance"] * (d["apr"] / 100 / 12) for d in active_debts)

        lines.append(f"| Metric | Value |")
        lines.append(f"|--------|-------|")
        lines.append(f"| Active debts | {len(active_debts)} |")
        lines.append(f"| Total debt | ${total_debt:,.2f} |")
        lines.append(f"| Monthly minimums | ${total_min:,.2f} |")
        lines.append(f"| Monthly interest (est.) | ${monthly_int:,.2f} |")

        # Check if any debt payments were made this month
        debt_payments = spending_by_cat.get("debt-payments", 0)
        if debt_payments > 0:
            lines.append(f"| Debt payments this month | ${debt_payments:,.2f} |")
            net_progress = debt_payments - monthly_int
            if net_progress > 0:
                lines.append(f"| Principal paid down | ${net_progress:,.2f} ✅ |")
            else:
                lines.append(f"| Net progress | -${abs(net_progress):,.2f} ⚠️ (interest > payments) |")

        lines.append(f"")
    else:
        lines.append(f"No active debts. Debt-free! 🎉")
        lines.append(f"")
else:
    lines.append(f"No debt tracking file found. Create `finances/debts/debts.json`.")
    lines.append(f"")

# --- Footer ---
lines.append(f"---")
lines.append(f"*Run `bash scripts/debt-tracker.sh payoff avalanche` for full payoff analysis.*")

report = "\n".join(lines) + "\n"

with open(report_file, "w") as f:
    f.write(report)

print(f"Report written to {report_file}")
print(f"  Transactions: {len(transactions)} | Expenses: ${total_expenses:,.2f} | Income: ${total_income:,.2f}")
PYEOF
