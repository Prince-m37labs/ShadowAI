from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import os
from typing import List, Optional, Dict
import asyncio
from time import perf_counter
from db import save_to_history
from db import find_similar_history


router = APIRouter()

CLAUDE_MODEL = "claude-sonnet-4-20250514"
MAX_RETRIES = 3
TIMEOUT = 60.0  # Increased timeout to 60 seconds

class GitOpsRequest(BaseModel):
    instruction: Optional[str] = None
    error_message: Optional[str] = None
    git_log: Optional[str] = None
    branch_status: Optional[str] = None
    commit_messages: Optional[List[str]] = None
    pr_diff: Optional[str] = None
    scenario_type: Optional[str] = None  # New field for interactive scenarios
    explain_terms: Optional[bool] = False

# Common Git scenarios for non-coders
GIT_SCENARIOS = {
    "error": "I got an error",
    "undo": "I want to undo something",
    "branch": "I'm not sure what branch I'm on",
    "merge": "I need to merge changes",
    "stash": "I need to save my changes temporarily",
    "reset": "I want to reset my changes",
    "conflict": "I have merge conflicts"
}

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

def create_scenario_prompt(scenario_type: str, error_message: Optional[str] = None) -> str:
    base_prompts = {
        "error": "I'm getting this Git error. Please help me fix it and explain what went wrong in simple terms:",
        "undo": "I want to undo my last Git action. Please guide me through the process step by step:",
        "branch": "I'm confused about which branch I'm on and what branches exist. Please help me understand:",
        "merge": "I need to merge changes from another branch. Please guide me through the process:",
        "stash": "I need to save my current changes temporarily. Please show me how to use Git stash:",
        "reset": "I want to reset my changes to a previous state. Please help me do this safely:",
        "conflict": "I have merge conflicts. Please help me resolve them step by step:"
    }
    
    prompt = base_prompts.get(scenario_type, "Please help me with this Git situation:")
    if error_message:
        prompt += f"\n\nError message:\n{error_message}"
    return prompt

@router.get("/git-scenarios")
async def get_git_scenarios():
    """Get available Git scenarios for non-coders"""
    return {"scenarios": GIT_SCENARIOS}

