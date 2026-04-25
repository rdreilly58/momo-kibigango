#!/usr/bin/env bash
# debt-tracker.sh — Track debts, calculate payoff timelines
# Usage:
#   bash scripts/debt-tracker.sh summary                    # Show all debts
#   bash scripts/debt-tracker.sh payoff avalanche [extra]   # Highest-interest-first payoff plan
#   bash scripts/debt-tracker.sh payoff snowball [extra]    # Smallest-balance-first payoff plan
#   bash scripts/debt-tracker.sh add                        # Add a new debt (interactive prompts via args)
#   bash scripts/debt-tracker.sh update <id> <balance>      # Update a debt balance
#   bash scripts/debt-tracker.sh report                     # Generate debt summary report

set -euo pipefail

FINANCE_DIR="$HOME/.openclaw/workspace/finances"
DEBTS_FILE="$FINANCE_DIR/debts/debts.json"
REPORT_DIR="$FINANCE_DIR/reports"

if [[ ! -f "$DEBTS_FILE" ]]; then
    echo "Error: No debts file found at $DEBTS_FILE"
    echo "Initialize with: finances/debts/debts.json"
    exit 1
fi

# Check for python3 (needed for JSON parsing)
if ! command -v python3 &>/dev/null; then
    echo "Error: python3 required for JSON processing"
    exit 1
fi

CMD="${1:-summary}"

case "$CMD" in
    summary)
        python3 -c "
import json, sys
with open('$DEBTS_FILE') as f:
    data = json.load(f)

debts = [d for d in data['debts'] if d['balance'] > 0]
if not debts:
    print('No active debts. You are debt-free!')
    sys.exit(0)

total_balance = sum(d['balance'] for d in debts)
total_minimum = sum(d['minimum_payment'] for d in debts)

print('=' * 60)
print('DEBT SUMMARY')
print('=' * 60)
print(f'Last updated: {data[\"last_updated\"]}')
print(f'Active debts: {len(debts)}')
print(f'Total balance: \${total_balance:,.2f}')
print(f'Total minimum payments: \${total_minimum:,.2f}/mo')
print()

for d in sorted(debts, key=lambda x: x['balance'], reverse=True):
    dtype = d['type'].replace('_', ' ').title()
    print(f'  {d[\"name\"]} ({dtype})')
    print(f'    Balance: \${d[\"balance\"]:,.2f} | APR: {d[\"apr\"]}% | Min: \${d[\"minimum_payment\"]}/mo | Due: {d[\"due_date\"]}th')
    if d['type'] == 'credit_card' and 'credit_limit' in d:
        util = (d['balance'] / d['credit_limit']) * 100
        flag = ' ⚠️' if util > 30 else ''
        print(f'    Utilization: {util:.1f}% of \${d[\"credit_limit\"]:,.0f}{flag}')
    print()

# Monthly interest estimate
monthly_interest = sum(d['balance'] * (d['apr'] / 100 / 12) for d in debts)
print(f'Estimated monthly interest: \${monthly_interest:,.2f}')
print('=' * 60)
"
        ;;

    payoff)
        METHOD="${2:-avalanche}"
        EXTRA="${3:-0}"

        python3 -c "
import json, sys, math

with open('$DEBTS_FILE') as f:
    data = json.load(f)

debts = [d.copy() for d in data['debts'] if d['balance'] > 0]
if not debts:
    print('No active debts!')
    sys.exit(0)

method = '$METHOD'
extra = float('$EXTRA')

if method == 'avalanche':
    debts.sort(key=lambda x: x['apr'], reverse=True)
    label = 'AVALANCHE (highest interest first)'
elif method == 'snowball':
    debts.sort(key=lambda x: x['balance'])
    label = 'SNOWBALL (smallest balance first)'
else:
    print(f'Unknown method: {method}. Use avalanche or snowball.')
    sys.exit(1)

print('=' * 60)
print(f'PAYOFF PLAN: {label}')
if extra > 0:
    print(f'Extra monthly payment: \${extra:,.2f}')
print('=' * 60)
print()

total_paid = 0
total_interest = 0
month = 0
max_months = 360  # 30 year cap

# Simulate month by month
active = [d.copy() for d in debts]
order_paid = []

