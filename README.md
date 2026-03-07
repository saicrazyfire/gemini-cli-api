# Gemini CLI API Wrapper

A FastAPI application that provides a secure, rate-limited HTTP interface to the `gemini` command-line tool.

## Features

- **Security First**: Uses `subprocess.run` with `shell=False` to pass arguments directly to the executable, preventing shell injection vulnerabilities. User input is strictly passed to the `-p` parameter. Quoting and escaping is applied via `shlex`.
- **Rate Limiting**: Integrated `slowapi` to prevent abuse. Configurable limits (default 10 requests per 60 seconds).
- **Timeouts**: Enforces execution timeouts to prevent hanging processes.
- **Dependency Management**: Powered by `uv` for fast, reproducible environments.

## Configuration

Settings are managed via a `config.yaml` file located in the root of the project.

Example `config.yaml`:
```yaml
app_name: "Gemini CLI API Wrapper"
debug: false
rate_limit:
  enabled: true
  requests: 10
  period_seconds: 60
cli:
  default_timeout_seconds: 30
  max_timeout_seconds: 120
```

To use a different configuration file path, you can set the `CONFIG_PATH` environment variable.

## Quickstart

1. Install dependencies using uv:
   ```bash
   uv sync
   ```

2. Run the application:
   ```bash
   uv run uvicorn app.main:app --reload
   ```

3. Access the interactive API docs at `http://127.0.0.1:8000/docs`

## Usage Examples

**Execute a prompt:**

```bash
curl -X POST "http://127.0.0.1:8000/v1/chat/completions" \
     -H "Content-Type: application/json" \
     -d '{"model": "gemini-cli", "messages": [{"role": "user", "content": "What is the capital of France?"}]}'
```

**Response Format:**

```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1677652288,
  "model": "gemini-cli",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "\n\nThe capital of France is Paris."
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0
  }
}
```
