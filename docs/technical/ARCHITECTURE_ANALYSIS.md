# Architecture Analysis: Current State vs. Desired State

**Date:** November 20, 2025
**Status:** Architecture Refinement Phase
**Focus:** Data Persistence and Separation of Concerns

---

## Executive Summary

The current system conflates **System Data** (Users, Auth, History) with **Target Analytical Data** (Business Transactions) in a single Postgres database. This violates the principle of separation of concerns and creates architectural friction for production deployments.

The refactoring establishes a **4-Component Data Architecture** where each component has a distinct responsibility and lifecycle.

---

## Current State Analysis

### What We Have Now

#### 1. Database Layer (docker-compose.yml)
```yaml
services:
  postgres:        # Single database for everything
    DATABASE_URL: vanna_db
  redis:          # Cache & message broker
  chroma:         # Vector store (declared but not integrated)
```

#### 2. Models (app/db/models.py)
**System Tables (Correct Location):**
- `users` - Authentication & RBAC
- `queries` - Query history
- `feedback` - Training loop data
- `audit_logs` - Compliance logging
- `configurations` - Runtime settings
- `business_ontologies` - Business term mappings

**Problem Table (Wrong Location):**
- `accounting_transactions` - Fake sample data seeded into System DB
  - Currently populated by `seed_sample_data()` in init scripts
  - This is **Target Data** but stored in **System DB**
  - Comment says "Common accounting transactions for demo/testing"

#### 3. Initialization Logic (init_project_enhanced.py)
**Current Flow:**
```
1. Check environment configuration
2. Verify database connectivity
3. Create all tables in single Postgres DB
4. Run Alembic migrations
5. Load ontology (from YAML)
6. Create admin user
7. Seed sample data (ACCOUNTING_TRANSACTIONS) ← PROBLEM
8. Validate schema
```

**Issues:**
- Mixes system initialization with test data loading
- No separation between system tables and target tables
- ChromaDB is available but not initialized/trained
- SQLite target database is not mentioned/handled
- No concept of read-only Target DB mounting

---

## Desired State: 4-Component Architecture

### Component 1: Postgres (System DB)
**Purpose:** Application infrastructure
**Location:** `postgresql://user:pass@postgres:5432/vanna_db`
**Tables:**
- Users & authentication
- Query history
- User feedback
- Audit logs
- Runtime configurations
- Business ontology mappings

**Initialization:** Single admin user + application schema
**Data Lifecycle:** Write-enabled, application-managed
**Persistence:** Docker volume `postgres_data`

### Component 2: SQLite (Target DB)
**Purpose:** Read-only business data for analysis
**Location:** Mounted volume (e.g., `/data/target.db` or similar)
**Tables:** Custom business schema (e.g., accounting, sales, HR data)
**Initialization:** Pre-existing file, mounted as read-only
**Data Lifecycle:** External, immutable within container
**Persistence:** External host volume

**Key Difference:** This is the data **to be analyzed**, not system data.

### Component 3: ChromaDB (Vector Store)
**Purpose:** Embeddings & semantic indexing
**Location:** `http://chroma:8000` (already in docker-compose)
**Collections:**
- `table_schemas` - DDL from Target DB
- `sample_queries` - Example questions and answers
- `business_terms` - Semantic understanding of business concepts

**Initialization:**
1. Connect to Target DB (SQLite)
2. Extract schema (DDL)
3. Generate embeddings for tables/columns/business meanings
4. Train ChromaDB with this schema context

**Data Lifecycle:** Derived from Target DB, updated when Target schema changes

### Component 4: Redis (Cache)
**Purpose:** Session cache, semantic cache, message broker
**Initialization:** No special setup needed (just ensure connectivity)

---

## Technical Blockers & Solutions

### Blocker 1: AccountingTransaction in System DB
**Current Problem:**
```python
# In app/db/models.py
class AccountingTransaction(Base):
    __tablename__ = "accounting_transactions"
    # ... defined in System DB
```

**Root Cause:** Target data is defined as ORM model in System DB

**Solution Options:**

**Option A (Recommended):** Move accounting_transactions entirely
- Remove from System DB models
- Create read-only accessor in Target DB
- Update app code to query Target DB for analytical data

**Option B:** Keep accounting_transactions but make it optional
- Only create/seed if Target DB unavailable
- Add config flag: `SEED_DEMO_DATA: false` (default)
- Useful for development but properly scoped

**Option C (Current):** Keep as-is but mark as demo-only
- Document that it's for testing only
- Don't seed in production
- Add migration to remove in production environments

**Recommendation:** Option A for production, Option B for dev flexibility

---

### Blocker 2: No Target DB Connection in Application
**Current Problem:**
- `app/config.py` only has `DATABASE_URL` (Postgres)
- No mention of Target DB connection

**Solution:**
- Add `TARGET_DATABASE_URL` to config (e.g., `sqlite:///data/target.db`)
- Create separate connection pool/session for Target DB
- Implement `TargetDB` context manager
- Add feature flag: `ENABLE_TARGET_DB: true/false`

**Implementation:**
```python
# app/config.py additions
TARGET_DATABASE_URL: Optional[str] = None
SEED_DEMO_DATA: bool = True  # Only seed if no Target DB

# app/db/target_db.py (new)
class TargetDatabaseClient:
    def __init__(self, target_db_url: str):
        self.engine = create_engine(target_db_url)

    def get_schema_ddl(self) -> str:
        """Extract DDL from Target DB"""
```

---

### Blocker 3: ChromaDB Not Integrated
**Current Problem:**
- ChromaDB service running but never initialized
- No training/indexing logic

