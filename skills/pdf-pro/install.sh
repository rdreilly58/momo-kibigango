#!/bin/bash
# PDF Pro Installation Script

echo "PDF Pro Skill - Installation"
echo "============================"

# Check if WeasyPrint is installed
if ! command -v weasyprint &> /dev/null; then
    echo "Installing WeasyPrint..."
    if command -v brew &> /dev/null; then
        brew install weasyprint
    else
        echo "Error: Homebrew not found. Please install WeasyPrint manually."
        echo "Visit: https://weasyprint.org/stable/install.html"
        exit 1
    fi
else
    echo "✓ WeasyPrint already installed"
fi

# Check Python environment
if [ -f ~/.openclaw/workspace/venv/bin/activate ]; then
    echo "Using existing Python virtual environment..."
    source ~/.openclaw/workspace/venv/bin/activate
else
    echo "Creating Python virtual environment..."
    python3 -m venv ~/.openclaw/workspace/venv
    source ~/.openclaw/workspace/venv/bin/activate
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r "$(dirname "$0")/requirements.txt"

echo ""
echo "✨ Installation complete!"
echo ""
echo "Test the installation:"
echo "  cd $(dirname "$0")"
echo "  ./test.sh"
echo ""
echo "Or try an example:"
echo "  ./scripts/md-to-pdf.sh examples/simple.md output.pdf"