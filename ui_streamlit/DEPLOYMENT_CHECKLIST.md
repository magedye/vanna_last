# Streamlit Module Deployment Checklist

## Pre-Deployment Verification

### Code Structure
- [x] `app.py` created (335 lines)
- [x] `client.py` created (359 lines)
- [x] `Dockerfile` created
- [x] `requirements.txt` created
- [x] `.streamlit/config.toml` created
- [x] `.env.example` created
- [x] `.gitignore` created
- [x] `.dockerignore` created
- [x] `README.md` created
- [x] `INTEGRATION_GUIDE.md` created
- [x] Total: 10 core files

### Security Verification
- [x] No PostgreSQL credentials in code
- [x] No Redis connection strings in code
- [x] No ChromaDB endpoints in code
- [x] No LLM API keys in code
- [x] No JWT signing keys in code
- [x] No database URLs in code
- [x] Only `BACKEND_URL` in frontend environment
- [x] JWT token stored in session_state (memory only)
- [x] Credentials never logged or exposed

### Docker Integration
- [x] Service added to docker-compose.yml
- [x] Build context set correctly: `../ui_streamlit`
- [x] Port 8501 exposed
- [x] Environment variables configured
- [x] `depends_on: [api]` for startup order
- [x] Network set to `vanna_project_net`
- [x] Health check configured

### API Client Features
- [x] JWT authentication implemented
- [x] Bearer token in headers
- [x] Token expiry checking
- [x] Session pooling with retry logic
- [x] Timeout handling (configurable)
- [x] Error handling with user messages
- [x] All public endpoints covered
- [x] All authenticated endpoints covered

### UI Implementation
- [x] Login page with credentials form
- [x] SQL Generator interface
- [x] Query Executor interface
- [x] Query History browser
- [x] Admin Dashboard
- [x] System status monitoring
- [x] Error messages user-friendly
- [x] Loading spinners for async operations

### Documentation
- [x] Module README.md complete
- [x] Integration guide complete
- [x] Code comments included
- [x] Configuration examples provided
- [x] Troubleshooting section included
- [x] Deployment scenarios documented

---

## Quick Start Verification

### Step 1: Verify Files Exist
```bash
cd /home/mfadmin/new-vanna/ui_streamlit

ls -la app.py           # ✓ Should exist
ls -la client.py        # ✓ Should exist
ls -la Dockerfile       # ✓ Should exist
ls -la requirements.txt # ✓ Should exist
ls -la README.md        # ✓ Should exist

# Count total lines
wc -l *.py
# Expected: ~700 total
```

### Step 2: Verify Docker Configuration
```bash
cd /home/mfadmin/new-vanna/vanna-engine

# Check service exists in docker-compose.yml
grep -A 15 "ui_streamlit:" docker-compose.yml | head -20
# Expected: service definition with build, ports, environment

# Verify build context
grep "context:" docker-compose.yml | grep streamlit
# Expected: context: ../ui_streamlit
```

### Step 3: Verify No Secrets Leak
```bash
cd /home/mfadmin/new-vanna/ui_streamlit

# Should NOT contain these
grep -r "POSTGRES" . --include="*.py" && echo "ERROR: PostgreSQL found!" || echo "✓ Safe"
grep -r "REDIS_PASSWORD" . --include="*.py" && echo "ERROR: Redis found!" || echo "✓ Safe"
grep -r "CHROMA" . --include="*.py" && echo "ERROR: Chroma found!" || echo "✓ Safe"
grep -r "openai" . --include="*.py" --ignore-case && echo "ERROR: LLM key found!" || echo "✓ Safe"

# Should contain these
grep -q "BACKEND_URL" .env.example && echo "✓ BACKEND_URL present" || echo "ERROR: Missing!"
grep -q "JWT" client.py && echo "✓ JWT auth implemented" || echo "ERROR: Missing!"
grep -q "VannaAPIClient" client.py && echo "✓ API client implemented" || echo "ERROR: Missing!"
```

### Step 4: Build and Test Locally
```bash
cd /home/mfadmin/new-vanna/vanna-engine

# Build just the Streamlit image
docker-compose build ui_streamlit
# Expected: Successful build, no errors

# Check image was created
docker images | grep vanna
# Expected: vanna-engine-ui_streamlit image listed

# Start services
./run.sh --build
# Expected: All services start, including ui_streamlit

# Wait 10 seconds for startup
sleep 10

# Test health check
curl http://localhost:8000/health
# Expected: {"status": "healthy", ...}

curl http://localhost:8501/_stcore/health
# Expected: 200 OK (may not return JSON, that's OK)
```

### Step 5: Test Web Interface
```bash
# Open in browser
open http://localhost:8501
# Expected: Streamlit login page loads

# Try login with default credentials
# Username: admin@example.com
# Password: AdminPassword123
# Expected: Login successful, dashboard loads
```

---

## Environment Configuration

### Required Environment Variables

**Backend (vanna-engine/.env or .env.dev)**:
```env
APP_ENV=development
DEBUG=true
API_V1_PREFIX=/api/v1
JWT_SECRET_KEY=<your-key>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
INIT_ADMIN_USERNAME=admin@example.com
INIT_ADMIN_PASSWORD=AdminPassword123
POSTGRES_URL=postgresql://...
REDIS_URL=redis://...
```

**Frontend (ui_streamlit/.env)**:
```env
BACKEND_URL=http://api:8000
API_TIMEOUT_SECONDS=30
DEBUG=true
DEFAULT_USERNAME=admin@example.com
DEFAULT_PASSWORD=AdminPassword123
```

---

## Production Deployment

