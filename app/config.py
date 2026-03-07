from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Gemini CLI API Wrapper"
    debug: bool = False
    
    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 10
    rate_limit_period_seconds: int = 60
    
    # CLI execution
    default_timeout_seconds: int = 30
    max_timeout_seconds: int = 120
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
