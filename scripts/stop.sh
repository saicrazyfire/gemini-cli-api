#!/usr/bin/env bash
# scripts/stop.sh

# Get the directory of this script, then go up one level to the project root
cd "$(dirname "$0")/.." || exit 1

PID_FILE=".uvicorn.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    
    if ps -p "$PID" > /dev/null; then
        echo "Stopping server with PID $PID..."
        kill "$PID"
        # Wait for the process to actually terminate
        while ps -p "$PID" > /dev/null; do sleep 1; done
        echo "Server stopped."
        rm -f "$PID_FILE"
    else
        echo "Process $PID is not running. Cleaning up stale PID file."
        rm -f "$PID_FILE"
    fi
else
    echo "No PID file found at $PID_FILE. The server may not be running via start.sh."
    
    # Fallback to finding uvicorn process
    # NOTE: This is a bit brute-force and might kill other uvicorn instances
    echo "Attempting to find and stop running uvicorn instance for app.main:app..."
    pkill -f "uvicorn app.main:app"
    if [ $? -eq 0 ]; then
        echo "Found and stopped fallback uvicorn processes."
    else
        echo "No running uvicorn instances found for app.main:app."
    fi
fi
