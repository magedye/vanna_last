# Streamlit Module Integration Guide

## Module Status: Complete ✓

The Streamlit frontend has been created as a fully encapsulated, self-contained module with **zero database access** and **secure HTTP-based communication** with the FastAPI backend.

## Quick Start

### 1. Start the Services

From the project root:

```bash
cd vanna-engine
./run.sh --build
```

This will:
- Start PostgreSQL, Redis, ChromaDB
- Start the FastAPI backend (port 8000)
- Start Streamlit frontend (port 8501)
- Initialize the database

### 2. Access the Application

```
Frontend: http://localhost:8501
API Docs: http://localhost:8000/docs
Metrics:  http://localhost:8000/metrics
Flower:   http://localhost:5555
```

### 3. Login

Default credentials (from `.env` or `.env.dev`):
- Username: `admin@example.com`
- Password: `AdminPassword123`

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    User Browser                              │
└────────────────────┬──────────────────────────────────────────┘
                     │ HTTP (port 8501)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│         Streamlit Frontend (ui_streamlit/)                   │
│  - app.py: UI pages, session management                      │
│  - client.py: JWT auth, API communication                    │
│  - NO database access, NO backend secrets                    │
└────────────────────┬──────────────────────────────────────────┘
                     │ HTTP (port 8000)
                     │ Bearer Token (JWT)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│         FastAPI Backend (vanna-engine/)                      │
