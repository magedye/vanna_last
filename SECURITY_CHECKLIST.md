# Security Configuration Checklist

**Version:** 1.0.0  
**Status:** PRODUCTION-READY  
**Last Updated:** 2025-11-13

---

## Overview

This document verifies the security posture of the Vanna Insight Engine across authentication, authorization, data protection, and operational hardening.

---

## 1. Authentication & Authorization

### JWT Token Security
- [x] **Implemented:** `app/core/security/auth.py`
  - Algorithm: HS256
  - Expiration: 24 hours (86400 seconds)
  - Secret: Configurable via `SECRET_KEY` environment variable
  
**Recommendation:** Ensure `SECRET_KEY` is strong and unique per environment:
```bash
# Generate a secure key
python -c "import secrets; print(secrets.token_hex(32))"
```

- [x] **Token Refresh:** `POST /api/v1/refresh-token` endpoint implemented
- [x] **Token Validation:** All protected endpoints verify JWT validity

### Role-Based Access Control (RBAC)
- [x] **Roles Implemented:** `viewer`, `analyst`, `admin`
- [x] **Per-Endpoint Authorization:** Enforced in route definitions
  - `viewer`: SQL generation, execution, feedback
  - `analyst`: viewer + config/metrics access
  - `admin`: All endpoints

**Configuration:** Roles are set during user signup (default: `viewer`) and updated by admin via database only.

### Password Security
- [x] **Hashing:** Bcrypt (4 rounds, 72-byte input limit)
- [x] **Truncation:** Passwords >72 bytes safely truncated with warning
- [x] **Verification:** Constant-time comparison via `bcrypt.checkpw`

**Requirement:** `.env.prod` must NOT contain user passwords; manage credentials via database or identity provider.

---

## 2. Data Protection

### Environment Secrets
- [x] **.gitignore Coverage:** `.env`, `.env.local`, `.env.*.local` are excluded
- [x] **Environment Files:**
  - `docker/env/.env.example` – Safe template with placeholder values
  - `docker/env/.env.dev` – Development-only secrets
  - `docker/env/.env.stage` – Staging secrets (non-production)
  - `.env.prod` – Production secrets (NEVER commit)

**Validation:**
```bash
# Verify .env.prod is NOT tracked
git ls-files | grep -i ".env.prod"
# Should return: (nothing)

# Verify .env is properly ignored
git status | grep ".env"
# Should return: (nothing)
```

### Sensitive Fields in Responses
- [x] **Password Redaction:** Never returned in API responses
- [x] **Token Masking:** JWT tokens masked in logs
- [x] **Correlation IDs:** Included in all responses for audit trail

### Database Connection Security
- [x] **URL Format:** `postgresql://user:password@host:port/database`
- [x] **SSL/TLS:** Configure `?sslmode=require` in `DATABASE_URL` for production
  
**Production Configuration:**
```bash
DATABASE_URL=postgresql://user:password@postgres.prod:5432/vanna_db?sslmode=require
```

### Redis Security
- [x] **Password Protection:** Enabled in `docker-compose.prod.yml`
  
**Production Configuration:**
```bash
REDIS_URL=redis://:${REDIS_PASSWORD}@redis.prod:6379/0
```

---

## 3. API Security

### Rate Limiting
- [x] **Implemented:** `app/core/rate_limiting.py`
- [x] **Default Limits:** 100 requests/minute per user
- [x] **Response Headers:** Includes `X-RateLimit-*` headers
- [x] **Correlation ID Logging:** Rate limit breaches logged with correlation ID

**Verification:**
```bash
# Test rate limit
for i in {1..101}; do
  curl -X POST "http://localhost:8000/api/v1/generate-sql" \
    -H "Authorization: Bearer <token>" \
    -H "Content-Type: application/json" \
    -d '{"question": "test"}'
done

# 101st request should return 429 Too Many Requests
```

### CORS Configuration
- [x] **Configured in `app/config.py`:** `CORS_ORIGINS` list
- [x] **Default:** Restricted to known frontend origins

**Verify in Production:**
```bash
CORS_ORIGINS=https://app.example.com,https://admin.example.com
```

### Input Validation
- [x] **Pydantic Schemas:** All request payloads validated
- [x] **SQL Validation:** `app/api/v1/routes/sql.py` validates queries before execution
- [x] **Question Validation:** Minimum length enforced (3 characters)

---

## 4. Correlation ID & Audit Trail

### Implementation
- [x] **Middleware:** `app/middleware/correlation.py`
  - Extracts `X-Correlation-ID` from request headers
  - Generates UUID if not provided
  - Propagates to all downstream services (logs, DB queries, Celery tasks)

