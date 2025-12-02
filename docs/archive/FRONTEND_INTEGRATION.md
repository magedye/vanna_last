# Frontend Integration Guide

## Overview

A frontend application needs to communicate with the Vanna Insight Engine API to provide users with SQL generation, validation, and explanation capabilities. This guide covers all requirements for integration.

---

## Quick Start

**API Base URL:** `http://localhost:8000` (development) or your production domain

**Authentication:** JWT Bearer tokens via `Authorization` header

**Content-Type:** `application/json` for all requests

---

## 1. Core Requirements

### 1.1 API Endpoint Access
Frontend must be able to reach:
- `http://localhost:8000` (development)
- `https://api.example.com` (production)

### 1.2 CORS Configuration
The API is configured with CORS support. Frontend running on different domain needs:
- Origins whitelist (configured in `.env`)
- Credentials enabled
- Content-Type header allowed

**Check CORS Status:**
```bash
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: POST" \
     http://localhost:8000/api/v1/login
```

### 1.3 Browser Requirements
- Modern browser (ES6+ support)
- Fetch API or Axios
- Local storage for token persistence
- HTTPS recommended for production

---

## 2. Authentication Flow

### Step 1: User Registration (Signup)

**Endpoint:** `POST /api/v1/signup`

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123",
  "full_name": "John Doe"
}
```

**Response (200):**
```json
{
  "user_id": "uuid-here",
  "email": "user@example.com",
  "full_name": "John Doe",
  "message": "User created successfully"
}
```

**Response (400):**
```json
{
  "error": "Email already registered",
  "correlation_id": "uuid"
}
```

**Frontend Implementation:**
```javascript
async function signup(email, password, fullName) {
  const response = await fetch('http://localhost:8000/api/v1/signup', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email,
      password,
      full_name: fullName
    })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Signup failed');
  }

  return response.json();
}
```

---

### Step 2: User Login

**Endpoint:** `POST /api/v1/login`

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": "uuid-here",
  "email": "user@example.com"
}
```

**Response (401):**
```json
{
  "error": "Invalid email or password",
  "correlation_id": "uuid"
}
```

**Frontend Implementation:**
```javascript
async function login(email, password) {
  const response = await fetch('http://localhost:8000/api/v1/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Login failed');
  }

  const data = await response.json();

  // Store token in localStorage
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('user_id', data.user_id);
  localStorage.setItem('user_email', data.email);

  return data;
}
```

---

### Step 3: Using JWT Token

Every authenticated request must include the JWT token in the `Authorization` header:

```javascript
const token = localStorage.getItem('access_token');

const response = await fetch('http://localhost:8000/api/v1/sql/generate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    question: "How many users signed up last month?"
  })
});
```

