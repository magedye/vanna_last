# Streamlit Module - Quick Reference

## Start Application

```bash
cd vanna-engine
./run.sh --build
```

**Access at:** http://localhost:8501  
**Default User:** admin@example.com / AdminPassword123

---

## Module Files

| File | Size | Purpose |
|------|------|---------|
| `app.py` | 12K | UI pages, navigation, forms |
| `client.py` | 12K | JWT auth, API client |
| `Dockerfile` | 4K | Container build |
| `requirements.txt` | 4K | Python dependencies |
| `README.md` | 8K | Module documentation |
| `INTEGRATION_GUIDE.md` | 12K | Deployment guide |
| `DEPLOYMENT_CHECKLIST.md` | 12K | Verification steps |

---

## Docker Commands

```bash
# Build frontend image
docker-compose build ui_streamlit

# View logs
docker-compose logs -f ui_streamlit

# Rebuild and restart
docker-compose up -d --build ui_streamlit

# Remove service
docker-compose down
```

---

## Local Development

```bash
cd ui_streamlit
pip install -r requirements.txt
streamlit run app.py
# Access at http://localhost:8501
```

---

## Environment Variables

**Frontend (.env):**
```env
BACKEND_URL=http://api:8000
API_TIMEOUT_SECONDS=30
DEBUG=true
```

**Backend:** (already configured in vanna-engine/)
```env
JWT_SECRET_KEY=...
POSTGRES_URL=...
REDIS_URL=...
```

---

## API Client Usage

```python
from client import VannaAPIClient

client = VannaAPIClient(backend_url="http://localhost:8000")

# Login
client.login("admin@example.com", "AdminPassword123")

# Generate SQL
result = client.generate_sql("Show top customers")
print(result["sql"])

# Execute query
result = client.execute_sql("SELECT * FROM users LIMIT 10")

# Get history
history = client.get_query_history()

# Submit feedback
client.submit_feedback(query_id, "Good translation", 5)

# Check health
health = client.health_check()
```

---

## Endpoints Used

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/api/v1/auth/login` | POST | No | User authentication |
| `/api/v1/generate-sql` | POST | No | Text-to-SQL |
| `/api/v1/fix-sql` | POST | No | SQL error fixing |
| `/api/v1/explain-sql` | POST | No | SQL explanation |
| `/api/v1/sql/execute` | POST | Yes | Query execution |
| `/api/v1/sql/history` | GET | Yes | Query history |
| `/api/v1/feedback` | POST | Yes | Feedback submission |
| `/api/admin/config` | GET | Admin | System config |
| `/health` | GET | No | Backend health |

---

## Remove Module

```bash
# Step 1: Stop services
docker-compose down

# Step 2: Delete directory
rm -rf ../ui_streamlit

# Step 3: Remove from docker-compose.yml
# Edit vanna-engine/docker-compose.yml
# Delete ui_streamlit service block (lines 145-164)

# Step 4: Restart backend only
./run.sh
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 8501 in use | Change `ports: ["8502:8501"]` in docker-compose.yml |
| Backend not found | Ensure backend is running: `curl http://localhost:8000/health` |
| Login fails | Check credentials in `.env` file |
| Build fails | Run `docker-compose build --no-cache ui_streamlit` |
| Module not starting | Check logs: `docker-compose logs ui_streamlit` |

---

## Customization

### Change Theme
Edit `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#FF6B6B"  # Change this
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"
```

### Add New Page
In `app.py`, add a render function:
```python
def render_my_page():
    st.header("My Page")
    # Your code here

# In render_main_app():
elif page == "My Page":
    render_my_page()
```

### Add API Endpoint Call
In `client.py`:
```python
def my_method(self, param):
    return self._make_request(
        "POST",
        "/api/v1/my-endpoint",
        {"param": param}
    )
```

---

## Security

✅ **Safe:** BACKEND_URL, timeouts, debug flag  
❌ **Never stored:** Database credentials, API keys, JWT secrets

---

## Status Check

```bash
# Backend health
curl http://localhost:8000/health

# Frontend health
curl http://localhost:8501/_stcore/health

# Docker services
docker-compose ps
```

---

## Deployment

For production, place behind reverse proxy (Nginx/Traefik):
```nginx
server {
    listen 443 ssl;
    server_name app.example.com;
    
    location / {
        proxy_pass http://ui_streamlit:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

**Created:** 2025-11-21  
**Status:** ✅ Production Ready  
**Location:** `/home/mfadmin/new-vanna/ui_streamlit/`
