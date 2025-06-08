from fastapi import APIRouter
from pydantic import BaseModel
import httpx
import os
import re
from time import perf_counter
from db import save_to_history

router = APIRouter()

class SecurityCheckInput(BaseModel):
    code: str

GROQ_MODEL = "llama3-70b-8192"

@router.post("/security-check")
async def security_check(input: SecurityCheckInput):
    code = input.code
    local_findings = []
    if re.search(r'\beval\s*\(', code):
        local_findings.append("Use of eval() detected.")
    if re.search(r'(password|secret|token|key)\s*=\s*["\'].*["\']', code, re.IGNORECASE):
        local_findings.append("Possible hardcoded secret detected.")
    if re.search(r'import\s+os', code) and re.search(r'os\.system\s*\(', code):
        local_findings.append("Use of os.system detected.")
    if re.search(r'input\s*\(', code) and not re.search(r'sanitize|escape', code, re.IGNORECASE):
        local_findings.append("User input may be unsanitized.")
    local_summary = "\n".join(local_findings) if local_findings else "No obvious issues found by local scan."
    prompt = (
        f"Analyze the following code for potential security vulnerabilities. "
        f"Point out any risky patterns, insecure practices, or sensitive information exposure.\n"
        f"Local scan findings:\n{local_summary}\n\nCode:\n{code}"
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
                feature="security-check",
                user_input=input.code,
                claude_prompt=prompt,
                claude_response=output,
                response_time_ms=response_time,
                metadata={"model": GROQ_MODEL}
            )
            return {"security": output}
    except Exception as e:
        return {"error": f"Groq failed: {str(e)}"}
