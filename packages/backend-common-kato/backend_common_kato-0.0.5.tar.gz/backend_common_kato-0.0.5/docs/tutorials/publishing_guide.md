# Publishing Backend Common to PyPI - Complete Guide

## Prerequisites

1. **Install build tools:**
```bash
pip install build twine
```

2. **Create PyPI account:**
   - Go to https://pypi.org/account/register/
   - Verify your email
   - Enable 2FA (recommended)

3. **Create API token:**
   - Go to https://pypi.org/manage/account/
   - Create API token for your account
   - Save the token securely

## Step 1: Prepare the Package

```bash
cd /Users/kato/Desktop/5.\ TechEdu/repositories/backend-common

# Install development dependencies
pip install -e ".[dev]"

# Run tests to ensure everything works
pytest tests/

# Format code
black src/
isort src/

# Type check
mypy src/backend_common/
```

## Step 2: Build the Package

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build the package
python -m build

# This creates:
# - dist/backend_common-0.1.0-py3-none-any.whl
# - dist/backend_common-0.1.0.tar.gz
```

## Step 3: Test the Package Locally

```bash
# Install the built package locally
pip install dist/backend_common-0.0.1-py3-none-any.whl

# Test import
python -c "from backend_common import BaseError; print('Import successful!')"
```

## Step 4: Upload to PyPI

### Option A: Using Twine (Recommended)

```bash
# Upload to TestPyPI first (optional but recommended)
python -m twine upload --repository testpypi dist/*

# Upload to real PyPI
python -m twine upload dist/*

# You'll be prompted for username (__token__) and password (your API token)
```

### Option B: Using GitHub Actions (Automated)

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

## Step 5: Verify Publication

```bash
# Install from PyPI
pip install backend-common

# Test in a new environment
python -c "from backend_common.exceptions import NotFoundError; print('Success!')"
```

## Version Management

To release new versions:

1. **Update version in `src/backend_common/__init__.py`:**
```python
__version__ = "0.1.1"
```

2. **Update version in `pyproject.toml`:**
```toml
version = "0.1.1"
```

3. **Build and publish:**
```bash
python -m build
python -m twine upload dist/*
```

## GitHub Repository Setup

```bash
# Initialize git repository
git init
git add .
git commit -m "Initial commit: Backend Common package"

# Create GitHub repository and push
git remote add origin https://github.com/yourusername/backend-common.git
git branch -M main
git push -u origin main
```

## Environment Variables for PyPI Token

```bash
# Set environment variables (optional)
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=your-pypi-token

# Then you can upload without prompts
twine upload dist/*
```

## Package Distribution

Once published, users can install with:

```bash
# Latest version
pip install backend-common

# Specific version
pip install backend-common==0.1.0

# With uv
uv add backend-common

# From git (for development versions)
pip install git+https://github.com/yourusername/backend-common.git
```

## Maintenance

- **Security updates:** Regularly update dependencies
- **Version management:** Use semantic versioning (MAJOR.MINOR.PATCH)
- **Documentation:** Keep README.md and examples updated
- **Testing:** Add more tests as features are added
- **CI/CD:** Set up automated testing and publishing
