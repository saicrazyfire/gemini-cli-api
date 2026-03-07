import subprocess
import time
import shlex
import logging
from typing import Optional
from .models import CliResponse
from .config import settings

logger = logging.getLogger(__name__)

async def execute_gemini_cli(prompt: str, timeout: Optional[int] = None) -> CliResponse:
    start_time = time.time()
    
    # Enforce timeout limits
    if timeout is None:
        timeout = settings.default_timeout_seconds
    timeout = min(timeout, settings.max_timeout_seconds)

    # Per user request: wrapping in quotes and escaping user input.
    # We use shlex.quote to safely escape any injected quotes.
    safe_prompt = shlex.quote(prompt)

    # Construct the command
    # Utilizing shell=False is the core security principle against injection.
    cmd = ["gemini", "-p", safe_prompt]
    
    logger.info(f"Executing CLI command: gemini -p <prompt redacted> with timeout {timeout}s")
    
    try:
        # We explicitly run with shell=False for security, which treats the entire safe_prompt as a single argument.
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False
        )
        
        execution_time_ms = (time.time() - start_time) * 1000
        
        return CliResponse(
            success=result.returncode == 0,
            stdout=result.stdout,
            stderr=result.stderr,
            exit_code=result.returncode,
            execution_time_ms=execution_time_ms
        )
        
    except subprocess.TimeoutExpired as e:
        execution_time_ms = (time.time() - start_time) * 1000
        logger.error(f"Command execution timed out after {timeout} seconds")
        return CliResponse(
            success=False,
            stdout="",
            stderr=f"Execution timed out after {timeout} seconds: {str(e)}",
            exit_code=124,  # Standard timeout exit code
            execution_time_ms=execution_time_ms
        )
    except FileNotFoundError:
        execution_time_ms = (time.time() - start_time) * 1000
        logger.error("The 'gemini' executable was not found on the system PATH")
        return CliResponse(
            success=False,
            stdout="",
            stderr="Executable 'gemini' not found. Ensure it is installed and in the system PATH.",
            exit_code=127,
            execution_time_ms=execution_time_ms
        )
    except Exception as e:
        execution_time_ms = (time.time() - start_time) * 1000
        logger.exception("Unexpected error during CLI execution")
        return CliResponse(
            success=False,
            stdout="",
            stderr=f"Unexpected execution error: {str(e)}",
            exit_code=1,
            execution_time_ms=execution_time_ms
        )
