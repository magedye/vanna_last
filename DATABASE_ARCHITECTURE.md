# Database Architecture - System vs Target

## Quick Reference

| Aspect | System Database (PostgreSQL) | Target Database (SQLite) |
|--------|------------------------------|--------------------------|
| **Purpose** | Application & User Data | Business Data Analysis |
| **Storage** | Live PostgreSQL Instance | mydb.db (protected copy) |
| **Access** | Read/Write | Read-Only |
| **Users** | Stored here | Not stored here |
| **Queries** | History stored here | Executed against this |
| **Authentication** | ✅ Happens here | ❌ Never here |
| **Audit Logs** | ✅ Stored here | Not applicable |
| **Backup** | Regular snapshots | Golden Copy protection |
| **Multi-user** | ✅ Supported | ⚠️ Analytical only |

---

## System Database (PostgreSQL)

### Location
```
PostgreSQL Container
  └─ Database: vanna_db
     └─ User: postgres
```

### Environment Variables
```bash
DB_TYPE=postgresql
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<your_password>
POSTGRES_DB=vanna_db
```

### Tables
```
vanna_db/
├─ users
│  ├─ id (PK)
│  ├─ email (UNIQUE)
│  ├─ password_hash (ENCRYPTED)
│  ├─ full_name
│  ├─ role (admin, analyst, viewer)
│  ├─ is_active
│  └─ created_at, updated_at
│
├─ queries
│  ├─ id (PK)
│  ├─ user_id (FK → users)
│  ├─ sql (TEXT)
│  ├─ status (pending, success, error)
│  ├─ result_count
│  └─ created_at, executed_at
│
├─ feedback
│  ├─ id (PK)
│  ├─ query_id (FK → queries)
│  ├─ user_id (FK → users)
│  ├─ rating (1-5)
│  ├─ comment (TEXT)
│  └─ created_at
│
├─ audit_logs
│  ├─ id (PK)
│  ├─ user_id (FK → users)
│  ├─ action (login, query, logout, etc.)
│  ├─ resource (table, query, user)
│  ├─ changes (JSONB)
│  └─ timestamp
│
├─ configurations
│  ├─ id (PK)
│  ├─ key (UNIQUE)
│  ├─ value (TEXT)
│  ├─ description
│  └─ updated_at
│
└─ business_ontologies
   ├─ id (PK)
   ├─ term_name
   ├─ description
   ├─ synonyms (ARRAY)
   ├─ data_source
   └─ owner
```

### What Happens Here
✅ User login and authentication
✅ Session management
✅ Password verification
✅ Query history tracking
✅ Feedback collection
✅ Audit trail of all actions
✅ Business ontology management
✅ System configuration storage

### Data Protection
✅ ACID transactions
✅ Encryption of sensitive fields
✅ Transaction rollback on error
✅ Backup and recovery support
✅ Role-based access control

### Example Operations
```sql
-- User Login (checks here)
SELECT password_hash FROM users WHERE email = 'user@example.com';

-- Query History (logs here)
INSERT INTO queries (user_id, sql, status) VALUES (1, 'SELECT...', 'success');

-- Audit Trail (records here)
INSERT INTO audit_logs (user_id, action, timestamp) VALUES (1, 'login', NOW());

-- User Lookup (for session)
SELECT id, role, is_active FROM users WHERE id = 1;
```

---

## Target Database (SQLite)

### Location
```
Original: /home/mfadmin/new-vanna/mydb.db (PROTECTED)
Working Copy: /app/data/vanna_db.db (READ-ONLY)
```

### Configuration
```bash
ENABLE_TARGET_DB=false              # Set to true to enable
TARGET_DATABASE_URL=                # Connection URL
TARGET_DB_PATH=/app/data/vanna_db.db   # Working copy location
```

### Access Mode
```python
# Read-only SQLite mode
sqlite:////app/data/vanna_db.db?mode=ro
```

### Data Contents
- Business tables (orders, customers, products, etc.)
- Historical transactions
- Analytical reference data
- Any existing business data

