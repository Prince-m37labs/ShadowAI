from fastapi import APIRouter
from pydantic import BaseModel
import httpx
import os
import re
from time import perf_counter
from db import save_to_history
import asyncio

router = APIRouter()

class SecurityCheckInput(BaseModel):
    code: str

CLAUDE_MODEL = "claude-sonnet-4-20250514"
MAX_RETRIES = 3
TIMEOUT = 60.0  # Increased timeout to 60 seconds

async def make_claude_request(client, headers, body, retry_count=0):
    try:
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=body,
            timeout=TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except httpx.TimeoutException as e:
        if retry_count < MAX_RETRIES:
            print(f"Timeout occurred, retrying... (attempt {retry_count + 1}/{MAX_RETRIES})")
            await asyncio.sleep(1 * (retry_count + 1))  # Exponential backoff
            return await make_claude_request(client, headers, body, retry_count + 1)
        raise Exception(f"Claude API timed out after {MAX_RETRIES} retries: {str(e)}")
    except httpx.HTTPStatusError as e:
        raise Exception(f"Claude API returned HTTP error: {str(e)}")
    except Exception as e:
        raise Exception(f"Claude API failed: {str(e)}")

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

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return {"error": "ANTHROPIC_API_KEY not set in environment"}

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }

    body = {
        "model": CLAUDE_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1024,
        "temperature": 0.5
    }

    start = perf_counter()
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            data = await make_claude_request(client, headers, body)
            
            output = ""
            for block in data.get("content", []):
                if block.get("type") == "text":
                    text = block.get("text", "")
                    output += text

            if not output:
                output = f"[Claude ERROR] Unexpected response: {data}"

            # Save to history
            save_to_history(
                feature="security-check",
                user_input=input.code,
                claude_prompt=prompt,
                claude_response=output,
                response_time_ms=(perf_counter() - start) * 1000,
                metadata={"model": CLAUDE_MODEL, "local_findings": local_findings}
            )

            return {"security": output}

    except Exception as e:
        error_msg = str(e)
        print(f"Claude Exception: {error_msg}")
        return {"error": error_msg}
