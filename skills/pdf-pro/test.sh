#!/bin/bash
# Test script for PDF Pro skill

set -uo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_DIR="/tmp/pdf_pro_test_$$"
mkdir -p "$TEST_DIR"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "PDF Pro Skill - Test Suite"
echo "=========================="

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Test function
run_test() {
    local test_name="$1"
    local test_cmd="$2"
    
    echo -n "Testing $test_name... "
    
    if eval "$test_cmd" > "$TEST_DIR/test.log" 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC}"
        echo "  Error output:"
        tail -5 "$TEST_DIR/test.log" | sed 's/^/    /'
        ((TESTS_FAILED++))
    fi
}

# Check dependencies
echo -e "\n1. Checking dependencies..."
run_test "WeasyPrint installed" "command -v weasyprint"
run_test "Pandoc installed" "command -v pandoc"
run_test "Python3 installed" "command -v python3"

# Test Markdown to PDF
echo -e "\n2. Testing Markdown to PDF conversion..."

# Create test markdown
cat > "$TEST_DIR/test.md" << 'EOF'
# Test Document

This is a **test** document with:

- Lists
- **Bold** text
- `Code`

## Code Block

```python
def hello():
    print("Hello, PDF!")
```
EOF

run_test "Basic MD to PDF" "$SKILL_DIR/scripts/md-to-pdf.sh '$TEST_DIR/test.md' '$TEST_DIR/test1.pdf'"
run_test "MD to PDF with title" "$SKILL_DIR/scripts/md-to-pdf.sh '$TEST_DIR/test.md' '$TEST_DIR/test2.pdf' --title 'Test Doc'"
run_test "MD to PDF with style" "$SKILL_DIR/scripts/md-to-pdf.sh '$TEST_DIR/test.md' '$TEST_DIR/test3.pdf' --style '$SKILL_DIR/styles/github.css'"

# Test HTML to PDF
echo -e "\n3. Testing HTML to PDF conversion..."

# Create test HTML
cat > "$TEST_DIR/test.html" << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Test HTML</title>
</head>
<body>
    <h1>Test HTML Document</h1>
    <p>This is a test paragraph with <strong>bold</strong> text.</p>
    <table>
        <tr><th>Header 1</th><th>Header 2</th></tr>
        <tr><td>Cell 1</td><td>Cell 2</td></tr>
    </table>
</body>
</html>
EOF

run_test "Basic HTML to PDF" "$SKILL_DIR/scripts/html-to-pdf.sh '$TEST_DIR/test.html' '$TEST_DIR/test4.pdf'"
run_test "HTML to PDF landscape" "$SKILL_DIR/scripts/html-to-pdf.sh '$TEST_DIR/test.html' '$TEST_DIR/test5.pdf' --landscape"
run_test "HTML to PDF with margins" "$SKILL_DIR/scripts/html-to-pdf.sh '$TEST_DIR/test.html' '$TEST_DIR/test6.pdf' --margins '2cm'"

# Test programmatic PDF generation
echo -e "\n4. Testing programmatic PDF generation..."

# Check if ReportLab is installed
if python3 -c "import reportlab" 2>/dev/null; then
    # Create test JSON
    cat > "$TEST_DIR/test_invoice.json" << 'EOF'
{
    "invoice_number": "TEST-001",
    "date": "2024-03-21",
    "client": {
        "name": "Test Client",
        "address": "123 Test St"
    },
    "items": [
        {"description": "Test Item", "quantity": 1, "rate": 100}
    ]
}
EOF
    
    run_test "Invoice generation" "python3 '$SKILL_DIR/scripts/code-to-pdf.py' '$TEST_DIR/test7.pdf' --template invoice --data '$TEST_DIR/test_invoice.json'"
    run_test "Simple content PDF" "python3 '$SKILL_DIR/scripts/code-to-pdf.py' '$TEST_DIR/test8.pdf' --content 'Test content' --title 'Test'"
else
    echo -e "${YELLOW}⚠ Skipping programmatic tests (ReportLab not installed)${NC}"
fi

# Check generated files
echo -e "\n5. Verifying output files..."
for i in {1..8}; do
    if [ -f "$TEST_DIR/test$i.pdf" ]; then
        size=$(ls -lh "$TEST_DIR/test$i.pdf" | awk '{print $5}')
        echo "  ✓ test$i.pdf exists ($size)"
    fi
done

# Summary
echo -e "\n=========================="
echo "Test Summary:"
echo -e "  ${GREEN}Passed: $TESTS_PASSED${NC}"
if [ $TESTS_FAILED -gt 0 ]; then
    echo -e "  ${RED}Failed: $TESTS_FAILED${NC}"
else
    echo -e "  ${GREEN}All tests passed!${NC}"
fi

# Cleanup
echo -e "\nCleaning up test files..."
rm -rf "$TEST_DIR"

echo -e "\n✨ PDF Pro skill is $([ $TESTS_FAILED -eq 0 ] && echo 'ready to use!' || echo 'partially working.')"

# Exit with appropriate code
exit $TESTS_FAILED