# Deployment Checklist

Complete verification checklist for production deployment.

---

## Pre-Deployment Verification

### Environment Configuration
- [ ] `.env.prod` created from `.env.example`
- [ ] All required variables set:
  - [ ] DATABASE_URL (PostgreSQL connection)
  - [ ] SECRET_KEY (app secret)
  - [ ] JWT_SECRET_KEY (JWT signing)
  - [ ] POSTGRES_PASSWORD (secure password)
  - [ ] REDIS_PASSWORD (secure password)
- [ ] Feature flags set correctly:
  - [ ] SEED_DEMO_DATA=false
  - [ ] ENABLE_TARGET_DB=true
  - [ ] AUTO_TRAIN_CHROMA=true
- [ ] LLM provider configured (OPENAI_API_KEY or alternative)
- [ ] CHROMA_HOST and CHROMA_PORT correct
- [ ] BACKUP_DIR writable and accessible

### Source Database (Golden Copy)
- [ ] Source database file obtained: `vanna_db.db`
- [ ] Copied to `assets/databases/vanna_db.db`
- [ ] File permissions correct (readable by app)
- [ ] File size > 0 (not empty)

### Docker Infrastructure
- [ ] Docker installed and running
- [ ] Docker Compose >= 1.29
- [ ] Sufficient disk space:
  - [ ] PostgreSQL: ~5GB minimum
  - [ ] Backups: ~10GB minimum
  - [ ] ChromaDB: ~2GB minimum
- [ ] Network connectivity verified
- [ ] Port availability checked (8000, 5432, 6379, 8001)

### Directory Structure
- [ ] `assets/databases/` exists
- [ ] `backups/` exists and writable
- [ ] `data/` exists and writable
- [ ] `logs/` exists and writable
- [ ] All `.gitkeep` files in place

---

## Deployment Steps

### 1. Preparation
- [ ] Pull latest code
- [ ] Review FINAL_COMPLETION_SUMMARY.md
- [ ] Read ADMIN_OPERATIONS_GUIDE.md
- [ ] Verify all files compile: `python3 -m py_compile app/config.py app/main.py`

### 2. Environment Setup
- [ ] Copy environment template: `cp docker/env/.env.example .env.prod`
- [ ] Edit `.env.prod` with production values
- [ ] Verify all critical variables: `grep -E "SECRET_KEY|DATABASE_URL|POSTGRES_PASSWORD|REDIS_PASSWORD" .env.prod | grep -v "^#"`
- [ ] Set VANNA_ENV_FILE: `export VANNA_ENV_FILE=.env.prod`

### 3. Source Database
- [ ] Obtain production vanna_db.db file
- [ ] Copy to Golden Copy location: `cp vanna_db.db assets/databases/`
- [ ] Verify file: `ls -lh assets/databases/vanna_db.db`

### 4. Start Services
- [ ] Start Docker services: `./run.sh` or `./run.ps1`
- [ ] Wait for services to be healthy:
  - [ ] PostgreSQL: `docker-compose logs postgres | grep "ready to accept"`
  - [ ] Redis: `docker-compose logs redis | grep "Ready"`
  - [ ] ChromaDB: `docker-compose logs chroma`
  - [ ] API: `docker-compose logs api | grep "Application startup complete"`

### 5. Initialize Databases
- [ ] Run initialization: `python scripts/init_project.py`
- [ ] Wait for completion (see logs in `logs/init_project.log`)
- [ ] Verify success:
  ```bash
  # Check database tables
  docker-compose exec postgres psql -U postgres -d vanna_db -c "\dt"
  
  # Check admin user
  docker-compose exec postgres psql -U postgres -d vanna_db -c "SELECT email, role FROM users LIMIT 5;"
  ```

### 6. Post-Initialization Verification
- [ ] Check API health: `curl http://localhost:8000/health`
- [ ] Check API docs: `curl http://localhost:8000/docs | grep -i "openapi"`
- [ ] Verify database connectivity:
  ```bash
  curl -X GET http://localhost:8000/admin/db/health \
    -H "Authorization: Bearer YOUR_TOKEN"
  ```
- [ ] List database tables:
  ```bash
  curl -X GET http://localhost:8000/admin/db/stats \
    -H "Authorization: Bearer YOUR_TOKEN"
  ```

### 7. Test Admin Operations
- [ ] Login and get admin token
- [ ] Test database health: `POST /admin/db/health`
- [ ] Test backup creation: `POST /admin/db/backup`
- [ ] Check backup status: `GET /admin/db/backup/status/{task_id}`
- [ ] List backups: `GET /admin/db/backup/list`
- [ ] Inspect ChromaDB: `GET /admin/db/chroma/knowledge-base`

### 8. Security Verification
- [ ] Verify no demo data in production (SEED_DEMO_DATA=false)
- [ ] Check audit logs: `SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT 10;`
- [ ] Test RBAC - admin endpoints fail without auth
- [ ] Test RBAC - non-admin users cannot access admin endpoints
- [ ] Verify SECRET_KEY is unique (not default)
- [ ] Verify JWT_SECRET_KEY is unique (not default)

