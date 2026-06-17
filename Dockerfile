FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim

# Copy project files
COPY . /app

# Disable development dependencies
ENV UV_NO_DEV=1

# Install git (and clean apt cache to keep image small)
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

# Sync the project into a new environment, asserting the lockfile is up to date
WORKDIR /app
RUN uv sync --locked

# Run in unbuffered mode for stdout
ENV PYTHONUNBUFFERED=1
CMD ["uv", "run", "main.py"]
