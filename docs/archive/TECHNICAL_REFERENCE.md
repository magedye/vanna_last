# Technical Reference & Architecture Standard – Vanna Insight Engine

## 1. Scope & Purpose

This document is the authoritative technical standard for the Vanna Insight Engine stack:

- FastAPI backend under `vanna-engine/app/`
- Streamlit frontend under `ui_streamlit/`

It codifies the final architecture after refactoring, with a focus on:

- Centralized configuration and secrets
- Unified database and migration behavior
- Centralized cryptography and authentication
- Frontend–backend integration (CORS, networking)
- Testing, seeding, backups, and observability

All new work should align with these standards.

---

## 2. Environment & Configuration

### 2.1 Configuration Hierarchy

Configuration is managed via `pydantic-settings` in `app/config.py` with this precedence:

1. **OS environment variables** – highest priority (production, CI, Kubernetes).
2. **ENV_FILE** – optional override env file (e.g. `docker/env/.env.dev`).
3. **Root `.env`** – local development defaults at repo root.

`ENV_FILE` is resolved relative to the project root; the root `.env` is always loaded first.

### 2.2 Missing Secrets Policy (Secure Fallbacks)

For `SECRET_KEY` and `JWT_SECRET_KEY`:

- If these variables are missing or empty, `app/config.py` uses a **Secure Runtime Fallback** via `secrets.token_hex(32)` and logs a **WARNING**.
- This behavior maximizes resilience for local and test environments while clearly signaling misconfiguration.
- **Standard:** Production deployments MUST provide explicit, non-default values for `SECRET_KEY` and `JWT_SECRET_KEY` via env files or environment variables.

### 2.3 Vector Database Configuration

Vector DB configuration is centralized in `Settings` (`app/config.py`):

- `VECTOR_DB_TYPE` – `"chroma"` (default) or `"qdrant"` (future).
- `CHROMA_HOST`, `CHROMA_PORT` – host/port for ChromaDB service (Docker service name `chromadb` by default).
- `QDRANT_HOST`, `QDRANT_PORT` – reserved for future Qdrant support.

`EmbeddingManager` (`app/core/semantic/embeddings.py`) must:

- Initialize the Chroma HTTP client using `CHROMA_HOST` and `CHROMA_PORT`.
- Fall back to an ephemeral in-memory client if HTTP health check fails.

---

## 3. Database & Data Persistence

### 3.1 System DB (PostgreSQL) & Target DB

The `Settings` class is the single source of truth for DB configuration:

- System DB (PostgreSQL) URL:
  - `POSTGRES_*` variables define internal service host, user, password, and DB name.
  - `Settings._build_postgres_url()` constructs `POSTGRES_URL`.
  - `DATABASE_URL` is kept in sync with `POSTGRES_URL` for backward compatibility unless explicitly set.
- Target DB (analytical / Golden Copy) URL:
  - `TARGET_DATABASE_URL` wins when set.
  - Otherwise derived from `DB_TYPE` plus DB-specific variables.
  - Supported `DB_TYPE` values: `sqlite`, `postgresql`, `mssql`, `oracle` (case-insensitive).

### 3.2 Alembic Migrations (Configuration Unification)

Alembic must use the same database URL as the application:

- `migrations/env.py` imports `get_settings()` from `app.config`.
- `_get_database_url()` is defined as:
  - `settings = get_settings()`
  - `return settings.DATABASE_URL`
- `run_migrations_offline()` and `run_migrations_online()` both call `_get_database_url()` and pass it to Alembic.

**Standard:** All future migration logic must rely on `Settings` for DB URLs; no direct `os.getenv(...)` URL reconstruction in Alembic.

### 3.3 Idempotent Seeding (Canonical Script)

The canonical database initializer is:

- `scripts/init_project.py` – **Master Database Initializer**

Key behaviors:

- Validates environment (including `DATABASE_URL` and `SECRET_KEY`) before running.
- Runs Alembic migrations where present.
- Creates tables via SQLAlchemy.
- Loads ontology and seeds sample data.
- **Creates/updates the default admin user idempotently** in `create_admin_user()`:
  - Checks for an existing user by `username`.
  - If found, ensures `role="admin"` and returns success.
  - If not found, creates a new admin user using `AuthManager` for password hashing.

