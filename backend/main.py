from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from routes.claude_qa import router as claude_qa_router  # <-- Existing import
from routes.gitops import router as gitops_router        # <-- Add this import

app = FastAPI()

# Allow frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # or ["*"] during dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(claude_qa_router)  # <-- Existing line
app.include_router(gitops_router)     # <-- Add this line

@app.get("/modules")
def get_modules():
    return [
        {"title": "AI Assistant", "description": "Write better code", "status": "active"},
        {"title": "Refactoring Engine", "description": "Clean up legacy code", "status": "coming-soon"},
    ]

class CodeInput(BaseModel):
    code: str

@app.post("/refactor")
async def refactor_code(input: CodeInput):
    # Just echoing for now — replace with actual logic later
    return {"refactored": input.code[::-1]}  # For demo, reverses code