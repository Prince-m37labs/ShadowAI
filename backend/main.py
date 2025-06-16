from fastapi import FastAPI
import os
from fastapi.middleware.cors import CORSMiddleware
from routes.refactor import router as refactor_router
from routes.docs_generator import router as docs_router
from routes.security_check import router as security_router
from routes.ask_qa import router as qa_router
from routes.stack_familiarizer import router as stack_router
from routes.gitops import router as gitops_router
from routes.screen_assist import router as screen_assist_router
from routes.history import router as history_router
from dotenv import load_dotenv

load_dotenv()

import db  # ensures DB connection is initialized and logs are printed

print("📦 Claude API Key:", os.getenv("ANTHROPIC_API_KEY"))
print("🛠 Mongo URI:", os.getenv("MONGODB_URI"))
app = FastAPI()

# Allow frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # or ["*"] during dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(refactor_router)
app.include_router(docs_router)
app.include_router(security_router)
app.include_router(qa_router)
app.include_router(stack_router)
app.include_router(gitops_router)
app.include_router(screen_assist_router)
app.include_router(history_router)

@app.get("/modules")
def get_modules():
    return [
        {"title": "AI Assistant", "description": "Write better code", "status": "active"},
        {"title": "Refactoring Engine", "description": "Clean up legacy code", "status": "coming-soon"},
    ]

@app.on_event("startup")
async def list_routes():
    print("Registered routes:")
    for route in app.routes:
        print(route.path)

@app.middleware("http")
async def log_request_path(request, call_next):
    print(f"[DEBUG] Incoming request path: {request.url.path}")
    response = await call_next(request)
    return response