### 9. Monitoring Setup
- [ ] Configure log aggregation (if applicable)
- [ ] Set up monitoring for backup tasks
- [ ] Configure alerts for failed backups
- [ ] Monitor disk space for backups
- [ ] Monitor database size growth

### 10. Backup & Recovery Test
- [ ] Create manual backup: `POST /admin/db/backup`
- [ ] Wait for completion and note filename
- [ ] Verify backup file exists: `ls -lh backups/backup_*.tar.gz`
- [ ] Test backup verification (optional advanced step)
- [ ] Document backup location and procedure

---

## Production Configuration Recommendations

### Security
- [ ] Use strong PostgreSQL password (32+ chars, mixed case + numbers + symbols)
- [ ] Use strong Redis password (32+ chars)
- [ ] Generate unique SECRET_KEY and JWT_SECRET_KEY
- [ ] Rotate secrets quarterly
- [ ] Enable TLS for database connections
- [ ] Use managed PostgreSQL service (AWS RDS, Azure Database, GCP Cloud SQL)

### Performance
- [ ] Set DB_POOL_SIZE to (2 × CPU_COUNT) + 2
- [ ] Set DB_MAX_OVERFLOW to min(5, DB_POOL_SIZE / 2)
- [ ] Configure Redis maxmemory-policy: allkeys-lru
- [ ] Enable query result caching
- [ ] Monitor slow queries

### Reliability
- [ ] Enable automated backups (hourly or daily)
- [ ] Test backup restoration weekly
- [ ] Monitor backup storage growth
- [ ] Set up alerts for backup failures
- [ ] Keep 14+ days of backups (not just 7)
- [ ] Replicate backups to separate storage (S3, etc.)

### Compliance
- [ ] Review audit logs daily
- [ ] Archive audit logs to immutable storage
- [ ] Document backup procedure
- [ ] Document disaster recovery procedure
- [ ] Test disaster recovery quarterly
- [ ] Maintain change log for all configurations

---

## Rollback Procedures

### If Initialization Fails
1. Check logs: `tail -f logs/init_project.log`
2. Verify database connectivity: `docker-compose logs postgres`
3. Check feature flags in .env
4. Reset PostgreSQL:
   ```bash
   docker-compose down
   docker volume rm vanna_project_postgres_data
   docker-compose up -d postgres redis chroma
   ```
5. Re-run initialization: `python scripts/init_project.py`

### If Services Won't Start
1. Check Docker status: `docker-compose ps`
2. Check service logs: `docker-compose logs [service_name]`
3. Verify ports not in use: `sudo lsof -i :8000 :5432 :6379 :8001`
4. Restart services: `docker-compose restart`

### If Database Corruption Suspected
1. Create backup of current state: `POST /admin/db/backup`
2. Verify recent backup exists: `GET /admin/db/backup/list`
3. Stop application (optional): `docker-compose stop api`
4. Restore from backup: `POST /admin/db/backup/restore/{filename}?confirm=true`
5. Verify data integrity

---

## Post-Deployment Validation

### Health Checks (Run hourly)
```bash
#!/bin/bash
# API Health
curl -f http://localhost:8000/health || exit 1

# Database Connectivity
curl -f -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:8000/admin/db/health || exit 1

# Backup Directory
test -d /app/backups && test -w /app/backups || exit 1

echo "✓ All health checks passed"
```

### Monitoring Checklist
- [ ] Database size growth rate (bytes/day)
- [ ] Backup size and frequency
- [ ] Audit log volume (records/day)
- [ ] API response times (p50, p95, p99)
- [ ] Error rates by endpoint
- [ ] Authentication success rate
- [ ] ChromaDB collection size

---

## Common Issues & Solutions

### Issue: "Golden Copy: Source database does not exist"
**Solution**:
```bash
cp vanna_db.db assets/databases/vanna_db.db
python scripts/init_project.py
```

### Issue: "PostgreSQL connection refused"
**Solution**:
```bash
# Wait for PostgreSQL to start
docker-compose logs postgres
# If stuck, reset:
docker-compose down
docker volume rm vanna_project_postgres_data
docker-compose up -d postgres
# Wait 10 seconds, then re-run init
```

### Issue: "ChromaDB connection failed"
**Solution**:
```bash
# ChromaDB is optional. Check if needed:
grep AUTO_TRAIN_CHROMA .env.prod
# If not needed, set to false and re-run
```

### Issue: "Token invalid for admin operations"
**Solution**:
```bash
# Get new token
curl -X POST http://localhost:8000/api/v1/login \
  -d '{"email":"admin@example.com","password":"..."}' \
  -H "Content-Type: application/json"
```

---

## Handoff Checklist

Before giving to operations team:

- [ ] All documentation reviewed
- [ ] Runbooks created for common procedures
- [ ] Backup restore test completed successfully
- [ ] Monitoring/alerting configured
- [ ] On-call procedures documented
- [ ] Escalation contacts established
- [ ] Training session completed
- [ ] Access credentials securely transferred
- [ ] Change log updated
- [ ] Disaster recovery plan filed

---

## Sign-Off

- [ ] Technical Lead: __________ Date: __________
- [ ] Security Review: __________ Date: __________
- [ ] Operations: __________ Date: __________
- [ ] Project Manager: __________ Date: __________

