# Quick Startup - Production Deployment

**Version:** 1.0.0  
**Date:** November 16, 2025  
**Status:** Production-Ready  
**Audience:** DevOps, SREs, Production Operators

> ⚠️ **CRITICAL**: `SECRET_KEY` and `JWT_SECRET_KEY` are **REQUIRED**. The application will fail to start without them. See [Variables You MUST Change](#variables-you-must-change-🔴-critical-security) below.

---

## TL;DR – Deploy in 60 Seconds

```bash
# 1. Configure environment
cp docker/env/.env.example .env.prod
nano .env.prod  # MUST set SECRET_KEY and JWT_SECRET_KEY

# 2. Start containers (Infrastructure)
./run.sh --env prod

# 3. Initialize database (Application)
./db_init.sh

# 4. Verify
curl http://localhost:8000/health | jq .
```

Done. Your production stack is live.

---

## What You Must Configure

**Before deploying, you MUST modify `.env.prod` with your production values.**

### Variables You MUST Change (🔴 Critical Security)

| Variable | Status | What to Enter | Example |
|----------|--------|---------------|---------|
| `SECRET_KEY` | 🔴 MUST CHANGE | App secret (min 32 chars) | `openssl rand -hex 32` |
| `JWT_SECRET_KEY` | 🔴 MUST CHANGE | JWT signing key (min 32 chars) | `openssl rand -hex 32` |
| `OPENAI_API_KEY` | 🔴 MUST CHANGE | Your production OpenAI key | `sk-proj-abc123xyz...` |
| `DATABASE_URL` | 🔴 MUST CHANGE | Production Postgres connection | `postgresql://user:pass@postgres:5432/vanna_db` |
| `POSTGRES_PASSWORD` | 🔴 MUST CHANGE | Strong database password | `MySecure!Pass123` |
| `REDIS_URL` | 🔴 MUST CHANGE | Production Redis connection | `redis://redis:6379/0` |

### Variables You CAN Configure (⚠️ Optional Adjustments)

| Variable | Status | Default Value | When to Change |
|----------|--------|-----------------|-----------------|
| `PORT` | ⚠️ OPTIONAL | `8000` | Only if port 8000 is already in use |
| `LOG_LEVEL` | ⚠️ OPTIONAL | `WARN` | Can set to ERROR for quieter logs |
| `SENTRY_DSN` | ⚠️ OPTIONAL | (empty) | Add if using Sentry error tracking |
| `SLACK_WEBHOOK_URL` | ⚠️ OPTIONAL | (empty) | Add if using Slack notifications |
| `CORS_ORIGINS` | ⚠️ OPTIONAL | (empty) | Add if using frontend on different domain |

### Variables You MUST NOT Change (✅ Use Defaults)

| Variable | Status | Default Value | Keep As |
|----------|--------|-----------------|---------|
| `ENVIRONMENT` | ✅ DEFAULT | `production` | Do NOT change |
| `DEBUG` | ✅ DEFAULT | `false` | Do NOT change |
| `POSTGRES_PORT` | ✅ DEFAULT | `5432` | Keep as is |
| `REDIS_PORT` | ✅ DEFAULT | `6379` | Keep as is |
| `CHROMA_PORT` | ✅ DEFAULT | `8001` | Keep as is |
| `FLOWER_PORT` | ✅ DEFAULT | `5555` | Keep as is |

---

## Prerequisites

| Requirement | Check |
|-------------|-------|
| Docker >= 20.10 | `docker --version` |
| Docker Compose >= 1.29 | `docker compose version` or `docker-compose --version` |
| `.env.prod` file created | `ls -la .env.prod` |
| Sufficient disk space | `df -h / | grep /` |
| Port 8000 available | `lsof -i :8000` (should be empty) |

---

## One-Command Production Start

```bash
./run.sh --env prod
```

This:
- ✅ Loads `.env.prod` configuration
- ✅ Applies `docker-compose.prod.yml` hardening overrides
- ✅ Detects and resolves port conflicts automatically
- ✅ Creates production Docker network
- ✅ Starts all services with gunicorn (multi-worker), CPU/RAM limits, no hot reload
- ✅ Displays endpoint URLs and health status

---

## Step-by-Step Production Deployment

### Step 1: Create and Configure `.env.prod`

**Create the file:**

```bash
cd /home/mfadmin/new-vanna/vanna-engine
cp docker/env/.env.example .env.prod
```

**Edit with YOUR production values:**

```bash
nano .env.prod
```

**Quick reference table – Which variables to edit:**

| # | Variable | Status | What to Enter |
|---|----------|--------|---------------|
| 1️⃣ | `PORT` | ⚠️ Check | Usually `8000` (change only if in use) |
| 2️⃣ | `ENVIRONMENT` | ✅ Default | Leave as `production` |
| 3️⃣ | `DEBUG` | ✅ Default | Leave as `false` |
| 4️⃣ | `LOG_LEVEL` | ✅ Default | Leave as `WARN` or change to `ERROR` |
| 5️⃣ | `DATABASE_URL` | 🔴 MUST CHANGE | Your Postgres host and credentials |
| 6️⃣ | `POSTGRES_PASSWORD` | 🔴 MUST CHANGE | Strong password for DB user |
| 7️⃣ | `REDIS_URL` | 🔴 MUST CHANGE | Your Redis host (usually `redis:6379/0`) |
| 8️⃣ | `SECRET_KEY` | 🔴 MUST CHANGE | Run: `openssl rand -hex 32` |
| 9️⃣ | `JWT_SECRET_KEY` | 🔴 MUST CHANGE | Run: `openssl rand -hex 32` |
| 🔟 | `OPENAI_API_KEY` | 🔴 MUST CHANGE | Get from https://platform.openai.com/api-keys |
| 1️⃣1️⃣ | `SENTRY_DSN` | ✅ Optional | Add only if using Sentry |

**Quick copy-paste template** (EDIT THESE VALUES BEFORE USING):

```env
# Step 1: Change these CRITICAL variables (REQUIRED - app fails without these)
PORT=8000
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@postgres:5432/vanna_db
POSTGRES_PASSWORD=YOUR_SECURE_PASSWORD
SECRET_KEY=your-secret-key-min-32-chars-random  # Generate: openssl rand -hex 32
JWT_SECRET_KEY=your-jwt-secret-min-32-chars-random  # Generate: openssl rand -hex 32
OPENAI_API_KEY=sk-your-openai-key-here

# Step 2: Keep these DEFAULTS (do not change)
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARN
REDIS_URL=redis://redis:6379/0

# Step 3: Optional - add only if needed
# SENTRY_DSN=https://key@sentry.io/project
# SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

### Step 2: Deploy Services

Start production stack:

```bash
./run.sh --env prod
```

**Expected output:**

```
========================================
🚀 Vanna Insight Engine Auto-Setup
========================================
🌍 Environment: .env.prod
📂 Working directory: /home/mfadmin/new-vanna/vanna-engine
🔧 Applying prod override file...

🔍 Checking and resolving port conflicts...
✅ Ports validated.

🛠️  Creating network: vanna_project_net
🧹 Removing stale vanna-engine containers...
🐳 Starting Docker Compose services...

------------------------------------------
✅ Deployment Successful!
------------------------------------------
🕸️  Network: vanna_project_net
📋 Environment: .env.prod

🌐 Ports:
   PORT=8000
   REDIS_PORT=6379
   POSTGRES_PORT=5432
   CHROMA_PORT=8001

📚 Documentation:
   Swagger UI: http://localhost:8000/docs
   ReDoc:      http://localhost:8000/redoc

------------------------------------------
```

### Step 3: Initialize Database (Application Setup)

After containers are running, initialize the database:

```bash
./db_init.sh
```

This script (running inside the container):
- Creates database tables
- Runs migrations
- Loads business ontology
- Creates admin user
- Seeds sample data

**Expected output:** Shows progress through each initialization step with checkmarks.

### Step 4: Verify Deployment

```bash
# 1. Check container status
docker-compose ps

# Expected: All services "Up"
# CONTAINER ID   IMAGE                    STATUS
# ...            vanna-api                Up 10 seconds
# ...            postgres                 Up 12 seconds
# ...            redis                    Up 11 seconds
# ...            chroma                   Up 9 seconds
```

```bash
# 2. Check API health
curl http://localhost:8000/health | jq .

# Expected response:
# {
#   "status": "healthy",
#   "version": "1.0.0",
#   "dependencies": {
#     "database": "connected",
#     "redis": "connected",
#     "chroma": "connected"
#   }
# }
```

```bash
# 3. Check logs
docker-compose logs --tail=20 api

# Should show no ERROR or CRITICAL messages
```

---

## Common Operations

### Stop Production Services

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
```

Or with data cleanup:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml down -v
```

### Restart a Service

```bash
docker-compose restart api
```

### View Logs

```bash
# Real-time API logs
docker-compose logs -f api

# Last 50 lines of all services
docker-compose logs --tail=50

# Search for errors
docker-compose logs | grep ERROR
```

### Scale API Workers

Edit `.env.prod` to increase API replicas:

```env
API_WORKERS=4  # or higher
```

Then redeploy:

```bash
./run.sh --env prod
```

### Force Rebuild Images

```bash
./run.sh --env prod --rebuild
```

Or manually:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

---

## Port Management

### Check Ports

```bash
# View all exposed ports
docker-compose ps

# Check specific port
lsof -i :8000

# List all service ports from .env
grep "PORT=" .env.prod
```

### Custom Port

Edit `.env.prod`:

```env
PORT=9000  # Instead of 8000
```

Restart:

```bash
./run.sh --env prod
```

If port is already in use, the script auto-increments.

---

## Database Management

### Initialize Database

```bash
# Inside the container
docker-compose exec postgres psql -U postgres -d vanna_db -c "\dt"

# Or from host (if psql installed)
psql -h localhost -U postgres -d vanna_db -c "\dt"
```

### Backup

```bash
docker-compose exec postgres pg_dump -U postgres vanna_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restore

```bash
docker-compose exec -T postgres psql -U postgres vanna_db < backup_20251114_120000.sql
```

---

## Monitoring & Logs

### Real-Time Monitoring

```bash
# Watch all service logs
docker-compose logs -f

# Watch specific service
docker-compose logs -f api

# Follow with timestamps
docker-compose logs -f --timestamps api
```

### Check Resource Usage

```bash
docker stats

# Shows CPU%, memory, network I/O for each container
```

### Prometheus Metrics

```bash
curl http://localhost:8000/metrics

# Includes request counts, latencies, error rates, etc.
```

### Application Health

```bash
# Detailed health check
curl -v http://localhost:8000/health

# Check dependencies
curl http://localhost:8000/admin/health/detailed | jq .dependencies
```

---

## Troubleshooting

### Services Won't Start

```bash
# Check logs
docker-compose logs api

# Common issues:
# - Port already in use → script auto-resolves
# - Database connection failed → check DATABASE_URL in .env.prod
# - Redis connection failed → check REDIS_URL in .env.prod
```

### Port Conflict

```bash
# Script auto-detects and bumps ports. To see what changed:
grep "PORT=" .env.prod

# Or check startup log
tail -20 startup.log | grep "🔄"
```

### API Won't Respond

```bash
# Check if container is running
docker-compose ps api

# Check logs for errors
docker-compose logs api | grep ERROR

# Restart the service
docker-compose restart api
```

### Database Connection Error

```env
# Verify in .env.prod
DATABASE_URL=postgresql://postgres:password@postgres:5432/vanna_db
```

Inside containers, use service name `postgres`, not `localhost`.

### High Memory Usage

```bash
# Check resource limits in docker-compose.prod.yml
# Adjust if needed:
services:
  api:
    mem_limit: 2g
    memswap_limit: 2g
```

Restart after changes:

```bash
./run.sh --env prod
```

---

## Clean Restart (Full Reset)

```bash
./run.sh --clean --env prod
```

This:
- Removes all containers
- Removes all volumes (DATA LOSS)
- Recreates network
- Starts fresh

**Warning:** This deletes all data. Use only for development or when you have a backup.

---

## Production Checklist

Before going live, verify:

- [ ] `.env.prod` created and all required variables set
- [ ] `SECRET_KEY` is set (min 32 chars, random - **REQUIRED**)
- [ ] `JWT_SECRET_KEY` is set (min 32 chars, random - **REQUIRED**)
- [ ] `OPENAI_API_KEY` is set (not default)
- [ ] `DATABASE_URL` points to correct Postgres instance
- [ ] `POSTGRES_PASSWORD` is not default
- [ ] `REDIS_URL` points to correct Redis instance
- [ ] Port 8000 is not in use or is intended to be mapped
- [ ] Docker and Docker Compose are installed
- [ ] Sufficient disk space available (`df -h`)
- [ ] All containers started successfully (`docker-compose ps`)
- [ ] Health endpoint responds (`curl http://localhost:8000/health`)
- [ ] Logs show no ERROR or CRITICAL messages
- [ ] Database is initialized and accessible
- [ ] Redis cache is working
- [ ] API documentation is accessible (`http://localhost:8000/docs`)

---

## Integration with CI/CD

### GitHub Actions Example

```yaml
- name: Deploy to Production
  run: |
    cd /home/mfadmin/new-vanna/vanna-engine
    cp .env.prod.secrets .env.prod  # From secrets
    ./run.sh --env prod
    sleep 10
    curl http://localhost:8000/health || exit 1
```

### GitLab CI Example

```yaml
deploy_production:
  stage: deploy
  script:
    - cd /home/mfadmin/new-vanna/vanna-engine
    - cp $PROD_ENV .env.prod
    - ./run.sh --env prod
    - sleep 10
    - curl http://localhost:8000/health
```

---

## Performance Tuning

### API Workers

Adjust in `.env.prod` or `docker-compose.prod.yml`:

```env
API_WORKERS=4  # Gunicorn worker processes (CPU-bound tasks)
```

Rule of thumb: `workers = (2 × CPU cores) + 1`

### Database Connections

```env
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10
```

### Redis

```env
REDIS_MAXMEMORY_POLICY=allkeys-lru  # Eviction policy
```

### Memory Limits

```yaml
# docker-compose.prod.yml
services:
  api:
    mem_limit: 2g  # Adjust based on load
```

---

## Support & Documentation

| Document | Purpose | Location |
|----------|---------|----------|
| **AGENTS.md** | Common commands & operations | [vanna-engine/AGENTS.md](vanna-engine/AGENTS.md) |
| **AUTH_FIXED.md** | Authentication & authorization details | [vanna-engine/AUTH_FIXED.md](vanna-engine/AUTH_FIXED.md) |
| **README.md** | Project overview & quick start | [README.md](README.md) |
| **API Documentation** | OpenAPI 3.1.0 interactive docs | http://localhost:8000/docs |
| **ReDoc** | Alternative API documentation | http://localhost:8000/redoc |

---

## One-Liner Summary

```bash
cp docker/env/.env.example .env.prod && nano .env.prod && ./run.sh --env prod && curl http://localhost:8000/health
```

---

**Maintained by:** DevOps Team  
**Last Updated:** November 14, 2025  
**Status:** Production-Ready  
**Emergency Contact:** DevOps on-call
