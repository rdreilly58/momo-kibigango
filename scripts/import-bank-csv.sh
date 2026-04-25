#!/usr/bin/env bash
# import-bank-csv.sh — Normalize bank CSVs into standard transaction format
# Usage: bash scripts/import-bank-csv.sh <csv-file> <bank: boa|capitalone|fidelity>

set -euo pipefail

FINANCE_DIR="$HOME/.openclaw/workspace/finances"
IMPORT_DIR="$FINANCE_DIR/imports"
IMPORT_LOG="$IMPORT_DIR/import-log.md"

# --- Validation ---

if [[ $# -lt 2 ]]; then
    echo "Usage: $0 <csv-file> <boa|capitalone|fidelity>"
    exit 1
fi

CSV_FILE="$1"
BANK="$2"

if [[ ! -f "$CSV_FILE" ]]; then
    echo "Error: File not found: $CSV_FILE"
    exit 1
fi

case "$BANK" in
    boa|capitalone|fidelity) ;;
    *)
        echo "Error: Unknown bank '$BANK'. Use: boa, capitalone, or fidelity"
        exit 1
        ;;
esac

mkdir -p "$IMPORT_DIR"

# Determine output file based on current month
MONTH_FILE="$IMPORT_DIR/$(date +%Y-%m)-transactions.csv"

# Create header if file doesn't exist
if [[ ! -f "$MONTH_FILE" ]]; then
    echo "date,description,amount,category,account" > "$MONTH_FILE"
fi

# --- Category guesser based on description ---
guess_category() {
    local desc
    desc="$(echo "$1" | tr '[:upper:]' '[:lower:]')"
    # Use if/elif with [[ ]] for pattern matching (handles spaces better than case)
    if [[ "$desc" == *rent* || "$desc" == *mortgage* || "$desc" == *property* || "$desc" == *hoa* ]]; then
        echo "housing"
    elif [[ "$desc" == *grocery* || "$desc" == *"whole foods"* || "$desc" == *trader* || "$desc" == *safeway* || "$desc" == *food* || "$desc" == *restaurant* || "$desc" == *doordash* || "$desc" == *grubhub* || "$desc" == *"uber eat"* || "$desc" == *mcdonald* || "$desc" == *starbuck* || "$desc" == *coffee* || "$desc" == *dunkin* || "$desc" == *chipotle* || "$desc" == *pizza* ]]; then
        echo "food"
    elif [[ "$desc" == *gas* || "$desc" == *shell* || "$desc" == *exxon* || "$desc" == *uber* || "$desc" == *lyft* || "$desc" == *metro* || "$desc" == *wmata* || "$desc" == *parking* || "$desc" == *toll* ]]; then
        echo "transport"
    elif [[ "$desc" == *electric* || "$desc" == *water* || "$desc" == *internet* || "$desc" == *comcast* || "$desc" == *verizon* || "$desc" == *"t-mobile"* || "$desc" == *phone* || "$desc" == *dominion* || "$desc" == *pepco* ]]; then
        echo "utilities"
    elif [[ "$desc" == *pharmacy* || "$desc" == *cvs* || "$desc" == *walgreen* || "$desc" == *doctor* || "$desc" == *medical* || "$desc" == *dental* || "$desc" == *health* || "$desc" == *hospital* ]]; then
        echo "healthcare"
    elif [[ "$desc" == *netflix* || "$desc" == *spotify* || "$desc" == *hulu* || "$desc" == *disney* || "$desc" == *hbo* || "$desc" == *movie* || "$desc" == *theater* || "$desc" == *concert* || "$desc" == *ticket* || "$desc" == *bar* || "$desc" == *brew* ]]; then
        echo "entertainment"
    elif [[ "$desc" == *subscription* || "$desc" == *membership* || "$desc" == *gym* || "$desc" == *fitness* || "$desc" == *github* || "$desc" == *aws* || "$desc" == *adobe* ]]; then
        echo "subscriptions"
    elif [[ "$desc" == *payment* || "$desc" == *"minimum pay"* ]]; then
        echo "debt-payments"
    elif [[ "$desc" == *transfer* || "$desc" == *saving* || "$desc" == *invest* || "$desc" == *fidelity* || "$desc" == *401k* || "$desc" == *ira* ]]; then
        echo "savings"
    else
        echo "misc"
    fi
}

# --- Bank-specific parsers ---
# Each outputs: date,description,amount,category,account

