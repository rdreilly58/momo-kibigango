#!/bin/bash
# test-printer.sh — Test printer connectivity and print a test page

set -uo pipefail

PRINTER=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -p|--printer)
            PRINTER="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: bash test-printer.sh [-p PRINTER_NAME]"
            echo ""
            echo "Tests printer connectivity and prints a test page"
            echo ""
            echo "OPTIONS:"
            echo "  -p, --printer PRINTER   Printer name (default: system default)"
            echo "  -h, --help              Show this help"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Use default if not specified
if [[ -z "$PRINTER" ]]; then
    PRINTER=$(lpstat -d 2>/dev/null | awk '{print $NF}')
    if [[ -z "$PRINTER" ]]; then
        echo "❌ No printer specified and no default printer set"
        exit 1
    fi
fi

echo "🧪 Testing Printer: $PRINTER"
echo "================================"
echo ""

# Test 1: Printer registration
echo "Test 1: Printer Registration"
if lpstat -v | grep -q "$PRINTER"; then
    echo "✅ Printer registered in CUPS"
else
    echo "❌ Printer NOT found in CUPS"
    exit 1
fi

# Test 2: Printer status
echo ""
echo "Test 2: Printer Status"
status=$(lpstat -p "$PRINTER" 2>/dev/null | grep -o "idle\|busy\|disabled\|error" | head -1)
if [[ "$status" == "idle" ]]; then
    echo "✅ Printer is idle and ready"
elif [[ "$status" == "busy" ]]; then
    echo "⚠️  Printer is busy (will accept print jobs)"
else
    echo "❌ Printer status: $status"
fi

# Test 3: Network connectivity
echo ""
echo "Test 3: Network Connectivity"
# Extract hostname from device URI
device_uri=$(lpstat -v | grep "$PRINTER" | awk -F': ' '{print $2}')
if [[ -n "$device_uri" ]]; then
    echo "ℹ️  Device URI: $device_uri"
    echo "✅ Printer device configured"
else
    echo "❌ Could not get device URI"
fi

# Test 4: Print test page
echo ""
echo "Test 4: Print Test Page"
test_file=$(mktemp /tmp/printer-test-XXXXXX.txt)

# Create test page content
cat > "$test_file" << 'TESTPAGE'
================================================================================
                         PRINTER TEST PAGE
================================================================================

Date/Time: $(date)
Printer: 
Host: $(hostname)

================================================================================
                         TEXT RENDERING TEST
================================================================================

BOLD: This text should appear in the document
LINES: |----|----|----|----|----|----|----|----|----|----|----|----|----|----
NUMBERS: 0123456789 0123456789 0123456789 0123456789 0123456789 0123456789

PARAGRAPH:
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor
incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis
nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

================================================================================
                         COLOR TEST (B&W equivalent)
================================================================================

Black: ████████████████████████████████████████████████████████████████████████
Gray:  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

================================================================================
                         PAGE LAYOUT TEST
================================================================================

Margin test:
  This line should have standard left margin
    This line should be indented
      This line should be double indented

Tab test:
	Tab 1
		Tab 2
			Tab 3

================================================================================
                         CONCLUSION
================================================================================

If you can read this document clearly, your printer is working correctly!

For issues:
  1. Check printer is online
  2. Verify CUPS is running (launchctl list | grep cups)
  3. Run: lpstat -p -d

================================================================================
TESTPAGE

# Replace variables
sed -i "" "s|\$(date)|$(date)|g" "$test_file"
sed -i "" "s|\$(hostname)|$(hostname)|g" "$test_file"

# Print test page
if lp -d "$PRINTER" "$test_file" 2>/dev/null; then
    echo "✅ Print job submitted successfully"
    job_id=$(lpq -P "$PRINTER" | tail -1 | awk '{print $1}')
    if [[ -n "$job_id" && "$job_id" != "Rank" ]]; then
        echo "   Job ID: $job_id"
        echo "   Status: Check printer in ~30 seconds"
    fi
else
    echo "❌ Failed to submit print job"
    rm -f "$test_file"
    exit 1
fi

# Cleanup
rm -f "$test_file"

echo ""
echo "================================"
echo "🧪 Test completed"
echo ""
echo "Check if test page printed. If successful, printer is working!"
