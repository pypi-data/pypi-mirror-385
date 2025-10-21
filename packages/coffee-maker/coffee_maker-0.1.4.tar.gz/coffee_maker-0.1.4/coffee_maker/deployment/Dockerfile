# Multi-stage Dockerfile for code_developer daemon
# Optimized for GCP Cloud Run deployment

# Stage 1: Base image with system dependencies
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    gnupg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install GitHub CLI (gh)
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && apt-get update \
    && apt-get install -y gh \
    && rm -rf /var/lib/apt/lists/*

# Stage 2: Python dependencies
FROM base as dependencies

# Install Poetry
RUN pip install --no-cache-dir poetry==1.8.3

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install Python dependencies (production only)
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Stage 3: Application
FROM base as application

# Copy Python packages from dependencies stage
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Create app user for security (non-root)
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app /workspace /var/log/coffee-maker && \
    chown -R appuser:appuser /app /workspace /var/log/coffee-maker

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appuser coffee_maker ./coffee_maker
COPY --chown=appuser:appuser docs ./docs
COPY --chown=appuser:appuser pyproject.toml ./

# Copy health check script
COPY --chown=appuser:appuser coffee_maker/deployment/healthcheck.sh /usr/local/bin/healthcheck.sh
RUN chmod +x /usr/local/bin/healthcheck.sh

# Set up workspace directory for project files
WORKDIR /workspace

# Switch to non-root user
USER appuser

# Environment variables (override at runtime)
ENV ANTHROPIC_API_KEY="" \
    GITHUB_TOKEN="" \
    COFFEE_MAKER_MODE="daemon" \
    COFFEE_MAKER_LOG_LEVEL="INFO" \
    COFFEE_MAKER_AUTO_APPROVE="true" \
    COFFEE_MAKER_CREATE_PRS="true" \
    ROADMAP_PATH="/workspace/docs/ROADMAP.md"

# Expose port for FastAPI control API
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD /usr/local/bin/healthcheck.sh

# Default command: Start daemon with API server
CMD ["python", "-m", "coffee_maker.api.main"]