**Standard:** Any seeding or initialization must be idempotent and should extend `init_project.py` rather than introduce new one-off scripts.

---

## 4. Authentication & Security

### 4.1 Centralized Cryptography Standard

All password hashing and verification uses:

- `app.core.security.auth.AuthManager`
  - Backed by the `bcrypt` library.
  - Enforces a maximum bcrypt input length (72 bytes), truncating with a warning where appropriate.

Implementation:

- `scripts/init_project.py` uses `AuthManager` for admin password hashing.
- `app/api/v1/routes/auth.py` imports `AuthManager` and a shared `settings` instance:
  - `auth_manager = AuthManager(settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM, settings.JWT_EXPIRATION_HOURS)`
  - Signup uses `auth_manager.hash_password(...)`.
  - Login uses `auth_manager.verify_password(...)`.

**Standard:** No route or script may implement its own bcrypt helpers; all must call `AuthManager`.

### 4.2 JWT & Role-Based Access Control (RBAC)

JWT configuration is centralized in `Settings`:

- `JWT_SECRET_KEY`
- `JWT_ALGORITHM` (default `"HS256"`)
- `JWT_EXPIRATION_HOURS`

Token creation and verification:

- `app/api/dependencies.py::create_access_token(user_id)` – builds a JWT with `sub=user_id` and `exp` according to `JWT_EXPIRATION_HOURS`.
- `get_current_user` decodes the token using `settings.JWT_SECRET_KEY` and `settings.JWT_ALGORITHM`, then loads the `User` from the DB.
- `get_current_admin_user` enforces `role == "admin"`.
- `requires_role(...)` provides more granular RBAC.

**Standard:**

- All protected API routes must use `get_current_user` or `get_current_admin_user` (or role-based wrappers constructed from `requires_role`).
- Admin-only routes must depend on `get_current_admin_user`.

### 4.3 Admin Dashboard Authentication

Admin dashboard authentication uses the same JWT token:

- `app.admin.auth.JWTAdminAuthBackend` reads tokens via `Authorization: Bearer <token>`.
- It uses `create_access_token` semantics and the `User` model for RBAC.

Tests in `tests/unit/test_admin_auth.py` verify:

- Admin users with valid tokens are allowed.
- Non-admin users are rejected with `403`.
- Missing tokens yield `401`.

---

## 5. Middleware, Rate Limiting & Observability

### 5.1 Middleware Ordering & Responsibilities

Key middleware in `app/main.py`:

- `MetricsMiddleware` – Prometheus-friendly metrics and request tracking.
- `CorrelationIDMiddleware` – injects/propagates `X-Correlation-ID`.
- `AuthContextMiddleware` – extracts user context (e.g., `user_id`) from JWT into `request.state`.
- `SlowAPIMiddleware` – rate limiting via `slowapi`.
- `CORSMiddleware` – CORS handling for browser clients.
- `GZipMiddleware` – response compression.

All middleware must handle exceptions gracefully and not mask HTTP error codes.

### 5.2 Rate Limiting User Context

Rate limiting is configured in `app/core/rate_limiting.py`:

- `Limiter` is instantiated with:
  - `key_func=get_rate_limit_key`
  - `headers_enabled=False` (custom exception handler manages headers)
  - `storage_uri=settings.RATE_LIMIT_STORAGE_URI` (Redis or memory)
- `get_rate_limit_key(request)`:
  - If `request.state.user_id` is set, returns `f"user:{request.state.user_id}"`.
  - Otherwise falls back to `slowapi.util.get_remote_address(request)` (client IP).
- `RateLimitExceptionHandler` ensures 429 responses with optional `Retry-After` and a structured `ErrorResponse`.

**Standard:** Authenticated endpoints MUST be rate limited by user ID via `request.state.user_id`; public endpoints may be limited by IP.

### 5.3 Observability (Sentry + OTLP)

`app/monitoring/observability.py` encapsulates uplinks:

