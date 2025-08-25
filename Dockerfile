# Use a Python image with uv installed.
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Install the project into /app.
WORKDIR /app

COPY . /app
RUN uv sync --locked

CMD ["uv", "run", "-m", "sandman_main.sandman"]
