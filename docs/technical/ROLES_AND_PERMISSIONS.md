# User Roles and Permissions

## Overview

The Vanna Insight Engine API supports **3 user roles** with different access levels and permissions:

```
┌─────────────────────────────────────────────────────────┐
│                    USER ROLES                           │
├─────────────────────────────────────────────────────────┤
│  1. VIEWER (default)     - Read-only SQL generation     │
│  2. ANALYST              - Enhanced permissions         │
│  3. ADMIN                - Full system access           │
└─────────────────────────────────────────────────────────┘
```

---

## Role Definitions

### 1. VIEWER (Default)
**Default role assigned to new users**

- **Can Access:**
  - ✓ Public SQL endpoints (no auth required)
  - ✓ Generate SQL from natural language questions
  - ✓ Fix and explain SQL queries
  - ✓ Validate SQL syntax
  - ✓ Execute queries (read-only)
  - ✓ View own query history and feedback
  - ✓ Submit feedback on generated queries

- **Cannot Access:**
  - ✗ Admin configuration endpoints
  - ✗ System monitoring and metrics (admin only)
  - ✗ Approve/reject SQL queries (analyst+ only)
  - ✗ View other users' data
  - ✗ Access scheduling features

- **Use Case:** Data analysts, business users who need to generate SQL but shouldn't modify system settings

**Example Endpoints:**
```bash
# VIEWER CAN access these:
POST /api/v1/sql/generate       # Generate SQL
POST /api/v1/sql/validate       # Validate SQL
GET /api/v1/sql/history         # View own queries
POST /api/v1/feedback           # Submit feedback
GET /api/v1/feedback/{id}       # View own feedback
```

---

### 2. ANALYST
**Enhanced permissions for data analysis work**

- **Can Access:**
  - ✓ All VIEWER permissions
  - ✓ View analytics and insights
  - ✓ Advanced query optimization
  - ✓ Query performance monitoring
  - ✓ Access to feedback metrics
  - ✓ Request query training/improvement
  - ✓ View system health status

- **Cannot Access:**
  - ✗ System configuration changes
  - ✗ User management
  - ✗ Approve/reject SQL (future enhancement)
  - ✗ Full admin dashboard

- **Use Case:** Senior data analysts, data engineers who need advanced features but shouldn't modify system config

**Example Endpoints:**
```bash
# ANALYST can access these (+ all VIEWER endpoints):
GET /admin/feedback-metrics     # View feedback statistics
GET /health                     # Check system health
POST /api/v1/feedback/train     # Request training
```

---

### 3. ADMIN
**Full system access and control**

- **Can Access:**
  - ✓ All VIEWER and ANALYST permissions
  - ✓ System configuration (get/update)
  - ✓ User management (future)
  - ✓ Approve/reject generated SQL
  - ✓ Create scheduled reports
  - ✓ View and manage audit logs
  - ✓ Configure system features
  - ✓ Access full admin dashboard
  - ✓ Monitor system performance
  - ✓ View all users' data and queries
  - ✓ Manage API keys and tokens

- **Cannot Access:**
  - (None - full system access)

- **Use Case:** System administrators, DevOps engineers, system operators

**Example Endpoints:**
```bash
# ADMIN can access these (+ all other endpoints):
GET /admin/config                    # Get configuration
POST /admin/config                   # Update settings
GET /admin/feedback-metrics          # Advanced metrics
POST /admin/approve-sql              # Approve queries
GET /admin/scheduled/list            # Manage schedules
POST /admin/scheduled/create         # Create schedules
DELETE /admin/scheduled/{report_id}  # Delete schedules
```

---

## Permission Matrix

| Feature | Viewer | Analyst | Admin |
|---------|--------|---------|-------|
| **Public Endpoints** | ✓ | ✓ | ✓ |
| Generate SQL | ✓ | ✓ | ✓ |
| Fix SQL | ✓ | ✓ | ✓ |
| Explain SQL | ✓ | ✓ | ✓ |
| Validate SQL | ✓ | ✓ | ✓ |
| View Own History | ✓ | ✓ | ✓ |
| Submit Feedback | ✓ | ✓ | ✓ |
| **Analyst Features** |  | | |
| View Analytics | ✗ | ✓ | ✓ |
| Feedback Metrics | ✗ | ✓ | ✓ |
| Request Training | ✗ | ✓ | ✓ |
| **Admin Features** |  | | |
| System Config | ✗ | ✗ | ✓ |
| User Management | ✗ | ✗ | ✓ |
| Approve Queries | ✗ | ✗ | ✓ |
| Audit Logs | ✗ | ✗ | ✓ |
| Scheduling | ✗ | ✗ | ✓ |
| View All Data | ✗ | ✗ | ✓ |

---

## How to Assign Roles

### At Signup
New users are assigned the default **VIEWER** role:
```python
# From app/api/v1/routes/auth.py
user = User(
    id=str(uuid.uuid4()),
    email=request.email,
    password_hash=hash_password(request.password),
    full_name=request.full_name,
    role="viewer",  # Default role
    is_active=True,
)
```

### Update User Role

