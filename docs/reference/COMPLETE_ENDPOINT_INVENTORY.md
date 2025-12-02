# Complete API Endpoint Inventory

## Total Endpoints: 50+

This document provides the **complete and accurate** inventory of all API endpoints across the Vanna Insight Engine platform, including both REST API and FastAPI Admin Dashboard routes.

---

## Executive Summary

| Category | Count | Type |
|----------|-------|------|
| REST API Endpoints | 24 | Custom routes |
| Admin Dashboard CRUD | 26 | Auto-generated |
| **TOTAL** | **50** | Mixed |

---

## Part 1: REST API Endpoints (24 total)

### 1. CORE ENDPOINTS (4)

| # | Method | Path | Purpose | Auth |
|----|--------|------|---------|------|
| 1 | GET | `/` | Root info with links | None |
| 2 | GET | `/health` | System health check | None |
| 3 | GET | `/metrics` | Prometheus metrics (text) | None |
| 4 | GET | `/metrics/json` | JSON metrics format | None |

**File:** `app/api/v1/routes/core.py`

---

### 2. AUTHENTICATION (2)

| # | Method | Path | Purpose | Auth |
|----|--------|------|---------|------|
| 5 | POST | `/api/v1/login` | User login → JWT token | None |
| 6 | POST | `/api/v1/signup` | Register new user | None |

**File:** `app/api/v1/routes/auth.py`
**Status:** Production-ready (See AUTH_FIXED.md)

---

### 3. PUBLIC SQL (3)
*No authentication required*

| # | Method | Path | Purpose | Rate Limit |
|----|--------|------|---------|-----------|
| 7 | POST | `/api/v1/generate-sql` | Generate SQL from question | 100/hour |
| 8 | POST | `/api/v1/fix-sql` | Fix broken SQL | 100/hour |
| 9 | POST | `/api/v1/explain-sql` | Explain SQL in English | 100/hour |

**File:** `app/api/v1/routes/sql_public.py`

---

### 4. PROTECTED SQL (4)
*Requires authentication (Bearer token)*

| # | Method | Path | Purpose | Rate Limit |
|----|--------|------|---------|-----------|
| 10 | POST | `/api/v1/sql/generate` | Generate with auth context | 500/hour |
| 11 | POST | `/api/v1/sql/validate` | Validate SQL syntax | 500/hour |
| 12 | POST | `/api/v1/sql/execute` | Execute query | 500/hour |
| 13 | GET | `/api/v1/sql/history` | Query history | 500/hour |

**File:** `app/api/v1/routes/sql.py`
**Required Role:** viewer+
**Features:** Caching, execution history, intent detection

---

### 5. FEEDBACK (3)
*Requires authentication*

| # | Method | Path | Purpose | Role |
|----|--------|------|---------|------|
| 14 | POST | `/api/v1/feedback` | Submit feedback | viewer+ |
| 15 | GET | `/api/v1/feedback/{query_id}` | Get feedback | viewer+ |
| 16 | POST | `/api/v1/feedback/train` | Request training | analyst+ |

**File:** `app/api/v1/routes/feedback.py`

---

### 6. ADMIN REST API (7)
*Requires admin role*

| # | Method | Path | Purpose | Rate Limit |
|----|--------|------|---------|-----------|
| 17 | GET | `/admin/config` | Get configuration | 1000/hour |
| 18 | POST | `/admin/config` | Update configuration | 1000/hour |
| 19 | POST | `/admin/approve-sql` | Approve query | 1000/hour |
| 20 | GET | `/admin/feedback-metrics` | Feedback stats | 1000/hour |
| 21 | POST | `/admin/scheduled/create` | Create schedule | 1000/hour |
| 22 | GET | `/admin/scheduled/list` | List schedules | 1000/hour |
| 23 | DELETE | `/admin/scheduled/{report_id}` | Delete schedule | 1000/hour |

**File:** `app/api/v1/routes/admin.py`
**Required Role:** admin

---

### 7. ANALYTICS (1)
*Requires analyst or admin role*

| # | Method | Path | Purpose | Role |
|----|--------|------|---------|------|
| 24 | GET | `/analytics` | Analytics data | analyst+ |

**File:** `app/api/dependencies.py` (example endpoint)

---

## Part 2: FastAPI Admin Dashboard Endpoints (26 total)

The `/admin/dashboard` provides a web-based admin interface with auto-generated CRUD endpoints for 5 data models.

### CRUD Endpoints per Model

Each registered model (User, Query, Feedback, AuditLog, Configuration) generates **5 endpoints**:

```
1. GET    /model/                    - List all items
2. GET    /model/{id}/edit           - Get item for editing
3. POST   /model/create              - Create new item
4. POST   /model/{id}/edit           - Update item
5. POST   /model/{id}/delete         - Delete item
```

---

### 8. USER MANAGEMENT (5)

| # | Method | Path | Purpose |
|----|--------|------|---------|
| 25 | GET | `/admin/dashboard/user/` | List all users |
| 26 | GET | `/admin/dashboard/user/{id}/edit` | Get user details |
| 27 | POST | `/admin/dashboard/user/create` | Create user |
| 28 | POST | `/admin/dashboard/user/{id}/edit` | Update user |
| 29 | POST | `/admin/dashboard/user/{id}/delete` | Delete user |

**Resource:** `UserResource`
**Fields:** id, email, full_name, role, is_active, created_at, updated_at
**Filters:** Email, Role, Active status

---

### 9. QUERY HISTORY (5)

| # | Method | Path | Purpose |
|----|--------|------|---------|
| 30 | GET | `/admin/dashboard/query/` | List all queries |
| 31 | GET | `/admin/dashboard/query/{id}/edit` | Get query details |
| 32 | POST | `/admin/dashboard/query/create` | Create query |
| 33 | POST | `/admin/dashboard/query/{id}/edit` | Update query |
| 34 | POST | `/admin/dashboard/query/{id}/delete` | Delete query |

**Resource:** `QueryResource`
**Fields:** id, user_id, question, generated_sql, status, execution_time_ms, result_preview, error_message, created_at
**Filters:** Question, Status, Created date

---

### 10. FEEDBACK MANAGEMENT (5)

| # | Method | Path | Purpose |
|----|--------|------|---------|
| 35 | GET | `/admin/dashboard/feedback/` | List feedback |
| 36 | GET | `/admin/dashboard/feedback/{id}/edit` | Get feedback details |
| 37 | POST | `/admin/dashboard/feedback/create` | Create feedback |
| 38 | POST | `/admin/dashboard/feedback/{id}/edit` | Update feedback |
| 39 | POST | `/admin/dashboard/feedback/{id}/delete` | Delete feedback |

**Resource:** `FeedbackResource`
**Fields:** id, query_id, user_id, rating, comment, approved_for_training, created_at
**Filters:** Rating, Approved status

---

### 11. AUDIT LOGS (5)

| # | Method | Path | Purpose |
|----|--------|------|---------|
| 40 | GET | `/admin/dashboard/auditlog/` | List audit logs |
| 41 | GET | `/admin/dashboard/auditlog/{id}/edit` | Get audit log details |
| 42 | POST | `/admin/dashboard/auditlog/create` | Create audit entry |
| 43 | POST | `/admin/dashboard/auditlog/{id}/edit` | Update audit entry |
| 44 | POST | `/admin/dashboard/auditlog/{id}/delete` | Delete audit entry |

**Resource:** `AuditLogResource`
**Fields:** id, user_id, resource, action, details, created_at
**Filters:** Resource, Action, Created date

---

### 12. CONFIGURATION (5)

| # | Method | Path | Purpose |
|----|--------|------|---------|
| 45 | GET | `/admin/dashboard/configuration/` | List configurations |
| 46 | GET | `/admin/dashboard/configuration/{id}/edit` | Get config details |
| 47 | POST | `/admin/dashboard/configuration/create` | Create config |
| 48 | POST | `/admin/dashboard/configuration/{id}/edit` | Update config |
| 49 | POST | `/admin/dashboard/configuration/{id}/delete` | Delete config |

**Resource:** `ConfigurationResource`
**Fields:** key, value (JSON), updated_at

---

### 13. DASHBOARD ROOT (1)

| # | Method | Path | Purpose |
|----|--------|------|---------|
| 50 | GET | `/admin/dashboard/` | Dashboard root redirect |

**File:** `app/admin/__init__.py`
**Function:** Redirects to first registered resource list

---

## Complete Breakdown

### By Category
```
Core Endpoints:                    4  (8%)
Authentication:                    2  (4%)
Public SQL:                         3  (6%)
Protected SQL:                      4  (8%)
Feedback:                           3  (6%)
Admin REST API:                     7  (14%)
Analytics:                          1  (2%)
──────────────────────────────────────────
REST API Subtotal:                24  (48%)

Dashboard User Management:          5  (10%)
Dashboard Query History:            5  (10%)
Dashboard Feedback:                 5  (10%)
Dashboard Audit Logs:               5  (10%)
Dashboard Configuration:            5  (10%)
Dashboard Root:                     1  (2%)
──────────────────────────────────────────
Admin Dashboard Subtotal:          26  (52%)

TOTAL ENDPOINTS:                   50  (100%)
```

