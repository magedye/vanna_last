# app_mvp.py - Wosool AI MVP (Simplified Version)
# النسخة المبسطة - جاهزة للتطوير الفوري

import os
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import hashlib

# Core imports
import chainlit as cl
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage
from sqlalchemy import create_engine, text, inspect
import pandas as pd
import redis

# ═══════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Config:
    # LLM
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
    LLM_MODEL = os.getenv('LLM_MODEL') or os.getenv('GROQ_MODEL', 'llama3-70b-8192')
    
    # Database
    DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'oracle').lower()
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', '1521'))
    DB_USER = os.getenv('DB_USER', '')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', '')
    
    # Redis
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))

# ═══════════════════════════════════════════════════════════
# Database Connection
# ═══════════════════════════════════════════════════════════

def get_db_connection_string():
    """Generate database connection string"""
    db_type = Config.DATABASE_TYPE
    
    if db_type == 'oracle':
        return f"oracle+oracledb://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}"
    elif db_type == 'postgres':
        return f"postgresql://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}"
    elif db_type == 'mssql':
        return f"mssql+pyodbc://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}?driver=ODBC+Driver+17+for+SQL+Server"
    else:
        return f"sqlite:///{Config.DB_NAME}"

try:
    engine = create_engine(get_db_connection_string(), echo=False)
    logger.info(f"✅ Database connected: {Config.DATABASE_TYPE}")
except Exception as e:
    logger.error(f"❌ Database error: {e}")
    engine = None

# ═══════════════════════════════════════════════════════════
# Redis Cache
# ═══════════════════════════════════════════════════════════

try:
    redis_client = redis.Redis(
        host=Config.REDIS_HOST,
        port=Config.REDIS_PORT,
        decode_responses=True,
        socket_connect_timeout=5
    )
    redis_client.ping()
    logger.info("✅ Redis connected")
except:
    redis_client = None
    logger.warning("⚠️ Redis unavailable - caching disabled")

# ═══════════════════════════════════════════════════════════
# LLM Provider
# ═══════════════════════════════════════════════════════════

llm = ChatGroq(
    groq_api_key=Config.GROQ_API_KEY,
    model_name=Config.LLM_MODEL,
    temperature=0.5
)

# ═══════════════════════════════════════════════════════════
# SQL Generation
# ═══════════════════════════════════════════════════════════

def get_database_schema() -> str:
    """Get database schema for context"""
    if not engine:
        return "Database not connected"
    
    try:
        inspector = inspect(engine)
        schema_info = "Database Schema:\n\n"
        
        tables = inspector.get_table_names()[:10]  # Limit to 10 tables
        
        for table_name in tables:
            schema_info += f"Table: {table_name}\n"
            for column in inspector.get_columns(table_name):
                schema_info += f"  - {column['name']}: {column['type']}\n"
            schema_info += "\n"
        
        return schema_info
    except Exception as e:
        return f"Error getting schema: {e}"

def generate_sql(question: str) -> str:
    """Generate SQL from natural language question"""
    
    schema = get_database_schema()
    
    prompt = f"""
You are a SQL expert. Generate ONLY a SQL query (no explanation).
Database type: {Config.DATABASE_TYPE}
Schema information:
{schema}

Question: {question}

Return ONLY the SQL query, nothing else.
"""
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        sql_query = response.content.strip()
        
        # Clean up SQL
        if sql_query.startswith("```sql"):
            sql_query = sql_query[6:]
        if sql_query.startswith("```"):
            sql_query = sql_query[3:]
        if sql_query.endswith("```"):
            sql_query = sql_query[:-3]
        
        sql_query = sql_query.strip()
        logger.info(f"Generated SQL: {sql_query[:100]}")
        
        return sql_query
    except Exception as e:
        logger.error(f"SQL generation error: {e}")
        raise

# ═══════════════════════════════════════════════════════════
# Query Execution
# ═══════════════════════════════════════════════════════════

