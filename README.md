# Vanna Insight Engine

**AI-Powered Text-to-SQL Backend System**

Version: 1.0.0  
Status: Production-Ready  
Last Updated: November 17, 2025

---

## Overview

Vanna Insight Engine is a FastAPI-based backend system that provides natural language to SQL query generation, SQL error correction, and SQL explanation capabilities powered by AI. The system uses Vanna AI with OpenAI integration to enable business users to interact with databases using plain English.

### Key Features

- **Text-to-SQL Generation**: Convert natural language questions into SQL queries
- **SQL Error Correction**: Automatically fix syntax and logical errors in SQL
- **SQL Explanation**: Get plain-English explanations of complex SQL queries
- **Multi-Database Support**: PostgreSQL, SQLite, MSSQL, Oracle
- **REST API**: OpenAPI 3.1.0 compliant endpoints with comprehensive documentation
- **Admin Dashboard**: Configuration management and system monitoring
- **Authentication & Authorization**: JWT-based security with role-based access control
- **Realtime Agent Chat**: Streaming Vanna Agent chat endpoints (SSE/WebSocket/polling) mounted under `/vanna`
- **Metrics & Monitoring**: Prometheus metrics, health checks, correlation IDs
- **Docker-Based Deployment**: Complete containerized stack with orchestration

---

## Quick Start

### Prerequisites

- Docker >= 20.10
- Docker Compose >= 1.29 (or `docker compose` v2)
- 2GB+ available disk space
- Port 8000 available (or configurable)

### Installation & First Run

```bash
# 1. Navigate to project directory
cd /home/mfadmin/new-vanna/vanna-engine

# 2. Create environment configuration
cp docker/env/.env.example docker/env/.env.dev

# 3. Edit environment variables (REQUIRED)
nano docker/env/.env.dev
# Set at minimum: OPENAI_API_KEY, SECRET_KEY, JWT_SECRET_KEY

# 4. Start the application
./run.sh

# 5. Verify deployment
curl http://localhost:8000/health
```

**API Documentation**: http://localhost:8000/docs

---

## Project Structure

```
vanna-engine/
├── app/                        # Application source code
│   ├── main.py                # FastAPI application entry point
│   ├── config.py              # Configuration management
│   ├── api/                   # API routes and endpoints
│   │   └── v1/routes/         # API v1 endpoints
│   │       ├── core.py        # Health, metrics, root
│   │       ├── auth.py        # Authentication (login, register)
│   │       ├── sql.py         # Protected SQL endpoints
│   │       ├── sql_public.py  # Public SQL endpoints
│   │       ├── feedback.py    # Feedback collection
│   │       └── admin.py       # Admin configuration
│   ├── core/                  # Core business logic
│   ├── services/              # External service integrations
│   ├── db/                    # Database models and migrations
│   ├── middleware/            # Request/response middleware
│   ├── monitoring/            # Metrics and logging
│   └── schemas.py             # Pydantic models
├── docker/
│   ├── Dockerfile             # Application container image
│   └── env/
│       ├── .env.example       # Environment template
│       ├── .env.dev           # Development configuration
│       └── .env.stage         # Staging configuration
├── tests/                     # Test suite
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── e2e/                   # End-to-end tests
├── scripts/                   # Utility scripts
├── migrations/                # Database migrations (Alembic)
├── k8s/                       # Kubernetes deployment manifests
├── docker-compose.yml         # Base service definitions
├── docker-compose.prod.yml    # Production overrides
├── run.sh                     # Main startup script
├── requirements.txt           # Python dependencies
├── AGENTS.md                  # Developer commands reference
└── QUICK_STARTUP.md          # Production deployment guide
```

---

## Core Components

### Services

- **API Server**: FastAPI application with Uvicorn/Gunicorn
- **PostgreSQL**: Primary database (configurable)
- **Redis**: Caching and session storage
- **Chroma**: Vector database for semantic search

### API Endpoints

#### Core Endpoints
- `GET /` - Root endpoint with API information
- `GET /health` - System health check
- `GET /metrics` - Prometheus metrics

#### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login (JWT token)

#### SQL Operations (Public)
- `POST /api/v1/generate-sql` - Generate SQL from natural language
- `POST /api/v1/fix-sql` - Fix SQL errors
- `POST /api/v1/explain-sql` - Explain SQL query

