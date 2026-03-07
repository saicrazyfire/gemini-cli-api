import os
import yaml
from pydantic import BaseModel

class RateLimitConfig(BaseModel):
    enabled: bool = True
    requests: int = 10
    period_seconds: int = 60

class CliConfig(BaseModel):
    default_timeout_seconds: int = 30
    max_timeout_seconds: int = 120

class Settings(BaseModel):
    app_name: str = "Gemini CLI API Wrapper"
    debug: bool = False
    rate_limit: RateLimitConfig = RateLimitConfig()
    cli: CliConfig = CliConfig()

def load_settings() -> Settings:
    config_path = os.environ.get("CONFIG_PATH", "config.yaml")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            data = yaml.safe_load(f) or {}
            return Settings(**data)
    return Settings()

settings = load_settings()