def execute_query(sql_query: str) -> pd.DataFrame:
    """Execute SQL query safely"""
    
    if not engine:
        raise Exception("Database not connected")
    
    # Security check - prevent dangerous operations
    dangerous_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'GRANT']
    if any(keyword in sql_query.upper() for keyword in dangerous_keywords):
        raise Exception("⛔ Dangerous SQL operation detected!")
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql_query))
            columns = result.keys()
            rows = result.fetchall()
            df = pd.DataFrame(rows, columns=columns)
            logger.info(f"Query executed: {len(df)} rows")
            return df
    except Exception as e:
        logger.error(f"Query execution error: {e}")
        raise

# ═══════════════════════════════════════════════════════════
# Caching
# ═══════════════════════════════════════════════════════════

def get_cached_result(question: str) -> Optional[Dict]:
    """Get cached query result"""
    if not redis_client:
        return None
    
    try:
        key = f"query:{hashlib.md5(question.encode()).hexdigest()}"
        cached = redis_client.get(key)
        if cached:
            logger.info("📦 Cache HIT")
            return json.loads(cached)
    except:
        pass
    return None

def cache_result(question: str, result: Dict):
    """Cache query result"""
    if not redis_client:
        return
    
    try:
        key = f"query:{hashlib.md5(question.encode()).hexdigest()}"
        redis_client.setex(key, 3600, json.dumps(result, default=str))
        logger.info("💾 Result cached")
    except:
        pass

# ═══════════════════════════════════════════════════════════
# Chainlit UI
# ═══════════════════════════════════════════════════════════

@cl.on_chat_start
async def start():
    """Initialize chat"""
    
    await cl.Message(
        content="""
🚀 **مرحباً بك في Wosool AI**

أنا مساعدك الذكي لاستكشاف قاعدة البيانات!

**مثال على أسئلة يمكنك طرحها:**
- "ما أعلى 10 منتجات حسب المبيعات؟"
- "عدد العملاء حسب المدينة"
- "إجمالي المبيعات لهذا الشهر"
- "أكثر 5 موظفين إنتاجية"

**الميزات:**
✅ توليد SQL تلقائي
✅ نتائج فورية
✅ تخزين مؤقت ذكي
✅ أمان عالي

ابدأ بسؤال الآن! 💬
        """,
        author="Wosool AI"
    ).send()

@cl.on_message
async def main(message: cl.Message):
    """Process user message"""
    
    try:
        user_question = message.content
        
        # Show loading
        response_msg = cl.Message(content="", author="Wosool AI")
        
        # Check cache first
        cached = get_cached_result(user_question)
        if cached:
            result = cached
            await response_msg.stream_token("💾 من الذاكرة المؤقتة:\n\n")
        else:
            # Generate SQL
            await response_msg.stream_token("🔄 جاري توليد الاستعلام...\n\n")
            sql_query = generate_sql(user_question)
            
            # Execute query
            await response_msg.stream_token(f"```sql\n{sql_query}\n```\n\n")
            await response_msg.stream_token("⏳ جاري تنفيذ الاستعلام...\n\n")
            
            df = execute_query(sql_query)
            
            # Cache result
            result = {
                'sql': sql_query,
                'data': df.to_dict('records'),
                'rows': len(df),
                'columns': list(df.columns)
            }
            cache_result(user_question, result)
        
        # Format response
        rows_count = result['rows']
        columns = result['columns'][:5]
        
        response_content = f"""
✅ **النتائج:**
- 📊 عدد الصفوف: {rows_count}
- 📋 الأعمدة: {', '.join(columns)}{"..." if len(result['columns']) > 5 else ""}

**البيانات:**
"""
        
        # Add data table
        if result['data']:
            df_display = pd.DataFrame(result['data']).head(10)
            response_content += "\n" + df_display.to_markdown(index=False)
        
        await response_msg.stream_token(response_content)
        
        logger.info(f"✅ Response sent: {rows_count} rows")
    
    except Exception as e:
        error_msg = f"❌ خطأ: {str(e)}"
        logger.error(error_msg)
        await cl.Message(
            content=error_msg,
            author="Wosool AI"
        ).send()

# ═══════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    logger.info("🚀 Starting Wosool AI MVP...")
    cl.run()
