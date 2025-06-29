FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files and source code (needed for local package install)
COPY pyproject.toml .
COPY README.md .
COPY uv.lock* .
COPY app/ ./app/

# Install dependencies and the local package
RUN uv sync --frozen --no-cache

# Expose port
EXPOSE 8000

# Run the application
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 