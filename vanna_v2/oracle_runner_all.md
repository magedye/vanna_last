ممتاز، هذا هو التحدي الحقيقي والخطوة الكبرى نحو بيئة الإنتاج (Production).

التعامل مع **Oracle Database** يتطلب دقة أعلى في كتابة الكود، لأنها صارمة جداً في التعامل مع أنواع البيانات والصلاحيات، خاصة في البيئة البنكية.

إليك التطبيق العملي الكامل لربط Vanna مع Oracle، مقسماً إلى ملفات نظيفة للحفاظ على معمارية المشروع.

-----

### 1️⃣ الخطوة الأولى: تثبيت المكتبة (Driver)

تأكد من تفعيل البيئة الافتراضية، ثم ثبت مكتبة Oracle الرسمية الحديثة (التي لا تحتاج إلى تثبيتات معقدة في النظام):

```bash
pip install oracledb
```

-----

### 2️⃣ الخطوة الثانية: إنشاء ملف `oracle_runner.py`

بدلاً من حشو الكود في `app.py`، سننشئ ملفاً خاصاً للاتصال بقاعدة البيانات. هذا يجعل الكود أنظف وأسهل في الصيانة.

قم بإنشاء ملف `oracle_runner.py`:

```python
import oracledb
import pandas as pd
from vanna.base import VannaBase

class OracleRunner:
    def __init__(self, user, password, dsn):
        self.user = user
        self.password = password
        self.dsn = dsn

    def run_sql(self, sql: str, context=None) -> pd.DataFrame:
        """
        دالة تنفيذ SQL واسترجاع DataFrame
        """
        try:
            # استخدام النمط Thin (لا يحتاج Oracle Client)
            with oracledb.connect(
                user=self.user, 
                password=self.password, 
                dsn=self.dsn
            ) as connection:
                
                # تنظيف كود SQL (Oracle تكره الفاصلة المنقوطة في نهاية الاستعلام عبر Driver)
                clean_sql = sql.strip().rstrip(';')
                
                # قراءة البيانات مباشرة باستخدام Pandas
                df = pd.read_sql(clean_sql, connection)
                return df
                
        except oracledb.Error as e:
            # رفع الخطأ كما هو ليتمكن Vanna من رؤيته ومحاولة تصحيحه
            raise e
        except Exception as e:
            raise e
```

-----

### 3️⃣ الخطوة الثالثة: تحديث أداة التدريب (`custom_tools.py`) لتناسب Oracle

أداة التدريب التي كتبناها سابقاً كانت تعتمد على `sqlite_master`. في Oracle، الوضع مختلف تماماً. سنستخدم حزمة `DBMS_METADATA` لاستخراج هيكل الجداول.

قم بتحديث ملف `custom_tools.py` بهذا الكود المخصص لـ Oracle:

```python
import oracledb
import pandas as pd
from vanna.core.tool import Tool, ToolContext, ToolResult
from pydantic import BaseModel, Field

# إعدادات المدخلات
class TrainRagArgs(BaseModel):
    limit: int = Field(default=5, description="عدد الصفوف كعينة (يفضل عدد قليل في Oracle)")

# الأداة
class TrainRagTool(Tool[TrainRagArgs]):
    def __init__(self, user, password, dsn):
        self.user = user
        self.password = password
        self.dsn = dsn

    @property
    def name(self):
        return "train_oracle_rag"

    @property
    def description(self):
        return "سحب هيكل جداول Oracle (DDL) وعينات بيانات لتحديث الذاكرة."

    @property
    def access_groups(self):
        return ["admin"]

    def get_args_schema(self):
        return TrainRagArgs

    def execute(self, context: ToolContext, args: TrainRagArgs) -> ToolResult:
        try:
            conn = oracledb.connect(user=self.user, password=self.password, dsn=self.dsn)
            cursor = conn.cursor()
            memory = context.agent.agent_memory
            
            # 1. استخراج قائمة الجداول (للمستخدم الحالي فقط)
            # نستخدم USER_TABLES بدلاً من ALL_TABLES للأمان والسرعة
            cursor.execute("SELECT table_name FROM USER_TABLES")
            tables = [row[0] for row in cursor.fetchall()]
            
            if not tables:
                return ToolResult(success=False, result_for_llm="لم يتم العثور على جداول لهذا المستخدم.")

            # 2. استخراج الـ DDL (هيكل الجداول)
            # Oracle توفر دالة جاهزة لتعطيك كود CREATE TABLE كاملاً
            ddl_statements = []
            for table in tables:
                try:
                    # إعداد الخيارات لناتج نظيف
                    cursor.execute("BEGIN DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM,'STORAGE',false); END;")
                    
                    cursor.execute(f"SELECT DBMS_METADATA.GET_DDL('TABLE', '{table}') FROM DUAL")
                    clob_ddl = cursor.fetchone()[0]
                    ddl_str = str(clob_ddl) # تحويل من LOB إلى نص
                    ddl_statements.append(ddl_str)
                except Exception as e:
                    print(f"⚠️ تخطي DDL للجدول {table}: {e}")

            # تخزين الـ DDL دفعة واحدة
            if ddl_statements:
                full_ddl = "\n".join(ddl_statements)
                if hasattr(memory, 'add_ddl'):
                    memory.add_ddl(full_ddl)
                else:
                    memory.add_documentation(full_ddl)

            # 3. استخراج عينات البيانات (Samples)
            trained_tables = []
            for table in tables:
                try:
                    # جملة Oracle لجلب عدد محدد من الصفوف
                    query = f'SELECT * FROM "{table}" FETCH NEXT {args.limit} ROWS ONLY'
                    df = pd.read_sql(query, conn)
                    
                    if not df.empty:
                        csv_data = df.to_csv(index=False)
                        memory.add_documentation(csv_data)
                        trained_tables.append(table)
                except Exception as e:
                    print(f"⚠️ تخطي بيانات الجدول {table}: {e}")

            conn.close()

            return ToolResult(
                success=True,
                result_for_llm=f"تم تدريب Oracle بنجاح على الجداول: {', '.join(trained_tables)}",
                ui_component=None
            )

        except Exception as e:
            return ToolResult(success=False, result_for_llm=f"خطأ Oracle: {str(e)}")
```

