#!/bin/zsh

# Remove built artifacts
rm -rf build dist

# Build pipy package
python -m build

# Publish pipy package
python -m twine upload dist/* --config-file .pypirc