while any(d['balance'] > 0 for d in active) and month < max_months:
    month += 1

    # Apply interest
    for d in active:
        if d['balance'] > 0:
            interest = d['balance'] * (d['apr'] / 100 / 12)
            d['balance'] += interest
            total_interest += interest

    # Pay minimums on all
    freed = 0
    for d in active:
        if d['balance'] > 0:
            payment = min(d['minimum_payment'], d['balance'])
            d['balance'] -= payment
            total_paid += payment
            if d['balance'] <= 0.01:
                d['balance'] = 0
                freed += d['minimum_payment'] - payment
                order_paid.append((d['name'], month))

    # Apply extra + freed to target debt
    available = extra + freed
    for d in active:
        if d['balance'] > 0 and available > 0:
            payment = min(available, d['balance'])
            d['balance'] -= payment
            total_paid += payment
            available -= payment
            if d['balance'] <= 0.01:
                d['balance'] = 0
                order_paid.append((d['name'], month))

print('Payoff order:')
for name, m in order_paid:
    years = m // 12
    months = m % 12
    time_str = f'{years}y {months}m' if years > 0 else f'{months}m'
    print(f'  {name}: paid off in {time_str} (month {m})')

print()
print(f'Total months to debt-free: {month}')
years = month // 12
months_rem = month % 12
print(f'That is: {years} years, {months_rem} months')
print(f'Total paid: \${total_paid:,.2f}')
print(f'Total interest paid: \${total_interest:,.2f}')
print('=' * 60)
"
        ;;

    update)
        DEBT_ID="${2:-}"
        NEW_BALANCE="${3:-}"
        if [[ -z "$DEBT_ID" || -z "$NEW_BALANCE" ]]; then
            echo "Usage: $0 update <debt-id> <new-balance>"
            exit 1
        fi

        python3 -c "
import json
with open('$DEBTS_FILE') as f:
    data = json.load(f)

found = False
for d in data['debts']:
    if d['id'] == '$DEBT_ID':
        old = d['balance']
        d['balance'] = float('$NEW_BALANCE')
        found = True
        print(f'Updated {d[\"name\"]}: \${old:,.2f} → \${d[\"balance\"]:,.2f}')
        break

if not found:
    print(f'Debt ID \"$DEBT_ID\" not found')
    raise SystemExit(1)

from datetime import date
data['last_updated'] = str(date.today())

with open('$DEBTS_FILE', 'w') as f:
    json.dump(data, f, indent=2)
    f.write('\n')
"
        ;;

    report)
        mkdir -p "$REPORT_DIR"
        REPORT_FILE="$REPORT_DIR/$(date +%Y-%m)-debt-report.md"

        python3 -c "
import json
from datetime import date

with open('$DEBTS_FILE') as f:
    data = json.load(f)

debts = [d for d in data['debts'] if d['balance'] > 0]
today = date.today()

lines = []
lines.append(f'# Debt Report — {today.strftime(\"%B %Y\")}')
lines.append(f'')
lines.append(f'Generated: {today}')
lines.append(f'')

if not debts:
    lines.append('**Debt-free!** No active debts.')
else:
    total = sum(d['balance'] for d in debts)
    total_min = sum(d['minimum_payment'] for d in debts)
    monthly_int = sum(d['balance'] * (d['apr'] / 100 / 12) for d in debts)

    lines.append(f'## Summary')
    lines.append(f'')
    lines.append(f'| Metric | Value |')
    lines.append(f'|--------|-------|')
    lines.append(f'| Active debts | {len(debts)} |')
    lines.append(f'| Total balance | \${total:,.2f} |')
    lines.append(f'| Monthly minimums | \${total_min:,.2f} |')
    lines.append(f'| Monthly interest (est.) | \${monthly_int:,.2f} |')
    lines.append(f'')
    lines.append(f'## Detail')
    lines.append(f'')
    lines.append(f'| Name | Type | Balance | APR | Min Payment | Due |')
    lines.append(f'|------|------|---------|-----|-------------|-----|')
    for d in sorted(debts, key=lambda x: x['apr'], reverse=True):
        dtype = d['type'].replace('_', ' ').title()
        lines.append(f'| {d[\"name\"]} | {dtype} | \${d[\"balance\"]:,.2f} | {d[\"apr\"]}% | \${d[\"minimum_payment\"]} | {d[\"due_date\"]}th |')

print('\n'.join(lines))
" > "$REPORT_FILE"

        echo "Debt report written to $REPORT_FILE"
        ;;

    *)
        echo "Usage: $0 <summary|payoff|update|report>"
        echo ""
        echo "Commands:"
        echo "  summary                     Show all debts"
        echo "  payoff <avalanche|snowball> [extra]  Payoff timeline"
        echo "  update <id> <balance>       Update a debt balance"
        echo "  report                      Generate debt report"
        exit 1
        ;;
esac
