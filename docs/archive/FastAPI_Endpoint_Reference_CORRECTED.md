# FastAPI Endpoint Reference (Corrected)

Authoritative reference for the current FastAPI implementation under `vanna-engine/app`. All details are derived directly from the source code listed below and supersede previous design documents.

- **Source routers inspected:** `app/api/v1/routes/{core,auth,sql_public,sql,feedback,db_admin,admin}.py`
- **Schemas:** `app/api/v1/schemas/{common,sql,feedback}.py`, `app/schemas.py`
- **Rate limiting:** `app/core/rate_limiting.py`
- **Settings defaults:** `app/config.py`

## Endpoint Summary Table

| Method | Path | Category | Auth | Status |
| --- | --- | --- | --- | --- |
| GET | `/` | Core | None | Stable |
| GET | `/health` | Core | None | Stable |
| GET | `/metrics` | Core | None | Stable |
| GET | `/metrics/json` | Core | None | Stable |
| POST | `/api/v1/auth/login` | Auth | None | Stable |
| POST | `/api/v1/auth/signup` | Auth | None | Stable |
| POST | `/api/v1/generate-sql` | Public SQL | None | Stable |
| POST | `/api/v1/fix-sql` | Public SQL | None | Stable |
| POST | `/api/v1/explain-sql` | Public SQL | None | Stable |
| POST | `/api/v1/sql/generate` | Auth SQL | Bearer JWT | Stable |
| POST | `/api/v1/sql/validate` | Auth SQL | Bearer JWT | Stable |
| POST | `/api/v1/sql/execute` | Auth SQL | Bearer JWT | Stable |
| GET | `/api/v1/sql/history` | Auth SQL | Bearer JWT | Stable |
| POST | `/api/v1/feedback` | Feedback | Bearer JWT | Stable |
| GET | `/api/v1/feedback/{query_id}` | Feedback | Bearer JWT | Stable |
| POST | `/api/v1/feedback/train` | Feedback | Bearer JWT | Stable |
| POST | `/admin/db/chroma/train` | Admin DB/DevOps | Admin JWT | Experimental |
| GET | `/admin/db/chroma/status/{task_id}` | Admin DB/DevOps | Admin JWT | Experimental |
| GET | `/admin/db/chroma/knowledge-base` | Admin DB/DevOps | Admin JWT | Experimental |
| DELETE | `/admin/db/chroma/clear` | Admin DB/DevOps | Admin JWT | Experimental |
| GET | `/admin/db/health` | Admin DB/DevOps | Admin JWT | Stable |
| GET | `/admin/db/target/health` | Admin DB/DevOps | Admin JWT | Stable |
| POST | `/admin/db/target/test` | Admin DB/DevOps | Admin JWT | Stable |
| GET | `/admin/db/stats` | Admin DB/DevOps | Admin JWT | Stable |
| POST | `/admin/db/backup` | Admin DB/DevOps | Admin JWT | Experimental |
| GET | `/admin/db/backup/status/{task_id}` | Admin DB/DevOps | Admin JWT | Experimental |
| GET | `/admin/db/backup/list` | Admin DB/DevOps | Admin JWT | Stable |
| POST | `/admin/db/backup/restore/{backup_filename}` | Admin DB/DevOps | Admin JWT | Experimental |
| GET | `/admin/config` | Admin Config | Admin JWT | Stable |
| POST | `/admin/config` | Admin Config | Admin JWT | Stub |
| POST | `/admin/approve-sql` | Admin Config | Admin JWT | Stub |
| GET | `/admin/feedback-metrics` | Admin Config | Admin JWT | Stable |
| POST | `/admin/scheduled/create` | Admin Config | Admin JWT | Stub |
| GET | `/admin/scheduled/list` | Admin Config | Admin JWT | Stub |
| DELETE | `/admin/scheduled/{report_id}` | Admin Config | Admin JWT | Stub |
| GET | `/vanna/` | Agent Chat | Bearer JWT | Stable |
| POST | `/vanna/api/vanna/v2/chat_sse` | Agent Chat (SSE) | Bearer JWT | Stable |
| WebSocket | `/vanna/api/vanna/v2/chat_websocket` | Agent Chat (Realtime) | Bearer JWT | Stable |
| POST | `/vanna/api/vanna/v2/chat_poll` | Agent Chat (Polling) | Bearer JWT | Stable |

