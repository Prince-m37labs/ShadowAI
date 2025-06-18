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
from typing import Dict, List, Optional
import asyncio
import re

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

# Initialize PaddleOCR with optimized settings for speed
ocr = PaddleOCR(
    use_angle_cls=False,  # Disable angle classification for speed
    lang='en',
    use_gpu=False,
    det_db_box_thresh=0.3,  # Higher threshold for faster processing
    use_dilation=False,  # Disable dilation for speed
    rec_algorithm='CRNN',
    rec_image_shape='3, 32, 320'  # Smaller image shape for faster processing
)

CLAUDE_MODEL = "claude-sonnet-4-20250514"
MAX_RETRIES = 3
TIMEOUT = 20.0  # Reduced timeout to 20 seconds
OCR_TIMEOUT = 5.0  # OCR timeout

SYSTEM_PROMPT = (
    "You are an AI that helps developers by analyzing screenshots of code.\n"
    "Always consider the user's query and try to find problems, bugs, or improvements in the code that relate to it."
)

def preprocess_image(img):
    # Resize moderately to balance speed and accuracy
    img = cv2.resize(img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_LINEAR)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply simple contrast enhancement
    clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(4, 4))
    enhanced = clahe.apply(gray)

    # Apply simple thresholding
    _, thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh

def create_prompt(user_query, extracted_code):
    return (
        f"Analyze this screenshot of code and answer the user's question: '{user_query}'\n\n"
        "IMPORTANT: Keep your response focused and to the point. Include:\n\n"
        "1. A brief, clear explanation (2-3 paragraphs max)\n"
        "   - Use simple, professional language\n"
        "   - Focus on the key points\n"
        "   - Use emojis sparingly for clarity\n\n"
        "2. Relevant code examples or suggestions in code blocks\n"
        "   - Include proper language specification\n"
        "   - Add brief comments\n"
        "   - Keep examples concise\n\n"
        f"Code from screenshot:\n{extracted_code}\n\n"
        "Keep the total response under 500 words and focus on the most important information."
    )

async def run_ocr_with_timeout(image, timeout=OCR_TIMEOUT):
    """Run OCR with timeout to prevent hanging"""
    try:
        # Run OCR in executor to allow timeout
        loop = asyncio.get_running_loop()
        result = await asyncio.wait_for(
            loop.run_in_executor(None, ocr.ocr, image, False),  # cls=False for speed
            timeout=timeout
        )
        return result
    except asyncio.TimeoutError:
        print(f"OCR timeout after {timeout} seconds")
        return None
    except Exception as e:
        print(f"OCR error: {str(e)}")
        return None

def extract_simple_text_from_image(image):
    """Simple text extraction fallback when OCR fails"""
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold to get binary image
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        
        # Find contours (potential text regions)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Extract potential text regions
        text_regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 20 and h > 10:  # Filter small regions
                text_regions.append((x, y, w, h))
        
        # Sort by y-coordinate (top to bottom)
        text_regions.sort(key=lambda x: x[1])
        
        # Return a simple representation
        return f"Found {len(text_regions)} potential text regions in image"
        
    except Exception as e:
        print(f"Simple text extraction error: {str(e)}")
        return "Image processing failed"

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

    print(f"[DEBUG] Processing {len(image_list)} images for session {session_id}")
    ocr_texts = []
    
    for idx, img_b64 in enumerate(image_list):
        try:
            print(f"[DEBUG] Processing image {idx + 1}/{len(image_list)}")
            image_data = base64.b64decode(img_b64.split(',')[-1])
            np_arr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            if img is None:
                print(f"[DEBUG] Failed to decode image {idx}")
                continue

            # Preprocess image
            processed_img = preprocess_image(img)

            # Run OCR on preprocessed image only (faster)
            print(f"[DEBUG] Running OCR on image {idx + 1}")
            result = await run_ocr_with_timeout(processed_img)
            
            if result is None:
                print(f"[DEBUG] OCR failed for image {idx + 1}, trying fallback")
                # Try fallback method
                fallback_text = extract_simple_text_from_image(img)
                if fallback_text:
                    ocr_texts.append(fallback_text)
                continue

            # Extract text from results
            ocr_results = []
            if result and len(result) > 0:
                for line in result[0]:
                    if line and len(line) >= 2:
                        text = line[1][0].strip()
                        if text and len(text) > 2:  # Filter out very short text
                            ocr_results.append(text)

            ocr_text = '\n'.join(ocr_results)
            if ocr_text.strip():
                ocr_texts.append(ocr_text)
                print(f"[DEBUG] Extracted {len(ocr_results)} text lines from image {idx + 1}")
            else:
                print(f"[DEBUG] No text extracted from image {idx + 1}")

        except Exception as e:
            print(f"[DEBUG] Error processing image {idx}: {str(e)}")
            continue
            
    full_ocr = '\n'.join(ocr_texts)
    print(f"[DEBUG] Total extracted text length: {len(full_ocr)}")
    
    if not full_ocr.strip():
        return {"error": "⚠️ We couldn't detect code on your screen. Please ensure your code editor is visible and try again."}
        
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
        "max_tokens": 2048,
        "temperature": 0.5
    }
    
    start = perf_counter()
    try:
        print(f"[DEBUG] Sending to Claude API")
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            data = await make_claude_request(client, headers, body)
            
            output = ""
            for block in data.get("content", []):
                if block.get("type") == "text":
                    text = block.get("text", "")
                    output += text

            if not output:
                output = f"[Claude ERROR] Unexpected response: {data}"

            processing_time = (perf_counter() - start) * 1000
            print(f"[DEBUG] Total processing time: {processing_time:.2f}ms")

            return {
                "analysis": output,
                "simple": output,
                "streamlined": output.split("Streamlined Version:")[-1].strip() if "Streamlined Version:" in output else ""
            }

    except Exception as e:
        error_msg = str(e)
        print(f"[DEBUG] Claude Exception: {error_msg}")
        return {"error": error_msg}
