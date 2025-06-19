from fastapi import APIRouter, Request
from pydantic import BaseModel
import httpx
import os
import asyncio
from time import perf_counter
from db import save_to_history, find_similar_history

router = APIRouter()

class AskQAInput(BaseModel):
    question: str
    code: str = ""  # Make code optional with default empty string

CLAUDE_MODEL = "claude-sonnet-4-20250514"
MAX_RETRIES = 3
TIMEOUT = 60.0

@router.post("/ask-qa")
async def ask_qa(input: AskQAInput):
    print(f"[DEBUG] Processing ask-qa request for question: {input.question[:50]}...")
    
    # Build prompt based on whether code is provided
    if input.code.strip():
        prompt = (
            "Answer the following question about the code in a clear and concise way.\n\n"
            "IMPORTANT: Keep your response focused and to the point. Include:\n\n"
            "1. A brief, clear explanation (2-3 paragraphs max)\n"
            "   - Use simple, professional language\n"
            "   - Focus on the key points\n"
            "   - Use emojis sparingly for clarity\n\n"
            "2. Relevant code examples in code blocks\n"
            "   - Include proper language specification\n"
            "   - Add brief comments\n"
            "   - Keep examples concise\n\n"
            f"Question: {input.question}\n\n"
            f"Code:\n{input.code}\n\n"
            "Keep the total response under 500 words and focus on the most important information."
        )
    else:
        prompt = (
            "Answer the following programming question in a clear and concise way.\n\n"
            "IMPORTANT: Keep your response focused and to the point. Include:\n\n"
            "1. A brief, clear explanation (2-3 paragraphs max)\n"
            "   - Use simple, professional language\n"
            "   - Focus on the key points\n"
            "   - Use emojis sparingly for clarity\n\n"
            "2. Relevant code examples in code blocks\n"
            "   - Include proper language specification\n"
            "   - Add brief comments\n"
            "   - Keep examples concise\n\n"
            f"Question: {input.question}\n\n"
            "Keep the total response under 500 words and focus on the most important information."
        )

    # Check for similar question in history
    if len(input.question.split()) > 4 and not input.question.lower().startswith("solve this"):
        context = f"{input.question} {input.code}"
        similar_response = await find_similar_history("ask-qa", input.question, context)
        if similar_response:
            print("[DEBUG] Found similar question in history, returning cached response")
            return {
                "response": similar_response
            }

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
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 2048,
        "temperature": 0.5,
        "stream": False  # Disable streaming
    }

    start = perf_counter()
    
    try:
        print("[DEBUG] Making request to Claude API")
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=body,
                timeout=TIMEOUT
            )
            response.raise_for_status()
            
            data = response.json()
            print(f"[DEBUG] Claude API response received")
            
            # Extract the text content from Claude's response
            full_response = ""
            for block in data.get("content", []):
                if block.get("type") == "text":
                    text = block.get("text", "")
                    full_response += text
            
            if not full_response:
                full_response = "No response received from Claude"
            
            print(f"[DEBUG] Response length: {len(full_response)}")
            
            # Save to history
            save_to_history(
                feature="ask-qa",
                user_input=body["messages"][0]["content"],
                claude_prompt=body["messages"][0]["content"],
                claude_response=full_response,
                response_time_ms=(perf_counter() - start) * 1000,
                metadata={"model": CLAUDE_MODEL}
            )
            
            return {
                "response": full_response
            }
            
    except Exception as e:
        print(f"[DEBUG] Exception in ask_qa: {e}")
        return {"error": str(e)}