## Legend

| Status | Meaning |
| --- | --- |
| `Stable` | Fully implemented and exercised endpoints. |
| `Experimental` | Implemented but rely on asynchronous tasks or destructive admin flows — use with caution. |
| `Stub` | Route exists but only returns a “planned” message. |

## System Overview

- **Default base URL:** `http://0.0.0.0:8000`
- **Version:** `settings.VERSION` (defaults to `1.0.0`)
- **OpenAPI docs:** `/docs`, `/redoc`, `/openapi.json`
- **Authentication:** HTTP `Authorization: Bearer <JWT>` created via `/api/v1/auth/login`
  - Regular auth: `get_current_user` (`app/api/dependencies.py:54-111`)
  - Admin auth: `get_current_admin_user` (same file, requires `user.role == "admin"`)
- **Correlation IDs:** injected by `CorrelationIDMiddleware`; every success/error payload includes a `correlation_id`

### Error Format

`ErrorResponse` in `app/api/v1/schemas/common.py` defines the global error body:

```json
{
  "error": "Descriptive error message",
  "correlation_id": "<uuid>"
}
```

No `error_code` or `timestamp` fields are emitted.

### Rate Limiting

- Limits configured in `app/core/rate_limiting.py`
  - Public SQL (`/api/v1/generate-sql`, `/fix-sql`, `/explain-sql`): **100/hour** per IP (`settings.PUBLIC_SQL_RATE_LIMIT`)
  - Authenticated SQL + Feedback POST endpoints: **500/hour** per authenticated user
  - Admin endpoints currently do **not** apply SlowAPI decorators
- Only a `Retry-After` response header is set when a limit is exceeded; there are no `X-RateLimit-*` headers.

---

## Core (Public)

### GET `/` — Stable
- **Auth:** None
- **Status codes:** `200`
- **Rate limit:** None
- **Request shape:** `n/a`
- **Response shape:** `{ "message": str, "docs": "/docs", "redoc": "/redoc", "openapi": "/openapi.json", "health": "/health", "metrics": "/metrics" }`

### GET `/health` — Stable
- **Auth:** None
- **Status codes:** `200`
- **Request shape:** `n/a`
- **Response shape (`HealthResponse`):** `{ "status": "healthy|degraded|unhealthy", "version": str, "providers_active": int, "dependencies": {"postgres": bool, "redis": bool, "chroma": bool}, "features": {"circuit_breaker": bool, "correlation_ids": bool, "failover": bool} }`

### GET `/metrics` — Stable
- **Auth:** None
- **Status codes:** `200`
- **Request shape:** `n/a`
- **Response shape:** Prometheus text exposition (`text/plain; version=0.0.4`).

### GET `/metrics/json` — Stable
- **Auth:** None
- **Status codes:** `200`
- **Request shape:** `n/a`
- **Response shape:** `{ "app_info": {"version": str, "name": str}, "providers_total": int, "service_status": "healthy|degraded|unhealthy", "dependencies": {"postgres": bool, "redis": bool, "chroma": bool}, "features": {"circuit_breaker": bool, "correlation_ids": bool, "failover": bool} }`

---

## Authentication (`/api/v1/auth`)

### POST `/api/v1/auth/login` — Stable
- **Auth:** None
- **Status codes:** `200`, `400`, `401`, `403`, `500`
- **Request shape (`LoginRequest`):** `{ "username": str, "password": str }`
- **Response shape (`LoginResponse`):** `{ "access_token": str, "token_type": "bearer", "user_id": str, "username": str }`
- **Notes:** Validates credentials against `User`. 401 for bad credentials, 403 for inactive accounts.

### POST `/api/v1/auth/signup` — Stable
- **Auth:** None
- **Status codes:** `200`, `400`, `500`
- **Request shape (`SignupRequest`):** `{ "username": str, "password": str, "full_name": str, "recovery_email": str|null }`
- **Response shape (`SignupResponse`):** `{ "user_id": str, "username": str, "full_name": str, "message": "User created successfully" }`
- **Notes:** Default role `viewer`; rejects duplicate usernames.

---

