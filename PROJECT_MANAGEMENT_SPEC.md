# PROJECT_MANAGEMENT_SPEC.md

## Document Metadata

| Property | Value |
|----------|-------|
| Version | 1.0 |
| Scope | Projects, Templates, Memberships, User Management |
| Owners | Delivery Engineering |
| Updated | Nov 27, 2025 |

## 1. Purpose

Provide governed workspaces that group dashboards, spreadsheets, and NL→SQL queries while extending RBAC with project roles and user groups.

## 2. Architecture

```
Users ──┐
        │ assign group/role via /api/v1/users/*
        ▼
ProjectService (/api/v1/projects)
        │ creates rows in projects + project_memberships
        ▼
Dashboards/Spreadsheets reference project_id + membership
```

User groups add another layer for policy scoping.

## 3. Data Model Summary

| Table | Fields | Description |
|-------|--------|-------------|
| `projects` | `id`, `name`, `description`, `owner_id`, `status`, `attributes`, timestamps | Core project entity |
| `project_memberships` | `project_id`, `user_id`, `role`, `created_at` | Role assignment per project; unique per user/project |
| `project_templates` | `id`, `name`, `description`, `payload` | JSON boilerplates applied at project creation |
| `user_groups` | `id`, `name`, `description` | Named groups |
| `user_group_memberships` | `group_id`, `user_id`, `role` | Group-level RBAC |

## 4. APIs

- `GET /api/v1/projects`: list projects accessible to current user; admin returns all.
- `POST /api/v1/projects`: create project (analyst/admin). Body includes optional `template_id` and metadata. Response returns `ProjectResponse`.
- `GET /api/v1/projects/{id}`: retrieve single project plus attributes/metadata.
- `PATCH /api/v1/projects/{id}`: update name/description/status/attributes.
- `DELETE /api/v1/projects/{id}`: remove project (admin only).
- `POST /api/v1/projects/{id}/members`: admin adds/updates membership. Raises 404 if project missing.
- `GET /api/v1/projects/templates`: list available templates for UI pickers.
- `GET /api/v1/users/roster`: admin roster view (extends auth module).
- `POST /api/v1/users/{id}/roles`: admin promotion/demotion.
- `POST /api/v1/users/{id}/groups`: admin assign group; group auto-created on demand.

## 5. Class Responsibilities

| Class | Responsibility |
|-------|----------------|
| `ProjectService` | CRUD, membership management, template hydration |
| `UserManagementService` | Roster, role updates, group assignments |
| `ProjectMemberRequest` (schema) | Validates role ∈ {viewer, analyst, admin, owner} |

## 6. SLAs & Error Modes

- `ProjectService.create_project` must complete <1s; membership + template seeding are synchronous.
- Each membership change invalidates cached project contexts for frontends.
- HTTP 403 returned when non-admin attempts membership changes; HTTP 404 when referencing unknown project or user.

## 7. Integration

- `SQLService` stores optional `project_id` on `Query` rows to allow project-level lineage.
- `DataPolicyEngine` can scope policies by project (payload includes `project_id`).
- Dashboards/spreadsheets filter by project membership to provide correct asset lists.

## 8. Folder Layout

```
app/modules/projects/service.py
app/modules/user_management/service.py
app/api/v1/routes/projects.py
app/api/v1/routes/user_management.py
app/api/v1/schemas/projects.py
app/api/v1/schemas/user_management.py
```

Projects are the organizing construct for every enterprise feature; do not introduce new top-level buckets without extending this specification.
