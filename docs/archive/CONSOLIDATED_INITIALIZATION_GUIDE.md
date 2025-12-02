# Consolidated Initialization Guide

**Final Comprehensive Refactoring Complete**
**Date:** 2025-11-20
**Status:** ✅ Production Ready

---

## Table of Contents

1. [What Changed](#what-changed)
2. [Quick Start](#quick-start)
3. [Detailed Workflow](#detailed-workflow)
4. [Authentication System](#authentication-system)
5. [Alembic Migrations](#alembic-migrations)
6. [Docker & Volumes](#docker--volumes)
7. [Troubleshooting](#troubleshooting)
8. [Deprecated Scripts](#deprecated-scripts)

---

## What Changed

### Script Consolidation

**Before (Complex):**
```
run.sh
├── docker-compose.yml
└── db_init.sh
    ├── init_system_db.py (System DB initialization)
    ├── init_project_enhanced.py (Legacy enhanced setup)
    └── startup.sh (Deprecated utilities)
```

**After (Unified):**
```
run.sh (unchanged)
├── docker-compose.yml (enhanced with volumes)
└── db_init.sh (updated to call)
    └── scripts/init_project.py (single master initializer)
```

### Key Improvements

| Aspect | Before | After |
|--------|--------|-------|
| **Scripts** | 3 competing scripts | 1 master script |
| **Alembic** | Not integrated | Fully integrated |
| **Auth** | Email-based | Username-based |
| **Migration** | Manual SQL | Alembic migration |
| **Idempotency** | Inconsistent | Guaranteed |
| **Error Handling** | Basic | Comprehensive |
| **Logging** | Scattered | Centralized |
| **Data Persistence** | Ad-hoc | Named volumes |

---

## Quick Start

### Absolute Minimal Setup (3 Commands)

```bash
# 1. Start services
./run.sh

# 2. Initialize database (runs master initializer with Alembic)
./db_init.sh

# 3. Test login (username-based auth)
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'
```

**Expected Output:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "username": "admin"
}
```

---

## Detailed Workflow

### Initialization Sequence

The `./db_init.sh` script orchestrates the following sequence:

```
1. Docker Environment Check
   └─ Verify Docker daemon is running

2. Locate API Container
   └─ Find running container with name "api"

3. Container Health Check
   └─ Wait for container to be ready (max 30s)

4. Optional: Clean Database
   └─ If --clean flag passed, remove old database

5. Master Initializer (init_project.py)
   ├─ 1. Environment validation
   ├─ 2. Database connectivity check
   ├─ 3. SQLAlchemy table creation
   ├─ 4. Alembic migration execution ⭐ CRITICAL
   ├─ 5. Business ontology loading
   ├─ 6. Admin user creation (username-based)
   ├─ 7. Sample data seeding
   ├─ 8. Target DB Golden Copy
   └─ 9. Schema validation

6. Summary and Next Steps
   └─ Display credentials and quick links
```

### What init_project.py Does

**Master Database Initializer** (`scripts/init_project.py`) is the single source of truth:

```python
class MasterDatabaseInitializer:
    def run(self):
        """Execute all initialization steps."""

        # Step 1: Check environment
        if not self.check_environment():
            return False  # Exit on failure

        # Step 2: Check DB connectivity
        if not self.check_database_connectivity():
            return False

        # Step 3: Create tables
        if not self.create_tables():
            return False

        # Step 4: Run Alembic migrations (NEW - CRITICAL)
        if not self.run_alembic_migrations():
            return False

        # Step 5-9: Continue with other initialization...

        return True
```

**Key Feature: Alembic Integration**

```python
def run_alembic_migrations(self) -> bool:
    """Run Alembic migrations (CRITICAL for schema updates)."""

    # This handles the email → username migration
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )

    # On success: email column renamed to username
    # On failure: schema remains unchanged, can retry
```

---

## Authentication System

### Migration: Email → Username

**Before Migration:**
```python
# User model had email field
class User:
    id: int
    email: str  # ← Unique login identifier
    password_hash: str
    role: str

# Login endpoint
POST /api/v1/auth/login
{
  "email": "admin@example.com",
  "password": "admin"
}
```

**After Migration:**
```python
# User model now has username field
class User:
    id: int
    username: str  # ← Unique login identifier (NEW)
    password_hash: str
    recovery_email: str  # ← Optional recovery method (NEW)
    role: str

# Login endpoint (NEW)
POST /api/v1/auth/login
{
  "username": "admin",  # ← Changed from email
  "password": "admin"
}
```

### How Alembic Handles the Migration

**Migration File:** `migrations/versions/002_rename_email_to_username.py`

```python
def upgrade():
    # Safely rename column
    op.alter_column('users', 'email', new_column_name='username')

    # Add optional recovery email field
    op.add_column('users', sa.Column('recovery_email', sa.String(255)))

    # Create unique index on username
    op.create_index('ix_users_username', 'users', ['username'], unique=True)

def downgrade():
    # Can be rolled back if needed
    op.drop_index('ix_users_username')
    op.drop_column('users', 'recovery_email')
    op.alter_column('users', 'username', new_column_name='email')
```

### Environment Variables

Set these in `.env` files before running `./db_init.sh`:

```bash
# Admin user creation (during initialization)
INIT_ADMIN_USERNAME=admin
INIT_ADMIN_PASSWORD=admin
INIT_ADMIN_RECOVERY_EMAIL=admin@example.com  # Optional

# Use these when creating additional users
INIT_ADMIN_USERNAME=john
INIT_ADMIN_PASSWORD=secure-password-here
INIT_ADMIN_RECOVERY_EMAIL=john@company.com
```

### Testing the New System

```bash
# 1. Run initialization
./db_init.sh

# 2. Login with USERNAME (not email)
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin"
  }'

# 3. Should receive JWT token
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "username": "admin"
}

# 4. Use token to access protected endpoints
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/query
```

---

## Alembic Migrations

### What is Alembic?

Alembic is the database migration framework for SQLAlchemy. It:
- Tracks schema changes over time
- Allows applying/rolling back migrations
- Integrates with version control
- Handles complex schema transformations

### How It Works in init_project.py

1. **Check for migrations**
   ```python
   migrations_dir = PROJECT_ROOT / "migrations" / "versions"
   if not migrations_dir.exists():
       logger.info("No migrations found, skipping")
   ```

2. **Execute pending migrations**
   ```python
   subprocess.run(["alembic", "upgrade", "head"])
   # Applies all migrations up to the latest version
   ```

3. **Verify results**
   ```python
   inspector = inspect(engine)
   columns = inspector.get_columns("users")
   assert "username" in columns
   ```

### Migration Files

```
migrations/
├── versions/
│   ├── 001_init.py
│   │   └── Creates initial schema (users, queries, feedback, etc.)
│   │
│   ├── 002_rename_email_to_username.py
│   │   ├── def upgrade():
│   │   │   └── Rename email → username, add recovery_email
│   │   └── def downgrade():
│   │       └── Undo the changes
│   │
│   └── [Future migrations will be added here]
│
├── env.py ..................... Alembic environment configuration
├── script.py.mako ............. Template for auto-generated migrations
└── alembic.ini ................ Alembic configuration
```

### Creating New Migrations

If you need to add a new column or change schema:

```bash
# 1. Install Alembic (if not already installed)
pip install alembic

# 2. Generate migration from model changes
alembic revision --autogenerate -m "add_new_column"

# 3. Review generated migration
nano migrations/versions/003_add_new_column.py

# 4. Apply migration
alembic upgrade head

# 5. Or inside running container
docker exec api alembic upgrade head
```

### Migration Best Practices

```python
# Good: Include both upgrade and downgrade
def upgrade():
    op.add_column('users', sa.Column('new_field', sa.String(100)))

def downgrade():
    op.drop_column('users', 'new_field')

# Good: Use reversible operations
op.alter_column('users', 'email', new_column_name='username')

# Bad: Operations that can't be rolled back
# op.execute("DELETE FROM users WHERE role='temp'")
```

---

## Docker & Volumes

### Updated docker-compose.yml

The refactored `docker-compose.yml` includes named volumes with bind mounts for data persistence:

```yaml
volumes:
  postgres_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ./data/postgres

  redis_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ./data/redis

  chroma_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ./data/chroma

  app_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ./data/app

  target_db:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ./data/target_db
```

### Directory Structure

```
vanna-engine/
└── data/
    ├── postgres/      # PostgreSQL data files
    │   └── [auto-created on first run]
    │
    ├── redis/         # Redis persistence
    │   └── [auto-created on first run]
    │
    ├── chroma/        # ChromaDB vector embeddings
    │   └── [auto-created on first run]
    │
    ├── app/           # Application data
    │   └── [auto-created on first run]
    │
    └── target_db/     # Target database (Golden Copy)
        └── [auto-created on first run]
```

### Benefits of Named Volumes

✅ Data persists across container restarts
✅ Easy backup/restore (copy `data/` directory)
✅ Clear separation of service data
✅ Compatible with production deployments
✅ Support for distributed systems

### Backup Strategy

```bash
# Backup all data (before upgrade)
tar -czf vanna_backup_$(date +%Y%m%d_%H%M%S).tar.gz data/

# Restore from backup
tar -xzf vanna_backup_20251120_143000.tar.gz

# Selective backup
cp -r data/postgres postgres_backup/

# Remove and recreate (clean slate)
rm -rf data/postgres
./run.sh  # Recreates data/postgres directory
./db_init.sh  # Reinitializes PostgreSQL
```

---

## Troubleshooting

### Issue 1: "API container not found"

**Symptoms:**
```
❌ API container not found (no running container with 'api' in name)
```

**Cause:** Docker services not running

**Solution:**
```bash
# Start services first
./run.sh

# Wait for containers to be ready
docker-compose ps

# Then run initialization
./db_init.sh
```

---

### Issue 2: "Database connection failed"

**Symptoms:**
```
✗ Database connectivity failed: connection refused
```

**Cause:** Database URL incorrect or PostgreSQL not healthy

**Solution:**
```bash
# Check PostgreSQL is healthy
docker-compose ps postgres
# STATUS should be: "healthy"

# Check DATABASE_URL
docker exec api env | grep DATABASE_URL

# Test connection manually
docker exec api python -c "
from app.db.database import engine
engine.connect()
print('✓ Connection OK')
"
```

---

### Issue 3: "Migration failed: email column still exists"

**Symptoms:**
```
⚠ Email column still exists - migration may not have run
```

**Cause:** Alembic didn't execute the migration

**Solution:**
```bash
# Check migration status
docker exec api alembic current

# Force migration
docker exec api alembic upgrade head

# Restart API
docker-compose restart api

# Verify results
docker exec api python -c "
from app.db.database import engine
from sqlalchemy import inspect
inspector = inspect(engine)
cols = [c['name'] for c in inspector.get_columns('users')]
print(f'User columns: {cols}')
assert 'username' in cols, 'Migration still failed'
"
```

---

### Issue 4: "Login fails: Invalid username or password"

**Symptoms:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -d '{"username": "admin", "password": "admin"}'
# Returns 401 Unauthorized
```

**Cause:**
1. User wasn't created, or
2. Password incorrect, or
3. Schema not migrated (still using email)

**Solution:**
```bash
# Re-run initialization
./db_init.sh

# Check user exists
docker exec api python -c "
from app.db.database import SessionLocal
from app.db.models import User
db = SessionLocal()
user = db.query(User).filter_by(username='admin').first()
if user:
    print(f'✓ User found: {user.username}')
else:
    print('✗ User not found')
"

# Test with correct password
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'
```

---

### Issue 5: "Data lost on container restart"

**Symptoms:**
```
Data disappears after: docker-compose down && docker-compose up
```

**Cause:** Named volumes not properly bound

**Solution:**
```bash
# Verify volumes are properly mounted
docker-compose config | grep -A 5 "volumes:"

# Check that data/ directory exists
ls -la data/
# Should see: postgres/ redis/ chroma/ app/ target_db/

# Stop and restart (preserves data)
docker-compose down
docker-compose up -d
# Data in data/ directory should still be there

# Clean completely (DESTROYS DATA!)
./run.sh --clean
# Then reinitialize
./db_init.sh
```

---

### Issue 6: "Port already in use"

**Symptoms:**
```
Error: Cannot start service api: listen tcp :8000: bind: address already in use
```

**Cause:** Another service using port 8000

**Solution:**
```bash
# Option 1: Change port in .env
nano docker/env/.env.dev
# Change: PORT=8001  (instead of 8000)

# Option 2: Kill process using the port
sudo lsof -i :8000
sudo kill -9 <PID>

# Option 3: Let run.sh auto-adjust
./run.sh  # Automatically finds next available port
```

---

### Issue 7: "Alembic command not found"

**Symptoms:**
```
Traceback: alembic: command not found
```

**Cause:** Alembic not installed or wrong Python environment

**Solution:**
```bash
# Install Alembic
pip install alembic

# Verify installation
alembic --version

# Or use inside container
docker exec api alembic upgrade head
```

---

## Deprecated Scripts

### What Happened

Three initialization scripts existed before consolidation:
- `scripts/init_system_db.py` - System database setup
- `scripts/init_project_enhanced.py` - Enhanced initialization
- `startup.sh` - Utilities (removed, no longer needed)

All three had overlapping functionality causing confusion and maintenance burden.

### Current Status

**All deprecated scripts now redirect to `init_project.py`**

```bash
# This still works but shows deprecation warning:
python scripts/init_system_db.py
# Output:
# ╔════════════════════════════════════════╗
# ║       SCRIPT DEPRECATED               ║
# ║  Use: scripts/init_project.py          ║
# ╚════════════════════════════════════════╝
# Redirecting to: scripts/init_project.py

# Same for init_project_enhanced.py
python scripts/init_project_enhanced.py
# Shows same warning and redirects
```

### Migration Path

| Old Command | New Equivalent | Status |
|-------------|----------------|--------|
| `python scripts/init_system_db.py` | `python scripts/init_project.py` | Deprecated |
| `python scripts/init_project_enhanced.py` | `python scripts/init_project.py` | Deprecated |
| `./db_init.sh` | `./db_init.sh` | ✅ Updated (now calls init_project.py) |

### Deprecation Timeline

- **2025-11-20:** Consolidation complete, deprecation warnings added
- **2025-12-20:** Planned removal of deprecated wrappers
- After 2025-12-20: Old scripts will no longer exist

### Why Consolidate?

**Before:**
```
Multiple scripts with overlapping features
├─ Duplicate code
├─ Inconsistent error handling
├─ No Alembic integration
└─ Difficult to maintain
```

**After:**
```
Single master initializer
├─ Single source of truth
├─ Comprehensive error handling
├─ Full Alembic integration
├─ Consistent behavior
└─ Easy to extend
```

---

## Complete Workflow Summary

### Development Setup (First Time)

```bash
# 1. Clone or navigate to project
cd /path/to/vanna-engine

# 2. Configure environment
cp docker/env/.env.example docker/env/.env.dev
nano docker/env/.env.dev
# Set: DATABASE_URL, SECRET_KEY, OPENAI_API_KEY (if using OpenAI)

# 3. Start Docker services
./run.sh

# 4. Initialize database (creates schema, runs migrations)
./db_init.sh

# 5. Verify setup
curl http://localhost:8000/health

# 6. Test login (username-based)
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'
```

### Daily Development

```bash
# Start services (if not running)
./run.sh

# Access API documentation
open http://localhost:8000/docs

# Run tests
docker-compose exec -T api pytest

# View logs
docker-compose logs -f api
```

### Production Deployment

```bash
# 1. Configure production environment
cp docker/env/.env.example docker/env/.env.prod
nano docker/env/.env.prod
# Set secure passwords and keys

# 2. Start services
./run.sh --env prod

# 3. Initialize database
./db_init.sh

# 4. Verify schema migration
docker exec api alembic current
# Should show: [version] -> [latest migration]

# 5. Test admin login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "yourpassword"}'

# 6. Monitor logs
docker-compose logs -f api
```

---

## Key Files Reference

| File | Purpose | Status |
|------|---------|--------|
| `run.sh` | Start/stop Docker services | ✅ Unchanged |
| `db_init.sh` | Database initialization orchestrator | ✅ Updated |
| `scripts/init_project.py` | Master initializer | ✅ NEW (critical) |
| `migrations/versions/002_*.py` | Email → username migration | ✅ NEW |
| `docker-compose.yml` | Service definitions | ✅ Updated (volumes) |
| `FINAL_REFACTORING_SUMMARY.md` | Complete refactoring overview | ✅ NEW |
| `SCRIPT_HIERARCHY.md` | Command reference | ✅ NEW |
| `AGENTS.md` | Agent commands | ✅ Updated |

---

## Next Steps

1. **Review** this guide and FINAL_REFACTORING_SUMMARY.md
2. **Test locally:** Follow "Development Setup" above
3. **Verify authentication** works with username
4. **Check Alembic** migrations run: `docker exec api alembic current`
5. **Plan migration** if running existing system
6. **Deploy** to staging first, then production

---

## Support & Questions

- **Schema issues:** Check `FINAL_REFACTORING_SUMMARY.md` section 6
- **Authentication:** See "Authentication System" section above
- **Migrations:** Reference "Alembic Migrations" section
- **Docker:** Review "Docker & Volumes" section
- **Commands:** Use AGENTS.md or SCRIPT_HIERARCHY.md

---

**Generated:** 2025-11-20
**Version:** 1.0
**Status:** ✅ Production Ready
