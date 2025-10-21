#!/bin/zsh

set -e

echo "🚀 Publishing package..."

# Get current version using regex (avoid import issues)
CURRENT_VERSION=$(python3 -c "
import re
with open('src/backend_common/__init__.py', 'r') as f:
    content = f.read()
version_match = re.search(r'__version__\s*=\s*[\"\'](.*?)[\"\']', content)
if version_match:
    print(version_match.group(1))
else:
    exit(1)
")

echo "📋 Current version: $CURRENT_VERSION"

# Check if .pypirc exists
if [ ! -f ".pypirc" ]; then
    echo "⚠️  .pypirc file not found"
    echo "Please create a .pypirc file with your PyPI credentials"
    exit 1
fi

# Build package
echo "🔨 Building package..."
./scripts/build.sh

# Validate package
echo "🔍 Validating package..."
twine check dist/*

# Confirm publication (fixed for zsh compatibility)
echo "📤 About to publish version $CURRENT_VERSION to PyPI"
echo -n "Continue? (y/N): "
read REPLY
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Publication cancelled"
    exit 0
fi

# Publish to PyPI
echo "📦 Publishing to PyPI..."
twine upload dist/* --config-file .pypirc

echo "✅ Package published successfully!"
echo "🌐 Available at: https://pypi.org/project/backend_common_kato/$CURRENT_VERSION"
