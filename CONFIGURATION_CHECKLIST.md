# Configuration Checklist

**Before running `./run.sh`, complete this checklist.**

---

## Environment Files Setup

### Development (`.env.dev`)

Create from template:
```bash
cp docker/env/.env.example docker/env/.env.dev
```

**Required changes:**
- [ ] `OPENAI_API_KEY` – Set to your dev OpenAI key
- [ ] `JWT_SECRET` – Set to any value (min 32 chars recommended)
- [ ] `DATABASE_URL` – Verify points to Docker Postgres
- [ ] `REDIS_URL` – Verify points to Docker Redis

**All other variables can use defaults** (PORT=8000, DEBUG=true, etc.)

---

### Staging (`.env.stage`)

Create from template:
```bash
cp docker/env/.env.example docker/env/.env.stage
```

**Required changes:**
- [ ] `PORT` – Set to available port
- [ ] `OPENAI_API_KEY` – Set to your staging OpenAI key
- [ ] `JWT_SECRET` – Set to secure random value (min 32 chars)
- [ ] `DATABASE_URL` – Point to staging Postgres server
- [ ] `POSTGRES_PASSWORD` – Set staging database password
- [ ] `REDIS_URL` – Point to staging Redis server
- [ ] `DEBUG` – Change to `false`
- [ ] `ENVIRONMENT` – Change to `staging`
- [ ] `LOG_LEVEL` – Change to `INFO`

---

### Production (`.env.prod`) – 🔴 CRITICAL

Create from template:
```bash
cp .env.example .env.prod
```

**🔴 MANDATORY CHANGES – Do not skip:**

- [ ] `PORT` – Set to production port (or accept 8000)
- [ ] `ENVIRONMENT` – Must be `production`
- [ ] `DEBUG` – Must be `false`
- [ ] `LOG_LEVEL` – Must be `WARN` or `ERROR`

**🔴 DATABASE CONFIGURATION – Must change:**

- [ ] `DATABASE_URL` – Change from `localhost` to your production Postgres host
  ```
  postgresql://user:PASSWORD@your-postgres-host:5432/vanna_db
  ```
- [ ] `POSTGRES_PASSWORD` – Set to strong production password

**🔴 CACHE CONFIGURATION – Must change:**

- [ ] `REDIS_URL` – Change from `localhost` to your production Redis host
  ```
  redis://your-redis-host:6379/0
  ```

**🔴 SECURITY CREDENTIALS – Must change:**

- [ ] `OPENAI_API_KEY` – Get from OpenAI dashboard, set to your key
  ```
  sk-proj-your-actual-key-here...
  ```
- [ ] `JWT_SECRET` – Generate random value, min 32 characters
  ```bash
  # Generate with:
  openssl rand -hex 32
  ```

**⚠️ OPTIONAL but RECOMMENDED for production:**

- [ ] `SENTRY_DSN` – If using Sentry error tracking, set to your project DSN
- [ ] `SLACK_WEBHOOK_URL` – If using Slack notifications, set to your webhook
- [ ] `CORS_ORIGINS` – If have frontend, set to frontend domain

**Do NOT change these** (use defaults):
- `POSTGRES_PORT=5432`
- `REDIS_PORT=6379`
- `CHROMA_PORT=8001`
- `FLOWER_PORT=5555`

---

## Validation Commands

### Check all required variables are set:

```bash
# Development
echo "=== DEV ===" && \
grep "OPENAI_API_KEY\|JWT_SECRET" docker/env/.env.dev | grep -v "^#"

# Staging
echo "=== STAGING ===" && \
grep "OPENAI_API_KEY\|JWT_SECRET\|DATABASE_URL\|REDIS_URL" docker/env/.env.stage | grep -v "^#"

# Production (CRITICAL)
echo "=== PRODUCTION ===" && \
grep "OPENAI_API_KEY\|JWT_SECRET\|DATABASE_URL\|REDIS_URL\|ENVIRONMENT\|DEBUG" .env.prod | grep -v "^#"
```

### Verify environment files exist:

```bash
# All required files
ls -la docker/env/.env.dev docker/env/.env.stage .env.prod
```

### Test environment file syntax (no errors):

```bash
# Source each file to check for syntax errors
bash -n docker/env/.env.dev && echo "Dev: OK"
bash -n docker/env/.env.stage && echo "Stage: OK"
bash -n .env.prod && echo "Prod: OK"
```

---

## Quick Configuration Generator

### Generate a strong JWT secret:

```bash
# Linux/macOS
openssl rand -hex 32

# Or use Python
python3 -c "import secrets; print(secrets.token_hex(32))"

# Or use node
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

### Generate a strong database password:

```bash
# Linux/macOS
openssl rand -base64 16

# Or Python
python3 -c "import secrets; print(secrets.token_urlsafe(16))"
```

---

## Startup Commands

Once configuration is complete, start with:

### Development

```bash
./run.sh
# Or explicitly
./run.sh --env dev
```

### Staging

```bash
./run.sh --env stage
```

### Production

```bash
./run.sh --env prod
```

### With clean restart (removes all containers/volumes):

```bash
./run.sh --clean --env prod
```

---

## Troubleshooting Configuration Issues

### Error: "Environment file .env.prod not found"

```bash
# Solution: Create the file
cp .env.example .env.prod
```

### Error: "Database connection refused"

```bash
# Check DATABASE_URL in .env file
grep DATABASE_URL .env.prod

# Verify Postgres is running
docker-compose ps postgres

# Verify connection string uses service name inside containers:
# ✅ CORRECT: postgresql://user:pass@postgres:5432/vanna_db
# ❌ WRONG: postgresql://user:pass@localhost:5432/vanna_db
```

### Error: "Redis connection refused"

```bash
# Check REDIS_URL in .env file
grep REDIS_URL .env.prod

# Verify Redis is running
docker-compose ps redis

# Verify connection string uses service name:
# ✅ CORRECT: redis://redis:6379/0
# ❌ WRONG: redis://localhost:6379/0
```

### Error: "Port X already in use"

```bash
# The script auto-detects and bumps ports
# But you can also manually change in .env file:
nano .env.prod
# Change PORT=8000 to PORT=9000 (or any available port)
```

### Error: "OpenAI API key invalid"

```bash
# Verify your key is set correctly
grep OPENAI_API_KEY .env.prod

# Verify format (should start with sk-)
# Get new key from: https://platform.openai.com/api-keys
```

---

## What Each Environment Variable Does

| Variable | Purpose | Example |
|----------|---------|---------|
| `PORT` | Main API port | `8000` |
| `ENVIRONMENT` | Environment name | `development`, `staging`, `production` |
| `DEBUG` | Enable debug mode (logs, hot reload) | `true` or `false` |
| `LOG_LEVEL` | Logging verbosity | `DEBUG`, `INFO`, `WARN`, `ERROR` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `POSTGRES_PASSWORD` | DB password | `YourSecurePassword123!` |
| `REDIS_URL` | Redis cache connection | `redis://host:6379/0` |
| `OPENAI_API_KEY` | OpenAI API authentication | `sk-proj-...` |
| `JWT_SECRET` | JWT token signing key | Random 32+ char string |
| `SENTRY_DSN` | Error tracking endpoint (optional) | `https://key@sentry.io/123456` |
| `SLACK_WEBHOOK_URL` | Slack notifications (optional) | `https://hooks.slack.com/...` |
| `CORS_ORIGINS` | Allowed frontend domains (optional) | `https://yourdomain.com` |

---

**Status:** All steps complete ✅

You're ready to run: `./run.sh --env prod`
