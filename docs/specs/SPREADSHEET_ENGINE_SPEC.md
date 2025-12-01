# SPREADSHEET_ENGINE_SPEC.md

## Metadata

| Property | Value |
|----------|-------|
| Version | 1.0 |
| Scope | Spreadsheet Engine, AI Formulas, Cell APIs |
| Owners | Analytics Enablement |
| Updated | Nov 27, 2025 |

## 1. Overview

The AI-powered spreadsheet engine provides collaborative sheets with governed access. It stores sheet schema/cell data, leverages Vanna to synthesize formulas, and respects the same policy/project constructs as NL→SQL and dashboards.

## 2. Architecture

```
/api/v1/spreadsheets/* ──> SpreadsheetService ──> spreadsheets + spreadsheet_cells
        │                               │
        │ AI formula request             └─> UsageMonitoringService
        ▼
VannaClient.generate_formula  (wraps vn.submit_prompt)
```

## 3. Components

| Component | Responsibility | Files |
|-----------|----------------|-------|
| SpreadsheetService | CRUD documents, manage cells, call Vanna for formulas | `app/modules/spreadsheets/service.py` |
| API Routes | `/api/v1/spreadsheets`, `/api/v1/spreadsheets/{id}/cells`, `/api/v1/spreadsheets/formula` | `app/api/v1/routes/spreadsheets.py` |
| Schemas | `SpreadsheetResponse`, `SpreadsheetCellRequest`, `FormulaRequest` | `app/api/v1/schemas/spreadsheets.py` |
| ORM Tables | `spreadsheets`, `spreadsheet_cells` | `app/db/models.py` |

## 4. APIs

- `GET /api/v1/spreadsheets`: list sheets accessible via project memberships.
- `POST /api/v1/spreadsheets`: create sheet (any authenticated user). Body contains `name`, optional `project_id`, optional schema JSON.
- `POST /api/v1/spreadsheets/{id}/cells`: upsert cell; enforces ownership or admin rights, applies policy engine, persists formula/value.
- `POST /api/v1/spreadsheets/formula`: generate formula from natural language prompt (calls `VannaClient.generate_formula`).
- `POST /api/v1/spreadsheets/{id}/ai-fill`: يقترح أعمدة/قيم ذكية استناداً إلى التعليمات.
- `POST /api/v1/spreadsheets/{id}/ai-formula`: يولّد معادلات خاصّة بشيت محدد ويخزنها في schema.
- `POST /api/v1/spreadsheets/{id}/sql-sync`: يسحب بيانات حديثة من SQL ويخزن الأعمدة/النتائج داخل الشيت.

## 5. Data Model

| Table | Fields |
|-------|--------|
| `spreadsheets` | `id`, `project_id`, `owner_id`, `name`, `schema (JSON)`, `is_locked`, timestamps |
| `spreadsheet_cells` | `id`, `spreadsheet_id`, `address`, `formula`, `value (JSON)`, `updated_at` |

## 6. SLAs & Safeguards

- `SPREADSHEET_MAX_CELLS` controls maximum cells per sheet (default 10k). Service must validate before insert.
- AI formula endpoint limited via rate limiting (leverages general SlowAPI middleware) and returns fallback `=SUM(A:A)` if Vanna unavailable.
- Ownership enforced; non-admin cannot modify another user’s sheet unless they share a project.

## 7. Integration & Governance

- Projects + memberships determine sheet visibility.
- DataPolicyEngine invoked before cell updates/SQL execution triggered by formulas.
- Semantic metadata + metrics registry provide context for formula generation when `FormulaRequest.context` supplied.
- Usage events recorded for sheet creation, cell updates, and AI formula generation.

## 8. Folder Layout

```
app/modules/spreadsheets/service.py
app/api/v1/routes/spreadsheets.py
app/api/v1/schemas/spreadsheets.py
```

The engine remains headless—UI clients call these APIs while rendering cell grids locally.
