# Vanna AI: Code Examples & Implementation Guide

## Table of Contents
1. Basic Setup Examples
2. Database Connections
3. Training Patterns
4. Query & Execution Patterns
5. Production Deployment
6. Advanced Patterns

---

## 1. BASIC SETUP EXAMPLES

### 1.1 Minimal Setup with Default Configuration

```python
import vanna as vn

# Get API key
api_key = vn.get_api_key('your-email@example.com')
vn.set_api_key(api_key)

# Set model (creates a unique model for your data)
vn.set_model('my_first_model')

# Connect to database
vn.connect_to_sqlite('chinook.db')

# Ask a question
result = vn.ask('What are the top 10 artists?')
print(result)
```

### 1.2 Setup with Explicit LLM & Vector Store

```python
from vanna.remote import VannaDefault
from vanna.chromadb import ChromaDB_VectorStore
from vanna.openai import OpenAI_Chat

# Option 1: Using Vanna's defaults (simplest)
vn = VannaDefault(
    model='my_model',
    api_key='your-vanna-api-key'
)

# Option 2: Custom combination
class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

vn = MyVanna(config={
    'api_key': 'sk-your-openai-key',
    'model': 'gpt-4-turbo'
})
```

### 1.3 Environment-Based Configuration

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Load configuration from .env
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
VANNA_API_KEY = os.getenv('VANNA_API_KEY')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

from vanna.remote import VannaDefault
vn = VannaDefault(
    model=os.getenv('VANNA_MODEL_NAME', 'default_model'),
    api_key=VANNA_API_KEY
)

vn.connect_to_postgres(
    host=DB_HOST,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    port=5432
)
```

---

## 2. DATABASE CONNECTIONS

### 2.1 PostgreSQL with Connection Pooling

```python
from sqlalchemy import create_engine
import psycopg2

# Create connection string
conn_string = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"

# Connect using Vanna helper
vn.connect_to_postgres(
    host=host,
    dbname=dbname,
    user=user,
    password=password,
    port=5432
)

# Verify connection
test_query = vn.run_sql("SELECT version();")
print("PostgreSQL version:", test_query.iloc[0, 0])
```

### 2.2 MySQL Connection with SSL

```python
vn.connect_to_mysql(
    host='mysql.example.com',
    user='app_user',
    password='secure_password',
    dbname='production_db',
    port=3306
)

# Test connection
tables = vn.run_sql("SHOW TABLES;")
print(f"Found {len(tables)} tables")
```

### 2.3 BigQuery Connection with Service Account

```python
vn.connect_to_bigquery(
    project_id='my-gcp-project',
    cred_file_path='path/to/service-account-key.json'
)

# Query specific dataset
vn.set_sql_context({
    'dataset': 'analytics'
})
```

### 2.4 Snowflake Connection with Key Pair Authentication

```python
vn.connect_to_snowflake(
    account='xy12345',
    user='analytics_user',
    password='secure_password',
    warehouse='COMPUTE_WH',
    database='ANALYTICS_DB',
    schema='PUBLIC'
)
```

### 2.5 DuckDB In-Memory Database (Testing)

```python
import duckdb

# Create in-memory database
conn = duckdb.connect(':memory:')

# Create sample table
conn.execute("""
    CREATE TABLE sales (
        sale_id INT,
        customer_id INT,
        amount DECIMAL(10, 2),
        sale_date DATE
    )
""")

# Insert sample data
conn.execute("""
    INSERT INTO sales VALUES
    (1, 101, 50.00, '2024-01-01'),
    (2, 102, 75.50, '2024-01-02')
""")

# Connect Vanna
vn.connect_to_duckdb(':memory:')
```

---

## 3. TRAINING PATTERNS

### 3.1 Complete Training with All Three Methods

```python
# 1. Add database schema (DDL)
vn.train(ddl="""
    CREATE TABLE customers (
        customer_id INT PRIMARY KEY,
        first_name VARCHAR(50),
        last_name VARCHAR(50),
        email VARCHAR(100),
        registration_date DATE,
        country VARCHAR(50)
    );
    
    CREATE TABLE orders (
        order_id INT PRIMARY KEY,
        customer_id INT,
        order_date DATE,
        total_amount DECIMAL(10, 2),
        status VARCHAR(20),
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    );
""")

# 2. Add business documentation
vn.train(documentation="""
    CUSTOMERS table:
    - Represents registered users in the system
    - registration_date uses UTC timezone
    - country uses ISO 3166-1 alpha-2 codes
    
    ORDERS table:
    - Tracks all customer transactions
    - status values: 'pending', 'shipped', 'delivered', 'cancelled'
    - total_amount includes tax
    - A customer can have multiple orders
    
    Business Rules:
    - Premium customers have 'PREMIUM' prefix in their ID
    - Orders over $1000 require manager approval
    - Cancelled orders should not be included in revenue calculations
""")

