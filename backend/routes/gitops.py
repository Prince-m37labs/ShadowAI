from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import os

router = APIRouter()

class GitOpsRequest(BaseModel):
    instruction: str

@router.post("/gitops")
async def gitops_handler(request: GitOpsRequest):
    prompt = f"Convert the following instruction into a git command only:\n\nInstruction:\n{request.instruction}"

    headers = {
        "Authorization": f"Bearer {os.getenv('CLAUDE_API_KEY')}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "claude-3-opus-20240229",  # Or the model you're allowed to use
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 100
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            content = data.get("content") or "No response from Claude."
            return {"git_command": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))