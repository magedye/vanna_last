# Vanna Insight Engine - Complete Schema Specification

**Comprehensive Pydantic Schemas for FastAPI Backend**

---

## Document Overview

**Project:** Vanna Insight Engine  
**Component:** Backend API Schemas  
**Version:** 1.0.0  
**Date:** November 12, 2025  
**Status:** Production-Ready

This document provides complete Pydantic schema definitions for all 22 API endpoints in the Vanna Insight Engine FastAPI backend, with security best practices, validation rules, and comprehensive documentation.

---

## Table of Contents

1. [Schema Design Principles](#schema-design-principles)
2. [Authentication Schemas](#authentication-schemas)
3. [SQL Operation Schemas](#sql-operation-schemas)
4. [Query Management Schemas](#query-management-schemas)
5. [Feedback System Schemas](#feedback-system-schemas)
6. [Admin Operation Schemas](#admin-operation-schemas)
7. [System Monitoring Schemas](#system-monitoring-schemas)
8. [Common Response Schemas](#common-response-schemas)
9. [Security Guidelines](#security-guidelines)
10. [JSON Request/Response Examples](#json-examples)

---

## 1. Schema Design Principles

### Core Principles

**✅ Security First**
- Always use `extra = "forbid"` to reject unknown fields
- Sanitize all user input fields (SQL, text, comments)
- Use UUIDs or validated patterns for all identifiers
- Never expose sensitive data in responses

**✅ Strong Typing**
- Use `StrictStr`, `StrictInt`, `StrictBool` for type safety
- Apply `constr()` with length and pattern constraints
- Use `Literal` for enum-like fields
- Define clear field descriptions for OpenAPI docs

**✅ Validation**
- Enforce min/max length constraints on all strings
- Use regex patterns for IDs and structured data
- Validate ranges for numeric fields
- Apply `strip_whitespace=True` for text inputs

**✅ Consistency**
- Use `snake_case` for all field names
- Use `PascalCase` for schema class names
- Consistent suffixes: `Request`, `Response`, `Item`, `ListResponse`
- Include `correlation_id` in all responses for traceability

---

## 2. Authentication Schemas

### POST /api/v1/auth/login

**Purpose:** User authentication and JWT token generation

```python
from pydantic import BaseModel, Field, constr, EmailStr
from typing import Literal

class LoginRequest(BaseModel):
    """User login credentials"""
    
    email: EmailStr = Field(
        ...,
        description="User email address (must be valid email format)"
    )
    password: constr(min_length=8, max_length=128) = Field(
        ...,
        description="User password (8-128 characters)"
    )
    
    class Config:
        extra = "forbid"


class LoginResponse(BaseModel):
    """Successful login response with JWT token"""
    
    access_token: constr(min_length=1, max_length=2048) = Field(
        ...,
        description="JWT access token for authentication"
    )
    token_type: Literal["bearer"] = Field(
        "bearer",
        description="Token type (always 'bearer')"
    )
    user: "UserResponse" = Field(
        ...,
        description="User information"
    )
    
    class Config:
        extra = "forbid"
```

**Security Notes:**
- Password never returned in response
- Use HTTPS for all authentication endpoints
- Implement rate limiting (5 attempts per minute)
- Log failed authentication attempts

---

### POST /api/v1/auth/refresh

**Purpose:** Refresh expired access token

```python
class TokenRefreshRequest(BaseModel):
    """Request to refresh access token"""
    
    refresh_token: constr(min_length=1, max_length=2048) = Field(
        ...,
        description="Valid refresh token"
    )
    
    class Config:
        extra = "forbid"


class TokenRefreshResponse(BaseModel):
    """New access token response"""
    
    access_token: constr(min_length=1, max_length=2048) = Field(
        ...,
        description="New JWT access token"
    )
    token_type: Literal["bearer"] = Field(
        "bearer",
        description="Token type"
    )
    
    class Config:
        extra = "forbid"
```

---

### POST /api/v1/auth/logout

**Purpose:** Invalidate user session and token

```python
class LogoutResponse(BaseModel):
    """Logout confirmation"""
    
    message: constr(strip_whitespace=True, min_length=1, max_length=200) = Field(
        ...,
        description="Logout confirmation message"
    )
    status: Literal["success"] = Field(
        "success",
        description="Operation status"
    )
    
    class Config:
        extra = "forbid"
```

---

### GET /api/v1/auth/me

**Purpose:** Get current authenticated user information

```python
from datetime import datetime
from typing import Literal

class UserResponse(BaseModel):
    """Current user information"""
    
    id: constr(regex=r'^[A-Za-z0-9\-]{1,100}$') = Field(
        ...,
        description="User unique identifier (UUID format)"
    )
    email: EmailStr = Field(
        ...,
        description="User email address"
    )
    name: constr(strip_whitespace=True, min_length=1, max_length=200) = Field(
        ...,
        description="User full name"
    )
    role: Literal["admin", "analyst", "viewer"] = Field(
        ...,
        description="User role (admin, analyst, or viewer)"
    )
    created_at: datetime = Field(
        ...,
        description="Account creation timestamp (UTC)"
    )
    last_login: datetime = Field(
        ...,
        description="Last login timestamp (UTC)"
    )
    
    class Config:
        extra = "forbid"
```

---

## 3. SQL Operation Schemas

### POST /api/v1/sql/generate

**Purpose:** Generate SQL from natural language question

```python
from typing import Optional
from pydantic import StrictBool, StrictFloat

class SQLGenerationRequest(BaseModel):
    """Request to generate SQL from natural language"""
    
    question: constr(strip_whitespace=True, min_length=5, max_length=1000) = Field(
        ...,
        description="Natural language question (5-1000 characters)",
        example="What were the total sales in Q4 2024?"
    )
    schema_context: Optional[constr(strip_whitespace=True, max_length=200)] = Field(
        None,
        description="Optional database schema context or hint"
    )
    include_explanation: StrictBool = Field(
        True,
        description="Whether to include SQL explanation"
    )
    
    class Config:
        extra = "forbid"


class SQLGenerationResponse(BaseModel):
    """Generated SQL query response"""
    
    query_id: constr(regex=r'^[A-Za-z0-9\-]{1,100}$') = Field(
        ...,
        description="Unique query identifier for tracking"
    )
    sql: constr(strip_whitespace=True, min_length=1, max_length=10000) = Field(
        ...,
        description="Generated SQL query (validated and safe)"
    )
    confidence: StrictFloat = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score (0.0 to 1.0)"
    )
    explanation: Optional[constr(max_length=2000)] = Field(
        None,
        description="Human-readable explanation of the SQL query"
    )
    warnings: list[constr(max_length=500)] = Field(
        default_factory=list,
        description="Any warnings about the generated query"
    )
    correlation_id: constr(regex=r'^[A-Za-z0-9\-]{1,100}$') = Field(
        ...,
        description="Request correlation ID for tracing"
    )
    status: Literal["success"] = Field(
        "success",
        description="Generation status"
    )
    
    class Config:
        extra = "forbid"
```

**Security Notes:**
- Sanitize `question` to prevent SQL injection attempts
- Validate generated SQL before returning
- Never execute SQL during generation
- Log all generation attempts for audit

---

### POST /api/v1/sql/execute

**Purpose:** Execute SQL query against database

```python
from pydantic import StrictInt
from typing import Any

class SQLExecutionRequest(BaseModel):
    """Request to execute SQL query"""
    
    query_id: constr(regex=r'^[A-Za-z0-9\-]{1,100}$') = Field(
        ...,
        description="Query ID from generation step"
    )
    sql: Optional[constr(strip_whitespace=True, min_length=1, max_length=10000)] = Field(
        None,
        description="Optional SQL override (must be validated first)"
    )
    limit: StrictInt = Field(
        1000,
        ge=1,
        le=10000,
        description="Maximum rows to return (1-10000)"
    )
    timeout_seconds: StrictInt = Field(
        30,
        ge=1,
        le=300,
        description="Query timeout in seconds (1-300)"
    )
    
    class Config:
        extra = "forbid"


class SQLExecutionResponse(BaseModel):
    """SQL execution results"""
    
    query_id: constr(regex=r'^[A-Za-z0-9\-]{1,100}$') = Field(
        ...,
        description="Query identifier"
    )
    columns: list[constr(strip_whitespace=True, min_length=1, max_length=100)] = Field(
        ...,
        description="Column names in result set"
    )
    rows: list[dict[str, Any]] = Field(
        ...,
        description="Result rows (list of column->value mappings)"
    )
    row_count: StrictInt = Field(
        ...,
        ge=0,
        description="Number of rows returned"
    )
    execution_time_ms: StrictFloat = Field(
        ...,
        ge=0.0,
        description="Query execution time in milliseconds"
    )
    cached: StrictBool = Field(
        False,
        description="Whether result came from cache"
    )
    correlation_id: constr(regex=r'^[A-Za-z0-9\-]{1,100}$') = Field(
        ...,
        description="Request correlation ID"
    )
    status: Literal["success", "error"] = Field(
        ...,
        description="Execution status"
    )
    
    class Config:
        extra = "forbid"
```

**Security Notes:**
- Use parameterized queries only
- Apply row-level security (RLS) based on user role
- Validate SQL before execution
- Set strict timeout limits
- Never expose internal table structures

---

### POST /api/v1/sql/fix

**Purpose:** Fix broken SQL query based on error

```python
class SQLFixRequest(BaseModel):
    """Request to fix broken SQL"""
    
    query_id: constr(regex=r'^[A-Za-z0-9\-]{1,100}$') = Field(
        ...,
        description="Original query ID"
    )
    sql: constr(strip_whitespace=True, min_length=1, max_length=10000) = Field(
        ...,
        description="Broken SQL query to fix"
    )
    error_message: constr(strip_whitespace=True, min_length=1, max_length=2000) = Field(
        ...,
        description="Database error message"
    )
    
    class Config:
        extra = "forbid"


class SQLFixResponse(BaseModel):
    """Fixed SQL response"""
    
    query_id: constr(regex=r'^[A-Za-z0-9\-]{1,100}$') = Field(
        ...,
        description="Query identifier"
    )
    original_sql: constr(max_length=10000) = Field(
        ...,
        description="Original broken SQL"
    )
    fixed_sql: constr(strip_whitespace=True, min_length=1, max_length=10000) = Field(
        ...,
        description="Fixed SQL query"
    )
    changes: list[constr(max_length=500)] = Field(
        ...,
        description="List of changes made to fix the query"
    )
    confidence: StrictFloat = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence in fix (0.0-1.0)"
    )
    correlation_id: constr(regex=r'^[A-Za-z0-9\-]{1,100}$') = Field(
        ...,
        description="Request correlation ID"
    )
    status: Literal["success"] = Field(
        "success",
        description="Fix status"
    )
    
    class Config:
        extra = "forbid"
```

---

### POST /api/v1/sql/summarize

**Purpose:** Generate natural language summary of SQL results

```python
class SQLSummarizeRequest(BaseModel):
    """Request to summarize SQL results"""
    
    query_id: constr(regex=r'^[A-Za-z0-9\-]{1,100}$') = Field(
        ...,
        description="Query ID with results"
    )
    question: constr(strip_whitespace=True, min_length=5, max_length=1000) = Field(
        ...,
        description="Original question for context"
    )
    
    class Config:
        extra = "forbid"


class SQLSummarizeResponse(BaseModel):
    """Natural language summary response"""
    
    query_id: constr(regex=r'^[A-Za-z0-9\-]{1,100}$') = Field(
        ...,
        description="Query identifier"
    )
    summary: constr(strip_whitespace=True, min_length=1, max_length=5000) = Field(
        ...,
        description="Natural language summary of results"
    )
    insights: list[constr(max_length=500)] = Field(
        default_factory=list,
        description="Key insights from data"
    )
    row_count: StrictInt = Field(
        ...,
        ge=0,
        description="Number of rows summarized"
    )
    correlation_id: constr(regex=r'^[A-Za-z0-9\-]{1,100}$') = Field(
        ...,
        description="Request correlation ID"
    )
    status: Literal["success"] = Field(
        "success",
        description="Summary status"
    )
    
    class Config:
        extra = "forbid"
```

---

### GET /api/v1/sql/{id}/followup

**Purpose:** Generate follow-up questions based on query results

```python
class FollowUpQuestionsResponse(BaseModel):
    """Suggested follow-up questions"""
    
    query_id: constr(regex=r'^[A-Za-z0-9\-]{1,100}$') = Field(
        ...,
        description="Original query ID"
    )
    questions: list[constr(strip_whitespace=True, min_length=5, max_length=500)] = Field(
        ...,
        min_items=1,
        max_items=5,
        description="List of 1-5 suggested follow-up questions"
    )
    correlation_id: constr(regex=r'^[A-Za-z0-9\-]{1,100}$') = Field(
        ...,
        description="Request correlation ID"
    )
    status: Literal["success"] = Field(
        "success",
        description="Request status"
    )
    
    class Config:
        extra = "forbid"
```

---

## 4. Query Management Schemas

### GET /api/v1/sql/history

**Purpose:** Retrieve user's query history

```python
class QueryHistoryRequest(BaseModel):
    """Query history filter parameters"""
    
    limit: StrictInt = Field(
        50,
        ge=1,
        le=100,
        description="Maximum queries to return (1-100)"
    )
    offset: StrictInt = Field(
        0,
        ge=0,
        description="Offset for pagination"
    )
    status_filter: Optional[Literal["success", "error", "pending"]] = Field(
        None,
        description="Filter by execution status"
    )
    
    class Config:
        extra = "forbid"


class QueryHistoryItem(BaseModel):
    """Single query history entry"""
    
    query_id: constr(regex=r'^[A-Za-z0-9\-]{1,100}$') = Field(
        ...,
        description="Query unique identifier"
    )
    question: constr(strip_whitespace=True, max_length=1000) = Field(
        ...,
        description="Original natural language question"
    )
    sql: constr(max_length=10000) = Field(
        ...,
        description="Generated SQL query"
    )
    status: Literal["success", "error", "pending"] = Field(
        ...,
        description="Query execution status"
    )
    row_count: Optional[StrictInt] = Field(
        None,
        ge=0,
        description="Number of rows returned (if executed)"
    )
    execution_time_ms: Optional[StrictFloat] = Field(
        None,
        ge=0.0,
        description="Execution time in milliseconds"
    )
    created_at: datetime = Field(
        ...,
        description="Query creation timestamp (UTC)"
    )
    
    class Config:
        extra = "forbid"


class QueryHistoryResponse(BaseModel):
    """Query history list response"""
    
    queries: list[QueryHistoryItem] = Field(
        ...,
        description="List of query history items"
    )
    total_count: StrictInt = Field(
        ...,
        ge=0,
        description="Total number of queries matching filter"
    )
    limit: StrictInt = Field(
        ...,
        description="Applied limit"
    )
    offset: StrictInt = Field(
        ...,
        description="Applied offset"
    )
    correlation_id: constr(regex=r'^[A-Za-z0-9\-]{1,100}$') = Field(
        ...,
        description="Request correlation ID"
    )
    
    class Config:
        extra = "forbid"
```

---

### GET /api/v1/sql/query/{id}

**Purpose:** Get detailed information about specific query

```python
class QueryDetailResponse(BaseModel):
    """Detailed query information"""
    
    query_id: constr(regex=r'^[A-Za-z0-9\-]{1,100}$') = Field(
        ...,
        description="Query unique identifier"
    )
    question: constr(strip_whitespace=True, max_length=1000) = Field(
        ...,
        description="Original natural language question"
    )
    sql: constr(max_length=10000) = Field(
        ...,
        description="Generated SQL query"
    )
    confidence: StrictFloat = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Generation confidence score"
    )
    explanation: Optional[constr(max_length=2000)] = Field(
        None,
        description="SQL explanation"
    )
    status: Literal["success", "error", "pending"] = Field(
        ...,
        description="Execution status"
    )
    results: Optional[dict[str, Any]] = Field(
        None,
        description="Query results (if executed)"
    )
    error_message: Optional[constr(max_length=2000)] = Field(
        None,
        description="Error message (if failed)"
    )
    execution_time_ms: Optional[StrictFloat] = Field(
        None,
        ge=0.0,
        description="Execution time in milliseconds"
    )
    created_at: datetime = Field(
        ...,
        description="Query creation timestamp (UTC)"
    )
    executed_at: Optional[datetime] = Field(
        None,
        description="Query execution timestamp (UTC)"
    )
    user_id: constr(regex=r'^[A-Za-z0-9\-]{1,100}$') = Field(
        ...,
        description="User who created the query"
    )
    
    class Config:
        extra = "forbid"
```

---

## 5. Feedback System Schemas

### POST /api/v1/feedback/flag

**Purpose:** Flag query as incorrect or problematic

```python
class FeedbackFlagRequest(BaseModel):
    """Request to flag query as incorrect"""
    
    query_id: constr(regex=r'^[A-Za-z0-9\-]{1,100}$') = Field(
        ...,
        description="Query ID to flag"
    )
    flag_type: Literal["incorrect_sql", "wrong_results", "security_concern", "other"] = Field(
        ...,
        description="Type of flag"
    )
    comment: constr(strip_whitespace=True, min_length=10, max_length=2000) = Field(
        ...,
        description="Explanation of the issue (10-2000 characters)"
    )
    severity: Literal["low", "medium", "high", "critical"] = Field(
        "medium",
        description="Issue severity"
    )
    
    class Config:
        extra = "forbid"


class FeedbackFlagResponse(BaseModel):
    """Flag submission confirmation"""
    
    feedback_id: constr(regex=r'^[A-Za-z0-9\-]{1,100}$') = Field(
        ...,
        description="Unique feedback identifier"
    )
    query_id: constr(regex=r'^[A-Za-z0-9\-]{1,100}$') = Field(
        ...,
        description="Flagged query ID"
    )
    status: Literal["received", "under_review"] = Field(
        ...,
        description="Feedback status"
    )
    message: constr(max_length=500) = Field(
        ...,
        description="Confirmation message"
    )
    correlation_id: constr(regex=r'^[A-Za-z0-9\-]{1,100}$') = Field(
        ...,
        description="Request correlation ID"
    )
    
    class Config:
        extra = "forbid"
```

---

### POST /api/v1/feedback/approve

**Purpose:** Submit corrected SQL for training

```python
class FeedbackApprovalRequest(BaseModel):
    """Request to approve corrected SQL"""
    
    query_id: constr(regex=r'^[A-Za-z0-9\-]{1,100}$') = Field(
        ...,
        description="Original query ID"
    )
    corrected_sql: constr(strip_whitespace=True, min_length=1, max_length=10000) = Field(
        ...,
        description="Corrected SQL query (validated)"
    )
    explanation: constr(strip_whitespace=True, min_length=10, max_length=2000) = Field(
        ...,
        description="Explanation of corrections (10-2000 characters)"
    )
    approve_for_training: StrictBool = Field(
        True,
        description="Whether to use this correction for model training"
    )
    
    class Config:
        extra = "forbid"


class FeedbackApprovalResponse(BaseModel):
    """Approval submission confirmation"""
    
    feedback_id: constr(regex=r'^[A-Za-z0-9\-]{1,100}$') = Field(
        ...,
        description="Unique feedback identifier"
    )
    query_id: constr(regex=r'^[A-Za-z0-9\-]{1,100}$') = Field(
        ...,
        description="Original query ID"
    )
    status: Literal["approved", "pending_review"] = Field(
        ...,
        description="Approval status"
    )
    training_scheduled: StrictBool = Field(
        ...,
        description="Whether training job was scheduled"
    )
    message: constr(max_length=500) = Field(
        ...,
        description="Confirmation message"
    )
    correlation_id: constr(regex=r'^[A-Za-z0-9\-]{1,100}$') = Field(
        ...,
        description="Request correlation ID"
    )
    
    class Config:
        extra = "forbid"
```

**Security Notes:**
- Validate `corrected_sql` before storing
- Require analyst or admin role for approvals
- Log all corrections for audit trail
- Review all training data before using

---

## 6. Admin Operation Schemas

### GET /api/v1/admin/training-data

**Purpose:** Get all training data for review (admin only)

```python
class TrainingDataRequest(BaseModel):
    """Training data filter parameters"""
    
    status_filter: Optional[Literal["pending", "approved", "rejected"]] = Field(
        None,
        description="Filter by approval status"
    )
    limit: StrictInt = Field(
        50,
        ge=1,
        le=500,
        description="Maximum items to return (1-500)"
    )
    offset: StrictInt = Field(
        0,
        ge=0,
        description="Offset for pagination"
    )
    
    class Config:
        extra = "forbid"


class TrainingDataItem(BaseModel):
    """Single training data entry"""
    
    id: constr(regex=r'^[A-Za-z0-9\-]{1,100}$') = Field(
        ...,
        description="Training data ID"
    )
    question: constr(max_length=1000) = Field(
        ...,
        description="Natural language question"
    )
    sql: constr(max_length=10000) = Field(
        ...,
        description="Correct SQL query"
    )
    source: Literal["user_correction", "admin_approval", "automated"] = Field(
        ...,
        description="Source of training data"
    )
    status: Literal["pending", "approved", "rejected"] = Field(
        ...,
        description="Approval status"
    )
    created_at: datetime = Field(
        ...,
        description="Creation timestamp (UTC)"
    )
    reviewed_at: Optional[datetime] = Field(
        None,
        description="Review timestamp (UTC)"
    )
    reviewed_by: Optional[constr(regex=r'^[A-Za-z0-9\-]{1,100}$')] = Field(
        None,
        description="Admin user ID who reviewed"
    )
    
    class Config:
        extra = "forbid"


class TrainingDataResponse(BaseModel):
    """Training data list response"""
    
    items: list[TrainingDataItem] = Field(
        ...,
        description="List of training data entries"
    )
    total_count: StrictInt = Field(
        ...,
        ge=0,
        description="Total number of entries"
    )
    pending_count: StrictInt = Field(
        ...,
        ge=0,
        description="Number of pending approvals"
    )
    approved_count: StrictInt = Field(
        ...,
        ge=0,
        description="Number of approved entries"
    )
    correlation_id: constr(regex=r'^[A-Za-z0-9\-]{1,100}$') = Field(
        ...,
        description="Request correlation ID"
    )
    
    class Config:
        extra = "forbid"
```

---

### POST /api/v1/admin/training-data/approve

**Purpose:** Approve training data for model retraining (admin only)

```python
class TrainingDataApprovalRequest(BaseModel):
    """Request to approve/reject training data"""
    
    training_data_id: constr(regex=r'^[A-Za-z0-9\-]{1,100}$') = Field(
        ...,
        description="Training data entry ID"
    )
    action: Literal["approve", "reject"] = Field(
        ...,
        description="Approval action"
    )
    comment: Optional[constr(strip_whitespace=True, max_length=1000)] = Field(
        None,
        description="Optional review comment"
    )
    
    class Config:
        extra = "forbid"


class TrainingDataApprovalResponse(BaseModel):
    """Approval action confirmation"""
    
    training_data_id: constr(regex=r'^[A-Za-z0-9\-]{1,100}$') = Field(
        ...,
        description="Training data entry ID"
    )
    action: Literal["approved", "rejected"] = Field(
        ...,
        description="Action taken"
    )
    status: Literal["success"] = Field(
        "success",
        description="Operation status"
    )
    message: constr(max_length=500) = Field(
        ...,
        description="Confirmation message"
    )
    correlation_id: constr(regex=r'^[A-Za-z0-9\-]{1,100}$') = Field(
        ...,
        description="Request correlation ID"
    )
    
    class Config:
        extra = "forbid"
```

---

### DELETE /api/v1/admin/training-data/{id}

**Purpose:** Delete training data entry (admin only)

```python
class TrainingDataDeleteResponse(BaseModel):
    """Training data deletion confirmation"""
    
    training_data_id: constr(regex=r'^[A-Za-z0-9\-]{1,100}$') = Field(
        ...,
        description="Deleted training data entry ID"
    )
    status: Literal["deleted"] = Field(
        "deleted",
        description="Deletion status"
    )
    message: constr(max_length=500) = Field(
        ...,
        description="Confirmation message"
    )
    correlation_id: constr(regex=r'^[A-Za-z0-9\-]{1,100}$') = Field(
        ...,
        description="Request correlation ID"
    )
    
    class Config:
        extra = "forbid"
```

---

### POST /api/v1/admin/schema/reload

**Purpose:** Reload database schema metadata (admin only)

```python
class SchemaReloadRequest(BaseModel):
    """Request to reload database schema"""
    
    force_refresh: StrictBool = Field(
        False,
        description="Force refresh even if cache is valid"
    )
    schema_names: Optional[list[constr(strip_whitespace=True, max_length=100)]] = Field(
        None,
        description="Specific schemas to reload (if None, reload all)"
    )
    
    class Config:
        extra = "forbid"


class SchemaReloadResponse(BaseModel):
    """Schema reload confirmation"""
    
    status: Literal["success", "partial"] = Field(
        ...,
        description="Reload status"
    )
    schemas_reloaded: StrictInt = Field(
        ...,
        ge=0,
        description="Number of schemas reloaded"
    )
    tables_discovered: StrictInt = Field(
        ...,
        ge=0,
        description="Total tables discovered"
    )
    reload_time_ms: StrictFloat = Field(
        ...,
        ge=0.0,
        description="Reload time in milliseconds"
    )
    message: constr(max_length=500) = Field(
        ...,
        description="Reload summary message"
    )
    correlation_id: constr(regex=r'^[A-Za-z0-9\-]{1,100}$') = Field(
        ...,
        description="Request correlation ID"
    )
    
    class Config:
        extra = "forbid"
```

---

### GET /api/v1/admin/feedback/metrics

**Purpose:** Get feedback system metrics (admin only)

```python
class FeedbackMetricsResponse(BaseModel):
    """Feedback system metrics"""
    
    total_feedback_count: StrictInt = Field(
        ...,
        ge=0,
        description="Total number of feedback entries"
    )
    flags_count: StrictInt = Field(
        ...,
        ge=0,
        description="Number of flagged queries"
    )
    approvals_count: StrictInt = Field(
        ...,
        ge=0,
        description="Number of approved corrections"
    )
    pending_review_count: StrictInt = Field(
        ...,
        ge=0,
        description="Number of items pending admin review"
    )
    average_response_time_hours: StrictFloat = Field(
        ...,
        ge=0.0,
        description="Average time to review feedback (hours)"
    )
    feedback_by_severity: dict[Literal["low", "medium", "high", "critical"], StrictInt] = Field(
        ...,
        description="Feedback count by severity level"
    )
    top_flagged_queries: list[constr(regex=r'^[A-Za-z0-9\-]{1,100}$')] = Field(
        ...,
        max_items=10,
        description="Query IDs most frequently flagged"
    )
    correlation_id: constr(regex=r'^[A-Za-z0-9\-]{1,100}$') = Field(
        ...,
        description="Request correlation ID"
    )
    
    class Config:
        extra = "forbid"
```

---

### POST /api/v1/admin/users

**Purpose:** Create new user account (admin only)

```python
class UserCreateRequest(BaseModel):
    """Request to create new user"""
    
    email: EmailStr = Field(
        ...,
        description="User email address (must be unique)"
    )
    name: constr(strip_whitespace=True, min_length=1, max_length=200) = Field(
        ...,
        description="User full name"
    )
    role: Literal["admin", "analyst", "viewer"] = Field(
        ...,
        description="User role"
    )
    password: constr(min_length=12, max_length=128) = Field(
        ...,
        description="Initial password (min 12 characters)"
    )
    send_welcome_email: StrictBool = Field(
        True,
        description="Whether to send welcome email"
    )
    
    class Config:
        extra = "forbid"


class UserCreateResponse(BaseModel):
    """User creation confirmation"""
    
    user_id: constr(regex=r'^[A-Za-z0-9\-]{1,100}$') = Field(
        ...,
        description="New user ID"
    )
    email: EmailStr = Field(
        ...,
        description="User email address"
    )
    role: Literal["admin", "analyst", "viewer"] = Field(
        ...,
        description="Assigned role"
    )
    status: Literal["created"] = Field(
        "created",
        description="Creation status"
    )
    message: constr(max_length=500) = Field(
        ...,
        description="Confirmation message"
    )
    correlation_id: constr(regex=r'^[A-Za-z0-9\-]{1,100}$') = Field(
        ...,
        description="Request correlation ID"
    )
    
    class Config:
        extra = "forbid"
```

---

## 7. System Monitoring Schemas

### GET /health

**Purpose:** Basic health check endpoint

```python
class HealthCheckResponse(BaseModel):
    """Health check response"""
    
    status: Literal["healthy", "degraded", "unhealthy"] = Field(
        ...,
        description="Overall system health status"
    )
    version: constr(strip_whitespace=True, min_length=1, max_length=50) = Field(
        ...,
        description="API version"
    )
    timestamp: datetime = Field(
        ...,
        description="Health check timestamp (UTC)"
    )
    
    class Config:
        extra = "forbid"
```

---

### GET /api/v1/info

**Purpose:** Get API information and capabilities

```python
class APIInfoResponse(BaseModel):
    """API information response"""
    
    name: constr(strip_whitespace=True, max_length=100) = Field(
        ...,
        description="API name"
    )
    version: constr(strip_whitespace=True, max_length=50) = Field(
        ...,
        description="API version"
    )
    description: constr(max_length=500) = Field(
        ...,
        description="API description"
    )
    documentation_url: constr(max_length=500) = Field(
        ...,
        description="Documentation URL"
    )
    contact_email: EmailStr = Field(
        ...,
        description="Contact email for support"
    )
    supported_features: list[constr(max_length=100)] = Field(
        ...,
        description="List of supported features"
    )
    rate_limits: dict[str, StrictInt] = Field(
        ...,
        description="API rate limits by endpoint category"
    )
    
    class Config:
        extra = "forbid"
```

---

### GET /api/v1/schema

**Purpose:** Get database schema metadata

```python
class TableSchema(BaseModel):
    """Database table schema"""
    
    table_name: constr(strip_whitespace=True, max_length=100) = Field(
        ...,
        description="Table name"
    )
    schema_name: constr(strip_whitespace=True, max_length=100) = Field(
        ...,
        description="Schema name"
    )
    columns: list["ColumnSchema"] = Field(
        ...,
        description="List of table columns"
    )
    primary_key: list[constr(max_length=100)] = Field(
        ...,
        description="Primary key column names"
    )
    foreign_keys: list["ForeignKeySchema"] = Field(
        default_factory=list,
        description="Foreign key relationships"
    )
    
    class Config:
        extra = "forbid"


class ColumnSchema(BaseModel):
    """Database column schema"""
    
    column_name: constr(strip_whitespace=True, max_length=100) = Field(
        ...,
        description="Column name"
    )
    data_type: constr(strip_whitespace=True, max_length=100) = Field(
        ...,
        description="Column data type"
    )
    is_nullable: StrictBool = Field(
        ...,
        description="Whether column allows NULL values"
    )
    default_value: Optional[str] = Field(
        None,
        description="Default value (if any)"
    )
    description: Optional[constr(max_length=500)] = Field(
        None,
        description="Column description"
    )
    
    class Config:
        extra = "forbid"


class ForeignKeySchema(BaseModel):
    """Foreign key relationship"""
    
    column_name: constr(max_length=100) = Field(
        ...,
        description="Source column name"
    )
    referenced_table: constr(max_length=100) = Field(
        ...,
        description="Referenced table name"
    )
    referenced_column: constr(max_length=100) = Field(
        ...,
        description="Referenced column name"
    )
    
    class Config:
        extra = "forbid"


class DatabaseSchemaResponse(BaseModel):
    """Complete database schema response"""
    
    schemas: list[TableSchema] = Field(
        ...,
        description="List of all accessible tables"
    )
    total_tables: StrictInt = Field(
        ...,
        ge=0,
        description="Total number of tables"
    )
    last_updated: datetime = Field(
        ...,
        description="Schema last updated timestamp (UTC)"
    )
    correlation_id: constr(regex=r'^[A-Za-z0-9\-]{1,100}$') = Field(
        ...,
        description="Request correlation ID"
    )
    
    class Config:
        extra = "forbid"
```

---

## 8. Common Response Schemas

### Error Response

```python
class ErrorDetail(BaseModel):
    """Single error detail"""
    
    code: constr(strip_whitespace=True, max_length=50) = Field(
        ...,
        description="Error code"
    )
    message: constr(strip_whitespace=True, max_length=500) = Field(
        ...,
        description="Error message"
    )
    field: Optional[constr(max_length=100)] = Field(
        None,
        description="Field name (if field-specific error)"
    )
    
    class Config:
        extra = "forbid"


class ErrorResponse(BaseModel):
    """Standard error response"""
    
    error: constr(strip_whitespace=True, max_length=500) = Field(
        ...,
        description="Main error message"
    )
    error_code: constr(strip_whitespace=True, max_length=50) = Field(
        ...,
        description="Error code for programmatic handling"
    )
    details: list[ErrorDetail] = Field(
        default_factory=list,
        description="Detailed error information"
    )
    correlation_id: constr(regex=r'^[A-Za-z0-9\-]{1,100}$') = Field(
        ...,
        description="Request correlation ID for support"
    )
    timestamp: datetime = Field(
        ...,
        description="Error timestamp (UTC)"
    )
    
    class Config:
        extra = "forbid"
```

---

### Validation Error Response

```python
class ValidationErrorDetail(BaseModel):
    """Validation error detail"""
    
    loc: list[str] = Field(
        ...,
        description="Location of validation error (field path)"
    )
    msg: constr(max_length=500) = Field(
        ...,
        description="Validation error message"
    )
    type: constr(max_length=100) = Field(
        ...,
        description="Error type"
    )
    
    class Config:
        extra = "forbid"


class ValidationErrorResponse(BaseModel):
    """Validation error response"""
    
    detail: list[ValidationErrorDetail] = Field(
        ...,
        description="List of validation errors"
    )
    correlation_id: constr(regex=r'^[A-Za-z0-9\-]{1,100}$') = Field(
        ...,
        description="Request correlation ID"
    )
    
    class Config:
        extra = "forbid"
```

---

## 9. Security Guidelines

### Input Validation

**Critical Fields (High Risk):**
- `sql` - SQL injection risk
- `question` - Prompt injection risk
- `comment` - XSS risk
- `error_message` - Information disclosure risk

**Validation Rules:**
1. **Length Constraints:** Always enforce min/max length
2. **Character Whitelisting:** Use regex patterns for IDs
3. **Type Safety:** Use `StrictStr`, `StrictInt`, `StrictBool`
4. **Sanitization:** Strip whitespace, remove HTML/JavaScript
5. **Parameterization:** Never concatenate SQL strings

---

### Authentication & Authorization

**Requirements:**
1. **All endpoints** (except `/health`, `/api/v1/info`) require authentication
2. **JWT tokens** must expire within 24 hours
3. **Refresh tokens** valid for 7 days maximum
4. **Role-based access:**
   - `viewer` - Read-only (history, query details)
   - `analyst` - Generate, execute, feedback
   - `admin` - All operations including user management

---

### Rate Limiting

**Recommended Limits:**
```python
RATE_LIMITS = {
    "auth": "5/minute",           # Login attempts
    "sql_generate": "20/minute",   # SQL generation
    "sql_execute": "10/minute",    # Query execution
    "feedback": "5/minute",        # Feedback submission
    "admin": "100/minute"          # Admin operations
}
```

---

### Logging & Monitoring

**Required Logging:**
1. **All authentication attempts** (success/failure)
2. **All SQL generation** (question + generated SQL)
3. **All query execution** (SQL + results summary)
4. **All feedback submissions**
5. **All admin operations**
6. **All errors** (with correlation ID)

**PII Protection:**
- Never log passwords or tokens
- Redact sensitive data in query results
- Sanitize error messages before logging

---

## 10. JSON Request/Response Examples

### Authentication Example

**POST /api/v1/auth/login**

Request:
```json
{
  "email": "analyst@example.com",
  "password": "SecurePassword123!"
}
```

Response (200):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "usr-7f3b9a8c-4e2d-11ef-a1b2-0242ac120002",
    "email": "analyst@example.com",
    "name": "John Doe",
    "role": "analyst",
    "created_at": "2024-01-15T10:30:00Z",
    "last_login": "2025-11-12T18:45:00Z"
  }
}
```

---

### SQL Generation Example

**POST /api/v1/sql/generate**

Request:
```json
{
  "question": "What were the top 5 selling products in Q4 2024?",
  "schema_context": "sales database",
  "include_explanation": true
}
```

Response (200):
```json
{
  "query_id": "qry-8d4c2b1a-4e2d-11ef-b3c4-0242ac130003",
  "sql": "SELECT product_name, SUM(quantity) as total_sold FROM sales WHERE sale_date BETWEEN '2024-10-01' AND '2024-12-31' GROUP BY product_name ORDER BY total_sold DESC LIMIT 5",
  "confidence": 0.92,
  "explanation": "This query retrieves the top 5 products by total quantity sold during Q4 2024 (October-December). It groups sales by product name and sorts by total quantity in descending order.",
  "warnings": [],
  "correlation_id": "cor-9e5d3c2b-4e2d-11ef-c4d5-0242ac140004",
  "status": "success"
}
```

---

### Query Execution Example

**POST /api/v1/sql/execute**

Request:
```json
{
  "query_id": "qry-8d4c2b1a-4e2d-11ef-b3c4-0242ac130003",
  "limit": 100,
  "timeout_seconds": 30
}
```

Response (200):
```json
{
  "query_id": "qry-8d4c2b1a-4e2d-11ef-b3c4-0242ac130003",
  "columns": ["product_name", "total_sold"],
  "rows": [
    {"product_name": "Widget Pro", "total_sold": 1523},
    {"product_name": "Gadget Plus", "total_sold": 1387},
    {"product_name": "Tool Master", "total_sold": 1156},
    {"product_name": "Device Elite", "total_sold": 982},
    {"product_name": "Component X", "total_sold": 847}
  ],
  "row_count": 5,
  "execution_time_ms": 127.5,
  "cached": false,
  "correlation_id": "cor-af6e4d3c-4e2d-11ef-d5e6-0242ac150005",
  "status": "success"
}
```

---

### Feedback Flag Example

**POST /api/v1/feedback/flag**

Request:
```json
{
  "query_id": "qry-8d4c2b1a-4e2d-11ef-b3c4-0242ac130003",
  "flag_type": "incorrect_sql",
  "comment": "The query uses wrong date range - should use fiscal quarter dates instead of calendar quarter",
  "severity": "medium"
}
```

Response (200):
```json
{
  "feedback_id": "fdb-b07f5e4d-4e2d-11ef-e6f7-0242ac160006",
  "query_id": "qry-8d4c2b1a-4e2d-11ef-b3c4-0242ac130003",
  "status": "received",
  "message": "Thank you for your feedback. This query has been flagged for review by our team.",
  "correlation_id": "cor-c18g6f5e-4e2d-11ef-f7g8-0242ac170007"
}
```

---

### Error Response Example

**POST /api/v1/sql/execute**

Response (400):
```json
{
  "error": "SQL execution failed due to timeout",
  "error_code": "SQL_TIMEOUT",
  "details": [
    {
      "code": "TIMEOUT",
      "message": "Query exceeded maximum execution time of 30 seconds",
      "field": null
    }
  ],
  "correlation_id": "cor-d29h7g6f-4e2d-11ef-g8h9-0242ac180008",
  "timestamp": "2025-11-12T18:50:23Z"
}
```

---

## Conclusion

This specification provides comprehensive Pydantic schemas for all 22 API endpoints in the Vanna Insight Engine backend. All schemas enforce:

✅ Strong typing and validation  
✅ Security best practices  
✅ Clear documentation  
✅ Consistent patterns  
✅ OpenAPI compatibility  

**Next Steps:**
1. Implement schemas in `app/schemas/` module
2. Apply to FastAPI route definitions
3. Generate OpenAPI documentation
4. Write unit tests for each schema
5. Integrate with frontend TypeScript types

---

**Document Version:** 1.0.0  
**Last Updated:** November 12, 2025  
**Status:** ✅ Production-Ready

**Ready for implementation! 🚀**
