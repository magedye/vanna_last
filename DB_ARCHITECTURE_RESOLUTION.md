# Database Architecture Conflict Resolution

**Date:** November 20, 2025  
**Status:** Conflicts Resolved  
**Version:** 1.0

## Overview

This document summarizes the database architecture conflicts that were identified and resolved in the Vanna Insight Engine. The system has been refactored to enforce a strict 4-component architecture separating System Database from Target Business Data.

---

## Conflicts Identified

### Conflict 1: AccountingTransaction in System DB

**Issue:**  
The `AccountingTransaction` model was defined in `app/db/models.py` alongside system tables (Users, Queries, Feedback, etc.), violating the principle of separation of concerns. This business data model was being seeded into the System Database (PostgreSQL), which should only contain application infrastructure.

**Root Cause:**  
Early development mixed all table definitions together. Demo/testing data was treated as system infrastructure rather than target analytical data.

**Resolution:**
1. ✅ Marked `AccountingTransaction` as **DEPRECATED** with clear documentation
2. ✅ Added comments explaining it belongs in Target DB, not System DB
3. ✅ Created `SEED_DEMO_DATA` feature flag to control seeding
4. ✅ Updated `init_system_db.py` to conditionally seed based on flag
5. ✅ Warns users when `SEED_DEMO_DATA=false` (production default)

**Files Changed:**
- `app/db/models.py` - Added deprecation notice
- `scripts/init_system_db.py` - Added `seed_demo_data_optional()` method

---

### Conflict 2: Script Confusion (init_project_enhanced.py vs init_system_db.py)

**Issue:**  
Two initialization scripts existed:
- `init_project_enhanced.py` - Mixes system DB setup with demo data seeding
- `init_system_db.py` - New script properly separates concerns

This created confusion about which script to use and conflicted with the 4-component architecture.

**Root Cause:**  
`init_project_enhanced.py` was the original enhanced version. `init_system_db.py` was added during refactoring but both coexist.

**Resolution:**
1. ✅ Marked `init_project_enhanced.py` as **DEPRECATED**
2. ✅ Added clear deprecation warnings in docstring
3. ✅ Added runtime warnings when the script runs
4. ✅ Documented which script to use for which scenario
5. ✅ Updated `db_init.sh` to call `init_system_db.py`

**Files Changed:**
- `scripts/init_project_enhanced.py` - Added deprecation notice and warnings
- `db_init.sh` - Updated to call `init_system_db.py`

---

### Conflict 3: Inconsistent Feature Flag Defaults

**Issue:**  
Feature flags (`SEED_DEMO_DATA`, `ENABLE_TARGET_DB`, `AUTO_TRAIN_CHROMA`) lacked clear documentation about:
- Default values for each environment
- Interaction between flags
- Production-safe defaults

This created risk of accidentally seeding demo data to production.

**Root Cause:**  
Feature flags were added quickly without comprehensive documentation of their implications.

**Resolution:**
1. ✅ Added detailed comments in `app/config.py` for each flag
2. ✅ Documented development vs production defaults
3. ✅ Explained dependencies between flags
4. ✅ Created examples for each deployment scenario

**Files Changed:**
- `app/config.py` - Enhanced feature flag documentation

---

### Conflict 4: Missing Semantic Separation in init_system_db.py

**Issue:**  
`init_system_db.py` created all tables from `Base.metadata` without distinguishing system tables from demo tables in its output.

**Root Cause:**  
The initialization logic didn't explicitly list expected system tables vs. demo tables.

**Resolution:**
1. ✅ Updated `create_system_tables()` to distinguish table types
2. ✅ Lists expected system tables: users, queries, feedback, audit_logs, configurations, business_ontologies
3. ✅ Warns if demo tables exist but `SEED_DEMO_DATA=false`
4. ✅ Provides clear guidance to users

**Files Changed:**
- `scripts/init_system_db.py` - Enhanced table reporting in `create_system_tables()`

---

## Architecture Enforcement

### System Database (PostgreSQL) - ONLY these tables:

```
✅ users
✅ queries
✅ feedback
✅ audit_logs
✅ configurations
✅ business_ontologies
```

### Target Database (SQLite) - Contains:

```
accounting_transactions (example)
sales_data
customer_data
inventory
[Any custom analytical data]
```

