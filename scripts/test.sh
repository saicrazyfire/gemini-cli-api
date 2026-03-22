#!/usr/bin/env bash
# scripts/test.sh

# A simple script to test the endpoints

# Arguments: <prompt> <model> <yolo>
PROMPT="${1:-What is the capital of France?}"
MODEL="${2:-gemini-3-flash-preview}"
YOLO="${3:-false}"
URL="http://127.0.0.1:8000/v1/chat/completions"
VERSION_URL="http://127.0.0.1:8000/v1/version"
MODELS_URL="http://127.0.0.1:8000/v1/models"

echo "Checking available models at $MODELS_URL..."
curl -sS "$MODELS_URL" | jq . || echo "Failed to get models"
echo "-----------------------------------"

echo "Checking Gemini CLI version at $VERSION_URL..."
curl -sS "$VERSION_URL" | jq . || echo "Failed to get version"
echo "-----------------------------------"

echo "Sending request to $URL..."
echo "Prompt: $PROMPT"
echo "Model: $MODEL"
echo "Yolo: $YOLO"
echo "-----------------------------------"

curl -sS -X POST "$URL" \
     -H "Content-Type: application/json" \
     -d "{
           \"model\": \"$MODEL\",
           \"messages\": [
             {\"role\": \"user\", \"content\": \"$PROMPT\"}
           ],
           \"yolo\": $YOLO
         }" | jq . || echo -e "\nEnsure you have 'jq' installed for formatted output, or the server returned an invalid response."

echo -e "\n-----------------------------------"
echo "Request complete."
