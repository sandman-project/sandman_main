# Use a Python image with uv installed.
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Make a new user with a home directory.
RUN useradd -m app

# Switch to the custom user.
USER app

ENV UV_COMPILE_BYTECODE=1

# Install the project into /app.
WORKDIR /app
COPY . /app

RUN uv sync --locked

# Put the virtual environment at the beginning of the path so we can run 
# without uv.
ENV PATH="/app/.venv/bin:$PATH"

CMD ["python3", "-m", "sandman_main.sandman"]
