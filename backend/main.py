from fastapi import FastAPI
import os
from fastapi.middleware.cors import CORSMiddleware
from routes.refactor import router as refactor_router
from routes.ask_qa import router as qa_router
from routes.gitops import router as gitops_router
from routes.screen_assist import router as screen_assist_router
from routes.history import router as history_router
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

load_dotenv()

import db  # ensures DB connection is initialized and logs are printed

print("🚀 Starting AI Development Assistant Backend...")
print("📦 Claude API Key:", "✅ Set" if os.getenv("ANTHROPIC_API_KEY") else "❌ Missing")
print("🛠 Mongo URI:", "✅ Set" if os.getenv("MONGODB_URI") else "❌ Missing")

app = FastAPI(title="AI Development Assistant API", version="1.0.0")

# Define allowed origins for CORS - support both local development and Replit
default_origins = ["http://localhost:3000", "https://localhost:3000"]
replit_origins = [f"https://{os.getenv('REPL_SLUG', '')}.{os.getenv('REPL_OWNER', '')}.repl.co"]

# Combine all allowed origins
all_origins = default_origins + replit_origins
env_origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "").split(",") if origin.strip()]
all_origins.extend(env_origins)

print(f"🌐 CORS Origins: {all_origins}")

# Allow frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=all_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(refactor_router)
app.include_router(qa_router)
app.include_router(gitops_router)
app.include_router(screen_assist_router)
app.include_router(history_router)

@app.get("/")
def root():
    return {"message": "AI Development Assistant API", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

@app.get("/modules")
def get_modules():
    return [
        {"title": "AI Assistant", "description": "Write better code", "status": "active"},
        {"title": "Refactoring Engine", "description": "Clean up legacy code", "status": "coming-soon"},
    ]

@app.on_event("startup")
async def list_routes():
    print("✅ Backend started successfully!")
    print("📋 Registered routes:")
    for route in app.routes:
        print(f"  - {route.path}")

@app.middleware("http")
async def log_request_path(request, call_next):
    logging.info(f"Incoming request path: {request.url.path}")
    response = await call_next(request)
    return response
