# Configuration Quick Reference

**TL;DR of what to edit before running `./run.sh`**

---

## The Absolute Minimum

### For Development:

```bash
cp docker/env/.env.example docker/env/.env.dev
nano docker/env/.env.dev
# Edit: OPENAI_API_KEY, JWT_SECRET
```

### For Staging:

```bash
cp docker/env/.env.example docker/env/.env.stage
nano docker/env/.env.stage
# Edit: OPENAI_API_KEY, JWT_SECRET, DATABASE_URL, POSTGRES_PASSWORD, REDIS_URL
```

### For Production (🔴 CRITICAL):

```bash
cp .env.example .env.prod
nano .env.prod
# Edit ALL the variables marked 🔴 below
```

---

## Variable Checklist by Environment

### Development (.env.dev)

```
🟡 REQUIRED:
  OPENAI_API_KEY = sk-your-dev-key

🟡 REQUIRED:
  JWT_SECRET = any-random-string-32-chars-minimum

✅ USE DEFAULTS:
  PORT = 8000
  DEBUG = true
  ENVIRONMENT = development
  DATABASE_URL = postgresql://postgres:postgres@postgres:5432/vanna_db
  REDIS_URL = redis://redis:6379/0
```

### Staging (.env.stage)

```
🟡 REQUIRED:
  PORT = available-port
  OPENAI_API_KEY = sk-your-staging-key
  JWT_SECRET = random-32-chars
  DATABASE_URL = postgresql://user:pass@your-staging-db:5432/vanna_db
  POSTGRES_PASSWORD = your-staging-password
  REDIS_URL = redis://your-staging-redis:6379/0

✅ USE DEFAULTS:
  DEBUG = false
  ENVIRONMENT = staging
  LOG_LEVEL = INFO
```

### Production (.env.prod) – 🔴 DO NOT SKIP

```
🔴 CHANGE THESE (Security Critical):
  OPENAI_API_KEY = sk-proj-your-actual-key-from-openai
  JWT_SECRET = $(openssl rand -hex 32)
  DATABASE_URL = postgresql://prod-user:strong-pass@your-prod-db.com:5432/vanna_db
  POSTGRES_PASSWORD = YourStrongDatabasePassword123!
  REDIS_URL = redis://your-prod-redis.com:6379/0

🔴 CHANGE THESE (Environment Config):
  ENVIRONMENT = production
  DEBUG = false
  LOG_LEVEL = WARN

⚠️  CHANGE IF NEEDED:
  PORT = 8000 (or 9000 if 8000 in use)

✅ LEAVE AS IS:
  POSTGRES_PORT = 5432
  REDIS_PORT = 6379
  CHROMA_PORT = 8001
  FLOWER_PORT = 5555
```

---

## 60-Second Setup

```bash
# 1. Copy template
cp .env.example .env.prod

# 2. Open editor
nano .env.prod

# 3. Find and replace these lines:
#    OLD                              NEW
#    OPENAI_API_KEY=sk-xxx            OPENAI_API_KEY=sk-your-actual-key
#    JWT_SECRET=change-me             JWT_SECRET=<generate with: openssl rand -hex 32>
#    DATABASE_URL=localhost           DATABASE_URL=<your-db-host>
#    POSTGRES_PASSWORD=change-me      POSTGRES_PASSWORD=<strong-password>
#    REDIS_URL=localhost              REDIS_URL=<your-redis-host>

# 4. Save (Ctrl+X, Y, Enter in nano)

# 5. Verify
grep "🔴" .env.prod  # Should see your changes

# 6. Deploy
./run.sh --env prod
```

---

## What NOT to Edit

**Never change these** (internal Docker ports):

```env
POSTGRES_PORT=5432        ← Keep!
REDIS_PORT=6379           ← Keep!
CHROMA_PORT=8001          ← Keep!
FLOWER_PORT=5555          ← Keep!
```

These ports are for container-to-container communication. Only change `PORT=8000` for the main API.

---

## Generate Required Secrets

### JWT_SECRET (random 32+ chars):

```bash
# Copy and run ONE of these:
openssl rand -hex 32                              # Linux/macOS
python3 -c "import secrets; print(secrets.token_hex(32))"  # Python
```

### POSTGRES_PASSWORD (strong password):

```bash
# Copy and run ONE of these:
openssl rand -base64 16                           # Linux/macOS
python3 -c "import secrets; print(secrets.token_urlsafe(16))"  # Python
```

### OPENAI_API_KEY:

Get from: https://platform.openai.com/api-keys

Format: `sk-proj-xxx...` or `sk-xxx...`

---

## Common Mistakes to Avoid

❌ **WRONG:**
```env
DATABASE_URL=postgresql://localhost:5432/vanna_db
REDIS_URL=redis://localhost:6379/0
```

✅ **RIGHT (for containers):**
```env
DATABASE_URL=postgresql://postgres:5432/vanna_db
REDIS_URL=redis://redis:6379/0
```

**Why?** Inside Docker containers, `localhost` means the container itself. Use service names like `postgres` and `redis`.

---

❌ **WRONG:**
```env
OPENAI_API_KEY=my-test-key
JWT_SECRET=abc123
```

✅ **RIGHT:**
```env
OPENAI_API_KEY=sk-proj-abc123xyz...
JWT_SECRET=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

**Why?** OpenAI keys must start with `sk-`. JWT secrets must be min 32 chars.

---

❌ **WRONG:**
```env
ENVIRONMENT=prod
DEBUG=yes
```

✅ **RIGHT:**
```env
ENVIRONMENT=production
DEBUG=false
```

**Why?** Use exact values. The code expects `production` and boolean `false`.

---

## File Locations

| Environment | Location | Template | Create Command |
|-------------|----------|----------|-----------------|
| Development | `docker/env/.env.dev` | `docker/env/.env.example` | `cp docker/env/.env.example docker/env/.env.dev` |
| Staging | `docker/env/.env.stage` | `docker/env/.env.example` | `cp docker/env/.env.example docker/env/.env.stage` |
| Production | `.env.prod` | `.env.example` | `cp .env.example .env.prod` |

---

## Next Steps

1. **Edit the file**: `nano .env.prod`
2. **Change the variables** marked with 🔴
3. **Save the file** (Ctrl+X, Y, Enter)
4. **Run**: `./run.sh --env prod`
5. **Verify**: `curl http://localhost:8000/health`

---

**For more details, see:**
- `CONFIGURATION_CHECKLIST.md` – Step-by-step guide
- `STARTUP_GUIDE.md` – Complete documentation
- `QUICK_STARTUP.md` – Production deployment guide