**Create a Helper Function:**
```javascript
async function apiCall(endpoint, method = 'GET', body = null) {
  const token = localStorage.getItem('access_token');

  const headers = {
    'Content-Type': 'application/json'
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const options = {
    method,
    headers
  };

  if (body) {
    options.body = JSON.stringify(body);
  }

  const response = await fetch(
    `http://localhost:8000${endpoint}`,
    options
  );

  if (response.status === 401) {
    // Token expired or invalid - clear and redirect to login
    localStorage.removeItem('access_token');
    window.location.href = '/login';
    return null;
  }

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || `API error: ${response.status}`);
  }

  return response.json();
}
```

---

## 3. API Endpoints Reference

### Public Endpoints (No Authentication)

#### 3.1 Generate SQL (Public)
**Endpoint:** `POST /api/v1/generate-sql`

**Request:**
```json
{
  "question": "How many users are active?"
}
```

**Response:**
```json
{
  "sql": "SELECT COUNT(*) FROM users WHERE is_active = true",
  "correlation_id": "uuid",
  "status": "success"
}
```

**Frontend Code:**
```javascript
async function generateSQL(question) {
  const response = await fetch('http://localhost:8000/api/v1/generate-sql', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question })
  });

  return response.json();
}
```

---

#### 3.2 Fix SQL (Public)
**Endpoint:** `POST /api/v1/fix-sql`

**Request:**
```json
{
  "sql": "SELECT * FORM users",
  "error_msg": "Syntax error near 'FORM'"
}
```

**Response:**
```json
{
  "sql": "SELECT * FROM users",
  "correlation_id": "uuid",
  "status": "success"
}
```

---

#### 3.3 Explain SQL (Public)
**Endpoint:** `POST /api/v1/explain-sql`

**Request:**
```json
{
  "sql": "SELECT * FROM users WHERE created_at > NOW() - INTERVAL 7 DAY"
}
```

**Response:**
```json
{
  "explanation": "This query returns all users who registered within the last 7 days",
  "correlation_id": "uuid",
  "status": "success"
}
```

---

### Protected Endpoints (Authentication Required)

#### 3.4 Generate SQL (Authenticated)
**Endpoint:** `POST /api/v1/sql/generate`

**Request:**
```json
{
  "question": "How many users are active?",
  "schema_name": "public",
  "force_rule_based": false
}
```

**Response:**
```json
{
  "sql": "SELECT COUNT(*) FROM users WHERE is_active = true",
  "correlation_id": "uuid",
  "confidence": 0.95,
  "intent": {
    "query_type": "COUNT",
    "entities": {
      "tables": ["users"],
      "columns": ["is_active"],
      "values": [true]
    },
    "filters": [
      {
        "column": "is_active",
        "operator": "=",
        "value": true
      }
    ],
    "confidence": 0.95
  },
  "warnings": [],
  "status": "success"
}
```

**Frontend Code:**
```javascript
async function generateSQLAuth(question) {
  return apiCall('/api/v1/sql/generate', 'POST', {
    question,
    schema_name: 'public',
    force_rule_based: false
  });
}
```

---

#### 3.5 Validate SQL (Authenticated)
**Endpoint:** `POST /api/v1/sql/validate`

**Request:**
```json
{
  "sql": "SELECT * FROM users WHERE id = 123",
  "question_id": "optional-reference-id"
}
```

**Response:**
```json
{
  "is_valid": true,
  "correlation_id": "uuid",
  "issues": [],
  "status": "success"
}
```

**Response (Invalid SQL):**
```json
{
  "is_valid": false,
  "correlation_id": "uuid",
  "issues": [
    {
      "severity": "error",
      "message": "Syntax error near 'FORM'",
      "line": 1
    }
  ],
  "status": "success"
}
```

---

#### 3.6 Execute SQL
**Endpoint:** `POST /api/v1/sql/execute`

**Request:**
```json
{
  "sql": "SELECT COUNT(*) FROM users WHERE created_at > NOW() - INTERVAL 30 DAY",
  "question": "How many users registered this month?"
}
```

**Response (200):**
```json
{
  "rows": [
    { "count": 1234 }
  ],
  "columns": ["count"],
  "row_count": 1,
  "execution_time_ms": 245,
  "correlation_id": "uuid",
  "cached": false,
  "status": "success"
}
```

**Response (400 - Invalid SQL):**
```json
{
  "error": "Syntax error in SQL query",
  "correlation_id": "uuid"
}
```

**Frontend Code:**
```javascript
async function executeSQLQuery(sql, question) {
  return apiCall('/api/v1/sql/execute', 'POST', {
    sql,
    question
  });
}

// Usage in component
const result = await executeSQLQuery(
  "SELECT * FROM users LIMIT 10",
  "Show me the first 10 users"
);

console.log(`Query executed in ${result.execution_time_ms}ms`);
console.log(`Results:`, result.rows);
console.log(`Columns:`, result.columns);
```

---

#### 3.7 Query History
**Endpoint:** `GET /api/v1/sql/history?limit=10`

**Query Parameters:**
- `limit` (optional): Number of queries to return (default: 10, max: 100)

**Response:**
```json
[
  {
    "id": "uuid",
    "question": "How many users?",
    "generated_sql": "SELECT COUNT(*) FROM users",
    "status": "executed",
    "execution_time_ms": 125,
    "created_at": "2025-11-20T10:30:00Z"
  },
  {
    "id": "uuid-2",
    "question": "List active users",
    "generated_sql": "SELECT * FROM users WHERE is_active = true",
    "status": "executed",
    "execution_time_ms": 342,
    "created_at": "2025-11-20T09:15:00Z"
  }
]
```

**Frontend Code:**
```javascript
async function getQueryHistory(limit = 10) {
  return apiCall(`/api/v1/sql/history?limit=${limit}`, 'GET');
}

