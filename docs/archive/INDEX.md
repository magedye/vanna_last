# Vanna Insight Engine - Documentation Index

**Last Updated:** November 20, 2025
**Status:** Complete and Production-Ready

---

## 🚀 Quick Start (Pick Your Need)

### I want to...

- **Start development immediately**
  → Read: [README.md](README.md) (Section: Quick Start)
  → Then run: `./run.sh --clean --build` + `./db_init.sh`

- **Deploy to production**
  → Read: [QUICK_STARTUP.md](../QUICK_STARTUP.md)
  → Then run: `./run.sh --env prod` + `./db_init.sh`

- **See all available commands**
  → Read: [AGENTS.md](AGENTS.md)
  → Or: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

- **Understand the new architecture**
  → Read: [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md)
  → And: [../REFACTORING_COMPLETE.md](../REFACTORING_COMPLETE.md)

---

## 📚 Documentation Guide

### Main Documents

| Document | Purpose | Length | Audience |
|----------|---------|--------|----------|
| **README.md** | Development quick start & API overview | ~500 lines | Developers |
| **QUICK_STARTUP.md** | Production deployment step-by-step | ~600 lines | DevOps/SRE |
| **QUICK_REFERENCE.md** | Cheat sheet for common tasks | ~200 lines | All users |
| **AGENTS.md** | Command reference for agents | ~200 lines | Developers/Automation |

### Refactoring Documentation

| Document | Purpose | Length |
|----------|---------|--------|
| **REFACTORING_SUMMARY.md** | Technical refactoring details | ~300 lines |
| **../REFACTORING_COMPLETE.md** | High-level summary & verification | ~300 lines |
| **This file (INDEX.md)** | Documentation navigation | ~200 lines |

### Enterprise Specifications

| Document | Purpose |
|----------|---------|
| **../SEMANTIC_LAYER_DESIGN.md** | Semantic compiler, glossary, and API contract |
| **../DATA_CONTROL_POLICIES.md** | Row/column security policies + enforcement SLAs |
| **../PROJECT_MANAGEMENT_SPEC.md** | Project templates, memberships, RBAC enhancements |
| **../DASHBOARD_MANAGER_SPEC.md** | Multi-dashboard orchestration and publish flows |
| **../SPREADSHEET_ENGINE_SPEC.md** | AI-powered spreadsheet behavior and endpoints |
| **../USAGE_MONITORING_SPEC.md** | Usage analytics data model and observability hooks |

---

## 🔧 Key Scripts

### Infrastructure (Docker)
**Script:** `./run.sh`
**Purpose:** Docker container lifecycle management
**When to run:** Before `./db_init.sh`
**Idempotent:** Yes

```bash
./run.sh --clean --build    # Dev with rebuild
./run.sh --env prod         # Production
./run.sh --diagnose         # System diagnostics
```

### Application (Database)
**Script:** `./db_init.sh`
**Purpose:** Database and application initialization
**When to run:** After `./run.sh` (containers must be running)
**Idempotent:** Yes (safe to re-run)

```bash
./db_init.sh                # Normal initialization
./db_init.sh --clean        # Clean and reinitialize
./db_init.sh --force        # Force (not recommended)
```

---

## 📋 Complete File Listing

### Root Level Files
```
/home/mfadmin/new-vanna/
├── README.md                          # Main project guide
├── QUICK_STARTUP.md                   # Production deployment
├── REFACTORING_COMPLETE.md            # Refactoring summary
└── [other root files...]
```

### vanna-engine/ Directory
```
vanna-engine/
├── db_init.sh                         # NEW: Database initialization
├── run.sh                             # Infrastructure launcher
├── README.md                          # Development guide
├── QUICK_REFERENCE.md                 # Command cheat sheet
├── AGENTS.md                          # Agent commands
├── REFACTORING_SUMMARY.md             # Technical details
├── INDEX.md                           # This file
├── docker-compose.yml                 # Main compose config
├── docker-compose.prod.yml            # Production overrides
├── Dockerfile                         # API container image
├── docker/env/
│   ├── .env.example                   # Environment template
│   ├── .env.dev                       # Development config
│   ├── .env.stage                     # Staging config
│   └── [other env files]
├── scripts/
│   ├── init_project_enhanced.py       # Database initialization
│   ├── backup_postgres.sh             # Backup utility
│   └── [other helper scripts]
├── app/                               # FastAPI application
├── tests/                             # Test suite
├── migrations/                        # Alembic migrations
└── [other directories...]
```

#### New Enterprise Module Tree

```
app/modules/
├── semantic_layer/        # Semantic compiler + services
├── data_control/          # Policy engine + CRUD service
├── projects/              # Project + template orchestration
├── dashboards/            # Dashboard lifecycle manager
├── spreadsheets/          # AI-powered spreadsheet engine
├── metrics/               # Pre-built metrics registry
├── usage_monitoring/      # Usage analytics service
└── user_management/       # Group/role automation
```

---

## 🔄 Workflow Comparison

### Old Workflow (Deprecated)
```bash
./startup.sh    # Single script (Docker + DB + Seed)
```
❌ Hard to debug
❌ Can't rerun safely
❌ All-or-nothing failure

### New Workflow (Current)
```bash
./run.sh        # Step 1: Infrastructure
./db_init.sh    # Step 2: Application
```
✅ Clear separation
✅ Idempotent & safe
✅ Better error isolation

---

## 🛠️ Common Tasks

