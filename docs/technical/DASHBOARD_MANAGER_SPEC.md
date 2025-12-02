# DASHBOARD_MANAGER_SPEC.md

## Metadata

| Property | Value |
|----------|-------|
| Version | 1.0 |
| Scope | Dashboard CRUD, Publishing, Metrics Integration |
| Owners | Insights Platform |
| Updated | Nov 27, 2025 |

## 1. Overview

Dashboard Manager provides multi-dashboard governance independent of Superset. It stores layout JSON, connects dashboards to projects, and exposes publish flows that call downstream adapters.

## 2. Architecture Diagram

```
/api/v1/dashboards*  ──>  DashboardService  ──>  dashboards + dashboard_panels
        │                           │
        │                           ├─> Superset/adapter (publish)
        │ project membership        └─> UsageMonitoringService
        ▼
ProjectService ─────> DataPolicyEngine (for downstream SQL uses)
```

## 3. Components

| Component | Responsibility | Key Files |
|-----------|----------------|-----------|
| DashboardService | List/create dashboards, publish via adapter, enforce project RBAC | `app/modules/dashboards/service.py` |
| API Routes | `/api/v1/dashboards`, `/api/v1/dashboards/{id}/publish` | `app/api/v1/routes/dashboards.py` |
| Schemas | `DashboardResponse`, `DashboardCreateRequest`, `DashboardPublishResponse` | `app/api/v1/schemas/dashboards.py` |
| Adapter Config | `settings.DASHBOARD_ADAPTER` | `app/config.py` |

## 4. APIs

- `GET /api/v1/dashboards`: list dashboards visible to current user (filters by `project_memberships`).
- `POST /api/v1/dashboards`: create dashboard (analyst/admin). Body includes project_id, layout JSON, optional `source_model` linking to semantic model.
- `POST /api/v1/dashboards/{id}/publish`: admin-only publish; updates status → `published` and triggers adapter.
- `GET /api/v1/dashboards/{id}`: return full layout + metadata payload.
- `PATCH /api/v1/dashboards/{id}`: update name/layout/source_model/metadata_json.
- `DELETE /api/v1/dashboards/{id}`: remove dashboard (admin/owner) with audit log.

## 5. Data Model

| Table | Fields | Notes |
|-------|--------|-------|
| `dashboards` | `id`, `project_id`, `owner_id`, `name`, `layout (JSON)`, `source_model`, `status`, `metadata_json` | Layout metadata, project scoping |
| `dashboard_panels` | `dashboard_id`, `panel_key`, `query`, `visualization_type`, `position (JSON)` | Panel definitions for layout editors |

## 6. SLAs & Error Conditions

- Create/publish endpoints respond <2s; publish should log adapter output for audit.
- `publish_dashboard` raises `ValueError` when dashboard missing; FastAPI surfaces HTTP 404.
- Layout JSON validated for basic structure (panel list, config). Additional validation performed by UI before submission.

## 7. Integration Points

- Semantic metrics referenced via `source_model` ensure dashboards stay aligned with the semantic layer.
- Projects enforce RBAC, and policies can be applied downstream to SQL queries executed by dashboard panels.
- Usage events recorded when dashboards are created/published for observability.

## 8. Folder Structure

```
app/modules/dashboards/service.py
app/api/v1/routes/dashboards.py
app/api/v1/schemas/dashboards.py
```

Dashboards remain headless—the backend manages definitions while actual rendering is handled by Superset or other clients through the publish adapter.
