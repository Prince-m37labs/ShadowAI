from fastapi import APIRouter, Request
from pydantic import BaseModel
import base64
import numpy as np
import cv2
import easyocr
import httpx
import os
import datetime
from time import perf_counter
from db import save_to_history
from typing import Dict, List, Optional
from simplify import simplify_explanation

router = APIRouter()

class ScreenAssistInput(BaseModel):
    image_base64: str
    query: str

class ScreenAssistSessionInput(BaseModel):
    image_base64_list: List[str] = None  # Accept a list of images
    query: str
    session_id: str
    is_final: bool = False

# In-memory session store for OCR text blobs and frame counts (simple, not for production scale)
session_ocr_blobs: Dict[str, Dict] = {}
# session_ocr_blobs[session_id] = {"text": str, "frames": int}

DEBUG_OCR_LOG = os.getenv("DEBUG_OCR_LOG", "false").lower() == "true"

# Move EasyOCR reader initialization outside the route for caching
reader = easyocr.Reader(['en'], gpu=False)

GROQ_MODEL = "llama3-70b-8192"

SYSTEM_PROMPT = """You are an AI that helps developers by analyzing screenshots of code.\nAlways consider the user's query and try to find problems, bugs, or improvements in the code that relate to it."""

def create_prompt(user_query, extracted_code):
    return f"""
User Question:
{user_query}

Visible Code:
{extracted_code}

What issues do you see in the code relevant to the question? Be specific and explain clearly.
"""

@router.post("/screen-assist")
async def screen_assist(input: ScreenAssistSessionInput, request: Request):
    session_id = input.session_id
    # Accept both legacy (single image) and new (list of images) for backward compatibility
    image_list = input.image_base64_list or []
    if not image_list and hasattr(input, 'image_base64'):
        image_list = [input.image_base64]
    if not image_list:
        return {"error": "No images provided."}
    ocr_texts = []
    debug_img_paths = []
    for idx, img_b64 in enumerate(image_list):
        try:
            image_data = base64.b64decode(img_b64.split(',')[-1])
            np_arr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        except Exception as e:
            continue  # Skip bad frames
        try:
            ocr_results = reader.readtext(img, detail=0)
            ocr_text = '\n'.join(ocr_results)
            ocr_texts.append(ocr_text)
            # Save debug image
            debug_img_dir = os.path.join(os.path.dirname(__file__), "../ocr_debug_imgs")
            os.makedirs(debug_img_dir, exist_ok=True)
            debug_img_path = os.path.join(debug_img_dir, f"{session_id}_{idx}_{datetime.datetime.utcnow().isoformat()}.png")
            cv2.imwrite(debug_img_path, img)
            debug_img_paths.append(debug_img_path)
        except Exception as e:
            continue
    full_ocr = '\n'.join(ocr_texts)
    if not full_ocr.strip():
        return {"error": "⚠️ We couldn’t detect code on your screen. Try again or share full screen with your code visible."}
    prompt = create_prompt(input.query, full_ocr)
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
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1024,
        "temperature": 0.5
    }
    start = perf_counter()
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=body
            )
            response.raise_for_status()
            data = response.json()
            if "choices" in data and data["choices"]:
                output = data["choices"][0]["message"]["content"]
            else:
                output = f"[Groq ERROR] Unexpected response: {data}"
            simple_output = simplify_explanation(output)
            response_time = (perf_counter() - start) * 1000
            save_to_history(
                feature="screen-assist",
                user_input=input.query,
                claude_prompt=prompt,
                claude_response=output,
                response_time_ms=response_time,
                metadata={"ocr_preview": full_ocr[:300], "model": GROQ_MODEL, "simple": simple_output}
            )
            return {"analysis": output, "simple": simple_output}
    except Exception as e:
        import traceback
        print("[DEBUG] Exception during Groq API call:", str(e))
        if hasattr(e, 'response') and e.response is not None:
            try:
                print("Groq Error Response:", e.response.text)
            except Exception:
                pass
        print("Groq Exception:", str(e))
        traceback.print_exc()
        return {"error": f"Groq failed: {str(e)}"}
    finally:
        # Clean up debug images
        for path in debug_img_paths:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception as del_e:
                print(f"[DEBUG] Could not delete debug image: {path} - {del_e}")
