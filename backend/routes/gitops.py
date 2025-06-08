from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import os
from typing import List, Optional

router = APIRouter()

GROQ_MODEL = "llama3-70b-8192"

class GitOpsRequest(BaseModel):
    instruction: Optional[str] = None
    error_message: Optional[str] = None
    git_log: Optional[str] = None
    branch_status: Optional[str] = None
    commit_messages: Optional[List[str]] = None
    pr_diff: Optional[str] = None

@router.post("/gitops")
async def gitops_handler(request: GitOpsRequest):
    prompt = None
    summary = None
    suggestions = []
    warnings = []
    command = None

    # 1. Git Error Interpreter
    if request.error_message:
        prompt = f"Explain this git error and how to fix it:\n\n{request.error_message}"
    # 2. Git Log or Branch Status Explainer
    elif request.git_log or request.branch_status:
        log = request.git_log or request.branch_status
        prompt = f"A developer sent this Git log output. Help explain what’s going on and what they should do next:\n\n{log}"
    # 3. Commit Hygiene Checker / PR Advisor
    elif request.commit_messages or request.pr_diff:
        if request.commit_messages:
            commits = '\n'.join(request.commit_messages)
            prompt = f"Review the following commit messages and suggest improvements for clarity and Git best practices:\n\n{commits}"
        else:
            prompt = f"Review this PR diff for best practices and suggest improvements:\n\n{request.pr_diff}"
    # 4. Command Generator (default)
    elif request.instruction:
        prompt = f"Convert the following instruction into a git command only:\n\nInstruction:\n{request.instruction}"
    else:
        return {"error": "No valid input provided."}

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return {"error": "GROQ_API_KEY not set in environment"}
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    body = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1024,
        "temperature": 0.5
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=body
            )
            response.raise_for_status()
            data = response.json()
            output = data["choices"][0]["message"]["content"]

            # Dangerous Command Detector
            risky_patterns = ["--force", "git push origin main", "rm -rf .git"]
            if any(p in output for p in risky_patterns):
                warnings.append("⚠️ This command is risky. Are you sure you want to do this?")

            # Try to parse for command, summary, suggestions
            if request.instruction:
                command = output.strip()
            elif request.error_message or request.git_log or request.branch_status:
                summary = output.strip()
            elif request.commit_messages or request.pr_diff:
                suggestions.append(output.strip())

            return {
                "summary": summary,
                "command": command,
                "warnings": warnings,
                "suggestions": suggestions
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Groq failed: {str(e)}")