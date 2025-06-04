from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class PromptInput(BaseModel):
    prompt: str

@router.post("/prompt-explorer")
async def prompt_explorer(input: PromptInput):
    # TODO: Replace this with actual Claude API call
    # For now, just echo the prompt back as a demo
    return {"content": f"Claude received: {input.prompt}"}