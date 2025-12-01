# BACKEND_ENHANCEMENTS.md

**Technical Addendum: Enterprise-Grade Backend Enhancements**

---

## Document Information

| Property | Value |
|----------|-------|
| **Document Version** | 1.0 |
| **Project** | Vanna Insight Engine (FastAPI Backend) |
| **Status** | For Implementation |
| **Date** | November 12, 2025 |
| **Purpose** | Define all backend enhancements for enterprise-grade standards |
| **Scope** | Core Layer, Services, APIs, Database, Security |

---

## Table of Contents

1. [Core Architecture & Initialization](#1-core-architecture--initialization)
2. [Configuration & Secrets Management](#2-configuration--secrets-management)
3. [Database Layer Improvements](#3-database-layer-improvements)
4. [LLM Integration Layer](#4-llm-integration-layer)
5. [Semantic Layer Integration](#5-semantic-layer-integration)
6. [Query Validation & Firewall](#6-query-validation--firewall)
7. [Audit & Observability](#7-audit--observability)
8. [Error Handling & Recovery](#8-error-handling--recovery)
9. [API Layer Enhancements](#9-api-layer-enhancements)
10. [Logging & Telemetry](#10-logging--telemetry)
11. [Testing & Validation](#11-testing--validation)
12. [Performance Optimizations](#12-performance-optimizations)
13. [Documentation & Standards](#13-documentation--standards)

---

## 1. Core Architecture & Initialization

### 1.1 System Manager Layer (NEW)

**Purpose:** Centralized runtime orchestration and health supervision

**Responsibilities:**
- Detect availability of database, vector store, LLM providers
- Compute real-time **System Health Score (0-100%)**
- Manage operation modes automatically:
  - `FULL_OPERATIONAL` - All components active
  - `LIMITED_AI` - DB + minimal LLM available
  - `READ_ONLY` - DB only
  - `CONFIGURATION` - Initial setup required
  - `EMERGENCY` - Minimal fallback mode

**Implementation:**
```python
# app/core/system_manager.py
from enum import Enum

class OperationalMode(str, Enum):
    FULL_OPERATIONAL = "FULL_OPERATIONAL"
    LIMITED_AI = "LIMITED_AI"
    READ_ONLY = "READ_ONLY"
    CONFIGURATION = "CONFIGURATION"
    EMERGENCY = "EMERGENCY"

class SystemManager:
    def __init__(self):
        self.health_score = 100
        self.operational_mode = OperationalMode.CONFIGURATION
    
    def compute_health_score(self) -> int:
        """Calculate system health (0-100%)"""
        database_health = self.check_database_health()  # 40%
        llm_health = self.check_llm_health()  # 30%
        redis_health = self.check_redis_health()  # 15%
        vector_db_health = self.check_vector_db_health()  # 15%
        
        score = (
            database_health * 0.40 +
            llm_health * 0.30 +
            redis_health * 0.15 +
            vector_db_health * 0.15
        )
        return int(score)
    
    def determine_operational_mode(self) -> OperationalMode:
        """Determine mode based on health score"""
        self.health_score = self.compute_health_score()
        
        if self.health_score >= 85:
            return OperationalMode.FULL_OPERATIONAL
        elif self.health_score >= 60:
            return OperationalMode.LIMITED_AI
        elif self.health_score >= 40:
            return OperationalMode.READ_ONLY
        else:
            return OperationalMode.EMERGENCY
```

**Benefits:**
- ✅ Predictable recovery on failure
- ✅ Simplified observability and alerting
- ✅ Consistent behavior across environments

---

## 2. Configuration & Secrets Management

### 2.1 Secure Environment Manager (NEW)

**Purpose:** Encrypt/decrypt all sensitive environment variables

**Implementation:**
```python
# app/core/security/secure_env_manager.py
from cryptography.fernet import Fernet
from pathlib import Path
import base64

class SecureEnvManager:
    def __init__(self, key_file: str = ".datamind_key"):
        self.key_file = Path(key_file)
        self.key = self._load_or_generate_key()
        self.cipher = Fernet(self.key)
    
    def _load_or_generate_key(self) -> bytes:
        """Load key from file or generate new one"""
        if self.key_file.exists():
            return self.key_file.read_bytes()
        else:
            key = Fernet.generate_key()
            self.key_file.write_bytes(key)
            return key
    
    def encrypt_value(self, value: str) -> str:
        """Encrypt a value and return base64"""
        encrypted = self.cipher.encrypt(value.encode())
        return f"ENC({base64.b64encode(encrypted).decode()})"
    
    def decrypt_value(self, encrypted: str) -> str:
        """Decrypt a value"""
        if not encrypted.startswith("ENC("):
            return encrypted
        
        encrypted_b64 = encrypted[4:-1]  # Remove ENC( and )
        encrypted_bytes = base64.b64decode(encrypted_b64)
        decrypted = self.cipher.decrypt(encrypted_bytes)
        return decrypted.decode()
```

**Usage in .env:**
```bash
DATABASE_PASSWORD=ENC(gAAAAABjk...)
OPENAI_API_KEY=ENC(gAAAAABjk...)
LLM_API_KEY=ENC(gAAAAABjk...)
```

### 2.2 Advanced Key Manager (NEW)

**Purpose:** Manage encryption keys and salts securely

**Implementation:**
```python
# app/core/security/advanced_key_manager.py
import os
from pathlib import Path
import hashlib
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend

class AdvancedKeyManager:
    def __init__(self):
        self.key_file = Path(".datamind_key")
        self.salt_file = Path(".datamind_salt")
    
    def generate_key_from_passphrase(self, passphrase: str) -> bytes:
        """Generate encryption key from passphrase using PBKDF2"""
        salt = self._get_or_create_salt()
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(passphrase.encode())
        return key
    
    def _get_or_create_salt(self) -> bytes:
        """Get salt from file or create new one"""
        if self.salt_file.exists():
            return self.salt_file.read_bytes()
        else:
            salt = os.urandom(32)
            self.salt_file.write_bytes(salt)
            return salt
    
    def rotate_key(self, old_passphrase: str, new_passphrase: str):
        """Rotate encryption key"""
        # Generate new salt
        new_salt = os.urandom(32)
        self.salt_file.write_bytes(new_salt)
        
        # Generate new key
        new_key = self.generate_key_from_passphrase(new_passphrase)
        self.key_file.write_bytes(new_key)
```

---

## 3. Database Layer Improvements

### 3.1 Enhanced Database Connector

**Implementation:**
```python
# app/db/database.py
from sqlalchemy import create_engine, event
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections
    pool_recycle=3600,   # Recycle stale connections
    echo=False
)

class DatabaseConnector:
    def __init__(self, engine):
        self.engine = engine
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False
    
    def get_schema_as_ddl(self) -> str:
        """Extract all DDL for RAG training"""
        # Uses SQLAlchemy Inspector to get schema
        pass
    
    def get_schema_info(self) -> dict:
        """Get detailed schema information"""
        # Returns tables, columns, types, relationships
        pass
```

### 3.2 Query Firewall Features

**Built-in Firewall:**
```python
# app/core/security/query_firewall.py
BLOCKED_KEYWORDS = [
    "DROP", "TRUNCATE", "DELETE", "INSERT", 
    "UPDATE", "ALTER", "CREATE", "GRANT", 
    "REVOKE", "EXEC", "EXECUTE", "xp_cmdshell"
]

def validate_query_safe(sql: str) -> Tuple[bool, str]:
    """Check if SQL is safe to execute"""
    sql_upper = sql.upper()
    
    # Check blocked keywords
    for keyword in BLOCKED_KEYWORDS:
        if keyword in sql_upper:
            return (False, f"Blocked keyword detected: {keyword}")
    
    # Check for multiple statements
    if sql.count(";") > 1:
        return (False, "Multiple statements not allowed")
    
    # Syntax validation
    try:
        parsed = sqlparse.parse(sql)
        if not parsed:
            return (False, "Invalid SQL syntax")
    except Exception as e:
        return (False, f"Parse error: {str(e)}")
    
    return (True, "Query validated")
```

---

## 4. LLM Integration Layer

### 4.1 Unified LLM Adapter

**Implementation:**
```python
# app/core/llm_adapter.py
class UnifiedLLMAdapter:
    def __init__(self, provider: str = "ollama"):
        self.provider = provider
        self.timeout = 60
        self.client = self._initialize_client()
    
    def _initialize_client(self):
        """Initialize LLM client based on provider"""
        if self.provider == "ollama":
            return OllamaClient(base_url=os.getenv("OLLAMA_BASE_URL"))
        elif self.provider == "openai":
            return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        elif self.provider == "azure":
            return AzureOpenAI(...)
        else:
            return MockLLMProvider()
    
    async def generate_sql(self, question: str, schema_context: dict) -> dict:
        """Generate SQL with automatic fallback"""
        try:
            return await self._generate_with_provider(question, schema_context)
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            # Fallback to mock
            return await self._generate_with_mock_provider(question, schema_context)
    
    def health_check(self) -> Tuple[bool, str]:
        """Check if LLM provider is available"""
        try:
            self.client.ping()
            return (True, f"{self.provider} is healthy")
        except:
            return (False, f"{self.provider} is unreachable")
```

---

## 5. Semantic Layer Integration

### 5.1 Formal Semantic Repository

**Implementation:**
```python
# app/core/semantic_layer.py
import yaml
from pathlib import Path

class SemanticRepository:
    def __init__(self, yaml_path: str = "config/business_ontology.yaml"):
        self.definitions = self._load_definitions(yaml_path)
    
    def _load_definitions(self, yaml_path: str) -> dict:
        """Load business metrics and dimensions"""
        with open(yaml_path) as f:
            return yaml.safe_load(f)
    
    def get_all_definitions_as_text(self) -> str:
        """Return definitions for LLM context"""
        text = "Business Definitions:\n\n"
        for metric, definition in self.definitions.items():
            text += f"- {metric}: {definition}\n"
        return text
    
    def get_metric(self, metric_name: str) -> dict:
        """Get specific metric definition"""
        return self.definitions.get(metric_name)
```

---

## 6. Query Validation & Firewall

### 6.1 Enhanced Query Validator

**Implementation:**
```python
# app/core/security/query_validator.py
import sqlparse

def validate_query_comprehensive(sql: str) -> Tuple[bool, str]:
    """Comprehensive query validation"""
    
    # 1. Firewall check
    is_safe, message = validate_query_safe(sql)
    if not is_safe:
        return (False, message)
    
    # 2. Syntax check
    try:
        parsed = sqlparse.parse(sql)
        if not parsed:
            return (False, "Invalid SQL syntax")
    except Exception as e:
        return (False, f"Syntax error: {e}")
    
    # 3. Column whitelist check (optional)
    allowed_tables = get_allowed_tables(user_role)
    for table in extract_tables_from_sql(sql):
        if table not in allowed_tables:
            return (False, f"Access denied to table: {table}")
    
    return (True, "Query validated")
```

---

## 7. Audit & Observability

### 7.1 Audit Logger

**Implementation:**
```python
# app/core/audit_logger.py
import json
from datetime import datetime, timezone

class AuditLogger:
    def __init__(self, log_file: str = "logs/audit.log"):
        self.log_file = log_file
    
    def log_event(self, event: dict):
        """Log audit event in JSON format"""
        event_with_timestamp = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **event
        }
        
        with open(self.log_file, "a") as f:
            f.write(json.dumps(event_with_timestamp) + "\n")
    
    def log_query_execution(self, user_id: str, sql: str, status: str):
        """Log query execution"""
        self.log_event({
            "event_type": "query_execution",
            "user_id": user_id,
            "sql_hash": hash(sql),
            "status": status,
            "component": "database"
        })
    
    def log_authentication_attempt(self, user: str, success: bool):
        """Log auth attempts"""
        self.log_event({
            "event_type": "authentication",
            "user": user,
            "success": success,
            "component": "auth"
        })
```

---

## 8. Error Handling & Recovery

### 8.1 Unified Exception Classes

**Implementation:**
```python
# app/utils/error_handlers.py

class DatabaseConnectionError(Exception):
    """Database connection failed"""
    pass

class InvalidSQLCommand(Exception):
    """SQL failed validation"""
    pass

class LLMGenerationError(Exception):
    """LLM failed to generate SQL"""
    pass

class SemanticContextError(Exception):
    """Semantic context unavailable"""
    pass

class ConfigurationDecryptionError(Exception):
    """Failed to decrypt configuration"""
    pass
```

---

## 9. API Layer Enhancements

### 9.1 Standardized Response Schema

**Implementation:**
```python
# app/api/schemas/base.py
from pydantic import BaseModel
from typing import Any, Optional

class StandardResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    correlation_id: Optional[str] = None

class ErrorResponse(StandardResponse):
    success: bool = False
    status_code: int
```

---

## 10. Logging & Telemetry

### 10.1 Structured JSON Logging

**Configuration:**
```python
# app/core/logging_config.py
LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(timestamp)s %(level)s %(name)s %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json"
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "logs/app.log",
            "formatter": "json"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"]
    }
}
```

---

## 11. Testing & Validation

### 11.1 Backend Test Suite

```python
# tests/unit/test_query_firewall.py
import pytest
from app.core.security.query_firewall import validate_query_safe

def test_blocks_drop_table():
    """Query with DROP should be blocked"""
    sql = "DROP TABLE users;"
    is_valid, message = validate_query_safe(sql)
    assert is_valid is False
    assert "DROP" in message

def test_allows_select():
    """Valid SELECT should pass"""
    sql = "SELECT * FROM users WHERE id = 1;"
    is_valid, message = validate_query_safe(sql)
    assert is_valid is True
```

---

## 12. Performance Optimizations

**Key Optimizations:**
- Connection pooling (configured above)
- Result caching with Redis
- Preload schema embeddings on startup
- Parallelize LLM calls using asyncio
- Vector index rebuild scheduling

---

## 13. Documentation & Standards

**Every module must include:**
```python
"""
Vanna Insight Engine – Module Name
Description: Purpose and usage summary.
Version: 1.0
Author: Backend Team
"""
```

---

## Expected Outcomes

| Category | Improvement | Benefit |
|----------|-------------|---------|
| **Security** | Encrypted config + query firewall | Enterprise protection |
| **Reliability** | System Manager + recovery modes | Self-healing backend |
| **Maintainability** | Modular services | Easier debugging |
| **Observability** | Audit + metrics + health | Transparent monitoring |
| **Intelligence** | Semantic feedback + learning | Continuous improvement |

---

**Status:** ✅ Ready for Implementation

**End of BACKEND_ENHANCEMENTS.md**

---

## 14. Enterprise Feature Enhancements

### 14.1 Semantic Compiler & Registry

- **Scope**: `app/modules/semantic_layer` + `/api/v1/semantic/*` endpoints.
- **Flow**: `SemanticCompiler.compile_from_dbt()` reads dbt docs → persists `*.semantic.yaml` → calls `VannaClient.train()` → refreshes ORM tables (`semantic_models`, `semantic_metrics`, etc.).
- **API Contract**: `GET/POST /api/v1/semantic/models` return/accept `SemanticModelResponse`, `POST /api/v1/semantic/compile` returns `{compiled_models, message}` with `202` semantics for async orchestration.
- **Error Handling**: Any compile failure raises `HTTPException` with correlation id & `get_error_documentation()` pointer. Retries respect `SEMANTIC_REFRESH_SECONDS` to avoid thrash.

### 14.2 Policy Engine & Data Control

- **Scope**: `app/modules/data_control`, DB tables `data_policies`, `policy_bindings`.
- **Runtime**: `SQLService.generate_sql/execute_sql` now call `DataPolicyEngine.evaluate()` and `validate_execution()` to enforce row/column level security before Stage 3 and Stage 6 of the NL→SQL pipeline.
- **APIs**: `/api/v1/data-control/policies` (list/create), `/preview` for dry-run, with admin-only auth enforced at router level.
- **SLAs**: Policies cached for `POLICY_CACHE_SECONDS` with automatic invalidation on write, ensuring query latency remains within <50ms overhead.

### 14.3 Project + User Management

- **Scope**: `app/modules/projects`, `app/modules/user_management` with new tables `projects`, `project_memberships`, `project_templates`, `user_groups`, `user_group_memberships`.
- **Responsibilities**: Provide boilerplates & templates, advanced RBAC (groups, owner roles), and per-project scoping for dashboards/spreadsheets/SQL queries.
- **APIs**: `/api/v1/projects*` for CRUD + membership, `/api/v1/users/roster`, `/api/v1/users/{id}/roles|groups` for rosters and group assignment.

### 14.4 Dashboard & Spreadsheet Engines

- **Dashboard Manager**: `DashboardService` ensures every layout has `status` + `metadata_json`. `/api/v1/dashboards` returns JSON describing layout structure, `/publish` calls chosen adapter (Superset by default) and updates status to `published`.
- **Spreadsheet Engine**: `SpreadsheetService` serializes documents to `spreadsheets` + `spreadsheet_cells`, and exposes `/api/v1/spreadsheets/formula` which uses `VannaClient.generate_formula()` for AI-assisted calculations.
- **Governance Hooks**: Project membership + policies are checked before any cell update; service enforces `SPREADSHEET_MAX_CELLS` and respect `SPREADSHEET_SANDBOX_BUCKET` for persistence when configured.

### 14.5 Usage Monitoring

- **Scope**: `app/modules/usage_monitoring` and `/api/v1/usage/*` endpoints.
- **Instrumentation**: `UsageMonitoringService.record_event()` is invoked by `SQLService` and can be reused by dashboards/spreadsheets; `/usage/events` accepts additional telemetry from UI clients.
- **Exposure**: `/usage/summary` returns aggregated counts for the last `days` parameter, enabling KPI dashboards and feed into the System Manager’s health score.

### 14.6 Integration Summary

- The new Alembic migration `003_enterprise_extensions.py` provisions every backing table and augments existing `users`/`queries` structures.
- `config.py` adds environment toggles (`ENABLE_SEMANTIC_COMPILER`, `ENABLE_ROW_LEVEL_SECURITY`, `DASHBOARD_ADAPTER`, etc.) to keep deployments deterministic.
- `app/main.py` wires routers with scoped dependencies, guaranteeing RBAC alignment with OPERATIONAL_DIRECTIVES.

These enhancements extend the headless backend into a fully governed enterprise platform while adhering to the existing security posture (RBAC, audit logging, rate limiting, Query Firewall).

### 14.7 API Coverage Checklist

| Domain | Endpoint(s) | Backing Service |
|--------|-------------|-----------------|
| Semantic Catalog | `/api/v1/entities`, `/dimensions`, `/hierarchies`, `/filters`, `/glossary` | `SemanticCatalogService` |
| Semantic Compiler | `/api/v1/compiler/compile`, `/api/v1/semantic/interpret` | `SemanticLayerService` |
| Metrics Registry | `/api/v1/metrics`, `/metrics/templates`, `/metrics/import` | `MetricsRegistryService` |
| Projects & Dashboards | `/api/v1/projects/*`, `/api/v1/dashboards/*` (GET/POST/PATCH/DELETE/Publish) | `ProjectService`, `DashboardService` |
| Spreadsheets | `/api/v1/spreadsheets/*`, `/ai-fill`, `/ai-formula`, `/sql-sync` | `SpreadsheetService` |
| User Management | `/api/v1/users/*`, `/users/{id}/assign-role`, `/users/{id}/groups` | `UserManagementService` |
| Data Policies | `/api/v1/policies`, `/policies/rows`, `/policies/columns` | `DataPolicyService` |
| Security | `/api/v1/security/audit-log|sessions|ip-restrictions|query-quota|token-rotation` | `SecurityService` |
| Usage Analytics | `/api/v1/usage/summary|users|queries|dashboards|llm-tokens` | `UsageMonitoringService` |

أي مراجعة أو إطلاق يجب أن يتحقق من هذه النقاط لضمان التغطية الكاملة للمتطلبات المؤسسية.
