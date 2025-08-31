# Use a Python image with uv installed.
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Make a new user with a home directory.
RUN useradd -m app

# Switch to the custom user.
USER app

# Install the project into /app.
WORKDIR /app
COPY . /app

RUN uv sync --locked

CMD ["uv", "run", "-m", "sandman_main.sandman"]