## Public SQL (`/api/v1`, rate limited 100/hour)

### POST `/api/v1/generate-sql` — Stable
- **Auth:** None
- **Status codes:** `200`, `400`, `500`
- **Request shape (`GenerateSQLRequest`):** `{ "question": str }`
- **Response shape (`SQLResponse`):** `{ "sql": str, "correlation_id": str, "status": "success" }`

### POST `/api/v1/fix-sql` — Stable
- **Auth:** None
- **Status codes:** `200`, `400`, `500`
- **Request shape (`FixSQLRequest`):** `{ "sql": str, "error_msg": str }`
- **Response shape:** `SQLResponse`

### POST `/api/v1/explain-sql` — Stable
- **Auth:** None
- **Status codes:** `200`, `500`
- **Request shape (`ExplainSQLRequest`):** `{ "sql": str }`
- **Response shape (`ExplanationResponse`):** `{ "explanation": str, "correlation_id": str, "status": "success" }`

---

## Authenticated SQL (`/api/v1/sql`, rate limited 500/hour on POST)

> Requires a valid Bearer JWT (viewer/analyst/admin). Missing/invalid tokens trigger `401`, inactive users trigger `403`.

### POST `/api/v1/sql/generate` — Stable
- **Status codes:** `200`, `400`, `401`, `403`, `500`
- **Request shape (`SQLGenerationRequest`):** `{ "question": str, "schema_name": str|null, "force_rule_based": bool }`
- **Response shape (`SQLGenerationResponse`):** `{ "sql": str, "correlation_id": str, "confidence": float, "intent": {"query_type": str, "entities": dict, "filters": list, "confidence": float}, "warnings": list[str], "status": "success" }`

### POST `/api/v1/sql/validate` — Stable
- **Status codes:** `200`, `401`, `403`, `500`
- **Request shape (`SQLValidationRequest`):** `{ "sql": str, "question_id": str|null }`
- **Response shape (`SQLValidationResponse`):** `{ "is_valid": bool, "correlation_id": str, "issues": [ { "severity": str, "message": str, "line": int|null } ], "status": "success" }`

### POST `/api/v1/sql/execute` — Stable
- **Status codes:** `200`, `400`, `401`, `403`, `500`
- **Request shape (`SQLExecutionRequest`):** `{ "question": str, "sql": str, "parameters": dict, "limit": int }`
- **Response shape (`SQLExecutionResponse`):** `{ "rows": list[dict], "columns": list[str], "row_count": int, "execution_time_ms": float, "correlation_id": str, "cached": bool, "status": "success" }`

### GET `/api/v1/sql/history` — Stable
- **Status codes:** `200`, `401`, `403`, `500`
- **Query params:** `limit` (int, default `10`)
- **Response shape:** `list[ { "id": str, "question": str, "generated_sql": str, "status": str, "execution_time_ms": int|null, "created_at": datetime } ]`
- **Notes:** No support for `offset` or `status` filters.

---

## Feedback & RLHF (`/api/v1/feedback*`, POST rate limited 500/hour)

### POST `/api/v1/feedback` — Stable
- **Status codes:** `200`, `401`, `403`, `404`, `500`
- **Request shape (`FeedbackRequest`):** `{ "query_id": str, "question": str, "rating": int (1-5), "comment": str|null, "approved_for_training": bool }`
- **Response shape (`FeedbackResponse`):** `{ "feedback_id": str, "query_id": str, "status": "recorded" }`

### GET `/api/v1/feedback/{query_id}` — Stable
- **Status codes:** `200`, `401`, `403`, `500`
- **Request shape:** `Path param query_id`
- **Response shape (`FeedbackListResponse`):** `{ "query_id": str, "feedback_items": [ { "id": str, "query_id": str, "rating": int|null, "comment": str|null, "approved_for_training": bool, "created_at": datetime } ], "total_count": int }`
- **Notes:** Returns a collection, not a single item.

### POST `/api/v1/feedback/train` — Stable
- **Status codes:** `200`, `401`, `403`, `500`
- **Request shape (`TrainingRequestSchema`):** `{ "feedback_ids": list[str]|null, "description": str|null }`
- **Response shape (`TrainingResponse`):** `{ "training_id": str, "status": "queued", "items_count": int, "message": str, "schema_version": str|null }`
- **Notes:** No analyst-only restriction; any authenticated user may request training as long as they own the feedback.

