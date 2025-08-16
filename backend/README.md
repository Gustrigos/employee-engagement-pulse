# Employee Pulse Backend (FastAPI)

MVP FastAPI backend following the workspace rules.

## Requirements
- Python 3.12
- Poetry
- PostgreSQL (for Prisma) – optional for mock endpoints

## Setup
```bash
poetry env use 3.12
poetry install
```

## Prisma (optional for now)
```bash
# Ensure DATABASE_URL is set in .env
poetry run prisma generate
# First migration example
# poetry run prisma migrate dev --name init
```

## Run
```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Quick Anthropic Debug (bypass FastAPI)

For rapid prototyping or when server logs are not visible, use the standalone debug harness:

```bash
cd backend
# Ensure ANTHROPIC_API_KEY is set in backend/.env or your shell
poetry run python -m scripts.debug_anthropic
```

This prints whether the key is present and dumps the structured result or error, independent of uvicorn.

## Test
```bash
poetry run pytest -q
```

## Lint/Format
```bash
poetry run ruff check .
poetry run ruff format .
```
