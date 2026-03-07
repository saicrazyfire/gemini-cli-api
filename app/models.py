from pydantic import BaseModel, Field

class CliRequest(BaseModel):
    prompt: str = Field(..., description="The input text to pass to the gemini CLI via the -p flag")
    
class CliResponse(BaseModel):
    success: bool
    stdout: str
    stderr: str
    exit_code: int
    execution_time_ms: float
