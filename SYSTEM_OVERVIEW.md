# DataMind AI: Unified System Overview & FastAPI Backend Integration Framework

**Enterprise-Grade Generative BI Platform with Natural Language to SQL Conversion**

---

## Document Metadata

| Property | Value |
|----------|-------|
| **Document Version** | 6.2 (Final - DataMind AI Integration) |
| **Project** | DataMind AI / Vanna Insight Engine (FastAPI Backend) |
| **Status** | Production-Ready, For Implementation |
| **Date** | November 12, 2025 |
| **Purpose** | Complete system architecture defining how the FastAPI backend integrates with all platform components (dbt, PostgreSQL, ClickHouse, Superset, Ollama/OpenAI, UI clients) |
| **Scope** | End-to-end architecture, operational flows, integration patterns, inputs/outputs, deployment considerations |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Architecture Overview](#2-system-architecture-overview)
3. [FastAPI Backend - The Core Engine](#3-fastapi-backend---the-core-engine)
4. [Integration Architecture](#4-integration-architecture)
5. [Operational Flow](#5-operational-flow)
6. [Data Contracts & Input/Output Specifications](#6-data-contracts--inputoutput-specifications)
7. [Security & Governance Framework](#7-security--governance-framework)
8. [Observability & Monitoring](#8-observability--monitoring)
9. [Technology Stack](#9-technology-stack)
10. [Implementation Phases](#10-implementation-phases)
11. [Expected Outcomes & Success Metrics](#11-expected-outcomes--success-metrics)
12. [Development & Maintenance Notes](#12-development--maintenance-notes)

---

## 1. Executive Summary

**DataMind AI** is an enterprise-grade **Generative BI and Conversational Analytics Platform** that transforms natural language into SQL queries, generates insights, and enables secure, governed access to organizational data through a modular, scalable architecture.

### 1.1 System Components

The platform consists of interconnected layers:

```
┌────────────────────────────────────────────────────┐
│          User Interface (UI) Layer                  │
│   Streamlit / React Frontend / Custom Clients      │
└───────────────────┬────────────────────────────────┘
                    │ REST API / WebSocket
                    ▼
┌────────────────────────────────────────────────────┐
│       FASTAPI BACKEND (Core Control Layer)         │
│  • Authentication / RBAC                            │
│  • API Endpoints (Query, Train, Health, Feedback)  │
│  • Query Validation & Execution                    │
│  • LLM Orchestration (Ollama, OpenAI, Azure)      │
│  • Governance & Audit Logging                      │
│  • Secure Config / Encryption Management           │
│  • Integration Services (dbt / Superset / CH)     │
└───────────────┬────────────────────────────────────┘
                │
    ┌───────────┴───────────┐
    │                       │
┌───▼──────────┐   ┌────────▼────────┐
│  Data Layer   │   │ Transformation  │
│ PostgreSQL/   │   │  Layer (dbt)    │
│  ClickHouse   │   │ Semantic Models │
│  (OLTP/OLAP)  │   │  for SSOT       │
└───────┬───────┘   └─────────────────┘
        │
        ▼
  ┌──────────────┐
  │ Superset BI  │
  │  Dashboards  │
  │  & Analytics │
  └──────────────┘
```

### 1.2 Core Value Propositions

1. **Natural Language to SQL** - Non-technical users ask questions in plain English
2. **Governed Data Access** - RBAC, query firewall, PII masking, audit trails
3. **Single Source of Truth** - dbt transforms raw data into trusted models
4. **Continuous Learning** - Feedback loop improves query accuracy over time
5. **Headless Architecture** - Backend-first design, UI-agnostic
6. **Enterprise Security** - Encrypted configuration, validated queries, role-based access

### 1.3 Key Differentiators

- ✅ **Native dbt Integration** - Queries against tested, documented data models
- ✅ **Multi-LLM Support** - Ollama (local), OpenAI, Azure, Anthropic with automatic fallback
- ✅ **Query Firewall** - Blocks DDL/DML operations, prevents destructive queries
- ✅ **7-Stage NL-to-SQL Pipeline** - Interpret → Generate → Validate → Optimize → Sanitize → Execute → Explain
- ✅ **Feedback-to-Training Loop** - User corrections automatically retrain the model
- ✅ **Phased Scalability** - PostgreSQL → ClickHouse migration path built-in
- ✅ **Complete Audit Trail** - Every query, every user action, fully logged

---

## 2. System Architecture Overview

### 2.1 High-Level Architecture Diagram

```
                  ┌──────────────────────────────┐
                  │      User Interface (UI)      │
                  │  Streamlit / React Frontend   │
                  └───────────────┬───────────────┘
                                  │ REST / WebSocket
                                  ▼
        ┌─────────────────────────────────────────────────────┐
        │              FASTAPI BACKEND (Core Layer)            │
        │------------------------------------------------------│
        │  • Correlation ID Middleware                         │
        │  • JWT Authentication & RBAC                         │
        │  • Rate Limiting & Circuit Breakers                  │
        │  • Exception Handling & Error Responses              │
        │------------------------------------------------------│
        │        7-Stage NL-to-SQL Pipeline                    │
        │  ┌──────────────────────────────────────────────┐   │
        │  │ 1. Interpret  → Parse NL into intent          │   │
        │  │ 2. Generate   → SQL from intent (Vanna+LLM)   │   │
        │  │ 3. Validate   → Security + syntax checks      │   │
        │  │ 4. Optimize   → Performance tuning            │   │
        │  │ 5. Sanitize   → PII masking                   │   │
        │  │ 6. Execute    → Run SQL, log results          │   │
        │  │ 7. Explain    → NL result description         │   │
        │  └──────────────────────────────────────────────┘   │
        │------------------------------------------------------│
        │  • System Manager (Health Scoring, Op Modes)         │
        │  • Secure Environment Manager (Encrypted .env)       │
        │  • Unified LLM Adapter (Multi-provider support)      │
        │  • Feedback Manager (Governance workflow)            │
        │  • Audit Logger (Complete traceability)              │
        └───────────────┬──────────────────────────────────────┘
                        │
            ┌───────────┴───────────┐
            │                       │
 ┌──────────▼──────────┐   ┌────────▼────────┐
 │  Data Layer          │   │ Transformation  │
 │ • PostgreSQL (OLTP)  │   │ Layer (dbt)     │
 │ • ClickHouse (OLAP)  │   │ • Models        │
 │   (Phase 2)          │   │ • Tests         │
 │ • Redis (Cache)      │   │ • Documentation │
 │ • ChromaDB (Vectors) │   │ • Metrics       │
 └──────────┬───────────┘   └────────┬────────┘
            │                        │
            └───────────┬────────────┘
                        │
                 ┌──────▼────── ┐
                 │  Superset BI  │
                 │  Dashboards & │
                 │  Reports      │
                 └───────────────┘
```

### 2.2 Component Responsibilities

| Component | Role | Key Functions |
|-----------|------|---------------|
| **FastAPI Backend** | Orchestration Hub | Routes all requests, enforces security, orchestrates AI/DB/UI interactions |
| **dbt Core** | Transformation Factory | Builds Single Source of Truth from raw data, provides tested models |
| **PostgreSQL** | Transactional Storage | User data, query history, audit logs, training data |
| **ClickHouse** | Analytical Storage | High-performance OLAP queries (Phase 2) |
| **Redis** | Caching & Queue | Session cache, Celery broker, result cache |
| **ChromaDB/Qdrant** | Vector Storage | Embeddings for semantic search and contextual retrieval |
| **Ollama/OpenAI** | LLM Processing | SQL generation from natural language |
| **Superset** | BI Layer | Dashboards, SQL Lab, reports (peer service, not managed by backend) |
| **Streamlit/React** | Presentation Layer | User interface for conversational analytics |

---

## 3. FastAPI Backend - The Core Engine

The FastAPI backend is the **central nervous system** of DataMind AI, connecting intelligence, governance, and user interaction into a single, secure architecture.

### 3.1 Primary Responsibilities

#### A. API Gateway & Routing
- **Public Endpoints** - Demo/marketing access with rate limiting
- **Authenticated Endpoints** - JWT-protected, role-based access
- **Admin Endpoints** - Governance, training data management, system configuration

#### B. Security & Governance
- **Authentication** - JWT with refresh tokens, password hashing (bcrypt)
- **Authorization** - RBAC (admin, analyst, viewer roles)
- **Query Firewall** - Blocks DDL/DML operations (DROP, DELETE, INSERT, UPDATE)
- **PII Masking** - Automatic detection and masking of sensitive data
- **Rate Limiting** - Per-user, per-IP throttling
- **Audit Logging** - Complete trail of all actions

#### C. AI Orchestration
- **Unified LLM Adapter** - Supports Ollama (local), OpenAI, Azure OpenAI, Anthropic
- **Automatic Fallback** - Switches to mock provider on LLM failure
- **Context Management** - Injects dbt documentation, schema info, business ontology
- **Prompt Engineering** - Optimized prompts for SQL generation accuracy

#### D. Data Management
- **Database Connector** - Connection pooling, health checks, auto-fallback
- **Result Caching** - Redis-based caching for frequently accessed queries
- **Query History** - Complete audit trail in PostgreSQL
- **Feedback Storage** - Stores user corrections for retraining

#### E. Integration Services
- **dbt Runner** - Triggers dbt commands (run, test, docs generate)
- **dbt Sync Task** - Automated training from dbt `manifest.json`
- **Superset Metrics** - Exposes analytics endpoints for dashboards
- **ClickHouse Router** - Routes analytical queries to ClickHouse (Phase 2)

### 3.2 System Manager Layer (Enterprise Feature)

**Purpose:** Real-time health monitoring and automatic recovery mode management

**Operational Modes:**

| Mode | Description | Available Components | Use Case |
|------|-------------|---------------------|----------|
| **FULL_OPERATIONAL** | All systems active | All | Normal operation |
| **LIMITED_AI** | DB + minimal LLM | Database, Fallback LLM | LLM provider outage |
| **READ_ONLY** | Database only | PostgreSQL | AI services down |
| **CONFIGURATION** | Setup mode | None | Initial deployment |
| **EMERGENCY** | Minimal fallback | Health endpoint only | Critical failure |

**Health Score Calculation:**

```python
Health Score = (
    DB_Status * 40% +
    LLM_Status * 30% +
    Redis_Status * 15% +
    Vector_DB_Status * 15%
)
```

**Benefits:**
- Predictable recovery on component failure
- Graceful degradation
- Clear operational status for monitoring
- Automatic mode switching

### 3.3 7-Stage NL-to-SQL Pipeline

**Complete flow for every user question:**

```
User Input: "How many active users from USA last month?"

1. INTERPRET
   ├─ Parse intent: count, filter, time range
   ├─ Extract entities: status=active, country=USA, date=last_month
   └─ Determine required tables: users, user_activity

2. GENERATE
   ├─ Retrieve context: dbt models, business ontology
   ├─ Build prompt: "Generate SQL for counting active USA users last month"
   ├─ Call LLM: Ollama/OpenAI via Unified Adapter
   └─ Output: Raw SQL query

3. VALIDATE
   ├─ Syntax check: sqlparse validation
   ├─ Security check: Query Firewall (no DDL/DML)
   ├─ Permission check: User RBAC allows access to users table
   └─ Output: Validated SQL or error

4. OPTIMIZE
   ├─ Add indexes hint if available
   ├─ Rewrite inefficient joins
   ├─ Add LIMIT clause if missing
   └─ Output: Optimized SQL

5. SANITIZE
   ├─ PII masking rules applied to WHERE clauses
   ├─ Sensitive column filtering
   └─ Output: Sanitized SQL

6. EXECUTE
   ├─ Run SQL via DatabaseConnector
   ├─ Log execution time, rows returned
   ├─ Store results in cache (Redis)
   ├─ Save to query_history table
   └─ Output: DataFrame / JSON results

7. EXPLAIN
   ├─ Generate natural language summary
   ├─ "Found 3,847 active users from USA in November 2025"
   ├─ Suggest follow-up questions
   └─ Output: User-friendly explanation
```

### 3.4 Feedback-to-Training Loop (Governance Workflow)

**User Path:**
1. Analyst receives generated SQL (query_id: `qry-12345`)
2. Results are incorrect
3. Analyst flags query: `POST /api/v1/feedback/flag`
   ```json
   {
     "query_id": "qry-12345",
     "comment": "SQL is using wrong table",
     "rating": 2
   }
   ```
4. Backend stores feedback with tag: `flagged-for-review`
5. Entry is excluded from future training

**Admin Path:**
1. Admin retrieves flagged queries: `GET /admin/training-data?tag=flagged-for-review`
2. Admin reviews, writes correct SQL
3. Admin submits approval: `POST /admin/training-data/approve`
   ```json
   {
     "flagged_entry_id": "train-abc123",
     "question": "How many active users from USA last month?",
     "corrected_sql": "SELECT COUNT(*) FROM dim_users WHERE status='active' AND country='USA' AND DATE_TRUNC('month', created_at) = DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')"
   }
   ```
4. Backend actions:
   - Adds correct (question, SQL) pair to training data
   - Removes incorrect flagged entry
   - Triggers Celery task to retrain embeddings
5. Result: Model learns from correction, accuracy improves

---

## 4. Integration Architecture

### 4.1 dbt Integration (Data Transformation Layer)

**Philosophy:** dbt is the "factory" that produces the Single Source of Truth (SSOT). FastAPI is the "storefront" that provides access to it.

**Integration Points:**

#### A. Consumption - Query dbt Models, Not Raw Tables

**Problem:** Querying raw tables requires complex joins, business logic duplication, high error rates.

**Solution:**
1. dbt builds clean, tested models (e.g., `dim_users`, `fct_orders`)
2. FastAPI trains Vanna on dbt model names and descriptions
3. Generated SQL references `dim_users` instead of joining 5 raw tables

**Benefits:**
- 40-60% reduction in SQL generation errors
- Faster query execution (pre-aggregated models)
- Consistent business logic (defined once in dbt)

#### B. Training - Automated Vanna Training from dbt Artifacts

**Implementation:** Celery scheduled task

**File:** `app/tasks/dbt_sync_task.py`

```python
from celery import shared_task
import json
from app.core.vanna_integration.training import ModelTrainer

@shared_task(bind=True, max_retries=3)
def sync_dbt_to_vanna(self):
    """
    Scheduled task: Reads dbt manifest.json, trains Vanna on all models.
    Runs daily at 2 AM UTC (configured in Celery Beat).
    """
    manifest_path = "/dbt/target/manifest.json"
    
    with open(manifest_path) as f:
        manifest = json.load(f)
    
    trainer = ModelTrainer()
    
    for node_id, node in manifest.get("nodes", {}).items():
        if node["resource_type"] == "model":
            model_name = node["name"]
            description = node.get("description", "")
            columns = node.get("columns", {})
            
            # Build training context
            context = f"""
            Table: {model_name}
            Description: {description}
            Columns:
            """
            for col_name, col_data in columns.items():
                col_desc = col_data.get("description", "")
                context += f"  - {col_name}: {col_desc}\n"
            
            # Train Vanna
            trainer.train_ddl(
                ddl=f"-- dbt model: {model_name}",
                documentation=context
            )
    
    return {"status": "success", "models_trained": len(models)}
```

**Schedule:**
```python
# Celery Beat configuration
celery_app.conf.beat_schedule = {
    'sync-dbt-daily': {
        'task': 'app.tasks.dbt_sync_task.sync_dbt_to_vanna',
        'schedule': crontab(hour=2, minute=0),  # 2 AM UTC
    },
}
```

#### C. Orchestration - Triggering dbt Commands

**Implementation:** Admin API endpoint

```python
# app/api/v1/routes/admin.py
from app.services.dbt_runner import DBTRunner

@router.post("/admin/dbt/run")
async def trigger_dbt_run(
    models: list[str] = None,
    admin: User = Depends(get_current_admin)
):
    """Trigger dbt run command. Admin only."""
    runner = DBTRunner()
    result = runner.run_models(models=models)
    
    return {
        "status": "success" if result["success"] else "failed",
        "output": result["stdout"]
    }
```

#### D. Data Quality Awareness

**Feature:** Backend aware of dbt test results

**Implementation:**

```python
# app/services/dbt_runner.py
class DBTRunner:
    def test_models(self) -> dict:
        """Execute dbt test, return pass/fail status"""
        result = subprocess.run(
            ["dbt", "test"],
            cwd=self.project_path,
            capture_output=True
        )
        return {"success": result.returncode == 0}

# app/core/system_manager.py
class SystemManager:
    def get_data_quality_status(self) -> str:
        """Check if dbt tests passed"""
        runner = DBTRunner()
        test_result = runner.test_models()
        
        if test_result["success"]:
            return "HEALTHY"
        else:
            return "DEGRADED - Data quality tests failed"
```

**User Impact:**
```
API Response:
{
  "sql": "SELECT COUNT(*) FROM fct_orders...",
  "results": [...],
  "warning": "⚠️ Data quality tests failed for fct_orders this morning. Results may be incomplete."
}
```

---

### 4.2 PostgreSQL Integration (Transactional Storage)

**Role:** Primary data store for:
- User accounts and authentication
- Query history and audit logs
- Training data metadata
- Feedback submissions
- System configuration

**Connection Management:**

```python
# app/db/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600    # Recycle connections every hour
)

SessionLocal = sessionmaker(bind=engine)
```

**Key Tables:**

| Table | Purpose | Owner |
|-------|---------|-------|
| `users` | User accounts, roles, auth | Backend |
| `queries` | Query history, correlation IDs | Backend |
| `feedback` | User corrections, ratings | Backend |
| `training_data` | Question-SQL pairs metadata | Backend |
| `audit_log` | Complete action audit trail | Backend |

**Backup Strategy:**
- Daily automated backups
- Point-in-time recovery enabled
- Retention: 30 days

---

### 4.3 ClickHouse Integration (Analytical Storage - Phase 2)

**Trigger Conditions:**
- Data volume > 500GB
- Query latency > 3 seconds (P95)
- 50K+ daily active users

**Migration Strategy:**

```
Phase 2.1: Setup (Week 1-2)
├─ Deploy ClickHouse cluster (3+ nodes)
├─ Configure data sync: PostgreSQL → ClickHouse
└─ Update dbt to target ClickHouse

Phase 2.2: Dual-Mode (Week 3-4)
├─ Implement query router in DatabaseConnector
├─ Route analytical queries → ClickHouse
├─ Route transactional queries → PostgreSQL
└─ Monitor performance

Phase 2.3: Optimization (Week 5-6)
├─ Tune ClickHouse schemas
├─ Add materialized views
└─ Benchmark and validate
```

**Query Routing Logic:**

```python
# app/services/db_connector.py
class DatabaseConnector:
    def execute_query(self, sql: str, query_type: str = "unknown"):
        """Route query to appropriate database"""
        
        if query_type == "analytical":
            # Large scans, aggregations, OLAP
            return self.clickhouse_client.execute(sql)
        else:
            # Transactional, small queries, OLTP
            return self.postgres_client.execute(sql)
```

---

### 4.4 LLM Provider Integration (Multi-Provider Support)

**Supported Providers:**

| Provider | Use Case | Cost | Latency |
|----------|----------|------|---------|
| **Ollama** | Development, privacy-sensitive | Free (local) | ~2-3s |
| **OpenAI** | Production, high accuracy | $$ | ~1-2s |
| **Azure OpenAI** | Enterprise, compliance | $$$ | ~1-2s |
| **Anthropic** | Long context, complex queries | $$ | ~2-3s |
| **Mock** | Testing, fallback | Free | <100ms |

**Unified LLM Adapter:**

```python
# app/core/llm_adapter.py
class UnifiedLLMAdapter:
    def __init__(self, provider: str = "ollama"):
        self.provider = provider
        self.client = self._initialize_client()
    
    def generate_sql(self, question: str, schema_context: dict) -> dict:
        """Generate SQL from natural language"""
        try:
            if self.provider == "ollama":
                return self._ollama_generate(question, schema_context)
            elif self.provider == "openai":
                return self._openai_generate(question, schema_context)
            elif self.provider == "azure":
                return self._azure_generate(question, schema_context)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            # Automatic fallback to mock provider
            return self._mock_generate(question, schema_context)
    
    def health_check(self) -> Tuple[bool, str]:
        """Check if LLM provider is available"""
        try:
            self.client.ping()
            return (True, f"{self.provider} is healthy")
        except:
            return (False, f"{self.provider} is unreachable")
```

**Configuration:**

```bash
# .env
LLM_PROVIDER=ollama  # ollama, openai, azure, anthropic
OLLAMA_MODEL=mistral:latest
OLLAMA_BASE_URL=http://localhost:11434

OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4

AZURE_OPENAI_ENDPOINT=https://...
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_DEPLOYMENT=gpt-4
```

---

### 4.5 Superset Integration (BI Layer - Peer Service)

**Relationship:** Superset is a **peer service**, not managed by FastAPI backend.

**Integration Points:**

#### A. Shared Database Connection
- Superset connects to same PostgreSQL/ClickHouse as FastAPI
- Queries dbt-built models for dashboards
- No direct API calls to FastAPI

#### B. Metrics Endpoint (Optional)

```python
# app/api/v1/routes/analytics.py
@router.get("/api/v1/analytics/metrics")
async def get_system_metrics():
    """
    Expose system metrics for Superset dashboards
    """
    return {
        "total_queries_today": await get_query_count(today),
        "active_users_now": await get_active_users(),
        "avg_query_latency_ms": await get_avg_latency(),
        "top_tables_queried": await get_top_tables()
    }
```

#### C. Embedded Dashboards (Optional)

```python
# Frontend can embed Superset dashboards via iframe
<iframe src="https://superset.example.com/superset/dashboard/1/" />
```

---

## 5. Operational Flow

### 5.1 End-to-End Request Flow

```
1. User Input (UI Layer)
   └─ User asks: "What were total sales last month?"
   └─ Frontend: POST /api/v1/sql/generate

2. API Gateway (FastAPI)
   ├─ CorrelationIDMiddleware: Generate/extract correlation_id
   ├─ JWT Authentication: Verify token, extract user
   ├─ RBAC Authorization: Check user has 'analyst' role
   └─ Rate Limiter: Check user hasn't exceeded quota

3. NL-to-SQL Pipeline (Backend)
   ├─ Stage 1: Interpret
   │   └─ Intent: aggregate, metric=sales, timeframe=last_month
   ├─ Stage 2: Generate
   │   ├─ Retrieve context: dbt models, ontology
   │   ├─ Build prompt: "Generate SQL for total sales last month using fct_sales model"
   │   ├─ Call LLM: Ollama/OpenAI via UnifiedLLMAdapter
   │   └─ Raw SQL: "SELECT SUM(amount) FROM fct_sales WHERE DATE_TRUNC('month', order_date) = ..."
   ├─ Stage 3: Validate
   │   ├─ Query Firewall: ✅ No DDL/DML
   │   ├─ Syntax Check: ✅ Valid SQL
   │   └─ RBAC Check: ✅ User can access fct_sales
   ├─ Stage 4: Optimize
   │   └─ Add index hint, check execution plan
   ├─ Stage 5: Sanitize
   │   └─ No PII detected in WHERE clause
   ├─ Stage 6: Execute
   │   ├─ DatabaseConnector: Run SQL
   │   ├─ Results: {"total_sales": 1234567.89}
   │   ├─ Cache in Redis: cache:qry-12345
   │   └─ Save to query_history table
   └─ Stage 7: Explain
       └─ "Total sales last month: $1,234,567.89"

4. Response Return (FastAPI → UI)
   └─ JSON response:
       {
         "query_id": "qry-12345",
         "sql": "SELECT SUM(amount) FROM fct_sales...",
         "results": [{"total_sales": 1234567.89}],
         "explanation": "Total sales last month: $1,234,567.89",
         "execution_time_ms": 142,
         "correlation_id": "corr-abc123"
       }

5. User Review (UI Layer)
   └─ User sees results, validates correctness

6. Feedback Loop (Optional)
   └─ If incorrect:
       ├─ User: POST /api/v1/feedback/flag
       ├─ Backend: Store feedback, tag for review
       └─ Admin: Review, approve correction, retrain model
```

### 5.2 System Startup Sequence

```
1. Environment Validation
   ├─ Load .env via SecureEnvironmentManager
   ├─ Decrypt encrypted values (Fernet AES-128)
   └─ Validate required vars present

2. Component Initialization
   ├─ DatabaseConnector: Test PostgreSQL connection
   ├─ Redis: Verify cache availability
   ├─ ChromaDB: Check vector store
   ├─ UnifiedLLMAdapter: Health check LLM provider
   └─ DBTRunner: Verify dbt project exists

3. Health Score Calculation
   ├─ DB: 40%, LLM: 30%, Redis: 15%, Vector: 15%
   └─ Determine operational mode

4. Operational Mode Selection
   ├─ Score ≥ 85%: FULL_OPERATIONAL
   ├─ Score 60-84%: LIMITED_AI
   ├─ Score 40-59%: READ_ONLY
   └─ Score < 40%: EMERGENCY

5. Background Tasks Startup
   ├─ Celery worker: Start task queue
   ├─ Celery beat: Start scheduled tasks
   └─ dbt sync task: Schedule daily at 2 AM

6. API Server Launch
   ├─ FastAPI app: Bind to port 8000
   ├─ Health endpoint: /health returns 200 OK
   └─ Metrics endpoint: /metrics exports Prometheus metrics

7. Ready for Requests
   └─ Log: "FastAPI backend ready. Mode: FULL_OPERATIONAL, Health: 95%"
```

### 5.3 Error Handling & Recovery

**Error Categories:**

| Error Type | Handling | User Impact |
|------------|----------|-------------|
| **LLM Unavailable** | Fallback to mock provider | Warning: "Using fallback, accuracy may be reduced" |
| **Database Down** | Switch to READ_ONLY mode | Error: "Query execution unavailable" |
| **dbt Tests Failed** | Continue, show warning | Warning: "Data quality issues detected" |
| **Rate Limit Exceeded** | Return 429 Too Many Requests | Error: "Request limit exceeded, try again in 60s" |
| **Invalid SQL Generated** | Re-attempt with refined prompt | Transparent retry, user sees nothing |
| **Query Timeout** | Cancel query, log error | Error: "Query took too long, please refine" |

**Automatic Recovery:**

```python
# app/core/system_manager.py
class SystemManager:
    def handle_component_failure(self, component: str):
        """Automatically adjust operation mode on failure"""
        
        if component == "llm":
            self.set_mode("LIMITED_AI")
            logger.warning("LLM failed, switched to LIMITED_AI mode")
        
        elif component == "database":
            self.set_mode("READ_ONLY")
            logger.error("Database failed, switched to READ_ONLY mode")
        
        elif component == "redis":
            # Continue without caching
            logger.warning("Redis failed, caching disabled")
        
        # Trigger alert to ops team
        self.send_alert(component, "CRITICAL")
```

---

## 6. Data Contracts & Input/Output Specifications

### 6.1 Primary Inputs Required for Setup

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `DB_HOST` | PostgreSQL host | `localhost` | Yes |
| `DB_NAME` | Database name | `datamind_ai` | Yes |
| `DB_USER` | Database user | `admin` | Yes |
| `DB_PASSWORD` | Database password | `<encrypted>` | Yes |
| `LLM_PROVIDER` | LLM service | `ollama` / `openai` | Yes |
| `OLLAMA_MODEL` | Ollama model name | `mistral:latest` | If Ollama |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` | If OpenAI |
| `ENCRYPTION_KEY` | Fernet key for .env | Auto-generated | Yes |
| `API_TOKEN` | Backend security token | Auto-generated | Yes |
| `DBT_PROJECT_PATH` | Path to dbt project | `/dbt` | Yes |
| `REDIS_URL` | Redis connection | `redis://localhost:6379` | Yes |

**All sensitive values encrypted in `.env` via SecureEnvManager.**

### 6.2 API Input/Output Contracts

#### Generate SQL Endpoint

**Request:**
```http
POST /api/v1/sql/generate
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "question": "How many active users from USA last month?",
  "context": {
    "user_role": "analyst",
    "department": "sales"
  }
}
```

**Response:**
```json
{
  "query_id": "qry-12345",
  "sql": "SELECT COUNT(*) FROM dim_users WHERE status='active' AND country='USA' AND DATE_TRUNC('month', created_at) = DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')",
  "explanation": "This query counts all active users from the USA who were created last month.",
  "confidence_score": 0.92,
  "correlation_id": "corr-abc123",
  "generated_at": "2025-11-12T14:30:00Z"
}
```

#### Execute SQL Endpoint

**Request:**
```http
POST /api/v1/sql/execute
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "sql": "SELECT COUNT(*) FROM dim_users WHERE status='active'",
  "query_id": "qry-12345"
}
```

**Response:**
```json
{
  "query_id": "qry-12345",
  "results": [
    {"count": 3847}
  ],
  "rows_returned": 1,
  "execution_time_ms": 142,
  "explanation": "Found 3,847 active users.",
  "correlation_id": "corr-abc123"
}
```

#### Feedback Endpoint

**Request:**
```http
POST /api/v1/feedback/flag
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "query_id": "qry-12345",
  "comment": "SQL is using wrong table, should use fct_users_aggregated",
  "rating": 2
}
```

**Response:**
```json
{
  "feedback_id": "fb-67890",
  "status": "flagged_for_review",
  "message": "Feedback submitted successfully. An admin will review this query.",
  "correlation_id": "corr-abc123"
}
```

---

## 7. Security & Governance Framework

### 7.1 Authentication & Authorization

**Authentication:**
- JWT tokens (HS256 algorithm)
- Refresh token rotation
- Token expiry: Access 15min, Refresh 7 days
- Password hashing: bcrypt (12 rounds)

**Authorization (RBAC):**

| Role | Permissions |
|------|-------------|
| **viewer** | View shared results, read-only access |
| **analyst** | Generate SQL, execute queries, submit feedback |
| **admin** | All analyst permissions + approve feedback, manage training data, configure system |

**Implementation:**

```python
# app/api/dependencies.py
from fastapi import Depends, HTTPException
from app.core.security.auth import decode_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Extract user from JWT token"""
    payload = decode_jwt(token)
    user = await get_user_by_id(payload["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

async def require_analyst(user: User = Depends(get_current_user)) -> User:
    """Require analyst or admin role"""
    if user.role not in ["analyst", "admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return user

async def require_admin(user: User = Depends(get_current_user)) -> User:
    """Require admin role"""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
```

### 7.2 Query Firewall

**Purpose:** Prevent destructive or unauthorized operations

**Blocked Patterns:**

```python
# app/core/query_validator.py
BLOCKED_KEYWORDS = [
    "DROP", "TRUNCATE", "DELETE", "INSERT", "UPDATE",
    "ALTER", "CREATE", "GRANT", "REVOKE",
    "EXEC", "EXECUTE", "xp_cmdshell"
]

def validate_query(sql: str) -> Tuple[bool, str]:
    """Check if SQL is safe to execute"""
    
    sql_upper = sql.upper()
    
    # Check for blocked keywords
    for keyword in BLOCKED_KEYWORDS:
        if keyword in sql_upper:
            return (False, f"Blocked keyword detected: {keyword}")
    
    # Check for multiple statements (SQL injection attempt)
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

### 7.3 PII Masking

**Automatic Detection & Masking:**

```python
# app/core/security/masking.py
import re

PII_PATTERNS = {
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
    "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"
}

def mask_pii(text: str) -> str:
    """Mask PII in text"""
    for pii_type, pattern in PII_PATTERNS.items():
        text = re.sub(pattern, f"[{pii_type.upper()}_MASKED]", text)
    return text
```

**Applied to:**
- Log entries
- Query results (optional, configurable)
- Audit trail entries
- Error messages

### 7.4 Audit Logging

**Complete Audit Trail:**

```python
# app/core/audit_logger.py
import json
from datetime import datetime, timezone

def log_audit_event(
    event_type: str,
    user: User,
    component: str,
    status: str,
    details: dict = None,
    correlation_id: str = None
):
    """Log audit event in structured format"""
    
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,  # query_execution, feedback_submit, config_change
        "user_id": user.id,
        "user_email": mask_pii(user.email),
        "component": component,  # db_connector, llm_adapter, api_gateway
        "status": status,  # success, failed, blocked
        "ip_address": request.client.host,
        "correlation_id": correlation_id,
        "details": details or {}
    }
    
    # Write to audit log file
    with open("logs/audit.log", "a") as f:
        f.write(json.dumps(event) + "\n")
    
    # Also store in database for querying
    db.audit_log.insert(event)
```

**Logged Events:**
- Query generation
- Query execution
- Feedback submission
- Training data changes
- Configuration updates
- Authentication attempts
- Authorization failures

---

## 8. Observability & Monitoring

### 8.1 Structured Logging

**Format:** JSON with correlation IDs

```json
{
  "timestamp": "2025-11-12T14:30:00.123Z",
  "level": "INFO",
  "service": "fastapi-backend",
  "component": "sql_generator",
  "correlation_id": "corr-abc123",
  "user_id": "user-456",
  "message": "SQL generated successfully",
  "details": {
    "question": "How many active users?",
    "sql_length": 145,
    "confidence_score": 0.92
  }
}
```

**Log Levels:**

| Level | Use Case | Examples |
|-------|----------|----------|
| **DEBUG** | Development details | "Retrieved 47 dbt models from manifest" |
| **INFO** | Normal operations | "Query executed successfully in 142ms" |
| **WARNING** | Recoverable issues | "Redis cache miss, querying database" |
| **ERROR** | Failures requiring attention | "LLM provider unreachable, using fallback" |
| **CRITICAL** | System-wide failures | "Database connection pool exhausted" |

### 8.2 Health Checks

**Endpoint:** `GET /health`

**Response:**

```json
{
  "status": "healthy",
  "version": "6.2.0",
  "operational_mode": "FULL_OPERATIONAL",
  "health_score": 95,
  "components": {
    "database": {
      "status": "healthy",
      "latency_ms": 12,
      "connection_pool": "8/10 active"
    },
    "llm": {
      "status": "healthy",
      "provider": "ollama",
      "model": "mistral:latest",
      "latency_ms": 1847
    },
    "redis": {
      "status": "healthy",
      "memory_used": "245MB",
      "cache_hit_rate": 0.78
    },
    "vector_db": {
      "status": "healthy",
      "collection_size": 3847,
      "index_type": "HNSW"
    },
    "dbt": {
      "status": "healthy",
      "last_run": "2025-11-12T02:00:00Z",
      "tests_passed": true
    }
  },
  "uptime_seconds": 14567,
  "timestamp": "2025-11-12T14:30:00Z"
}
```

### 8.3 Prometheus Metrics

**Endpoint:** `GET /metrics`

**Exported Metrics:**

```
# Query metrics
http_requests_total{method="POST", endpoint="/api/v1/sql/generate", status="200"}
query_generation_latency_seconds{quantile="0.5"}
query_generation_latency_seconds{quantile="0.95"}
query_generation_latency_seconds{quantile="0.99"}
query_execution_latency_seconds{quantile="0.95"}

# System metrics
system_health_score{operational_mode="FULL_OPERATIONAL"}
database_connection_pool_active
database_connection_pool_idle
redis_cache_hit_rate
llm_generation_success_rate

# Business metrics
active_users_count
total_queries_today
feedback_flagged_count
training_data_size
```

**Grafana Dashboard:**
- Query latency over time
- Error rate trends
- Active users
- System health score
- Component availability

---

## 9. Technology Stack

### 9.1 Core Backend

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Web Framework | FastAPI | 0.109.2 | Async HTTP API server |
| ASGI Server | Uvicorn | 0.27.1 | Production ASGI server |
| Settings | pydantic-settings | 2.1.0 | Configuration management |
| Validation | Pydantic | 2.5.3 | Data validation |

### 9.2 Database & ORM

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| SQL Database | PostgreSQL | 16 | Primary data store (OLTP) |
| Analytical DB | ClickHouse | 24.x | High-performance analytics (Phase 2) |
| ORM | SQLAlchemy | 2.0.27 | Database abstraction |
| Driver | psycopg2-binary | 2.9.9 | PostgreSQL connectivity |
| Migrations | Alembic | 1.13.1 | Schema versioning |

### 9.3 AI & NL Processing

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| SQL Generation | Vanna | 0.5.5 | Trained SQL generation |
| LLM (Local) | Ollama | Latest | On-premise LLM inference |
| LLM (Cloud) | OpenAI, Anthropic, Google | Latest | Cloud LLM providers |
| Embeddings | ChromaDB | 0.4.22 | Vector storage & search |
| NLP | NLTK | 3.8.1 | Text processing |

### 9.4 Caching & Message Queues

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Cache/Broker | Redis | 7.0 | Session cache, Celery broker |
| Task Queue | Celery | 5.3.4 | Background jobs |
| Job Monitoring | Flower | 2.0.1 | Celery web dashboard |

### 9.5 Data Transformation

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Transformation | dbt-core | 1.7.x | SQL model orchestration |
| PostgreSQL Adapter | dbt-postgres | 1.7.x | dbt → PostgreSQL |
| ClickHouse Adapter | dbt-clickhouse | 1.6.x | dbt → ClickHouse (Phase 2) |

### 9.6 Security

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| JWT Tokens | python-jose | 3.3.0 | Token encoding/decoding |
| Password Hashing | passlib (bcrypt) | 1.7.4 | Secure password storage |
| Encryption | cryptography | 42.0.5 | Fernet (AES-128) for .env |
| SQL Parsing | sqlparse | 0.4.4 | SQL syntax validation |

### 9.7 Monitoring & Logging

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Structured Logging | python-json-logger | 2.0.7 | JSON log output |
| Metrics | prometheus-client | 0.19.0 | Prometheus metrics export |

### 9.8 Testing

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Test Framework | pytest | 8.0.0 | Unit & integration tests |
| Async Testing | pytest-asyncio | 0.23.5 | Async test support |
| Fake Data | Faker | 22.6.0 | Test data generation |
| Coverage | pytest-cov | 4.1.0 | Code coverage reporting |

### 9.9 Deployment

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Containers | Docker, Docker Compose | Local & staging deployment |
| Orchestration | Kubernetes | Production deployment |
| CI/CD | GitHub Actions | Automated testing & deployment |

---

## 10. Implementation Phases

### Phase 0: Foundation (Weeks 1-4)

**Goal:** Core FastAPI backend with 7-stage NL-to-SQL pipeline

**Deliverables:**
- ✅ FastAPI app with JWT authentication
- ✅ PostgreSQL database with core tables
- ✅ 7-stage pipeline (Interpret → Generate → Validate → Optimize → Sanitize → Execute → Explain)
- ✅ Vanna OSS integration with Ollama
- ✅ Query Firewall and PII masking
- ✅ Health checks and basic monitoring
- ✅ Docker Compose setup

**Testing:**
- Unit tests: 80%+ coverage
- Integration tests: All endpoints
- E2E test: NL question → SQL → Results

**Success Criteria:**
- Can generate SQL from natural language
- Can execute SQL securely
- Can explain results in natural language
- All security features active

---

### Phase 1: Frontend Integration (Weeks 5-8)

**Goal:** Connect backend to Streamlit/React UI

**Deliverables:**
- ✅ REST API fully documented (OpenAPI)
- ✅ Frontend communicates with backend via JWT
- ✅ User can ask questions, see results
- ✅ Feedback submission working
- ✅ Query history displayed

**Testing:**
- UI/UX testing
- API contract testing
- Performance testing (50 concurrent users)

**Success Criteria:**
- Non-technical users can query data
- Feedback loop functional
- Sub-3s query latency

---

### Phase 2: dbt Integration (Weeks 9-14)

**Goal:** Native dbt integration with automated training

**Deliverables:**
- ✅ dbt project with 10-20 core models
- ✅ Backend queries dbt models, not raw tables
- ✅ Automated daily sync: dbt manifest → Vanna training
- ✅ dbt test results exposed in health endpoint
- ✅ Admin can trigger dbt run/test from UI

**Testing:**
- dbt tests: All models passing
- Training sync: Verified daily
- Query accuracy: 90%+ on test suite

**Success Criteria:**
- 40-60% reduction in SQL generation errors
- Data quality warnings working
- Consistent business logic

---

### Phase 3: Superset & Advanced Analytics (Weeks 15-20)

**Goal:** BI dashboards and reporting

**Deliverables:**
- ✅ Superset deployed and connected
- ✅ 5-10 pre-built dashboards
- ✅ Metrics endpoint for Superset
- ✅ Embedded dashboards in UI (optional)
- ✅ ClickHouse migration path documented

**Testing:**
- Dashboard performance
- Data consistency checks
- Superset API integration

**Success Criteria:**
- Dashboards load in <2s
- Data matches query results
- Analysts using Superset regularly

---

### Phase 4: ClickHouse Migration (Conditional - Weeks 21-26)

**Trigger Conditions:**
- Data volume > 500GB
- Query latency > 3s (P95)
- 50K+ daily active users

**Deliverables:**
- ✅ ClickHouse cluster deployed
- ✅ dbt re-targeted to ClickHouse
- ✅ Data sync: PostgreSQL → ClickHouse
- ✅ Query router: analytical → ClickHouse, transactional → PostgreSQL
- ✅ Performance benchmarks

**Testing:**
- Migration testing (data integrity)
- Performance benchmarks
- Rollback procedures

**Success Criteria:**
- 10x faster analytical queries
- 50-60% cost reduction
- Zero downtime migration

---

## 11. Expected Outcomes & Success Metrics

### 11.1 Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Query Success Rate** | ≥ 90% | Successful SQL generation / Total attempts |
| **System Health** | ≥ 85% | Weighted component availability |
| **Query Latency (P95)** | < 3 seconds | End-to-end: NL question → Results |
| **Query Latency (P50)** | < 1 second | Median response time |
| **Governance Coverage** | 100% | All queries logged, auditable |
| **Concurrent Users** | 50+ | Simultaneous API requests |
| **Data Accuracy** | 95% | Consistency with dbt models |
| **Feedback Response Time** | < 24 hours | Admin review of flagged queries |

### 11.2 Business Outcomes

**Year 1:**
- 70% reduction in time-to-insight for analysts
- 50% reduction in support tickets for data access
- 30% increase in data-driven decisions
- 100% audit compliance (SOC2, GDPR)

**Year 2:**
- 500+ active users (analysts + stakeholders)
- 10,000+ queries per day
- 95%+ user satisfaction
- 3x ROI on platform investment

### 11.3 Technical Outcomes

**Reliability:**
- 99.5% uptime (SLA)
- <0.1% query failure rate
- Automatic recovery from component failures

**Scalability:**
- 10x data volume growth without degradation
- 50+ concurrent users → 500+ (Phase 4)
- Linear cost scaling with usage

**Maintainability:**
- <1 hour for minor updates
- <4 hours for major releases
- Complete rollback capability

---

## 12. Development & Maintenance Notes

### 12.1 Operational Rules

1. **FastAPI is the Single Gateway** - All external/internal communication goes through backend
2. **No Direct Database Access** - All queries via secure DatabaseConnector
3. **All Changes Logged** - Configuration changes via Audit Logger
4. **Continuous Validation** - Health checks and integration tests
5. **Document Everything** - All fixes in error_registry.md or CHANGELOG.md

### 12.2 Security Checklist

- [ ] All `.env` values encrypted via SecureEnvManager
- [ ] JWT tokens expire (15min access, 7 days refresh)
- [ ] Query Firewall active and tested
- [ ] PII masking applied to logs and results
- [ ] RBAC enforced on all endpoints
- [ ] Audit logging complete and tamper-proof
- [ ] Rate limiting configured
- [ ] HTTPS enforced in production
- [ ] Database connection pooling configured
- [ ] Secrets never in version control

### 12.3 Monitoring Checklist

- [ ] Prometheus metrics endpoint active
- [ ] Grafana dashboards configured
- [ ] Alerting rules defined
- [ ] Log aggregation setup (ELK/Datadog)
- [ ] Health checks passing
- [ ] Correlation IDs in all logs
- [ ] Uptime monitoring (Pingdom/UptimeRobot)

### 12.4 Backup & Disaster Recovery

**PostgreSQL:**
- Daily automated backups
- Point-in-time recovery enabled
- 30-day retention
- Tested restore procedures

**Configuration:**
- `.env` backed up (encrypted)
- dbt project in version control
- Docker images tagged and stored

**Recovery Time Objectives:**
- RTO (Recovery Time): < 4 hours
- RPO (Recovery Point): < 1 hour

---

## 13. Conclusion

The **DataMind AI** platform represents a fully aligned, enterprise-ready data intelligence ecosystem, with the **FastAPI backend** serving as the foundation for operational reliability and analytical intelligence.

### 13.1 Architecture Summary

- **Headless Backend** - FastAPI as central orchestration hub
- **Data Factory** - dbt produces Single Source of Truth
- **Multi-LLM Support** - Ollama (local), OpenAI, Azure, Anthropic
- **Phased Scalability** - PostgreSQL → ClickHouse migration
- **Complete Governance** - Audit trails, query firewall, RBAC
- **Continuous Learning** - Feedback loop improves accuracy

### 13.2 Key Achievements

✅ **Seamless Integration** - dbt, Superset, ClickHouse, UI clients  
✅ **Future Scalability** - Advanced AI integrations ready  
✅ **Complete Transparency** - Detailed logging, auditable workflows  
✅ **Enterprise Security** - Encrypted config, validated queries, role-based access  
✅ **Operational Excellence** - Health scoring, automatic recovery, monitoring

### 13.3 Next Steps

1. **Review this document** with architecture team
2. **Validate technology choices** with stakeholders
3. **Begin Phase 0 implementation** per roadmap
4. **Set up development environment** per setup guide
5. **Execute testing strategy** per test plan

---

**End of Document — DataMind AI Unified System Overview & FastAPI Backend Integration Framework**

---

**Document Status:**  
**Version:** 6.2 Final  
**Date:** November 12, 2025  
**Status:** Production-Ready, For Implementation  
**Next Review:** Post-Phase 1 Completion

**Changes from v6.1:**
- ✅ Integrated DataMind AI system overview
- ✅ Added complete operational flow documentation
- ✅ Detailed integration architecture for all components
- ✅ Expanded security and governance framework
- ✅ Added input/output specifications
- ✅ Comprehensive success metrics and outcomes
- ✅ Complete technology stack with versions
- ✅ Phased implementation roadmap
- ✅ Development and maintenance guidelines

---

**For questions or clarifications:**
- Architecture: Tech Lead
- Integration: System Architect
- Security: Security Engineer
- Implementation: Project Manager

---

## 13. Enterprise Feature Matrix & Roadmap Alignment

### 13.1 Capability Overview

| Capability | APIs | Backing Tables / Services | Notes |
|------------|------|---------------------------|-------|
| Semantic Layer | `/api/v1/semantic/*` | `semantic_models`, `semantic_metrics`, dbt `schema.yml` | Compiler produces YAML + Vanna training payloads; context injected into Stage 1–2 of NL→SQL pipeline. |
| Project Management & Templates | `/api/v1/projects*` | `projects`, `project_memberships`, `project_templates` | Governs NL→SQL access and drives boilerplate provisioning (templates stored as JSON). |
| User Management Enhancements | `/api/v1/users/*` | `user_groups`, `user_group_memberships` | Extends RBAC, enabling group-scoped project access and data policies. |
| Data Control Engine | `/api/v1/data-control/policies*` | `data_policies`, `policy_bindings` | Policies cached inside `DataPolicyEngine`, executed before validation/execution pipeline stages. |
| Metrics Registry | `/api/v1/metrics/*` | `metric_definitions`, YAML at `ontology/metrics.yaml` | Registry feeds both semantic prompt context and dashboard/spreadsheet engines. |
| Dashboard Manager | `/api/v1/dashboards*` | `dashboards`, `dashboard_panels` | Publishes to Superset/adapter defined by `DASHBOARD_ADAPTER`. |
| Spreadsheet Engine | `/api/v1/spreadsheets*` | `spreadsheets`, `spreadsheet_cells` | AI formulas generated through `VannaClient.generate_formula`, row-level governance enforced by project & policies. |
| Usage Monitoring | `/api/v1/usage/*` | `usage_events`, `UsageMonitoringService` | Feeds System Manager score, Observability exporters, and SLA dashboards. |

### 13.2 Component Interaction Summary

```
Projects/User Mgmt ───┐
                      │ membership context
                      ▼
               Data Policy Engine ──────► SQLService (NL→SQL Stages 1-7)
                      ▲                         │
Semantic Compiler ────┘                         │ enriched prompt
          │                                      ▼
          └─► Metrics Registry ─► Prompt Context + Dashboard Manager

Spreadsheet Engine ─► VannaClient.generate_formula ─► SQLService (optional execution)
Usage Monitoring ◄─┴─ SQLService, Dashboards, Spreadsheets (event hooks)
```

### 13.3 Operational Considerations

- **SLAs**: Semantic compiles must finish <5 minutes, policy cache TTL <= `POLICY_CACHE_SECONDS`, dashboard publish action <10 seconds to keep CI/CD green.
- **Backwards compatibility**: All new routers live under `/api/v1/*` with their own auth dependencies; legacy clients remain unaffected.
- **Governance Loop**: Policies + usage analytics flow into the same audit tables referenced by VANNA governance specs, closing the loop with dbt and RAG feedback.
- **Observability**: `UsageMonitoringService` is wired into Prometheus via existing middleware; new events are surfaced under the `usage_events_total` counter and summarized via the `/api/v1/usage/summary` endpoint.

These additions extend the system’s headless architecture into a full enterprise analytics fabric without disrupting the existing Streamlit/UI clients or the 7-Stage NL→SQL pipeline.

### 13.4 API Tree (Reference)

```
/api/v1/
    semantic/interpret | semantic/models        ← طبقة دلالية
    entities/          ← الكيانات التجارية
    dimensions/, hierarchies/, filters/, glossary/
    compiler/compile   ← محرك التحويل الدلالي
    metrics/, metrics/templates, metrics/import
    projects/, projects/{id}
    dashboards/, dashboards/{id}/publish
    spreadsheets/, spreadsheets/{id}/ai-fill, sql-sync
    users/, users/{id}/assign-role, users/{id}/groups
    policies/, policies/rows, policies/columns
    security/audit-log, security/sessions, security/ip-restrictions, ...
    usage/summary, usage/users, usage/queries, usage/dashboards, usage/llm-tokens
```

هذا المخطط هو المرجع الرسمي قبل أي تطوير إضافي، والـ FastAPI backend الحالي يحقق هذه الهيكلية بشكل مباشر.