// Usage
const history = await getQueryHistory(20);
history.forEach(query => {
  console.log(`${query.created_at}: ${query.question}`);
  console.log(`  SQL: ${query.generated_sql}`);
  console.log(`  Execution time: ${query.execution_time_ms}ms`);
});
```

**Statuses:**
- `generated` - SQL was generated but not yet executed
- `executed` - SQL was executed successfully
- `failed` - Execution failed with error

---

#### 3.8 Submit Feedback
**Endpoint:** `POST /api/v1/feedback`

**Request:**
```json
{
  "query_id": "uuid",
  "rating": 5,
  "comment": "Perfect SQL!",
  "approved_for_training": true
}
```

**Response:**
```json
{
  "feedback_id": "uuid",
  "query_id": "uuid",
  "status": "recorded"
}
```

**Frontend Code:**
```javascript
async function submitFeedback(queryId, rating, comment, approveForTraining = false) {
  return apiCall('/api/v1/feedback', 'POST', {
    query_id: queryId,
    rating,
    comment,
    approved_for_training: approveForTraining
  });
}

// Usage in component
const feedback = await submitFeedback(
  queryId,
  5,
  "This SQL was exactly what I needed!",
  true // Approve for model training
);
```

**Rating Scale:** 1-5 stars
- 1: Not helpful
- 2: Somewhat helpful
- 3: Moderately helpful
- 4: Very helpful
- 5: Excellent

---

#### 3.9 Get Feedback for Query
**Endpoint:** `GET /api/v1/feedback/{query_id}`

**Response:**
```json
{
  "query_id": "uuid",
  "feedback_items": [
    {
      "id": "feedback-uuid",
      "rating": 5,
      "comment": "Great query!",
      "created_at": "2025-11-20T10:30:00Z"
    }
  ],
  "total_count": 1
}
```

---

#### 3.10 Request Training
**Endpoint:** `POST /api/v1/feedback/train`

**Request:**
```json
{
  "feedback_ids": ["feedback-uuid-1", "feedback-uuid-2"]
}
```

Or without specific feedback IDs to use all approved feedback:
```json
{}
```

**Response:**
```json
{
  "training_id": "uuid",
  "status": "queued",
  "items_count": 15,
  "message": "Training job queued with 15 feedback items",
  "schema_version": "1.0.0"
}
```

**Frontend Code:**
```javascript
async function requestTraining(feedbackIds = null) {
  return apiCall('/api/v1/feedback/train', 'POST', {
    feedback_ids: feedbackIds
  });
}

// Usage - Train on all approved feedback
const training = await requestTraining();
console.log(`Training queued: ${training.training_id}`);
console.log(`Items: ${training.items_count}`);
```

---

### Admin Endpoints (Admin Role Required)

#### 3.11 Get Configuration
**Endpoint:** `GET /admin/config`

**Response:**
```json
{
  "environment": "production",
  "debug_mode": false,
  "version": "1.0.0",
  "features": {
    "sql_generation": true,
    "sql_fixing": true,
    "sql_explanation": true,
    "circuit_breaker": true
  }
}
```

---

## 3.12 Roles & Permissions Reference

Understanding user roles is critical for showing/hiding features in your frontend.

### User Roles

| Role | Default | Can Generate SQL | Can Execute SQL | Can View Feedback | Can Request Training | Can Access Admin |
|------|---------|------------------|-----------------|-------------------|----------------------|------------------|
| viewer | Yes | ✓ | ✓ | ✓ | ✗ | ✗ |
| analyst | No | ✓ | ✓ | ✓ | ✓ | ✗ |
| admin | No | ✓ | ✓ | ✓ | ✓ | ✓ |

### Endpoint Access by Role

```javascript
const endpointAccess = {
  // Public (no role required)
  'POST /api/v1/login': ['public'],
  'POST /api/v1/signup': ['public'],
  'POST /api/v1/generate-sql': ['public'],
  'POST /api/v1/fix-sql': ['public'],
  'POST /api/v1/explain-sql': ['public'],

  // Viewer+ (authenticated users)
  'POST /api/v1/sql/generate': ['viewer', 'analyst', 'admin'],
  'POST /api/v1/sql/validate': ['viewer', 'analyst', 'admin'],
  'POST /api/v1/sql/execute': ['viewer', 'analyst', 'admin'],
  'GET /api/v1/sql/history': ['viewer', 'analyst', 'admin'],
  'POST /api/v1/feedback': ['viewer', 'analyst', 'admin'],
  'GET /api/v1/feedback/{id}': ['viewer', 'analyst', 'admin'],

  // Analyst+ (advanced features)
  'POST /api/v1/feedback/train': ['analyst', 'admin'],
  'GET /analytics': ['analyst', 'admin'],

  // Admin only
  'GET /admin/config': ['admin'],
  'POST /admin/config': ['admin'],
  '/admin/dashboard/*': ['admin'],
};

