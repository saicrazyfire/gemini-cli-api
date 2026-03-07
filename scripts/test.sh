#!/usr/bin/env bash
# scripts/test.sh

# A simple script to test the /v1/chat/completions endpoint

# Default prompt if none provided
PROMPT="${1:-What is the capital of France?}"
MODEL="gemini-cli"
URL="http://127.0.0.1:8000/v1/chat/completions"

echo "Sending request to $URL..."
echo "Prompt: $PROMPT"
echo "-----------------------------------"

curl -sS -X POST "$URL" \
     -H "Content-Type: application/json" \
     -d "{
           \"model\": \"$MODEL\",
           \"messages\": [
             {\"role\": \"user\", \"content\": \"$PROMPT\"}
           ]
         }" | jq . || echo -e "\nEnsure you have 'jq' installed for formatted output, or the server returned an invalid response."

echo -e "\n-----------------------------------"
echo "Request complete."
