# Golden Copy Strategy Implementation Guide

## Overview

The "Golden Copy" strategy protects the original analytical database (mydb.db) by creating a working copy for runtime access. This architecture cleanly separates:

1. **System Database** (PostgreSQL): User authentication, queries, feedback, audit logs
2. **Target Database** (SQLite): Read-only analytical business data

## Architecture

```
mydb.db (Original - Protected)
    ↓
    ├─ Copy to runtime on startup
    ↓
/app/data/vanna_db.db (Working Copy - Read-Only)
    ↓
Application reads data
    ↓
System DB (PostgreSQL)
    └─ User credentials, authentication, queries
```

## Implementation Components

### 1. Golden Copy Manager (`scripts/lib/golden_copy.py`)

Manages the copy operation with these features:

- **Source Priority**: Checks `mydb.db` in project root first
- **Idempotent**: Only copies if runtime doesn't exist
- **Verification**: Compares file sizes after copy
- **Direct Source Support**: Can use specific file path instead of directory

**Key Methods:**
```python
copy_source_to_runtime(force=False)  # Copy with optional force override
get_runtime_db_url(read_only=True)   # Get SQLite connection string
```

### 2. Project Initialization (`scripts/init_project.py`)

Updated to:

1. **Detect mydb.db** in project root (`/home/mfadmin/new-vanna/mydb.db`)
2. **Use it as Golden Copy source** automatically
3. **Initialize System Database** (PostgreSQL) separately
4. **Skip writes to SQLite** - only reads occur

**Initialization Flow:**
```
1. setup_golden_copy()           # Copy mydb.db to runtime
   └─ Copy mydb.db → /app/data/vanna_db.db

2. run_system_db_initialization() # Initialize PostgreSQL
   └─ Create users, queries, feedback tables

3. setup_chromadb_training()      # Optional vector DB training
```

### 3. Database Configuration (`docker/env/.env.example`)

**System Database (REQUIRED):**
```bash
DB_TYPE=postgresql
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<secure_password>
POSTGRES_DB=vanna_db
```

This database stores:
- User credentials and authentication
- Query history and feedback
- Audit logs
- Application configurations

**Target Database (OPTIONAL):**
```bash
ENABLE_TARGET_DB=false              # Set to true to enable
TARGET_DATABASE_URL=                # URL to SQLite/other DB
TARGET_DB_SOURCE=assets/databases/vanna_db.db
TARGET_DB_PATH=/app/data/vanna_db.db
```

### 4. Database Initialization (`app/db/database.py`)

The `init_db()` function:
- Only writes to `settings.DATABASE_URL` (PostgreSQL System Database)
- Never modifies the Target Database (SQLite)
- Creates tables: users, queries, feedback, audit_logs, configurations, business_ontologies

```python
def init_db():
    """Initialize database tables."""
    # This ONLY writes to System Database (PostgreSQL)
    Base.metadata.create_all(bind=engine)
```

## Data Flow

### User Authentication (System Database)
```
User Login Request
    ↓
Query users table (PostgreSQL)
    ↓
Validate credentials
    ↓
Create session (Redis)
```

### Analytical Queries (Target Database)
```
User Query Request
    ↓
Query Target DB (/app/data/vanna_db.db)
    ↓
Read-only execution
    ↓
Store query result in System DB (audit log)
```

## Key Features

### ✅ Read-Only Access to Target Database
- SQLite opened with `mode=ro` flag
- No accidental writes to business data
- Original mydb.db never modified

### ✅ Automatic Copy on Startup
- Idempotent: Safe to re-run initialization
- Verifies file integrity after copy
- Logs detailed status

### ✅ User Data in PostgreSQL
- Single source of truth for authentication
- Atomic transactions for security
- Better concurrency support

### ✅ Optional Target Database
- Works with or without TARGET_DATABASE_URL
- Graceful degradation if not configured
- Business data analysis is optional feature

## File Locations

