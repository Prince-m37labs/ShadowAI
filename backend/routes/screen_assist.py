from fastapi import APIRouter, Request
from pydantic import BaseModel
import base64
import numpy as np
import cv2
from paddleocr import PaddleOCR
import httpx
import os
import datetime
from time import perf_counter
from db import save_to_history
from typing import Dict, List, Optional
import asyncio

router = APIRouter()

class ScreenAssistInput(BaseModel):
    image_base64: str
    query: str

class ScreenAssistSessionInput(BaseModel):
    image_base64_list: List[str] = None
    query: str
    session_id: str
    is_final: bool = False

session_ocr_blobs: Dict[str, Dict] = {}

DEBUG_OCR_LOG = os.getenv("DEBUG_OCR_LOG", "false").lower() == "true"

# Initialize PaddleOCR once at module level
ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False)

CLAUDE_MODEL = "claude-sonnet-4-20250514"
MAX_RETRIES = 3
TIMEOUT = 60.0  # Increased timeout to 60 seconds

SYSTEM_PROMPT = (
    "You are an AI that helps developers by analyzing screenshots of code.\n"
    "Always consider the user's query and try to find problems, bugs, or improvements in the code that relate to it."
)

def preprocess_image(img):
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    return thresh

def create_prompt(user_query, extracted_code):
    return f"""
User Question:
{user_query}

Visible Code:
{extracted_code}

What issues do you see in the code relevant to the question? Be specific and explain clearly.
"""

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

@router.post("/screen-assist")
async def screen_assist(input: ScreenAssistSessionInput, request: Request):
    session_id = input.session_id
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
            
            # Preprocess image
            processed_img = preprocess_image(img)
            
            # Run PaddleOCR
            result = ocr.ocr(processed_img, cls=True)
            
            # Extract text from results
            ocr_results = []
            if result:
                for line in result[0]:
                    if line and len(line) >= 2:
                        text = line[1][0]  # Get the text from the result
                        ocr_results.append(text)
            
            ocr_text = '\n'.join(ocr_results)
            ocr_texts.append(ocr_text)
            
            if DEBUG_OCR_LOG:
                debug_img_dir = os.path.join(os.path.dirname(__file__), "../ocr_debug_imgs")
                os.makedirs(debug_img_dir, exist_ok=True)
                debug_img_path = os.path.join(debug_img_dir, f"{session_id}_{idx}_{datetime.datetime.utcnow().isoformat()}.png")
                cv2.imwrite(debug_img_path, processed_img)
                debug_img_paths.append(debug_img_path)
        except Exception as e:
            print(f"Error processing image {idx}: {str(e)}")
            continue
            
    full_ocr = '\n'.join(ocr_texts)
    if not full_ocr.strip():
        return {"error": "⚠️ We couldn't detect code on your screen. Try again or share full screen with your code visible."}
        
    prompt = create_prompt(input.query, full_ocr)
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
        "system": SYSTEM_PROMPT,
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
                feature="screen-assist",
                user_input=input.query,
                claude_prompt=prompt,
                claude_response=output,
                response_time_ms=(perf_counter() - start) * 1000,
                metadata={"model": CLAUDE_MODEL, "session_id": session_id}
            )

            return {
                "analysis": output,
                "simple": output
            }

    except Exception as e:
        error_msg = str(e)
        print(f"Claude Exception: {error_msg}")
        return {"error": error_msg}
    finally:
        for path in debug_img_paths:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception as del_e:
                print(f"[DEBUG] Could not delete debug image: {path} - {del_e}")
