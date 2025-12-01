# Agent Operational Directives (agents.md)

**AI Agent Behavioral Constitution & Development Standards**

---

## Document Metadata

| Property | Value |
|----------|-------|
| **Document Version** | 2.0 (Enhanced) |
| **Project Context** | Vanna Insight Engine (Enterprise FastAPI Backend) |
| **Status** | Final, Authoritative |
| **Date** | November 12, 2025 |
| **Purpose** | Define operational principles, behavioral directives, and development standards for AI agents working on this project |
| **Audience** | AI agents, human developers, DevOps engineers |

---

## Table of Contents

1. [Overview & Purpose](#1-overview--purpose)
2. [Pre-Execution & Context Preparation](#2-pre-execution--context-preparation)
3. [Task Management & Workflow](#3-task-management--workflow)
4. [Code Design & Implementation](#4-code-design--implementation)
5. [Environment & Runtime Rules](#5-environment--runtime-rules)
6. [File & Documentation Management](#6-file--documentation-management)
7. [User Interaction & Autonomy](#7-user-interaction--autonomy)
8. [Security & Configuration Management](#8-security--configuration-management)
9. [Testing & Quality Assurance](#9-testing--quality-assurance)
10. [Version Control & Change Management](#10-version-control--change-management)
11. [Error Handling & Recovery](#11-error-handling--recovery)
12. [Performance & Optimization](#12-performance--optimization)
13. [Reporting & Transparency](#13-reporting--transparency)
14. [Operational Discipline](#14-operational-discipline)
15. [Project-Specific Directives (Vanna Insight Engine)](#15-project-specific-directives-vanna-insight-engine)

---

## 1. Overview & Purpose

### 1.1 Mission Statement

This document serves as the **operational constitution** for AI agents working on the Vanna Insight Engine project. It defines:

- How agents behave during development
- How agents communicate with users
- How agents execute tasks and record progress
- How agents ensure quality, security, and maintainability

### 1.2 Core Principles

1. **Clarity Before Action** - Never proceed with ambiguous requirements
2. **Transparency by Default** - Log everything, hide nothing
3. **Quality Over Speed** - Correctness trumps rapid completion
4. **User as Final Authority** - Confirm, don't assume
5. **Incremental Progress** - Small, validated steps over large leaps

### 1.3 Scope

Every task, process, or code execution initiated by the agent **MUST** adhere to the principles outlined in this document. Violations should be flagged immediately and corrected.

---

## 2. Pre-Execution & Context Preparation

### 2.1 Context Verification (MANDATORY)

**Before starting ANY task, the agent MUST:**

1. ✅ Read all relevant project files to understand:
   - Current architecture
   - Existing dependencies
   - Previous work and decisions
   - Known issues or constraints

2. ✅ Verify availability and completeness of:
   - Required data files
   - Configuration files (`.env`, `config.py`)
   - Database schemas
   - API credentials (warn if missing)

3. ✅ Load task history:
   - Check `tasks.log` for pending or blocked tasks
   - Review last session's progress
   - Identify dependencies between tasks

### 2.2 Ambiguity Resolution Protocol

**When information is missing or ambiguous:**

```
Step 1: Identify the ambiguity precisely
Step 2: Check if reasonable defaults exist (e.g., SQLite for database)
Step 3: If yes → Propose default and ask for confirmation
        If no → Ask user for clarification
Step 4: Document the choice in `tasks.log`
```

**Example:**
```
❌ BAD: "I'll assume you want PostgreSQL."
✅ GOOD: "Database not specified. Recommend PostgreSQL (production-grade) 
         or SQLite (development). Default: PostgreSQL. Confirm?"
```

### 2.3 Explicit Assumptions

**If proceeding with assumptions, the agent MUST:**

1. State all assumptions explicitly
2. Log assumptions in `tasks.log`
3. Mark assumptions with `[ASSUMPTION]` tag
4. Allow user to override before execution

**Format:**
```markdown
## Task: Setup Database Connection
**Assumptions:**
- [ASSUMPTION] Database: PostgreSQL 16
- [ASSUMPTION] Port: 5432 (non-standard to avoid conflicts)
- [ASSUMPTION] User: vanna_user (can be changed in .env)

**Action Required:**
Please confirm or override these assumptions before I proceed.
```

---

## 3. Task Management & Workflow

### 3.1 Task Decomposition

**All complex projects MUST be broken down into:**

1. **Milestones** - Major project phases (e.g., "Phase 0: Foundation")
2. **Tasks** - Individual work units (e.g., "Setup FastAPI app")
3. **Subtasks** - Granular steps (e.g., "Install FastAPI dependency")

**Each task must define:**
- **ID**: Unique identifier (e.g., `TASK-001`)
- **Description**: What needs to be done
- **Dependencies**: Tasks that must complete first
- **Status**: `pending`, `in_progress`, `blocked`, `completed`, `failed`
- **Owner**: Who is responsible (agent or user)
- **Estimated Time**: Rough estimate
- **Actual Time**: Time taken upon completion

### 3.2 Task Logging Format

**File:** `tasks.log` (created at project root)

**Format:**
```markdown
# Task Log - Vanna Insight Engine

---

## [TASK-001] Setup FastAPI Application
- **Status**: completed
- **Dependencies**: None
- **Started**: 2025-11-12 10:00 UTC
- **Completed**: 2025-11-12 10:45 UTC
- **Duration**: 45 minutes
- **Owner**: Agent
- **Changes**:
  - Created `app/main.py` with FastAPI app instance
  - Added `/health` endpoint
  - Configured CORS middleware
- **Testing**: ✅ Health check returns 200 OK
- **Notes**: Used FastAPI 0.109.2 as per v6.1 spec

---

## [TASK-002] Setup Database Layer
- **Status**: in_progress
- **Dependencies**: TASK-001
- **Started**: 2025-11-12 11:00 UTC
- **Owner**: Agent
- **Progress**: 60% (models defined, migrations pending)
- **Blockers**: None
- **Next Steps**:
  1. Run Alembic migrations
  2. Seed database with test data
  3. Test ORM queries

---

## [TASK-003] Implement JWT Authentication
- **Status**: pending
- **Dependencies**: TASK-002
- **Owner**: Agent
- **Estimated Time**: 2 hours
- **Notes**: Refer to v6.1 spec, Section 8.1
```

### 3.3 Autonomous Execution

**The agent SHOULD execute tasks autonomously when:**
- All dependencies are satisfied
- No user input is required
- Task complexity is low-to-medium

**The agent MUST ask for confirmation when:**
- Task involves destructive operations (delete, drop, truncate)
- Task involves external API calls with costs
- Task modifies critical configuration
- Task complexity is high or risky

### 3.4 Task Reminders

**At the start of each session, the agent MUST:**

1. Load `tasks.log`
2. Display pending/blocked tasks
3. Highlight any tasks requiring user input
4. Propose the next task to work on

**Example Output:**
```
📋 Task Status Summary:
- ✅ 5 tasks completed
- 🔄 1 task in progress (TASK-002: Setup Database Layer)
- ⏸️ 2 tasks pending (TASK-003, TASK-004)
- 🚫 0 tasks blocked

📌 Proposed Next Action:
Complete TASK-002 (Setup Database Layer), then proceed to TASK-003 (JWT Auth).

Would you like me to continue with TASK-002?
```

---

## 4. Code Design & Implementation

### 4.1 Design Principles

**All code generated by the agent MUST adhere to:**

1. **Minimal Dependencies**
   - Use standard library when possible
   - Avoid heavy frameworks unless justified
   - Document all external dependencies in `requirements.txt`

2. **Graceful Error Recovery**
   - Try-except blocks for all I/O operations
   - Fallback mechanisms for external services
   - Never crash on expected failures (e.g., network timeout)

3. **User Configurability**
   - All magic numbers should be constants or config values
   - Provide sensible defaults
   - Allow runtime override via environment variables or CLI args

4. **Code Readability**
   - Clear variable names (no single-letter variables except `i`, `j` in loops)
   - Docstrings for all functions and classes
   - Comments for non-obvious logic

### 4.2 Default Technology Choices (Vanna Project)

**When user does not specify, use these defaults:**

| Component | Default | Reason |
|-----------|---------|--------|
| **Backend Framework** | FastAPI 0.109.2 | As per v6.1 spec |
| **Database (Dev)** | SQLite 3.x | Zero-config, local |
| **Database (Prod)** | PostgreSQL 16 | Production-ready, as per spec |
| **Cache/Queue** | Redis 7.0 | As per v6.1 spec |
| **Task Queue** | Celery 5.3.4 | As per v6.1 spec |
| **LLM Provider** | Ollama (local) | No API costs, privacy |
| **Vector DB** | ChromaDB 0.4.22 | As per v6.1 spec |
| **Testing** | pytest 8.0.0 | Industry standard |
| **ORM** | SQLAlchemy 2.0.27 | As per v6.1 spec |

**Reference:** Always check `Vanna-Insight-Engine-Unified-Architecture-v6.1.md`, Section 11 (Technology Stack) for authoritative versions.

### 4.3 Database Initialization

**When creating a new database:**

1. Use migrations (Alembic) for schema changes
2. Include seed data script (`scripts/seed_db.py`)
3. Provide mock data for testing (at least 10 records per table)
4. Document schema in `docs/database_schema.md`

**SQLite Default Setup:**
```python
# app/db/database.py (SQLite)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./vanna.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite-specific
    echo=True  # Log SQL queries during development
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

### 4.4 LLM Integration Defaults

**When implementing LLM calls:**

1. **Default Provider**: Ollama (local)
2. **No automatic installation**: Do NOT run `pip install ollama` or similar
3. **Reference only**: Provide URL to Ollama documentation
4. **Mock fallback**: Implement mock LLM responses for testing

**Example:**
```python
# app/core/llm/adapter.py
class LLMAdapter:
    def __init__(self, provider: str = "ollama", base_url: str = "http://localhost:11434"):
        self.provider = provider
        self.base_url = base_url
    
    async def generate(self, prompt: str) -> str:
        """Generate text from LLM."""
        if self.provider == "ollama":
            # Make HTTP request to Ollama API
            # DO NOT import ollama library
            ...
        elif self.provider == "mock":
            # Return mock response for testing
            return f"Mock response for: {prompt[:50]}..."
```

### 4.5 Docker Compose Constraints

**When using Docker Compose:**

1. ❌ **NO external downloads during runtime** (no `pip install`, `apt-get install`)
2. ✅ **Pre-install all dependencies in Dockerfile**
3. ✅ **Use multi-stage builds** to reduce image size
4. ✅ **Pin all dependency versions** (no `latest` tags)

**Dockerfile Best Practices:**
```dockerfile
# ✅ CORRECT: Pre-install dependencies
FROM python:3.11-slim

WORKDIR /app

# Copy requirements first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ❌ WRONG: Do NOT install during CMD or runtime
```

---

## 5. Environment & Runtime Rules

### 5.1 Virtual Environment Management

**Rules:**
1. **One virtual environment per project** - No duplicates
2. **Name convention**: `.venv` (hidden, at project root)
3. **Python version**: 3.11+ (as per Vanna project)
4. **Activation reminder**: Agent must remind user to activate venv

**Setup Script:**
```bash
# scripts/setup_env.sh
#!/bin/bash
python3.11 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Virtual environment ready"
```

### 5.2 Network Accessibility

**The agent MUST ensure:**

1. **Local access**: Project runs on `localhost` by default
2. **Network access**: Can be accessed from remote devices (optional)
3. **Port configuration**: Non-standard ports to avoid conflicts

**Default Ports (Vanna Project):**
```
- FastAPI Backend: 8000
- PostgreSQL: 5432
- Redis: 6379
- ChromaDB: 8001
- Celery Flower: 5555
- Superset: 8088
```

**If port conflicts occur:**
- Agent should detect conflict
- Suggest alternative port
- Update docker-compose.yml automatically

### 5.3 Offline Development

**During development phase (Phase 0-1):**

1. ❌ **NO internet calls** for library downloads
2. ❌ **NO automatic pip installs**
3. ✅ **Assume all dependencies are pre-installed**
4. ✅ **Use local resources only**

**Exception:** External API calls for:
- LLM inference (if remote provider)
- Database connections (if cloud-hosted)

**These must be configurable** via environment variables to support offline mode.

### 5.4 Gradual Build Strategy

**Order of Development (STRICTLY ENFORCE):**

```
Phase 0: Core Backend
├─ 1. Database layer (models, migrations)
├─ 2. Core services (Vanna integration)
├─ 3. API endpoints (FastAPI routes)
├─ 4. Authentication & security
├─ 5. Testing (unit + integration)
└─ 6. Docker deployment

Phase 1: Frontend (ONLY AFTER Phase 0 COMPLETE)
├─ 1. React/Vue setup
├─ 2. API client
├─ 3. UI components
└─ 4. Integration testing

Phase 2: dbt Integration
...
```

**Agent MUST NOT:**
- Jump ahead to UI before backend is stable
- Implement advanced features before core is tested
- Deploy before all tests pass

---

## 6. File & Documentation Management

### 6.1 Documentation Structure

**Maintain centralized documentation in `/docs` folder:**

```
/docs
├── architecture/
│   ├── Vanna-Insight-Engine-Unified-Architecture-v6.1.md  (static)
│   └── design-decisions.md  (append-only)
├── api/
│   ├── openapi.yaml  (auto-generated)
│   └── endpoints.md  (manual reference)
├── operations/
│   ├── deployment.md
│   ├── monitoring.md
│   └── troubleshooting.md
├── development/
│   ├── setup.md
│   ├── testing.md
│   └── contribution-guide.md
├── dynamic/
│   ├── tasks.log  (updated every session)
│   ├── changelog.md  (updated on releases)
│   └── meeting-notes.md
└── agents.md  (this file - static, versioned)
```

### 6.2 Document Categories

| Category | Update Frequency | Examples |
|----------|------------------|----------|
| **Static** | Rarely (major changes only) | Architecture, design philosophy |
| **Semi-Static** | Monthly or per-phase | API docs, deployment guides |
| **Dynamic** | Daily/per-session | tasks.log, changelog |

### 6.3 Duplication Prevention

**Rules:**
1. **One source of truth** per topic (no duplicate READMEs)
2. **Link, don't copy** - Use references instead of copying content
3. **Archive, don't delete** - Move old versions to `/docs/archive/`

**When updating documents:**
- Check for related documents that need updates
- Update all cross-references
- Mark deprecated content clearly

**Example:**
```markdown
## ⚠️ DEPRECATED: Old Setup Instructions

This section is deprecated as of 2025-11-12.

**New Location:** See [setup.md](/docs/development/setup.md)
```

### 6.4 Change Logging

**Every file modification MUST be logged:**

**Format (in `tasks.log`):**
```markdown
### File Changes - 2025-11-12 14:30 UTC

**Modified:**
- `app/main.py`: Added CORS middleware
- `app/config.py`: Added OPENAI_API_KEY setting
- `requirements.txt`: Added python-jose==3.3.0

**Created:**
- `app/api/v1/routes/sql.py`: SQL generation endpoints
- `tests/test_sql_generation.py`: Unit tests for SQL service

**Deleted:**
- `app/old_legacy_code.py`: Removed obsolete code
```

### 6.5 Code Header Comments

**All generated code files MUST include:**

```python
"""
Module: app/services/sql_service.py
Purpose: SQL execution and validation service
Project: Vanna Insight Engine
Spec Reference: Vanna-Insight-Engine-Unified-Architecture-v6.1.md, Section 3.1

Refer to agents.md for operational and behavioral directives.

Created: 2025-11-12
Author: AI Agent (validated by human developer)
"""
```

---

## 7. User Interaction & Autonomy

### 7.1 Proactive Communication

**The agent MUST be proactive, not passive:**

✅ **Do:**
- Ask clarifying questions when requirements are vague
- Propose better alternatives when you detect inefficiencies
- Warn about potential issues before they occur
- Suggest modern, reliable libraries over outdated ones

❌ **Don't:**
- Assume user intent without confirmation
- Silently make critical decisions
- Proceed when blocked by missing information
- Use deprecated or unmaintained libraries without warning

### 7.2 Decision-Making Framework

**When making technical decisions:**

```
1. Check if v6.1 spec specifies the technology
   └─ If YES → Use spec version
   └─ If NO → Proceed to step 2

2. Is there an industry-standard choice?
   └─ If YES → Propose standard + reason
   └─ If NO → Propose top 2-3 options with pros/cons

3. Present to user with recommendation
   └─ Wait for confirmation
   └─ Log decision in tasks.log
```

**Example:**
```
🤔 Decision Required: Testing Framework

**Options:**
1. pytest (recommended) - Industry standard, rich plugin ecosystem
2. unittest - Built-in, no dependencies
3. nose2 - Legacy, not actively maintained

**Recommendation:** pytest 8.0.0
**Reason:** Spec v6.1 specifies pytest. Best async support.

**Action:** Shall I proceed with pytest?
```

### 7.3 Progress Reporting

**After completing each task, provide:**

1. **Summary**: What was accomplished
2. **Changes**: Files created/modified/deleted
3. **Testing**: Test results (pass/fail counts)
4. **Issues**: Any problems encountered
5. **Next Steps**: Proposed next task

**Format:**
```markdown
✅ Task Complete: TASK-002 (Setup Database Layer)

**Summary:**
- Created 8 SQLAlchemy models (User, Query, Feedback, etc.)
- Generated Alembic migrations (3 files)
- Seeded database with 50 mock records

**Changes:**
- Created: app/db/models.py (250 lines)
- Created: alembic/versions/001_initial_schema.py
- Modified: app/config.py (added DATABASE_URL)

**Testing:**
- ✅ All models can be instantiated
- ✅ Migrations run successfully
- ✅ Mock data inserted (50 records)
- ✅ Query tests pass (10/10)

**Issues:** None

**Next Steps:**
Proceed to TASK-003 (Implement JWT Authentication)?
```

### 7.4 Conflict & Risk Notification

**The agent MUST warn the user when:**

1. About to delete files or data
2. Conflicting configuration detected
3. Security vulnerability found
4. Performance bottleneck likely
5. Breaking API change proposed

**Warning Format:**
```
⚠️ WARNING: Destructive Operation Detected

**Action:** About to drop table `queries` and recreate it
**Impact:** All existing query history will be lost
**Affected Records:** ~1,247 rows

**Alternatives:**
1. Create migration to alter table (recommended)
2. Export data, drop, recreate, re-import
3. Proceed with drop (CANNOT BE UNDONE)

**Recommendation:** Option 1 (migration)

Please confirm or select alternative before I proceed.
```

---

## 8. Security & Configuration Management

### 8.1 Secure Defaults

**All security-sensitive values MUST:**

1. Have secure defaults (strong, random)
2. Be easily changeable by user
3. Never be committed to version control
4. Be documented in `.env.example`

**Example `.env.example`:**
```bash
# Vanna Insight Engine - Environment Configuration
# Copy to .env and update with your values

# Security (CHANGE THESE)
JWT_SECRET_KEY=change-me-to-random-256-bit-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/vanna_db

# Redis
REDIS_URL=redis://localhost:6379/0

# LLM Provider (Ollama default)
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# Optional: OpenAI (for cloud LLM)
# OPENAI_API_KEY=sk-...

# Ports (change if conflicts exist)
FASTAPI_PORT=8000
POSTGRES_PORT=5432
REDIS_PORT=6379
```

### 8.2 Credential Management

**Rules:**
1. ❌ **NEVER hardcode credentials** in source code
2. ✅ **Use environment variables** for all secrets
3. ✅ **Provide generation script** for random secrets

**Secret Generation Script:**
```python
# scripts/generate_secrets.py
import secrets

def generate_jwt_secret() -> str:
    """Generate 256-bit JWT secret key."""
    return secrets.token_urlsafe(32)

def generate_api_key() -> str:
    """Generate random API key."""
    return f"vanna_{secrets.token_hex(16)}"

if __name__ == "__main__":
    print("Generated Secrets:")
    print(f"JWT_SECRET_KEY={generate_jwt_secret()}")
    print(f"API_KEY={generate_api_key()}")
```

### 8.3 Port Management

**Default Ports:**
- See Section 5.2 for Vanna project defaults

**Conflict Resolution:**
1. Agent detects port conflict (e.g., port 8000 in use)
2. Suggests alternative (e.g., 8001)
3. Updates `docker-compose.yml` or `config.py`
4. Logs change in `tasks.log`

**Port Configuration File:**
```yaml
# config/ports.yaml
services:
  fastapi:
    default: 8000
    alternative: 8001
  postgres:
    default: 5432
    alternative: 5433
  redis:
    default: 6379
    alternative: 6380
```

### 8.4 Remote AI Model Security

**When connecting to remote LLM APIs:**

1. Use HTTPS only (never HTTP)
2. Validate SSL certificates
3. Implement API key rotation mechanism
4. Log all API calls (without exposing keys)
5. Implement rate limiting to prevent cost overruns

**Example:**
```python
# app/core/llm/remote_provider.py
import httpx
from app.config import settings

class RemoteLLMProvider:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.base_url = "https://api.openai.com/v1"  # HTTPS only
        self.client = httpx.AsyncClient(
            timeout=30.0,
            verify=True,  # Validate SSL
        )
    
    async def generate(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        # Log call (mask API key)
        logger.info("LLM API call", extra={
            "provider": "openai",
            "api_key": f"{self.api_key[:8]}***",  # Masked
            "prompt_length": len(prompt),
        })
        
        # Make request
        response = await self.client.post(
            f"{self.base_url}/completions",
            headers=headers,
            json={"prompt": prompt, "model": "gpt-3.5-turbo"}
        )
        
        return response.json()["choices"][0]["text"]
```

---

## 9. Testing & Quality Assurance

### 9.1 Testing Strategy

**The agent MUST test every component before moving forward.**

**Testing Pyramid:**
```
        /\
       /  \  E2E (5-10%)
      /____\
     /      \  Integration (20-30%)
    /________\
   /          \  Unit (60-70%)
  /__________\
```

**Test Coverage Requirements:**
- **Minimum**: 80% overall
- **Critical paths**: 95%+ (auth, SQL generation, data access)
- **Utilities**: 60%+ (logging, helpers)

### 9.2 Test Execution Order

**For each module:**

```
1. Unit Tests First
   └─ Test individual functions in isolation
   └─ Mock all external dependencies
   └─ Run: pytest tests/unit/

2. Integration Tests Second
   └─ Test interactions between components
   └─ Use test database (SQLite in-memory)
   └─ Run: pytest tests/integration/

3. End-to-End Tests Last
   └─ Test complete user workflows
   └─ Use Docker Compose test environment
   └─ Run: pytest tests/e2e/
```

### 9.3 Test Automation

**The agent MUST:**

1. Generate tests automatically for all new code
2. Run tests before marking task as complete
3. Log test results in `tasks.log`
4. Fix failing tests immediately

**Test Naming Convention:**
```python
# ✅ CORRECT: Descriptive test names
def test_sql_generation_returns_valid_select_query():
    ...

def test_jwt_authentication_rejects_expired_token():
    ...

# ❌ WRONG: Vague test names
def test_sql():
    ...

def test_auth():
    ...
```

### 9.4 Test Data Management

**Rules:**
1. Use fixtures for reusable test data
2. Use Faker library for random data generation
3. Clean up test data after each test (use pytest fixtures)

**Example:**
```python
# tests/conftest.py
import pytest
from faker import Faker
from app.db.database import SessionLocal, engine
from app.db.models import Base, User

fake = Faker()

@pytest.fixture(scope="function")
def db_session():
    """Create test database session."""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def sample_user(db_session):
    """Create sample user for testing."""
    user = User(
        email=fake.email(),
        hashed_password="hashed_password_123",
        role="analyst"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user
```

### 9.5 Validation Before Progression

**Before moving to next phase, validate:**

| Checkpoint | Criteria |
|------------|----------|
| **Functionality** | All features work as specified |
| **Tests** | 80%+ coverage, all tests pass |
| **Documentation** | All new code documented |
| **Security** | No critical vulnerabilities |
| **Performance** | Response times within acceptable range |
| **Deployment** | Docker Compose builds successfully |

---

## 10. Version Control & Change Management

### 10.1 Git Workflow

**The agent MUST follow this Git workflow:**

```
1. Before starting task:
   └─ git checkout -b feature/TASK-XXX-short-description

2. During development:
   └─ Commit after each logical unit of work
   └─ Use semantic commit messages (see 10.2)

3. After task completion:
   └─ git push origin feature/TASK-XXX
   └─ Create pull request (if applicable)
   └─ Update tasks.log with commit hash
```

### 10.2 Semantic Commit Messages

**Format:** `<type>(<scope>): <subject>`

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, no logic change)
- `refactor`: Code restructuring (no behavior change)
- `test`: Adding or updating tests
- `chore`: Maintenance (dependencies, configs)

**Examples:**
```bash
✅ CORRECT:
feat(auth): add JWT refresh token endpoint
fix(sql): escape special characters in generated queries
docs(api): update OpenAPI spec with new endpoints
test(db): add integration tests for User model

❌ WRONG:
update files
fix bug
added stuff
```

### 10.3 Commit Frequency

**Commit after:**
- Implementing a complete function/class
- Fixing a bug
- Completing a test suite
- Updating documentation

**DO NOT commit:**
- Broken code (unless marked as WIP)
- Sensitive data (.env, credentials)
- Large binary files (use Git LFS)

### 10.4 Branch Strategy

**For Vanna project:**

```
main (production-ready)
└─ develop (integration branch)
   ├─ feature/TASK-001-setup-fastapi
   ├─ feature/TASK-002-database-layer
   ├─ fix/ISSUE-123-jwt-expiration
   └─ docs/update-api-spec
```

**Rules:**
- `main`: Only merge when phase complete and tested
- `develop`: Daily integration of completed features
- `feature/*`: Individual task branches
- `fix/*`: Bug fix branches
- `docs/*`: Documentation-only changes

---

## 11. Error Handling & Recovery

### 11.1 Error Detection

**The agent MUST detect and log:**

1. **Syntax Errors** - During code generation
2. **Runtime Errors** - During execution
3. **Test Failures** - During test runs
4. **Deployment Errors** - During Docker builds
5. **Configuration Errors** - Missing env vars, invalid configs

### 11.2 Automatic Recovery Strategies

**When an error occurs:**

```
Step 1: Log error details (type, message, stack trace)
Step 2: Attempt automatic fix (if known solution exists)
Step 3: If fixed → Continue execution
        If not fixed → Notify user and suggest manual fix
Step 4: Update tasks.log with error and resolution
```

**Common Errors & Auto-Fixes:**

| Error | Auto-Fix |
|-------|----------|
| Missing dependency | Add to requirements.txt, re-install |
| Port conflict | Suggest alternative port |
| Database connection failed | Check if Docker container is running |
| Migration conflict | Generate new migration file |

### 11.3 Error Logging Format

```python
# app/monitoring/logging.py
import logging
import json

logger = logging.getLogger(__name__)

def log_error(error: Exception, context: dict = None):
    """Log error with context."""
    error_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "error_type": type(error).__name__,
        "error_message": str(error),
        "stack_trace": traceback.format_exc(),
        "context": context or {},
    }
    logger.error(json.dumps(error_data))
```

### 11.4 Rollback Procedures

**If a task fails catastrophically:**

1. **Git Rollback:**
   ```bash
   git reset --hard HEAD~1  # Undo last commit
   ```

2. **Database Rollback:**
   ```bash
   alembic downgrade -1  # Undo last migration
   ```

3. **Docker Rollback:**
   ```bash
   docker-compose down
   docker-compose up -d  # Restart with previous image
   ```

4. **Document Rollback:**
   ```markdown
   ## Rollback - 2025-11-12 15:45 UTC
   **Reason:** TASK-007 failed (database migration error)
   **Actions Taken:**
   - Reverted git commit abc1234
   - Downgraded database migration
   - Restarted Docker containers
   **Status:** System restored to pre-TASK-007 state
   ```

---

## 12. Performance & Optimization

### 12.1 Performance Baselines

**The agent MUST ensure:**

| Metric | Target | Measurement |
|--------|--------|-------------|
| **API Response Time (P95)** | < 500ms | Load testing |
| **Database Query Time (P95)** | < 100ms | SQL profiling |
| **Test Suite Execution** | < 2 minutes | pytest duration |
| **Docker Build Time** | < 5 minutes | CI/CD logs |
| **Memory Usage (Backend)** | < 512MB | Docker stats |

### 12.2 Optimization Strategy

**When performance issues detected:**

```
1. Profile the bottleneck
   └─ Use cProfile for Python code
   └─ Use EXPLAIN ANALYZE for SQL queries

2. Identify root cause
   └─ Slow database queries? → Add indexes
   └─ Excessive API calls? → Add caching
   └─ Large data transfers? → Add pagination

3. Implement fix
   └─ Test performance improvement
   └─ Document change in tasks.log

4. Monitor continuously
   └─ Add Prometheus metrics
   └─ Set up alerts for regressions
```

### 12.3 Caching Strategy

**Implement caching for:**

1. **Frequently accessed data** (user profiles, config)
2. **Expensive computations** (SQL generation, embeddings)
3. **External API responses** (LLM results)

**Cache Tiers:**
```
1. In-Memory (Python dict) → 1ms access time
2. Redis → 10ms access time
3. PostgreSQL → 50-100ms access time
```

**Example:**
```python
# app/core/cache/service.py
from redis import Redis
import json

class CacheService:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
    
    async def get(self, key: str) -> dict | None:
        """Get cached value."""
        value = await self.redis.get(key)
        return json.loads(value) if value else None
    
    async def set(self, key: str, value: dict, ttl: int = 3600):
        """Set cached value with TTL (default 1 hour)."""
        await self.redis.setex(key, ttl, json.dumps(value))
```

---

## 13. Reporting & Transparency

### 13.1 Operational Traceability

**The agent MUST log:**

1. **All file changes** (create, modify, delete)
2. **All executed commands** (git, docker, pytest)
3. **All API calls** (internal and external)
4. **All errors and warnings**
5. **All performance metrics**

**Log Format (JSON):**
```json
{
  "timestamp": "2025-11-12T15:30:45Z",
  "event_type": "file_modified",
  "file_path": "app/main.py",
  "changes": {
    "lines_added": 15,
    "lines_removed": 3
  },
  "task_id": "TASK-003",
  "agent_version": "2.0"
}
```

### 13.2 Progress Summaries

**Generate summary after:**
- Each completed task
- Each completed phase
- End of each work session

**Format:**
```markdown
# Progress Summary - 2025-11-12

## Work Session: 10:00 - 16:00 UTC (6 hours)

### Completed Tasks (3)
- ✅ TASK-001: Setup FastAPI Application
- ✅ TASK-002: Setup Database Layer
- ✅ TASK-003: Implement JWT Authentication

### In Progress (1)
- 🔄 TASK-004: Implement SQL Generation Pipeline (60%)

### Blocked (0)
- None

### Metrics
- Lines of code written: 1,247
- Tests added: 23 (21 passed, 2 skipped)
- Test coverage: 85%
- Commits: 7

### Issues Encountered
- Minor: Port 8000 conflict (resolved by using 8001)
- None critical

### Next Session Plan
1. Complete TASK-004 (SQL Generation Pipeline)
2. Start TASK-005 (Query Validation & Security)
3. Write integration tests for SQL service

### Estimated Progress
- Phase 0 completion: 75%
- Expected Phase 0 done: 2025-11-14
```

### 13.3 Accuracy & Credibility

**To ensure report accuracy:**

1. **Verify all numbers** (test counts, coverage, lines of code)
2. **Cross-reference with logs** (tasks.log, git log)
3. **Include evidence** (links to commits, test outputs)
4. **Mark estimates clearly** (use "estimated", "approximately")

---

## 14. Operational Discipline

### 14.1 Stage Completion Criteria

**The agent MUST NOT proceed to next stage unless:**

✅ All tasks in current stage marked as `completed`  
✅ All tests pass (80%+ coverage)  
✅ Documentation updated  
✅ Code reviewed (if human review required)  
✅ Changes committed to Git  
✅ User confirmation received (for major stages)

### 14.2 Context Consistency

**At all times, ensure:**

1. **Task context is clear** - Know what you're working on
2. **Dependencies are satisfied** - Required tasks completed
3. **Project structure is intact** - No broken imports or missing files
4. **Configuration is valid** - All env vars set

### 14.3 Session Startup Protocol

**On startup, the agent MUST:**

```
1. Display welcome message with agent version
2. Load tasks.log
3. Display pending/blocked tasks
4. Check for Git uncommitted changes (warn if any)
5. Validate environment (dependencies, database, services)
6. Propose next task or ask user for instructions
```

**Example Output:**
```
🤖 Vanna Insight Engine - AI Agent v2.0

📂 Loading project context...
- Project: Vanna Insight Engine (FastAPI Backend)
- Phase: Phase 0 (Foundation)
- Last update: 2025-11-12 14:30 UTC

📋 Task Status:
- ✅ 3 completed
- 🔄 1 in progress (TASK-004: SQL Generation Pipeline)
- ⏸️ 2 pending
- 🚫 0 blocked

⚠️ Uncommitted changes detected:
- app/services/sql_service.py (modified)
- tests/test_sql_generation.py (new file)

🔧 Environment check:
- ✅ Python 3.11.5
- ✅ Virtual environment active (.venv)
- ✅ PostgreSQL running (port 5432)
- ✅ Redis running (port 6379)
- ⚠️ ChromaDB not running (start with: docker-compose up -d chroma)

🎯 Proposed Action:
Complete TASK-004 (SQL Generation Pipeline - 60% done)

How would you like to proceed?
```

### 14.4 File Header Requirement

**All generated files MUST include:**

```python
# ==============================================================================
# Vanna Insight Engine - {Module Name}
# ==============================================================================
# Refer to agents.md for operational and behavioral directives.
# ==============================================================================
```

---

## 15. Project-Specific Directives (Vanna Insight Engine)

### 15.1 Architecture Compliance

**All work MUST comply with:**

**Primary Reference:**  
`Vanna-Insight-Engine-Unified-Architecture-v6.1.md`

**Key Sections:**
- Section 3: Core Component (FastAPI Backend)
- Section 4: Native dbt Integration
- Section 8: Security & Governance Framework
- Section 11: Technology Stack
- Section 13: Deployment Architecture

**If spec conflicts with agents.md:**
- **Spec takes precedence** for technical decisions
- **agents.md takes precedence** for process/workflow

### 15.2 Technology Constraints

**MUST USE (as per v6.1 spec):**

| Component | Technology | Version |
|-----------|-----------|---------|
| Backend | FastAPI | 0.109.2 |
| Database | PostgreSQL | 16 |
| Cache | Redis | 7.0 |
| Vector DB | ChromaDB | 0.4.22 |
| Task Queue | Celery | 5.3.4 |
| ORM | SQLAlchemy | 2.0.27 |
| Testing | pytest | 8.0.0 |

**DO NOT substitute** without user approval.

### 15.3 7-Stage NL-to-SQL Pipeline

**When implementing SQL generation:**

**MUST follow these stages (from v6.1 spec, Section 3.1.C):**

1. **Interpret** - Parse NL question into structured intent
2. **Generate** - Create SQL from intent (Vanna + context)
3. **Validate** - Security checks, syntax validation
4. **Optimize** - Performance tuning (indexes, query plans)
5. **Sanitize** - PII masking
6. **Execute** - Run SQL, log results
7. **Explain** - Natural language result description

**Each stage must be:**
- Implemented as separate function
- Logged independently
- Unit tested
- Monitored with metrics

### 15.4 Security Requirements

**Implement these security features (from v6.1 spec, Section 8):**

1. **JWT Authentication**
   - 256-bit secret key
   - Refresh token support
   - Expiration: 60 minutes (configurable)

2. **RBAC (Role-Based Access Control)**
   - Roles: `admin`, `analyst`, `viewer`
   - Enforce at endpoint level

3. **Query Firewall**
   - Block: DROP, DELETE, INSERT, UPDATE, ALTER, TRUNCATE
   - Allow: SELECT only

4. **PII Masking**
   - Detect: email, phone, SSN, credit card, IP address
   - Mask in logs and responses

5. **Audit Logging**
   - Log all queries, feedback, admin actions
   - JSON format with correlation IDs

### 15.5 Phase Execution Order

**STRICTLY FOLLOW (from v6.1 spec, Section 10):**

**Phase 0 (Weeks 1-4): Foundation**
- FastAPI app + 7-stage pipeline
- JWT auth + RBAC
- PostgreSQL + Redis + ChromaDB
- Docker Compose
- Tests (80%+ coverage)

**Phase 1 (Weeks 5-8): Frontend Integration**
- React/Vue app
- API integration
- Admin dashboard

**Phase 2 (Weeks 9-14): dbt Integration**
- dbt project (5-10 models)
- Automated training (Celery task)
- Admin API for dbt runs

**Phase 3 (Weeks 15-20): Superset Integration**
- Superset deployment
- Dashboards
- Row-level security

**Phase 4 (Months 7+): ClickHouse (Optional)**
- When triggered by scale requirements

**Agent MUST NOT skip phases or work on Phase N+1 before Phase N is complete.**

---

## Appendix A: Checklist Templates

### Task Completion Checklist

```markdown
## Task Completion Checklist - TASK-XXX

### Code
- [ ] Functionality implemented as specified
- [ ] Code follows project conventions (PEP 8, type hints)
- [ ] Docstrings added for all functions/classes
- [ ] Error handling implemented
- [ ] Logging added for key operations

### Testing
- [ ] Unit tests written (coverage >= 80%)
- [ ] Integration tests written (if applicable)
- [ ] All tests pass
- [ ] Edge cases tested

### Documentation
- [ ] Code comments added for complex logic
- [ ] API docs updated (if endpoint added/changed)
- [ ] tasks.log updated with progress

### Version Control
- [ ] Changes committed with semantic message
- [ ] Branch pushed to remote
- [ ] No sensitive data in commits

### Validation
- [ ] Manually tested in dev environment
- [ ] No regressions introduced
- [ ] Performance acceptable (< 500ms response)

### User Confirmation
- [ ] User reviewed changes (if required)
- [ ] User approved task completion
```

### Phase Completion Checklist

```markdown
## Phase Completion Checklist - Phase 0

### Deliverables
- [ ] All phase tasks completed (refer to v6.1 spec, Section 10)
- [ ] All features working as specified
- [ ] Docker Compose builds successfully

### Testing
- [ ] Unit tests: 80%+ coverage
- [ ] Integration tests: All pass
- [ ] E2E tests: Critical paths verified

### Documentation
- [ ] README.md updated
- [ ] API docs complete (OpenAPI spec)
- [ ] Deployment guide complete

### Quality
- [ ] No critical bugs
- [ ] No security vulnerabilities
- [ ] Performance targets met

### Deployment
- [ ] Docker images built
- [ ] Environment variables documented
- [ ] Deployment tested locally

### Review
- [ ] Code reviewed (if applicable)
- [ ] User approval received
- [ ] Ready for next phase
```

---

## Appendix B: Quick Reference Commands

### Development

```bash
# Setup
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run FastAPI
uvicorn app.main:app --reload --port 8000

# Run tests
pytest tests/ -v --cov=app --cov-report=html

# Database migrations
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic downgrade -1

# Docker
docker-compose up -d
docker-compose logs -f fastapi
docker-compose down
```

### Git

```bash
# Start task
git checkout -b feature/TASK-XXX-description

# Commit
git add .
git commit -m "feat(scope): description"

# Push
git push origin feature/TASK-XXX
```

### Monitoring

```bash
# Logs
tail -f logs/app.log

# Database
psql -U user -d vanna_db -c "SELECT COUNT(*) FROM queries;"

# Redis
redis-cli PING
redis-cli KEYS "cache:*"
```

---

## Document Status

**Version:** 2.0 (Enhanced)  
**Date:** November 12, 2025  
**Status:** Final, Authoritative  
**Next Review:** Post-Phase 1 completion

**Changes from v1.0:**
- ✅ Added Version Control & Change Management section
- ✅ Added Error Handling & Recovery section
- ✅ Added Performance & Optimization section
- ✅ Added Project-Specific Directives (Vanna Insight Engine)
- ✅ Expanded Testing & QA section with coverage targets
- ✅ Added checklist templates (Appendix A)
- ✅ Added quick reference commands (Appendix B)
- ✅ Integrated with Vanna v6.1 spec references

---

**END OF AGENTS.MD**

---

**Note to AI Agents:**  
This document is your operational constitution. Follow it rigorously. When in doubt, ask the user. When certain, proceed confidently. Always log your actions. Always test your work. Always communicate transparently.

**Your mission is to build reliable, maintainable, and high-quality software. This document is your roadmap to achieving that mission.**

---

### 15.6 Enterprise Additions Checklist (MANDATORY)

1. **Semantic Layer Hygiene**
   - Ensure `app/modules/semantic_layer` compiles successfully (either via `/api/v1/semantic/compile` or scheduled task) after *any* dbt change.
   - Never bypass `SemanticLayerService.build_generation_context()` when touching `SQLService`; prompt context must include semantic + policy + metric data.
2. **Policy Engine**
   - Every new NL→SQL endpoint must call `DataPolicyEngine.evaluate()` before execution. Validate RLS/CLS toggles (`ENABLE_ROW_LEVEL_SECURITY`, `ENABLE_COLUMN_LEVEL_SECURITY`) as part of code reviews.
3. **Router Registration**
   - When adding enterprise routes, mount them in `app/main.py` with the correct dependency (`Auth_Dependency` vs `Admin_Auth_Dependency`) and document them in `INDEX.md` + `VANNA_OSS_INTEGRATION.md`.
4. **Migrations & Schemas**
   - Extend Alembic migration `003_enterprise_extensions.py` or create `00X_*` follow-ups for any schema delta touching `projects`, `semantic_*`, `data_policies`, `dashboards`, `spreadsheets`, or `usage_events`.
5. **Usage Telemetry**
   - All long-running operations (dashboard publish, spreadsheet formula generation, semantic compile) must emit `UsageMonitoringService.record_event()` entries and include correlation IDs.
6. **Documentation Sync**
   - Update the new specification files (`SEMANTIC_LAYER_DESIGN.md`, `DATA_CONTROL_POLICIES.md`, etc.) whenever behavior or APIs change. Failing to do so blocks promotion to production.
7. **API Coverage Verification**
   - Ensure the canonical endpoints (`/api/v1/entities`, `/dimensions`, `/metrics`, `/projects`, `/dashboards`, `/spreadsheets`, `/users`, `/policies`, `/security/*`, `/usage/*`) are exercised in QA plans before release; missing coverage is grounds for rejection.

These directives guarantee the newly introduced enterprise capabilities remain aligned with the legacy governance loop and the 7-Stage NL→SQL pipeline.
