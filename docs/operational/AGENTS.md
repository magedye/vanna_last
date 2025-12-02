# AGENTS.md - Vanna Insight Engine Agent Commands

## Project Overview
Vanna Insight Engine: AI-Powered Text-to-SQL Backend (v1.0.0, 100% complete)

## Common Commands

### Environment Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit environment variables (LLM keys, DB URLs)
nano .env
```

### Database Operations (UPDATED - Master Initializer)
```bash
# Initialize database (MASTER SCRIPT - calls init_project.py)
./db_init.sh

# Force reinitialize (idempotent)
./db_init.sh --force

# Clean and reinitialize
./db_init.sh --clean

# Run migrations manually (rarely needed - init_project.py handles this)
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Note: db_init.sh must run AFTER containers are started (./run.sh)
# Note: Master initializer (init_project.py) runs Alembic automatically
```

### Development Server
```bash
# Start FastAPI with auto-reload
uvicorn app.main:app --reload

# Start with specific host/port
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Docker Operations
```bash
# Start all services (uses .env.dev by default)
./run.sh

# Start with clean build
./run.sh --build

# Clean rebuild (remove containers/volumes)
./run.sh --clean --build

# Use specific environment
VANNA_ENV_FILE=docker/env/.env.stage ./run.sh

# Stop all services
docker-compose down

# View logs
docker-compose logs -f api

# Rebuild and restart
docker-compose up -d --build api
```

### Environment Management
```bash
# View current environment file structure
cat docker/env/.env.example

# All environments MUST have identical variables (only values differ)
# - .env.example: Template with all variables
# - .env.dev: Development (SQLite, Ollama, 1 worker)
# - .env.stage: Staging (PostgreSQL, OpenAI, 4 workers)
# - .env.production.example: Production template (not loaded)

# When adding new variables:
# 1. Add to .env.example with comments
# 2. Add to docker/env/.env.dev and docker/env/.env.prod if overrides are needed
# 3. Update app/config.py to read variable
# 4. All files MUST have same variable count

# Critical: Unified passwords across environments
# REDIS_PASSWORD=abc@12345 (same in all files)
# REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0 (uses variable substitution)
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_interpreter.py -v

# Run integration tests
pytest tests/integration/
```

### Vanna Model Training
```bash
# Generate training data
python scripts/generate_training_data.py

# Train Vanna model
python scripts/train_vanna_model.py

# Validate model
python scripts/validate_vanna_model.py
```

### Monitoring
```bash
# View application logs
tail -f logs/app.log

# View Celery logs
docker-compose logs -f celery_worker

# Access Flower (Celery monitoring)
open http://localhost:5555

# View Prometheus metrics
curl http://localhost:8000/metrics
```

### API Endpoints
```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs

# Core endpoints
curl http://localhost:8000/                    # Root with links
curl http://localhost:8000/health              # Health status
curl http://localhost:8000/metrics             # Prometheus metrics

# SQL endpoints (OpenAPI v3.1.0 compliant)
curl -X POST "http://localhost:8000/api/v1/generate-sql" \
  -H "Content-Type: application/json" \
  -d '{"question": "How many orders this month?"}'

curl -X POST "http://localhost:8000/api/v1/fix-sql" \
  -H "Content-Type: application/json" \
  -d '{"sql": "SELECT * FORM users", "error_msg": "Syntax error"}'

curl -X POST "http://localhost:8000/api/v1/explain-sql" \
  -H "Content-Type: application/json" \
  -d '{"sql": "SELECT * FROM users WHERE id > 100"}'

# Admin endpoints (configuration, approval, scheduling)
curl http://localhost:8000/admin/config                    # Get config
curl http://localhost:8000/admin/feedback-metrics          # Feedback stats
curl http://localhost:8000/admin/scheduled/list            # Scheduled reports
```

### Kubernetes Deployment
```bash
# Deploy to staging
kubectl apply -k k8s/overlays/staging

# Deploy to production
kubectl apply -k k8s/overlays/production

# Check pod status
kubectl get pods
```

## Agent Behavior
- Use absolute paths for file operations
- Verify directory existence before creating files/directories
- Log all actions with ISO timestamps
- Ensure dependency order for service startup
- Sync state between AGENTS.md and .vanna_amp_state/

## State Persistence
- Environment variables in .vanna_amp_state/session.env
- Context in .vanna_amp_state/context.log
- Workspace metadata in .vanna_amp_state/workspace.json
- Sync AGENTS.md bidirectionally with .vanna_amp_state/

## Archived Documentation
- Legacy delivery summaries and specs: /home/mfadmin/new-vanna/archive/2025-11-11-docs
- Historical in-project guides (STARTUP_GUIDE, QUICK_REFERENCE, etc.): /home/mfadmin/new-vanna/archive/2025-11-11-docs/vanna-engine
- Reference the archive when older runbooks or specs are needed; current workflow docs stay under vanna-engine/

## Implementation Timeline
- 2025-11-11T11:50:08+03:00 - Validation fixes completed: pytest green, mypy reduced errors, manual API test passed
- 2025-11-11T14:30:00+03:00 - OpenAPI 3.1.0 complete implementation: all 13 endpoints, correlation IDs, health checks, admin suite

### Streamlit Frontend
```bash
# Build just the frontend image
docker-compose build ui_streamlit

# Access Streamlit UI
open http://localhost:8501

# View Streamlit logs
docker-compose logs -f ui_streamlit

# Rebuild and restart frontend
docker-compose up -d --build ui_streamlit

# Remove Streamlit service (keep backend running)
# 1. docker-compose down (stops all)
# 2. rm -rf ../ui_streamlit (delete module)
# 3. Edit docker-compose.yml (delete ui_streamlit service block)
# 4. ./run.sh (restart backend only)
```

### Streamlit Development
```bash
# Local development (without Docker)
cd ../ui_streamlit
pip install -r requirements.txt
streamlit run app.py

# Access at http://localhost:8501
# Backend must be running at http://localhost:8000
```

### Streamlit Configuration
```bash
# Edit environment variables
nano ../ui_streamlit/.env

# Edit Streamlit theme and settings
nano ../ui_streamlit/.streamlit/config.toml

# View module structure
ls -la ../ui_streamlit/

# Key files:
# - app.py: UI pages and logic
# - client.py: JWT auth and API communication
# - .env.example: Configuration template
# - requirements.txt: Dependencies
```
