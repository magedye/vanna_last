# Final Architecture Phase - Implementation Plan

**Date:** November 20, 2025  
**Status:** In Progress  
**Scope:** Script Orchestration, Golden Copy Strategy, Admin Management APIs

---

## Phase 1: Script Orchestration Refactoring

### Current State
- `scripts/init_project_enhanced.py` - Full initialization (deprecated, mixed concerns)
- `scripts/init_system_db.py` - System specialist (Postgres only)
- `db_init.sh` - Shell trigger

### Target State
- `scripts/init_project.py` - Main orchestrator (renamed from enhanced)
- `scripts/init_system_db.py` - System specialist (unchanged)
- `db_init.sh` - Trigger with enhanced health checks
- `scripts/lib/golden_copy.py` - Golden Copy strategy implementation
- `scripts/lib/chroma_manager.py` - ChromaDB training & management

### Implementation Steps
1. Rename `init_project_enhanced.py` → `init_project.py` (main orchestrator)
2. Create `scripts/lib/golden_copy.py` for Target DB management
3. Create `scripts/lib/chroma_manager.py` for ChromaDB operations
4. Update `init_project.py` to orchestrate properly
5. Update `db_init.sh` to call the orchestrator
6. Update `app/config.py` with proper environment variables

---

## Phase 2: Golden Copy Strategy

### Current Target DB Location
- File: `vanna_db.db` (in project root)
- Issue: Exposed, subject to accidental modification

### New Strategy
- **Source Location:** `assets/databases/vanna_db.db` (protected)
- **Runtime Location:** `/app/data/vanna_db.db` (mounted volume in container)
- **Environment Variable:** `TARGET_DB_PATH` (configured in .env)
- **Copy Logic:** On init, copy from source to runtime location
- **Read-Only Connection:** System connects to runtime copy only

### Benefits
✅ Original file protected  
✅ Runtime isolation  
✅ Easy to restore/reset  
✅ Backup-ready structure  
✅ Versioning-friendly  

---

## Phase 3: Docker Compose Enhancements

### Volume Structure
```yaml
volumes:
  postgres_data:        # System DB (persistent)
  redis_data:           # Cache (persistent)
  chroma_data:          # Vector DB (persistent)
  target_db_data:       # Target DB mount point (NEW)
```

### Service Updates
- **api:** Add mount for `/app/data` (Target DB location)
- **postgres:** Already configured
- **redis:** Already configured
- **chroma:** Already configured

---

## Phase 4: Admin APIs (app/api/v1/routes/db_admin.py)

### Endpoints

#### ChromaDB Management
- `POST /api/v1/admin/db/chroma/train` - Train from Target DB
- `GET /api/v1/admin/db/chroma/status` - Training status
- `GET /api/v1/admin/db/chroma/knowledge-base` - Inspect vectors
- `DELETE /api/v1/admin/db/chroma/clear` - Clear (with confirmation)

#### System DB Maintenance
- `GET /api/v1/admin/db/health` - Connection pool status
- `GET /api/v1/admin/db/stats` - Table statistics
- `POST /api/v1/admin/db/vacuum` - Optimize (Postgres VACUUM)

#### Backup & Recovery
- `POST /api/v1/admin/db/backup` - Trigger backup (async task)
- `GET /api/v1/admin/db/backup/status` - Backup status
- `GET /api/v1/admin/db/backup/list` - List available backups
- `POST /api/v1/admin/db/restore/{backup_id}` - Restore from backup

### RBAC
- Require `role == "admin"` or superuser flag
- Optional confirmation flag for destructive operations
- Audit logging for all operations

---

## Phase 5: Backup Strategy

### Scope
✅ PostgreSQL (System DB)  
✅ ChromaDB (Vectors)  
✅ vanna_db.db (Target DB)  
✗ Redis (ephemeral cache, excluded)

### Implementation
- **Trigger:** API endpoint → Background Celery task
- **Location:** `backups/` directory (docker volume)
- **Naming:** `backup_YYYY-MM-DD_HH:MM:SS.tar.gz`
- **Retention:** Keep last 7 backups (configurable)
- **Compression:** gzip format
- **Validation:** Verify backup integrity on restore

### Script: `scripts/lib/backup_manager.py`
- `backup_all()` - Full backup
- `restore_all(backup_id)` - Full restore
- `list_backups()` - List available backups
- `verify_backup(backup_id)` - Validate integrity

---

## Files to Create/Modify

### CREATE
1. `scripts/lib/golden_copy.py` - Golden Copy management
2. `scripts/lib/chroma_manager.py` - ChromaDB operations
3. `scripts/lib/backup_manager.py` - Backup & restore
4. `app/api/v1/routes/db_admin.py` - Admin endpoints
5. `app/services/db_management.py` - Business logic
6. `assets/databases/.gitkeep` - Protect directory
7. `backups/.gitkeep` - Backup directory

### RENAME
- `scripts/init_project_enhanced.py` → `scripts/init_project.py`

### MODIFY
1. `scripts/init_project.py` (orchestrator)
2. `scripts/init_system_db.py` (add Golden Copy calls)
3. `db_init.sh` (call new orchestrator)
4. `docker-compose.yml` (add volume mounts)
5. `app/config.py` (add TARGET_DB_PATH, BACKUP_DIR)
6. `app/main.py` (include db_admin router)
7. `.env.example` (new variables)
8. `.gitignore` (protect vanna_db.db source)

---

## Environment Variables (New)

```env
# Golden Copy Strategy
TARGET_DB_PATH=/app/data/vanna_db.db
TARGET_DB_SOURCE=assets/databases/vanna_db.db

# Backup Configuration
BACKUP_DIR=backups
BACKUP_RETENTION_COUNT=7

# ChromaDB Training
AUTO_TRAIN_CHROMA_ON_INIT=true
CHROMA_BATCH_SIZE=100
```

---

## Testing Strategy

### Unit Tests
- `test_golden_copy.py` - Copy logic
- `test_chroma_manager.py` - ChromaDB training
- `test_backup_manager.py` - Backup/restore

### Integration Tests
- Full init with Golden Copy
- ChromaDB training from Target DB
- Backup creation and restore
- Admin API endpoints with RBAC

### Manual Testing
1. `./run.sh` → start services
2. `./db_init.sh` → initialize
3. Verify vanna_db.db at `/app/data/vanna_db.db`
4. Test admin endpoints with curl

---

## Timeline

| Phase | Task | Estimated |
|-------|------|-----------|
| 1 | Script orchestration refactoring | 30 min |
| 2 | Golden Copy implementation | 30 min |
| 3 | Docker Compose updates | 15 min |
| 4 | Admin API endpoints | 45 min |
| 5 | Backup system | 45 min |
| - | **Total** | **2.5 hours** |

---

## Validation Checklist

- [ ] All scripts compile without errors
- [ ] Golden Copy strategy works (file copied correctly)
- [ ] Docker Compose volumes properly configured
- [ ] Admin endpoints accessible with proper auth
- [ ] ChromaDB training endpoint functional
- [ ] Backup creation and restore working
- [ ] RBAC enforced on admin endpoints
- [ ] Audit logging for admin operations
- [ ] Backward compatibility maintained
- [ ] Documentation updated

---

## Success Criteria

✅ **Separation of Concerns:** Scripts have distinct, focused roles  
✅ **Data Safety:** Golden Copy protects original vanna_db.db  
✅ **Scalability:** Admin APIs enable operational management  
✅ **Observability:** Audit logging tracks all admin operations  
✅ **Reliability:** Backup/restore enables disaster recovery  
✅ **Production Ready:** All components properly documented  

---

Next: Begin Phase 1 implementation
