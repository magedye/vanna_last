# VANNA_OSS_INTEGRATION.md

**Vanna OSS Integration & Governance Specification**

---

## Document Information

| Property | Value |
|----------|-------|
| **Specification Version** | 1.0 |
| **Project** | Vanna Insight Engine (FastAPI Backend) |
| **Status** | For Implementation |
| **Date** | November 12, 2025 |
| **Purpose** | Complete backend integration of Vanna OSS functions |
| **Scope** | API Endpoints, Function Mapping, Workflows, Governance |

---

## Table of Contents

1. [Overview](#1-overview)
2. [Vanna OSS Function Mapping](#2-vanna-oss-function-mapping)
3. [Core Analytic API Endpoints](#3-core-analytic-api-endpoints)
4. [Governance & Feedback API Endpoints](#4-governance--feedback-api-endpoints)
5. [Operational Workflows](#5-operational-workflows)
6. [Pydantic Schemas](#6-pydantic-schemas)
7. [Integration Best Practices](#7-integration-best-practices)

---

## 1. Overview

This specification defines the complete technical integration of the **Vanna OSS library** into the Vanna Insight Engine FastAPI backend.

**Primary Goal:** Map every Vanna OSS function to a corresponding FastAPI endpoint or internal service, establishing a robust **"Feedback-to-Training" governance workflow**.

---

## 2. Vanna OSS Function Mapping

| Vanna OSS Function | Purpose | FastAPI Implementation |
|-------------------|---------|----------------------|
| `vn.generate_sql` | Generate SQL from natural language | `POST /api/v1/sql/generate` |
| `vn.run_sql` | Execute SQL against database | `POST /api/v1/sql/execute` |
| `vn.fix_sql` | Auto-correct failed SQL | `POST /api/v1/sql/fix` |
| `vn.generate_summary` | NL summary of results | `POST /api/v1/sql/summarize` |
| `vn.generate_followup_questions` | Suggest related questions | `GET /api/v1/sql/{query_id}/followup` |
| `vn.get_related_ddl` | Retrieve DDL for context | **Internal Service** |
| `vn.get_related_documentation` | Retrieve docs for context | **Internal Service** |
| `vn.train` | Add (question, SQL) pair | Multiple endpoints (feedback, approve, add) |
| `vn.get_training_data` | Retrieve training entries | `GET /api/v1/admin/training-data` |
| `vn.remove_training_data` | Delete training pair by ID | `DELETE /api/v1/admin/training-data/{id}` |
| `vn.connect_to_*` | Establish DB connections | **Internal Service** |
| `vn.train(documentation=...)` | Ingest semantic/glossary docs from dbt | Triggered via `POST /api/v1/semantic/compile` |
| `vn.submit_prompt` (wrapped by `VannaClient.generate_formula`) | AI spreadsheet formula synthesis | `POST /api/v1/spreadsheets/formula`, `/spreadsheets/{id}/ai-formula` |
| `vn.semantic_interpret` (heuristic) | Map NL question → metric/dimension/filter | `POST /api/v1/semantic/interpret` |
| `vn.semantic_compile` | Convert semantic definition → SQL | `POST /api/v1/compiler/compile` |

---

## 3. Core Analytic API Endpoints

### POST /api/v1/sql/fix

**Description:** Auto-correct SQL based on database error

**Request Schema:**
```python
class SQLFixRequest(BaseModel):
    sql: str = Field(..., description="The broken SQL query")
    error_msg: str = Field(..., description="The database error message")
```

**Response Schema:**
```python
class SQLGenerationResponse(BaseModel):
    query_id: int
    sql: str
    confidence: float
    explanation: str
```

### POST /api/v1/sql/summarize

**Description:** Generate natural language summary of query and results

**Request Schema:**
```python
class SQLSummaryRequest(BaseModel):
    sql: Optional[str] = Field(None, description="SQL query to summarize")
    query_id: Optional[int] = Field(None, description="Alternatively, query ID")
```

**Response Schema:**
```python
class ExplanationResponse(BaseModel):
    query_id: int
    summary: str
    key_findings: List[str]
```

### GET /api/v1/sql/{query_id}/followup

**Description:** Suggest follow-up questions

**Response Schema:**
```python
class FollowupQuestionsResponse(BaseModel):
    query_id: int
    original_question: str
    followup_questions: List[str]
```

---

## 4. Governance & Feedback API Endpoints

### 4.1 User Feedback (Analyst Role)

#### POST /api/v1/feedback/flag

**Purpose:** Flag incorrect query for admin review

**Vanna Function:** `vn.train(question, sql, tag="flagged_for_review")`

**Request Schema:**
```python
class FlagFeedbackRequest(BaseModel):
    query_id: int = Field(..., description="Query ID from queries table")
    comment: str = Field(..., description="Feedback explaining issue")
    rating: Optional[int] = Field(None, ge=1, le=5, description="1-5 star rating")
```

**Response Schema:**
```python
class FeedbackResponse(BaseModel):
    id: int
    message: str = "Feedback submitted and tagged for review"
    vanna_action: str = "train_flagged"
```

### 4.2 Admin Governance Endpoints (Admin Role)

#### GET /api/v1/admin/training-data

**Purpose:** Retrieve all training data (filterable by tag)

**Query Parameters:**
- `tag` (optional) - Filter by tag (e.g., `flagged_for_review`)

**Response Schema:**
```python
class TrainingDataResponse(BaseModel):
    id: str
    question: str
    sql: str
    tag: Optional[str] = None
```

#### POST /api/v1/admin/training-data/approve

**Purpose:** Approve corrected SQL - CORE GOVERNANCE ACTION

**Vanna Functions:**
1. `vn.train(question, corrected_sql)` - Add correct pair
2. `vn.remove_training_data(id)` - Remove incorrect pair

**Request Schema:**
```python
class ApproveFeedbackRequest(BaseModel):
    flagged_entry_id: str = Field(..., description="Entry to remove")
    question: str = Field(..., description="Original question")
    corrected_sql: str = Field(..., description="New correct SQL")
```

**Response Schema:**
```python
class TrainingDataResponse(BaseModel):
    id: str
    question: str
    sql: str
    tag: Optional[str]
```

#### DELETE /api/v1/admin/training-data/{id}

**Purpose:** Permanently delete training pair

**Response:** `204 No Content`

#### POST /api/v1/admin/schema/reload

**Purpose:** Trigger full schema reload into Vanna model

**Response:** `202 Accepted` (async task)

#### GET /api/v1/admin/feedback/metrics

**Purpose:** Return metrics on training data state

**Response Schema:**
```python
class FeedbackMetricsResponse(BaseModel):
    total_training_entries: int
    flagged_for_review_count: int
    approval_ratio: float
    last_sync: str
```

---

## 5. Operational Workflows

### Workflow A: User Flags Incorrect Query

```
1. User (Analyst) receives generated SQL (Query ID: qry_123)
2. User finds results incorrect
3. User submits POST /api/v1/feedback/flag
   {
     "query_id": "qry_123",
     "comment": "This SQL is wrong",
     "rating": 1
   }
4. Backend receives request:
   a. Looks up qry_123 in queries table
   b. Calls vn.train(question=question, sql=generated_sql, tag="flagged_for_review")
   c. Saves feedback comment to feedback table
5. Result: Incorrect pair tagged for admin review, won't be used for new queries
```

### Workflow B: Admin Reviews and Approves

```
1. Admin calls GET /api/v1/admin/training-data?tag=flagged_for_review
2. Backend calls vn.get_training_data() and filters by tag
3. Admin reviews list, identifies incorrect entry (ID: train_abc)
4. Admin writes corrected SQL
5. Admin submits POST /api/v1/admin/training-data/approve:
   {
     "flagged_entry_id": "train_abc",
     "question": "Original question text",
     "corrected_sql": "SELECT ... -- correct SQL"
   }
6. Backend actions:
   a. Calls vn.train(question, corrected_sql) - adds CORRECT pair
   b. Calls vn.remove_training_data(id=train_abc) - removes INCORRECT pair
7. Result: Model trained on correct SQL, feedback loop closed
```

---

## 6. Pydantic Schemas

Complete schema definitions for all endpoints:

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# ===== SQL GENERATION =====

class SQLFixRequest(BaseModel):
    sql: str = Field(..., description="The broken SQL query")
    error_msg: str = Field(..., description="Database error message")

class SQLSummaryRequest(BaseModel):
    sql: Optional[str] = Field(None, description="SQL query to summarize")
    query_id: Optional[int] = Field(None, description="Query ID to summarize")

class SQLGenerationResponse(BaseModel):
    query_id: int
    sql: str
    confidence: float
    explanation: str

class ExplanationResponse(BaseModel):
    query_id: int
    summary: str
    key_findings: List[str]

class FollowupQuestionsResponse(BaseModel):
    query_id: int
    original_question: str
    followup_questions: List[str]

# ===== FEEDBACK & GOVERNANCE =====

class FlagFeedbackRequest(BaseModel):
    query_id: int = Field(..., description="Query ID to flag")
    comment: str = Field(..., description="Feedback text")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating 1-5")

class FeedbackResponse(BaseModel):
    id: int
    message: str = "Feedback submitted and tagged for review"
    vanna_action: str = "train_flagged"
    timestamp: datetime

class TrainingDataResponse(BaseModel):
    id: str = Field(..., description="Unique ID from Vanna vector store")
    question: str
    sql: str
    tag: Optional[str] = Field(None, description="Governance tag")
    created_at: Optional[datetime] = None

class ApproveFeedbackRequest(BaseModel):
    flagged_entry_id: str = Field(..., description="Entry to remove")
    question: str = Field(..., description="Original/edited question")
    corrected_sql: str = Field(..., description="New correct SQL")

class FeedbackMetricsResponse(BaseModel):
    total_training_entries: int
    flagged_for_review_count: int
    approval_ratio: float
    last_sync: datetime
```

---

## 7. Integration Best Practices

### 7.1 Error Handling

```python
@router.post("/api/v1/sql/generate")
async def generate_sql(request: NLQuestionRequest):
    try:
        # Generate SQL
        result = await vn.generate_sql(request.question)
        return {"success": True, "data": result}
    except LLMGenerationError as e:
        return {"success": False, "error": str(e), "status": 500}
    except DatabaseError as e:
        return {"success": False, "error": "Database unavailable", "status": 503}
```

### 7.2 Logging

```python
# Every Vanna call should be logged
logger.info(
    "SQL Generated",
    extra={
        "query_id": query_id,
        "question": question,
        "sql": sql,
        "confidence": confidence,
        "user_id": user_id
    }
)
```

### 7.3 Monitoring

```python
# Track key metrics
metrics.counter("vanna.sql_generated", tags={"status": "success"})
metrics.histogram("vanna.generation_latency", value=elapsed_time)
metrics.gauge("vanna.training_entries_total", value=total_count)
```

---

## Implementation Checklist

- [ ] All API endpoints implemented
- [ ] Pydantic schemas defined
- [ ] Vanna OSS library integrated
- [ ] Feedback-to-training loop tested
- [ ] Admin governance endpoints secured
- [ ] Error handling comprehensive
- [ ] Logging/monitoring in place
- [ ] Documentation complete

---

**Status:** ✅ Ready for Implementation

**End of VANNA_OSS_INTEGRATION.md**

---

## 8. Enterprise Extensions & Semantic Workflows

### 8.1 Semantic Compiler ↔ Vanna

- `SemanticLayerService.compile_from_dbt()` persists each dbt model as `*.semantic.yaml` then calls `VannaClient.train(documentation=doc)` to load business descriptions, hierarchies, and metrics into the existing Chroma-backed RAG store.
- Compiled models are exposed through `/api/v1/semantic/models` so frontend clients can reason about available semantics and present curated question starters.
- All generated prompts include policy clauses + registry metrics, which improves Vanna’s intent recognition and reduces hallucinations inside Stages 1–3 of the NL→SQL pipeline.

### 8.2 Spreadsheet Engine

- `/api/v1/spreadsheets/formula` leverages the new `VannaClient.generate_formula()` helper (thin wrapper on `vn.submit_prompt`) so analysts receive governed formulas that reference semantic metrics.
- Formulas + cell values are stored in `spreadsheet_cells`, and each cell edit runs through `DataPolicyEngine` to ensure masked columns are never surfaced.

### 8.3 Dashboard & Metrics Registry

- `MetricsRegistryService.sync_from_yaml()` keeps `metric_definitions` aligned with dbt metrics; these definitions are reused by dashboards and the semantic compiler to maintain “single source of metric truth”.
- The dashboard publish endpoint reuses existing Vanna integrations (semantic context + usage telemetry) to provide downstream BI with accurate SQL definitions.

### 8.4 Governance Hooks

- Usage events (`/api/v1/usage/events`) and policy CRUD operations emit audit logs that match the patterns described in Section 5 of this document.
- Every enterprise endpoint adheres to the same RBAC abstractions (`get_current_user`, `get_current_admin_user`, `get_analyst_or_admin`) so Vanna’s governance loop remains closed regardless of client entry point.

### 8.5 Semantic Catalog APIs

| Asset | Endpoint |
|-------|----------|
| Entities / Business Ontology | `/api/v1/entities` |
| Dimensions | `/api/v1/dimensions` |
| Hierarchies | `/api/v1/hierarchies` |
| Filters | `/api/v1/filters` |
| Glossary | `/api/v1/glossary` |
| Compiler | `/api/v1/compiler/compile` |

هذه النقاط هي المرجع الرسمي قبل أي تكامل إضافي مع Vanna OSS أو أي عميل خارجي.
