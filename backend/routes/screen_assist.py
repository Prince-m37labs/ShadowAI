# NOTE for frontend: capture 5 screenshots over 10 seconds (every 2s) to ensure coverage.
# Pass these in image_base64_list to this route.
from fastapi import APIRouter, Request
from pydantic import BaseModel
import base64
import numpy as np
import cv2
from paddleocr import PaddleOCR
import pytesseract
import easyocr
import httpx
import os
import datetime
from time import perf_counter
from typing import Dict, List, Optional
import asyncio
import re
from difflib import get_close_matches

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
    det_db_box_thresh=0.3,  # Higher threshold for faster processing
    use_dilation=False,  # Disable dilation for speed
    rec_algorithm='CRNN',
    rec_image_shape='3, 32, 480'  # Wider shape for better small-font capture
)

# Initialize EasyOCR reader once
easyocr_reader = easyocr.Reader(['en'], gpu=False)

CLAUDE_MODEL = "claude-sonnet-4-20250514"
MAX_RETRIES = 3
TIMEOUT = 20.0  # Reduced timeout to 20 seconds
OCR_TIMEOUT = 5.0  # OCR timeout

SYSTEM_PROMPT = (
    "You are an AI that helps developers by analyzing screenshots of code.\n"
    "Always consider the user's query and try to find problems, bugs, or improvements in the code that relate to it."
)

def preprocess_image(img):
    # Do not resize image — preserve original dimensions
    # img = cv2.resize(img, None, fx=3.0, fy=3.0, interpolation=cv2.INTER_LINEAR)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply CLAHE for local contrast enhancement (helps low-contrast themes)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    # Denoise with bilateral filter (preserve edges)
    gray = cv2.bilateralFilter(gray, 9, 75, 75)

    # Adaptive threshold to handle varying font weights and themes
    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        blockSize=17,
        C=3
    )

    # Morphological operations to clarify character edges
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # Invert back to original form if needed
    morph = cv2.bitwise_not(morph)

    return morph

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

#
# Removed run_ocr_with_timeout: replaced with pytesseract/easyocr fallback logic

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

# Common programming keywords for fuzzy matching
KEYWORDS = {
    "python": [
        "def", "return", "print", "for", "while", "if", "elif", "else", "import",
        "from", "class", "try", "except", "finally", "with", "as", "raise", "assert",
        "yield", "lambda", "global", "nonlocal", "pass", "break", "continue", "in", "is"
    ]
}

# Known OCR error fixes (exact replacements)
OCR_FIXES = {
    "prinf": "printf",
    "retunr": "return",
    "Retrun": "Return",
    "fucntion": "function",
    "funtcion": "function",
    "flase": "false",
    "Flase": "False",
    "ture": "true",
    "Ture": "True"
}

def clean_ocr_text(text: str, lang="python") -> str:
    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:
        words = re.findall(r'\w+|\W+', line)
        cleaned_line = ""
        for word in words:
            stripped = word.strip()
            if stripped in OCR_FIXES:
                cleaned_line += OCR_FIXES[stripped]
            elif stripped.isalpha() and lang in KEYWORDS:
                close = get_close_matches(stripped, KEYWORDS[lang], n=1, cutoff=0.85)
                cleaned_line += close[0] if close else word
            else:
                cleaned_line += word
        cleaned_lines.append(cleaned_line)
    return "\n".join(cleaned_lines)

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

            # Use pytesseract first, fallback to easyocr, then fallback to simple extraction
            print(f"[DEBUG] Running OCR on image {idx + 1}")
            ocr_text = ""
            try:
                ocr_text = pytesseract.image_to_string(processed_img)
                if not ocr_text.strip():
                    raise ValueError("Tesseract returned empty text")
                print(f"[DEBUG] Tesseract OCR result for image {idx + 1}:\n{ocr_text}")
            except Exception as tesseract_error:
                print(f"[DEBUG] Tesseract failed: {tesseract_error}")
                try:
                    result = easyocr_reader.readtext(processed_img)
                    ocr_text = "\n".join([line[1] for line in result if line[1].strip()])
                    print(f"[DEBUG] EasyOCR fallback result for image {idx + 1}:\n{ocr_text}")
                except Exception as easyocr_error:
                    print(f"[DEBUG] EasyOCR failed: {easyocr_error}")
                    ocr_text = extract_simple_text_from_image(img)
                    ocr_text = f"[OCR failed, fallback]: {ocr_text}"

            if ocr_text.strip():
                ocr_texts.append(ocr_text.strip())
                print(f"[DEBUG] Extracted text from image {idx + 1}")
            else:
                print(f"[DEBUG] No text extracted from image {idx + 1}")

        except Exception as e:
            print(f"[DEBUG] Error processing image {idx}: {str(e)}")
            continue
            
    full_ocr = '\n'.join(ocr_texts)
    full_ocr = clean_ocr_text(full_ocr, lang="python")
    print(f"[DEBUG] Cleaned OCR Text:\n{full_ocr}")
    print(f"[DEBUG] Total extracted text length: {len(full_ocr)}")
    
    if not full_ocr.strip():
        fallback_message = (
            "⚠️ We couldn't detect readable code from your screen capture. "
            "This may happen if:\n"
            "- Your code font is very small\n"
            "- Your editor theme is dark with low contrast\n\n"
            "🛠 Try increasing font size, using a light theme, or zooming in before running Screen Assist again."
        )
        return {"error": fallback_message}
        
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
