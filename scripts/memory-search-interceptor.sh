#!/bin/bash
# Memory Search Tool Interceptor
# This script intercepts memory_search calls and redirects to mem-search
# Source this in your session to enable the override

# Override the memory_search function if it exists
memory_search() {
    echo "⚠️  INTERCEPTED: memory_search() is broken (OpenAI quota exceeded)"
    echo "Using mem-search (local embeddings) instead..."
    echo ""
    
    if [ -z "$1" ]; then
        echo "Usage: mem-search \"query\""
        return 1
    fi
    
    cd ~/.openclaw/workspace || return 1
    source venv/bin/activate 2>/dev/null || {
        echo "Error: Virtual environment not found"
        return 1
    }
    
    python3 scripts/memory_search_local.py "$@"
}

# Export the function so it's available
export -f memory_search

echo "✅ Memory search interceptor enabled"
echo "   - Built-in memory_search() will redirect to mem-search"
echo "   - Use: mem-search \"your query\""
