# Quick Reference - New Startup Workflow

**Date:** November 20, 2025
**Version:** 1.0.0

---

## New Workflow (2 Steps)

### Development Setup
```bash
# Step 1: Start Docker infrastructure
./run.sh --clean --build

# Step 2: Initialize database and application
./db_init.sh

# Step 3: Verify
curl http://localhost:8000/health
```

### Production Deployment
```bash
# Step 1: Configure
cp docker/env/.env.example docker/env/.env.dev
nano docker/env/.env.dev  # Edit APP_ENV, DEBUG, WORKERS, etc.

# Step 2: Start infrastructure
./run.sh --env prod

# Step 3: Initialize application
./db_init.sh

# Step 4: Verify
curl http://localhost:8000/health
```

---

## Flags & Options

### run.sh
| Flag | Purpose |
|------|---------|
| `--build` | Rebuild Docker images |
| `--clean` | Remove containers/volumes before start |
| `--env prod` | Use production environment |
| `--diagnose` | Show system diagnostics |

### db_init.sh
| Flag | Purpose |
|------|---------|
| `--force` | Force reinitialize (not recommended) |
| `--clean` | Delete database before init |

---

## Common Commands

```bash
# View running containers
docker ps

# View API logs
docker-compose logs -f api

# Access container shell
docker-compose exec api bash

# Restart a service
docker-compose restart api

# Stop all services
docker-compose down

# View all ports being used
grep "PORT=" docker/env/.env.dev

# Check API health
curl http://localhost:8000/health | jq .

# Access API documentation
open http://localhost:8000/docs  # macOS
xdg-open http://localhost:8000/docs  # Linux
```

---

## What Each Script Does

### `./run.sh` (Infrastructure)
- ✓ Detects Docker Compose binary
- ✓ Validates environment files
- ✓ Checks and resolves port conflicts
- ✓ Creates Docker network
- ✓ Removes stale containers
- ✓ Starts services with docker-compose

### `./db_init.sh` (Application)
- ✓ Finds running API container
- ✓ Validates container readiness
- ✓ Executes `init_project_enhanced.py` which:
  - Creates database tables
  - Runs Alembic migrations
  - Loads business ontology
  - Creates admin user
  - Seeds sample data
  - Validates schema

---

## Default Credentials

After running `./db_init.sh`:

| Field | Value |
|-------|-------|
| **Email** | `admin@example.com` |
| **Password** | `[REDACTED:password]` |
| **Role** | `admin` |

⚠️ **CHANGE IN PRODUCTION**

---

## Troubleshooting

### Containers won't start
```bash
./run.sh --diagnose  # Show system info
docker-compose logs   # Check logs
```

### Database initialization fails
```bash
# Check if containers are running
docker ps

# View detailed logs
./db_init.sh 2>&1 | tee /tmp/init.log

# Look for error messages
docker-compose logs api | grep ERROR
```

### Port already in use
- `run.sh` auto-detects and bumps ports
- Check: `grep "PORT=" docker/env/.env.dev`
- Or specify port: Edit `.env` file before running

### Idempotent re-run needed
```bash
# Safe to re-run (checks for existing records)
./db_init.sh
```

---

## Migration from Old Workflow

| Old | New |
|-----|-----|
| `./startup.sh` | `./run.sh` + `./db_init.sh` |
| `python scripts/init_project.py` | `./db_init.sh` |

---

## Documentation Files

| File | Purpose |
|------|---------|
| **README.md** | Development quick start |
| **QUICK_STARTUP.md** | Production deployment guide |
| **AGENTS.md** | Common commands reference |
| **REFACTORING_SUMMARY.md** | Technical refactoring details |
| **This file** | Quick reference card |

---

## Key Improvements

✅ **Separation of Concerns**
- Infrastructure (Docker) separate from application setup

✅ **Better Debugging**
- Isolate failures to infrastructure vs. application layer

✅ **Idempotent**
- `db_init.sh` safe to re-run multiple times

✅ **CI/CD Friendly**
- Can handle infrastructure and application stages independently

---

## More Information

- Full guide: `README.md`
- Production: `QUICK_STARTUP.md`
- Commands: `AGENTS.md`
- Technical: `REFACTORING_SUMMARY.md`

---

**Status:** Production Ready ✅
