# # Add this utility to simplify Groq output using LangChain and OpenAI
# import os
# import httpx
# import asyncio
# from time import perf_counter

# CLAUDE_MODEL = "claude-sonnet-4-20250514"
# MAX_RETRIES = 3
# TIMEOUT = 60.0  # Increased timeout to 60 seconds

# async def make_claude_request(client, headers, body, retry_count=0):
#     try:
#         response = await client.post(
#             "https://api.anthropic.com/v1/messages",
#             headers=headers,
#             json=body,
#             timeout=TIMEOUT
#         )
#         response.raise_for_status()
#         return response.json()
#     except httpx.TimeoutException as e:
#         if retry_count < MAX_RETRIES:
#             print(f"Timeout occurred, retrying... (attempt {retry_count + 1}/{MAX_RETRIES})")
#             await asyncio.sleep(1 * (retry_count + 1))  # Exponential backoff
#             return await make_claude_request(client, headers, body, retry_count + 1)
#         raise Exception(f"Claude API timed out after {MAX_RETRIES} retries: {str(e)}")
#     except httpx.HTTPStatusError as e:
#         raise Exception(f"Claude API returned HTTP error: {str(e)}")
#     except Exception as e:
#         raise Exception(f"Claude API failed: {str(e)}")

# async def simplify_explanation(original: str) -> str:
#     api_key = os.getenv("ANTHROPIC_API_KEY")
#     if not api_key:
#         return original  # fallback: return original if no key

#     headers = {
#         "x-api-key": api_key,
#         "anthropic-version": "2023-06-01",
#         "Content-Type": "application/json"
#     }

#     body = {
#         "model": CLAUDE_MODEL,
#         "messages": [
#             {
#                 "role": "user",
#                 "content": f"""You are a simplifier for junior developers.
# Rephrase the following explanation in plain, friendly terms:

# {original}"""
#             }
#         ],
#         "max_tokens": 1024,
#         "temperature": 0.3
#     }

#     start = perf_counter()
#     try:
#         async with httpx.AsyncClient(timeout=TIMEOUT) as client:
#             data = await make_claude_request(client, headers, body)
            
#             output = ""
#             for block in data.get("content", []):
#                 if block.get("type") == "text":
#                     text = block.get("text", "")
#                     output += text

#             if not output:
#                 output = f"[Claude ERROR] Unexpected response: {data}"

#             return output

#     except Exception as e:
#         print(f"Claude Exception: {str(e)}")
#         return original  # fallback to original on error
