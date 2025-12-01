# Secrets Management Guide

**Version:** 1.0.0  
**Status:** Production-Ready  
**Owner:** DevOps / Security

---

## Overview

This guide covers credential management across development, staging, and production environments for the Vanna Insight Engine.

---

## Quick Reference

| Environment | Storage | Rotation | Access Control |
|-------------|---------|----------|-----------------|
| **Development** | `docker/env/.env.dev` (local) | Manual | ✓ Not committed |
| **Staging** | `docker/env/.env.stage` + Secrets Manager | 180 days | ✓ Limited team |
| **Production** | Kubernetes Secrets / Vault | 90 days | ✓ RBAC + encryption |

---

## Development Environment

### Setup

1. **Copy template** (committed to Git):
```bash
cp docker/env/.env.example docker/env/.env.dev
```

2. **Add development secrets** (NOT committed):
```bash
# Edit docker/env/.env.dev and add:
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
DATABASE_URL=postgresql://dev_user:dev_password@localhost:5432/vanna_dev
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=sk-...
VANNA_API_KEY=...
```

3. **Load in shell**:
```bash
export $(cat docker/env/.env.dev | xargs)
```

4. **Verify .gitignore**:
```bash
git check-ignore docker/env/.env.dev
# Should NOT be ignored (example file only)

git check-ignore .env
# Should be ignored (actual secrets)
```

### Secrets in Development
- ✅ Use weak/test credentials (never production values)
- ✅ Store in `.env` (in `.gitignore`)
- ✅ Use `docker/env/.env.example` as template (in Git)
- ✅ Rotate quarterly or when developer leaves team

---

## Staging Environment

### Setup (Cloud Secrets Manager)

#### Option A: AWS Secrets Manager

```bash
# Create secret in AWS
aws secretsmanager create-secret \
  --name vanna/staging/secrets \
  --secret-string '{
    "DATABASE_URL": "postgresql://...",
    "REDIS_URL": "redis://...",
    "SECRET_KEY": "...",
    "OPENAI_API_KEY": "sk-..."
  }'

# Inject into Docker Compose
export $(aws secretsmanager get-secret-value \
  --secret-id vanna/staging/secrets \
  --query SecretString \
  --output text | jq -r 'to_entries[] | "\(.key)=\(.value)"')

docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

#### Option B: Google Cloud Secret Manager

```bash
# Create secret
echo -n '{"SECRET_KEY":"...","DATABASE_URL":"..."}' | \
  gcloud secrets create vanna-staging-secrets --data-file=-

# Retrieve for use
gcloud secrets versions access latest --secret=vanna-staging-secrets | \
  jq -r 'to_entries[] | "\(.key)=\(.value)"' > docker/env/.env.stage
```

#### Option C: Azure Key Vault

```bash
# Create secrets
az keyvault secret set \
  --vault-name vanna-staging \
  --name DATABASE-URL \
  --value "postgresql://..."

# Retrieve
az keyvault secret show \
  --vault-name vanna-staging \
  --name DATABASE-URL \
  --query value -o tsv
```

### Rotation Policy

- **Frequency:** Every 180 days (6 months)
- **Manual Process:**
  1. Generate new secret in cloud vault
  2. Update applications to read new value
  3. Delete old secret after verification
- **Automated (Recommended):** Use Lambda/Cloud Function for auto-rotation

---

## Production Environment

### Kubernetes Secrets (Recommended)

#### 1. Create Secrets (One-Time)

```bash
# Generate strong credentials
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
REDIS_PASSWORD=$(python -c "import secrets; print(secrets.token_hex(32))")
DB_PASSWORD=$(python -c "import secrets; print(secrets.token_hex(32))")

# Create namespace
kubectl create namespace vanna

# Create Kubernetes secret
kubectl create secret generic vanna-secrets \
  --from-literal=SECRET_KEY="$SECRET_KEY" \
  --from-literal=DATABASE_URL="postgresql://vanna:$DB_PASSWORD@postgres.prod:5432/vanna_db?sslmode=require" \
  --from-literal=REDIS_URL="redis://:$REDIS_PASSWORD@redis.prod:6379/0" \
  --from-literal=CELERY_BROKER_URL="redis://:$REDIS_PASSWORD@redis.prod:6379/1" \
  --from-literal=CELERY_RESULT_BACKEND="redis://:$REDIS_PASSWORD@redis.prod:6379/2" \
  --from-literal=OPENAI_API_KEY="sk-..." \
  --from-literal=VANNA_API_KEY="..." \
  --from-literal=CORS_ORIGINS="https://app.example.com" \
  -n vanna

