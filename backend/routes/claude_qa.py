# backend/routes/claude_qa.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import os

router = APIRouter()

class QARequest(BaseModel):
    question: str
    context: str

@router.post("/claude-qa")
async def claude_qa(request: QARequest):
    headers = {
        "x-api-key": os.getenv("ANTHROPIC_API_KEY"),
        "Authorization": f"Bearer {os.getenv('CLAUDE_API_KEY')}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "claude-3-opus-20240229",
        "messages": [
            {"role": "user", "content": f"Answer the following based on context:\nContext:\n{request.context}\n\nQuestion:\n{request.question}"}
        ],
        "max_tokens": 512
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages", headers=headers, json=payload
            )
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))