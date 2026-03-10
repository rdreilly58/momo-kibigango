#!/bin/bash
# print.sh — Print files to local Brother printers
#
# Usage:
#   print.sh [OPTIONS] FILE [FILE...]
#
# Options:
#   -p PRINTER    Printer name (default: Brother_MFC_L2700DW_series)
#   -c COPIES     Number of copies (default: 1)
#   -o OPTION     lp print option (can be repeated)
#   -l, --list    List available printers
#   -h, --help    Show this help
#
# Examples:
#   print.sh document.pdf
#   print.sh -p Brother_HL_L2350DW_series -c 2 report.pdf
#   print.sh --list

set -euo pipefail

PRINTER="Brother_MFC_L2700DW_series"
COPIES=1
LP_OPTIONS=()

while [[ $# -gt 0 ]]; do
  case $1 in
    -p|--printer)
      PRINTER="$2"
      shift 2
      ;;
    -c|--copies)
      COPIES="$2"
      shift 2
      ;;
    -o)
      LP_OPTIONS+=("-o" "$2")
      shift 2
      ;;
    -l|--list)
      echo "Available printers:"
      lpstat -p -d | grep "printer " | awk '{print "  " $2}' | sed 's/ is.*//'
      echo ""
      lpstat -d | awk '{print "Default: " $NF}'
      exit 0
      ;;
    -h|--help)
      head -30 "$0" | tail -20
      exit 0
      ;;
    -*)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
    *)
      break
      ;;
  esac
done

if [[ $# -eq 0 ]]; then
  echo "Error: no files specified" >&2
  echo "Use: print.sh [OPTIONS] FILE [FILE...]" >&2
  exit 1
fi

# Check if printer exists
if ! lpstat -p | grep -q "$PRINTER"; then
  echo "Error: printer '$PRINTER' not found" >&2
  echo "Available printers:" >&2
  lpstat -p | grep "printer " | awk '{print "  " $2}' | sed 's/ is.*//' >&2
  exit 1
fi

echo "[print] Sending to: $PRINTER (copies: $COPIES)"
for file in "$@"; do
  if [[ ! -f "$file" ]]; then
    echo "[print] Error: file not found: $file" >&2
    exit 1
  fi
  echo "[print] $file"
  if [[ ${#LP_OPTIONS[@]} -gt 0 ]]; then
    lp -d "$PRINTER" -n "$COPIES" "${LP_OPTIONS[@]}" "$file"
  else
    lp -d "$PRINTER" -n "$COPIES" "$file"
  fi
done

echo "[print] Done"
