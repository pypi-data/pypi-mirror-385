#!/bin/zsh

set -e

echo "🧪 Running tests..."

# Run tests with pytest
if command -v pytest >/dev/null 2>&1; then
    pytest tests/ -v
else
    python -m pytest tests/ -v
fi

echo "✅ Tests completed!"
