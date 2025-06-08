from fastapi import APIRouter
from pydantic import BaseModel
import httpx
import os
from time import perf_counter
from db import save_to_history

router = APIRouter()

GROQ_MODEL = "llama3-70b-8192"

class GenerateDocsInput(BaseModel):
    code: str

@router.post("/generate-docs")
async def generate_docs(input: GenerateDocsInput):
    prompt = (
        f"""
        Analyze the following code and generate documentation with these sections:
        1. Description: What does this code do?
        2. Inputs/Outputs: What are the inputs and outputs?
        3. Example Usage: Show a usage example.
        
        Code:
        {input.code}
        """
    )
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
    start = perf_counter()
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
            response_time = (perf_counter() - start) * 1000
            save_to_history(
                feature="docs-generator",
                user_input=input.code,
                claude_prompt=prompt,
                claude_response=output,
                response_time_ms=response_time,
                metadata={"model": GROQ_MODEL}
            )
            return {"docs": output}
    except Exception as e:
        return {"error": f"Groq failed: {str(e)}"}