### What Happens Here
✅ Read-only data discovery
✅ Schema inspection
✅ Query result generation
✅ Data analysis & exploration
❌ No user data storage
❌ No authentication
❌ No modifications allowed
❌ No session management

### Data Protection
✅ Original mydb.db never modified
✅ Read-only access enforced
✅ Working copy created at startup
✅ File integrity verified
✅ Can restore from original anytime

### Golden Copy Strategy
```
mydb.db (Original)
  │
  ├─ Never modified ✓
  ├─ Protected backup ✓
  │
  └─ Copy on startup
      │
      └─ /app/data/vanna_db.db (Working Copy)
         │
         ├─ Read-only mode ✓
         ├─ Application accesses ✓
         └─ Original always safe ✓
```

### Example Operations
```sql
-- Data discovery (read-only)
SELECT * FROM sqlite_master;

-- Query analysis (read-only)
SELECT COUNT(*) FROM orders WHERE date >= '2025-01-01';

-- Schema inspection (read-only)
PRAGMA table_info(customers);

-- All writes REJECTED
INSERT INTO orders VALUES(...);
-- Error: attempt to write a readonly database
```

---

## Data Flow Diagram

### Authentication Flow
```
User Login Request
    ↓
FastAPI Endpoint
    ↓
Query PostgreSQL System Database
    │
    ├─ Check users table
    ├─ Verify password_hash
    ├─ Create session token
    └─ Log audit entry
        ↓
PostgreSQL (System DB)
    │
    ├─ Update last_login
    ├─ Store audit_log
    └─ Record in Redis cache
        ↓
Return JWT Token
    ↓
User Authenticated ✓
```

### Query Execution Flow
```
User Submits Natural Language Query
    ↓
FastAPI Endpoint
    ↓
Extract from Authenticated Session
    │
    ├─ Verify user permission
    ├─ Check user role
    └─ Get user_id
        ↓
Generate SQL (via Vanna/LLM)
    │
    ├─ Inspect Target DB schema
    │  └─ Query SQLite (read-only)
    │
    └─ Create SQL query
        ↓
Execute Query
    │
    ├─ Run against SQLite (read-only)
    └─ Collect results
        ↓
Log Query Execution
    │
    └─ Store in PostgreSQL
        ├─ queries table
        ├─ audit_logs table
        └─ update user.last_query_at
        ↓
Return Results to User
    ↓
User Sees Results ✓
```

### Audit Trail Flow
```
Every User Action
    ↓
log_to_audit_trail(action, resource, changes)
    ↓
PostgreSQL audit_logs Table
    │
    ├─ Timestamp
    ├─ User ID
    ├─ Action type
    ├─ Resource type
    └─ Changes (JSONB)
        ↓
Examples:
├─ login@2025-11-20T10:30:00Z | User 1 | login
├─ query@2025-11-20T10:31:15Z | User 1 | SELECT...
├─ feedback@2025-11-20T10:31:45Z | User 1 | rating=4
└─ logout@2025-11-20T10:35:00Z | User 1 | logout
```

---

## Key Rules

### System Database (PostgreSQL)
```
✅ Writes allowed
✅ User data stored here
✅ ACID transactions required
✅ Backup regularly
✅ Multiple writers supported
✅ Encryption recommended
```

### Target Database (SQLite)
```
❌ No writes allowed
❌ No user data here
❌ Read-only mode enforced
❌ Protected by Golden Copy
❌ Analytical use only
❌ Single source of truth (original mydb.db)
```

---

## Configuration Examples

### Development Setup
```bash
# System Database
DB_TYPE=postgresql
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=development_password
POSTGRES_DB=vanna_db

# Target Database (optional)
ENABLE_TARGET_DB=false
TARGET_DATABASE_URL=
TARGET_DB_PATH=/app/data/vanna_db.db
```