-----

### 4️⃣ الخطوة الرابعة: تحديث `app.py` لربط كل شيء

الآن نربط الـ Runner الجديد والأداة الجديدة في ملف التشغيل الرئيسي.

قم بتحديث `app.py`:

```python
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request

# استيراد مكونات Vanna
from vanna import Agent
from vanna.core.registry import ToolRegistry
from vanna.core.user import UserResolver, User, RequestContext
from vanna.tools import RunSqlTool, VisualizeDataTool
from vanna.servers.fastapi import VannaFastAPIServer
from vanna.integrations.google import GeminiLlmService
from vanna.integrations.chromadb import ChromaAgentMemory

# استيراد ملفاتنا الجديدة الخاصة بـ Oracle
from oracle_runner import OracleRunner
from custom_tools import TrainRagTool, TrainRagArgs

# 1. الإعدادات
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL = os.getenv("VANNA_LLM_MODEL", "gemini-2.5-flash")

# إعدادات Oracle من ملف .env
ORACLE_USER = os.getenv("ORACLE_USER")
ORACLE_PASS = os.getenv("ORACLE_PASS")
ORACLE_DSN = os.getenv("ORACLE_DSN")  # مثال: localhost:1521/XEPDB1

# 2. المكونات الأساسية
llm = GeminiLlmService(model=MODEL, api_key=API_KEY)

# استخدام OracleRunner بدلاً من SqliteRunner
oracle_runner = OracleRunner(user=ORACLE_USER, password=ORACLE_PASS, dsn=ORACLE_DSN)
db_tool = RunSqlTool(sql_runner=oracle_runner)

agent_memory = ChromaAgentMemory(collection_name="vanna_memory_oracle", persist_directory="./chroma_db_oracle")

# 3. المستخدمين
class SimpleUserResolver(UserResolver):
    async def resolve_user(self, request_context: RequestContext) -> User:
        user_email = request_context.get_cookie('vanna_email') or 'guest@example.com'
        group = 'admin' if user_email == 'admin@example.com' else 'user'
        return User(id=user_email, email=user_email, group_memberships=[group])
user_resolver = SimpleUserResolver()

# 4. تسجيل الأدوات
tools = ToolRegistry()
tools.register_local_tool(db_tool, access_groups=['admin', 'user'])
tools.register_local_tool(VisualizeDataTool(), access_groups=['admin', 'user'])

# تسجيل أداة تدريب Oracle
training_tool = TrainRagTool(user=ORACLE_USER, password=ORACLE_PASS, dsn=ORACLE_DSN)
tools.register_local_tool(training_tool, access_groups=['admin'])

# 5. الوكيل
agent = Agent(
    llm_service=llm,
    tool_registry=tools,
    user_resolver=user_resolver,
    agent_memory=agent_memory
)

# 6. السيرفر
if __name__ == "__main__":
    server = VannaFastAPIServer(agent)
    
    # API لزر التدريب
    @server.app.post("/api/custom/train")
    async def run_training_manually(request: Request):
        result = training_tool.execute(
             ToolContext(agent=agent, user=User(id="api", email="api", group_memberships=["admin"])),
             TrainRagArgs(limit=5)
        )
        return {"status": "completed", "details": result.result_for_llm}

    print(f"🚀 Starting Vanna Server (Oracle Mode) on port 7262...")
    server.run(host="0.0.0.0", port=7262)
```

-----

### 5️⃣ الخطوة الخامسة: تحديث ملف `.env`

لا تنسَ إضافة بيانات اتصال Oracle في ملف البيئة:

```bash
GOOGLE_API_KEY="مفتاحك_هنا"
VANNA_LLM_MODEL="gemini-2.5-flash"

# إعدادات Oracle
ORACLE_USER="HR"         # اسم المستخدم (تأكد أن لديه صلاحية SELECT)
ORACLE_PASS="oracle_password"
ORACLE_DSN="192.168.1.50:1521/orclpdb"  # عنوان السيرفر والخدمة
```

### 💡 نصيحة بنكية هامة (Best Practice)

في البنوك، لا نستخدم المستخدم `SYSTEM` أو `SYS` للاتصال.

  * **أنشئ مستخدم خاص للذكاء الاصطناعي** (مثلاً: `AI_READER`).
  * امنحه صلاحية `CREATE SESSION`.
  * امنحه صلاحية `SELECT` **فقط** على الجداول (Views) التي تريد تحليلها.
  * بالنسبة لأداة التدريب، ستحتاج لمنحه صلاحية `SELECT_CATALOG_ROLE` بشكل مؤقت أو صلاحية استخدام `DBMS_METADATA` لقراءة الهيكل.