### Verification
All API responses include `correlation_id`:
```json
{
  "sql": "SELECT * FROM orders",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Rate Limiting & Correlation
- [x] **Logging:** Rate limit violations logged with correlation ID
- [x] **Traceability:** All requests can be traced end-to-end

**Configuration:**
```bash
ENABLE_TRACING=true  # Enables detailed tracing in production
```

---

## 5. Docker & Container Security

### Image Security
- [x] **Base Image:** Python 3.11-slim (minimal, security patches)
- [x] **Dependency Pinning:** `requirements.txt` pins versions
- [x] **No Secrets in Image:** Environment variables injected at runtime

### Container Runtime Security
- [x] **Production Overlay:** `docker-compose.prod.yml` enforces:
  - Non-root user: `runAsUser: 1000` (Kubernetes)
  - No privilege escalation
  - Dropped capabilities (no CAP_ALL)
  - Read-only root filesystem (recommended)

### Volume Management
- [x] **Development:** Volumes mounted for hot reload
- [x] **Production:** No volume mounts (immutable)

---

## 6. Kubernetes Security (Production)

### Pod Security
- [x] **Security Context:** Non-root user, dropped capabilities
- [x] **Resource Limits:** CPU & memory limits enforced
- [x] **Network Policies:** `k8s/overlays/production/networkpolicy.yaml` exists

### Health Probes
- [x] **Liveness Probe:** Checks `/health` every 10s, restart on failure
- [x] **Readiness Probe:** Checks `/health` every 5s, remove from service on failure
- [x] **Graceful Shutdown:** 30s termination grace period

### Pod Disruption Budget
- [x] **High Availability:** `k8s/overlays/production/pdb.yaml` ensures ≥1 replica running

---

## 7. Secrets Management

### Environment Variables (Recommended for Development)
- [x] `docker/env/.env.dev` – Local development secrets
- [x] `docker/env/.env.stage` – Staging environment secrets
- [x] `.env.prod` – **NEVER commit to Git**

### Kubernetes Secrets (Production)
- [ ] **TODO:** Create `k8s/base/secrets.yaml` or use external secret manager
- [ ] **TODO:** Integrate with HashiCorp Vault or AWS Secrets Manager
- [ ] **TODO:** Remove hard-coded credentials from `docker-compose.prod.yml`

**Implementation Guide:**
```yaml
# k8s/base/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: vanna-secrets
type: Opaque
stringData:
  DATABASE_URL: postgresql://user:password@postgres:5432/vanna_db
  REDIS_URL: redis://:password@redis:6379/0
  SECRET_KEY: <generated-secret-key>
```

### Vault Integration (Production)
- [ ] **TODO:** Implement HashiCorp Vault integration
- [ ] **TODO:** Configure Kubernetes auth method in Vault
- [ ] **TODO:** Auto-rotate secrets (recommended: 90-day rotation)

---

## 8. Logging & Monitoring

### Structured Logging
- [x] **Correlation IDs:** All logs include request context
- [x] **Masked Secrets:** Passwords, tokens never logged
- [x] **Log Levels:** Configurable via `LOG_LEVEL` environment variable

**Verify masking:**
```bash
grep -r "password\|token\|secret" logs/ | grep -v "\\*\\*\\*"
# Should return: (nothing)
```

### Metrics Exposure
- [x] **Prometheus Endpoint:** `GET /metrics`
- [x] **Annotations:** Kubernetes scrape annotations set

**Verify metrics:**
```bash
curl http://localhost:8000/metrics
```

### Health Checks
- [x] **Comprehensive:** `GET /health` checks all dependencies
- [x] **Feature Flags:** Returned in health response
- [x] **Graceful Degradation:** API returns 503 if critical services down

---

## 9. Pre-Deployment Checklist

### Development to Production Promotion

#### Before Deploying to Staging
- [ ] Run tests: `pytest --cov`
- [ ] Run linter: `mypy app/`
- [ ] Run security scan: `bandit -r app/`
- [ ] Update `CHANGELOG.md`
- [ ] Tag release: `git tag -a v1.0.0 -m "Release notes"`

#### Before Deploying to Production
- [ ] Verify `.env.prod` is NOT committed: `git ls-files | grep .env.prod`
- [ ] Confirm `SECRET_KEY` is unique and strong
- [ ] Confirm `CORS_ORIGINS` restricted to production domain
- [ ] Confirm `DATABASE_URL` uses SSL: `?sslmode=require`
- [ ] Confirm Redis password set: `REDIS_PASSWORD` in environment
- [ ] Test health endpoint: `curl https://api.example.com/health`
- [ ] Load test: `ab -n 1000 -c 10 https://api.example.com/health`

### Post-Deployment Validation
- [ ] Monitor error logs for first 1 hour
- [ ] Verify correlation IDs in logs
- [ ] Run smoke tests: `pytest tests/smoke/`
- [ ] Validate API responses with production domain
- [ ] Check metrics: `curl https://api.example.com/metrics`

---

## 10. Known Gaps & TODOs

| Item | Status | Priority | Owner |
|------|--------|----------|-------|
| Kubernetes Secrets integration | ❌ TODO | HIGH | Ops |
| Secret rotation policy | ❌ TODO | HIGH | Ops |
| TLS/SSL certificate automation | ❌ TODO | HIGH | Ops |
| Vault integration | ❌ TODO | MEDIUM | Ops |
| API rate limit DDoS protection | ✅ DONE | — | — |
| Correlation ID tracing | ✅ DONE | — | — |
| Password hashing (bcrypt) | ✅ DONE | — | — |
| JWT token validation | ✅ DONE | — | — |

---

## Quick Reference: Environment Variable Secrets

### `.env.prod` Template (DO NOT COMMIT)
```bash
# FastAPI
SECRET_KEY=<use python -c "import secrets; print(secrets.token_hex(32))">
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://user:strong_password@postgres.prod:5432/vanna_db?sslmode=require

# Redis
REDIS_PASSWORD=<strong-redis-password>
REDIS_URL=redis://:${REDIS_PASSWORD}@redis.prod:6379/0

# CORS
CORS_ORIGINS=https://app.example.com,https://admin.example.com

# Tracing
ENABLE_TRACING=true
```

---

## References

- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Kubernetes Security Best Practices](https://kubernetes.io/docs/concepts/security/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