**Solution:**
- Create `chroma_client.py` in `app/services/`
- Implement schema extraction and embedding generation
- Add training pipeline to initialization

**Dependencies Check:**
```bash
# In requirements.txt, verify:
chromadb>=0.3.21    # Should be present
```

---

## Proposed Implementation Plan

### Phase 1: Configuration & Dependencies
1. Update `app/config.py` with Target DB configuration
2. Verify `chromadb` is in `requirements.txt`
3. Verify `redis` client is in `requirements.txt`

### Phase 2: New Initialization Script
Create `scripts/init_system_db.py`:
```python
class SystemDBInitializer:
    def __init__(self, config):
        self.config = config

    def initialize(self):
        # 1. Initialize Postgres (System DB)
        self.setup_system_database()

        # 2. Create admin user
        self.create_default_admin()

        # 3. Setup ChromaDB (if Target DB available)
        if self.config.TARGET_DATABASE_URL:
            self.train_chroma_db()

        # 4. Verify Redis connectivity
        self.verify_redis()
```

### Phase 3: Refactor db_init.sh
Update orchestration to call new script:
```bash
./db_init.sh
  └─ Calls: docker exec api python scripts/init_system_db.py
```

### Phase 4: Documentation
- Update README with 4-component architecture
- Add volume mounting instructions for Target DB
- Clarify data flow and responsibilities

---

## Recommended Environment Variables

```env
# System Database (PostgreSQL)
DATABASE_URL=postgresql://postgres:password@postgres:5432/vanna_db
POSTGRES_PASSWORD=secure_password

# Target Database (SQLite - read-only)
TARGET_DATABASE_URL=sqlite:////data/target.db
# Note: Mounted as read-only volume in docker-compose

# Feature Flags
SEED_DEMO_DATA=false              # In production, must be false
ENABLE_TARGET_DB=true             # Expect Target DB to exist

# ChromaDB
CHROMA_HOST=chroma
CHROMA_PORT=8000
AUTO_TRAIN_CHROMA=true            # Auto-train on startup

# Redis
REDIS_URL=redis://:password@redis:6379/0
REDIS_PASSWORD=secure_password
```

---

## Docker Compose Updates Required

### Add Target DB Volume Mount
```yaml
services:
  api:
    volumes:
      - /host/path/to/target.db:/data/target.db:ro  # Read-only
```

### Update Environment Variables
```yaml
services:
  api:
    environment:
      TARGET_DATABASE_URL: ${TARGET_DATABASE_URL}
      SEED_DEMO_DATA: ${SEED_DEMO_DATA:-false}
      ENABLE_TARGET_DB: ${ENABLE_TARGET_DB:-true}
```

---

## Data Flow Diagram

```
                    User Request
                         │
                         ▼
                    ┌─────────────┐
                    │   FastAPI   │
                    │ Application │
                    └────┬─────┬──┘
                         │     │
              ┌──────────┘     └──────────┐
              │                           │
              ▼                           ▼
        ┌──────────────┐          ┌──────────────┐
        │  System DB   │          │  Target DB   │
        │ (PostgreSQL) │          │  (SQLite)    │
        ├──────────────┤          ├──────────────┤
        │ Users        │          │ Accounting   │
        │ Queries      │          │ Sales        │
        │ Feedback     │          │ HR Data      │
        │ Audit Logs   │          │ [Custom]     │
        │ Ontologies   │          │ (Read-only)  │
        └──────────────┘          └──────┬───────┘
                │                        │
                ├────────────────┬───────┘
                │                │
                ▼                ▼
           ┌──────────┐    ┌──────────────┐
           │  Redis   │    │  ChromaDB    │
           ├──────────┤    ├──────────────┤
           │ Cache    │    │ Embeddings   │
           │ Sessions │    │ Schema Index │
           │ Celery   │    │ Semantic Vec │
           └──────────┘    └──────────────┘
```

---

## Migration Path

### For Existing Deployments

1. **If accounting_transactions used in production:**
   - Export data to external SQLite (as Target DB)
   - Update queries to read from Target DB
   - Remove accounting_transactions from System DB
   - Run migrations

2. **If development/demo only:**
   - Simply set `SEED_DEMO_DATA=false`
   - Keep accounting_transactions table but don't populate
   - Add Target DB mount when ready

3. **For new deployments:**
   - Start with no accounting_transactions seeding
   - Mount Target DB with business data
   - Initialize ChromaDB from Target schema

---

## Verification Checklist

- [ ] Current `init_project_enhanced.py` seeds accounting_transactions (PROBLEM IDENTIFIED)
- [ ] `docker-compose.yml` has Postgres, Redis, ChromaDB (CONFIRMED)
- [ ] ChromaDB is NOT initialized with Target DB schema (PROBLEM IDENTIFIED)
- [ ] `app/config.py` has no TARGET_DATABASE_URL (PROBLEM IDENTIFIED)
- [ ] `chromadb` package in requirements.txt (TO CHECK)
- [ ] No read-only volume mount for Target DB (PROBLEM IDENTIFIED)

---

## Next Steps

1. Review this analysis with team
2. Decide on blocker handling (Options A/B/C above)
3. Implement refactored `init_system_db.py`
4. Update `db_init.sh` to call new script
5. Update `docker-compose.yml` for volume mounts
6. Create comprehensive integration guide

---

**Technical Lead Recommendation:**
Implement **Option A** (move accounting_transactions) for architectural cleanness, with **Option B features** (keep table but optional seeding) for backward compatibility during migration.
