# SEMANTIC_LAYER_DESIGN.md

## Document Metadata

| Property | Value |
|----------|-------|
| Version | 1.0 |
| Scope | Semantic Layer + Compiler + Registry |
| Owners | Platform Engineering / Governance |
| Updated | Nov 27, 2025 |

## 1. Overview

The semantic layer converts tested dbt assets into governed context for the NL→SQL pipeline, dashboards, and spreadsheets. It unifies metrics, dimensions, filters, and glossary terms, with enforcement hooks for the Data Policy Engine.

## 2. Architecture

```
dbt manifest/catalog
        │
        ▼
SemanticCompiler (app/modules/semantic_layer/compiler.py)
        │ writes *.semantic.yaml + ORM rows
        ▼
SemanticLayerService ──┐
        │ context      │ policy hints
        ▼              │
SQLService.generate_sql ── DataPolicyEngine ──> NL→SQL stages 1–3
        │
        ▼
VannaClient.train/documentation + Chroma vectors
```

## 3. Components

| Component | Responsibility | Key Classes/Files |
|-----------|----------------|-------------------|
| SemanticCompiler | Parse dbt docs, derive metrics/dimensions/hierarchies, persist YAML + train Vanna | `app/modules/semantic_layer/compiler.py` |
| SemanticLayerService | CRUD semantic models, produce prompt context, refresh child tables | `app/modules/semantic_layer/service.py` |
| ORM Tables | Persist compiled artifacts (`semantic_models`, `semantic_metrics`, `semantic_dimensions`, `semantic_filters`, `semantic_hierarchies`, `business_terms`) | `app/db/models.py` |
| API Layer | Expose `/api/v1/semantic/*` operations | `app/api/v1/routes/semantic.py`, schemas in `app/api/v1/schemas/semantic.py` |

## 4. APIs

| Endpoint | Method | Description | Request Schema | Response |
|----------|--------|-------------|----------------|----------|
| `/api/v1/semantic/models` | GET | List semantic models w/ metrics and dimensions | n/a | `SemanticModelResponse[]` |
| `/api/v1/semantic/models` | POST | Upsert model header metadata | `SemanticModelCreateRequest` | `SemanticModelResponse` |
| `/api/v1/semantic/compile` | POST | Trigger dbt compile + Vanna training | `SemanticCompileRequest` | `SemanticCompileResponse` | 
| `/api/v1/semantic/interpret` | POST | NL question → metric/filter/dimension intent | `InterpreterRequest` | `InterpreterResponse` |
| `/api/v1/entities` | CRUD | Business ontology / semantic entities | `EntityRequest`, `EntityPatchRequest` | `EntityResponse` |
| `/api/v1/dimensions` | CRUD | Dimension dictionary (model scoped) | `DimensionRequest`, `DimensionPatchRequest` | `DimensionResponse` |
| `/api/v1/hierarchies` | CRUD | Drill-down definitions | `HierarchyRequest`, `HierarchyUpdateRequest` | `HierarchyResponse` |
| `/api/v1/filters` | CRUD | Semantic filters / presets | `FilterRequest` | `FilterResponse` |
| `/api/v1/glossary` | GET/POST/DELETE | Business glossary management | `GlossaryEntryRequest` | `GlossaryEntryResponse` |
| `/api/v1/compiler/compile` | POST | Compile metric+filters+dimensions → SQL | `CompilerRequest` | `CompilerResponse` |

All read endpoints require authenticated users; mutations require analyst/admin roles and compiler access remains admin-only.

## 5. Data Models

| Table | Columns (key fields) | Notes |
|-------|----------------------|-------|
| `semantic_models` | `id`, `name`, `dbt_model`, `version`, `owner_id`, `extra_metadata` | One row per semantic model |
| `semantic_metrics` | `model_id`, `name`, `expression`, `agg`, `tags` | Derived metrics per model |
| `semantic_dimensions` | `model_id`, `name`, `data_type`, `expression`, `grain`, `hierarchy_path` | Dimension metadata |
| `semantic_filters` | `model_id`, `name`, `expression`, `default_value` | Named reusable filters |
| `semantic_hierarchies` | `model_id`, `name`, `levels[]` | Drill paths |
| `business_terms` | `term`, `definition`, `related_metrics`, `related_dimensions` | Business glossary |

## 6. Semantic YAML Contract

```yaml
semantic_model: customer_success
version: 1.2
source_model: dim_customers
metrics:
  - name: active_customers
    expression: "COUNT_IF(status = 'active')"
    agg: count
    tags: [csat]
dimensions:
  - name: customer_segment
    data_type: text
    grain: segment
filters:
  - name: account_region
    expression: "region = '{{region}}'"
    default_value: GLOBAL
hierarchies:
  - name: region_hierarchy
    levels: [region, country, city]
```

## 7. SLAs & Error Conditions

- Compile runtime < 5 minutes per invocation; abort if dbt manifest missing or stale.
- `SEMANTIC_REFRESH_SECONDS` ensures scheduled refresh must not run more frequently than every 15 minutes by default.
- Failures surface HTTP 500 with correlation IDs and pointer to latest dbt manifest to accelerate debugging.

## 8. Integration Points

- **dbt**: consumes `schema.yml`, `manifest.json`, `catalog.json`.
- **Vanna OSS**: `VannaClient.train(documentation=...)` ingests compiled docs; `VannaClient.generate_sql` receives enriched context from `SemanticLayerService.build_generation_context`.
- **Data Policy Engine**: receives `policy_clauses` and masked column information to embed in prompts.
- **Dashboards/Spreadsheets**: reuse semantic metadata when generating SQL or formulas.

## 9. Folder Structure

```
app/modules/semantic_layer/
├── __init__.py
├── compiler.py
├── models.py (dataclasses: SemanticModelDefinition, SemanticMetricDefinition, ...)
└── service.py
```

All semantic changes must be mirrored into documentation and migrations to keep the enterprise knowledge graph consistent.