@router.post("/gitops")
async def gitops_handler(request: GitOpsRequest):
    prompt = None
    summary = None
    suggestions = []
    warnings = []
    command = None
    steps = []
    beginner_explanation = None

    # Build the prompt based on the request type
    if request.instruction:
        prompt = f"Generate a Git command for: {request.instruction}\n\n"
        prompt += "IMPORTANT: Keep your response focused and to the point. Provide:\n\n"
        prompt += "1. A brief explanation of what the command does (1-2 sentences)\n"
        prompt += "2. The exact Git command to run\n"
        prompt += "3. Any important warnings or notes\n\n"
        prompt += "Keep the total response under 300 words."
        
    elif request.error_message:
        prompt = f"Help me fix this Git error: {request.error_message}\n\n"
        prompt += "IMPORTANT: Keep your response focused and to the point. Provide:\n\n"
        prompt += "1. A brief explanation of the error (1-2 sentences)\n"
        prompt += "2. Step-by-step solution (3-4 steps max)\n"
        prompt += "3. The commands to run\n\n"
        prompt += "Keep the total response under 400 words."
        
    elif request.scenario_type:
        scenario = GIT_SCENARIOS.get(request.scenario_type, request.scenario_type)
        prompt = f"Help me with this Git scenario: {scenario}\n\n"
        prompt += "IMPORTANT: Keep your response focused and to the point. Provide:\n\n"
        prompt += "1. A brief explanation of the scenario (1-2 sentences)\n"
        prompt += "2. Step-by-step solution (3-4 steps max)\n"
        prompt += "3. The commands to run\n\n"
        prompt += "Keep the total response under 400 words."
        
    elif request.git_log or request.branch_status:
        context = f"Git Log: {request.git_log}\nBranch Status: {request.branch_status}"
        prompt = f"Analyze this Git status and provide guidance:\n{context}\n\n"
        prompt += "IMPORTANT: Keep your response focused and to the point. Provide:\n\n"
        prompt += "1. A brief analysis of the current state (1-2 sentences)\n"
        prompt += "2. Recommended next steps (2-3 steps max)\n"
        prompt += "3. Any relevant commands\n\n"
        prompt += "Keep the total response under 300 words."
        
    elif request.commit_messages:
        messages = "\n".join(request.commit_messages)
        prompt = f"Review these commit messages and provide feedback:\n{messages}\n\n"
        prompt += "IMPORTANT: Keep your response focused and to the point. Provide:\n\n"
        prompt += "1. Brief feedback on the commit messages (1-2 sentences)\n"
        prompt += "2. Suggestions for improvement\n"
        prompt += "3. Examples of better commit messages\n\n"
        prompt += "Keep the total response under 300 words."
        
    elif request.pr_diff:
        prompt = f"Review this pull request diff and provide feedback:\n{request.pr_diff}\n\n"
        prompt += "IMPORTANT: Keep your response focused and to the point. Provide:\n\n"
        prompt += "1. Brief analysis of the changes (1-2 sentences)\n"
        prompt += "2. Key suggestions for improvement\n"
        prompt += "3. Any potential issues to address\n\n"
        prompt += "Keep the total response under 400 words."
        
    else:
        prompt = "Provide general Git guidance and best practices.\n\n"
        prompt += "IMPORTANT: Keep your response focused and to the point. Provide:\n\n"
        prompt += "1. Brief overview of Git best practices (2-3 paragraphs max)\n"
        prompt += "2. Key commands to remember\n"
        prompt += "3. Common workflow tips\n\n"
        prompt += "Keep the total response under 500 words."

    if len(prompt.split()) > 4 and not prompt.lower().startswith("solve this"):
        context = prompt  # can include more if needed
        cached = await find_similar_history("gitops", prompt, context)
        if cached:
            print("[DEBUG] Returning cached response from MongoDB...")
            return {
                "summary": cached,
                "command": cached,
                "warnings": [],
                "suggestions": [cached],
                "steps": [],
                "beginner_explanation": None,
                "explain_terms_enabled": request.explain_terms
            }

    if request.explain_terms:
        prompt += "\n\nAlso define any technical Git terms used in your explanation so a beginner can understand them easily."

    # Add request for step-by-step instructions and beginner explanation
    if request.scenario_type or request.error_message:
        prompt += "\n\nPlease provide:\n1. Step-by-step instructions to fix this\n2. A simple explanation for beginners"

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

            # Improved parsing for steps and beginner explanation
            if request.scenario_type or request.error_message:
                # Look for step patterns in the response
                lines = output.split('\n')
                current_step = None
                for line in lines:
                    line = line.strip()
                    if line.lower().startswith(('step', '1.', '2.', '3.', '4.', '5.')):
                        if current_step:
                            steps.append(current_step)
                        current_step = line
                    elif current_step and line:
                        current_step += '\n' + line
                    elif 'beginner' in line.lower() or 'simple' in line.lower():
                        if not beginner_explanation:
                            beginner_explanation = line
                        else:
                            beginner_explanation += '\n' + line
                
                if current_step:
                    steps.append(current_step)

            # Better parsing for steps and beginner explanation
            if request.scenario_type or request.error_message:
                # Clear any previous parsing
                steps = []
                beginner_explanation = None
                
                # Split by sections and look for step patterns
                sections = output.split('\n\n')
                for section in sections:
                    section = section.strip()
                    if not section:
                        continue
                    
                    # Check if this section contains steps
                    if any(section.lower().startswith(('step', '1.', '2.', '3.', '4.', '5.')) for line in section.split('\n')):
                        steps.append(section)
                    # Check if this section is for beginners
                    elif 'beginner' in section.lower() or 'simple' in section.lower():
                        beginner_explanation = section

            # Dangerous Command Detector
            risky_patterns = ["--force", "git push origin main", "rm -rf .git"]
            if any(p in output for p in risky_patterns):
                warnings.append("⚠️ This command is risky. Are you sure you want to do this?")

            # Try to parse for command, summary, suggestions
            if request.instruction:
                command = output.strip()
            elif request.error_message or request.git_log or request.branch_status:
                summary = output.strip()
            elif request.commit_messages or request.pr_diff:
                suggestions.append(output.strip())

            # Fallback parsing
            if not command and 'git ' in output:
                command = output.strip()
            if not summary:
                summary = output.strip()
            if not suggestions:
                suggestions.append(output.strip())

            print("[DEBUG Claude Output]", output)
            print("[DEBUG Command Parsed]", command)
            print("[DEBUG Summary Parsed]", summary)
            print("[DEBUG Suggestions Parsed]", suggestions)

            # Save to history
            save_to_history(
                feature="gitops",
                user_input=str(request.dict()),
                claude_prompt=prompt,
                claude_response=output,
                response_time_ms=(perf_counter() - start) * 1000,
                metadata={
                    "model": CLAUDE_MODEL,
                    "scenario_type": request.scenario_type,
                    "has_steps": bool(steps),
                    "has_beginner_explanation": bool(beginner_explanation)
                }
            )

            return {
                "summary": summary,
                "command": command,
                "warnings": warnings,
                "suggestions": suggestions,
                "steps": steps,
                "beginner_explanation": beginner_explanation,
                "explain_terms_enabled": request.explain_terms
            }

    except Exception as e:
        error_msg = str(e)
        print(f"Claude Exception: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)