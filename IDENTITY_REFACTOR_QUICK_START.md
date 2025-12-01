# Identity Refactor - Quick Start Guide

## What Changed
The authentication system now uses **username** instead of **email** as the primary login credential.

### Before
```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -d '{"email": "admin@example.com", "password": "admin"}'

# Signup
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -d '{"name": "John", "email": "john@example.com", "password": "..."}'
```

### After
```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -d '{"username": "admin", "password": "admin"}'

# Signup
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -d '{
    "username": "john",
    "name": "John Doe",
    "password": "...",
    "recovery_email": "john@example.com"
  }'
```

## Steps to Deploy

### 1. Apply Database Migration
```bash
cd /path/to/vanna-engine

# Inside running container or with active DB connection:
alembic upgrade head

# Verify:
# SELECT username, recovery_email FROM users LIMIT 1;
```

### 2. Update Your Frontend/Client
- Change login form field from `email` → `username`
- Change signup form to accept `username` instead of `email`
- Update API request payloads
- Update response handling to expect `username` in login response

### 3. Update Environment Variables (if needed)
```bash
# All of these are optional - defaults are shown:
INIT_ADMIN_USERNAME=admin
INIT_ADMIN_PASSWORD=admin
INIT_ADMIN_RECOVERY_EMAIL=admin@example.com
```

### 4. Test the Changes
```bash
# 1. Login with new format
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'

# Should return: {"access_token": "...", "token_type": "bearer", "user_id": "...", "username": "admin"}

# 2. Create new user with username
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "name": "Test User",
    "password": "testpass123"
  }'
```

## Affected Files (Reference)

| Component | Files Modified |
|-----------|----------------|
| Database | `app/db/models.py`, migration file |
| API Schemas | `app/schemas.py` |
| Auth Routes | `app/api/v1/routes/auth.py` |
| Admin Dashboard | `app/admin/auth.py`, `app/admin/models.py`, `app/admin/resources.py` |
| Data Layer | `app/db/repositories.py` |
| Initialization | `scripts/init_*.py` |

## Rollback (if needed)
```bash
alembic downgrade -1  # Revert to previous schema
# Old code will need to be restored from backup
```

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Login returns "Invalid username or password" | Ensure you're sending `username` field, not `email` |
| "column 'email' does not exist" error | Run `alembic upgrade head` to apply migration |
| Admin dashboard shows no users | Restart admin UI service after migration |
| Old users can't login | They should - their email became their username automatically via migration |

## Key Points

✅ **All existing user data is preserved** - Email addresses are automatically migrated to the username field

✅ **Recovery email is optional** - Users can log in with just username/password

✅ **Zero downtime deployment** possible if done carefully:
1. Deploy code
2. Run migration
3. Verify endpoints work
4. Update client applications

⚠️ **Usernames are case-sensitive** in the database queries

⚠️ **Client applications MUST be updated** to send `username` instead of `email`

## Default Admin User

After migration, the default admin user is:
- **Username:** `admin`
- **Password:** `admin` (change in production!)
- **Recovery Email:** Optional, can be set via `INIT_ADMIN_RECOVERY_EMAIL` env var

## Next Steps

1. **Run the migration** - Apply alembic upgrade
2. **Update frontend** - Change login/signup forms to use username
3. **Test thoroughly** - Especially login and signup flows
4. **Update documentation** - Ensure all API docs reference username, not email
5. **Monitor logs** - Watch for auth-related errors after deployment
6. **Gradual rollout** - Consider rolling out to users gradually if possible

## Questions?

Refer to the full summary: `IDENTITY_REFACTOR_SUMMARY.md`