// Example: Check if user can access feature
function canUserTrain(userRole) {
  return ['analyst', 'admin'].includes(userRole);
}

// Hide/show features based on role
const isAdmin = currentUserRole === 'admin';
const isAnalyst = ['analyst', 'admin'].includes(currentUserRole);
const isViewer = ['viewer', 'analyst', 'admin'].includes(currentUserRole);
```

---

## 4. Error Handling

### Standard Error Response Format
All errors follow this format:
```json
{
  "error": "Error message",
  "correlation_id": "uuid-for-tracking"
}
```

### Common HTTP Status Codes

| Status | Meaning | Cause | Action |
|--------|---------|-------|--------|
| 200 | OK | Successful request | Process response |
| 201 | Created | Resource created | Process response |
| 400 | Bad Request | Invalid input/validation failed | Check request format and values |
| 401 | Unauthorized | Missing/invalid JWT token | Redirect to login, clear token |
| 403 | Forbidden | User lacks required role/permission | Show permission denied message |
| 404 | Not Found | Resource doesn't exist | Show "not found" message |
| 429 | Too Many Requests | Rate limit exceeded | Implement exponential backoff retry |
| 500 | Server Error | Unexpected server error | Show error with correlation ID, retry later |

### Frontend Error Handler
```javascript
async function handleAPIError(response) {
  const errorData = await response.json();
  const { error, correlation_id } = errorData;

  switch (response.status) {
    case 400:
      console.error('Bad Request:', error);
      return {
        message: 'Invalid request. Please check your input.',
        correlationId: correlation_id
      };

    case 401:
      console.warn('Unauthorized - clearing token and redirecting');
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_id');
      localStorage.removeItem('user_email');
      window.location.href = '/login';
      return {
        message: 'Session expired. Please login again.',
        correlationId: correlation_id
      };

    case 403:
      console.error('Forbidden:', error);
      return {
        message: 'You do not have permission to perform this action.',
        correlationId: correlation_id
      };

    case 404:
      console.error('Not Found:', error);
      return {
        message: 'The requested resource was not found.',
        correlationId: correlation_id
      };

    case 429:
      console.warn('Rate Limited - implement exponential backoff');
      return {
        message: 'Too many requests. Please wait a moment and try again.',
        correlationId: correlation_id,
        retryAfter: response.headers.get('Retry-After') || 60
      };

    case 500:
      console.error('Server Error:', error);
      return {
        message: 'Server error occurred. Please try again later.',
        correlationId: correlation_id
      };

    default:
      return {
        message: error || `HTTP ${response.status} error`,
        correlationId: correlation_id
      };
  }
}

