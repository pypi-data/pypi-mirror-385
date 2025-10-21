#!/bin/zsh

set -e

echo "🔨 Building package..."

# Clean first
./scripts/clean.sh

# Build package
python -m build

echo "✅ Build completed!"
echo "📦 Built files:"
ls -la dist/
