# Golden Copy Strategy - Quick Start

## What is Golden Copy?

The Golden Copy strategy protects your original analytical database (mydb.db) by creating a working copy that the application reads from. Your original file is never modified.

```
mydb.db (Original - Safe)
    ↓ [Copy on startup]
    ↓
/app/data/vanna_db.db (Working Copy - Application uses this)
    ↓
PostgreSQL (System Database - User authentication)
```

## Setup (5 minutes)

### 1. Verify mydb.db exists
```bash
ls -lh /home/mfadmin/new-vanna/mydb.db
# Output: -rw-r--r-- 1 root root 2.6M Nov 20 mydb.db
```

### 2. Configure environment
```bash
cd /home/mfadmin/new-vanna/vanna-engine

# Check/edit configuration
cat docker/env/.env.example | grep -A 10 "DATABASE CONFIGURATION"

# For development: Copy example to .env.dev
cp docker/env/.env.example docker/env/.env.dev
```

**Key settings to verify:**
```bash
# System Database (must be PostgreSQL for user data)
DB_TYPE=postgresql
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=vanna_db

# Golden Copy (automatic)
TARGET_DB_PATH=/app/data/vanna_db.db
```

### 3. Initialize project
```bash
python scripts/init_project.py
```

**Expected output:**
```
======================================================================
  1. GOLDEN COPY STRATEGY
======================================================================
Found Golden Copy source: /home/mfadmin/new-vanna/mydb.db
Copying database from source to runtime...
✓ Golden Copy created successfully
  Source:  /home/mfadmin/new-vanna/mydb.db (2,621,440 bytes)
  Runtime: /app/data/vanna_db.db (2,621,440 bytes)

======================================================================
  2. SYSTEM DATABASE INITIALIZATION
======================================================================
✓ System Database initialization completed

✓ INITIALIZATION COMPLETE
```

### 4. Start services
```bash
./run.sh  # Docker Compose with default .env.dev
```

### 5. Verify setup
```bash
# Health check
curl http://localhost:8000/health

# Login
curl -X POST http://localhost:8000/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"AdminPassword123"}'
```

## Database Architecture

### System Database (PostgreSQL)
Stores application data - **User authentication happens here**:
- Users (credentials, roles)
- Queries (query history)
- Feedback (user feedback on results)
- Audit logs (all actions)
- Configurations (app settings)
- Business Ontologies (data dictionary)

### Target Database (SQLite - /app/data/vanna_db.db)
Stores business data - **Read-only for analysis**:
- Read-only access via Golden Copy
- Used for data discovery & query generation
- Original mydb.db never modified

## Commands

### Check Golden Copy status
```bash
# View file sizes
ls -lh /home/mfadmin/new-vanna/mydb.db /app/data/vanna_db.db

# View copy details in logs
tail -f vanna-engine/logs/init_project.log | grep "Golden Copy"
```

### Re-initialize Golden Copy
```bash
# Force fresh copy (overwrites working copy)
cd /home/mfadmin/new-vanna/vanna-engine
python -c "
from scripts.lib.golden_copy import GoldenCopyManager
from pathlib import Path
gc = GoldenCopyManager(source_file=Path('../mydb.db'), runtime_dir=Path('/app/data'))
gc.copy_source_to_runtime(force=True)
"
```

### Check System Database
```bash
# PostgreSQL connection
docker-compose exec postgres psql -U postgres -d vanna_db

# List tables
\dt

# Check users
SELECT email, role, is_active FROM users;

# Exit
\q
```

### Test read-only access
```bash
# Try to open working copy (read-only mode)
sqlite3 /app/data/vanna_db.db ".tables"

# Try to insert (should fail)
sqlite3 /app/data/vanna_db.db "INSERT INTO orders VALUES(1, 'test');"
# Error: attempt to write a readonly database
```

## Troubleshooting

### Problem: "Golden Copy source not found"
**Fix:** Ensure mydb.db exists in project root
```bash
ls -lh /home/mfadmin/new-vanna/mydb.db
# If missing: copy it from backup or source system
```

### Problem: "User authentication fails"
**Check:** PostgreSQL is running and has users table
```bash
docker-compose ps postgres
docker-compose exec postgres psql -U postgres -d vanna_db -c "SELECT COUNT(*) FROM users;"
```

### Problem: "Cannot connect to Target Database"
**This is OK** - Target DB is optional. Set `ENABLE_TARGET_DB=false`

### Problem: "File size mismatch" after copy
**Fix:** Delete working copy and re-initialize
```bash
rm /app/data/vanna_db.db
python scripts/init_project.py
```

## Security Notes

✅ **Original mydb.db is protected**
- Never modified by application
- Can only be changed by manual operations
- Safe for production

✅ **User data in PostgreSQL**
- Proper authentication & authorization
- ACID transactions
- Backup/recovery support

✅ **Target DB is read-only**
- No accidental data modification
- All write operations go to System DB
- Audit trails for all queries

## What's Next?

- [Full Implementation Guide](./GOLDEN_COPY_IMPLEMENTATION.md)
- [Environment Configuration](./docker/env/.env.example)
- [Common Commands](../../AGENTS.md)
- [API Documentation](./docs/api.md)

## Environment Variables Quick Reference

```bash
# System Database (REQUIRED for user authentication)
DB_TYPE=postgresql
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=vanna_db

# Golden Copy (AUTOMATIC)
TARGET_DB_PATH=/app/data/vanna_db.db

# Optional: Target Database
ENABLE_TARGET_DB=false
TARGET_DATABASE_URL=

# Admin User (created on init)
INIT_ADMIN_USERNAME=admin@example.com
INIT_ADMIN_PASSWORD=AdminPassword123

# Demo Data (disable in production)
SEED_DEMO_DATA=true
```

---

**Last Updated:** 2025-11-20
**Status:** Production Ready