// Retry with exponential backoff
async function apiCallWithRetry(endpoint, method = 'GET', body = null, maxRetries = 3) {
  let lastError;

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      const token = localStorage.getItem('access_token');
      const headers = { 'Content-Type': 'application/json' };

      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const options = { method, headers };
      if (body) options.body = JSON.stringify(body);

      const response = await fetch(
        `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}${endpoint}`,
        options
      );

      if (!response.ok) {
        if (response.status === 429) {
          // Rate limited - implement exponential backoff
          const retryAfter = response.headers.get('Retry-After') || Math.pow(2, attempt);
          console.warn(`Rate limited. Retrying after ${retryAfter}s...`);
          await new Promise(resolve => setTimeout(resolve, retryAfter * 1000));
          continue;
        }

        const errorInfo = await handleAPIError(response);
        throw new Error(errorInfo.message);
      }

      return await response.json();
    } catch (error) {
      lastError = error;

      if (attempt < maxRetries - 1) {
        const delay = Math.pow(2, attempt) * 1000; // Exponential backoff
        console.warn(`Attempt ${attempt + 1} failed. Retrying in ${delay}ms...`);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }

  throw lastError || new Error('Max retries exceeded');
}
```

---

## 5. Rate Limiting

The API applies rate limits to prevent abuse:

**Limits by Endpoint Type:**
- Public endpoints: 100/hour
- Authenticated endpoints: 500/hour
- Admin endpoints: 1000/hour

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1634567890
Retry-After: 3600
```

**Frontend Handling:**
```javascript
async function apiCallWithRetry(endpoint, method, body, retries = 3) {
  for (let attempt = 0; attempt < retries; attempt++) {
    const response = await apiCall(endpoint, method, body);

    if (response.status === 429) {
      const retryAfter = response.headers.get('Retry-After') || 60;
      console.warn(`Rate limited. Retrying after ${retryAfter}s...`);
      await new Promise(resolve => setTimeout(resolve, retryAfter * 1000));
      continue;
    }

    return response;
  }

  throw new Error('Max retries exceeded');
}
```

---

## 6. TypeScript Types

Define types for API responses:

```typescript
// Auth
export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: 'bearer';
  user_id: string;
  email: string;
}

export interface SignupRequest {
  email: string;
  password: string;
  full_name: string;
}

// SQL Generation
export interface GenerateSQLRequest {
  question: string;
  schema_name?: string;
  force_rule_based?: boolean;
}

export interface Intent {
  query_type: string;
  entities: Record<string, string[]>;
  filters: Record<string, string>[];
  confidence: number;
}

export interface GenerateSQLResponse {
  sql: string;
  correlation_id: string;
  confidence: number;
  intent: Intent;
  warnings: string[];
  status: 'success' | 'error';
}

// SQL Validation
export interface ValidateSQLRequest {
  sql: string;
  question_id?: string;
}

export interface ValidationIssue {
  severity: 'error' | 'warning';
  message: string;
  line: number;
}

export interface ValidateSQLResponse {
  is_valid: boolean;
  correlation_id: string;
  issues: ValidationIssue[];
  status: 'success' | 'error';
}

// Error
export interface ErrorResponse {
  error: string;
  correlation_id: string;
}
```

---

## 7. React Integration Example

### 7.1 Custom Hook for API
```javascript
import { useState, useCallback } from 'react';

export function useAPI() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const apiCall = useCallback(async (endpoint, method = 'GET', body = null) => {
    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('access_token');
      const headers = { 'Content-Type': 'application/json' };

      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const options = { method, headers };
      if (body) options.body = JSON.stringify(body);

      const response = await fetch(
        `http://localhost:8000${endpoint}`,
        options
      );

      if (response.status === 401) {
        localStorage.removeItem('access_token');
        window.location.href = '/login';
        return null;
      }

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { apiCall, loading, error };
}
```

### 7.2 SQL Generator Component
```javascript
import { useState } from 'react';
import { useAPI } from './useAPI';

export function SQLGenerator() {
  const { apiCall, loading, error } = useAPI();
  const [question, setQuestion] = useState('');
  const [result, setResult] = useState(null);

  const handleGenerate = async (e) => {
    e.preventDefault();

    try {
      const data = await apiCall('/api/v1/sql/generate', 'POST', {
        question
      });

      setResult(data);
    } catch (err) {
      console.error('Generation failed:', err);
    }
  };

  return (
    <div>
      <form onSubmit={handleGenerate}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question..."
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Generating...' : 'Generate SQL'}
        </button>
      </form>

      {error && <div className="error">{error}</div>}

      {result && (
        <div className="result">
          <h3>Generated SQL:</h3>
          <pre>{result.sql}</pre>
          <p>Confidence: {(result.confidence * 100).toFixed(1)}%</p>
        </div>
      )}
    </div>
  );
}
```

### 7.3 Login Component
```javascript
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAPI } from './useAPI';

