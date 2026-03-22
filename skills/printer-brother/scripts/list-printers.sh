#!/bin/bash
# list-printers.sh — List available Brother printers with status

set -uo pipefail

echo "📠 Available Brother Printers"
echo "=============================="
echo ""

lpstat -v | grep -i brother | while read line; do
    # Extract printer name and device URI
    printer_name=$(echo "$line" | awk -F': ' '{print $1}' | sed 's/device for //')
    device_uri=$(echo "$line" | awk -F': ' '{print $2}')
    
    # Get status
    status=$(lpstat -p "$printer_name" 2>/dev/null | grep -o "idle\|busy\|disabled\|error" | head -1)
    status=${status:-"unknown"}
    
    # Check if default
    default=$(lpstat -d | grep -q "$printer_name" && echo "DEFAULT" || echo "")
    
    # Format output
    status_icon=""
    case "$status" in
        "idle") status_icon="✅" ;;
        "busy") status_icon="⏳" ;;
        "disabled") status_icon="❌" ;;
        "error") status_icon="⚠️" ;;
        *) status_icon="❓" ;;
    esac
    
    printf "%-35s %s %s\n" "$printer_name" "$status_icon" "$default"
    echo "  URI: $device_uri"
    echo ""
done

echo "=============================="
echo ""
echo "ℹ️  Use: bash print-file.sh -p PRINTER_NAME -f document.pdf"
