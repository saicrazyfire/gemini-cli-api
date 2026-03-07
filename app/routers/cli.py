import time
import uuid
from fastapi import APIRouter, Request, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address

from .models import (
    ChatCompletionRequest, 
    ChatCompletionResponse, 
    ChatCompletionChoice, 
    ChatMessage, 
    Usage
)
from .cli_executor import execute_gemini_cli
from .config import settings

router = APIRouter(prefix="/v1", tags=["openai"])
limiter = Limiter(key_func=get_remote_address)

@router.post("/chat/completions", response_model=ChatCompletionResponse)
@limiter.limit(f"{settings.rate_limit.requests}/{settings.rate_limit.period_seconds}seconds")
async def create_chat_completion(request: Request, payload: ChatCompletionRequest):
    """
    Executes the Gemini CLI compatible with the OpenAI Chat Completions API.
    """
    if not payload.messages:
        raise HTTPException(status_code=400, detail="Messages array cannot be empty")
        
    # Format messages into a single prompt for the CLI
    prompt_parts = []
    for msg in payload.messages:
        prompt_parts.append(f"{msg.role}: {msg.content}")
    prompt = "\n\n".join(prompt_parts)
    
    response = await execute_gemini_cli(prompt=prompt)
    
    if not response.success:
        raise HTTPException(
            status_code=500, 
            detail=f"CLI Execution failed. Stderr: {response.stderr}"
        )
        
    # Construct OpenAI compatible response
    msg = ChatMessage(role="assistant", content=response.stdout)
    choice = ChatCompletionChoice(index=0, message=msg, finish_reason="stop")
    usage = Usage(prompt_tokens=0, completion_tokens=0, total_tokens=0)
    
    return ChatCompletionResponse(
        id=f"chatcmpl-{uuid.uuid4()}",
        created=int(time.time()),
        model=payload.model,
        choices=[choice],
        usage=usage
    )