export function LoginPage() {
  const navigate = useNavigate();
  const { apiCall, loading, error } = useAPI();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();

    try {
      const data = await apiCall('/api/v1/login', 'POST', {
        email,
        password
      });

      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('user_id', data.user_id);
      localStorage.setItem('user_email', data.email);

      navigate('/dashboard');
    } catch (err) {
      console.error('Login failed:', err);
    }
  };

  return (
    <form onSubmit={handleLogin}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
        required
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
        required
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>
      {error && <p className="error">{error}</p>}
    </form>
  );
}
```

---

## 8. Vue Integration Example

### 8.1 Composable
```javascript
import { ref } from 'vue';

export function useAPI() {
  const loading = ref(false);
  const error = ref(null);

  const apiCall = async (endpoint, method = 'GET', body = null) => {
    loading.value = true;
    error.value = null;

    try {
      const token = localStorage.getItem('access_token');
      const headers = { 'Content-Type': 'application/json' };

      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const options = { method, headers };
      if (body) options.body = JSON.stringify(body);

      const response = await fetch(
        `http://localhost:8000${endpoint}`,
        options
      );

      if (response.status === 401) {
        localStorage.removeItem('access_token');
        window.location.href = '/login';
        return null;
      }

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error);
      }

      return await response.json();
    } catch (err) {
      error.value = err.message;
      throw err;
    } finally {
      loading.value = false;
    }
  };

  return { apiCall, loading, error };
}
```

### 8.2 Component
```vue
<template>
  <div class="generator">
    <form @submit.prevent="generateSQL">
      <input
        v-model="question"
        type="text"
        placeholder="Ask a question..."
        :disabled="loading"
      />
      <button :disabled="loading">
        {{ loading ? 'Generating...' : 'Generate SQL' }}
      </button>
    </form>

    <div v-if="error" class="error">{{ error }}</div>

    <div v-if="result" class="result">
      <h3>Generated SQL:</h3>
      <pre>{{ result.sql }}</pre>
      <p>Confidence: {{ (result.confidence * 100).toFixed(1) }}%</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAPI } from '@/composables/useAPI';

const question = ref('');
const result = ref(null);
const { apiCall, loading, error } = useAPI();

async function generateSQL() {
  try {
    result.value = await apiCall('/api/v1/sql/generate', 'POST', {
      question: question.value
    });
  } catch (err) {
    console.error('Generation failed:', err);
  }
}
</script>
```

---

## 9. Environment Configuration

### Frontend Environment Variables
```bash
# .env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_TIMEOUT=30000

# .env.production
REACT_APP_API_URL=https://api.example.com
REACT_APP_API_TIMEOUT=30000
```

### Usage in Code
```javascript
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const response = await fetch(`${API_URL}/api/v1/login`, options);
```

---

## 10. Checklist for Frontend Integration

- [ ] **Auth Flow**
  - [ ] Signup form with email/password validation
  - [ ] Login form that stores JWT token
  - [ ] Logout function that clears token
  - [ ] Auto-redirect to login on 401
  - [ ] Token refresh logic (if applicable)

- [ ] **SQL Generation**
  - [ ] Text input for natural language questions
  - [ ] Display generated SQL in editable format
  - [ ] Show confidence score
  - [ ] Display query intent/entities
  - [ ] Handle loading and error states

- [ ] **SQL Validation**
  - [ ] Real-time validation as user edits SQL
  - [ ] Display validation issues with line numbers
  - [ ] Syntax highlighting
  - [ ] Suggestions for fixes

- [ ] **Query History**
  - [ ] List previous queries
  - [ ] Pagination support
  - [ ] Re-run query functionality
  - [ ] Delete history option

- [ ] **Feedback**
  - [ ] Rating system (1-5 stars)
  - [ ] Feedback comments
  - [ ] Track helpful/not helpful
  - [ ] Show feedback history

- [ ] **Error Handling**
  - [ ] Display user-friendly error messages
  - [ ] Correlation ID for support
  - [ ] Retry mechanism
  - [ ] Rate limit handling

- [ ] **Performance**
  - [ ] Debounce API calls
  - [ ] Cache frequently used queries
  - [ ] Pagination for large lists
  - [ ] Loading spinners

- [ ] **Security**
  - [ ] HTTPS in production
  - [ ] Secure token storage (localStorage vs SessionStorage)
  - [ ] CSRF protection
  - [ ] Input validation
  - [ ] Password requirements display

---

## 11. Testing

### Mock API Responses
```javascript
// __mocks__/api.js
export const mockGenerateSQLResponse = {
  sql: "SELECT COUNT(*) FROM users",
  correlation_id: "test-uuid",
  confidence: 0.95,
  intent: { /* ... */ },
  warnings: [],
  status: "success"
};
```

### Test Example
```javascript
import { render, screen, fireEvent } from '@testing-library/react';
import { SQLGenerator } from './SQLGenerator';