**Option 1: Direct Database Update**
```bash
# Using SQLite (development)
sqlite3 vanna_db.db "UPDATE users SET role = 'admin' WHERE email = 'user@example.com';"

# Using PostgreSQL (production)
psql -U postgres -d vanna_db -c "UPDATE users SET role = 'admin' WHERE email = 'user@example.com';"
```

**Option 2: Admin Dashboard** (when available)
- Access `/admin/users` (future endpoint)
- Select user and change role dropdown
- Click Save

**Option 3: API Endpoint** (future implementation)
```bash
# Future endpoint to update user role
PUT /admin/users/{user_id}/role
{
  "role": "admin"
}
```

---

## Role-Based Access Control (RBAC)

### Checking Roles in Code

**Single Role Check:**
```python
from app.api.dependencies import get_current_admin_user

@router.get("/admin/config")
async def get_config(user: User = Depends(get_current_admin_user)):
    # Only admin users can access this
    return {"config": {...}}
```

**Multiple Role Check:**
```python
from app.api.dependencies import requires_role, get_current_user

@router.get("/analytics")
async def get_analytics(
    user: User = Depends(requires_role("analyst", "admin"))
):
    # Only analyst and admin users can access this
    return {"analytics": {...}}
```

**All Authenticated Users:**
```python
from app.api.dependencies import get_current_user

@router.get("/api/v1/sql/history")
async def get_history(user: User = Depends(get_current_user)):
    # Any authenticated user can access
    return {"queries": user.queries}
```

---

## Common Role Combinations

### Use Case 1: Small Team
```
- 1 ADMIN      (system operator)
- 2 ANALYST    (senior analysts)
- 5 VIEWER     (business users, report readers)
```

### Use Case 2: Enterprise
```
- 2-3 ADMIN      (operations team)
- 10-20 ANALYST  (data engineering/analytics team)
- 100+ VIEWER    (business users across departments)
```

### Use Case 3: Automation/Service Account
```
- 1 ADMIN (service account with limited scope)
  - Use for CI/CD pipelines
  - Scheduled jobs
  - System integrations
```

---

## Role Elevation and Revocation

### Elevate User to Analyst
```bash
sqlite3 vanna_db.db "UPDATE users SET role = 'analyst' WHERE email = 'user@example.com';"
```

### Elevate User to Admin
```bash
sqlite3 vanna_db.db "UPDATE users SET role = 'admin' WHERE email = 'user@example.com';"
```

### Revoke Admin Access
```bash
sqlite3 vanna_db.db "UPDATE users SET role = 'viewer' WHERE email = 'admin@example.com';"
```

### Deactivate User (Block Access)
```bash
sqlite3 vanna_db.db "UPDATE users SET is_active = FALSE WHERE email = 'user@example.com';"
```

---

## Available Dependency Functions

Located in `app/api/dependencies.py`:

| Function | Returns | Purpose |
|----------|---------|---------|
| `get_current_user` | User object | Any authenticated user |
| `get_current_admin_user` | User object | Admin-only users (raises 403 if not admin) |
| `requires_role(*roles)` | Function | Custom RBAC - specify allowed roles |
| `get_analyst_or_admin` | User object | Analyst or admin users (pre-configured) |
| `get_viewer_analyst_or_admin` | User object | All authenticated users (pre-configured) |

---

## API Endpoint Access Summary

### Public (No Auth)
```
GET  /                          # Root info
GET  /health                    # Health check
GET  /metrics                   # Prometheus metrics
POST /api/v1/generate-sql       # Generate SQL (public)
POST /api/v1/fix-sql            # Fix SQL (public)
POST /api/v1/explain-sql        # Explain SQL (public)
```

### Viewer+ (Any Authenticated User)
```
POST /api/v1/login              # Login
POST /api/v1/signup             # Register
POST /api/v1/sql/generate       # Generate SQL (auth)
POST /api/v1/sql/validate       # Validate SQL
POST /api/v1/sql/execute        # Execute SQL
GET  /api/v1/sql/history        # Query history
POST /api/v1/feedback           # Submit feedback
GET  /api/v1/feedback/{id}      # Get feedback
```

### Analyst+ (Analyst & Admin)
```
GET  /admin/feedback-metrics    # Feedback statistics
POST /api/v1/feedback/train     # Request training
```

### Admin Only
```
GET  /admin/config              # Get configuration
POST /admin/approve-sql         # Approve queries
GET  /admin/scheduled/list      # List schedules
POST /admin/scheduled/create    # Create schedule
```

---

## Security Notes

1. **Default Role is Viewer** - New users get minimal permissions by default
2. **No Role Enumeration** - Endpoint returns 403/401, not "user is viewer" message
3. **Database-Backed Roles** - Changes take effect on next login
4. **Token-Based Verification** - JWT token contains user_id, role verified from DB
5. **Audit Trail** - Admin actions logged to audit_logs table

---

## Future Enhancements

Planned role features:
- [ ] Custom role creation
- [ ] Permission templates
- [ ] Time-based role elevation (temporary admin)
- [ ] Role-based API key generation
- [ ] Organization/team-based RBAC
- [ ] Delegation of specific admin tasks
