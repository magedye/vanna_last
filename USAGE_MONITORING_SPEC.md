# USAGE_MONITORING_SPEC.md

## Metadata

| Property | Value |
|----------|-------|
| Version | 1.0 |
| Scope | Usage Event Capture, Summary APIs, Observability |
| Owners | SRE / Platform Monitoring |
| Updated | Nov 27, 2025 |

## 1. Purpose

Provide a native usage analytics layer to monitor NL→SQL throughput, dashboard adoption, spreadsheet activity, and policy hits. Data feeds System Manager health scoring, Prometheus exporters, and executive dashboards.

## 2. Architecture

```
Producers (SQLService, Dashboards, Spreadsheets, UI clients)
          │  record_event(user_id, event_type, metadata)
          ▼
UsageMonitoringService (app/modules/usage_monitoring/service.py)
          │ writes to usage_events
          ▼
/api/v1/usage/summary  ──> aggregated JSON + Prometheus metrics
```

## 3. Components

| Component | Responsibility |
|-----------|----------------|
| UsageMonitoringService | Persist events, summarize last N days | `app/modules/usage_monitoring/service.py` |
| API Routes | `/api/v1/usage/events` (POST), `/api/v1/usage/summary` (GET) | `app/api/v1/routes/usage.py` |
| Schema | Ensures metadata is a simple dict of strings | `app/api/v1/schemas/usage.py` |
| ORM Table | `usage_events` (`id`, `user_id`, `event_type`, `metadata`, `source`, `created_at`) | `app/db/models.py` |

## 4. Event Types

| Event | Producer | Metadata Keys |
|-------|----------|---------------|
| `sql_generation` | `SQLService.generate_sql` | `question`, `policy_filters` |
| `sql_execution` | `SQLService.execute_sql` | `rows` |
| `dashboard_publish` | DashboardService | `dashboard_id`, `adapter` |
| `spreadsheet_formula` | SpreadsheetService | `prompt`, `project_id` |
| Custom | `/api/v1/usage/events` | Defined by caller |

## 5. APIs

- `POST /api/v1/usage/events`
  - Auth: any authenticated user.
  - Body: `UsageEventRequest { event_type: str, metadata: Dict[str,str], source?: str }`
  - Response: `{ "status": "accepted" }` with 202 semantics.

- `GET /api/v1/usage/summary?days=7`
  - Auth: admin.
  - Response: `UsageSummaryResponse { summary: {event_type: {user_id: count}}, generated_at }`
- `GET /api/v1/usage/users|queries|dashboards|llm-tokens`
  - Auth: admin.
  - Return aggregated dict keyed by user/reference with counts (or token totals).

## 6. SLAs & Retention

- `USAGE_RETENTION_DAYS` (default 30) controls summary window. Full retention is handled at the database tier (backups + TTL policies).
- Event recording must remain non-blocking (<10ms). Failures log warnings but do not impact API responses.
- Summary endpoint should complete <250ms for 30-day window; add indexes if necessary.

## 7. Integration

- System Manager consumes summaries to adjust the health score and trigger mode changes when activity drops unexpectedly.
- Prometheus exporters consume summary data to expose `usage_events_total{event_type}` counters.
- Audit pipeline (SIEM) tail `usage_events` for compliance reporting.

## 8. Folder Layout

```
app/modules/usage_monitoring/service.py
app/api/v1/routes/usage.py
app/api/v1/schemas/usage.py
```

Usage monitoring is a foundational signal—any new enterprise module must emit events describing success/failure paths.
