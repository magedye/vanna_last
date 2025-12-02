# Script Hierarchy & Command Reference

## Visual Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│  ENTRYPOINT SCRIPTS (User runs these)                            │
├─────────────────────────────────────────────────────────────────┤
│  ./run.sh                     └─ Docker lifecycle (up/down/logs) │
│  ./db_init.sh                 └─ Database initialization         │
│  ./run.ps1                    └─ Windows PowerShell equivalent   │
└─────────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────────┐
│  ORCHESTRATION (Called by db_init.sh)                            │
├─────────────────────────────────────────────────────────────────┤
│  docker exec api python scripts/init_project.py                  │
│                    └─ Master Database Initializer                │
└─────────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────────┐
│  INITIALIZATION STEPS (Executed sequentially)                    │
├─────────────────────────────────────────────────────────────────┤
│  1. check_environment()          └─ Validate config              │
│  2. check_database_connectivity() └─ Test DB connection          │
│  3. create_tables()              └─ SQLAlchemy schema            │
│  4. run_alembic_migrations()     └─ Alembic migrations           │
│  5. load_ontology()              └─ Business terms               │
│  6. create_admin_user()          └─ User creation (username)     │
│  7. seed_sample_data()           └─ Test data (idempotent)       │
│  8. setup_target_db_golden_copy() └─ DB backup strategy          │
│  9. validate_schema()            └─ Verification                 │
└─────────────────────────────────────────────────────────────────┘
```

## File Organization

```
vanna-engine/
├── run.sh ........................... [1] Start Docker containers
├── run.ps1 .......................... [1] Windows start script
├── db_init.sh ....................... [2] Initialize database
│
├── docker-compose.yml ............... Docker service definitions
├── docker-compose.prod.yml .......... Production overrides
├── docker/ .......................... Docker build files
│   └── env/
│       ├── .env.dev ................. Development configuration
│       ├── .env.stage ............... Staging configuration
│       └── .env.example ............. Configuration template
│
├── scripts/
│   ├── init_project.py .............. [3] Master initializer (NEW)
│   ├── init_system_db.py ............ [DEPRECATED] Wrapper only
│   ├── init_project_enhanced.py ..... [DEPRECATED] Wrapper only
│   │
│   ├── train_vanna_model.py ......... Vanna model training
│   ├── validate_vanna_model.py ...... Model validation
│   ├── generate_training_data.py .... Training data generation
│   │
│   └── verify_endpoints.py .......... API endpoint verification
│
├── migrations/
│   ├── env.py ....................... Alembic environment
│   ├── alembic.ini .................. Alembic configuration
│   └── versions/
│       ├── 001_init.py .............. Initial schema
│       └── 002_rename_email_to_username.py ... Auth migration
│
└── logs/
    └── init_project.log ............. Initialization log
```

---

## Quick Command Reference

### Environment Setup (First Time)

```bash
# 1. Copy environment configuration
cp docker/env/.env.example docker/env/.env.dev

# 2. Edit configuration (set LLM keys, passwords, etc.)
nano docker/env/.env.dev

# 3. Start Docker services
./run.sh

# 4. Initialize database (Alembic migrations will run)
./db_init.sh

# 5. Verify login works (username-based auth)
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'
```

### Regular Operations

```bash
# Start services
./run.sh

# Stop services
./run.sh --clean

# View logs
docker-compose logs -f api

# Access database
docker-compose exec -T api sqlite3 database.db

# Run tests
docker-compose exec -T api pytest

# Initialize database
./db_init.sh

# Force reinitialize
./db_init.sh --force

# Clean and reinitialize
./db_init.sh --clean
```

### Database Migration

```bash
# Inside container or with Python installed:

# Run pending migrations
alembic upgrade head

# Check migration status
alembic current

# Create new migration
alembic revision --autogenerate -m "description"

# Rollback last migration
alembic downgrade -1

# View migration history
alembic history --verbose
```

### Production Deployment

```bash
# 1. Prepare production environment
cp docker/env/.env.example docker/env/.env.prod
nano docker/env/.env.prod

# 2. Set environment and start services
./run.sh --env prod

# 3. Initialize database
./db_init.sh

# 4. Verify schema migration
docker exec api python -c "
from app.db.database import engine
from sqlalchemy import inspect
inspector = inspect(engine)
cols = [c['name'] for c in inspector.get_columns('users')]
assert 'username' in cols, 'Username column missing!'
print('✓ Schema verified')
"

