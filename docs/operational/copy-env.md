# Environment File Management

This project now uses a **central root `.env`** as the single source of truth for configuration, with **optional environment-specific overrides** under `docker/env/`.

## Files

- Root master config (all shared settings, secrets, flags):
  - `.env` (project root) — single source of truth
  - `.env.production.example` (project root) — non-functional production template
- Docker environment overrides (only differences from root `.env`):
  - `docker/env/.env.dev`
  - `docker/env/.env.prod`
  - `docker/env/.env.example` (template for new environments)

## Root `.env`

- Contains the complete configuration for:
  - System DB (PostgreSQL) via `POSTGRES_*` / `POSTGRES_URL`
  - Target DB / Golden Copy (`DB_TYPE`, `TARGET_DB_PATH`, `TARGET_DB_SOURCE`)
  - Redis, Chroma, Celery, LLM providers, security, monitoring, etc.
- Used by:
  - Local `uvicorn` / `pytest` runs
  - Docker Compose (via `run.sh` and `docker-compose.yml`)

### Creating/Updating the root `.env`

If you want to start from the production template:

```bash
cd vanna-engine
cp .env.production.example .env
```

Then edit `.env` to match your environment (DB passwords, API keys, etc.).

## Docker overrides (docker/env)

- `./run.sh` always uses root `.env` for Docker Compose.
- When you pass an environment, e.g.:

```bash
./run.sh --env dev
./run.sh --env prod
```

it sets `ENV_FILE` to:

- `docker/env/.env.dev` for `--env dev`
- `docker/env/.env.prod` for `--env prod`

`app/config.py` then loads:

1. Root `.env`
2. Override file from `ENV_FILE` (if present) — values here take precedence.

### Example overrides

- `docker/env/.env.dev`
  - `APP_ENV=development`
  - `DEBUG=true`
  - `WORKERS=1`
  - `DB_TYPE=sqlite`
- `docker/env/.env.prod`
  - `APP_ENV=production`
  - `DEBUG=false`
  - `WORKERS=8`
  - `DB_TYPE=postgresql`

## When adding new variables

1. Add the variable to the root `.env` with a sensible default.
2. If a value differs by environment, add only the differing value to:
   - `docker/env/.env.dev` and/or `docker/env/.env.prod`
3. Ensure `app/config.py` reads the variable (via `os.getenv` or Pydantic field).
