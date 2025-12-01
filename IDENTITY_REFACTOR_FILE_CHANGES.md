# Identity Refactor - File-by-File Changes

## 1. Core Database Model

### File: `app/db/models.py`
**Change:** Line 23 - Replace email column with username and add recovery_email

```python
# BEFORE
email = Column(String(255), unique=True, nullable=False, index=True)

# AFTER
username = Column(String(255), unique=True, nullable=False, index=True)
password_hash = Column(String(255), nullable=False)
full_name = Column(String(255))
role = Column(String(50), default="viewer")
is_active = Column(Boolean, default=True)
recovery_email = Column(String(255), nullable=True)  # NEW
```

---

## 2. Database Migration

### File: `migrations/versions/002_rename_email_to_username.py` (NEW FILE)
**Content:** Complete Alembic migration with upgrade and downgrade

Key operations:
- Drop `ix_users_email` index
- Rename `email` column to `username`
- Create `ix_users_username` index
- Add `recovery_email` column

---

## 3. API Schemas

### File: `app/schemas.py`

#### LoginRequest (Lines 132-143)
```python
# BEFORE
class LoginRequest(BaseModel):
    email: constr(strip_whitespace=True, min_length=5, max_length=100)
    password: constr(min_length=8, max_length=100)

# AFTER
class LoginRequest(BaseModel):
    username: constr(strip_whitespace=True, min_length=3, max_length=100)
    password: constr(min_length=8, max_length=100)
```

#### SignupRequest (Lines 158-173)
```python
# BEFORE
class SignupRequest(BaseModel):
    name: constr(...)
    email: constr(...)
    password: constr(...)

# AFTER
class SignupRequest(BaseModel):
    username: constr(...)
    name: constr(...)
    password: constr(...)
    recovery_email: Optional[constr(...)] = None
```

---

## 4. Authentication Routes

### File: `app/api/v1/routes/auth.py`

#### Class Definitions (Lines 19-50)
```python
# LoginRequest - username instead of email
# LoginResponse - username instead of email
# SignupRequest - username first, added recovery_email
# SignupResponse - username instead of email
```

#### Login Endpoint (Lines 72-117)
```python
# BEFORE
user = db.query(User).filter(User.email == request.email).first()
raise HTTPException(..., detail="Invalid email or password")
logger.info(f"User {user.email} logged in successfully")
return LoginResponse(access_token=..., email=user.email)

# AFTER
user = db.query(User).filter(User.username == request.username).first()
raise HTTPException(..., detail="Invalid username or password")
logger.info(f"User {user.username} logged in successfully")
return LoginResponse(access_token=..., username=user.username)
```

#### Signup Endpoint (Lines 120-166)
```python
# BEFORE
existing_user = db.query(User).filter(User.email == request.email).first()
if existing_user: raise HTTPException(..., detail="Email already registered")
user = User(email=request.email, ...)

# AFTER
existing_user = db.query(User).filter(User.username == request.username).first()
if existing_user: raise HTTPException(..., detail="Username already registered")
user = User(username=request.username, recovery_email=request.recovery_email, ...)
```

#### Imports
```python
# BEFORE
from app.db.database import SessionLocal  # REMOVED - unused import (F401)

# AFTER
# SessionLocal import removed
```

---

## 5. Admin Authentication

### File: `app/admin/auth.py`

#### AdminPrincipal Dataclass (Lines 22-29)
```python
# BEFORE
@dataclass
class AdminPrincipal:
    id: str
    email: str
    full_name: Optional[str]
    role: str

# AFTER
@dataclass
class AdminPrincipal:
    id: str
    username: str
    full_name: Optional[str]
    role: str
```

#### Authentication Method (Lines 90-95)
```python
# BEFORE
return AdminPrincipal(id=user.id, email=user.email, ...)

# AFTER
return AdminPrincipal(id=user.id, username=user.username, ...)
```

---

## 6. Admin ORM Models

### File: `app/admin/models.py`

#### User Model (Lines 7-23)
```python
# BEFORE
class User(Model):
    id = fields.CharField(pk=True, max_length=36)
    email = fields.CharField(max_length=255, unique=True)
    ...
    def __str__(self): return self.full_name or self.email

# AFTER
class User(Model):
    id = fields.CharField(pk=True, max_length=36)
    username = fields.CharField(max_length=255, unique=True)
    ...
    recovery_email = fields.CharField(max_length=255, null=True)
    ...
    def __str__(self): return self.full_name or self.username
```

---

## 7. Admin Resources

### File: `app/admin/resources.py`

