#!/bin/zsh

set -e

echo "Using virtual environment at: $VIRTUAL_ENV"
source ".venv/bin/activate"

echo "🧪 Running tests..."

# Run tests with pytest
if command -v pytest >/dev/null 2>&1; then
    pytest tests/ -v
else
    python3 -m pytest tests/ -v
fi

echo "✅ Tests completed!"