| Component | Location | Purpose |
|-----------|----------|---------|
| Original Database | `/home/mfadmin/new-vanna/mydb.db` | Source (Protected) |
| Working Copy | `/app/data/vanna_db.db` | Runtime (Read-Only) |
| System DB | `postgres://host:5432/vanna_db` | User Data |
| Golden Copy Manager | `scripts/lib/golden_copy.py` | Copy Logic |
| Initialization | `scripts/init_project.py` | Orchestrator |
| Configuration | `docker/env/.env.example` | Environment Template |

## Environment Variables

```bash
# System Database (REQUIRED)
DB_TYPE=postgresql                          # Type of system DB
POSTGRES_HOST=postgres                      # Host
POSTGRES_PORT=5432                          # Port
POSTGRES_USER=postgres                      # Username
POSTGRES_PASSWORD=<password>                # Password
POSTGRES_DB=vanna_db                        # Database name

# Golden Copy & Target Database
ENABLE_TARGET_DB=false                      # Enable target DB
TARGET_DATABASE_URL=                        # Target DB URL
TARGET_DB_SOURCE=assets/databases/vanna_db.db   # (Fallback)
TARGET_DB_PATH=/app/data/vanna_db.db        # Runtime location

# Initialization
SEED_DEMO_DATA=true                         # Seed sample data
INIT_ADMIN_USERNAME=admin@example.com       # Admin user
INIT_ADMIN_PASSWORD=AdminPassword123        # Admin password
```

## Startup Process

### 1. Project Initialization
```bash
cd /home/mfadmin/new-vanna/vanna-engine
python scripts/init_project.py
```

**Actions:**
- Detects mydb.db in project root
- Creates /app/data/vanna_db.db as working copy
- Initializes PostgreSQL System Database
- Creates admin user
- Trains ChromaDB (if enabled)

### 2. Start Services
```bash
./run.sh  # Docker Compose
```

**Services:**
- PostgreSQL (System Database)
- Redis (Caching & message broker)
- FastAPI (Application)
- ChromaDB (Vector store, optional)
- Celery (Task queue, optional)

### 3. Verify Setup
```bash
# Health check
curl http://localhost:8000/health

# Login with default credentials
# Email: admin@example.com
# Password: AdminPassword123 (from env or random generated)
```

## Troubleshooting

### Issue: mydb.db not found
**Solution:** Place mydb.db in `/home/mfadmin/new-vanna/mydb.db`
```bash
cp /path/to/mydb.db /home/mfadmin/new-vanna/mydb.db
```

### Issue: Golden Copy not created
**Check:**
```bash
ls -lh /home/mfadmin/new-vanna/mydb.db        # Original exists?
ls -lh /app/data/vanna_db.db                  # Working copy created?
```

**Logs:**
```bash
tail -f vanna-engine/logs/init_project.log
```

### Issue: User table creation failed
**Ensure:** PostgreSQL is running and DATABASE_URL is correct
```bash
docker-compose ps postgres  # Check if running
```

### Issue: Target DB not accessible
**This is non-critical** - System DB will work, but Target DB features disabled
- Verify TARGET_DATABASE_URL if configured
- Set ENABLE_TARGET_DB=true only if Target DB exists

## Production Checklist

- [ ] PostgreSQL running and accessible
- [ ] mydb.db placed in project root
- [ ] DATABASE_URL points to PostgreSQL
- [ ] SEED_DEMO_DATA=false (prevent test data)
- [ ] Proper admin credentials set
- [ ] ENABLE_TARGET_DB=true only if Target DB ready
- [ ] Backups configured (BACKUP_DIR)
- [ ] Redis running for caching

## See Also

- [AGENTS.md](../../AGENTS.md) - Common commands
- [docker-compose.yml](./docker-compose.yml) - Service definitions
- [app/config.py](./app/config.py) - Configuration details
- [app/db/models.py](./app/db/models.py) - Data models
