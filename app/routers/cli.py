import time
import uuid

from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.cli_executor import execute_gemini_cli, get_gemini_version
from app.config import settings
from app.models import (
    ChatCompletionChoice,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatMessage,
    Model,
    ModelList,
    Usage,
    VersionResponse,
)

router = APIRouter(prefix="/v1", tags=["openai"])
limiter = Limiter(key_func=get_remote_address)


@router.get("/version", response_model=VersionResponse)
async def get_version():
    """
    Returns the version of the underlying Gemini CLI.
    """
    version_str = await get_gemini_version()
    return VersionResponse(version=version_str)


@router.get("/models", response_model=ModelList)
async def list_models():
    """
    Returns the list of available models to satisfy OpenAI API client verification.
    """
    return ModelList(
        data=[
            Model(id=m, created=int(time.time()), owned_by="system")
            for m in settings.models.allowed
        ]
    )


@router.post("/chat/completions", response_model=ChatCompletionResponse)
@limiter.limit(
    f"{settings.rate_limit.requests}/{settings.rate_limit.period_seconds}seconds"
)
async def create_chat_completion(request: Request, payload: ChatCompletionRequest):
    """
    Executes the Gemini CLI compatible with the OpenAI Chat Completions API.
    """
    if not payload.messages:
        raise HTTPException(status_code=400, detail="Messages array cannot be empty")

    model_name = payload.model
    if model_name not in settings.models.allowed:
        model_name = settings.models.default

    # Format messages into a single prompt for the CLI
    prompt_parts = []
    for msg in payload.messages:
        prompt_parts.append(f"{msg.role}: {msg.content}")
    prompt = "\n\n".join(prompt_parts)

    response = await execute_gemini_cli(
        prompt=prompt,
        model=model_name,
        yolo=payload.yolo or False,
    )

    if not response.success:
        raise HTTPException(
            status_code=500, detail=f"CLI Execution failed. Stderr: {response.stderr}"
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
        usage=usage,
    )