---

## Admin – Database & DevOps (`/admin/db`, Admin JWT required)

### POST `/admin/db/chroma/train` — Experimental
- **Status codes:** `202`, `401`, `403`, `500`
- **Request shape:** `none`
- **Response shape:** `{ "status": "queued", "task_id": str, "message": str, "status_url": str }`
- **Notes:** Queues `train_chroma_from_target_db` Celery task.

### GET `/admin/db/chroma/status/{task_id}` — Experimental
- **Status codes:** `200`, `401`, `403`, `500`
- **Request shape:** `Path param task_id`
- **Response shape:** `{ "task_id": str, "status": "pending|training|completed|failed|retrying", "progress": int, "message": str }`

### GET `/admin/db/chroma/knowledge-base` — Experimental
- **Status codes:** `200`, `401`, `403`, `500`
- **Request shape:** `none`
- **Response shape:** `{ "total_collections": int, "collections": [ { "name": str, "count": int, "metadata": dict } ] }`

### DELETE `/admin/db/chroma/clear` — Experimental
- **Status codes:** `200`, `400`, `401`, `403`, `500`
- **Query params:** `collection_name` (str), `confirm` (bool, must be `true`)
- **Response shape:** `{ "status": "success", "message": str, "collection": str }`

### GET `/admin/db/health` — Stable
- **Status codes:** `200`, `401`, `403`, `503`
- **Response shape:** `{ "status": "healthy", "database": str, "version": str, "connection_pool": { "size": int, "overflow": int, "checked_in": int, "checked_out": int } }`

### GET `/admin/db/target/health` — Stable
- **Status codes:** `200`, `401`, `403`, `503`
- **Response shape:** either `{ "status": "disabled", "message": str, "db_type": str }` or `{ "status": "healthy", "db_type": str, "tables_sample": list[str], "table_count_checked": int }` / `{ "probe_result": any }` depending on DB type.

### POST `/admin/db/target/test` — Stable
- **Status codes:** `200`, `400`, `401`, `403`, `503`
- **Request shape (`TargetDBTestRequest`):** combination of `db_type`, `connection_url`, or discrete connection fields (see schema).
- **Response shape:** For SQLite `{ "status": "healthy", "db_type": "sqlite", "tables_sample": list[str], "connection_url_used": str }`; for others `{ "status": "healthy", "db_type": str, "probe_result": any, "connection_url_used": str }`.

### GET `/admin/db/stats` — Stable
- **Status codes:** `200`, `401`, `403`, `500`
- **Response shape:** `{ "total_tables": int, "tables": [ { "name": str, "size": str } ] }`

### POST `/admin/db/backup` — Experimental
- **Status codes:** `202`, `401`, `403`, `500`
- **Request shape:** `none`
- **Response shape:** `{ "status": "queued", "task_id": str, "message": str, "status_url": str }`

### GET `/admin/db/backup/status/{task_id}` — Experimental
- **Status codes:** `200`, `401`, `403`, `500`
- **Response shape:** `{ "task_id": str, "status": "pending|in_progress|completed|failed|retrying", "progress": int, "result": any|null }`

### GET `/admin/db/backup/list` — Stable
- **Status codes:** `200`, `401`, `403`, `500`
- **Response shape:** `{ "total_backups": int, "backups": [ { "filename": str, "size_bytes": int, "size_mb": float, "created": float } ] }`

### POST `/admin/db/backup/restore/{backup_filename}` — Experimental
- **Status codes:** `202`, `400`, `401`, `403`, `500`
- **Query params:** `confirm` must be `true`
- **Response shape:** `{ "status": "queued", "task_id": str, "message": str, "status_url": str }`

---

## Admin – Configuration & Analytics (`/admin`, Admin JWT required)

### GET `/admin/config` — Stable
- **Status codes:** `200`, `401`, `403`, `500`
- **Response shape (`ConfigResponse`):** `{ "environment": str, "debug_mode": bool, "version": str, "features": { ... }, "llm": { "provider": str, ... } }` (fields are intentionally flexible per schema).

