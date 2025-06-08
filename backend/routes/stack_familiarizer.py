from fastapi import APIRouter
from pydantic import BaseModel
import httpx
import os
from time import perf_counter
from db import save_to_history

router = APIRouter()

class StackExplainInput(BaseModel):
    file_content: str
    file_type: str = None

@router.post("/explain-stack")
async def explain_stack(input: StackExplainInput):
    file_type_hint = f"This is a {input.file_type}. " if input.file_type else ""
    prompt = (
        f"{file_type_hint}Explain the technologies and libraries listed in the following project file. "
        f"Describe their purpose and how they fit into a modern web stack:\n\n{input.file_content}"
    )
    headers = {
        "x-api-key": os.getenv("ANTHROPIC_API_KEY"),
        "Authorization": f"Bearer {os.getenv('CLAUDE_API_KEY')}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "claude-3-opus-20240229",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1024
    }
    start = perf_counter()
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            content = data.get("content") or "No response from Claude."
            response_time = (perf_counter() - start) * 1000
            meta = {"file_type": input.file_type} if input.file_type else None
            save_to_history(
                feature="explain-stack",
                user_input=input.file_content,
                claude_prompt=prompt,
                claude_response=content,
                response_time_ms=response_time,
                metadata=meta
            )
            return {"explanation": content}
    except Exception as e:
        return {"explanation": f"Error: {str(e)}"}
