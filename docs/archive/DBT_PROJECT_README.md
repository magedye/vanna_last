# Vanna Insight Engine – dbt Project

This directory houses the dbt assets that act as the single source of truth for the application's database schema.

## Contents

- `dbt_project.yml` – Project metadata
- `profiles.yml` – SSOT-compliant profile definitions (reads from environment variables)
- `models/schema.yml` – Canonical documentation for every table and column used by the FastAPI backend

## Usage

```bash
# List resources
dbt ls

# Run model tests
dbt test

# Generate documentation
dbt docs generate && dbt docs serve
```

Make sure the required environment variables (`POSTGRES_*`, `DBT_PROJECT_PATH`, `DBT_PROFILE_NAME`) are set before running dbt commands locally or inside Docker containers.
