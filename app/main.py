from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .config import settings
from .routers import cli

# Initialize the rate limiter to use in-memory remote IP tracking
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title=settings.app_name,
    description="A secure FastAPI wrapper for the gemini CLI command",
    version="0.1.0",
)

# Apply RateLimiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(cli.router)

@app.get("/health")
@limiter.limit(f"{settings.rate_limit.requests}/{settings.rate_limit.period_seconds}seconds")
async def health_check(request: Request):
    return {"status": "ok", "version": "0.1.0"}
