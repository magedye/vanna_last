# Vanna Insight Engine - Streamlit Frontend

A fully encapsulated, self-contained Streamlit web interface for the Vanna Insight Engine backend.

## Features

- 🔐 Secure JWT-based authentication
- 🚀 Text-to-SQL generation from natural language
- 🔧 SQL error fixing and validation
- 📖 SQL explanation in plain English
- 💾 Query history and execution
- 📊 Admin dashboard and configuration
- 🛡️ Zero database credentials stored locally
- 🐳 Runs as independent Docker service

## Architecture

This is a **fully isolated module**:
- **No database access**: All communication goes through HTTP to the backend
- **No backend credentials**: Only frontend configuration stored
- **Removable**: Delete this directory and Docker service to remove UI completely
- **Decoupled**: Can be deployed independently from backend

## Getting Started

### Prerequisites

- Python 3.11+
- Docker (for containerized deployment)
- Running Vanna Insight Engine backend

### Local Development

1. Copy environment file:
   ```bash
   cp .env.example .env
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run Streamlit:
   ```bash
   streamlit run app.py
   ```

4. Open http://localhost:8501 in your browser

### Docker Deployment

The frontend is integrated into docker-compose.yml:

```bash
# Start all services
cd vanna-engine
./run.sh

# Access Streamlit
open http://localhost:8501
```

## Configuration

### Environment Variables

Create `.env` file with:

```env
# Backend API Configuration
BACKEND_URL=http://api:8000
API_TIMEOUT_SECONDS=30

# Debug Mode
DEBUG=true

# Default Credentials (optional)
DEFAULT_USERNAME=admin@example.com
DEFAULT_PASSWORD=AdminPassword123
```

### Streamlit Config

Edit `.streamlit/config.toml` for:
- Theme colors
- Port and server settings
- Cache configuration

## Project Structure

```
ui_streamlit/
├── app.py                      # Main Streamlit application
├── client.py                   # Secure API client (JWT handling)
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container configuration
├── .env.example               # Environment template
├── .streamlit/
│   └── config.toml           # Streamlit settings
└── README.md                 # This file
```

## API Client (client.py)

The `VannaAPIClient` class handles:

- **Authentication**: JWT token management via `/auth/login`
- **Token Refresh**: Automatic expiry checking
- **Error Handling**: Retry logic and graceful degradation
- **Session Management**: HTTP session with connection pooling

### Key Methods

```python
client = VannaAPIClient(backend_url="http://api:8000")

# Authentication
client.login(username, password)
client.logout()

# SQL Operations
client.generate_sql("What are my top customers?")
client.fix_sql(sql, error_message)
client.explain_sql(sql_query)
client.execute_sql(sql_query)

# Query History
client.get_query_history()

# Feedback
client.submit_feedback(query_id, feedback, rating)

# Admin
client.get_config()

# Health
client.health_check()
```

## Security Model

### What is NOT stored here
- Database credentials (PostgreSQL, ChromaDB, Redis)
- Backend internal configuration
- LLM API keys
- Encryption keys

### What IS stored
- Frontend configuration (URLs, timeouts)
- Session JWT tokens (temporary, memory-only)
- User feedback and preferences

### Authentication Flow

1. User enters credentials on login page
2. Client sends to `/api/v1/auth/login`
3. Backend verifies credentials
4. Backend returns JWT access token
5. Client includes token in subsequent API requests
6. Token automatically cleared on logout

## Development

### Code Organization

- **app.py**: UI pages and Streamlit layout
- **client.py**: All backend communication
- **Separation of concerns**: No business logic in app.py, no UI code in client.py

### Adding New Features

1. **New API endpoint?** Add method to `VannaAPIClient` in client.py
2. **New page?** Add render function in app.py
3. **New configuration?** Add to `.env.example` and environment loading

### Testing

Manual testing via Streamlit development server:
```bash
streamlit run app.py --logger.level=debug
```

## Deployment

### Docker Compose Integration

The service is included in `../vanna-engine/docker-compose.yml`:

```yaml
ui_streamlit:
  build: ../ui_streamlit
  ports:
    - "8501:8501"
  environment:
    BACKEND_URL: http://api:8000
    DEBUG: "false"
  depends_on:
    - api
  networks:
    - vanna_project_net
```

### Production Considerations

1. **HTTPS**: Place behind reverse proxy (Nginx/Traefik)
2. **Environment variables**: Use secure secret management
3. **Rate limiting**: Handled by backend
4. **Session timeout**: Configured via JWT expiry
5. **Monitoring**: Check health endpoint regularly

## Troubleshooting

### Connection Issues

```bash
# Check backend is running
curl http://localhost:8000/health

# Check Streamlit is running
curl http://localhost:8501/_stcore/health
```

### Authentication Issues

- Verify credentials are correct
- Check backend JWT configuration
- Review `/health` endpoint for service status

### Performance

- Increase `API_TIMEOUT_SECONDS` for slow queries
- Use `--logger.level=error` to reduce logging overhead
- Check backend for slow SQL execution

## Cleanup

To remove the Streamlit service entirely:

```bash
# Stop and remove Docker service
docker-compose down

# Delete directory
rm -rf ui_streamlit/

# Remove from docker-compose.yml if standalone
```

## License

Same as parent Vanna Insight Engine project.

## Support

For issues, refer to:
- Backend documentation: `../vanna-engine/README.md`
- API endpoints: `../vanna-engine/ALL_ENDPOINTS.md`
- Configuration: `../vanna-engine/.env.example`
