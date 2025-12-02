# Vanna 2.0: Quick Reference Card

## INSTALLATION

```bash
# Basic
pip install vanna

# With specific database support
pip install 'vanna[postgres]'  # PostgreSQL
pip install 'vanna[mysql]'     # MySQL
pip install 'vanna[mssql]'     # SQL Server
pip install 'vanna[bigquery]'  # BigQuery
pip install 'vanna[all-databases]'  # All

# With specific vector store
pip install 'vanna[qdrant]'     # Qdrant
pip install 'vanna[milvus]'     # Milvus
```

---

## CORE INITIALIZATION

### Minimal Setup
```python
from vanna.remote import VannaDefault

vn = VannaDefault(
    model='your_model_name',
    api_key='your-api-key'
)
vn.connect_to_postgres(
    host='localhost', dbname='mydb', user='user', password='pass'
)
result = vn.ask("What is the total revenue?")
```

### Full Setup with Custom Config
```python
from vanna import Agent, AgentConfig
from vanna.integrations.anthropic import AnthropicLlmService
from vanna.core.registry import ToolRegistry
from vanna.core.user import UserResolver, User, RequestContext

llm = AnthropicLlmService(model='claude-3', api_key='key')
tools = ToolRegistry()

class MyResolver(UserResolver):
    async def resolve_user(self, ctx):
        return User(id='user1', username='dev')

config = AgentConfig(
    max_tool_iterations=10,
    stream_responses=True,
    temperature=0.7
)

agent = Agent(
    llm_service=llm,
    tool_registry=tools,
    user_resolver=MyResolver(),
    config=config
)
```

---

## DATABASE CONNECTIONS

| Database | Method | Example |
|----------|--------|---------|
| **PostgreSQL** | `vn.connect_to_postgres()` | `vn.connect_to_postgres(host='localhost', dbname='db', user='user', password='pass', port=5432)` |
| **MySQL** | `vn.connect_to_mysql()` | `vn.connect_to_mysql(host='localhost', user='root', password='pass', dbname='db', port=3306)` |
| **SQL Server** | `vn.connect_to_mssql()` | `vn.connect_to_mssql(odbc_conn_str='Driver={...};Server=...;')` |
| **BigQuery** | `vn.connect_to_bigquery()` | `vn.connect_to_bigquery(project_id='proj', cred_file_path='creds.json')` |
| **Snowflake** | `vn.connect_to_snowflake()` | `vn.connect_to_snowflake(account='xy', user='u', password='p', warehouse='WH', database='DB', schema='SCHEMA')` |
| **SQLite** | `vn.connect_to_sqlite()` | `vn.connect_to_sqlite('database.db')` |
| **DuckDB** | `vn.connect_to_duckdb()` | `vn.connect_to_duckdb(':memory:')` |
| **Oracle** | `vn.connect_to_oracle()` | `vn.connect_to_oracle(user='u', password='p', dsn='host:port/sid')` |

---

## TRAINING METHODS

### Method 1: DDL (Database Schema)
```python
vn.train(ddl="""
    CREATE TABLE users (
        id INT PRIMARY KEY,
        name VARCHAR(100),
        email VARCHAR(100)
    )
""")
```

### Method 2: Documentation (Business Context)
```python
vn.train(documentation="""
    - Users table stores customer profiles
    - Email field is unique and required
    - Premium users have 'PREMIUM' prefix
""")
```

### Method 3: SQL Examples (Query Pairs)
```python
vn.train(sql="""
    SELECT user_id, COUNT(*) as orders
    FROM orders
    GROUP BY user_id
    ORDER BY orders DESC
    /* This shows top customers by order count */
""")

# Or with question
vn.add_question_sql(
    question="Top 10 customers?",
    sql="SELECT ... LIMIT 10"
)
```

### Method 4: Automatic Schema
```python
df_schema = vn.run_sql("SELECT * FROM INFORMATION_SCHEMA.COLUMNS")
plan = vn.get_training_plan_generic(df_schema)
vn.train(plan=plan)
```

---

## QUERY METHODS

### Single Method: ask()
```python
result = vn.ask("What is total revenue?")
# Returns: {
#   'sql': '...',
#   'df': DataFrame,
#   'figure': PlotlyFigure,
#   'explanation': '...',
#   'followup_questions': [...]
# }
```

### Multi-Step Approach
```python
sql = vn.generate_sql("Total revenue?")
df = vn.run_sql(sql)
explanation = vn.generate_explanation(sql=sql)
plotly_code = vn.generate_plotly_code(sql=sql, df=df)
figure = vn.get_plotly_figure(plotly_code=plotly_code, df=df)
followups = vn.generate_followup_questions(sql=sql, df=df)
```

---

## TRAINING DATA MANAGEMENT

```python
# Get all training data
all_training = vn.get_training_data()

# Get related data for a question
related_ddl = vn.get_related_ddl(question="...")
related_docs = vn.get_related_documentation(question="...")
similar_sql = vn.get_similar_question_sql(question="...")

# Remove training data
vn.remove_training_data(id='training_id')
```

---

## VECTOR STORES

| Vector Store | Installation | LLM Combination |
|--------------|--------------|-----------------|
| **ChromaDB** | `pip install vanna` | Any LLM |
| **Qdrant** | `pip install 'vanna[qdrant]'` | CloudAuthenticatedLLM |
| **Milvus** | `pip install 'vanna[milvus]'` | Any LLM |
| **Pinecone** | `pip install 'vanna[pinecone]'` | Any LLM |

