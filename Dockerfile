# Use a Python image with uv installed to make an intermediate image.
#
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

# Make a new user with a home directory.
RUN useradd -m app

# Switch to the custom user.
USER app

ENV UV_COMPILE_BYTECODE=1

# Install the application into /app without development dependencies.
WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

COPY . /app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# Now make the final image without uv from the intermediate.
#
FROM python:3.12-slim-bookworm

# Make a new user with a home directory.
RUN useradd -m app

# Copy the application from the intermediate image.
COPY --from=builder --chown=app:app /app /app

# Switch to the custom user.
USER app

# Put the virtual environment at the beginning of the path so we can run 
# without uv.
ENV PATH="/app/.venv/bin:$PATH"

# -u is for unbuffered output.
CMD ["python3", "-u", "/app/run_sandman.py"]
