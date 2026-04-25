# Personal Finance System

Local-only financial tracking for Bob Reilly. All data is git-ignored — nothing here gets committed.

## Directory Structure

```
finances/
├── imports/          # Bank CSV imports + normalized transaction files
│   ├── YYYY-MM-transactions.csv   # Monthly normalized transactions
│   └── import-log.md              # Import history log
├── reports/          # Generated monthly/weekly reports
│   └── YYYY-MM-report.md
├── budgets/          # Monthly budget definitions
│   └── YYYY-MM-budget.json
├── credit-cards/     # Credit card tracking (balances, limits, due dates)
│   └── cards.json
├── debts/            # Debt tracking (all types)
│   └── debts.json
└── README.md         # This file
```

## Importing Bank Statements

### Supported Banks

| Bank | CSV Format | Download Location |
|------|-----------|-------------------|
| **Bank of America** | Date, Description, Amount, Running Bal | Online Banking → Statements → Download |
| **Capital One** | Transaction Date, Posted Date, Card No, Description, Category, Debit, Credit | Account → Statements → Download CSV |
| **Fidelity** | Date, Action, Symbol, Description, Quantity, Price, Commission, Fees, Amount | NetBenefits → Activity & Orders → Download |

### Import Steps

1. Download CSV from your bank's website
2. Run the import script:
   ```bash
   bash scripts/import-bank-csv.sh /path/to/downloaded.csv boa
   bash scripts/import-bank-csv.sh /path/to/downloaded.csv capitalone
   bash scripts/import-bank-csv.sh /path/to/downloaded.csv fidelity
   ```
3. Transactions are normalized and appended to `imports/YYYY-MM-transactions.csv`
4. Import is logged in `imports/import-log.md`

### Normalized Format

All imports are converted to:
```
date,description,amount,category,account
2026-04-15,WHOLE FOODS #123,-45.67,food,boa
```

- Negative amounts = money out (expenses)
- Positive amounts = money in (income/refunds)

## Expense Categories

| Category | Examples |
|----------|---------|
| housing | Rent, mortgage, property tax, HOA |
| food | Groceries, restaurants, delivery, coffee |
| transport | Gas, metro, Uber, car insurance, parking |
| utilities | Electric, water, internet, phone, gas |
| healthcare | Doctor, pharmacy, insurance premiums, dental |
| entertainment | Streaming, concerts, games, bars |
| subscriptions | Software, gym, memberships, news |
| debt-payments | Credit card payments, loan payments |
| savings | Transfers to savings, investments |
| misc | Everything else |

## Credit Card Tracking

### Workflow

1. **Set up cards** in `credit-cards/cards.json`:
   ```json
   {
     "cards": [
       {
         "name": "BoA Cash Rewards",
         "last4": "1234",
         "limit": 5000,
         "balance": 1200,
         "apr": 24.99,
         "due_date": 15,
         "min_payment": 35,
         "autopay": true
       }
     ]
   }
   ```
2. **Update balances** after each statement or import
3. **Monitor utilization** — stay under 30% for credit score health
4. **Track due dates** — the finance agent will remind you

## Debt Tracking

### Workflow

1. **Register debts** in `debts/debts.json` (credit cards, medical, personal loans)
2. **Run payoff analysis**:
   ```bash
   bash scripts/debt-tracker.sh summary          # Current snapshot
   bash scripts/debt-tracker.sh payoff avalanche  # Highest-interest-first plan
   bash scripts/debt-tracker.sh payoff snowball   # Smallest-balance-first plan
   ```
3. **Update after payments** — track progress month over month

### Debt Types
- Credit card balances (from `credit-cards/cards.json`)
- Medical bills
- Personal loans
- Any other obligations

## Monthly/Weekly Reports

### Generate a Monthly Report
```bash
bash scripts/finance-report.sh 2026-04    # Specific month
bash scripts/finance-report.sh             # Current month
```

Reports include:
- Spending by category vs budget
- Top expenses
- Credit card utilization summary
- Debt progress (paid down vs new charges)
- Month-over-month comparison

Output: `reports/YYYY-MM-report.md`

## Natural Language Usage

Talk to the OpenClaw finance agent naturally:
- "Spent $45 on groceries at Trader Joe's"
- "How much did I spend on food this month?"
- "Import my Capital One statement"
- "What's my total debt?"
- "Generate this month's report"
- "Am I over budget on entertainment?"