### Staging Setup
```bash
# System Database
DB_TYPE=postgresql
POSTGRES_HOST=postgres.staging.internal
POSTGRES_PORT=5432
POSTGRES_USER=vanna_user
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}  # From secrets
POSTGRES_DB=vanna_staging

# Target Database (enabled)
ENABLE_TARGET_DB=true
TARGET_DATABASE_URL=sqlite:////data/analytics.db
TARGET_DB_PATH=/app/data/vanna_db.db
```

### Production Setup
```bash
# System Database
DB_TYPE=postgresql
POSTGRES_HOST=postgres.prod.internal
POSTGRES_PORT=5432
POSTGRES_USER=vanna_prod
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}  # From AWS Secrets Manager
POSTGRES_DB=vanna_prod

# Target Database (enabled with backup)
ENABLE_TARGET_DB=true
TARGET_DATABASE_URL=sqlite:////mnt/data/analytics.db
TARGET_DB_PATH=/app/data/vanna_db.db

# Initialization
SEED_DEMO_DATA=false  # No test data in prod
BACKUP_DIR=/backups/vanna
BACKUP_RETENTION_COUNT=30
```

---

## Separation of Concerns

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                        │
│                    (FastAPI Endpoints)                      │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
        ↓                                 ↓
┌──────────────────────┐        ┌─────────────────────┐
│  System Database     │        │ Target Database     │
│  (PostgreSQL)        │        │ (SQLite)            │
├──────────────────────┤        ├─────────────────────┤
│ Purpose: App & User  │        │ Purpose: Analytics  │
│ Read/Write: YES      │        │ Read/Write: NO      │
│ Users: YES ✓         │        │ Users: NO ✗         │
│ Auth: YES ✓          │        │ Auth: NO ✗          │
│ Queries: History     │        │ Queries: Against    │
│ Transactions: ACID   │        │ Transactions: None  │
└──────────────────────┘        └─────────────────────┘
        │                                 │
        └────────────────┬────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
        ↓                                 ↓
   PostgreSQL Container             mydb.db Working Copy
   (Running Instance)               (Read-Only SQLite)
```

---

## User Authentication - System Database ONLY

```
✅ User Registration
   └─ PostgreSQL users table
   └─ Password hashed with bcrypt
   └─ Role assigned

✅ User Login
   └─ Query PostgreSQL users table
   └─ Verify password hash
   └─ Create session/JWT
   └─ Log audit entry

✅ Session Management
   └─ JWT tokens (in memory)
   └─ Redis cache (optional)
   └─ NOT stored in Target DB

✅ Access Control
   └─ Role check in PostgreSQL
   └─ Permission validation
   └─ Audit logged

✅ Password Reset
   └─ Hash new password
   └─ Update PostgreSQL
   └─ Audit log created

❌ NEVER in Target Database (SQLite)
   └─ No passwords
   └─ No sessions
   └─ No user records
   └─ No authentication
```

---

## Data Protection Strategy

### Original File (mydb.db)
```
Location: /home/mfadmin/new-vanna/mydb.db (PROTECTED)
Status: Read-only
Backup: Version control
Restore: Can restore anytime from original
Modification: Manual process only (not by app)
Size: 2.6 MB
```

### Working Copy (vanna_db.db)
```
Location: /app/data/vanna_db.db (RUNTIME)
Status: Read-only
Created: At startup from mydb.db
Lifetime: Ephemeral (can be recreated)
Modification: Never by application
Verification: File size checked after copy
```

### System Database (PostgreSQL)
```
Location: PostgreSQL instance
Status: Read/Write for app
Backup: Regular snapshots
Recovery: From backups
Encryption: At rest (recommended)
```

---

## See Also

- [Golden Copy Implementation Guide](./vanna-engine/GOLDEN_COPY_IMPLEMENTATION.md)
- [Quick Start Guide](./vanna-engine/GOLDEN_COPY_QUICK_START.md)
- [Environment Configuration](./vanna-engine/docker/env/.env.example)
- [Common Commands](./AGENTS.md)

---

**Last Updated:** 2025-11-20  
**Architecture Version:** 1.0  
**Status:** Production Ready ✅