#### SQL Operations (Authenticated)
- `POST /api/v1/sql/execute` - Execute SQL query
- `POST /api/v1/sql/validate` - Validate SQL syntax

#### Admin (Admin Role Required)
- `GET /admin/config` - Get configuration
- `POST /admin/config` - Update configuration
- `GET /admin/feedback-metrics` - Feedback statistics
- `GET /admin/scheduled/list` - Scheduled reports

### Vanna Agent Chat (Realtime)

A dedicated FastAPI sub-application is mounted at **`/vanna`** when `FEATURE_VANNA_ENABLED=true`. It exposes streaming-friendly chat interfaces backed by the upgraded Vanna 2.x Agent stack:

- `GET /vanna/` – Embedded Vanna web UI (loads the published web components bundle)
- `POST /vanna/api/vanna/v2/chat_sse` – Server-Sent Events stream (default for browsers)
- `WEBSOCKET /vanna/api/vanna/v2/chat_websocket` – Bidirectional realtime channel
- `POST /vanna/api/vanna/v2/chat_poll` – Fallback HTTP polling endpoint

All chat endpoints require the same JWT used for `/api/v1/*` routes. Include `Authorization: Bearer <token>` in the request headers (or supply the token via cookies/metadata when integrating from another service).

#### Example (SSE)

```python
import requests
import json

token = "Bearer <your-jwt>"
resp = requests.post(
    "http://localhost:8000/vanna/api/vanna/v2/chat_sse",
    json={
        "message": "Show me the top 10 projects by ARR",
        "conversation_id": "conv_demo",
        "metadata": {},
    },
    headers={"Authorization": token},
    stream=True,
)

for line in resp.iter_lines():
    if line.startswith(b"data: "):
        payload = line[6:]
        if payload != b"[DONE]":
            chunk = json.loads(payload)
            print(chunk)
```

Use the WebSocket endpoint for richer desktop clients; the payload schema matches the SSE chunks. Frontends can also host the official Vanna web component bundle by pointing to `/vanna/` or overriding the CDN via `VANNA_COMPONENT_CDN`.

---

## Environment Configuration

The application uses environment files for configuration. Copy the template and customize:

```bash
cp docker/env/.env.example docker/env/.env.dev
```

### Required Variables (MUST Configure)

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for AI features | `sk-proj-abc123...` |
| `SECRET_KEY` | Application secret (32+ chars) | Generate: `openssl rand -hex 32` |
| `JWT_SECRET_KEY` | JWT signing key (32+ chars) | Generate: `openssl rand -hex 32` |
| `DATABASE_URL` | Database connection string | `postgresql://user:pass@postgres:5432/vanna_db` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `SecurePass123!` |

### Agent Chat & UI Settings (Optional)

| Variable | Description | Example |
|----------|-------------|---------|
| `VANNA_COMPONENT_CDN` | Override the default CDN used by `/vanna/` to load the Vanna web components bundle | `https://assets.example.com/vanna-components.js` |

### Streamlit Frontend Variants

Two Streamlit frontends are now available:

- `ui_streamlit/` – original reference UI (read-only in this workspace).
- `ui_streamlit_agent/` – writable copy with the new Agent Chat page that streams `/vanna/api/vanna/v2/chat_sse`. Run it with `cd ui_streamlit_agent && streamlit run app.py`.

---

## Database Backups

PostgreSQL data can now be snapshotted with a single helper script that reads the configured environment variables and emits timestamped archives under `backups/postgres/`.

### Manual backup

```bash
# Dump the full database defined in .env (includes data)
./scripts/backup_postgres.sh

# Use an alternate env file and capture schema-only metadata
./scripts/backup_postgres.sh --env-file .env.prod --schema-only
```

Each run produces a `*.sql.gz` archive such as `vanna_db_data_20250101T000000Z.sql.gz`. The script validates that `pg_dump` is installed and that all `POSTGRES_*` variables are populated before running.

### Automation example

Add a cron entry (or Kubernetes CronJob) so backups run unattended:

```
0 3 * * * cd /home/mfadmin/new-vanna/vanna-engine && ./scripts/backup_postgres.sh --env-file .env.prod >/var/log/vanna_pg_backup.log 2>&1
```

Rotate the resulting archives to durable storage (object store, NAS, etc.) based on your retention policy.