- `setup_observability(app)`:
  - Initializes Sentry when `SENTRY_DSN` is provided:
    - Uses `sentry_sdk` with `FastApiIntegration`.
    - Respects `SENTRY_ENVIRONMENT` and `SENTRY_TRACES_SAMPLE_RATE`.
  - Initializes OTLP tracing when `ENABLE_TRACING` is `true` and `OTLP_ENDPOINT` is set:
    - Uses OpenTelemetry SDK and FastAPI instrumentation.

**Standard:** Sentry and OTLP are optional but must be enabled strictly via configuration, not hardcoded.

---

## 6. Frontend Integration (Streamlit)

### 6.1 CORS & Browser Integration

Backend CORS configuration in `app/main.py`:

- Uses `fastapi.middleware.cors.CORSMiddleware` with:
  - `allow_origins=settings.CORS_ORIGINS`
  - `allow_credentials=True`
  - `allow_methods=["*"]`
  - `allow_headers=["*"]`

Defaults in `Settings.CORS_ORIGINS` (`app/config.py`) include:

- `http://localhost`
- `http://localhost:3000`
- `http://localhost:8000`
- `http://localhost:8501` (Streamlit frontend)

Integration tests in `tests/integration/test_openapi_surface.py` (`TestCORSPreflight`) validate:

- Preflight from `http://localhost:8501` includes proper CORS headers.
- Disallowed origins do not receive `access-control-allow-origin` for their origin.

### 6.2 Docker Networking & Streamlit Configuration

Streamlit configuration (`ui_streamlit/.env.example`):

- `BACKEND_URL=http://api:8000` – uses the Docker service name `api` from Compose.
- `DEFAULT_USERNAME` / `DEFAULT_PASSWORD` – default demo credentials (`admin` / `admin`).

**Standard:**

- Browser → backend should use the public hostname or `localhost` (CORS origins).
- Streamlit container → backend should use the internal Docker DNS name `http://api:8000`.

---

## 7. Testing & Quality Gates

### 7.1 Unit & Integration Tests

Existing coverage:

- Unit tests under `tests/unit/` for config, auth, and core utilities.
- Integration tests under `tests/integration/` for:
  - Admin dashboard & JWT admin backend.
  - OpenAPI surface and CORS behavior.
  - SQL API flows and authentication behavior.

### 7.2 End-to-End (E2E) Testing

Canonical E2E test:

- `tests/e2e/test_full_sql_flow.py` – drives the complete pipeline:
  - Authenticated SQL generate → validate → execute.
  - Query history retrieval.
  - Feedback submission and training request.

**Standard:** New end-to-end scenarios (e.g., additional feedback workflows) should extend `tests/e2e/` and follow the same style as `test_full_sql_flow.py`.

---

## 8. Backups & Operational Tasks

### 8.1 Backup & Restore

Backup APIs are defined in `app/api/v1/routes/db_admin.py`:

- `POST /api/v1/admin/db/backup` – triggers async full system backup.
- `GET /api/v1/admin/db/backup/status/{task_id}` – checks backup task status.
- `GET /api/v1/admin/db/backup/list` – lists recent backup files.
- `POST /api/v1/admin/db/backup/restore/{backup_filename}` – triggers async restore.

Implementation details:

- Celery tasks in `app/tasks/backup_tasks.py` orchestrate:
  - `backup_all_systems`
  - `restore_all_systems`
  - `verify_backup`
- Backup artifacts are written under `BACKUP_DIR` (default `backups/`) set in `Settings`.
- `scripts/lib/backup_manager.py` encapsulates the underlying backup mechanics.

**Standard:** Backups and restores must always be triggered through the API + Celery task flow; direct manual DB dumps are not part of the official contract.

---

## 9. Change Management

When changing architecture-critical behavior (config, auth, DB URLs, vector DB, CORS, rate limiting, or backup semantics):

1. Update this `TECHNICAL_REFERENCE.md` to reflect the new standard.
2. Update `app/config.py` or other central modules rather than scattering logic.
3. Add or update tests in:
   - `tests/unit/` for configuration and helpers.
   - `tests/integration/` for API and CORS behavior.
   - `tests/e2e/` for full workflows.

This document should always be considered the ground truth for how the Vanna Insight Engine is intended to behave in production.