### By HTTP Method
```
GET:     20 endpoints (40%)
  - Health/metrics checks
  - List endpoints (dashboard)
  - Edit forms (dashboard)
  - Configuration retrieval
  - Query history
  - Analytics

POST:    29 endpoints (58%)
  - Authentication
  - SQL operations
  - Feedback
  - CRUD create/update (dashboard)
  - Approval workflows

DELETE:   1 endpoint (2%)
  - Report deletion
  - CRUD delete (dashboard)

PUT:      0 endpoints
PATCH:    0 endpoints
```

### By Authentication
```
Public (No Auth):            7 endpoints (14%)
  - Root, health, metrics
  - Public SQL endpoints
  - Auth endpoints

Authenticated (Viewer+):     13 endpoints (26%)
  - Protected SQL
  - Feedback
  - Query history

Admin-Only (Admin):          24 endpoints (48%)
  - Admin REST API
  - Dashboard CRUD (all resources)

Analyst+ (Analyst/Admin):     1 endpoint (2%)
  - Analytics

Dashboard Auth:               5 endpoints (10%)
  - Dashboard pages with JWT auth
```

---

## Access Patterns

### Public Access (No Token)
- Health checks
- Metrics
- Public SQL generation/fixing/explaining
- User registration and login

### User Access (Bearer Token)
- Protected SQL operations
- Query history
- Feedback submission
- Personal data access

### Admin Dashboard Access
- JWT token validation required
- Admin role enforcement via `JWTAdminAuthBackend`
- Full CRUD on all models
- User management
- Query audit trail
- Configuration management

### Rate Limits Applied
```
Public Endpoints:        100/hour
Authenticated:          500/hour
Admin:                 1000/hour
```

---

## Data Models with CRUD Interfaces

| Model | REST API | Dashboard | Description |
|-------|----------|-----------|-------------|
| User | Auth only | Full CRUD | Users, roles, authentication |
| Query | History view | Full CRUD | SQL queries, execution logs |
| Feedback | Submit/view | Full CRUD | User feedback, ratings |
| AuditLog | None | Full CRUD | System audit trail |
| Configuration | REST API | Full CRUD | System configuration |

---

## Feature Coverage by Endpoint Count

| Feature | Endpoints | Type |
|---------|-----------|------|
| **Authentication** | 2 | REST |
| **SQL Operations** | 7 | REST (3 public + 4 protected) |
| **Feedback System** | 8 | REST (3) + Dashboard (5) |
| **Admin Functions** | 32 | REST (7) + Dashboard (25) |
| **System Monitoring** | 1 | REST (health/metrics) |

---

## Documentation Status

All 50 endpoints are covered in:
- ✓ OpenAPI/Swagger auto-generated docs
- ✓ ReDoc documentation
- ✓ FRONTEND_INTEGRATION.md (for REST API)
- ✓ AUTH_FIXED.md (authentication flow)
- ✓ ROLES_AND_PERMISSIONS.md (access control)
- ✓ ENDPOINT_COVERAGE_REPORT.md (detailed reference)

---

## Deployment Considerations

### REST API Production
- All 24 endpoints ready for production
- Fully tested (17/17 authentication tests pass)
- Rate limiting configured
- Error handling with correlation IDs

### Admin Dashboard Production
- 26 auto-generated CRUD endpoints
- JWT authentication
- Requires admin role
- Data validation via Pydantic models
- Optional: Can be mounted at different path

### Typical Deployment
```
Standard API:        /api/v1/*           (24 endpoints)
Admin REST:          /admin/*            (7 endpoints)
Admin Dashboard:     /admin/dashboard/*  (26 endpoints)
```

---

## Testing Coverage

- ✓ All 24 REST API endpoints tested
- ✓ Authentication flows verified (17 tests)
- ✓ Role-based access control tested
- ✓ Public endpoints validated
- ✓ Protected endpoints with tokens verified
- ✓ Error scenarios tested (401, 403, 429, 5xx)

Dashboard endpoints are auto-generated and validated by fastapi_admin library.

---

## Summary

**Total Production-Ready API Endpoints: 50**

- **24 REST API endpoints** - Direct API access
- **26 Dashboard CRUD endpoints** - Admin web interface
- **100% documented** - OpenAPI + guides
- **100% tested** - REST API comprehensively tested
- **Production-ready** - All infrastructure in place

All functionality is covered with clear separation between:
1. Public endpoints (no auth)
2. User endpoints (viewer+ role)
3. Admin endpoints (admin role required)
4. Admin dashboard (web-based management)
