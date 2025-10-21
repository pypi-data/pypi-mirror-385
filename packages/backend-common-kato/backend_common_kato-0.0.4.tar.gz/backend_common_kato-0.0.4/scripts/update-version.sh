#!/bin/zsh

set -e

# Enhanced version update script for backend-common package
# Usage:
#   ./update-version.sh <new_version>           # Set specific version
#   ./update-version.sh --auto [major|minor|patch]  # Auto-increment from PyPI
#   ./update-version.sh --check                 # Just check PyPI version
# Examples:
#   ./update-version.sh 0.0.4
#   ./update-version.sh --auto patch
#   ./update-version.sh --auto minor

PACKAGE_NAME="backend-common-kato"

# Function to get the latest version from PyPI
get_pypi_version() {
    echo "🔍 Checking latest version on PyPI for package: $PACKAGE_NAME" >&2
    local pypi_response=$(curl -s "https://pypi.org/pypi/$PACKAGE_NAME/json" 2>/dev/null)

    if [ $? -ne 0 ] || [ -z "$pypi_response" ]; then
        echo "⚠️  Warning: Could not fetch version from PyPI. Package might not be published yet." >&2
        echo "0.0.0"
        return
    fi

    local latest_version=$(echo "$pypi_response" | python3 -c "
import json
import sys
try:
    data = json.load(sys.stdin)
    print(data['info']['version'])
except:
    print('0.0.0')
")

    echo "📦 Latest version on PyPI: $latest_version" >&2
    echo "$latest_version"
}

# Function to increment version
increment_version() {
    local version=$1
    local type=$2

    python3 -c "
version = '$version'
parts = list(map(int, version.split('.')))

if '$type' == 'major':
    parts[0] += 1
    parts[1] = 0
    parts[2] = 0
elif '$type' == 'minor':
    parts[1] += 1
    parts[2] = 0
elif '$type' == 'patch':
    parts[2] += 1

print('.'.join(map(str, parts)))
"
}

# Function to compare versions
compare_versions() {
    local v1=$1
    local v2=$2

    python3 -c "
from packaging import version
v1 = version.parse('$v1')
v2 = version.parse('$v2')

if v1 > v2:
    print('greater')
elif v1 < v2:
    print('less')
else:
    print('equal')
"
}

# Function to get current local version
get_local_version() {
    python3 -c "
import re
with open('src/backend_common/__init__.py', 'r') as f:
    content = f.read()
version_match = re.search(r'__version__\s*=\s*[\"\'](.*?)[\"\']', content)
print(version_match.group(1) if version_match else 'unknown')
"
}

# Function to validate version format
validate_version() {
    local version=$1
    if ! echo "$version" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.-]+)?$'; then
        echo "❌ Error: Invalid version format. Please use semantic versioning (e.g., 1.2.3)"
        exit 1
    fi
}

# Function to update version in files
update_version_files() {
    local new_version=$1

    echo "📝 Updating version files..."

    # Update version in pyproject.toml
    sed -i '' "s/^version = \".*\"/version = \"$new_version\"/" pyproject.toml

    # Update version in __init__.py
    sed -i '' "s/__version__ = \".*\"/__version__ = \"$new_version\"/" src/backend_common/__init__.py

    # Verify changes
    local updated_version_pyproject=$(grep '^version =' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
    local updated_version_init=$(get_local_version)

    if [ "$updated_version_pyproject" = "$new_version" ] && [ "$updated_version_init" = "$new_version" ]; then
        echo "✅ Version successfully updated to $new_version"
        echo "   - pyproject.toml: $updated_version_pyproject"
        echo "   - __init__.py: $updated_version_init"
        return 0
    else
        echo "❌ Error: Version update failed"
        echo "   - pyproject.toml: $updated_version_pyproject"
        echo "   - __init__.py: $updated_version_init"
        return 1
    fi
}

# Main script logic
main() {
    # Check if packaging module is available
    if ! python3 -c "import packaging" 2>/dev/null; then
        echo "📦 Installing packaging module for version comparison..."
        pip3 install packaging
    fi

    local current_local_version=$(get_local_version)
    echo "📍 Current local version: $current_local_version"

    if [ "$1" = "--check" ]; then
        local pypi_version=$(get_pypi_version)
        echo ""
        echo "📊 Version Summary:"
        echo "   Local:  $current_local_version"
        echo "   PyPI:   $pypi_version"

        local comparison=$(compare_versions "$current_local_version" "$pypi_version")
        if [ "$comparison" = "greater" ]; then
            echo "   Status: Local version is ahead of PyPI"
        elif [ "$comparison" = "less" ]; then
            echo "   Status: PyPI version is ahead of local"
        else
            echo "   Status: Versions are in sync"
        fi
        exit 0
    fi

    local new_version=""

    if [ "$1" = "--auto" ]; then
        local increment_type=${2:-patch}

        if [[ ! "$increment_type" =~ ^(major|minor|patch)$ ]]; then
            echo "❌ Error: Invalid increment type. Use: major, minor, or patch"
            exit 1
        fi

        local pypi_version=$(get_pypi_version)
        local base_version="$pypi_version"

        # Use the higher version between local and PyPI as base
        local comparison=$(compare_versions "$current_local_version" "$pypi_version")
        if [ "$comparison" = "greater" ]; then
            base_version="$current_local_version"
            echo "🔄 Using local version as base (ahead of PyPI)"
        else
            echo "🔄 Using PyPI version as base"
        fi

        new_version=$(increment_version "$base_version" "$increment_type")
        echo "🎯 Auto-incremented version ($increment_type): $base_version → $new_version"

    elif [ $# -eq 0 ]; then
        echo "❌ Error: No version specified"
        echo ""
        echo "Usage:"
        echo "  $0 <new_version>                    # Set specific version"
        echo "  $0 --auto [major|minor|patch]       # Auto-increment from PyPI (default: patch)"
        echo "  $0 --check                          # Check current versions"
        echo ""
        echo "Examples:"
        echo "  $0 0.0.4"
        echo "  $0 --auto patch"
        echo "  $0 --auto minor"
        echo "  $0 --check"
        exit 1
    else
        new_version=$1
        validate_version "$new_version"

        # Check if this version already exists on PyPI
        local pypi_version=$(get_pypi_version)
        local comparison=$(compare_versions "$new_version" "$pypi_version")

        if [ "$comparison" = "equal" ]; then
            echo "⚠️  Warning: Version $new_version already exists on PyPI"
            echo "   Consider using --auto to increment automatically"
        elif [ "$comparison" = "less" ]; then
            echo "⚠️  Warning: Version $new_version is lower than PyPI version ($pypi_version)"
        fi
    fi

    # Final confirmation for manual versions
    if [ "$1" != "--auto" ]; then
        echo ""
        echo "🔄 Version change summary:"
        echo "   From: $current_local_version"
        echo "   To:   $new_version"
        echo ""
        read -p "Continue with version update? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "❌ Version update cancelled"
            exit 1
        fi
    fi

    # Update version files
    if update_version_files "$new_version"; then
        echo ""
        echo "🎉 Version update completed!"
        echo ""
        echo "📋 Next steps:"
        echo "   1. Review changes:    git diff"
        echo "   2. Commit changes:    git add . && git commit -m 'bump version to $new_version'"
        echo "   3. Create tag:        git tag v$new_version"
        echo "   4. Push changes:      git push && git push --tags"
        echo "   5. Build & publish:   ./scripts/publish.sh"
    else
        exit 1
    fi
}

main "$@"