# 3. Add example SQL queries
vn.train(sql="""
    -- Query: Get customer with highest spending
    SELECT 
        c.customer_id,
        c.first_name,
        c.last_name,
        SUM(o.total_amount) as total_spending
    FROM customers c
    INNER JOIN orders o ON c.customer_id = o.customer_id
    WHERE o.status != 'cancelled'
    GROUP BY c.customer_id, c.first_name, c.last_name
    ORDER BY total_spending DESC
    LIMIT 10;
""")

# Verify training
training_data = vn.get_training_data()
print(f"Total training records: {len(training_data)}")
```

### 3.2 Automatic Schema Training

```python
import pandas as pd

# Extract information schema
df_information_schema = vn.run_sql(
    """
    SELECT 
        table_schema,
        table_name,
        column_name,
        data_type
    FROM information_schema.columns
    WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
    ORDER BY table_name, ordinal_position
    """
)

# Generate and execute training plan
plan = vn.get_training_plan_generic(df_information_schema)
vn.train(plan=plan)

print("Schema training complete")
```

### 3.3 Incremental Training from Multiple Sources

```python
import os
import glob

# Train from DDL files
for ddl_file in glob.glob('schemas/*.sql'):
    with open(ddl_file, 'r') as f:
        ddl_content = f.read()
        vn.train(ddl=ddl_content)

# Train from documentation files
for doc_file in glob.glob('docs/*.md'):
    with open(doc_file, 'r') as f:
        doc_content = f.read()
        vn.train(documentation=doc_content)

# Train from example queries
for sql_file in glob.glob('examples/*.sql'):
    with open(sql_file, 'r') as f:
        sql_content = f.read()
        vn.train(sql=sql_content)

print("Incremental training complete")
```

### 3.4 Training with Question-SQL Pairs

```python
# High-quality training data: question + SQL pairs
training_pairs = [
    (
        "How many customers registered each month?",
        """
        SELECT 
            DATE_TRUNC('month', registration_date) as month,
            COUNT(*) as customer_count
        FROM customers
        GROUP BY DATE_TRUNC('month', registration_date)
        ORDER BY month DESC
        """
    ),
    (
        "What is the average order value by country?",
        """
        SELECT 
            c.country,
            AVG(o.total_amount) as avg_order_value
        FROM orders o
        INNER JOIN customers c ON o.customer_id = c.customer_id
        GROUP BY c.country
        ORDER BY avg_order_value DESC
        """
    ),
    (
        "Find top 5 countries by revenue",
        """
        SELECT 
            c.country,
            SUM(o.total_amount) as revenue
        FROM orders o
        INNER JOIN customers c ON o.customer_id = c.customer_id
        WHERE o.status = 'delivered'
        GROUP BY c.country
        ORDER BY revenue DESC
        LIMIT 5
        """
    )
]

for question, sql in training_pairs:
    vn.add_question_sql(question=question, sql=sql)

print(f"Added {len(training_pairs)} question-SQL training pairs")
```

---

## 4. QUERY & EXECUTION PATTERNS

### 4.1 Basic Query with Error Handling

```python
def ask_safe(question: str, max_retries: int = 3) -> dict:
    """Safely ask a question with retry logic."""
    for attempt in range(max_retries):
        try:
            result = vn.ask(question)
            if result.get('sql'):
                return result
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt == max_retries - 1:
                return {'error': 'Failed to generate valid query after retries'}
    
    return {'error': 'Unknown error'}

# Usage
result = ask_safe("What was last month's revenue?")
if 'error' not in result:
    print(result['df'])
```

### 4.2 Generate and Validate SQL Separately

```python
def validate_sql(sql: str, expected_keywords: list) -> bool:
    """Validate generated SQL contains expected keywords."""
    sql_upper = sql.upper()
    return all(keyword.upper() in sql_upper for keyword in expected_keywords)

# Generate SQL
question = "Show me today's orders"
sql = vn.generate_sql(question)

# Validate
if validate_sql(sql, ['SELECT', 'FROM', 'orders']):
    print("SQL is valid, executing...")
    result = vn.run_sql(sql)
    print(result)
else:
    print("Generated SQL doesn't look right")
    print(f"SQL: {sql}")
```

### 4.3 Complex Multi-Step Query

```python
# Step 1: Generate SQL
question = "Compare Q3 and Q4 revenue by region"
sql = vn.generate_sql(question)

# Step 2: Execute
df_results = vn.run_sql(sql)

# Step 3: Explain results
explanation = vn.generate_explanation(
    sql=sql,
    question=question
)

# Step 4: Generate visualization
plotly_code = vn.generate_plotly_code(
    question=question,
    sql=sql,
    df=df_results
)

