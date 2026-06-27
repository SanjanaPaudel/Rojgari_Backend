# Stage 1: Build virtual environment using uv
FROM python:3.12-slim AS builder

# Install uv using the official binary from its Docker image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Enable bytecode compilation and use copy link mode
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PROJECT_ENVIRONMENT=/opt/venv

WORKDIR /app

# Copy dependency specification files
COPY pyproject.toml uv.lock ./

# Install dependencies (without copying the application source)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev


# Stage 2: Runtime image
FROM python:3.12-slim

# Install system runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the compiled virtual environment from the builder
COPY --from=builder /opt/venv /opt/venv

# Configure paths and runtime environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv

# Copy application source code
COPY . .

# Expose the port Django will run on
EXPOSE 8000

# Run the Django development server by default
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
