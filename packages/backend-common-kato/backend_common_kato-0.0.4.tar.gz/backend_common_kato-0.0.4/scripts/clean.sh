#!/bin/zsh

# Disable error on no glob matches
setopt NULL_GLOB

echo "🧹 Cleaning build artifacts..."

# Remove build artifacts (handle missing directories gracefully)
[ -d "build" ] && rm -rf build
[ -d "dist" ] && rm -rf dist
[ -d "htmlcov" ] && rm -rf htmlcov
[ -d ".pytest_cache" ] && rm -rf .pytest_cache
[ -f ".coverage" ] && rm -f .coverage

# Remove egg-info directories (now safe with NULL_GLOB)
for dir in *.egg-info; do
    [ -d "$dir" ] && rm -rf "$dir"
done

# Remove Python cache files
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

echo "✅ Clean completed!"
