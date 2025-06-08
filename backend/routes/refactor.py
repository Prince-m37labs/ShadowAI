from fastapi import APIRouter
from pydantic import BaseModel
import httpx
import os
from time import perf_counter
from db import save_to_history

router = APIRouter()

class CodeInput(BaseModel):
    code: str
    mode: str = "readability"

GROQ_MODEL = "llama3-70b-8192"

@router.post("/refactor")
async def refactor_code(input: CodeInput):
    prompt = f"Refactor the following code to make it more modern, readable, and idiomatic:\n\n{input.code}"
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return {"error": "GROQ_API_KEY not set in environment"}
    print("Groq Key:", repr(api_key))  # Debug: print the key (should not be None or empty)
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
    print("Groq Payload:", body)  # Debug: print the payload
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
            print("Groq Response:", data)  # Debug: print the full Groq response
            if "choices" in data and data["choices"]:
                output = data["choices"][0]["message"]["content"]
            else:
                output = f"[Groq ERROR] Unexpected response: {data}"
            print("Returning refactored:", output)
            response_time = (perf_counter() - start) * 1000
            save_to_history(
                feature="refactor",
                user_input=input.code,
                claude_prompt=prompt,
                claude_response=output,
                response_time_ms=response_time,
                metadata={"mode": input.mode, "model": GROQ_MODEL}
            )
            return {"refactored": output}
    except Exception as e:
        import traceback
        if hasattr(e, 'response') and e.response is not None:
            try:
                print("Groq Error Response:", e.response.text)
            except Exception:
                pass
        print("Groq Exception:", str(e))
        traceback.print_exc()
        return {"error": f"Groq failed: {str(e)}"}
