# Using uv for Python Development & Production

## Quick Start

### 1. Install uv
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Initialize New Project
```bash
# Create new project from scratch
uv init my-project --python 3.12
cd my-project

# Or initialize in existing directory
uv init --python 3.12
```

### 3. Create Package Template
```bash
# Initialize as a package with src layout
uv init --package --python 3.12

# This creates:
# - pyproject.toml with package configuration
# - src/my_project/ directory structure
# - Basic __init__.py files
```

## Package Management

### Adding Dependencies

```bash
# Add production dependency
uv add fastapi uvicorn sqlalchemy

# Add development dependency (creates [dependency-groups])
uv add --dev pytest black mypy ruff

# Add specific dependency groups
uv add --group testing pytest-xdist pytest-benchmark
uv add --group docs mkdocs mkdocs-material

# Add from specific source
uv add "requests>=2.28.0"
uv add "django>=4.0,<5.0"
```

### Installing Dependencies

```bash
# Install all dependencies (production only)
uv sync

# Install with dev dependencies
uv sync --group dev

# Install specific groups
uv sync --group docs --group testing

# Install all groups
uv sync --all-groups
```

### Managing Dependencies

```bash
# Update all dependencies
uv lock --upgrade

# Remove dependency
uv remove requests

# Remove dev dependency
uv remove --dev pytest-cov

# Show dependency tree
uv tree

# Show outdated packages
uv pip list --outdated
```

## Project Configuration

### pyproject.toml Setup (Modern PEP 735 Format)

```toml
[project]
name = "my-project"
version = "0.1.0"
description = "My awesome project"
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "sqlalchemy>=2.0.0",
    "pydantic>=2.0.0",
]

# ✅ MODERN: Use dependency-groups (PEP 735)
[dependency-groups]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "black>=23.9.0",
    "ruff>=0.1.0",
    "mypy>=1.6.0",
]
docs = [
    "mkdocs>=1.5.0",
    "mkdocs-material>=9.4.0",
]
testing = [
    "pytest-xdist>=3.3.0",
    "pytest-benchmark>=4.0.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

## Development Workflow

### Daily Development

```bash
# 1. Install everything for development
uv sync --group dev

# 2. Run your application
uv run python -m my_project
uv run fastapi dev src/my_project/main.py

# 3. Run tests
uv run pytest
uv run pytest --cov=src

# 4. Format and lint code
uv run black src/ tests/
uv run ruff check src/ tests/
uv run ruff format src/ tests/

# 5. Type checking
uv run mypy src/

# 6. Run specific scripts
uv run python scripts/setup_db.py
```

### Working with Virtual Environment

```bash
# Run commands directly with uv run (recommended)
uv run python my_script.py
uv run pytest
uv run black .

# Or activate virtual environment if needed
source .venv/bin/activate
```

## Production Deployment

### Docker Example

```dockerfile
FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Copy project files
WORKDIR /app
COPY pyproject.toml uv.lock ./
COPY src/ ./src/

# Install production dependencies only
RUN uv sync --frozen --no-cache

# Run application
CMD ["uv", "run", "python", "-m", "my_project"]
```

### Production Install

```bash
# Install only production dependencies (no dev tools)
uv sync --frozen --no-cache

# Verify production environment
uv run python -c "import sys; print(sys.path)"
```

## Advanced Usage

### Multiple Python Versions

```bash
# Install specific Python version
uv python install 3.11 3.12

# Use specific version for project
uv init --python 3.11

# Switch Python version
uv python pin 3.12
```

### Export Requirements

```bash
# Export production requirements
uv export --no-hashes > requirements.txt

# Export dev requirements
uv export --group dev --no-hashes > requirements-dev.txt

# Export with hashes for security
uv export --format requirements-txt > requirements-locked.txt
```

### Scripts and Tools

```bash
# Add script to pyproject.toml
[project.scripts]
my-cli = "my_project.cli:main"

# Then run with:
uv run my-cli

# Or install globally
uv tool install my-project
```

## Real Project Example

### Complete Setup Flow

```bash
# 1. Create new project
uv init backend-service --python 3.12
cd backend-service

# 2. Add core dependencies
uv add fastapi uvicorn sqlalchemy alembic pydantic-settings

# 3. Add development tools (creates [dependency-groups])
uv add --dev pytest pytest-asyncio httpx black ruff mypy

# 4. Create basic structure
mkdir -p src/backend_service tests

# 5. Install in development mode
uv sync --group dev

# 6. Lock dependencies
uv lock

# 7. Run development server
uv run uvicorn src.backend_service.main:app --reload
```

### Common Commands Reference

```bash
# Project setup
uv init                          # Initialize new project
uv add <package>                 # Add production dependency
uv add --dev <package>           # Add development dependency
uv sync --group dev              # Install all dependencies

# Development
uv run pytest                    # Run tests
uv run black .                   # Format code
uv run mypy src/                 # Type check

# Dependency management
uv lock                          # Update lock file
uv lock --upgrade               # Upgrade all dependencies
uv remove <package>             # Remove dependency

# Production
uv sync --frozen --no-cache     # Production install
uv export > requirements.txt    # Export requirements
```

## Best Practices

1. **Always commit both `pyproject.toml` and `uv.lock`**
2. **Use `--frozen` in production** for reproducible builds
3. **Prefer `uv sync --group dev`** for development dependencies
4. **Use `uv run`** instead of activating virtual environments
5. **Pin Python version** with `uv python pin`
6. **Use `[dependency-groups]`** (PEP 735) for modern uv projects
7. **Lock after any dependency changes** with `uv lock`