#### UserResource (Lines 11-28)
```python
# BEFORE
filters = [
    admin_filters.Search(name="email", label="Email", ...),
    ...
]
fields = [
    "id",
    "email",
    Field("full_name", label="Full Name"),
    ...
]

# AFTER
filters = [
    admin_filters.Search(name="username", label="Username", ...),
    ...
]
fields = [
    "id",
    "username",
    Field("full_name", label="Full Name"),
    Field("recovery_email", label="Recovery Email"),
    ...
]
```

---

## 8. Repository Layer

### File: `app/db/repositories.py`

#### UserRepository Methods
```python
# BEFORE
def create(self, email: str, ...):
    user = User(email=email, ...)
    
def get_by_email(self, email: str):
    return self.db.query(User).filter(User.email == email).first()

# AFTER
def create(self, username: str, ...):
    user = User(username=username, ...)
    
def get_by_username(self, username: str):
    return self.db.query(User).filter(User.username == username).first()
```

---

## 9. System Database Initialization

### File: `scripts/init_system_db.py`

#### Admin User Creation (Lines 344-401)
```python
# BEFORE
admin_email = os.getenv("INIT_ADMIN_USERNAME", "admin@example.com")
existing_admin = self.db.query(User).filter_by(email=admin_email).first()
...
admin_user = User(email=admin_email, ...)

# AFTER
admin_username = os.getenv("INIT_ADMIN_USERNAME", "admin")
admin_recovery_email = os.getenv("INIT_ADMIN_RECOVERY_EMAIL", None)
existing_admin = self.db.query(User).filter_by(username=admin_username).first()
...
admin_user = User(username=admin_username, recovery_email=admin_recovery_email, ...)
```

---

## 10. Project Initialization Scripts

### Files: `scripts/init_project.py` and `scripts/init_project_enhanced.py`

#### Admin User Creation (Lines 273-297)
```python
# BEFORE
admin = self.db.query(User).filter_by(email="admin@example.com").first()
admin_user = User(email="admin@example.com", ...)

# AFTER
admin = self.db.query(User).filter_by(username="admin").first()
admin_user = User(username="admin", ...)
```

#### Sample User Creation (Lines 331-365)
```python
# BEFORE
existing_admin = self.db.query(User).filter_by(email=admin_username).first()
admin_user = User(email=admin_username, ...)
existing_user = self.db.query(User).filter_by(email="test@example.com").first()
sample_user = User(email="test@example.com", ...)

# AFTER
existing_admin = self.db.query(User).filter_by(username=admin_username).first()
admin_user = User(username=admin_username, ...)
existing_user = self.db.query(User).filter_by(username="testuser").first()
sample_user = User(username="testuser", ...)
```

---

## 11. Training Data Generation

### File: `scripts/generate_training_data.py`

#### Sample User Creation (Lines 23-42)
```python
# BEFORE
user = User(
    id=str(uuid.uuid4()),
    email=f"user{i+1}@example.com",
    ...
)

# AFTER
user = User(
    id=str(uuid.uuid4()),
    username=f"sampleuser{i+1}",
    ...
)
```

---

## Summary of Changes by Type

### Renames
- `email` field → `username` field (in User model)
- `get_by_email()` → `get_by_username()` (in UserRepository)
- `AdminPrincipal.email` → `AdminPrincipal.username`

### Additions
- `recovery_email` column (nullable) in User model
- `recovery_email` field in Tortoise User model
- `recovery_email` parameter in SignupRequest schema
- `recovery_email` field in admin User resource
- `INIT_ADMIN_RECOVERY_EMAIL` environment variable support

### Deletions
- `SessionLocal` import from `app/api/v1/routes/auth.py` (unused)

### Database Operations
- New Alembic migration (version 002)
- Column rename with index updates
- New nullable column addition

### Error Messages
- "Invalid email or password" → "Invalid username or password"
- "Email already registered" → "Username already registered"

### Default Values
- Admin user default changed from "admin@example.com" to "admin"
- Test user default changed from "test@example.com" to "testuser"
- Sample user defaults changed from "user1@example.com" to "sampleuser1", etc.

---

## Lines of Code Changed

| File | Lines Changed | Type |
|------|--------------|------|
| app/db/models.py | 1 | Model update |
| migrations/versions/002_*.py | 60 | NEW file |
| app/schemas.py | 20 | Schema update |
| app/api/v1/routes/auth.py | 45 | Route update |
| app/admin/auth.py | 4 | Admin auth |
| app/admin/models.py | 4 | Admin model |
| app/admin/resources.py | 8 | Admin resources |
| app/db/repositories.py | 10 | Repository |
| scripts/init_system_db.py | 12 | Init script |
| scripts/init_project.py | 18 | Init script |
| scripts/init_project_enhanced.py | 18 | Init script |
| scripts/generate_training_data.py | 2 | Data generation |

**Total: ~202 lines of code across 12 files**
