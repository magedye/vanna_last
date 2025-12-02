# Endpoints Quick Reference

**Total:** 50 endpoints | **REST API:** 24 | **Admin Dashboard:** 26

---

## By Category

### Core (4)
```
GET  /                      Root info
GET  /health                Health check
GET  /metrics               Prometheus metrics (text)
GET  /metrics/json          Prometheus metrics (JSON)
```

### Authentication (2)
```
POST /api/v1/login          Login (email/password)
POST /api/v1/signup         Register (email/password/name)
```

### Public SQL (3) - 100/hr limit
```
POST /api/v1/generate-sql   Generate SQL from question
POST /api/v1/fix-sql        Fix broken SQL
POST /api/v1/explain-sql    Explain SQL in English
```

### Protected SQL (4) - Requires auth, 500/hr limit
```
POST /api/v1/sql/generate   Generate SQL (with context)
POST /api/v1/sql/validate   Validate SQL syntax
POST /api/v1/sql/execute    Execute SQL query
GET  /api/v1/sql/history    Query history (limit=10)
```

### Feedback (3) - Requires auth, 500/hr limit
```
POST /api/v1/feedback       Submit feedback
GET  /api/v1/feedback/{id}  Get feedback for query
POST /api/v1/feedback/train Request model training
```

### Admin (7) - Requires admin role, 1000/hr limit
```
GET  /admin/config          Get configuration
POST /admin/config          Update config (planned)
POST /admin/approve-sql     Approve SQL (planned)
GET  /admin/feedback-metrics Get metrics (planned)
POST /admin/scheduled/create Create schedule (planned)
GET  /admin/scheduled/list   List schedules (planned)
DELETE /admin/scheduled/{id} Delete schedule (planned)
```

### Admin Dashboard (26) - Auto-generated CRUD

**Users (5)**
```
GET  /admin/dashboard/user/
GET  /admin/dashboard/user/{id}/edit
POST /admin/dashboard/user/create
POST /admin/dashboard/user/{id}/edit
POST /admin/dashboard/user/{id}/delete
```

**Queries (5)**
```
GET  /admin/dashboard/query/
GET  /admin/dashboard/query/{id}/edit
POST /admin/dashboard/query/create
POST /admin/dashboard/query/{id}/edit
POST /admin/dashboard/query/{id}/delete
```

**Feedback (5)**
```
GET  /admin/dashboard/feedback/
GET  /admin/dashboard/feedback/{id}/edit
POST /admin/dashboard/feedback/create
POST /admin/dashboard/feedback/{id}/edit
POST /admin/dashboard/feedback/{id}/delete
```

**Audit Logs (5)**
```
GET  /admin/dashboard/auditlog/
GET  /admin/dashboard/auditlog/{id}/edit
POST /admin/dashboard/auditlog/create
POST /admin/dashboard/auditlog/{id}/edit
POST /admin/dashboard/auditlog/{id}/delete
```

**Configuration (5)**
```
GET  /admin/dashboard/configuration/
GET  /admin/dashboard/configuration/{id}/edit
POST /admin/dashboard/configuration/create
POST /admin/dashboard/configuration/{id}/edit
POST /admin/dashboard/configuration/{id}/delete
```

**Navigation (1)**
```
GET  /admin/dashboard/       Root redirect
```

---

## By Authentication

### Public (no auth) - 7 endpoints
```
GET  /
GET  /health
GET  /metrics
GET  /metrics/json
POST /api/v1/login
POST /api/v1/signup
POST /api/v1/generate-sql
POST /api/v1/fix-sql
POST /api/v1/explain-sql
```

### Viewer+ - 13 endpoints
```
POST /api/v1/sql/generate
POST /api/v1/sql/validate
POST /api/v1/sql/execute
GET  /api/v1/sql/history
POST /api/v1/feedback
GET  /api/v1/feedback/{id}
POST /api/v1/feedback/train  (analyst+ only)
```

