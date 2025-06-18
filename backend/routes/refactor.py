from fastapi import APIRouter
from pydantic import BaseModel
import httpx
import os
from time import perf_counter
from db import save_to_history
from db import find_similar_history
import asyncio


router = APIRouter()

class RefactorInput(BaseModel):
    code: str
    mode: str = "readability"
    target_language: str = "same"  # Default to same language as input

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

@router.post("/refactor")
async def refactor_code(input: RefactorInput):
    if len(input.code.split()) > 4:
        context = f"{input.code} {input.mode}"
        if input.mode == 'modern':
            context += f" {input.target_language}"
        cached = await find_similar_history("refactor", input.code, context)
        if cached:
            print("[DEBUG] Returning cached response from MongoDB...")
            return {"refactored": cached}

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return {"error": "ANTHROPIC_API_KEY not set in environment"}

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }

    # Only include language conversion for modern mode
    language_conversion = f"Convert the code to {input.target_language} and " if input.mode == 'modern' and input.target_language != 'same' else ""
    
    body = {
        "model": CLAUDE_MODEL,
        "messages": [
            {
                "role": "user",
                "content": f"""You are an expert code refactoring assistant. {language_conversion}Refactor the provided code according to the specified mode.

Mode: {input.mode}

If the mode is 'modern':
  - Convert the code to modern JavaScript/TypeScript practices
  - Use ES6+ features, async/await, arrow functions, destructuring, etc.
  - {f"Convert the code to {input.target_language}" if input.target_language != 'same' else "Keep the same programming language but modernize the syntax"}
If the mode is 'clean', improve code readability and structure.
If the mode is 'optimize', focus on performance improvements.
If the mode is 'security', focus on security improvements and vulnerability fixes.

IMPORTANT: Keep your response focused and to the point. Include:

1. A brief explanation of the changes made (1-2 paragraphs max)
   - Use simple, professional language
   - Focus on the key improvements
   - Use emojis sparingly for clarity

2. The refactored code in a code block with proper language specification
   - Add brief comments
   - Keep the code clean and readable

Code to refactor:
{input.code}

Keep the total response under 500 words and focus on the most important changes."""
            }
        ],
        "max_tokens": 2048,
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
                feature="refactor",
                user_input=input.code,
                claude_prompt=body["messages"][0]["content"],
                claude_response=output,
                response_time_ms=(perf_counter() - start) * 1000,
                metadata={
                    "mode": input.mode,
                    "target_language": input.target_language if input.mode == 'modern' else None,
                    "model": CLAUDE_MODEL
                }
            )

            return {"refactored": output}

    except Exception as e:
        error_msg = str(e)
        print(f"Claude Exception: {error_msg}")
        return {"error": error_msg}
