from fastapi import APIRouter
from pydantic import BaseModel
import httpx
import os
from time import perf_counter
from db import save_to_history
import asyncio

router = APIRouter()

class AskQAInput(BaseModel):
    question: str

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

@router.post("/ask-qa")
async def ask_qa(input: AskQAInput):
    print(f"[DEBUG] Processing ask-qa request for question: {input.question[:50]}...")
    prompt = f"Answer the following question as if explaining to a developer:\n\n{input.question}"
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
            print("[DEBUG] Making Claude API request...")
            data = await make_claude_request(client, headers, body)
            
            output = ""
            for block in data.get("content", []):
                if block.get("type") == "text":
                    text = block.get("text", "")
                    output += text

            if not output:
                output = f"[Claude ERROR] Unexpected response: {data}"

            print("[DEBUG] Claude response received, attempting to save to MongoDB...")
            try:
                # Save to history asynchronously
                doc_id = await save_to_history(
                    feature="ask-qa",
                    user_input=input.question,
                    claude_prompt=prompt,
                    claude_response=output,
                    response_time_ms=(perf_counter() - start) * 1000,
                    metadata={"model": CLAUDE_MODEL}
                )
                print(f"[DEBUG] Successfully saved to MongoDB with ID: {doc_id}")
            except Exception as db_error:
                print(f"[ERROR] Failed to save to MongoDB: {str(db_error)}")
                # Continue with the response even if saving fails
                pass

            return {"answer": output}

    except Exception as e:
        error_msg = str(e)
        print(f"[ERROR] Claude Exception: {error_msg}")
        return {"error": error_msg}