### POST `/admin/config` — Stub
- **Status codes:** `200`, `401`, `403`
- **Request shape:** Arbitrary config dict
- **Response shape (`ConfigUpdateResponse`):** `{ "message": "Configuration update feature is planned for future implementation", "status": "planned" }`

### POST `/admin/approve-sql` — Stub
- **Status codes:** `200`, `401`, `403`
- **Request shape:** none (approval not implemented)
- **Response shape (`AdminFeatureResponse`):** `{ "message": "SQL approval feature is planned for future implementation", "status": "planned" }`

### GET `/admin/feedback-metrics` — Stable
- **Status codes:** `200`, `401`, `403`, `500`
- **Response shape (`FeedbackMetricsResponse`):** `{ "total_feedback_count": int, "approved_for_training_count": int, "average_rating": float, "queries_with_feedback": int }`

### POST `/admin/scheduled/create` — Stub
- **Status codes:** `200`, `401`, `403`
- **Response shape:** `{ "message": "Scheduled report creation feature is planned for future implementation", "status": "planned" }`

### GET `/admin/scheduled/list` — Stub
- **Status codes:** `200`, `401`, `403`
- **Response shape (`ScheduledReportListResponse`):** `{ "message": "Scheduled reports feature is planned for future implementation", "status": "planned", "scheduled_reports": [] }`

### DELETE `/admin/scheduled/{report_id}` — Stub
- **Status codes:** `200`, `401`, `403`
- **Response shape:** `{ "message": "Scheduled report deletion feature is planned for future implementation", "status": "planned" }`

---

## Vanna Agent Chat (`/vanna`, Bearer JWT required)

These endpoints proxy to the upgraded Vanna Agent framework. Clients must include `Authorization: Bearer <JWT>` so the agent can resolve the user identity.

### GET `/vanna/` — Stable
- **Status codes:** `200`, `401`
- **Response shape:** HTML page that loads the published Vanna component bundle (override CDN via `VANNA_COMPONENT_CDN`).
- **Notes:** Handy sanity check that the agent server is mounted; responds with a lightweight UI shell.

### POST `/vanna/api/vanna/v2/chat_sse` — Stable
- **Status codes:** `200`, `401`, `403`, `500`
- **Request shape (`ChatRequest`):** `{ "message": str, "conversation_id": str|null, "request_id": str|null, "metadata": dict }`
- **Response shape:** Server-Sent Events stream. Each `data:` line is a JSON-serialized `ChatStreamChunk`. Stream terminates with `data: [DONE]`.
- **Notes:** Best option for browser-based streaming; honors the same throttling and RLS policies as the rest of the API.

### WebSocket `/vanna/api/vanna/v2/chat_websocket` — Stable
- **Status codes:** Standard WebSocket closes for auth errors or failures
- **Request shape:** First frame must contain the same JSON body as the SSE endpoint.
- **Response shape:** JSON objects mirroring `ChatStreamChunk` plus a `{ "type": "completion" }` message on success, or `{ "type": "error" }` on failure.
- **Notes:** Sends chat updates as soon as they are available and supports bidirectional instructions mid-conversation.

### POST `/vanna/api/vanna/v2/chat_poll` — Stable
- **Status codes:** `200`, `401`, `403`, `500`
- **Request shape:** Identical to `chat_sse`.
- **Response shape (`ChatResponse`):** `{ "conversation_id": str, "request_id": str, "total_chunks": int, "chunks": [ ChatStreamChunk, ... ] }`
- **Notes:** Use for cron jobs or platform integrations where long-lived connections are impractical. Each call returns the full set of chunks for the request.

---

## Mapping Hints for Frontend

- `authStore` should depend only on `user_id` and `username` from `POST /api/v1/auth/login`. No `email`, `first_name`, or role metadata is returned.
- `GET /api/v1/sql/history` accepts only the optional `limit` parameter. There is no support for `offset` or `status` filters, so pagination must happen client-side.
- `GET /api/v1/feedback/{query_id}` always returns a list (`feedback_items`) plus `total_count`, never a single feedback object. UIs should iterate the collection even if only one item is expected.

---

For backend developers and SDK builders, this document is now fully aligned with the current codebase. Frontend teams can consume it immediately thanks to the summary table, explicit status codes, and mapping hints above.