parse_boa() {
    # BoA format: Date,Description,Amount,Running Bal.
    # Skip header line, parse remaining
    tail -n +2 "$CSV_FILE" | while IFS=',' read -r date desc amount _rest; do
        # Clean fields
        date="$(echo "$date" | tr -d '"' | xargs)"
        desc="$(echo "$desc" | tr -d '"' | sed 's/,/ /g' | xargs)"
        amount="$(echo "$amount" | tr -d '"$' | xargs)"

        [[ -z "$date" || -z "$amount" ]] && continue

        # Normalize date from MM/DD/YYYY to YYYY-MM-DD
        if [[ "$date" =~ ^([0-9]{1,2})/([0-9]{1,2})/([0-9]{4})$ ]]; then
            date="$(printf '%04d-%02d-%02d' "${BASH_REMATCH[3]}" "${BASH_REMATCH[1]}" "${BASH_REMATCH[2]}")"
        fi

        category="$(guess_category "$desc")"
        echo "$date,\"$desc\",$amount,$category,boa"
    done
}

parse_capitalone() {
    # Capital One format: Transaction Date,Posted Date,Card No.,Description,Category,Debit,Credit
    tail -n +2 "$CSV_FILE" | while IFS=',' read -r txn_date _posted _card desc _cat debit credit _rest; do
        date="$(echo "$txn_date" | tr -d '"' | xargs)"
        desc="$(echo "$desc" | tr -d '"' | sed 's/,/ /g' | xargs)"
        debit="$(echo "$debit" | tr -d '"$' | xargs)"
        credit="$(echo "$credit" | tr -d '"$' | xargs)"

        [[ -z "$date" ]] && continue

        # Normalize date from YYYY-MM-DD (Capital One native) or MM/DD/YYYY
        if [[ "$date" =~ ^([0-9]{1,2})/([0-9]{1,2})/([0-9]{4})$ ]]; then
            date="$(printf '%04d-%02d-%02d' "${BASH_REMATCH[3]}" "${BASH_REMATCH[1]}" "${BASH_REMATCH[2]}")"
        fi

        # Debit = expense (negative), Credit = refund (positive)
        if [[ -n "$debit" && "$debit" != "0" ]]; then
            amount="-$debit"
        elif [[ -n "$credit" && "$credit" != "0" ]]; then
            amount="$credit"
        else
            continue
        fi

        category="$(guess_category "$desc")"
        echo "$date,\"$desc\",$amount,$category,capitalone"
    done
}

parse_fidelity() {
    # Fidelity format: Date,Action,Symbol,Description,Quantity,Price,Commission,Fees,Amount
    tail -n +2 "$CSV_FILE" | while IFS=',' read -r date action _symbol desc _qty _price _comm _fees amount _rest; do
        date="$(echo "$date" | tr -d '"' | xargs)"
        desc="$(echo "$desc" | tr -d '"' | sed 's/,/ /g' | xargs)"
        amount="$(echo "$amount" | tr -d '"$' | xargs)"
        action="$(echo "$action" | tr -d '"' | xargs)"

        [[ -z "$date" || -z "$amount" ]] && continue

        # Normalize date from MM/DD/YYYY to YYYY-MM-DD
        if [[ "$date" =~ ^([0-9]{1,2})/([0-9]{1,2})/([0-9]{4})$ ]]; then
            date="$(printf '%04d-%02d-%02d' "${BASH_REMATCH[3]}" "${BASH_REMATCH[1]}" "${BASH_REMATCH[2]}")"
        fi

        # Build description from action + desc
        full_desc="$action - $desc"
        category="$(guess_category "$full_desc")"
        echo "$date,\"$full_desc\",$amount,$category,fidelity"
    done
}

# --- Run parser ---

BEFORE_COUNT=0
if [[ -f "$MONTH_FILE" ]]; then
    BEFORE_COUNT=$(wc -l < "$MONTH_FILE")
fi

case "$BANK" in
    boa)         parse_boa >> "$MONTH_FILE" ;;
    capitalone)  parse_capitalone >> "$MONTH_FILE" ;;
    fidelity)    parse_fidelity >> "$MONTH_FILE" ;;
esac

AFTER_COUNT=$(wc -l < "$MONTH_FILE")
NEW_ROWS=$(( AFTER_COUNT - BEFORE_COUNT ))

echo "Imported $NEW_ROWS transactions from $BANK → $MONTH_FILE"

# --- Log the import ---

if [[ ! -f "$IMPORT_LOG" ]]; then
    echo "# Import Log" > "$IMPORT_LOG"
    echo "" >> "$IMPORT_LOG"
fi

echo "- **$(date '+%Y-%m-%d %H:%M')** | $BANK | $(basename "$CSV_FILE") | $NEW_ROWS rows → $(basename "$MONTH_FILE")" >> "$IMPORT_LOG"

echo "Import logged to $IMPORT_LOG"
