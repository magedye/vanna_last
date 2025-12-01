import os
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# ------------------------------
# Vanna Core Imports
# ------------------------------
from vanna import Agent
from vanna.core.user import UserResolver, User, RequestContext
from vanna.core.registry import ToolRegistry
from vanna.servers.fastapi import VannaFastAPIServer
from vanna.integrations.chromadb import ChromaAgentMemory
from vanna.integrations.google import GeminiLlmService
from vanna.tools import RunSqlTool, VisualizeDataTool
from vanna.tools.agent_memory import (
    SaveQuestionToolArgsTool,
    SearchSavedCorrectToolUsesTool,
    SaveTextMemoryTool
)

# ------------------------------
# Custom Modules (Project Layer)
# ------------------------------
from db_connect.factory import get_db_runner
from custom_tools import TrainRagTool, TrainRagArgs
from security.guardrails import validate_user_input

# ==============================================
# 1. Load Environment Configuration
# ==============================================
load_dotenv()

ENV = os.getenv("ENV", "DEV")   # DEV, PROD
DB_TYPE = os.getenv("DB_TYPE", "sqlite")

API_KEY = os.getenv("GOOGLE_API_KEY")
LLM_MODEL = os.getenv("GOOGLE_MODEL_NAME", "gemini-2.5-flash")

CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "vanna_memory")

print(f"🌍 Environment: {ENV}")
print(f"🗄 Database Engine: {DB_TYPE}")
print(f"🤖 LLM Model: {LLM_MODEL}")

# ==============================================
# 2. Configure Language Model (LLM)
# ==============================================
llm = GeminiLlmService(
    api_key=API_KEY,
    model=LLM_MODEL
)

# ==============================================
# 3. Configure Database Runner (Factory Pattern)
# ==============================================
sql_runner = get_db_runner()
db_tool = RunSqlTool(sql_runner=sql_runner)

# Training Tool (Only admin can use it)
training_tool = TrainRagTool()

# ==============================================
# 4. Configure Memory (ChromaDB)
# ==============================================
agent_memory = ChromaAgentMemory(
    collection_name=COLLECTION_NAME,
    persist_directory=CHROMA_PATH
)

# ==============================================
# 5. User Authentication (Simple resolver)
# ==============================================
class SimpleUserResolver(UserResolver):
    async def resolve_user(self, request_context: RequestContext) -> User:
        email = request_context.get_cookie("vanna_email") or "guest@example.com"
        group = "admin" if email == "admin@example.com" else "user"
        return User(
            id=email,
            email=email,
            group_memberships=[group]
        )

user_resolver = SimpleUserResolver()

# ==============================================
# 6. Tool Registry
# ==============================================
tools = ToolRegistry()

# User Tools
tools.register_local_tool(db_tool, access_groups=["admin", "user"])
tools.register_local_tool(VisualizeDataTool(), access_groups=["admin", "user"])
tools.register_local_tool(SearchSavedCorrectToolUsesTool(), access_groups=["admin", "user"])

# Admin Tools
tools.register_local_tool(SaveTextMemoryTool(), access_groups=["admin"])
tools.register_local_tool(SaveQuestionToolArgsTool(), access_groups=["admin"])
tools.register_local_tool(training_tool, access_groups=["admin"])

# ==============================================
# 7. Assemble the Agent
# ==============================================
agent = Agent(
    tool_registry=tools,
    user_resolver=user_resolver,
    llm_service=llm,
    agent_memory=agent_memory
)

# ==============================================
# 8. Create FastAPI App via Vanna Server
# ==============================================
server = VannaFastAPIServer(agent)
app = server.create_app()

# ==============================================
# 9. Security Middleware (Prompt Guardrails)
# ==============================================
@app.middleware("http")
async def guardrail_middleware(request: Request, call_next):
    if "/chat" in request.url.path and request.method == "POST":
        try:
            # validate_user_input(request)  # Optional activation
            pass
        except Exception as e:
            return JSONResponse(status_code=400, content={"error": str(e)})
    return await call_next(request)

# ==============================================
# 10. CORS (Admin + User Panels)
# ==============================================
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    # Add server IP during deployment
    os.getenv("SERVER_IP_ORIGIN", "*")
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================================
# 11. Custom Admin Training Route
# ==============================================
@app.post("/api/custom/train")
async def api_train_manual(request: Request):
    admin = User(id="api_admin", email="admin@example.com", group_memberships=["admin"])
    ctx = RequestContext(user=admin)

    from vanna.core.tool import ToolContext
    tool_ctx = ToolContext(agent=agent, user=admin)

    result = training_tool.execute(tool_ctx, TrainRagArgs(limit=10))
    
    return {"status": "success", "message": result.result_for_llm}

# ==============================================
# 12. Run Server
# ==============================================
if __name__ == "__main__":
    print("🚀 Starting Vanna Enterprise Backend on port 7262...")
    uvicorn.run(app, host="0.0.0.0", port=7262)