# Step 5: Create figure
figure = vn.get_plotly_figure(
    plotly_code=plotly_code,
    df=df_results
)

# Step 6: Suggest follow-ups
followup_questions = vn.generate_followup_questions(
    question=question,
    sql=sql,
    df=df_results
)

print("Results:")
print(df_results)
print("\nExplanation:", explanation)
print("\nFollow-up questions:")
for q in followup_questions:
    print(f"  - {q}")
```

### 4.4 Batch Query Processing

```python
def process_questions_batch(questions: list) -> list:
    """Process multiple questions and collect results."""
    results = []
    for i, question in enumerate(questions, 1):
        print(f"Processing {i}/{len(questions)}: {question}")
        try:
            result = vn.ask(question)
            results.append({
                'question': question,
                'sql': result.get('sql'),
                'row_count': len(result.get('df', [])),
                'status': 'success'
            })
        except Exception as e:
            results.append({
                'question': question,
                'error': str(e),
                'status': 'failed'
            })
    return results

# Usage
questions = [
    "Total revenue by month",
    "Top 10 customers",
    "Average order value by product"
]
batch_results = process_questions_batch(questions)
```

---

## 5. PRODUCTION DEPLOYMENT

### 5.1 FastAPI Application

```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Data Query API")

class QueryRequest(BaseModel):
    question: str
    visualize: bool = False

