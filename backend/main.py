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

print("📦 Claude API Key:", os.getenv("ANTHROPIC_API_KEY"))
print("🛠 Mongo URI:", os.getenv("MONGODB_URI"))
app = FastAPI()

# Define allowed origins for CORS using environment variable
# Set CORS_ORIGINS to a comma-separated list of allowed origins in your environment
origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")]

# Allow frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(refactor_router)
app.include_router(qa_router)
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
    logging.info(f"Incoming request path: {request.url.path}")
    response = await call_next(request)
    return response