### Development
```bash
# Initialize for the first time
./run.sh --clean --build
./db_init.sh

# Daily development
./run.sh                        # Already running, just start
# (make changes and save)
# API auto-reloads due to --reload flag in docker-compose

# View logs
docker-compose logs -f api

# Restart API service
docker-compose restart api
```

### Production
```bash
# First-time deployment
./run.sh --env prod
./db_init.sh

# Verify health
curl http://localhost:8000/health

# View logs
docker-compose logs -f api

# Rolling restart
docker-compose restart api
```

### Database Management
```bash
# Re-initialize database (data loss!)
./db_init.sh --clean

# Access psql directly
docker-compose exec postgres psql -U postgres -d vanna_db

# Backup
docker-compose exec postgres pg_dump -U postgres vanna_db > backup.sql

# Restore
docker-compose exec -T postgres psql -U postgres vanna_db < backup.sql
```

### Enterprise API Quick Links

- Semantic Models: `GET/POST /api/v1/semantic/models`, `POST /api/v1/semantic/compile`
- Semantic Interpreter & Compiler: `POST /api/v1/semantic/interpret`, `POST /api/v1/compiler/compile`
- Semantic Catalog: `/api/v1/entities`, `/api/v1/dimensions`, `/api/v1/hierarchies`, `/api/v1/filters`, `/api/v1/glossary`
- Projects & Templates: `GET/POST /api/v1/projects`, `GET /api/v1/projects/templates`
- Data Policies: `GET/POST /api/v1/data-control/policies`
- Dashboards & Spreadsheets: `/api/v1/dashboards*`, `/api/v1/spreadsheets*`
- Metrics Registry: `GET /api/v1/metrics`, `/metrics/templates`, `/metrics/import`
- Usage Analytics: `GET /api/v1/usage/summary|users|queries|dashboards|llm-tokens`
- User Management: `GET /api/v1/users`, `POST /api/v1/users`, `POST /api/v1/users/{id}/assign-role`
- Security: `GET /api/v1/security/audit-log|sessions`, `POST /api/v1/security/ip-restrictions|query-quota|token-rotation`

---

## 🚨 Troubleshooting Guide

### "Port already in use"
- `./run.sh` auto-detects and bumps ports
- Check: `grep "PORT=" docker/env/.env.dev`

### "Container is not running"
- Ensure Docker daemon is active: `docker ps`
- Start containers: `./run.sh`

### "Database initialization failed"
- Check containers are running: `docker ps`
- View logs: `docker-compose logs api`
- See: QUICK_STARTUP.md (Troubleshooting section)

### "Admin password not working"
- Default: `admin@example.com` / `[REDACTED:password]`
- See: README.md (Section 3: Authentication)

---

## 📊 Project Statistics

| Metric | Value |
|--------|-------|
| **FastAPI Version** | 0.104+ |
| **Python Version** | 3.8+ |
| **Docker Compose** | 1.29+ |
| **Endpoints** | 13+ (documented in OpenAPI 3.1.0) |
| **Database Models** | 10+ |
| **Test Coverage** | ~85% |

---

## 🔐 Security Notes

1. **Environment Files**
   - Never commit `.env` files to git
   - Use `.gitignore` to exclude them
   - Example: [See .gitignore](../.gitignore)

2. **Secrets Management**
   - `SECRET_KEY` - Generate with: `openssl rand -hex 32`
   - `JWT_SECRET_KEY` - Generate with: `openssl rand -hex 32`
   - Change admin password immediately in production

3. **CORS Configuration**
   - Edit `CORS_ORIGINS` in environment file
   - Default: restricted to localhost

---

## 🔗 External Resources

| Resource | URL |
|----------|-----|
| **FastAPI Docs** | https://fastapi.tiangolo.com/ |
| **SQLAlchemy** | https://docs.sqlalchemy.org/ |
| **Docker Compose** | https://docs.docker.com/compose/ |
| **Vanna OSS** | https://github.com/vanna-ai/vanna |

---

## 📞 Support & Questions

### For Different Issues:

| Issue | See Document |
|-------|--------------|
| Development setup | README.md |
| Production deployment | QUICK_STARTUP.md |
| Commands & operations | AGENTS.md or QUICK_REFERENCE.md |
| Technical refactoring | REFACTORING_SUMMARY.md |
| API integration | README.md (Section: API Endpoints) |
| Authentication | README.md (Section: Authentication) |

---

## ✅ Verification Checklist

Before going live:

- [ ] Docker & Docker Compose installed
- [ ] `.env` file configured with production values
- [ ] `SECRET_KEY` and `JWT_SECRET_KEY` are set
- [ ] API keys (OpenAI, etc.) are configured
- [ ] Database URL points to production DB
- [ ] Port 8000 (or custom port) is available
- [ ] `./run.sh` starts all services successfully
- [ ] `./db_init.sh` completes without errors
- [ ] `curl http://localhost:8000/health` returns success
- [ ] Default admin password changed

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| **1.0.0** | Nov 20, 2025 | Refactoring complete - Architecture separation |
| **0.9.0** | Nov 11, 2025 | OpenAPI 3.1.0 complete implementation |

---

## 📬 Next Steps

1. **New to the project?**
   → Start with [README.md](README.md)

2. **Need to deploy?**
   → Go to [QUICK_STARTUP.md](../QUICK_STARTUP.md)

3. **Looking for commands?**
   → Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

4. **Want technical details?**
   → Read [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md)

---

**Created:** November 20, 2025
**Last Updated:** November 20, 2025
**Maintained by:** Development Team
**Status:** ✅ Production Ready