### Example: Qdrant
```python
from vanna.qdrant import Qdrant_VectorStore
from vanna.openai import OpenAI_Chat
from qdrant_client import QdrantClient

class MyVanna(Qdrant_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        Qdrant_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

client = QdrantClient(":memory:")
vn = MyVanna(config={'client': client, 'api_key': 'sk-...'})
```

---

## LLM PROVIDERS

| LLM | Import | Setup |
|-----|--------|-------|
| **OpenAI** | `from vanna.openai import OpenAI_Chat` | `vn.set_api_key('sk-...')` |
| **Anthropic** | `from vanna.integrations.anthropic import AnthropicLlmService` | `AnthropicLlmService(api_key='...')` |
| **Google Gemini** | `from vanna.integrations.google import GoogleLlmService` | `GoogleLlmService(api_key='...')` |
| **Ollama** | `from vanna.ollama import Ollama` | `Ollama(config={'model': 'llama2'})` |
| **Mistral** | `from vanna.integrations.mistral import MistralLlmService` | `MistralLlmService(api_key='...')` |

---

## AUTHENTICATION PATTERNS

### JWT Authentication
```python
class JwtResolver(UserResolver):
    async def resolve_user(self, request_context: RequestContext) -> User:
        token = request_context.get_header('Authorization').split(' ')[1]
        claims = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return User(
            id=claims['user_id'],
            username=claims['username'],
            group_memberships=claims['groups']
        )
```

### Session Cookie
```python
class SessionResolver(UserResolver):
    async def resolve_user(self, request_context: RequestContext) -> User:
        session_id = request_context.get_cookie('session_id')
        user = await session_store.get_user(session_id)
        return User(id=user['id'], username=user['name'])
```

---

## DEPLOYMENT OPTIONS

### FastAPI
```python
from vanna.servers.fastapi import VannaFastAPIServer

server = VannaFastAPIServer(agent)
app = server.create_app()
# Run: uvicorn main:app --host 0.0.0.0 --port 8000
```

### Streamlit
```python
import streamlit as st

@st.cache_resource
def setup():
    vn = VannaDefault(...)
    vn.connect_to_postgres(...)
    return vn

vn = setup()
question = st.text_input("Ask a question:")
result = vn.ask(question)
st.dataframe(result['df'])
```

### Docker
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

---

## CUSTOM TOOLS

```python
from vanna.core.tool import Tool, ToolContext, ToolResult
from pydantic import BaseModel, Field

class MyArgs(BaseModel):
    param: str = Field(description="Parameter")

class MyTool(Tool[MyArgs]):
    @property
    def name(self) -> str:
        return "my_tool"
    
    @property
    def description(self) -> str:
        return "Tool description"
    
    @property
    def access_groups(self) -> list[str]:
        return ['admin']  # Access control
    
    def get_args_schema(self):
        return MyArgs
    
    async def execute(self, context: ToolContext, args: MyArgs) -> ToolResult:
        # Implement logic
        return ToolResult(
            success=True,
            result_for_llm="Result for LLM",
            ui_component=UiComponent(...)
        )

tool_registry.register(MyTool())
```

---

## COMMON CONFIGURATIONS

### Production Setup
```python
config = AgentConfig(
    max_tool_iterations=5,
    stream_responses=True,
    temperature=0.3,  # Lower = more deterministic
    auto_save_conversations=True,
    include_thinking_indicators=True
)
```

### Development Setup
```python
config = AgentConfig(
    max_tool_iterations=10,
    stream_responses=False,
    temperature=0.7,  # Higher = more creative
    auto_save_conversations=False
)
```

---

## ERROR HANDLING

```python
import logging

logging.basicConfig(level=logging.DEBUG)

try:
    result = vn.ask("Question?")
    if not result or 'error' in result:
        print("Query failed:", result.get('error'))
except Exception as e:
    print(f"Error: {e}")
    # Log and retry logic
```

---

## SECURITY BEST PRACTICES

✅ DO:
- Use environment variables for credentials
- Validate user input before processing
- Implement rate limiting per user
- Use HTTPS in production
- Set `allow_llm_to_see_data=False` for sensitive data
- Keep API keys and passwords secret
- Implement audit logging

❌ DON'T:
- Hardcode credentials in code
- Trust untrusted user input
- Run without authentication
- Expose database connection strings
- Deploy without HTTPS
- Skip input validation

---

## TROUBLESHOOTING

| Issue | Solution |
|-------|----------|
| "Generated SQL is incorrect" | Add more training data (DDL, docs, examples) |
| "Connection refused" | Check database service is running, verify credentials |
| "LLM timeout" | Implement retry with exponential backoff |
| "Memory usage high" | Use cloud vector store or implement pagination |
| "Generated answers instead of SQL" | Reset conversation, provide context limits |

---

## KEY METRICS

- **Training Data**: DDL statements + Documentation + Example SQL pairs
- **Query Accuracy**: Depends on quality of training data
- **Response Time**: Typically 1-5 seconds for SQL generation
- **Vector Store Size**: ~100KB per DDL statement average

---

## USEFUL LINKS

- **Documentation**: https://vanna.ai/docs
- **GitHub**: https://github.com/vanna-ai/vanna
- **Issues**: https://github.com/vanna-ai/vanna/issues
- **Discussions**: https://github.com/vanna-ai/vanna/discussions

---

*Vanna 2.0 Quick Reference | Updated November 2025*