│  - Authentication: /api/v1/auth/login                        │
│  - SQL Operations: /api/v1/generate-sql, etc.                │
│  - Admin Routes: /api/admin/*                                │
│  - Database: PostgreSQL, ChromaDB, Redis                     │
└─────────────────────────────────────────────────────────────┘
```

## Module Structure

```
ui_streamlit/
├── app.py                          # Main Streamlit app (700 lines)
│   ├── render_login_page()         # Authentication UI
│   ├── render_main_app()           # Dashboard navigation
│   ├── render_sql_generator()      # Text-to-SQL interface
│   ├── render_query_executor()     # Direct SQL execution
│   ├── render_query_history()      # Query history browser
│   └── render_admin_panel()        # Admin dashboard
│
├── client.py                       # API Client (400 lines)
│   ├── VannaAPIClient              # Main client class
│   │   ├── login()                 # JWT authentication
│   │   ├── logout()                # Clear token
│   │   ├── generate_sql()          # Text-to-SQL
│   │   ├── fix_sql()               # SQL error fixing
│   │   ├── explain_sql()           # SQL explanation
│   │   ├── execute_sql()           # Query execution
│   │   ├── get_query_history()     # History retrieval
│   │   ├── submit_feedback()       # Feedback submission
│   │   ├── get_config()            # Admin config
│   │   └── health_check()          # Backend health
│   └── get_client()                # Global client instance
│
├── Dockerfile                      # Container build (25 lines)
│   ├── Python 3.11 base
│   ├── Pip requirements installation
│   ├── Port 8501 exposure
│   └── Health check
│
├── requirements.txt                # Dependencies (6 packages)
│   ├── streamlit==1.28.1
│   ├── requests==2.31.0
│   ├── python-dotenv==1.0.0
│   ├── pydantic==2.5.0
│   ├── jwt==1.3.1
│   └── PyJWT==2.7.0
│
├── .streamlit/
│   └── config.toml                 # Streamlit configuration
│       ├── Theme colors
│       ├── Port settings
│       └── Server options
│
├── .env.example                    # Environment template
├── .gitignore                      # Git exclusions
├── .dockerignore                   # Docker build exclusions
├── README.md                       # Module documentation
└── INTEGRATION_GUIDE.md            # This file
```

## Security Features

### What is NOT included (Zero Backend Exposure)
- ❌ PostgreSQL credentials
- ❌ Redis URL or password
- ❌ ChromaDB endpoint configuration
- ❌ LLM API keys (OpenAI, Anthropic, etc.)
- ❌ JWT signing keys
- ❌ Database connection strings
- ❌ Backend internal configuration

### What IS included (Safe Frontend Config)
- ✅ Backend URL (public API endpoint)
- ✅ Request timeouts
- ✅ Debug mode flag
- ✅ Optional demo credentials (for testing)

### Authentication Flow
```
1. User enters username/password
   └──> Sent to POST /api/v1/auth/login
2. Backend verifies, returns JWT token
3. Client stores token in session_state (memory only)
4. All subsequent requests include: Authorization: Bearer {token}
5. Token automatically cleared on logout
6. Token expires per JWT_EXPIRATION_HOURS (default: 24 hours)
```

## Docker Compose Integration

The ui_streamlit service in docker-compose.yml:

```yaml
ui_streamlit:
  build:
    context: ../ui_streamlit      # Build from isolated directory
    dockerfile: Dockerfile
  ports:
    - "8501:8501"                  # Expose Streamlit port
  environment:
    BACKEND_URL: http://api:8000   # Internal Docker network
    DEBUG: ${DEBUG:-false}          # From .env
  depends_on:
    - api                           # Wait for backend startup
  networks:
    - vanna_project_net             # Shared network
  healthcheck:                       # Container health monitoring
    test: ["CMD", "python", "-c", "import requests; ..."]
    interval: 30s
```

## API Endpoints Used

The Streamlit frontend calls these backend endpoints:

### Public (No Auth)
- `POST /api/v1/auth/login` - User authentication
- `POST /api/v1/generate-sql` - Text-to-SQL
- `POST /api/v1/fix-sql` - SQL error fixing
- `POST /api/v1/explain-sql` - SQL explanation
- `GET /health` - Backend health check

### Authenticated
- `POST /api/v1/sql/execute` - Query execution
- `GET /api/v1/sql/history` - Query history
- `POST /api/v1/feedback` - Feedback submission

### Admin Only
- `GET /api/admin/config` - System configuration
- `POST /api/admin/approve-sql` - SQL approval
- `GET /api/admin/feedback-metrics` - Metrics

## Deployment Options

### Option 1: Docker Compose (Recommended)
```bash
cd vanna-engine
./run.sh
# Streamlit available at http://localhost:8501
```

### Option 2: Standalone Docker
```bash
cd ui_streamlit
docker build -t vanna-streamlit .
docker run -p 8501:8501 \
  -e BACKEND_URL=http://backend:8000 \
  vanna-streamlit
```

### Option 3: Local Development
```bash
cd ui_streamlit
pip install -r requirements.txt
streamlit run app.py
# Available at http://localhost:8501
```

## Removing the Module

To completely remove the Streamlit service:

### Step 1: Stop containers
```bash
cd vanna-engine
docker-compose down
```

### Step 2: Delete module directory
```bash
rm -rf ../ui_streamlit
```

### Step 3: Remove from docker-compose.yml
```bash
# Delete the ui_streamlit service block
nano docker-compose.yml
```

### Step 4: Restart backend only
```bash
./run.sh
```

After removal:
- Backend continues working normally
- API docs still available at `/docs`
- All backend functionality intact
- Only web UI is removed

## Configuration Management

### Adding New Environment Variables

1. Add to `.env.example`:
   ```env
   NEW_VAR=default_value
   ```

2. Update Dockerfile or docker-compose.yml if needed

3. Load in app.py:
   ```python
   new_var = os.getenv("NEW_VAR", "default")
   ```

### Production Deployment

1. **Build Docker image**:
   ```bash
   docker build -t vanna-streamlit:1.0 ui_streamlit/
   ```

2. **Push to registry**:
   ```bash
   docker push my-registry/vanna-streamlit:1.0
   ```

3. **Deploy with docker-compose**:
   ```yaml
   ui_streamlit:
     image: my-registry/vanna-streamlit:1.0
     ports:
       - "8501:8501"
     environment:
       BACKEND_URL: https://api.example.com
       DEBUG: "false"
   ```

4. **Use reverse proxy** (Nginx/Traefik):
   - Terminate HTTPS
   - Handle rate limiting
   - Route to backend and frontend

## Troubleshooting

### "Connection refused" on startup
- Check backend is running: `curl http://localhost:8000/health`
- Verify BACKEND_URL matches docker-compose network

### Login fails with "401 Unauthorized"
- Verify credentials in `.env`
- Check backend auth configuration
- Review backend logs: `docker-compose logs api`

### Streamlit not responding
- Check container status: `docker-compose ps`
- View logs: `docker-compose logs ui_streamlit`
- Rebuild: `docker-compose up -d --build ui_streamlit`

### Port 8501 already in use
```bash
# Change in docker-compose.yml or .env
PORT_STREAMLIT=8502
# Then update docker-compose: ports: ["${PORT_STREAMLIT}:8501"]
```

## Performance Tips

1. **Connection Pooling**: HTTPAdapter in client.py handles this
2. **Timeout Tuning**: Adjust `API_TIMEOUT_SECONDS` for slow queries
3. **Caching**: Streamlit caches by default, add `@st.cache_data` to expensive functions
4. **Error Handling**: All API calls have retry logic in client.py

## Development Workflow

```bash
# 1. Terminal 1: Start backend services
cd vanna-engine
docker-compose up -d postgres redis chroma

# 2. Terminal 2: Run backend
cd vanna-engine
uvicorn app.main:app --reload

# 3. Terminal 3: Run frontend
cd ui_streamlit
streamlit run app.py

# 4. Browser: Open http://localhost:8501
```

## Next Steps

1. **Customize Theme**: Edit `.streamlit/config.toml`
2. **Add Pages**: Create new render functions in app.py
3. **Extend API Client**: Add methods to VannaAPIClient
4. **Deploy**: Follow production deployment section
5. **Monitor**: Use `/metrics` endpoint and Flower dashboard

## Support and Documentation

- **Module README**: `README.md` (this directory)
- **API Docs**: http://localhost:8000/docs
- **Backend Setup**: `../vanna-engine/README.md`
- **Environment Config**: `../vanna-engine/.env.example`
- **All Endpoints**: `../vanna-engine/ALL_ENDPOINTS.md`

---

**Status**: ✅ Production Ready
**Last Updated**: 2025-11-21
**Version**: 1.0.0