# Verify secret created
kubectl get secrets -n vanna
kubectl describe secret vanna-secrets -n vanna
```

#### 2. Reference in Deployment

Update `k8s/overlays/production/vanna-api-patch.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vanna-api
spec:
  template:
    spec:
      serviceAccountName: vanna-api
      containers:
        - name: api
          env:
            # Secrets from Secret object
            - name: SECRET_KEY
              valueFrom:
                secretKeyRef:
                  name: vanna-secrets
                  key: SECRET_KEY
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: vanna-secrets
                  key: DATABASE_URL
            - name: REDIS_URL
              valueFrom:
                secretKeyRef:
                  name: vanna-secrets
                  key: REDIS_URL
            - name: OPENAI_API_KEY
              valueFrom:
                secretKeyRef:
                  name: vanna-secrets
                  key: OPENAI_API_KEY
            
            # Non-sensitive config from ConfigMap
            - name: APP_ENV
              valueFrom:
                configMapKeyRef:
                  name: vanna-config
                  key: APP_ENV
            - name: LOG_LEVEL
              valueFrom:
                configMapKeyRef:
                  name: vanna-config
                  key: LOG_LEVEL
```

#### 3. Apply Deployment

```bash
# Deploy secrets and config
kubectl apply -f k8s/base/secrets.yaml
kubectl apply -f k8s/base/configmap.yaml

# Deploy application
kubectl apply -k k8s/overlays/production

# Verify pods can access secrets
kubectl logs -f deployment/vanna-api -n vanna | grep "Database connected"
```

### Secret Rotation (Kubernetes)

#### Manual Rotation

```bash
# 1. Generate new secret
NEW_SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")

# 2. Update secret
kubectl patch secret vanna-secrets \
  -p '{"data":{"SECRET_KEY":"'"$(echo -n $NEW_SECRET_KEY | base64)"'"}}' \
  -n vanna

# 3. Rollout restart
kubectl rollout restart deployment/vanna-api -n vanna

# 4. Monitor rollout
kubectl rollout status deployment/vanna-api -n vanna
```

#### Automated Rotation (Recommended)

Use **Sealed Secrets** or **HashiCorp Vault**:

```bash
# Install Sealed Secrets
helm repo add sealed-secrets https://kubernetes.github.io/sealed-secrets
helm install sealed-secrets sealed-secrets/sealed-secrets -n kube-system

# Create sealing key
kubeseal --fetch-cert > /tmp/sealing-key.crt

# Seal a secret
echo -n my-secret | kubectl create secret generic my-secret \
  --dry-run=client --from-file=/dev/stdin \
  -o yaml | kubeseal -f - > my-sealed-secret.yaml

# Commit sealed secret to Git
git add my-sealed-secret.yaml
git commit -m "Add sealed secret"

# Deploy (controller auto-unseals)
kubectl apply -f my-sealed-secret.yaml
```

---

## HashiCorp Vault Integration (Advanced)

### Setup

```bash
# Install Vault Agent Injector
helm repo add hashicorp https://helm.releases.hashicorp.com
helm install vault hashicorp/vault --values vault-values.yaml

# Create KV v2 secret engine
vault secrets enable -path=vanna kv-v2

# Store secrets in Vault
vault kv put vanna/production/secrets \
  DATABASE_URL="postgresql://..." \
  SECRET_KEY="..." \
  REDIS_URL="..."
```

### Pod Annotation

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vanna-api
spec:
  template:
    metadata:
      annotations:
        vault.hashicorp.com/agent-inject: "true"
        vault.hashicorp.com/role: "vanna-api"
        vault.hashicorp.com/agent-inject-secret-secrets: "vanna/data/production/secrets"
        vault.hashicorp.com/agent-inject-template-secrets: |
          {{- with secret "vanna/data/production/secrets" -}}
          export SECRET_KEY="{{ .Data.data.SECRET_KEY }}"
          export DATABASE_URL="{{ .Data.data.DATABASE_URL }}"
          {{- end }}
    spec:
      serviceAccountName: vanna-api
      containers:
        - name: api
          command: ["/vault/secrets/secrets", "&&", "app.main"]
```

### Automatic Secret Rotation

```bash
# Configure Vault to rotate credentials
vault write -f vanna/rotate/production
```

---

## Environment-Specific Secrets Summary