---

## Observability Uplinks

The backend now exposes knobs for upstream error tracking (Sentry) and distributed tracing (OpenTelemetry + OTLP). Both are optional—leave the variables unset to disable them.

### Sentry

| Variable | Description |
| --- | --- |
| `SENTRY_DSN` | Project DSN from Sentry. Enables automatic error reporting. |
| `SENTRY_TRACES_SAMPLE_RATE` | Fraction (0.0-1.0) of requests to capture as spans (default `0.1`). |
| `SENTRY_ENVIRONMENT` | Overrides environment label (defaults to `APP_ENV`). |

Once `SENTRY_DSN` is provided, the FastAPI stack boots with Sentry SDK and no further changes are required.

### OpenTelemetry / OTLP

Set `ENABLE_TRACING=true` along with the exporter settings below to emit spans to an OTLP-compatible collector (Grafana Tempo, Jaeger, Datadog, etc.).

| Variable | Description |
| --- | --- |
| `OTLP_ENDPOINT` | Collector endpoint, e.g. `http://otel-collector:4317`. |
| `OTLP_HEADERS` | Optional comma-separated headers (`key=value,key2=value2`). |
| `OTLP_INSECURE` | Set to `true` when using plaintext/http collectors. |

When configured, the service registers an OpenTelemetry tracer provider and instruments FastAPI routes automatically.

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8000` | API server port |
| `APP_ENV` | `development` | Environment: development/staging/production |
| `DEBUG` | `true` | Debug mode (set `false` for production) |
| `LOG_LEVEL` | `INFO` | Logging level: DEBUG/INFO/WARN/ERROR |
| `REDIS_URL` | `redis://redis:6379/0` | Redis connection |
| `DB_TYPE` | `sqlite` | Database type: sqlite/postgresql/mssql/oracle |

---

## Running the Application

### Development Mode (Default)

```bash
./run.sh
```

Includes:
- Hot reload enabled
- Verbose logging
- Debug mode active
- Single worker process

### Staging Environment

```bash
./run.sh --env stage
```

Uses `docker/env/.env.stage` configuration.

### Production Mode

```bash
./run.sh --env prod
```

Includes:
- Multi-worker Gunicorn server
- Resource limits and health checks
- Production logging (WARN level)
- No hot reload

See [QUICK_STARTUP.md](QUICK_STARTUP.md) for detailed production deployment guide.

### Additional Options

```bash
./run.sh --build          # Rebuild Docker images
./run.sh --clean          # Remove all containers/volumes first
./run.sh --diagnose       # Run system diagnostics
```

---

## Command Management System 🚀

**New!** Easy access to all project commands with the built-in command launcher:

### Windows
```cmd
tools\command-system\run_listcmd.cmd
```

### Linux/macOS
```bash
./tools/command-system/run_listcmd.sh
```

### Features
- 📋 **90+ predefined commands** organized by category
- 🔍 **Search** commands: `./run_listcmd.sh search docker`
- 📂 **Filter by category**: `./run_listcmd.sh cat test`
- ✅ **Safe execution** with confirmation prompts
- 📝 **Automatic logging** of all actions
- 🎯 **Dry-run mode**: `./run_listcmd.sh dry`
- 🎨 **Color-coded output** for clarity
- ⚡ **Zero installation** - works immediately

See [tools/command-system/README.md](tools/command-system/README.md) for full documentation.

---

## Common Operations

### View Logs

```bash
cd vanna-engine
docker compose logs -f api          # Follow API logs
docker compose logs --tail=50       # Last 50 lines (all services)
```

### Stop Services

```bash
cd vanna-engine
docker compose down                 # Stop services
docker compose down -v              # Stop and remove volumes (data loss)
```

### Run Tests

```bash
cd vanna-engine
pytest                              # Run all tests
pytest tests/unit/                  # Unit tests only
pytest --cov=app                    # With coverage report
```

### Database Operations

```bash
# Access PostgreSQL
docker compose exec postgres psql -U postgres -d vanna_db

# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"
```

### Check Service Health

```bash
curl http://localhost:8000/health | jq .
curl http://localhost:8000/metrics
```

---

## Testing

The project includes comprehensive test coverage:

- **Unit Tests**: `tests/unit/` - Component-level testing
- **Integration Tests**: `tests/integration/` - Service integration testing
- **E2E Tests**: `tests/e2e/` - End-to-end workflow testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_interpreter.py

# Generate coverage report
pytest --cov=app --cov-report=html
```

---

## Monitoring & Observability

### Health Checks

```bash
# Basic health
curl http://localhost:8000/health

# Detailed health (admin only)
curl -H "Authorization: Bearer <token>" http://localhost:8000/admin/health/detailed
```

### Metrics

Prometheus metrics available at `/metrics`:

```bash
curl http://localhost:8000/metrics
```

Includes:
- Request count and latency
- Error rates
- Database connection pool stats
- Cache hit/miss rates

### Logging

Logs written to `logs/app.log` and stdout. Configure level via `LOG_LEVEL` environment variable.

---

## Deployment

### Docker Compose (Recommended for Development/Staging)

```bash
cd vanna-engine
./run.sh --env prod
```

### Kubernetes (Production)

```bash
cd vanna-engine
kubectl apply -k k8s/overlays/production
```

See [QUICK_STARTUP.md](QUICK_STARTUP.md) for production deployment best practices.

---

## Security Considerations

- **Never commit** `.env` files to version control
- **Rotate secrets** regularly (SECRET_KEY, JWT_SECRET_KEY, API keys)
- **Use strong passwords** for database credentials
- **Enable HTTPS** in production (reverse proxy recommended)
- **Restrict CORS origins** via `CORS_ORIGINS` environment variable
- **Regular updates** of dependencies for security patches

---

## Troubleshooting

### Port Already in Use

The `run.sh` script auto-detects and resolves port conflicts. Check logs:

```bash
tail -20 vanna-engine/startup.log
```

### Services Won't Start

```bash
# Check container status
docker compose ps

# View error logs
docker compose logs api

# Common fixes:
docker compose down -v              # Clean restart
./run.sh --clean --env dev          # Full cleanup and restart
```

### Database Connection Failed

Verify `DATABASE_URL` in your environment file matches the PostgreSQL service configuration.

### Authentication Errors

Ensure `SECRET_KEY` and `JWT_SECRET_KEY` are set and consistent across restarts.

---

## Documentation

- **[QUICK_STARTUP.md](QUICK_STARTUP.md)** - Production deployment guide with step-by-step instructions
- **[vanna-engine/AGENTS.md](vanna-engine/AGENTS.md)** - Common commands and developer operations
- **API Documentation** - Interactive docs at `http://localhost:8000/docs`
- **ReDoc** - Alternative API docs at `http://localhost:8000/redoc`

---

## Support & Resources

| Resource | Location |
|----------|----------|
| API Documentation | http://localhost:8000/docs |
| Health Check | http://localhost:8000/health |
| Metrics | http://localhost:8000/metrics |
| Common Commands | [vanna-engine/AGENTS.md](vanna-engine/AGENTS.md) |
| Production Guide | [QUICK_STARTUP.md](QUICK_STARTUP.md) |
| Issue Tracker | Check project repository |

---

## Technology Stack

- **Framework**: FastAPI 0.109.2
- **Server**: Uvicorn/Gunicorn
- **AI/ML**: Vanna AI 0.5.5, OpenAI GPT
- **Database**: PostgreSQL 16, SQLite (configurable: MSSQL, Oracle)
- **Cache**: Redis 7
- **Vector DB**: Chroma
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Testing**: Pytest
- **Containerization**: Docker, Docker Compose
- **Orchestration**: Kubernetes (optional)

---

## License

See project repository for license information.

---

## Changelog

### Version 1.0.0 (November 2025)
- Production-ready release
- OpenAPI 3.1.0 complete implementation
- 13 API endpoints with full documentation
- Correlation ID tracking across all requests
- Admin configuration and monitoring suite
- Docker-based deployment with auto-scaling
- Comprehensive test coverage
- Production hardening and security features

---

**Ready to get started?**

1. Copy `docker/env/.env.example` to `docker/env/.env.dev`
2. Edit the required variables (OPENAI_API_KEY, SECRET_KEY, JWT_SECRET_KEY)
3. Run `./run.sh` from the `vanna-engine/` directory
4. Open http://localhost:8000/docs to explore the API

For production deployment, see [QUICK_STARTUP.md](QUICK_STARTUP.md).
