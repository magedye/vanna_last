import os
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Vanna Imports
from vanna import Agent
from vanna.core.user import UserResolver, User, RequestContext
from vanna.core.registry import ToolRegistry
from vanna.core.tool import ToolContext   # <-- الإصلاح
from vanna.servers.fastapi import VannaFastAPIServer

# Integrations
from vanna.integrations.google import GeminiLlmService
from vanna.integrations.chromadb import ChromaAgentMemory

# Tools
from vanna.tools import RunSqlTool, VisualizeDataTool
from vanna.tools.agent_memory import (
    SaveQuestionToolArgsTool,
    SearchSavedCorrectToolUsesTool,
    SaveTextMemoryTool
)

# Custom
try:
    from db_connect.factory import get_db_runner  # Preferred package path
except ImportError:
    from factory import get_db_runner  # Local fallback for monorepo layout
from custom_tools import TrainRagTool, TrainRagArgs
from security.guardrails import validate_user_input


# ---------------------------------------
# 1. Load Configuration
# ---------------------------------------
load_dotenv()

ENV = os.getenv("ENV", "DEV")
DB_TYPE = os.getenv("DB_TYPE", "sqlite").lower()
API_KEY = os.getenv("GOOGLE_API_KEY")

DB_PATH = os.getenv("VANNA_DATABASE_PATH", "./mydb.db")
CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "vanna_memory")

MODEL = "gemini-2.5-flash"


# ---------------------------------------
# 2. Configure LLM
# ---------------------------------------
llm = GeminiLlmService(
    model=MODEL,
    api_key=API_KEY
)


# ---------------------------------------
# 3. Configure Database Runner
# ---------------------------------------
# Keep SQLite-first defaults while allowing DB_TYPE override
os.environ.setdefault("DB_TYPE", DB_TYPE)
os.environ.setdefault("SQLITE_DB_PATH", DB_PATH)

sql_runner = get_db_runner()
db_tool = RunSqlTool(sql_runner=sql_runner)
training_tool = TrainRagTool(sql_runner, db_type=DB_TYPE)


# ---------------------------------------
# 4. Configure Memory
# ---------------------------------------
os.makedirs(CHROMA_PATH, exist_ok=True)
agent_memory = ChromaAgentMemory(
    collection_name=COLLECTION_NAME,
    persist_directory=CHROMA_PATH
)


# ---------------------------------------
# 5. User Resolver
# ---------------------------------------
class SimpleUserResolver(UserResolver):
    async def resolve_user(self, request_context: RequestContext) -> User:
        email = request_context.get_cookie("vanna_email") or "guest@example.com"
        group = "admin" if email == "admin@example.com" else "user"
        return User(id=email, email=email, group_memberships=[group])


user_resolver = SimpleUserResolver()


# ---------------------------------------
# 6. Tools Registry
# ---------------------------------------
tools = ToolRegistry()

# Normal Tools
tools.register_local_tool(db_tool, access_groups=["admin", "user"])
tools.register_local_tool(VisualizeDataTool(), access_groups=["admin", "user"])
tools.register_local_tool(SearchSavedCorrectToolUsesTool(), access_groups=["admin", "user"])

# Admin Tools
tools.register_local_tool(SaveTextMemoryTool(), access_groups=["admin"])
tools.register_local_tool(SaveQuestionToolArgsTool(), access_groups=["admin"])
tools.register_local_tool(training_tool, access_groups=["admin"])


# ---------------------------------------
# 7. Agent Assembly
# ---------------------------------------
agent = Agent(
    tool_registry=tools,
    llm_service=llm,
    user_resolver=user_resolver,
    agent_memory=agent_memory
)


# ---------------------------------------
# 8. FastAPI Server Assembly
# ---------------------------------------
server = VannaFastAPIServer(agent)
app = server.create_app()


# ---------------------------------------
# 9. Security Middleware
# ---------------------------------------
@app.middleware("http")
async def guardrail_middleware(request: Request, call_next):

    if "/chat" in request.url.path and request.method == "POST":
        try:
            body = await request.json()
            message = body.get("message", "")
            validate_user_input(message)
        except Exception as e:
            return JSONResponse(status_code=400, content={"error": str(e)})

    return await call_next(request)


# ---------------------------------------
# 10. CORS (Correct Secure Version)
# ---------------------------------------
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,    # لا تستخدم "*" مع allow_credentials
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------
# 11. Custom Admin API (Train Button)
# ---------------------------------------
@app.post("/api/custom/train")
async def api_train_manual():

    admin_user = User(id="api_admin", email="admin@example.com", group_memberships=["admin"])
    tool_ctx = ToolContext(agent=agent, user=admin_user)

    result = training_tool.execute(tool_ctx, TrainRagArgs(limit=10))
    return {"status": "success", "message": result.result_for_llm}


# ---------------------------------------
# 12. Main Execution
# ---------------------------------------
if __name__ == "__main__":
    print("🌍 Starting Vanna Enterprise Backend on Port 7262...")
    uvicorn.run(app, host="0.0.0.0", port=7262)