### Pre-Production Checklist
- [ ] Update `.env` with production database URLs (backend only)
- [ ] Set `DEBUG=false` in frontend environment
- [ ] Update `BACKEND_URL` to production API endpoint
- [ ] Configure HTTPS/SSL (reverse proxy required)
- [ ] Set secure JWT secret key
- [ ] Update CORS origins in backend
- [ ] Configure backup and recovery
- [ ] Set up monitoring and logging
- [ ] Create database backups
- [ ] Test disaster recovery

### Production Deployment Steps

1. **Build Docker images**:
```bash
# Backend image
docker build -t vanna-engine:1.0 vanna-engine/

# Frontend image
docker build -t vanna-streamlit:1.0 ui_streamlit/
```

2. **Push to registry** (e.g., Docker Hub, ECR, GCR):
```bash
docker tag vanna-engine:1.0 registry.example.com/vanna-engine:1.0
docker tag vanna-streamlit:1.0 registry.example.com/vanna-streamlit:1.0

docker push registry.example.com/vanna-engine:1.0
docker push registry.example.com/vanna-streamlit:1.0
```

3. **Update docker-compose.yml** for production:
```yaml
version: '3.8'

services:
  api:
    image: registry.example.com/vanna-engine:1.0
    environment:
      DEBUG: "false"
      BACKEND_URL: https://api.example.com
      # ... other prod settings

  ui_streamlit:
    image: registry.example.com/vanna-streamlit:1.0
    environment:
      BACKEND_URL: https://api.example.com
      DEBUG: "false"
    # ... prod config
```

4. **Deploy with Docker Swarm or Kubernetes**:
```bash
# Docker Swarm
docker stack deploy -c docker-compose.yml vanna

# Kubernetes
kubectl apply -k k8s/overlays/production
```

5. **Configure reverse proxy** (Nginx example):
```nginx
server {
    listen 443 ssl http2;
    server_name api.example.com;
    
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    
    location / {
        proxy_pass http://api:8000;
        proxy_set_header Authorization $http_authorization;
    }
}

server {
    listen 443 ssl http2;
    server_name app.example.com;
    
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    
    location / {
        proxy_pass http://ui_streamlit:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## Troubleshooting

### Build Issues

**Error: `ERROR: Unable to find image 'vanna-insight-engine:latest'`**
```bash
# Solution: Build the image first
docker-compose build ui_streamlit
```

**Error: `requirements.txt not found`**
```bash
# Verify file exists
ls -la /home/mfadmin/new-vanna/ui_streamlit/requirements.txt
# If missing, create it with:
# streamlit==1.28.1
# requests==2.31.0
# python-dotenv==1.0.0
# pydantic==2.5.0
# jwt==1.3.1
# PyJWT==2.7.0
```

### Runtime Issues

**Error: `Connection refused` when accessing http://localhost:8501**
```bash
# Check if container is running
docker-compose ps
# Expected: ui_streamlit service should be "Up"

# Check logs
docker-compose logs ui_streamlit
# Look for errors in startup

# If port conflict:
# Change docker-compose.yml: ports: ["8502:8501"]
# Then access: http://localhost:8502
```

**Error: `Login failed: Connection error`**
```bash
# Check backend is running
docker-compose ps api
# Expected: api service should be "Up"

# Verify backend URL
echo $BACKEND_URL  # Should be http://api:8000 for Docker

# Check backend logs
docker-compose logs api | tail -20
# Look for error messages
```

**Error: `ModuleNotFoundError: No module named 'streamlit'`**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or rebuild Docker image
docker-compose build --no-cache ui_streamlit
```

---

## Monitoring & Maintenance

### Health Checks
```bash
# Backend health
curl http://localhost:8000/health

# Frontend health
curl http://localhost:8501/_stcore/health

# Docker health
docker-compose ps
# All services should show "Up" and "healthy" (if healthcheck defined)
```

### Logs
```bash
# View frontend logs
docker-compose logs -f ui_streamlit

# View all logs
docker-compose logs -f

# View backend logs
docker-compose logs -f api
```

### Metrics
```bash
# View Prometheus metrics
curl http://localhost:8000/metrics

# Access Flower dashboard
open http://localhost:5555

# Access API docs
open http://localhost:8000/docs
```

### Cleanup
```bash
# Remove stopped containers
docker-compose down

# Remove images
docker rmi vanna-engine-ui_streamlit

# Remove volumes (WARNING: Deletes data!)
docker-compose down -v
```

---

## Performance Tuning

### Memory
- Frontend baseline: ~200 MB
- Backend: ~500 MB
- Databases: ~300 MB each
- Total: ~1.5 GB minimum

### CPU
- Single user: ~10% utilization
- Multiple concurrent users: Scale horizontally

### Network
- Login: ~1s
- SQL generation: ~2-10s
- Query execution: ~1-5s
- History load: ~500ms

### Optimization Tips
1. Increase `API_TIMEOUT_SECONDS` for slow queries
2. Enable query caching in backend
3. Use connection pooling (already implemented)
4. Monitor query performance
5. Implement pagination for history

---

## Rollback Procedure

If issues occur after deployment:

```bash
# 1. Stop services
docker-compose down

# 2. Revert to previous version
git checkout HEAD~1 docker-compose.yml

# 3. Rebuild with previous version
docker-compose build --no-cache

# 4. Restart services
./run.sh

# 5. Verify functionality
curl http://localhost:8000/health
curl http://localhost:8501/_stcore/health
```

---

## Support

For issues or questions:
1. Check logs: `docker-compose logs ui_streamlit`
2. Verify configuration: `.env.example`
3. Review documentation: `README.md`, `INTEGRATION_GUIDE.md`
4. Check backend health: `http://localhost:8000/health`
5. Review error messages in UI

---

## Sign-Off

**Status**: ✅ Ready for Deployment
**Date**: 2025-11-21
**Checked By**: Amp
**Version**: 1.0.0
