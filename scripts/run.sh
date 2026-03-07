#!/usr/bin/env bash
# scripts/run.sh

# Get the directory of this script, then go up one level to the project root
cd "$(dirname "$0")/.." || exit 1

echo "Starting Gemini CLI API Wrapper..."

# Run the uvicorn server in the background via uv and save the PID
# We assume standard setup where uvicorn listens on port 8000
# PYTHONPATH is set so that the 'app' internal imports work correctly.
PYTHONPATH="$(pwd)" nohup uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 > .uvicorn.log 2>&1 &

# Save the process ID to a file so we can stop it later
echo $! > .uvicorn.pid

echo "Server started with PID $(cat .uvicorn.pid)."
echo "Logs are being written to .uvicorn.log"
