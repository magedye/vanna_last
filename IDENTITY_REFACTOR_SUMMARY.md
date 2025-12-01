# User Identity Refactor: Email to Username Migration

**Status:** Completed
**Date:** 2025-11-20
**Version:** 1.0

## Overview
Successfully refactored the Vanna Insight Engine authentication system to use simple alphanumeric usernames as the primary login identifier instead of strict email format. The system maintains database integrity with an Alembic migration while preserving all existing user data.

## Changes Made

### 1. Database Schema Changes

#### File: `app/db/models.py`
- **Removed:** `email` column (String(255), unique, indexed)
- **Added:** `username` column (String(255), unique, indexed) as primary authentication field
- **Added:** `recovery_email` column (String(255), nullable) for optional password recovery

#### Migration: `migrations/versions/002_rename_email_to_username.py`
Created a comprehensive Alembic migration that:
- Drops the `ix_users_email` unique index
- Renames the `email` column to `username`
- Creates a new `ix_users_username` unique index
- Adds a new nullable `recovery_email` column

**Reversibility:** The migration includes a full downgrade function to revert changes if needed.

### 2. Pydantic Schema Updates

#### File: `app/schemas.py`
- **LoginRequest:** Changed `email` → `username` (3-100 characters)
- **SignupRequest:** Added `username` field, added optional `recovery_email` field
- Both schemas maintain validation constraints and security requirements

### 3. Authentication Endpoints

#### File: `app/api/v1/routes/auth.py`
- **Updated Models:**
  - `LoginRequest`: username + password
  - `LoginResponse`: Returns username instead of email
  - `SignupRequest`: Accepts username, full_name, optional recovery_email
  - `SignupResponse`: Returns username

- **Updated Login Endpoint:**
  - Queries database by `User.username` instead of `User.email`
  - Error messages updated to "Invalid username or password"
  - Logs use username for audit trail

- **Updated Signup Endpoint:**
  - Checks for existing username instead of email
  - Creates users with username field
  - Stores optional recovery_email if provided

- **Code Cleanup:** Removed unused `SessionLocal` import (F401 flake8 fix)

### 4. Admin Authentication

#### File: `app/admin/auth.py`
- Updated `AdminPrincipal` dataclass: `email` field → `username`
- JWT authentication still uses user ID, but now retrieves username for principal

### 5. Admin UI Models (Tortoise ORM)

#### File: `app/admin/models.py`
- Changed `email` field to `username`
- Added `recovery_email` field (nullable)
- Updated `__str__` method to display username instead of email

#### File: `app/admin/resources.py`
- Search filter changed from "email" to "username"
- Updated field display to show username and recovery_email
- Admin dashboard now searchable by username

### 6. Data Access Layer

#### File: `app/db/repositories.py`
- **UserRepository.create():** Updated to accept `username` instead of `email`
- **UserRepository.get_by_email()** → **get_by_username():** New method signature
- Removed email-based lookups

### 7. Initialization Scripts

#### File: `scripts/init_system_db.py`
- Admin user now created with username "admin" (default, configurable via `INIT_ADMIN_USERNAME`)
- Added support for optional `INIT_ADMIN_RECOVERY_EMAIL` environment variable
- Updated query to use `filter_by(username=...)`

#### File: `scripts/init_project.py`
- Admin user created with username "admin"
- Sample test user created with username "testuser"
- Updated all database queries to use username field

#### File: `scripts/init_project_enhanced.py`
- Same changes as init_project.py for consistency

#### File: `scripts/generate_training_data.py`
- Sample users created with usernames like "sampleuser1", "sampleuser2", etc.
- Training data generation now uses username field

## Environment Variables

### New/Updated Variables
```bash
# Changed default from admin@example.com to admin
INIT_ADMIN_USERNAME=admin

# Existing variable, same behavior
INIT_ADMIN_PASSWORD=admin

# New variable for recovery email (optional)
INIT_ADMIN_RECOVERY_EMAIL=admin@example.com
```

## Database Migration Instructions

### For Running Migrations
```bash
# Inside running container
cd /home/mfadmin/new-vanna/vanna-engine
alembic upgrade head
```

### For Verification
The migration will:
1. Preserve all existing user data (existing emails become usernames)
2. Create the recovery_email column as NULL for existing users
3. Update indexes to support username-based queries
4. Maintain referential integrity for FK relationships

### Rollback (if needed)
```bash
alembic downgrade -1
```

## Breaking Changes