# 5. Test admin login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "yourpassword"}'
```

### Troubleshooting

```bash
# View detailed logs
docker-compose logs api | tail -100

# Check database structure
docker exec api python scripts/init_project.py --verbose

# Verify Alembic configuration
docker exec api alembic current

# Test database connection
docker exec api python -c "
from app.db.database import engine
print('✓ Database connection OK')
"

# Check environment variables
docker exec api env | grep DATABASE_URL
```

---

## Deprecation Notice

### Old Scripts (Deprecated - Will Be Removed 2025-12-20)

```bash
# DO NOT USE (shows deprecation warning)
python scripts/init_system_db.py

# DO NOT USE (shows deprecation warning)
python scripts/init_project_enhanced.py

# USE INSTEAD
python scripts/init_project.py
```

Both deprecated scripts will automatically redirect to `init_project.py` but show a deprecation warning. They will be removed entirely on **2025-12-20**.

**Migration Path:**
```bash
# Old approach (deprecated)
./db_init.sh  # calls init_system_db.py internally

# New approach (use db_init.sh - it already calls init_project.py)
./db_init.sh  # calls init_project.py internally
```

---

## Environment Variables Reference

### Required Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@postgres:5432/vanna_db

# Authentication
SECRET_KEY=your-secret-key-here

# Redis
REDIS_URL=redis://:password@redis:6379/0
REDIS_PASSWORD=your-redis-password

# Admin User (for initialization)
INIT_ADMIN_USERNAME=admin
INIT_ADMIN_PASSWORD=admin
INIT_ADMIN_RECOVERY_EMAIL=admin@example.com  # optional
```

### Optional Variables

```bash
# Application
APP_ENV=development
DEBUG=true

# LLM Provider
LLM_PROVIDER=openai
OPENAI_API_KEY=your-key
AZURE_OPENAI_KEY=your-key  # if using Azure

# Vector Database
VECTOR_DB_TYPE=chroma
CHROMA_HOST=chroma
CHROMA_PORT=8000

# Database Pool
DB_POOL_SIZE=5
DB_POOL_TIMEOUT=30

# DBT (if using)
DBT_PROJECT_PATH=dbt_project
DBT_PROFILE_NAME=vanna_engine
```

---

## Port Configuration

Default ports (can be adjusted in `.env` files):

| Service | Port | URL |
|---------|------|-----|
| FastAPI | 8000 | http://localhost:8000 |
| Chroma | 8001 | http://localhost:8001 |
| Flower | 5555 | http://localhost:5555 |
| PostgreSQL | 5432 | localhost:5432 |
| Redis | 6380 | 127.0.0.1:6380 |

---

## Data Directories

Persistent data is stored in:

```
vanna-engine/data/
├── postgres/    # PostgreSQL database files
├── redis/       # Redis persistence
├── chroma/      # ChromaDB vector store
├── app/         # Application data
└── target_db/   # Target database (Golden Copy)
```

**Backup Strategy:**
```bash
# Backup all data
tar -czf vanna_backup_$(date +%Y%m%d).tar.gz data/

# Restore from backup
tar -xzf vanna_backup_20251120.tar.gz

# Individual service backup
cp -r data/postgres vanna_postgres_backup/
```

---

## Health Checks

```bash
# API health
curl http://localhost:8000/health

# Database connection
curl http://localhost:8000/admin/config | jq .database_status

# Full diagnostic
curl http://localhost:8000/metrics

# Service status
docker-compose ps
```

---

## Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| "API container not found" | Services not running | Run: `./run.sh` |
| "Database connection failed" | Wrong DATABASE_URL | Check `.env` file |
| "Migration failed" | Alembic not configured | Run: `./db_init.sh` |
| "Login fails with username" | Email → username migration incomplete | Run: `./db_init.sh` |
| "Port already in use" | Another service on same port | Edit `.env` to use different port |
| "Data lost on restart" | Named volumes not configured | Check `docker-compose.yml` volumes section |

---

## Next Steps

1. **Start services:** `./run.sh`
2. **Initialize database:** `./db_init.sh`
3. **Test API:** `curl http://localhost:8000/health`
4. **Login (username):** `curl -X POST "http://localhost:8000/api/v1/auth/login" -H "Content-Type: application/json" -d '{"username": "admin", "password": "admin"}'`
5. **View docs:** Visit http://localhost:8000/docs

---

**Last Updated:** 2025-11-20
**Status:** ✅ Current
**Version:** 1.0
