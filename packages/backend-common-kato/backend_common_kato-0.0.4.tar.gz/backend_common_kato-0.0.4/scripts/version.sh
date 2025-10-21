#!/bin/zsh

set -e

# Get current version from __init__.py without importing the full module
python3 -c "
import re
import sys

# Read the __init__.py file
with open('src/backend_common/__init__.py', 'r') as f:
    content = f.read()

# Extract version using regex
version_match = re.search(r'__version__\s*=\s*[\"\'](.*?)[\"\']', content)
if version_match:
    print(version_match.group(1))
else:
    print('Version not found')
    sys.exit(1)
"