### API Changes
1. **Login endpoint** now expects `username` instead of `email`
   ```json
   // Old
   {"email": "admin@example.com", "password": "..."}
   
   // New
   {"username": "admin", "password": "..."}
   ```

2. **Signup endpoint** now requires `username`
   ```json
   // Old
   {"name": "...", "email": "...", "password": "..."}
   
   // New
   {"username": "...", "name": "...", "password": "...", "recovery_email": "..."}
   ```

3. **Login response** now contains `username` instead of `email`
   ```json
   // Old
   {"access_token": "...", "token_type": "bearer", "user_id": "...", "email": "..."}
   
   // New
   {"access_token": "...", "token_type": "bearer", "user_id": "...", "username": "..."}
   ```

### Admin Dashboard
- User search now filters by username instead of email
- Admin principal representation uses username

## Testing Recommendations

### Manual API Testing
```bash
# New login format
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'

# New signup format
curl -X POST "http://localhost:8000/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "name": "New User",
    "password": "securepassword123",
    "recovery_email": "newuser@example.com"
  }'
```

### Database Verification
```bash
# Connect to PostgreSQL and verify schema
SELECT column_name, data_type FROM information_schema.columns 
WHERE table_name = 'users';

# Should show:
# - username (VARCHAR)
# - recovery_email (VARCHAR, nullable)
# - No email column
```

## Security Considerations

✅ **Maintained:**
- Password hashing via bcrypt remains unchanged
- JWT token generation/verification unaffected
- RBAC and permission checks intact
- Audit logging preserved

✅ **Improved:**
- Username is more human-friendly (non-technical users can use simple names)
- Recovery email field enables future password reset via email
- No loss of security posture

## Files Modified (Summary)

| File | Changes |
|------|---------|
| `app/db/models.py` | email → username, added recovery_email |
| `migrations/versions/002_rename_email_to_username.py` | NEW migration |
| `app/schemas.py` | Updated LoginRequest, SignupRequest |
| `app/api/v1/routes/auth.py` | Updated auth endpoints, removed SessionLocal import |
| `app/admin/auth.py` | email → username in AdminPrincipal |
| `app/admin/models.py` | email → username, added recovery_email |
| `app/admin/resources.py` | Updated search filter and fields |
| `app/db/repositories.py` | get_by_email() → get_by_username() |
| `scripts/init_system_db.py` | Admin user creation uses username |
| `scripts/init_project.py` | Admin/test user creation uses username |
| `scripts/init_project_enhanced.py` | Admin/test user creation uses username |
| `scripts/generate_training_data.py` | Sample users use username field |

## Backward Compatibility

⚠️ **Not Backward Compatible:**
- Existing API clients expecting `email` in requests/responses will fail
- Database schema change requires migration
- Admin dashboard search by email will no longer work

✅ **Data Preservation:**
- All existing user records preserved
- Historical queries and feedback intact
- Audit logs maintained

## Future Enhancements

Possible follow-up work:
1. Implement password recovery via recovery_email
2. Add email validation for recovery_email field
3. Support email-based login alongside username (optional)
4. Add username validation regex constraints
5. Implement username change functionality

## Validation Checklist

- [x] Database model updated
- [x] Alembic migration created with upgrade/downgrade
- [x] Pydantic schemas updated
- [x] Authentication endpoints refactored
- [x] Admin layer updated
- [x] Repository methods updated
- [x] Initialization scripts updated
- [x] Unused imports removed (SessionLocal)
- [x] Error messages updated
- [x] Logging updated
- [x] All files searched for remaining email references

## Deployment Checklist

Before deploying to production:
1. **Backup database** - Create full backup of PostgreSQL
2. **Test migration** - Run migration on staging environment
3. **Verify schema** - Confirm username/recovery_email columns exist
4. **Test endpoints** - Verify login/signup work with new format
5. **Update clients** - Ensure frontend/SDKs updated for new request format
6. **Monitor logs** - Watch for authentication errors post-deploy
7. **Admin dashboard** - Test user search and display in admin UI

## Support & Troubleshooting

### Issue: "column "email" does not exist"
**Solution:** Migration not applied. Run: `alembic upgrade head`

### Issue: "Unique constraint violation on email"
**Solution:** This error should not occur if migration ran correctly. Check migration history.

### Issue: Login fails with valid username
**Solution:** Ensure frontend is sending `username` field (not `email`) in JSON payload.

### Issue: Old users can't login
**Solution:** Verify migration ran and old email values now exist in username column.