jest.mock('./useAPI', () => ({
  useAPI: () => ({
    apiCall: jest.fn().mockResolvedValue(mockGenerateSQLResponse),
    loading: false,
    error: null
  })
}));

test('generates SQL on form submit', async () => {
  render(<SQLGenerator />);

  fireEvent.change(screen.getByPlaceholderText('Ask a question...'), {
    target: { value: 'Count users' }
  });

  fireEvent.click(screen.getByText('Generate SQL'));

  expect(await screen.findByText(/SELECT COUNT/)).toBeInTheDocument();
});
```

---

## 12. Deployment Considerations

### CORS for Production
Add frontend domain to `.env.prod`:
```bash
CORS_ORIGINS=https://app.example.com,https://www.example.com
```

### API URL Configuration
```bash
# Frontend .env.production
REACT_APP_API_URL=https://api.example.com
```

### SSL/TLS
- Use HTTPS in production
- API should also use HTTPS
- Consider certificate pinning for mobile apps

### Rate Limiting
- Implement client-side retry with exponential backoff
- Show user-friendly "too many requests" message
- Cache results where applicable

---

## 13. Advanced Patterns

### 13.1 Query Caching

Cache generated SQL to reduce API calls:

```javascript
class QueryCache {
  constructor(maxSize = 100, ttlMs = 3600000) {
    this.cache = new Map();
    this.maxSize = maxSize;
    this.ttlMs = ttlMs;
  }

  set(question, sql) {
    if (this.cache.size >= this.maxSize) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }

    this.cache.set(question, {
      sql,
      timestamp: Date.now()
    });
  }

  get(question) {
    const entry = this.cache.get(question);
    if (!entry) return null;

    // Check if expired
    if (Date.now() - entry.timestamp > this.ttlMs) {
      this.cache.delete(question);
      return null;
    }

    return entry.sql;
  }

  clear() {
    this.cache.clear();
  }
}

// Usage
const queryCache = new QueryCache();

async function generateSQLWithCache(question) {
  // Check cache first
  const cached = queryCache.get(question);
  if (cached) {
    console.log('Using cached SQL');
    return { sql: cached, cached: true };
  }

  // Call API
  const result = await apiCall('/api/v1/sql/generate', 'POST', {
    question
  });

  // Cache result
  queryCache.set(question, result.sql);
  return { ...result, cached: false };
}
```

### 13.2 Token Refresh & Session Management

```javascript
class SessionManager {
  constructor() {
    this.tokenExpireTime = null;
    this.refreshThreshold = 5 * 60 * 1000; // 5 minutes before expiry
  }

  login(data) {
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('user_id', data.user_id);
    localStorage.setItem('user_email', data.email);
    localStorage.setItem('login_time', Date.now().toString());

    // Calculate token expiry (assuming 24-hour token)
    this.tokenExpireTime = Date.now() + 24 * 60 * 60 * 1000;
  }

  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('user_email');
    localStorage.removeItem('login_time');
    this.tokenExpireTime = null;
  }

  isLoggedIn() {
    return !!localStorage.getItem('access_token');
  }

  getToken() {
    if (!this.isLoggedIn()) return null;

    // Check if token should be refreshed
    if (this.tokenExpireTime && Date.now() > this.tokenExpireTime - this.refreshThreshold) {
      console.warn('Token expiring soon');
      // Trigger logout/redirect to login
      this.logout();
      window.location.href = '/login';
      return null;
    }

    return localStorage.getItem('access_token');
  }

  getUserInfo() {
    return {
      user_id: localStorage.getItem('user_id'),
      email: localStorage.getItem('user_email'),
      token: this.getToken()
    };
  }
}
```

### 13.3 Request Deduplication

Prevent duplicate API calls for the same request:

```javascript
class RequestDeduplicator {
  constructor() {
    this.pending = new Map();
  }

