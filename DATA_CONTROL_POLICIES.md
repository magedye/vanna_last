# DATA_CONTROL_POLICIES.md

## Document Metadata

| Property | Value |
|----------|-------|
| Version | 1.0 |
| Scope | Data Policy Engine, RLS/CLS, Policy APIs |
| Owners | Security & Governance |
| Updated | Nov 27, 2025 |

## 1. Overview

Data control policies enforce row-level and column-level security for every NL→SQL request, dashboard, spreadsheet, or AI formula execution. Policies are centrally managed through `/api/v1/data-control/policies` and cached inside `DataPolicyEngine` to guarantee predictable latency.

## 2. Architecture Diagram

```
Policy Admin API (/api/v1/data-control/policies)
             │
             ▼
        DataPolicyService ─────┐
             │ writes rows     │ cache
             ▼                 ▼
       data_policies + policy_bindings  ──> DataPolicyEngine.evaluate()
                                                      │
                                                      ▼
                                        SQLService.generate/execute_sql
```

## 3. Components

| Component | Responsibility | Key Files |
|-----------|----------------|-----------|
| DataPolicyService | CRUD operations, role association, preview | `app/modules/data_control/service.py` |
| DataPolicyEngine | Evaluate policies, build prompt context, validate executions | `app/modules/data_control/policy_engine.py` |
| API Routes | Expose admin endpoints | `app/api/v1/routes/data_control.py` |
| Schemas | Validate requests/responses | `app/api/v1/schemas/data_control.py` |

## 4. APIs

### GET /api/v1/data-control/policies
- **Auth**: Admin only.
- **Response**: `PolicyResponse[]` with `policy_type`, `predicate_sql`, `column_mask`, `priority`.

### POST /api/v1/data-control/policies
- **Request**: `PolicyCreateRequest` (`name`, `policy_type ∈ {row,column,deny}`, optional `predicate_sql`, `column_mask`, `roles[]`).
- **Behavior**: Persists policy, creates bindings per role, invalidates cache.

### POST /api/v1/data-control/policies/{id}/preview
- **Response**: `PolicyPreviewResponse` returning normalized predicate/mask for UI display.

## 5. Data Model

| Table | Fields | Notes |
|-------|--------|-------|
| `data_policies` | `id`, `name`, `policy_type`, `predicate_sql`, `column_mask[]`, `priority`, `created_at` | Core policy definitions |
| `policy_bindings` | `id`, `policy_id`, `role`, `column_name`, `priority` | Many-to-many between policies and roles or columns |

## 6. Runtime Behavior

1. `SQLService.generate_sql()` calls `DataPolicyEngine.build_policy_context()` to emit human-readable statements for the prompt.
2. After SQL generation, `DataPolicyEngine.evaluate()` returns `PolicyEvaluationResult` (clauses + masked columns). Clauses are appended to SQL via `_append_policy_filters` before Stage 4 (Optimize).
3. Before execution, `DataPolicyEngine.validate_execution()` ensures no deny policies are violated.
4. `UsageMonitoringService` records any policy hits for auditing.

## 7. SLAs & Error Handling

- **Policy cache TTL**: `POLICY_CACHE_SECONDS` (default 300s). Cache invalidated on create/update.
- **Latency budget**: Policy evaluation must add <50ms per request; expensive clauses should be pushed down to dbt models when possible.
- **Errors**: Violation → HTTP 403 with policy name; unknown policy id → HTTP 404; invalid inputs → HTTP 422.

## 8. Integration

- Works with `projects` and `user_groups` to scope policies by role and project membership.
- Policies can include placeholders referencing semantic models or dbt tags (documented in YAML metadata) to keep enforcement declarative.
- Audit logs and `usage_events` capture policy enforcement for compliance reporting.

## 9. Folder Structure

```
app/modules/data_control/
├── __init__.py
├── models.py            # dataclasses for PolicyEvaluationResult
├── policy_engine.py     # runtime evaluator
└── service.py           # CRUD + preview helpers
```

All policy changes must be reviewed along with updated documentation and regression tests targeting `SQLService`.

## 10. Canonical `/api/v1/policies/*` Endpoints

| Endpoint | Purpose | Example Payload |
|----------|---------|-----------------|
| `POST /api/v1/policies/rows` | Define RLS condition per role | `{"role": "analyst", "condition": "region = 'EMEA'"}` |
| `POST /api/v1/policies/columns` | Mask/obfuscate sensitive columns | `{"table": "dim_customer", "column": "email", "mask": "SHA256_HASH", "roles": ["viewer"]}` |
| `GET /api/v1/policies` | Alias لـ `/api/v1/data-control/policies` لضمان التوافق مع مواصفات الـ API العليا | n/a |

هذه المسارات هي المرجع الرسمي لتفعيل سياسات التحكم بالبيانات ضمن الطبقة الخلفية.
