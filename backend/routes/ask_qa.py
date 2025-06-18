from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
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
                "analysis": similar_response,
                "simple": similar_response,
                "streamlined": similar_response.split("Streamlined Version:")[-1].strip() if "Streamlined Version:" in similar_response else ""
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
        "stream": True
    }

    start = perf_counter()
    
    async def stream_response():
        print("[DEBUG] Starting stream_response function")
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            try:
                print("[DEBUG] Making request to Claude API")
                async with client.stream(
                    "POST",
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=body,
                    timeout=TIMEOUT
                ) as response:
                    response.raise_for_status()
                    print("[DEBUG] Claude API response received, starting to read lines")
                    full_response = ""
                    
                    # Handle Claude's streaming response format
                    async for line in response.aiter_lines():
                        print(f"[DEBUG] Received line: {line[:100]}...")  # Log first 100 chars
                        if line.startswith('data: '):
                            data = line[6:]  # Remove 'data: ' prefix
                            if data.strip() == '[DONE]':
                                print("[DEBUG] Received [DONE] signal")
                                break
                            
                            try:
                                # Parse the JSON chunk from Claude
                                import json
                                chunk_data = json.loads(data)
                                print(f"[DEBUG] Parsed JSON chunk: {chunk_data}")
                                
                                # Handle different types of streaming events
                                if chunk_data.get('type') == 'content_block_delta':
                                    delta = chunk_data.get('delta', {})
                                    if delta.get('type') == 'text_delta':
                                        text = delta.get('text', '')
                                        full_response += text
                                        print(f"[DEBUG] Yielding text delta: {text[:50]}...")
                                        yield f"data: {text}\n\n"
                                elif 'content' in chunk_data and chunk_data['content']:
                                    # Fallback for older format
                                    for content_block in chunk_data['content']:
                                        if content_block.get('type') == 'text':
                                            text = content_block.get('text', '')
                                            full_response += text
                                            print(f"[DEBUG] Yielding text: {text[:50]}...")
                                            yield f"data: {text}\n\n"
                            except json.JSONDecodeError as e:
                                print(f"[DEBUG] JSON decode error: {e}")
                                # If it's not JSON, treat as plain text
                                if data.strip():
                                    full_response += data
                                    print(f"[DEBUG] Yielding plain text: {data[:50]}...")
                                    yield f"data: {data}\n\n"
                    
                    print(f"[DEBUG] Stream completed, full response length: {len(full_response)}")
                    # Save to history after stream completes
                    save_to_history(
                        feature="ask-qa",
                        user_input=body["messages"][0]["content"],
                        claude_prompt=body["messages"][0]["content"],
                        claude_response=full_response,
                        response_time_ms=(perf_counter() - start) * 1000,
                        metadata={"model": CLAUDE_MODEL}
                    )
            except Exception as e:
                print(f"[DEBUG] Exception in stream_response: {e}")
                yield f"data: [ERROR] {str(e)}\n\n"

    return StreamingResponse(
        stream_response(),
        media_type="text/event-stream"
    )