### Development (`docker/env/.env.dev`)
```bash
SECRET_KEY=dev-key-not-secure-replace-in-prod
DATABASE_URL=postgresql://dev:dev@localhost:5432/vanna_dev
REDIS_URL=redis://localhost:6379/0
LLM_PROVIDER=ollama  # Use local LLM for dev
OPENAI_API_KEY=  # Leave empty in dev
```

### Staging (`docker/env/.env.stage` / Secrets Manager)
```bash
SECRET_KEY=<generated-strong-key>
DATABASE_URL=postgresql://vanna:password@postgres.staging:5432/vanna_staging?sslmode=require
REDIS_URL=redis://:password@redis.staging:6379/0
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-... # Non-prod key
```

### Production (Kubernetes Secrets / Vault)
```bash
SECRET_KEY=<highly-random-256-bit-key>
DATABASE_URL=postgresql://vanna:password@postgres.prod:5432/vanna_prod?sslmode=require&ssl_cert=/etc/ssl/certs/ca-bundle.crt
REDIS_URL=redis://:password@redis.prod:6379/0
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-... # Production key with spend limits
CORS_ORIGINS=https://app.example.com,https://admin.example.com  # Restrict to prod domain
```

---

## Security Best Practices

### ✅ DO

- [ ] Generate strong secrets (minimum 32 random bytes)
- [ ] Use different secrets per environment
- [ ] Rotate secrets every 90 days (production)
- [ ] Use SSL/TLS for database connections (add `?sslmode=require`)
- [ ] Encrypt secrets at rest in Kubernetes (Sealed Secrets or Vault)
- [ ] Audit all secret access
- [ ] Limit secret access by RBAC
- [ ] Never log or output secrets (use masking)

### ❌ DON'T

- [ ] Commit real secrets to Git
- [ ] Use same secrets across environments
- [ ] Reuse old secrets after rotation
- [ ] Share secrets via email or chat
- [ ] Store secrets in plain text files on disk
- [ ] Use weak or predictable secrets
- [ ] Allow public access to secret storage
- [ ] Keep old secret backups indefinitely

---

## Incident Response: Leaked Secret

If a secret is compromised:

1. **Immediate Actions** (within 5 minutes)
   - Revoke the compromised secret
   - Block any API keys in cloud provider (AWS, OpenAI, etc.)
   - Notify security team

2. **Short-term** (within 1 hour)
   - Generate new secret
   - Update all environments
   - Deploy new version

3. **Follow-up** (within 24 hours)
   - Review audit logs for misuse
   - Update incident response policy
   - Communicate with stakeholders

**Example:**
```bash
# 1. Revoke
kubectl delete secret vanna-secrets -n vanna

# 2. Regenerate
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")

# 3. Recreate
kubectl create secret generic vanna-secrets \
  --from-literal=SECRET_KEY="$SECRET_KEY" \
  ... other secrets ...

# 4. Restart
kubectl rollout restart deployment/vanna-api -n vanna
```

---

## Validation Checklist

### Before Staging Deployment
- [ ] All secrets generated with `secrets.token_hex(32)` or equivalent
- [ ] `docker/env/.env.stage` created from `docker/env/.env.example` template
- [ ] Secrets Manager access configured (AWS/GCP/Azure)
- [ ] Database user created with secure password
- [ ] Redis password set and verified
- [ ] LLM API keys valid and active
- [ ] Secrets rotated from previous staging cycle

### Before Production Deployment
- [ ] Secrets stored in Kubernetes / Vault (NOT in Git)
- [ ] RBAC roles created for secret access
- [ ] Sealed Secrets or Vault configured for encryption
- [ ] Secret rotation schedule established (90-day)
- [ ] Incident response plan in place
- [ ] Audit logging enabled for all secret access
- [ ] Production domain configured in CORS_ORIGINS
- [ ] Database SSL certificate installed
- [ ] All team members briefed on secret policy

---

## References

- [Kubernetes Secrets Documentation](https://kubernetes.io/docs/concepts/configuration/secret/)
- [Sealed Secrets by Bitnami](https://github.com/bitnami-labs/sealed-secrets)
- [HashiCorp Vault](https://www.vaultproject.io/)
- [OWASP Secrets Management](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/assets/uploads/secure-coding-practices-quick-reference-guide-v2_en.pdf)
- [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/)
- [Google Cloud Secret Manager](https://cloud.google.com/secret-manager)
- [Azure Key Vault](https://azure.microsoft.com/en-us/services/key-vault/)
