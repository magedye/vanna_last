# DBT_INTEGRATION_STRATEGY.md

**Analytical Transformation Layer - dbt Integration Strategy**

---

## Document Information

| Property | Value |
|----------|-------|
| **Specification Version** | 1.0 |
| **Project** | Vanna Insight Engine (FastAPI Backend) |
| **Status** | For Implementation |
| **Date** | November 12, 2025 |
| **Purpose** | Strategic integration of dbt as data transformation layer |
| **Scope** | Consumption, Training, Governance, Implementation |

---

## Table of Contents

1. [Strategic Opinion](#1-strategic-opinion)
2. [Integration Architecture](#2-integration-architecture)
3. [Core Integration Points](#3-core-integration-points)
4. [New Backend Components](#4-new-backend-components)
5. [Implementation Roadmap](#5-implementation-roadmap)
6. [Best Practices](#6-best-practices)

---

## 1. Strategic Opinion

### The Complementary Architecture

The integration of **dbt** is **not a replacement** for the Vanna Insight Engine; it is a **perfect complement**.

| Layer | Role | Purpose |
|-------|------|---------|
| **dbt (Factory)** | Transformation | Transforms raw data into clean, tested models (e.g., `fct_orders`, `dim_customers`) |
| **Vanna (Storefront)** | Consumption | Provides NL-to-SQL capability to access the SSOT |

**Result:** Vanna transitions from querying raw data to querying trusted, pre-modeled, documented data, dramatically improving accuracy and governance.

---

## 2. Integration Architecture

### Operational Flow

```
┌─────────────────────────────┐
│   Raw Data Warehouse        │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ dbt (Transform, Test, Docs) │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────┐
│ Clean Data Warehouse        │
│ (dbt Models: fct_*, dim_*)  │
└──────────────┬──────────────┘
               ↓
┌──────────────────────────────────┐
│ Vanna Insight Engine (Backend)   │
│ 1. Train on dbt docs (manifest)  │
│ 2. Connect to clean warehouse    │
└──────────────┬───────────────────┘
               ↓
┌─────────────────────────────┐
│ User Request (NL-to-SQL)    │
└──────────────┬──────────────┘
               ↓
┌─────────────────────────────────┐
│ Vanna-Generated SQL             │
│ (Querying dbt Models)           │
└─────────────────────────────────┘
```

---

## 3. Core Integration Points

### 3.1 Consumption: dbt Produces, Vanna Consumes

**Problem:** Querying raw tables requires complex multi-join SQL, which is slow and error-prone.

**Solution:**
```
dbt creates clean models
    ↓
Vanna connects to dbt models
    ↓
User asks: "What were total sales last month?"
    ↓
Vanna generates: SELECT SUM(amount) FROM fct_orders...
```

**Benefit:** 40-60% reduction in SQL generation errors

### 3.2 Training: Automated Vanna Training via dbt Artifacts

**Most Powerful Integration Point**

**dbt produces:** `manifest.json` and `catalog.json` - machine-readable artifacts with all model/column documentation

**Implementation:**
1. Celery task reads `manifest.json` daily
2. Iterates through models and columns
3. Trains Vanna on documentation: `vn.train(documentation="...")`
4. Result: Vanna knowledge automatically synced with dbt SSOT

**Benefit:** Data engineers update column description in dbt → Vanna learns automatically next day

### 3.3 Governance: Unification of Metrics

**Challenge:** User asks for "profit margin" but Vanna calculates it incorrectly

**Solution:**
1. Data team defines "profit margin" **once** in dbt model
2. Vanna trained on dbt docs knows this metric exists
3. User asks "profit margin" → Vanna generates simple `SELECT avg_profit_margin FROM...`

**Benefit:** 70-85% improvement in governance

### 3.4 Data Quality-Aware Responses (Advanced)

**Feature:** dbt supports data quality checks (`dbt test`)

**Implementation:** SystemManager checks last `dbt test` results

**Benefit:** API warns user if key model failed quality checks: *"Sales data failed quality tests today"*

---

## 4. New Backend Components

### 4.1 New Service: services/dbt_runner.py

**Purpose:** Interface for backend to trigger dbt commands

```python
"""
Vanna Insight Engine – dbt Runner Service
Purpose: Execute dbt commands from backend
"""
import subprocess
from pathlib import Path
from app.config import settings

class DBTRunner:
    def __init__(self, project_path: str = settings.DBT_PROJECT_PATH):
        self.project_path = Path(project_path)
    
    def run_models(self, models: list = None) -> dict:
        """Execute dbt run command"""
        cmd = ["dbt", "run"]
        if models:
            cmd.extend(["--select", " ".join(models)])
        
        result = subprocess.run(
            cmd,
            cwd=self.project_path,
            capture_output=True,
            text=True
        )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    
    def test_models(self) -> dict:
        """Execute dbt test command"""
        result = subprocess.run(
            ["dbt", "test"],
            cwd=self.project_path,
            capture_output=True,
            text=True
        )
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "errors": result.stderr
        }
    
    def generate_docs(self) -> dict:
        """Generate dbt documentation"""
        result = subprocess.run(
            ["dbt", "docs", "generate"],
            cwd=self.project_path,
            capture_output=True,
            text=True
        )
        
        return {
            "success": result.returncode == 0,
            "docs_path": str(self.project_path / "target")
        }
```

### 4.2 New Celery Task: tasks/dbt_sync_task.py

**Purpose:** Automated training on dbt artifacts

```python
"""
Vanna Insight Engine – dbt Sync Task
Purpose: Synchronize dbt documentation with Vanna training
"""
from celery import shared_task
import json
from pathlib import Path
from app.core.vanna_integration.client import VannaClient

@shared_task(bind=True, max_retries=3)
def sync_dbt_to_vanna(self):
    """
    Scheduled task: Reads dbt manifest.json, trains Vanna on all models
    Runs daily at 2 AM UTC
    """
    try:
        manifest_path = Path("/dbt/target/manifest.json")
        
        if not manifest_path.exists():
            raise FileNotFoundError("dbt manifest not found")
        
        with open(manifest_path) as f:
            manifest = json.load(f)
        
        vn = VannaClient()
        trained_count = 0
        
        # Extract all models
        for node_id, node in manifest.get("nodes", {}).items():
            if node["resource_type"] == "model":
                model_name = node["name"]
                description = node.get("description", "")
                columns = node.get("columns", {})
                
                # Train on model
                if description:
                    vn.train(documentation=f"Model: {model_name} - {description}")
                
                # Train on columns
                for col_name, col_data in columns.items():
                    col_desc = col_data.get("description", "")
                    if col_desc:
                        vn.train(documentation=f"Column {col_name} in {model_name}: {col_desc}")
                
                trained_count += 1
        
        return {
            "status": "success",
            "models_trained": trained_count,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60 * 2 ** self.request.retries)
```

### 4.3 Configuration Variables

**Update .env:**
```bash
# dbt Integration
DBT_PROJECT_PATH=./dbt_project
DBT_MANIFEST_PATH=./dbt_project/target/manifest.json
DBT_TARGET=production
DBT_SYNC_SCHEDULE=0 2 * * *  # Daily at 2 AM UTC
```

### 4.4 Admin API Endpoints

**Trigger dbt runs from backend:**

```python
# app/api/v1/routes/admin.py
@router.post("/admin/dbt/run")
async def trigger_dbt_run(
    models: list = None,
    admin: User = Depends(get_current_admin)
):
    """Trigger dbt run"""
    runner = DBTRunner()
    result = runner.run_models(models=models)
    return {"status": "success", "result": result}

@router.post("/admin/dbt/test")
async def trigger_dbt_test(admin: User = Depends(get_current_admin)):
    """Trigger dbt test"""
    runner = DBTRunner()
    result = runner.test_models()
    return {"status": "success", "result": result}
```

---

## 5. Implementation Roadmap

### Phase 1: Vanna Standalone (MVP)

**Duration:** Months 1-3

**Goals:**
- Deploy Vanna without dbt
- Connect directly to existing tables
- Validate core NL-to-SQL pipeline
- Establish feedback loop

**Deliverables:**
- Working FastAPI backend
- Query generation functional
- Feedback mechanism implemented

### Phase 2: dbt Foundation (Core Integration)

**Duration:** Months 4-6

**Goals:**
- Build foundational dbt project (5-10 core models)
- Point Vanna to dbt models
- Implement automated training sync
- Achieve 80/20 benefit

**Deliverables:**
- dbt project with core models
- Automated sync working
- Improved SQL accuracy (40-60% fewer errors)

### Phase 3: Full Integration (Enterprise)

**Duration:** Months 7-12

**Goals:**
- Implement dbt_runner service
- Integrate data quality checks
- Expand dbt project coverage
- Production-ready governance

**Deliverables:**
- Complete dbt coverage
- Quality-aware API responses
- 70-85% governance improvement

---

## 6. Best Practices

### 6.1 dbt Project Structure

```
dbt_project/
├── dbt_project.yml          # Project config
├── profiles.yml             # Connection config
├── models/
│   ├── staging/            # Raw layer
│   │   └── stg_*.sql
│   ├── intermediate/       # Transformation layer
│   │   └── int_*.sql
│   └── marts/              # Business layer
│       ├── fact_*.sql
│       └── dim_*.sql
├── macros/                 # Reusable SQL
├── tests/                  # Data quality tests
├── docs/                   # Documentation
├── target/                 # Generated (manifest.json, catalog.json)
└── seeds/                  # Static data
```

### 6.2 Model Documentation

```yaml
# models/marts/fact_orders.yml
version: 2

models:
  - name: fact_orders
    description: "Aggregated daily order facts"
    columns:
      - name: order_id
        description: "Unique order identifier (primary key)"
        tests:
          - unique
          - not_null
      - name: order_date
        description: "Date order was placed"
      - name: total_amount
        description: "Total order value in USD"
        tests:
          - not_null
```

### 6.3 Quality Tests

```yaml
tests:
  - name: orders_have_revenue
    description: "Orders must have positive revenue"
    SQL: |
      SELECT * FROM {{ ref('fact_orders') }}
      WHERE total_amount <= 0
```

---

## Expected Benefits

| Metric | Impact | Timeframe |
|--------|--------|-----------|
| **SQL Error Rate** | 40-60% reduction | Phase 2 |
| **Query Latency** | 20-30% improvement | Phase 2 |
| **Governance** | 70-85% improvement | Phase 3 |
| **Time to New Model** | 75% faster | Phase 3 |
| **Data Quality Awareness** | 100% coverage | Phase 3 |

---

## Success Metrics

- ✅ All dbt models properly documented
- ✅ Automated training syncs daily
- ✅ SQL generation accuracy improved 40%+
- ✅ Data quality tests passing 95%+
- ✅ Zero destructive SQL generated
- ✅ Governance audit trail complete

---

**Implementation Status:** Ready for Phase 1

**Next Steps:**
1. Approve dbt project structure
2. Set up development dbt environment
3. Create first 5 core models
4. Begin Phase 2 planning

---

**End of DBT_INTEGRATION_STRATEGY.md**

---

## 7. Semantic Alignment & Policy Surface

### 7.1 Semantic YAML Overlay

`SemanticCompiler` now auto-generates `*.semantic.yaml` files per dbt model. Example output:

```yaml
semantic_model: sales_performance
version: v1
source_model: fct_orders
metrics:
  - name: total_revenue
    expression: "SUM(net_amount)"
    agg: sum
    tags: [core, finance]
dimensions:
  - name: order_date
    data_type: date
    grain: day
filters:
  - name: region_filter
    expression: "region = '{{region}}'"
    default_value: GLOBAL
hierarchies:
  - name: geo_hierarchy
    levels: [continent, country, state]
```

These artifacts are stored under `ontology/semantic_models/` and mirrored into the new SQLAlchemy tables for runtime lookups.

### 7.2 Policy + Metric Propagation

- dbt metrics (`metrics/*.yml`) are ingested by `MetricsRegistryService.sync_from_yaml()` and surfaced via `/api/v1/metrics/definitions`.
- Row/column-level policies reference dbt metadata (tags/grains) and are enforced inside `SQLService` prior to Stage 3 (Validate) and Stage 6 (Execute). The policy engine ensures dbt quality gates apply even when NL→SQL routes around Superset.

### 7.3 Operational Guardrails

- `SEMANTIC_REFRESH_SECONDS` controls how frequently dbt manifests are re-ingested.
- Semantic compiles produce `UsageEvent` entries so ops teams can monitor data freshness alongside dbt test runs (`dbt test` status is still captured by System Manager).
- Any compile error includes the associated dbt model reference and fails fast rather than allowing stale docs to pollute the Vanna embeddings.

### 7.4 Exposed Catalog APIs

| dbt Artifact | FastAPI Endpoint | Consumer |
|--------------|------------------|----------|
| Models / Columns | `/api/v1/entities`, `/api/v1/dimensions`, `/api/v1/hierarchies` | UI + Semantic Compiler |
| Metrics YAML | `/api/v1/metrics`, `/api/v1/metrics/templates`, `/api/v1/metrics/import` | Catalog + Governance |
| Documentation / Descriptions | `/api/v1/glossary` | Business glossary synchronization |

بهذا الشكل تصبح ملفات dbt المصدر الوحيد لكل ما يتاح عبر الطبقة الدلالية داخل Vanna Insight Engine.
