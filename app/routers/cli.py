from fastapi import APIRouter, Request, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address

from .models import CliRequest, CliResponse
from .cli_executor import execute_gemini_cli
from .config import settings

router = APIRouter(prefix="/api/v1/gemini", tags=["gemini"])
limiter = Limiter(key_func=get_remote_address)

@router.post("/execute", response_model=CliResponse)
@limiter.limit(f"{settings.rate_limit_requests}/{settings.rate_limit_period_seconds}seconds")
async def execute_cli(request: Request, payload: CliRequest):
    """
    Executes the Gemini CLI with the provided prompt.
    The prompt is safely passed to the '-p' flag of the 'gemini' command.
    """
    if not payload.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
        
    response = await execute_gemini_cli(prompt=payload.prompt)
    
    if not response.success:
        # We still return a 200 OK with the execution status in the body to distinguish 
        # between an API failure (like 500) and a CLI failure (like invalid CLI usage).
        pass
        
    return response
