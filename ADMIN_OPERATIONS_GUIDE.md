# Admin Operations Guide

Quick reference for database administration tasks.

---

## Health & Status

### Check Database Health
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/admin/db/health
```

**Response**:
```json
{
  "status": "healthy",
  "database": "PostgreSQL",
  "version": "PostgreSQL 16.0...",
  "connection_pool": {
    "size": 20,
    "overflow": 10,
    "checked_in": 18,
    "checked_out": 2
  }
}
```

### Get Database Statistics
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/admin/db/stats
```

---

## Backup Operations

### Create Full Backup
```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/admin/db/backup
```

**Response**: Returns task_id for polling
```json
{
  "status": "queued",
  "task_id": "a1b2c3d4-e5f6...",
  "message": "Backup operation scheduled",
  "status_url": "/api/v1/admin/db/backup/status/a1b2c3d4-e5f6..."
}
```

### Check Backup Status
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/admin/db/backup/status/a1b2c3d4-e5f6...
```

### List Available Backups
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/admin/db/backup/list
```

**Response**:
```json
{
  "total_backups": 5,
  "backups": [
    {
      "filename": "backup_2025-11-20_14-30-45.tar.gz",
      "size_bytes": 52428800,
      "size_mb": 50.0,
      "created": 1700492445
    },
    ...
  ]
}
```

### Restore from Backup
```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/admin/db/backup/restore/backup_2025-11-20_14-30-45.tar.gz?confirm=true"
```

⚠️ **WARNING**: Restore is destructive and will overwrite current data.

---

## ChromaDB Operations

### Train ChromaDB from Target Schema
```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/admin/db/chroma/train
```

Returns task_id for polling like backup operations.

**Prerequisites**:
- TARGET_DATABASE_URL configured
- ENABLE_TARGET_DB=true

### Check ChromaDB Training Status
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/admin/db/chroma/status/task-id-here
```

### Inspect ChromaDB Knowledge Base
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/admin/db/chroma/knowledge-base
```

**Response**:
```json
{
  "total_collections": 2,
  "collections": [
    {
      "name": "target_schema",
      "count": 1,
      "metadata": {
        "type": "database_schema",
        "source": "sqlite:////data/vanna_db.db"
      }
    }
  ]
}
```

### Clear ChromaDB Collection
```bash
curl -X DELETE -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/admin/db/chroma/clear?collection_name=target_schema&confirm=true"
```

⚠️ **WARNING**: This clears all documents from the collection and cannot be undone without restore.

---

## Feature Flags (Environment Variables)

### Development Mode
```env
SEED_DEMO_DATA=true              # Seed 50 demo transactions
ENABLE_TARGET_DB=false           # Target DB not required
AUTO_TRAIN_CHROMA=false          # Manual ChromaDB setup
DEBUG=true                       # Verbose logging
```

### Production Mode
```env
SEED_DEMO_DATA=false             # No test data
ENABLE_TARGET_DB=true            # Target DB required
AUTO_TRAIN_CHROMA=true           # Auto-train on startup
DEBUG=false                      # Production logging
```

---

## Initialization

### Full System Initialization
```bash
# After containers start
./run.sh  # or docker-compose up

# Then initialize databases
python scripts/init_project.py
```

### Initialize System DB Only
```bash
python scripts/init_system_db.py
```

### Manual Golden Copy
```bash
# Copy source to runtime
cp assets/databases/vanna_db.db /app/data/vanna_db.db
```

---

## Audit Logging

All admin operations are logged to `AuditLog` table:

```sql
SELECT user_id, action, resource, details, created_at
FROM audit_logs
WHERE action LIKE 'db.%'
ORDER BY created_at DESC
LIMIT 20;
```

**Logged Actions**:
- `db.backup.create` - Backup created
- `db.backup.list` - Backup list requested
- `db.backup.restore` - Restore operation started
- `db.chroma.train` - ChromaDB training started
- `db.chroma.inspect` - Knowledge base inspected
- `db.chroma.clear` - Collection cleared

---

## Troubleshooting

### Backup Fails
**Check**:
- PostgreSQL service health: `docker-compose logs postgres`
- Disk space: `df -h`
- Backup directory exists: `ls -la backups/`

**Solution**:
```bash
# Check database connectivity
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/admin/db/health

# Verify backup directory
docker-compose exec api ls -la /app/backups/
```

### ChromaDB Training Fails
**Prerequisites**:
- ChromaDB service running: `docker-compose logs chroma`
- Target DB accessible
- ENABLE_TARGET_DB=true

**Solution**:
```bash
# Check ChromaDB health
curl http://localhost:8001/

# Verify Target DB configuration
grep TARGET_DATABASE_URL .env
```

### Authentication Fails
**Get token**:
```bash
curl -X POST http://localhost:8000/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"..."}'
```

**Include in requests**:
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/admin/db/health
```

---

## Monitoring

### Check Service Health
```bash
# API service
curl http://localhost:8000/health

# All services
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f postgres
docker-compose logs -f chroma
```

### Application Logs
```bash
# View init logs
tail -f logs/init_project.log
tail -f logs/init_system_db.log

# View app logs (in container)
docker-compose exec api tail -f logs/app.log
```

---

## Performance

### Database Pool Stats
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/admin/db/health | jq '.connection_pool'
```

### Table Sizes
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/admin/db/stats | jq '.tables | sort_by(.size)'
```

### Backup Sizes
```bash
# Check recent backups
ls -lh backups/*.tar.gz | head -10
```

---

## Best Practices

1. **Regular Backups**
   - Schedule daily backups via cron or k8s CronJob
   - Monitor backup success rate
   - Test restore operations quarterly

2. **ChromaDB Management**
   - Train on fresh Target DB schemas
   - Monitor collection size via inspection endpoint
   - Clear old collections before training new ones

3. **Audit Trail**
   - Review audit logs weekly
   - Monitor for failed operations
   - Alert on failed backups

4. **Feature Flags**
   - Never run production with SEED_DEMO_DATA=true
   - Test golden copy in staging before production
   - Enable AUTO_TRAIN_CHROMA only when Target DB is ready

---

## API Documentation

Full OpenAPI documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

All endpoints require authentication via `Authorization: Bearer $TOKEN` header.
