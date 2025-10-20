# Using uv for Python Development & Production

## Install uv
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Initialize Project
```bash
python3.11 -m venv .venv
uv init --python 3.11
```

## Create & Activate Virtual Environment (should use python client)
```bash
# uv venv .venv --python 3.11
# source .venv/bin/activate  # Unix/Mac
# .venv\Scripts\activate   # Windows
```

## Add Dependencies
```bash
uv add fastapi uvicorn gunicorn

uv add -r requirements.txt
```
To migrate from `requirements.txt`, add all needed packages:
```bash
uv add fastapi asyncpg uvicorn sqlalchemy psycopg2-binary pydantic pydantic-ai pydantic-settings langchain langchain_community tiktoken chromadb langchain-openai langchain-core langchainhub whisper pypdf2 python-docx boto3 structlog python-json-logger gunicorn alembic mako yt-dlp pypdf azure-core azure-storage-blob cffi cryptography isodate pycparser azure-identity msal msal-extensions pyjwt amqp billiard celery click-didyoumean click-plugins click-repl kombu tzdata vine botocore jmespath python-dateutil six urllib3 decorator imageio imageio-ffmpeg moviepy pillow proglog certifi charset-normalizer idna requests chardet reportlab ffmpeg-python future googletrans redis
```
For `langchain-chroma` (if needed):
```bash
uv add langchain-chroma --prerelease=allow
```

## Lock & Sync Dependencies
```bash
uv lock           # Pin versions
uv lock --upgrade # Update to latest compatible
uv sync           # Install from uv.lock
uv sync --active  # Sync with active venv
```

# Production

## Install Dependencies
```bash
uv sync --frozen --no-cache
```
- `--frozen`: Use exact versions from `uv.lock`
- `--no-cache`: Avoid cached packages

Ensure `pyproject.toml` and `uv.lock` are present in production.

## Migrating from pip
1. Remove `requirements.txt`
2. `uv init` to create `pyproject.toml`
3. `uv add ...` to add dependencies
4. `uv lock` to pin versions
5. Commit `pyproject.toml` and `uv.lock`
6. Use `uv sync --frozen` in builds

## Export to requirements.txt (if needed)
```bash
uv pip compile --all-extras --output-file requirements.txt pyproject.toml
```