### Feature Flags Control:

| Flag | Purpose | Dev Default | Prod Default | Notes |
|------|---------|-------------|--------------|-------|
| `SEED_DEMO_DATA` | Seed demo transactions | `true` | `false` | **MUST** be false in production |
| `ENABLE_TARGET_DB` | Expect Target DB mounted | `false` | `true` | When true, requires TARGET_DATABASE_URL |
| `AUTO_TRAIN_CHROMA` | Auto-train from schema | `false` | `true` | Only works if ENABLE_TARGET_DB=true |

---

## Updated Initialization Flow

### Development (docker-compose)

```bash
# Step 1: Start services
./run.sh

# Step 2: Initialize System DB only
docker exec api python scripts/init_system_db.py
# This:
#   ✓ Creates System DB tables
#   ✓ Seeds demo data (SEED_DEMO_DATA=true by default)
#   ✓ Creates admin user
#   ✓ Verifies Redis
#   ✓ (Skips ChromaDB if ENABLE_TARGET_DB=false)
```

### Production (Kubernetes)

```bash
# .env.prod settings:
SEED_DEMO_DATA=false           # No demo data
ENABLE_TARGET_DB=true          # External DB mounted
AUTO_TRAIN_CHROMA=true         # Auto-index for semantic search
TARGET_DATABASE_URL=...        # External SQLite or PostgreSQL

# Initialize
./db_init.sh
# This:
#   ✓ Creates System DB tables only (no demo data)
#   ✓ Connects to Target DB (read-only)
#   ✓ Trains ChromaDB from Target schema
#   ✓ Creates admin user
#   ✓ Verifies Redis connectivity
```

---

## Files Modified Summary

| File | Change | Reason |
|------|--------|--------|
| `app/db/models.py` | Added deprecation notice to AccountingTransaction | Document that it's business data, not system |
| `app/config.py` | Enhanced feature flag documentation | Clarify defaults and interactions |
| `scripts/init_system_db.py` | Added seed_demo_data_optional() step | Conditional demo data seeding |
| `scripts/init_system_db.py` | Enhanced table categorization | Distinguish system vs demo tables |
| `scripts/init_project_enhanced.py` | Added deprecation warnings | Guide users to new script |
| `db_init.sh` | (Already updated in previous work) | Call new init_system_db.py |

---

## Production Deployment Checklist

- [ ] Set `SEED_DEMO_DATA=false` in production .env
- [ ] Set `ENABLE_TARGET_DB=true` if using Target DB
- [ ] Configure `TARGET_DATABASE_URL` for Target DB
- [ ] Set `AUTO_TRAIN_CHROMA=true` if using ChromaDB
- [ ] Run `./db_init.sh` after starting containers
- [ ] Verify: `curl http://localhost:8000/health`
- [ ] Check: no demo data in system DB with `SELECT COUNT(*) FROM accounting_transactions;`

---

## Testing DB Separation

### Verify System Tables Only

```sql
-- Connect to System DB (PostgreSQL)
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Expected output:
-- users
-- queries
-- feedback
-- audit_logs
-- configurations
-- business_ontologies
-- (accounting_transactions ONLY if SEED_DEMO_DATA=true)
```

### Verify Target DB (SQLite)

```bash
# If Target DB mounted at /data/target.db
sqlite3 /data/target.db ".tables"
# Should show business data tables, NOT system tables
```

---

## Backward Compatibility

- ✅ `AccountingTransaction` model still exists for development
- ✅ `init_project_enhanced.py` still works (with deprecation warning)
- ✅ Default behavior unchanged (SEED_DEMO_DATA=true for dev)
- ✅ All feature flags are optional with sensible defaults

---

## Next Steps

1. **Document in AGENTS.md:** Add examples of production vs dev deployment
2. **Example env files:** Create .env.dev, .env.prod with correct defaults
3. **Docker Compose:** Add example Target DB volume mount
4. **Migration Guide:** For existing deployments upgrading to new architecture

---

## Related Documents

- `SYSTEM_DB_ARCHITECTURE.md` - System DB design
- `IMPLEMENTATION_SUMMARY.md` - Implementation details
- `ARCHITECTURE_ANALYSIS.md` - Original analysis
- `AGENTS.md` - Command reference
