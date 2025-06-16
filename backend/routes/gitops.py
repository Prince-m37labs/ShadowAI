from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import os
from typing import List, Optional
import asyncio
from time import perf_counter
from db import save_to_history

router = APIRouter()

CLAUDE_MODEL = "claude-sonnet-4-20250514"
MAX_RETRIES = 3
TIMEOUT = 60.0  # Increased timeout to 60 seconds

class GitOpsRequest(BaseModel):
    instruction: Optional[str] = None
    error_message: Optional[str] = None
    git_log: Optional[str] = None
    branch_status: Optional[str] = None
    commit_messages: Optional[List[str]] = None
    pr_diff: Optional[str] = None

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
        prompt = f"A developer sent this Git log output. Help explain what's going on and what they should do next:\n\n{log}"
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

            # Save to history
            save_to_history(
                feature="gitops",
                user_input=str(request.dict()),
                claude_prompt=prompt,
                claude_response=output,
                response_time_ms=(perf_counter() - start) * 1000,
                metadata={"model": CLAUDE_MODEL}
            )

            return {
                "summary": summary,
                "command": command,
                "warnings": warnings,
                "suggestions": suggestions
            }

    except Exception as e:
        error_msg = str(e)
        print(f"Claude Exception: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)