class QueryResponse(BaseModel):
    question: str
    sql: str
    result: dict
    explanation: str

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """Execute a natural language query."""
    try:
        logger.info(f"Processing query: {request.question}")
        
        result = vn.ask(
            question=request.question,
            visualize=request.visualize
        )
        
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return QueryResponse(
            question=request.question,
            sql=result['sql'],
            result=result['df'].to_dict() if result.get('df') is not None else {},
            explanation=result.get('explanation', '')
        )
    
    except Exception as e:
        logger.error(f"Query failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

# Run: uvicorn main:app --host 0.0.0.0 --port 8000
```

### 5.2 Streamlit Dashboard

```python
import streamlit as st
import pandas as pd
from vanna.remote import VannaDefault

st.set_page_config(
    page_title="Data Chat",
    page_icon="📊",
    layout="wide"
)

@st.cache_resource
def setup_vanna():
    """Initialize Vanna agent."""
    vn = VannaDefault(
        model=st.secrets["vanna"]["model_name"],
        api_key=st.secrets["vanna"]["api_key"]
    )
    vn.connect_to_postgres(
        host=st.secrets["database"]["host"],
        dbname=st.secrets["database"]["dbname"],
        user=st.secrets["database"]["user"],
        password=st.secrets["database"]["password"],
        port=st.secrets["database"]["port"]
    )
    return vn

vn = setup_vanna()

st.title("📊 Data Intelligence Assistant")

col1, col2 = st.columns([3, 1])

with col1:
    question = st.text_input(
        "Ask a question about your data:",
        placeholder="e.g., What were our sales last quarter?"
    )

with col2:
    visualize = st.checkbox("Create chart", value=True)

if question:
    with st.spinner("🤔 Thinking..."):
        result = vn.ask(question, visualize=visualize)
    
    st.subheader("Generated SQL")
    st.code(result.get('sql', ''), language='sql')
    
    st.subheader("Results")
    if result.get('df') is not None:
        st.dataframe(result['df'], use_container_width=True)
    
    if result.get('figure'):
        st.subheader("Visualization")
        st.plotly_chart(result['figure'], use_container_width=True)
    
    if result.get('explanation'):
        st.subheader("Explanation")
        st.info(result['explanation'])
    
    if result.get('followup_questions'):
        st.subheader("🔄 You might also ask:")
        for q in result['followup_questions'][:5]:
            st.write(f"• {q}")
```

### 5.3 Docker Deployment

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Expose port
EXPOSE ${PORT}

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:${PORT}/health')"

# Run application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "${PORT}"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  vanna-app:
    build: .
    ports:
      - "8000:8000"
    environment:
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      VANNA_API_KEY: ${VANNA_API_KEY}
      DB_HOST: postgres
      DB_NAME: ${DB_NAME}
      DB_USER: ${DB_USER}
      DB_PASSWORD: ${DB_PASSWORD}
    depends_on:
      - postgres

volumes:
  postgres_data:
```

---

## 6. ADVANCED PATTERNS

### 6.1 Custom Tool Implementation

```python
from vanna.core.tool import Tool, ToolContext, ToolResult
from vanna.components import UiComponent, SimpleTextComponent
from pydantic import BaseModel, Field
from typing import Type
import requests

class SendAlertArgs(BaseModel):
    metric_name: str = Field(description="Name of the metric")
    threshold: float = Field(description="Alert threshold")
    actual_value: float = Field(description="Actual value")

class SendAlertTool(Tool[SendAlertArgs]):
    @property
    def name(self) -> str:
        return "send_metric_alert"
    
    @property
    def description(self) -> str:
        return "Send alert notification when metric exceeds threshold"
    
    @property
    def access_groups(self) -> list[str]:
        return ['admin', 'data_team']
    
    def get_args_schema(self) -> Type[SendAlertArgs]:
        return SendAlertArgs
    
    async def execute(self, context: ToolContext, args: SendAlertArgs) -> ToolResult:
        # Send to monitoring system
        message = f"Alert: {args.metric_name} = {args.actual_value} (threshold: {args.threshold})"
        
        response = requests.post(
            "https://alerts.internal.com/api/alerts",
            json={"message": message, "severity": "high"},
            headers={"Authorization": f"Bearer {context.user.metadata.get('alert_token')}"}
        )
        
        return ToolResult(
            success=response.status_code == 200,
            result_for_llm=f"Alert sent successfully",
            ui_component=UiComponent(
                simple_component=SimpleTextComponent(text=message)
            )
        )
```

### 6.2 Conversation Memory Management

```python
from collections import deque
from datetime import datetime, timedelta

class ConversationManager:
    def __init__(self, max_history: int = 10, max_age_hours: int = 24):
        self.conversation_history = deque(maxlen=max_history)
        self.max_age = timedelta(hours=max_age_hours)
    
    def add_interaction(self, question: str, sql: str, result_summary: str):
        """Add to conversation history."""
        self.conversation_history.append({
            'timestamp': datetime.now(),
            'question': question,
            'sql': sql,
            'result_summary': result_summary
        })
    
    def get_context(self) -> str:
        """Get conversation context for LLM."""
        context_lines = []
        for item in self.conversation_history:
            context_lines.append(f"Q: {item['question']}")
            context_lines.append(f"A: {item['result_summary']}")
        return "\n".join(context_lines)
    
    def clear_old_interactions(self):
        """Remove interactions older than max_age."""
        cutoff_time = datetime.now() - self.max_age
        while (self.conversation_history and 
               self.conversation_history[0]['timestamp'] < cutoff_time):
            self.conversation_history.popleft()

# Usage
manager = ConversationManager(max_history=20)

for question in ["Total revenue?", "By region?", "Year-over-year?"]:
    result = vn.ask(question)
    manager.add_interaction(
        question=question,
        sql=result['sql'],
        result_summary=result['df'].to_string()
    )
```

### 6.3 Rate Limiting & Quota Management

```python
from datetime import datetime, timedelta
import json

class QuotaManager:
    def __init__(self, daily_limit: int = 100):
        self.daily_limit = daily_limit
        self.user_stats = {}
    
    def check_quota(self, user_id: str) -> bool:
        """Check if user has remaining quota."""
        today = datetime.now().date()
        
        if user_id not in self.user_stats:
            self.user_stats[user_id] = {'date': today, 'count': 0}
        
        stats = self.user_stats[user_id]
        
        # Reset if new day
        if stats['date'] != today:
            stats['date'] = today
            stats['count'] = 0
        
        return stats['count'] < self.daily_limit
    
    def record_query(self, user_id: str):
        """Record query execution."""
        if user_id in self.user_stats:
            self.user_stats[user_id]['count'] += 1
    
    def get_remaining(self, user_id: str) -> int:
        """Get remaining queries for user."""
        if user_id not in self.user_stats:
            return self.daily_limit
        return self.daily_limit - self.user_stats[user_id]['count']

# Usage
quota = QuotaManager(daily_limit=50)

def ask_with_quota(user_id: str, question: str) -> dict:
    if not quota.check_quota(user_id):
        return {'error': 'Daily quota exceeded'}
    
    result = vn.ask(question)
    quota.record_query(user_id)
    
    return {
        **result,
        'remaining_quota': quota.get_remaining(user_id)
    }
```

---

## TESTING EXAMPLES

### Unit Test

```python
import pytest
from unittest.mock import Mock, patch

def test_sql_generation():
    """Test SQL generation."""
    question = "Total revenue?"
    sql = vn.generate_sql(question)
    
    assert sql is not None
    assert "SELECT" in sql.upper()
    assert len(sql) > 10

def test_database_connection():
    """Test database connectivity."""
    try:
        result = vn.run_sql("SELECT 1")
        assert len(result) > 0
    except Exception as e:
        pytest.fail(f"Database connection failed: {e}")

@patch('vanna.ask')
def test_ask_with_mock(mock_ask):
    """Test ask() with mocked response."""
    mock_ask.return_value = {
        'sql': 'SELECT * FROM users',
        'df': Mock()
    }
    
    result = vn.ask("Users?")
    assert result['sql'] == 'SELECT * FROM users'
```

---

*This guide provides production-ready code examples. Always test thoroughly before deployment.*
