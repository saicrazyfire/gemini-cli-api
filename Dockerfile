# ---------- Stage 1: build ----------
FROM python:3.12-slim AS builder

# Install uv for fast dependency resolution
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

# Copy dependency manifests first for layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies into a virtual environment
RUN uv sync --frozen --no-dev --no-install-project

# Copy the application code
COPY app/ app/
COPY config.yaml .
COPY README.md .

# Install the project itself
RUN uv sync --frozen --no-dev

# ---------- Stage 2: runtime ----------
FROM python:3.12-slim AS runtime

# ── Install Node.js 22 LTS + Gemini CLI ──
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates && \
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    npm install -g @google/gemini-cli && \
    apt-get purge -y curl && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/* /root/.npm

# Verify gemini is on PATH
RUN gemini --version || echo "gemini CLI installed (version check may not be supported)"

WORKDIR /app

# Copy the virtual environment and app from the builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/app /app/app
COPY --from=builder /app/config.yaml /app/config.yaml

# Put the venv on PATH
ENV PATH="/app/.venv/bin:$PATH"

# ── Gemini CLI config ──
# The CLI stores OAuth tokens, settings.json, and extensions in ~/.gemini/.
# Bind-mount this directory (see docker-compose) so credentials persist
# across container restarts.
#
# First-time setup:
#   docker compose -f docker-compose.simple.yaml run --rm api gemini
# This opens an interactive session to complete the OAuth browser flow.
# After login, the tokens are saved in the bind-mounted .gemini/ dir.

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