  async execute(key, request) {
    // If request already pending, return same promise
    if (this.pending.has(key)) {
      return this.pending.get(key);
    }

    // Execute request and cache promise
    const promise = request().finally(() => {
      this.pending.delete(key);
    });

    this.pending.set(key, promise);
    return promise;
  }
}

// Usage
const deduplicator = new RequestDeduplicator();

async function generateSQL(question) {
  return deduplicator.execute(
    `generate-${question}`,
    () => apiCall('/api/v1/sql/generate', 'POST', { question })
  );
}

// Multiple calls with same question only result in one API call
await Promise.all([
  generateSQL("How many users?"),
  generateSQL("How many users?"),
  generateSQL("How many users?")
]);
```

### 13.4 Analytics & Error Tracking

Track errors and performance:

```javascript
class AnalyticsTracker {
  trackAPICall(method, endpoint, status, duration, correlationId) {
    const event = {
      type: 'api_call',
      method,
      endpoint,
      status,
      duration,
      correlationId,
      timestamp: new Date().toISOString()
    };

    if (status >= 400) {
      // Send error to monitoring service
      this.trackError(event);
    }

    // Send analytics
    console.log('Analytics:', event);
  }

  trackError(errorEvent) {
    // Send to Sentry, LogRocket, etc.
    console.error('Error tracked:', errorEvent);
  }

  trackFeatureUsage(feature) {
    console.log(`Feature used: ${feature}`);
  }
}

// Usage in API wrapper
const tracker = new AnalyticsTracker();

async function trackedAPICall(endpoint, method = 'GET', body = null) {
  const startTime = performance.now();
  let correlationId = null;

  try {
    const response = await apiCall(endpoint, method, body);
    correlationId = response.correlation_id;
    const duration = performance.now() - startTime;

    tracker.trackAPICall(method, endpoint, 200, duration, correlationId);
    return response;
  } catch (error) {
    const duration = performance.now() - startTime;
    tracker.trackAPICall(method, endpoint, error.status || 500, duration, correlationId);
    throw error;
  }
}
```

---

## 14. Support & Documentation

### API Resources

- **Live Docs:** `http://localhost:8000/docs` (Swagger UI)
- **ReDoc:** `http://localhost:8000/redoc` (Alternative docs)
- **OpenAPI Schema:** `http://localhost:8000/openapi.json` (Machine-readable spec)
- **Health Check:** `GET http://localhost:8000/health` (Dependency status)
- **Metrics:** `GET http://localhost:8000/metrics` (Prometheus format)
- **JSON Metrics:** `GET http://localhost:8000/metrics/json` (JSON format metrics)

### Documentation Files

- **ALL_ENDPOINTS.md** - Complete endpoint reference
- **ENDPOINTS_QUICK_REFERENCE.md** - Quick lookup
- **AUTH_FIXED.md** - Authentication details
- **ROLES_AND_PERMISSIONS.md** - Access control
- **COMPLETE_ENDPOINT_INVENTORY.md** - Full inventory

### Getting Help

1. Check the endpoint documentation at `/docs`
2. Review error messages and correlation IDs in logs
3. Use correlation IDs for support tickets
4. Check rate limit status in response headers
5. Verify JWT token validity and expiration

### Common Issues

| Issue | Solution |
|-------|----------|
| 401 Unauthorized | Check JWT token in localStorage; re-login if expired |
| 403 Forbidden | Verify user role has access; check ROLES_AND_PERMISSIONS.md |
| 429 Rate Limited | Implement exponential backoff; check rate limits for your tier |
| CORS Error | Verify API domain is in CORS_ORIGINS; check browser console |
| Stale Data | Check cache TTL; clear browser cache if needed |
| Slow Queries | Use correlation IDs to trace request; optimize SQL |