### Admin+ - 30 endpoints
```
GET  /admin/config
POST /admin/config
POST /admin/approve-sql
GET  /admin/feedback-metrics
POST /admin/scheduled/create
GET  /admin/scheduled/list
DELETE /admin/scheduled/{id}
+ 26 dashboard CRUD endpoints
```

---

## By HTTP Method

| Method | Count | Examples |
|--------|-------|----------|
| GET | 20 | Health, metrics, history, list CRUD |
| POST | 29 | Auth, SQL ops, feedback, create/update CRUD |
| DELETE | 1 | Delete scheduled report/CRUD items |

---

## Request Examples

### Login
```bash
curl -X POST http://localhost:8000/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

Response:
```json
{
  "access_token": "eyJ0eXAi...",
  "token_type": "bearer",
  "user_id": "uuid-here",
  "email": "user@example.com"
}
```

### Public SQL Generation
```bash
curl -X POST http://localhost:8000/api/v1/generate-sql \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How many orders did we get this month?"
  }'
```

Response:
```json
{
  "sql": "SELECT COUNT(*) FROM orders WHERE DATE_TRUNC('month', created_at) = DATE_TRUNC('month', CURRENT_DATE);",
  "correlation_id": "uuid-here",
  "status": "success"
}
```

### Protected SQL Generation (with token)
```bash
curl -X POST http://localhost:8000/api/v1/sql/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "question": "Top 10 customers by revenue"
  }'
```

Response:
```json
{
  "sql": "SELECT customer_id, SUM(amount) as revenue FROM orders GROUP BY customer_id ORDER BY revenue DESC LIMIT 10;",
  "correlation_id": "uuid-here",
  "confidence": 0.95,
  "intent": {
    "query_type": "aggregation",
    "entities": ["customer_id", "amount"],
    "filters": [],
    "confidence": 0.95
  },
  "warnings": []
}
```

### Submit Feedback
```bash
curl -X POST http://localhost:8000/api/v1/feedback \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "query_id": "uuid-here",
    "rating": 5,
    "comment": "Excellent results!",
    "approved_for_training": true
  }'
```

### Get Health
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "providers_active": 1,
  "dependencies": {
    "postgres": true,
    "redis": true,
    "chroma": true
  },
  "features": {
    "circuit_breaker": true,
    "correlation_ids": true,
    "failover": true
  }
}
```

---

## Documentation

| URL | Purpose |
|-----|---------|
| `/docs` | Swagger UI (try endpoints) |
| `/redoc` | ReDoc (read-only docs) |
| `/openapi.json` | OpenAPI spec (JSON) |
| `/` | Root info with links |

---

## Rate Limits

| Tier | Limit | Applies To |
|------|-------|-----------|
| Public | 100/hour | Per IP address |
| Authenticated | 500/hour | Per user ID |
| Admin | 1000/hour | Per admin user |

**Exceeded:** Returns HTTP 429 (Too Many Requests)

---

## Response Format

All responses include:
- `correlation_id` (UUID for request tracing)
- `status` (success/error)
- Appropriate HTTP status code

---

## Authentication Header

All protected endpoints require:
```
Authorization: Bearer <JWT_TOKEN_FROM_LOGIN>
```

---

## Default Roles

- **New Users:** viewer (basic SQL access)
- **Manual Assignment:** analyst (analytics access), admin (full system)

---

## Key Files

- **Routes:** `app/api/v1/routes/*.py` (24 endpoints)
- **Admin:** `app/admin/` (26 dashboard endpoints)
- **Auth:** `app/api/dependencies.py` (JWT verification)
- **Main:** `app/main.py` (route registration)

---

## Detailed Docs

- **ALL_ENDPOINTS.md** - Complete endpoint reference
- **MASTER_ENDPOINT_INVENTORY.md** - Detailed inventory with status
- **COMPLETE_ENDPOINT_INVENTORY.md** - Original inventory document
- **AUTH_FIXED.md** - Authentication details
- **ROLES_AND_PERMISSIONS.md** - Access control
- **FRONTEND_INTEGRATION.md** - API usage guide
